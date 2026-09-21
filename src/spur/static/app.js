import {
  Color, DirectionalLight, EdgesGeometry, GridHelper, HemisphereLight,
  LineBasicMaterial, LineSegments, Mesh, MeshStandardMaterial, PerspectiveCamera,
  Scene, Vector3, WebGLRenderer, OrbitControls, STLLoader,
} from './vendor/three.bundle.min.js';

const $ = (sel) => document.querySelector(sel);
const form = $('#params');
const mateInput = $('#mate-teeth');
const fields = new Map(); // name -> { input, wrap, title }
const defaults = {};

const DIMS = [
  ['pitch_d', 'Pitch Ø'],
  ['tip_d', 'Tip Ø'],
  ['caliper_over_tips', 'Calipers across tips'],
  ['span', (d) => `Span over ${d.span_teeth} teeth`],
  ['root_d', 'Root Ø'],
  ['base_d', 'Base Ø'],
  ['tip_thickness', 'Tip thickness'],
  ['root_thickness', 'Tooth at root'],
  ['root_gap', 'Gap at root'],
  ['root_fillet', 'Root fillet used'],
  ['bore_effective', 'Bore Ø incl. clearance'],
  ['recess_id', 'Recess inner Ø'],
  ['recess_od', 'Recess outer Ø'],
  ['recess_fillet', 'Recess fillet used'],
  ['web', 'Web thickness'],
];

const fmt = (v) => Number(v).toFixed(3).replace(/\.?0+$/, '');
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

// ---------------------------------------------------------------- form

async function buildForm() {
  const res = await fetch('api/schema');
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  const schema = await res.json();
  const groups = new Map();

  for (const [name, prop] of Object.entries(schema.properties)) {
    defaults[name] = prop.default;
    const group = prop.group ?? 'Other';
    if (!groups.has(group)) {
      const fs = document.createElement('fieldset');
      const legend = document.createElement('legend');
      legend.textContent = group;
      fs.append(legend);
      form.append(fs);
      groups.set(group, fs);
    }

    let input;
    if (prop.enum) {
      input = document.createElement('select');
      for (const v of prop.enum) input.add(new Option(v, v));
    } else {
      input = document.createElement('input');
      input.type = 'number';
      input.inputMode = 'decimal';
      if (prop.minimum !== undefined) input.min = prop.minimum;
      if (prop.maximum !== undefined) input.max = prop.maximum;
      input.step = prop.step ?? (prop.type === 'integer' ? 1 : 'any');
    }
    input.name = name;

    const wrap = document.createElement('label');
    wrap.className = 'field';
    wrap.title = prop.description ?? '';
    const title = prop.title ?? name;
    const nameEl = Object.assign(document.createElement('span'), { className: 'name', textContent: title });
    const unit = Object.assign(document.createElement('span'), { className: 'unit', textContent: prop.unit ?? '' });
    const control = Object.assign(document.createElement('span'), { className: 'control' });
    control.append(input, unit);
    wrap.append(nameEl, control);
    if (prop.description) {
      wrap.append(Object.assign(document.createElement('small'), { textContent: prop.description }));
    }
    groups.get(group).append(wrap);
    fields.set(name, { input, wrap, title });
  }
}

function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];
  mateInput.value = h.get('mate_teeth') ?? '';
}

/** Query string with only the parameters that differ from the defaults. */
function gearQuery() {
  const q = new URLSearchParams();
  for (const [name, { input }] of fields) {
    if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value);
  }
  return q;
}

// ---------------------------------------------------------------- messages

function showMessages(errors = [], warnings = []) {
  const box = $('#messages');
  box.replaceChildren(
    ...errors.map((t) => Object.assign(document.createElement('p'), { className: 'error', textContent: t })),
    ...warnings.map((t) => Object.assign(document.createElement('p'), { className: 'warning', textContent: t })),
  );
}

