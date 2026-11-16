/* Developer controlled DOM/native-message fixtures. No browser/visual claim. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm'), assert = require('node:assert/strict');
const repo = path.resolve(__dirname, '../../../..');
const E = require(path.join(repo, 'js/namelecule-molecular-detective-engine.js'));
const source = fs.readFileSync(path.join(repo, 'js/namelecule-molecular-detective.js'), 'utf8');
const fixtures = require(path.join(repo, 'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json'));
const catalog = require(path.join(repo, 'games/data/alkane-structures.json'));
const clone = value => JSON.parse(JSON.stringify(value));
for (const molecule of catalog.molecules) fixtures[molecule.id].sourceMOL = molecule.mol;
let checks = 0; const records = [];
function check(label, fn) { fn(); ++checks; records.push(label); }
function surface() {
  const listeners = new Map();
  return {addEventListener(type, fn) { const a = listeners.get(type) || []; if (!a.includes(fn)) a.push(fn); listeners.set(type, a); },
    removeEventListener(type, fn) { listeners.set(type, (listeners.get(type) || []).filter(item => item !== fn)); },
    fire(type, data = {}) { for (const fn of [...(listeners.get(type) || [])]) fn(data); }, listeners};
}
function boot(controlled = true) {
  const nodes = new Map(), outer = [], commands = [], frames = new Map(), timers = new Map(), scrolls = [];
  let serial = 0, uuid = 0, nativeRevision = 0;
  function node(id = '') {
    const classes = new Set(), attrs = {};
    const element = Object.assign(surface(), {id, hidden: false, disabled: false, value: '', children: [], isConnected: true,
      classList: {add(...a) { a.forEach(c => classes.add(c)); }, remove(...a) { a.forEach(c => classes.delete(c)); },
        contains(c) { return classes.has(c); }, toggle(c, force) { const yes = force === undefined ? !classes.has(c) : force; yes ? classes.add(c) : classes.delete(c); return yes; }},
      setAttribute(k, v) { attrs[k] = v; }, getAttribute(k) { return attrs[k]; },
      append(...a) { this.children.push(...a); }, replaceChildren(...a) { this.children = a; }, focus() {},
      getBoundingClientRect() { const top = id === 'feedback' ? 800 : id === 'detective-feedback-end' ? 950 : id === 'mission-title' ? 200 : id === 'mission-prompt' ? 260 : 0;
        return {top, bottom: id === 'body' ? 1100 : top + (id === 'detective-feedback-end' ? 1 : 40), height: id === 'body' ? 1100 : id === 'detective-feedback-end' ? 1 : 40}; },
    });
    Object.defineProperty(element, 'options', {get() { return this.children; }});
    return element;
  }
  const document = {body: node('body'), documentElement: Object.assign(node('html'), {scrollHeight: 2000}),
    getElementById(id) { if (nodes.has(id)) return nodes.get(id); const find = n => n.id === id ? n : (n.children || []).map(find).find(Boolean);
      for (const item of nodes.values()) { const found = find(item); if (found) return found; } return null; },
    createElement: () => node(), createTextNode: text => ({textContent: text}), createDocumentFragment: () => node()};
  document.scrollingElement = document.documentElement;
  for (const id of ['molecule-viewer','viewer-wrap','viewer-mask','viewer-message','game-status','molecule-select','mission-select','mission-name','mission-prompt','selection-kind','selection-status','check-answer','clear-selection','next-mission','zoom-in','zoom-out','retry-load','feedback','mission-title']) nodes.set(id, node(id));
  const native = Object.assign(surface(), {postMessage: (data, origin) => commands.push(clone(data))});
  nodes.get('molecule-viewer').contentWindow = native;
  const parent = {postMessage: (data, origin) => outer.push(clone(data))};
  const context = Object.assign(surface(), {document, URLSearchParams, structuredClone, console, NameleculeMolecularDetectiveEngine: E,
    location: {origin: 'http://localhost:57116', search: controlled ? '?embedded=1&lessonSession=fixture_lesson_0123456789' : ''},
    crypto: {randomUUID: () => 'native-session-' + (++uuid)}, innerHeight: 700, innerWidth: 1200, scrollY: 0, scrollX: 0,
    matchMedia: () => ({matches: true}), scrollTo: value => scrolls.push(value),
    requestAnimationFrame: fn => { const id = ++serial; frames.set(id, fn); return id; }, cancelAnimationFrame: id => frames.delete(id),
    setTimeout: fn => { const id = ++serial; timers.set(id, fn); return id; }, clearTimeout: id => timers.delete(id),
    ResizeObserver: class { constructor(fn) { this.fn = fn; } observe() {} disconnect() {} }, parent});
  context.window = context; if (!controlled) context.parent = context;
  vm.createContext(context); vm.runInContext(source, context);
  const snap = () => clone(context.NameleculeMolecularDetective.snapshot());
  const flush = () => { let count = 0; while (frames.size) { assert.ok(++count < 20); const batch = [...frames.values()]; frames.clear(); batch.forEach(fn => fn()); } };
  const receive = (data, options = {}) => context.fire('message', {data, origin: context.location.origin, source: native, ...options});
  const ready = (options = {}) => { const session = new URLSearchParams(nodes.get('molecule-viewer').src.split('?')[1]).get('session');
    receive({channel: 'namelecule-molecular-detective-v1', session, requestId: 0, type: 'ready', inventory: E.starterIds.map(id => ({id})), ...options}); };
  const lessonLoad = (requestId, moleculeId = 'ethane', family = 'parent-chain', raw = {atoms: [], bonds: [], attempts: 0, submitted: false}, extra = {}, options = {}) => {
    const snapshot = clone(fixtures[moleculeId]), mission = E.missions(snapshot).find(m => m.family === family);
    const data = {channel: 'namelecule-detective-lesson-v1', session: 'fixture_lesson_0123456789', command: 'load', requestId,
      attemptId: 'attempt-' + requestId, moleculeId, snapshot, missionId: mission.id, initialState: clone(raw), explanation: 'Εξήγηση μαθήματος.', ...extra};
    context.fire('message', {data, origin: context.location.origin, source: parent, ...options}); return data;
  };
  const complete = (actual = null, selection = null) => {
    const load = commands.at(-1); assert.equal(load.command, 'load');
    receive({...load, type: 'round', snapshot: clone(actual || fixtures[load.moleculeId])});
    const config = commands.at(-1); assert.equal(config.command, 'configure');
    const raw = selection || config.initialSelection || {atoms: [], bonds: []};
    receive({...config, type: 'configured', atoms: raw.atoms.slice().sort((a,b) => a-b), bonds: raw.bonds.slice().sort((a,b) => a-b), selectionRevision: ++nativeRevision});
    return config;
  };
  const select = (atoms, bonds = [], extra = {}, options = {}) => {
    const command = commands.findLast(c => c.command === 'configure');
    receive({...command, type: 'selection', atoms, bonds, selectionRevision: ++nativeRevision, ...extra}, options);
  };
  return {context, nodes, outer, commands, native, ready, complete, lessonLoad, select, snap, flush, receive, scrolls, frames, timers};
}

const h = boot();
check('no lesson ready before actual native inventory readiness', () => { assert.equal(h.outer.length, 0); });
check('one validated early load waits for native boot then forwards independent load', () => {
  h.lessonLoad(1); assert.equal(h.commands.length, 0); h.ready();
  assert.equal(h.outer[0].type, 'ready'); assert.equal(h.outer[0].requestId, undefined); assert.equal(h.commands.at(-1).command, 'load');
});
check('empty native configure acknowledges canonical mission and source snapshot proof', () => {
  h.complete(); h.flush(); const loaded = h.outer.find(m => m.type === 'loaded');
  assert.equal(loaded.missionId, E.missions(fixtures.ethane)[0].id); assert.equal(loaded.stateRevision, 0);
  assert.deepEqual(loaded.state, {atoms: [], bonds: [], attempts: 0, submitted: false});
  assert.deepEqual(loaded.snapshot, fixtures.ethane); assert.equal(h.nodes.get('next-mission').hidden, true);
  assert.equal(h.outer.find(m => m.type === 'reveal').purpose, 'entry');
});
check('actual check increments attempts, emits four raw fields, and keeps lesson next hidden', () => {
  h.select([1,2]); h.nodes.get('check-answer').fire('click'); h.flush();
  const packet = h.outer.findLast(m => m.type === 'state');
  assert.deepEqual(packet.state, {atoms: [1,2], bonds: [], attempts: 1, submitted: true}); assert.equal(packet.stateRevision, 2);
  assert.equal(h.snap().correct, true); assert.equal(h.nodes.get('next-mission').hidden, true);
  assert.equal(h.outer.findLast(m => m.type === 'reveal').purpose, 'feedback');
  assert.ok(h.nodes.get('feedback').children.some(n => n.textContent === 'Εξήγηση μαθήματος.'));
});
check('editing a correct selection resets submitted/feedback and preserves actual check count', () => {
  h.select([1]); assert.equal(h.snap().correct, false); assert.equal(h.nodes.get('feedback').hidden, true);
  assert.deepEqual(h.outer.findLast(m => m.type === 'state').state, {atoms: [1], bonds: [], attempts: 1, submitted: false});
});
check('stale native selection revision and wrong source/origin/session are ignored', () => {
  const before = h.snap(), size = h.outer.length;
  h.select([2], [], {selectionRevision: 0}); h.select([2], [], {}, {source: {}}); h.select([2], [], {}, {origin: 'http://wrong'}); h.select([2], [], {session: 'wrong'});
  assert.deepEqual(h.snap(), before); assert.equal(h.outer.length, size);
});
check('new load starts empty and configured restoration is exact rather than previous round leakage', () => {
  h.lessonLoad(2, 'butane', 'single-bonds'); const config = h.complete();
  assert.deepEqual(config.initialSelection, {atoms: [], bonds: []}); assert.equal(h.snap().attempts, 0); assert.equal(h.snap().submitted, false);
});
let request = 2;
for (const molecule of catalog.molecules) for (const mission of E.missions(fixtures[molecule.id])) {
  check('exact canonical mission and submitted raw restore: ' + molecule.id + '/' + mission.family, () => {
    const raw = {atoms: mission.kind === 'atoms' ? mission.accepted[0].slice().reverse() : [], bonds: mission.kind === 'bonds' ? mission.accepted[0].slice().reverse() : [], attempts: 3, submitted: true};
    h.lessonLoad(++request, molecule.id, mission.family, raw); const config = h.complete();
    assert.deepEqual(config.initialSelection, {atoms: raw.atoms, bonds: raw.bonds});
    const loaded = h.outer.findLast(m => m.type === 'loaded'); assert.equal(loaded.missionId, mission.id); assert.equal(loaded.state.attempts, 3); assert.equal(loaded.state.submitted, true);
    assert.equal(h.snap().correct, true); assert.equal(h.nodes.get('feedback').hidden, false); assert.equal(h.snap().missionId, mission.id);
  });
}
check('outer stale/replayed request, wrong origin/source/session cannot replace the round', () => {
  const before = h.snap(), count = h.commands.length;
  h.lessonLoad(request); h.lessonLoad(request+1, 'ethane', 'parent-chain', undefined, {}, {origin:'http://wrong'});
  h.lessonLoad(request+1, 'ethane', 'parent-chain', undefined, {}, {source:{}}); h.lessonLoad(request+1, 'ethane', 'parent-chain', undefined, {session:'wrong'});
  assert.deepEqual(h.snap(), before); assert.equal(h.commands.length, count);
});
for (const [label, raw] of [
  ['duplicate atom',{atoms:[1,1],bonds:[],attempts:1,submitted:true}], ['unknown atom',{atoms:[999],bonds:[],attempts:1,submitted:true}],
  ['wrong kind',{atoms:[],bonds:[1],attempts:1,submitted:true}], ['negative attempts',{atoms:[1],bonds:[],attempts:-1,submitted:true}],
  ['unattempted submission',{atoms:[1],bonds:[],attempts:0,submitted:true}], ['invalid submitted',{atoms:[],bonds:[],attempts:0,submitted:'true'}],
]) check('invalid initial state rejected with full outer identity: ' + label, () => {
  const data = h.lessonLoad(++request, 'ethane', 'parent-chain', raw), packet = h.outer.at(-1);
  assert.equal(packet.type, 'error'); for (const key of ['requestId','attemptId','moleculeId','missionId']) assert.equal(packet[key], data[key]);
});
check('known standalone-only molecule cannot enter the bounded lesson pool', () => {
  h.lessonLoad(++request, 'methyl_2_butane'); assert.equal(h.outer.at(-1).type, 'error');
});
check('native full name/source mismatch fails before native configure', () => {
  h.lessonLoad(++request); const load = h.commands.at(-1), count = h.commands.length;
  const bad = clone(fixtures.ethane); bad.sourceMOL += '\n';
  h.receive({...load,type:'round',snapshot:bad}); assert.equal(h.commands.length,count); assert.equal(h.snap().phase,'error'); assert.equal(h.outer.at(-1).type,'error');
});
check('native restore disagreement fails before loaded acknowledgement', () => {
  h.lessonLoad(++request,'ethane','parent-chain',{atoms:[1,2],bonds:[],attempts:1,submitted:true});
  const count = h.outer.filter(m => m.type === 'loaded').length; h.complete(null,{atoms:[],bonds:[]});
  assert.equal(h.snap().phase,'error'); assert.equal(h.outer.filter(m => m.type === 'loaded').length,count);
});
check('new round/error recovery and user input cancel delayed reveal; native Escape forwards exit', () => {
  h.lessonLoad(++request); h.complete(); const before = h.outer.filter(m => m.type === 'reveal').length;
  h.context.fire('wheel'); h.flush(); assert.equal(h.outer.filter(m => m.type === 'reveal').length,before); assert.equal(h.outer.findLast(m => m.type === 'scroll-interrupt').requestId,request);
  h.nodes.get('molecule-viewer').fire('load'); let prevented=false; h.native.fire('keydown',{key:'Escape',preventDefault(){prevented=true;}});
  assert.equal(prevented,true); assert.equal(h.outer.findLast(m => m.type === 'exit').requestId,request);
});
check('zoom/resize stay in the native protocol and raw state remains unchanged', () => {
  const before=h.snap(); h.nodes.get('zoom-in').fire('click'); assert.equal(h.commands.at(-1).command,'zoom');
  h.context.fire('resize'); h.flush(); assert.equal(h.commands.at(-1).command,'resize');
  assert.deepEqual(h.snap().atoms,before.atoms); assert.deepEqual(h.snap().bonds,before.bonds);
});
check('pagehide removes both message listeners and bfcache return starts a fresh native session', () => {
  const src=h.nodes.get('molecule-viewer').src; h.context.fire('pagehide'); assert.equal(h.commands.at(-1).command,'stop');
  assert.equal(h.context.listeners.get('message').length,0); h.context.fire('pageshow',{persisted:true});
  assert.equal(h.context.listeners.get('message').length,2); assert.notEqual(h.nodes.get('molecule-viewer').src,src);
});
const standalone=boot(false); standalone.ready();
check('standalone retains all27 inventory/selectors and sends no outer lesson messages', () => {
  assert.equal(standalone.nodes.get('molecule-select').options.length,27); assert.equal(standalone.commands.at(-1).moleculeId,'methane');
  standalone.complete(); standalone.select([1]); standalone.nodes.get('check-answer').fire('click');
  assert.equal(standalone.nodes.get('next-mission').hidden,false); standalone.nodes.get('next-mission').fire('click');
  assert.equal(standalone.commands.at(-1).moleculeId,'ethane'); assert.equal(standalone.outer.length,0);
  standalone.complete(); standalone.nodes.get('molecule-select').value='ethanol'; standalone.nodes.get('molecule-select').fire('change');
  assert.equal(standalone.commands.at(-1).moleculeId,'ethanol'); standalone.complete();
});
const result={recordedUTC:new Date().toISOString(),role:'Developer controlled execution',type:'DOM/native-message fixtures; not browser or visual execution',checks,passed:checks,records};
if(process.argv.includes('--write')) fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
