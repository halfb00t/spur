import {
  Color, DirectionalLight, EdgesGeometry, GridHelper, HemisphereLight,
  LineBasicMaterial, LineSegments, Mesh, MeshStandardMaterial, PerspectiveCamera,
  Scene, Vector3, WebGLRenderer, OrbitControls, STLLoader,
} from './vendor/three.bundle.min.js';

const $ = (sel) => document.querySelector(sel);
const form = $('#params');
const mateInput = $('#mate-teeth');
const fields = new Map(); // name -> { input, wrap, title, rels, reason }
const defaults = {};
// Field name (or the mate box) -> the raw link token its control could not hold. It is sent
// in place of the control's value so the server's 422 marks it (L44). A Map and not rows: a
// line-leading row is harvested as a DIMS key by test_api.py.
const rejected = new Map();

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
  // Under the hob root the value is the cutter's tip radius (derive()), and root_form_d is set
  // exactly when that root was built, so the label follows the build and not the request.
  // Loose != null on purpose: null and undefined read radial, and 0 is a legal number.
  ['root_fillet', (d) => (d.root_form_d != null ? 'Hob tip radius used' : 'Root fillet used')],
  ['root_form_d', 'Hob root junction Ø'],
  ['root_waist', 'Narrowest tooth in the root'],
  ['tip_chamfer_effective', 'Tip chamfer used'],
  ['bore_effective', 'Bore Ø incl. clearance'],
  ['hex_across_flats', 'Hex across flats incl. clearance'],
  ['hex_across_corners', 'Hex across corners'],
  ['keyway_floor_to_wall', 'Keyway floor to opposite wall'],
  ['keyway_width_effective', 'Keyway width incl. clearance'],
  ['recess_id', 'Recess inner Ø'],
  ['recess_od', 'Recess outer Ø'],
  ['recess_fillet', 'Recess fillet used'],
  ['web', 'Web thickness'],
  ['cutout_hub_wall', 'Thinnest wall, cutout to bore'],
  ['cutout_rim_wall', 'Thinnest wall, cutout to root'],
  ['spoke_fillet_effective', 'Spoke fillet used'],
  ['hex_cell_effective', (d) => `Honeycomb cell A/F (${d.hex_cell_count} cells)`],
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
    // Why the field is dimmed, when it is (applyRelations). Its own row, after .control and
    // never inside it or under the class `name`, which the browser test reads as the label.
    const reason = Object.assign(document.createElement('span'), { className: 'reason', id: `reason-${name}` });
    // It sits inside the wrapping <label>, so its text is already in the input's accessible
    // name, and aria-describedby below reads it again. aria-hidden takes it out of the name
    // only; a node a describedby points at is still announced as the description.
    reason.setAttribute('aria-hidden', 'true');
    wrap.append(nameEl, control, reason);
    if (prop.description) {
      wrap.append(Object.assign(document.createElement('small'), { textContent: prop.description }));
    }
    groups.get(group).append(wrap);
    fields.set(name, { input, wrap, title, rels: prop.enabled_when ?? [], reason });
  }

  buildSelectors(schema.selectors ?? [], groups);
}

// Called after the control was assigned the token. A non-empty token that reads back empty is
// one the control cannot hold (a select with no such option reads selectedIndex -1, a number
// box sanitises it). No enum or number check of its own: the server decides (L02).
function refuse(name, input, token) {
  if (token && input.value === '') rejected.set(name, token);
}

function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  rejected.clear();
  for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];
  for (const [name, { input }] of fields) refuse(name, input, h.get(name));
  mateInput.value = h.get('mate_teeth') ?? '';
  refuse('mate_teeth', mateInput, h.get('mate_teeth'));
  applyRelations();
  deriveSelectors();
}

/** Query string with only the parameters that differ from the defaults, plus every link
 *  token its control could not hold, sent as given (L44). */
function gearQuery() {
  const q = new URLSearchParams();
  for (const [name, { input }] of fields) {
    if (rejected.has(name)) { q.set(name, rejected.get(name)); continue; }
    if (input.value !== '' && String(input.value) !== String(defaults[name])) q.set(name, input.value);
  }
  return q;
}

// ---------------------------------------------------------------- relations (L41)

/** The value the page sends for a field: an emptied box is its default, as in gearQuery.
 *  A gate that is not a field throws on the destructuring, loudly. */
function effective(name) {
  const { input } = fields.get(name);
  return input.value === '' ? defaults[name] : input.value;
}

