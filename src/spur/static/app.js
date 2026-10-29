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

// The parts the page shows: the routes and texts that differ, and nothing else; the fields,
// their defaults and their rows come from the part's own schema. Indexed only by a radio's
// literal value or by 'gear' in the bootstrap, never by text from a link: a lookup by hash
// text would resolve `constructor` (33-RESEARCH Pattern 6). `tag` opens a link's hash, `mate`
// says whether the page sends the mate box with it, `gridAlong` whether the floor grid is also
// sized from the part's height (a shaft is long where a gear is flat: 33-08). The gear's texts
// are the ones index.html ships, so the gear page reads as it did before the switch.
const PARTS = {
  gear: {
    schema: 'api/schema', info: 'api/info', model: 'api/model', tag: '', noun: 'gear', mate: true,
    gridAlong: false,
    title: 'spur · parametric spur gear', sub: 'parametric involute spur gear',
    aria: '3D preview of the gear', fitTitle: 'Fit gear to view',
  },
  shaft: {
    schema: 'api/shaft/schema', info: 'api/shaft/info', model: 'api/shaft/model',
    tag: 'part=shaft', noun: 'shaft', mate: false, gridAlong: true,
    title: 'spur · DIN 5480 splined shaft', sub: 'DIN 5480 splined shaft',
    aria: '3D preview of the shaft', fitTitle: 'Fit shaft to view',
  },
};
// The part whose form is built; empty until the first build, so the first link always builds.
let part = '';
let P = PARTS.gear;
// The page's message for a link whose `part` it has no form for, or null (D-15). While it is
// set, update() builds nothing: a field edit or Reset must not build a part the link did not
// name (D-20). A switch, or the next hashchange, clears it. body[data-refused] follows it and
// dims the form and Reset (style.css).
let refused = null;
// The shaft's result rows come in its schema; null means the gear's table above.
let dims = null;
// Bumped by every buildForm: a build that finds a later one started returns false, so a slow
// schema fetch of the part the user left cannot rebuild the page under the one they chose.
let formSeq = 0;
const radios = document.querySelectorAll('.part-switch input');

// ---------------------------------------------------------------- form

// Builds the form of one part, first emptying everything the other part's form left: a value
// from one part's form must never reach the other's request (L05).
async function buildForm(which) {
  const build = ++formSeq;
  let schema;
  try {
    const res = await fetch(PARTS[which].schema);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    schema = await res.json();
  } catch (err) {
    // Overtaken: the newer build owns the page and its message. A failure here must not reach
    // the caller's catch, which would write its error over the newer page and clear the
    // refusal of a newer link.
    if (build !== formSeq) return false;
    throw err;
  }
  if (build !== formSeq) return false;
  // Past this line the page is emptied, so it holds no part until the build below finishes. A
  // throw in between (a schema without `properties`, a selector naming no group) must make the
  // next link or switch rebuild: with `part` still naming the old part, followHash took its
  // same-part branch and read the link into an empty form, and the old radio stayed checked.
  part = '';
  form.replaceChildren();
  fields.clear();
  for (const key of Object.keys(defaults)) delete defaults[key];
  selectors.length = 0;
  stash.clear(); rejected.clear();
  mateInput.value = '';
  clearTimeout(debounce);
  inflight?.abort();
  inflight = null;
  seq++;
  $('#dims').replaceChildren();
  $('#centre-distance').textContent = '—';
  showMessages();
  setDownloads(null);
  setStatus('');
  clearScene();
  dims = schema.dims ?? null;
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
    } else if (prop.type === 'string') {
      // A text box, because a number box blanks `8f` (33-RESEARCH Pitfall 1). `pattern` and
      // `maxLength` are hints only: the server decides what a value means (L02).
      input = document.createElement('input');
      input.type = 'text';
      if (prop.maxLength !== undefined) input.maxLength = prop.maxLength;
      if (prop.pattern !== undefined) input.pattern = prop.pattern;
      input.spellcheck = false;
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
  part = which;
  P = PARTS[which];
  markPart();
  // The mate box and the other part's hint are hidden by CSS on this attribute and not by a
  // write here: the guard in test_api.py refuses any script that shuts a control (L41). The
  // texts go in as text and attributes, never markup.
  document.body.dataset.part = which;
  document.title = P.title;
  $('header .sub').textContent = P.sub;
  canvas.setAttribute('aria-label', P.aria);
  $('#fit').setAttribute('title', P.fitTitle);
  return true;
}