async function problems(res) {
  try {
    const body = await res.json();
    if (!Array.isArray(body.detail)) return [String(body.detail ?? res.statusText)];
    return body.detail.map((d) => {
      const msg = String(d.msg).replace(/^Value error, /, '');
      for (const name of [d.loc?.[1], ...(d.ctx?.fields ?? [])]) {
        fields.get(name)?.wrap.classList.add('invalid');
      }
      const field = fields.get(d.loc?.[1]);
      return field ? `${field.title}: ${msg}` : msg;
    });
  } catch {
    return [`${res.status} ${res.statusText}`];
  }
}

function renderInfo(info) {
  const rows = [];
  for (const [key, label] of DIMS) {
    const v = info[key];
    if (v === null || v === undefined) continue;
    const row = document.createElement('div');
    row.append(
      Object.assign(document.createElement('dt'), { textContent: typeof label === 'function' ? label(info) : label }),
      Object.assign(document.createElement('dd'), { textContent: `${fmt(v)} mm` }),
    );
    rows.push(row);
  }
  $('#dims').replaceChildren(...rows);
  $('#centre-distance').textContent = info.centre_distance != null ? `${fmt(info.centre_distance)} mm` : '—';
  showMessages([], info.warnings ?? []);
}

function setDownloads(q) {
  for (const kind of ['stl', 'step']) {
    const a = $(`#dl-${kind}`);
    if (q) {
      const qs = q.toString();
      a.href = `api/model.${kind}${qs ? `?${qs}` : ''}`;
      a.removeAttribute('aria-disabled');
    } else {
      a.removeAttribute('href');
      a.setAttribute('aria-disabled', 'true');
    }
  }
}

const setStatus = (text) => { $('#status').textContent = text; };

// ---------------------------------------------------------------- update loop

let seq = 0;
let inflight = null;

async function update() {
  const q = gearQuery();
  const mate = mateInput.value;
  const infoQ = new URLSearchParams(q);
  if (mate) infoQ.set('mate_teeth', mate);
  const hash = infoQ.toString();
  history.replaceState(null, '', hash ? `#${hash}` : location.pathname + location.search);

  for (const { wrap } of fields.values()) wrap.classList.remove('invalid');
  setDownloads(null);
  inflight?.abort();
  const ctl = new AbortController();
  inflight = ctl;
  const mine = ++seq;
  setStatus('Building…');

  const fail = (errors) => {
    if (mine !== seq) return;
    showMessages(errors);
    $('#dims').replaceChildren();
    setStatus(mesh ? 'Showing the last valid gear' : '');
  };

  try {
    const infoRes = await fetch(`api/info?${infoQ}`, { signal: ctl.signal });
    if (!infoRes.ok) return fail(await problems(infoRes));
    const info = await infoRes.json();
    if (mine !== seq) return;
    renderInfo(info);

    const stlQ = new URLSearchParams(q);
    stlQ.set('quality', 'preview');
    const res = await fetch(`api/model.stl?${stlQ}`, { signal: ctl.signal });
    if (!res.ok) return fail(await problems(res));
    const buf = await res.arrayBuffer();
    if (mine !== seq) return;
    showModel(buf);
    setDownloads(q);
    setStatus('');
  } catch (err) {
    if (err.name !== 'AbortError') fail([`Request failed: ${err.message}`]);
  }
}

let debounce;
const scheduleUpdate = () => {
  clearTimeout(debounce);
  debounce = setTimeout(update, 350);
};

// ---------------------------------------------------------------- 3D view

const canvas = $('#canvas');
const renderer = new WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new Scene();
const camera = new PerspectiveCamera(35, 1, 0.1, 10000);
camera.up.set(0, 0, 1); // CAD convention: Z up
scene.add(camera);
scene.add(new HemisphereLight(0xffffff, 0x404850, 1.5));
const key = new DirectionalLight(0xffffff, 1.6); // follows the camera
key.position.set(0.6, 1, 0);
key.target.position.set(0, 0, -1);
camera.add(key, key.target);