// A switch and not a lookup table: a table of rows shaped like `['eq', ...]` is harvested
// as a DIMS key by test_api.py, and a plain-object lookup resolves `constructor`. An op the
// schema carries that is not here is a stop-and-ask (D-02), so it throws and does not guess.
function holds({ field, op, value }) {
  const have = Number(effective(field));
  switch (op) {
    case 'eq': return have === value;
    case 'gt': return have > value;
    default: throw new Error(`Unknown enabled_when op: ${op}`);
  }
}

/** What one condition asks of its gate, in the gate's own title: the reason states a need
 *  and nothing about what the server does with the value (L02). */
function need({ field, op, value }) {
  const { title } = fields.get(field);
  return op === 'eq' ? `${title} = ${value}` : `${title} above ${value}`;
}

// Dims a field whose relation does not hold, and says why. It never disables, hides or
// clears the field: a shared link's value must load, be editable and be sent (L05).
// Called from exactly three places, readHash, the form's input listener and #reset, and
// never from a build's success: a 422 must leave the state the fields imply (CF-4).
// Every condition is evaluated, so an unknown op anywhere in a list throws -- and the throw
// is caught per field, here, and nowhere else. Uncaught, it skipped scheduleUpdate()/update()
// at all four call sites and left the part, the dimensions and the download links on the
// previous parameters while the fields moved on (L08). A relation the page cannot read does
// not get to pick the field's state: the field stays plain, as every field was before L41,
// and its own reason row says so. That row, unlike #messages, is not rewritten by a build,
// so the error outlives the next keystroke; the other fields are still evaluated.
function applyRelations() {
  for (const { input, wrap, rels, reason } of fields.values()) {
    try {
      const off = rels.map(holds).includes(false);
      wrap.classList.toggle('inactive', off);
      reason.textContent = off ? `Needs ${rels.map(need).join(' and ')}` : '';
      if (off) input.setAttribute('aria-describedby', reason.id);
      else input.removeAttribute('aria-describedby');
    } catch (err) {
      wrap.classList.remove('inactive');
      reason.textContent = `Cannot tell whether this field is used: ${err.message}`;
      input.setAttribute('aria-describedby', reason.id);
    }
  }
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
  const mate = mateInput.value || rejected.get('mate_teeth') || '';
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

// ---------------------------------------------------------------- selectors (L42)

// Field name -> the string its box held when a pick zeroed it: what the user typed, a page
// default the box still held, or a value from an earlier link. A later pick that needs the
// field above its threshold puts that string back and never invents one: a flat nobody
// entered would be a number the tool printed and nobody chose (L08). A hand edit of the box
// does not update the entry, so a restore can bring back a string older than the last one
// typed (24-REVIEW IN-01); dropping the entry on a hand edit is filed as
// docs/ideas/2026-10-21-stash-entry-survives-a-hand-edit.md. Memory only. Reset clears it and
// so does a reload; a hash navigation leaves it (D-08, D-19). A restore keeps the entry, and
// the next zeroing pick overwrites it (PD-08).
const stash = new Map();

// One record per selector the schema carries: { select, wrap, reason, options, pending }.
// `pending` is a pick the fields cannot satisfy yet, or null: { chosen, condition, keep, was } --
// the option asked for, the condition that needs a number the user has not typed, `keep` set by
// completePending() for the one derive that must not end it, and `was` what showPending() found
// in the field's reason row, put back when the pick ends with no derive to rewrite the row.
const selectors = [];

// A selector is a view of fields and never a field: its row is not `label.field`, its select
// has no `name`, and nothing here touches `fields`, so gearQuery() cannot send it and update()
// cannot put it in the hash (L05, D-04). Its title, labels and conditions come from the schema
// alone, as text only (L02, BS-4).
function buildSelectors(list, groups) {
  for (const [i, { title, group, options }] of list.entries()) {
    const fs = groups.get(group);
    if (!fs) throw new Error(`Selector "${title}" names the group "${group}", which no field has`);
    const select = document.createElement('select');
    select.id = `selector-${i}`;
    for (const { label } of options) select.add(new Option(label));
    const nameEl = Object.assign(document.createElement('span'), { className: 'name', textContent: title });
    const control = Object.assign(document.createElement('span'), { className: 'control' });
    control.append(select);
    // Filled only when the options cannot be read; aria-hidden like every reason row (a
    // describedby still announces it).
    const reason = Object.assign(document.createElement('span'), { className: 'reason', id: `reason-selector-${i}` });
    reason.setAttribute('aria-hidden', 'true');
    const wrap = document.createElement('label');
    wrap.className = 'selector';
    wrap.append(nameEl, control, reason);
    fs.insertBefore(wrap, fs.querySelector('label.field'));
    const s = { select, wrap, reason, options, pending: null };
    select.addEventListener('input', (event) => pick(s, event));
    selectors.push(s);
  }
}

// Shows the one option whose conditions all hold, through the relations' own holds(). It is
// derived and never written: loading a link must send what it sent before the select
// existed (L05, D-06). Called from exactly the three places applyRelations() is, and never
// from a build response, so the select follows the fields under a 422.
// An option is shown only when exactly one holds. None holding is the blank select (selectedIndex
// -1): the model makes exactly one hold for every non-negative value, but the form accepts a
// negative, and 13 of the 27 cells of {-1, 0, 6} match none (24-RESEARCH Finding 5). Two holding
// is blank too, because a select that picked the first would claim a shape the fields do not
// single out (PD-06). Caught per selector, as applyRelations() is per field: an uncaught throw
// skipped scheduleUpdate()/update() at every call site (the WR-01 incident), so an option the
// page cannot read blanks its own select and says so in its own row.
// A pending pick survives only the derive completePending() marked with `keep` (the number it
// asked for was typed, or another is still missing); every other derive ends it, so Reset, a
// hash navigation and any other field moving show the fields' state.
function deriveSelectors() {
  for (const s of selectors) deriveSelector(s);
}

function deriveSelector(s) {
  if (s.pending?.keep) {
    s.pending.keep = false;
    showPending(s);
    return;
  }
  endPending(s, false);
  try {
    const hits = s.options.map((o) => !o.when.map(holds).includes(false));
    const i = hits.indexOf(true);
    s.select.selectedIndex = i === hits.lastIndexOf(true) ? i : -1;
    s.reason.textContent = '';
    s.select.removeAttribute('aria-describedby');
  } catch (err) {
    s.select.selectedIndex = -1;
    s.reason.textContent = `Cannot tell which option holds: ${err.message}`;
    s.select.setAttribute('aria-describedby', s.reason.id);
  }
}

// What a pick must write to make the chosen option hold, or the condition that stops it. It
// plans and never writes, so a pick and the completion of a pending pick share one rule: for
// each condition that does not hold, an `eq` field gets the string 0, never an empty box (an
// emptied box reads as the field's default, so it would not be a zero, BS-1), and its old
// string is stashed; a `gt` field gets its own stashed string back when that string clears the
// threshold; otherwise the pick is pending (D-07..D-09). An op holds() does not know throws
// before any write.
function plan(chosen) {
  const writes = [];
  for (const condition of chosen.when) {
    if (holds(condition)) continue;
    const { field, op, value } = condition;
    const kept = stash.get(field);
    if (op === 'eq') writes.push([field, String(value), true]);
    else if (stash.has(field) && Number(kept === '' ? defaults[field] : kept) > value) writes.push([field, kept, false]);
    else return { writes: [], condition };
  }
  return { writes, condition: null };
}

// The one statement in this section that writes a field (test_api.py counts it), and only
// after the whole plan: writing as the walk went would have zeroed fields under a pick that
// then went pending (24-RESEARCH Finding 10).
function write(writes) {
  for (const [field, to, zeroed] of writes) {
    const { input } = fields.get(field);
    if (zeroed) stash.set(field, input.value);
    // The box now holds what the pick wrote, so the request sends that, not an old link token (D-19).
    input.value = to; rejected.delete(field);
  }
}

// A pick writes the minimum that makes the chosen option hold, or goes pending. The keyway is
// left to the server's 422 (D-10). No update() here and no stopPropagation() on a write: this
// runs on the select's input, which then bubbles to the form's listener, whose derive lands
// the select on the chosen option (its conditions now hold) and whose scheduleUpdate() sends
// the one request (PD-04). A pick first ends the pending pick before it and puts that one's
// row back, because no derive runs between two picks that both go pending.
function pick(s, event) {
  endPending(s, true);
  const chosen = s.options[s.select.selectedIndex];
  const { writes, condition } = plan(chosen);
  if (condition) return pend(s, chosen, condition, event);
  write(writes);
}

// The pick cannot be made true without a number the user has not typed: nothing is written,
// the select keeps what was asked for, and the field that needs the number says so in its own
// reason row, which describes that field and the select. The focus does not move: on Blink
// and Gecko (Windows, Linux) an arrow key on the focused select commits the next option and
// fires `input`, so a focus() here ended a keyboard walk at the first pending step, the next
// arrow editing that number box instead (24 WR-01; the Codex review of PR #36 traced it to
// both engines' select handlers). stopPropagation() keeps the form's listener from deriving
// the select back to the fields' state and from scheduling a request for a part that did not
// change (MEASURED, 24-RESEARCH Finding 4). The pick stays pending until the number it asked
// for is typed, when completePending() writes what it held back, or until anything else moves
// the fields, when the next derive shows their state.
function pend(s, chosen, condition, event) {
  event.stopPropagation();
  s.pending = { chosen, condition, keep: false, was: null };
  showPending(s);
}

// Renders the pending pick and remembers the row it overwrites. On a kept derive it runs after
// applyRelations() has rewritten every row, so `was` is always the row's own text.
function showPending(s) {
  const { chosen, condition } = s.pending;
  const { input, reason } = fields.get(condition.field);
  s.pending.was = { input, reason, text: reason.textContent, by: input.getAttribute('aria-describedby') };
  s.select.selectedIndex = s.options.indexOf(chosen);
  s.wrap.classList.add('pending');
  reason.textContent = `${chosen.label} needs ${need(condition)}`;
  input.setAttribute('aria-describedby', reason.id);
  s.select.setAttribute('aria-describedby', reason.id);
}

// Ends a pending pick. `restore` puts the field's row back as showPending() found it, for the
// one path no derive follows (a new pick on the select); a derive rewrites every row itself.
function endPending(s, restore) {
  if (!s.pending) return;
  if (restore && s.pending.was) {
    const { input, reason, text, by } = s.pending.was;
    reason.textContent = text;
    if (by === null) input.removeAttribute('aria-describedby');
    else input.setAttribute('aria-describedby', by);
  }
  s.wrap.classList.remove('pending');
  s.select.removeAttribute('aria-describedby');
  s.pending = null;
}

// A field changed under a pending pick. Runs in the capture phase, so before the form's own
// listener derives. The field the pick asked for: the plan is run again, and one that holds
// writes now what the pick held back (the zeros, a stashed string) so the derive that follows
// shows the chosen option; one still short of a number keeps the pick pending on that field.
// Anything else -- another field, or a pick on another selector -- ends the pick: its row is
// put back and it is derived here, because another selector's pending pick stops its event
// before the form's listener (the Codex re-review of PR #36, CX-04). The select's own event
// is a new pick, which pick() handles. An empty box is not a typed number: effective() reads
// it as the field's default, which would complete the pick and zero the other fields on a
// Backspace or a leading `.` (24 WR-02, reproduced), so the pick stays pending until the box
// holds a number.
function completePending(event) {
  for (const s of selectors) {
    if (!s.pending || event.target === s.select) continue;
    const { chosen, condition } = s.pending;
    const { input } = fields.get(condition.field);
    if (event.target !== input) {
      endPending(s, true);
      deriveSelector(s);
      continue;
    }
    const next = input.value === '' ? { writes: [], condition } : plan(chosen);
    endPending(s, false);
    if (next.condition) s.pending = { chosen, condition: next.condition, keep: true, was: null };
    else write(next.writes);
  }
}

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
  // The browser test's one scene observable; STLLoader is non-indexed: 3 vertices per triangle.
  canvas.dataset.triangles = String(geometry.attributes.position.count / 3);
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
form.addEventListener('input', completePending, true);
form.addEventListener('input', (e) => rejected.delete(e.target.name));
form.addEventListener('input', () => { applyRelations(); deriveSelectors(); scheduleUpdate(); });
mateInput.addEventListener('input', scheduleUpdate);
mateInput.addEventListener('input', () => rejected.delete('mate_teeth'));
window.addEventListener('hashchange', () => { readHash(); update(); });
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
new ResizeObserver(resize).observe(canvas.parentElement);

$('#fit').addEventListener('click', fit);
$('#reset').addEventListener('click', () => {
  for (const [name, { input }] of fields) input.value = defaults[name];
  rejected.clear();
  mateInput.value = '';
  stash.clear();
  applyRelations();
  deriveSelectors();
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
    showMessages([`Could not build the form: ${err.message}`]);
    return;
  }
  readHash();
  update();
})();