// The radios follow the part on the page, not the click: a build that fails or is overtaken
// leaves the page on the part it shows.
function markPart() {
  for (const radio of radios) radio.checked = radio.value === part;
}

// What a refusal tells a screen reader, beside the look body[data-refused] gives (style.css).
// aria-disabled is valid on a group and a button, not on the unnamed <form> (WAI-ARIA 1.2), so it
// goes on the form's fieldsets and on Reset. It is no `disabled` or `inert`, which the guard in
// test_api.py refuses (L41): the controls stay focusable, and the page only says they do nothing.
// aria-describedby points at #messages, where the refusal is (D-15). The form's fieldsets are
// rebuilt by every build, and Reset is not, so a clear must reach both.
const REFUSAL_MARKED = '#params fieldset, #reset';

function markRefused() {
  for (const el of document.querySelectorAll(REFUSAL_MARKED)) {
    el.setAttribute('aria-disabled', 'true');
    el.setAttribute('aria-describedby', 'messages');
  }
}

function clearRefusal() {
  refused = null;
  delete document.body.dataset.refused;
  for (const el of document.querySelectorAll(REFUSAL_MARKED)) {
    el.removeAttribute('aria-disabled');
    el.removeAttribute('aria-describedby');
  }
}

// A radio's change: build that part's form at its defaults, then show it. No value crosses
// a switch (D-13) and the hash is the new part's, written by update() (D-14).
async function switchTo(which) {
  clearRefusal();
  try {
    if (!(await buildForm(which))) return;
  } catch (err) {
    showMessages([`Could not build the form: ${err.message}`]);
    markPart();
    return;
  }
  for (const [name, { input }] of fields) input.value = defaults[name];
  applyRelations();
  deriveSelectors();
  update();
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

// The `part` values of a link, read as text. partOf compares them as literals and nothing
// indexes PARTS by them: a lookup by hash text would resolve `constructor` and `__proto__`
// (T-33-15).
const partValues = (hash) => new URLSearchParams(hash.slice(1)).getAll('part');

/** 'gear' for no part or one empty value, 'shaft' for exactly one `shaft`, else null. The gear
 *  link carries no `part` key, and `gear` is not a second spelling of it (D-15). */
function partOf(hash) {
  const values = partValues(hash);
  if (values.length === 0 || (values.length === 1 && values[0] === '')) return 'gear';
  return values.length === 1 && values[0] === 'shaft' ? 'shaft' : null;
}

// A link with a part the page has no form for: the gear form at its defaults, nothing drawn,
// neither radio checked, and the hash as the link wrote it. This message is the narrow exception
// to "the server words refusals" (L02): no route takes `part`, so no server can word it (D-15).
// The value is echoed quoted by JSON.stringify and shown as text, never as markup (T-33-23).
async function refuseLink(values) {
  const text = `Unknown part ${JSON.stringify(values.join(', '))} in the link; use the Gear or Shaft switch`;
  refused = text;
  document.body.dataset.refused = '';
  if (!(await buildForm('gear'))) return;
  for (const [name, { input }] of fields) input.value = defaults[name];
  applyRelations();
  deriveSelectors();
  for (const radio of radios) radio.checked = false;
  markRefused();
  showMessages([text]);
}

// The hashchange listener and the bootstrap: a link names the part, and the form of that part
// is built before the link is read into it (D-14). A link that keeps the part is handled before
// any await, in the event itself, as the listener did before there were two parts (the golden
// sweep sends one request per link and relies on it). formSeq is bumped so a slower build
// started by an earlier link cannot land under this one.
async function followHash() {
  clearRefusal();
  formSeq++;
  const which = partOf(location.hash);
  if (which === part) { markPart(); readHash(); update(); return; }
  try {
    if (which === null) await refuseLink(partValues(location.hash));
    else if (await buildForm(which)) { readHash(); update(); }
  } catch (err) {
    // refuseLink sets the refusal before its gear build. A build that throws never showed the
    // refusal, and the form still on the page is the old part's, so the page must not keep
    // looking refused or answer that form's keystrokes with a message about the link.
    clearRefusal();
    showMessages([`Could not build the form: ${err.message}`]);
    markPart();
  }
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

function dimRow(label, text) {
  const row = document.createElement('div');
  row.append(
    Object.assign(document.createElement('dt'), { textContent: label }),
    Object.assign(document.createElement('dd'), { textContent: text }),
  );
  return row;
}

function renderInfo(info) {
  const rows = [];
  if (dims) {
    // The part's own rows, in its schema's order. A number shows with its unit when it has one,
    // a string as itself; an absent value is no row (D-22), as for the gear.
    for (const { key, label, unit } of dims) {
      const v = info[key];
      if (v === null || v === undefined) continue;
      rows.push(dimRow(label, typeof v === 'string' ? v : unit ? `${fmt(v)} ${unit}` : fmt(v)));
    }
  } else {
    for (const [key, label] of DIMS) {
      const v = info[key];
      if (v === null || v === undefined) continue;
      rows.push(dimRow(typeof label === 'function' ? label(info) : label, `${fmt(v)} mm`));
    }
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
      a.href = `${P.model}.${kind}${qs ? `?${qs}` : ''}`;
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
  // A build threw after it emptied the page (buildForm). Reset and the mate box sit outside the
  // form and still call here, but there is no form to read, and P is still the old part's: a
  // build now would draw that part's defaults under a blank form.
  if (!part) return;
  if (refused) { showMessages([refused]); return; }
  const q = gearQuery();
  const mate = mateInput.value || rejected.get('mate_teeth') || '';
  const infoQ = new URLSearchParams(q);
  if (mate && P.mate) infoQ.set('mate_teeth', mate);
  const hash = [P.tag, infoQ.toString()].filter(Boolean).join('&');
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
    setStatus(mesh ? `Showing the last valid ${P.noun}` : '');
  };

  try {
    const infoRes = await fetch(`${P.info}?${infoQ}`, { signal: ctl.signal });
    if (!infoRes.ok) return fail(await problems(infoRes));
    const info = await infoRes.json();
    if (mine !== seq) return;
    renderInfo(info);

    const stlQ = new URLSearchParams(q);
    stlQ.set('quality', 'preview');
    const res = await fetch(`${P.model}.stl?${stlQ}`, { signal: ctl.signal });
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
  // A grid sized from the width alone is 40 mm under a 1000 mm shaft and cannot be seen; a part
  // that says so (`gridAlong`) also counts its height. The gear's grid is as it was.
  const across = Math.max(box.max.x - box.min.x, box.max.y - box.min.y);
  const extent = (P.gridAlong ? Math.max(across, box.max.z - box.min.z) : across) * 1.6;
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

// Empties the scene of the part the user left, so a 422 on the new one never shows the old
// part under it (and `mesh` then reads null for the status line).
function clearScene() {
  if (mesh) {
    scene.remove(mesh, edges);
    mesh.geometry.dispose();
    edges.geometry.dispose();
    mesh = null;
    edges = null;
  }
  box = null;
  placeGrid(); // no box: removes the grid
  fitted = false;
  delete canvas.dataset.triangles;
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
window.addEventListener('hashchange', followHash);
for (const radio of radios) {
  radio.addEventListener('change', () => switchTo(radio.value));
}
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

applyTheme();
resize();
followHash();