const controls = new OrbitControls(camera, canvas);
const material = new MeshStandardMaterial({ metalness: 0.1, roughness: 0.55 });
const edgeMaterial = new LineBasicMaterial();
const loader = new STLLoader();
let mesh = null;
let edges = null;
let grid = null;
let box = null;
let fitted = false;

let frameQueued = false;
function render() {
  if (frameQueued) return;
  frameQueued = true;
  requestAnimationFrame(() => {
    frameQueued = false;
    renderer.render(scene, camera);
  });
}
controls.addEventListener('change', render);

function placeGrid() {
  if (grid) {
    scene.remove(grid);
    grid.geometry.dispose();
    grid.material.dispose();
    grid = null;
  }
  if (!box) return;
  const extent = Math.max(box.max.x - box.min.x, box.max.y - box.min.y) * 1.6;
  const step = [0.5, 1, 2, 5, 10, 20, 50, 100].find((s) => extent / s <= 24) ?? 200;
  const size = Math.ceil(extent / step) * step;
  const colour = css('--grid');
  grid = new GridHelper(size, Math.round(size / step), colour, colour);
  grid.rotation.x = Math.PI / 2; // GridHelper lies in XZ; we want XY
  grid.position.z = box.min.z - 0.01;
  scene.add(grid);
}

function applyTheme() {
  scene.background = new Color(css('--view-bg'));
  material.color.set(css('--mesh'));
  edgeMaterial.color.set(css('--edge'));
  placeGrid();
  render();
}

function fit() {
  if (!box) return;
  const centre = box.getCenter(new Vector3());
  const radius = box.getSize(new Vector3()).length() / 2;
  const dist = (radius / Math.sin((camera.fov * Math.PI) / 360)) * 1.1;
  camera.position.copy(centre).addScaledVector(new Vector3(0.55, -0.9, 0.95).normalize(), dist);
  camera.near = dist / 200;
  camera.far = dist * 50;
  camera.updateProjectionMatrix();
  controls.target.copy(centre);
  controls.update();
  render();
}

function showModel(buffer) {
  const geometry = loader.parse(buffer);
  geometry.computeBoundingBox();
  if (mesh) {
    scene.remove(mesh, edges);
    mesh.geometry.dispose();
    edges.geometry.dispose();
  }
  mesh = new Mesh(geometry, material);
  edges = new LineSegments(new EdgesGeometry(geometry, 40), edgeMaterial);
  scene.add(mesh, edges);
  const previous = box;
  box = geometry.boundingBox.clone();
  placeGrid();
  // Refit on first load or when the part size changes a lot; otherwise keep the user's view.
  const size = (b) => b.getSize(new Vector3()).length();
  if (!fitted || Math.abs(size(box) / size(previous) - 1) > 0.3) {
    fit();
    fitted = true;
  }
  render();
}

function resize() {
  const { clientWidth: w, clientHeight: h } = canvas.parentElement;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  render();
}

// ---------------------------------------------------------------- wiring

form.addEventListener('submit', (e) => e.preventDefault());
form.addEventListener('input', scheduleUpdate);
mateInput.addEventListener('input', scheduleUpdate);
window.addEventListener('hashchange', () => { readHash(); update(); });
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
new ResizeObserver(resize).observe(canvas.parentElement);

$('#fit').addEventListener('click', fit);
$('#reset').addEventListener('click', () => {
  for (const [name, { input }] of fields) input.value = defaults[name];
  mateInput.value = '';
  update();
});
$('#copy-link').addEventListener('click', async (e) => {
  const button = e.currentTarget;
  try {
    await navigator.clipboard.writeText(location.href);
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy link'; }, 1500);
  } catch {
    window.prompt('Copy this link:', location.href); // clipboard API needs HTTPS or localhost
  }
});

(async () => {
  applyTheme();
  resize();
  try {
    await buildForm();
  } catch (err) {
    showMessages([`Could not load the parameter schema: ${err.message}`]);
    return;
  }
  readHash();
  update();
})();
