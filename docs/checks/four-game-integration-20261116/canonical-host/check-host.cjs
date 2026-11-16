/* Controlled protocol/native-function fixtures. No browser or visual claim. */
'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const repo = path.resolve(__dirname, '../../../..');
const read = file => fs.readFileSync(path.join(repo, file), 'utf8');
const native = read('js/mulermoc-nom-molview-56.js');
const core = read('js/mulermoc-nom-core-56.js');
const segment = (source, start, end) => source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start)));
const records = [], messages = [], timers = new Map(), microtasks = [], listeners = new Map();
let timerId = 0, graph;
const node = {id: 'comp5', textContent: '', classList: {contains: () => false}};
const svgHost = {clientWidth: 700, clientHeight: 360, classList: {add() {}}};
const root = {clientHeight: 360, dataset: {}};
const container = {querySelectorAll: () => [node]};
const add = (prefix, type, listener) => {
  const key = prefix + type;
  listeners.set(key, [...(listeners.get(key) || []), listener]);
};
const remove = (prefix, type, listener) => listeners.set(prefix + type, (listeners.get(prefix + type) || []).filter(fn => fn !== listener));
const parent = {postMessage: data => messages.push(JSON.parse(JSON.stringify(data)))};
const context = {
  URLSearchParams, Number, String, Array, Set, Date, Math, Infinity,
  parent, location: {origin: 'http://localhost:57115', search: '?session=fixture_session_0123456789'},
  document: {documentElement: root,
    querySelector: selector => selector.includes('nameCompContainer') ? container : selector.includes('SVG svg') ? {getScreenCTM: () => ({})} : null,
    querySelectorAll: () => [], getElementById: () => svgHost,
    addEventListener: (type, fn) => add('d:', type, fn), removeEventListener: (type, fn) => remove('d:', type, fn)},
  innerHeight: 360,
  addEventListener: (type, fn) => add('w:', type, fn), removeEventListener: (type, fn) => remove('w:', type, fn),
  setTimeout: fn => { const id = ++timerId; timers.set(id, fn); return id; }, clearTimeout: id => timers.delete(id),
  requestAnimationFrame: fn => { const id = ++timerId; timers.set(id, fn); return id; }, cancelAnimationFrame: id => timers.delete(id),
  queueMicrotask: fn => microtasks.push(fn),
  fMulerSelectClearLayer() {}, fMulerQuizRefresh() {}, fClearHighlights() {}, fShowNameAnalysis() {},
  fMulerSelectRepaint() {}, fUpdateSVG() {}, fResizeViewers() {}, fZoom2D() {},
  fViewerHeights2D3D: () => ({h2: 100, h3: 100, full: 200}),
  fNameAnalysisModeForBoxId: () => 'compCarbonsCount',
  fMulerSelectPurpose: () => context.MulerSelectPurpose || 'free',
  fMulerSelectGeom: () => ({med: 100, comp: [], verts: [], vassign: [],
    anchors: graph.atoms.map((atom, i) => ({atom: i, x: i * 1000, y: 1000, w: 100, h: 100})),
    groups: graph.bonds.map((bond, i) => ({bond: i, lines: [{x1: i * 1000, y1: 0, x2: i * 1000 + 500, y2: 0}]}))}),
  MULER_SELECT_ATOM_R: 0.3, MULER_SELECT_BOND_HW: 0.15,
  speechSynthesis: {cancel() {}}, Jmol: {script() {}}, jmolAppletNomeclature: {},
  selectedMol: 'methane', mode2D: 'expanded', modeSuffix: '_2D_Expanded', currentMolName: 'methane',
  nameMainCompList1: ['μεθ'], substNamingMode: 'school', etherNamingMode: 'iupac', mainChainMode: 'algorithmic',
  nameAnalysisMode: 'none', numberingFlag: false, narrateAnalysisFlag: false, rotateFlag: false,
};
context.window = context;
vm.createContext(context);
vm.runInContext(read('js/jsme-nick-nomeclature-moc2-data_56.js') + '\n' + read('js/MULERMOC_namelecule_alkanes_v1_data.js') + '\nglobalThis.nameExamples=nameExamples; Object.assign(nameExamples, nameExamplesCustom);', context);
for (const [id, entry] of Object.entries(context.nameExamples)) entry.structure2D_Expanded = entry.structure2D_Expanded || context.MOL2D[id]?.expanded;
vm.runInContext(segment(core, 'function fMolCountsLine(', '// Preserve atom/bond fields'), context);
for (const [start, end] of [
  ['function fMulerSelectState()', 'function fMulerSelectActive()'],
  ['function fMulerSelectMolKey()', 'function fMulerSelectPresenting()'],
  ['function fMulerSelectClear()', '// Bond line groups'],
  ['function fMulerSelectToggle(', '// Quiz target registry'],
  ['function fMulerQuizHydrogenParent(', 'function fMulerSelectPick('],
  ['function fMulerSelectPick(', 'function fMulerSelectToggle('],
]) vm.runInContext(segment(native, start, end), context);
context.fSelectMol = () => {
  graph = context.fParseMolV2000(context.nameExamples[context.selectedMol].structure2D_Expanded);
  context.allAtomsTypeList = graph.atoms.map(atom => atom.el.replace(/^\[([A-Z][a-z]?)\]$/, '$1'));
  context.bondList = graph.bonds.map(bond => Array.from(bond));
  context.currentMolName = node.textContent = context.selectedMol;
};
context.jsmeNomeclatureApplet = {
  molFile: () => context.nameExamples[context.selectedMol].structure2D_Expanded,
  getAtom: (mol, id) => ({label: context.allAtomsTypeList[id - 1]}),
  getBond: (mol, id) => ({atoms: context.bondList[id - 1].slice(0, 2), order: context.bondList[id - 1][2]}),
};
for (const entry of Object.values(context.nameExamples)) entry.classification = {chemicalClass: 'fixture', seriesKey: 'fixture'};
context.fSelectMol();
vm.runInContext(read('js/namelecule-molecular-detective-host.js'), context);
const flushMicro = () => { while (microtasks.length) microtasks.shift()(); };
const flush = () => { let limit = 50; while (timers.size && --limit) { const batch = [...timers.values()]; timers.clear(); batch.forEach(fn => fn()); flushMicro(); } assert.ok(limit > 0); };
let requestId = 0;
function command(type, data = {}, options = {}) {
  const packet = {channel: 'namelecule-molecular-detective-v1', session: 'fixture_session_0123456789',
    requestId: ++requestId, type, roundId: 'round-1', moleculeId: 'ethane', ...data};
  for (const fn of listeners.get('w:message') || []) fn({data: packet, origin: context.location.origin, source: parent, ...options});
  return packet;
}
let checks = 0;
function check(label, action) { action(); ++checks; records.push(label); }
const selection = () => JSON.parse(JSON.stringify(context.fMulerSelectState()));
check('startup sends ready once with expanded inventory', () => {
  assert.equal(messages.length, 1); assert.equal(messages[0].type, 'ready'); assert.ok(messages[0].inventory.length > 100);
});
const starterIds = require(path.join(repo, 'js/namelecule-molecular-detective-engine.js')).starterIds;
for (const moleculeId of starterIds) check('actual source expanded graph fixture: ' + moleculeId, () => {
  command('load', {moleculeId, roundId: moleculeId}); flush();
  const round = messages.at(-1); assert.equal(round.type, 'round'); assert.equal(round.snapshot.moleculeId, moleculeId);
  assert.equal(round.snapshot.atoms.length, graph.atoms.length); assert.equal(round.snapshot.bonds.length, graph.bonds.length);
  assert.deepEqual(round.snapshot.atoms.map(atom => atom.id), Array.from(graph.atoms, (atom, i) => i + 1));
  assert.deepEqual(round.snapshot.bonds.map(bond => [bond.a,bond.b,bond.order]), JSON.parse(JSON.stringify(graph.bonds)));
  assert.equal(context.MulerQuizTarget, null); assert.equal(context.MulerSelectPurpose, 'free');
});
command('load'); flush();
command('configure', {kind: 'atoms', missionId: 'm1'});
check('configure clears and activates exact mission', () => {
  assert.equal(messages.at(-1).type, 'configured'); assert.equal(messages.at(-1).missionId, 'm1');
  assert.equal(context.fMulerSelectState().active, true); assert.deepEqual(messages.at(-1).atoms, []);
});
const hydrogen = context.allAtomsTypeList.indexOf('H') + 1;
check('actual native free picker keeps raw H identity', () => {
  const pick = context.fMulerSelectPick((hydrogen - 1) * 1000, 1000);
  assert.equal(pick.atom, hydrogen); context.fMulerSelectToggle(pick); flushMicro();
  assert.deepEqual(selection().atoms2D, [hydrogen]); assert.deepEqual(messages.at(-1).atoms, [hydrogen]);
});
check('wrong-kind bond retains atom attempt', () => {
  context.fMulerSelectToggle({kind:'bond',bond:1}); flushMicro();
  assert.deepEqual(selection().atoms2D, [hydrogen]); assert.deepEqual(selection().bonds2D, []); assert.equal(messages.at(-1).note,'WRONG_KIND');
});
check('same raw atom toggles off', () => {
  context.fMulerSelectToggle({kind:'atom',atom:hydrogen}); flushMicro(); assert.deepEqual(selection().atoms2D, []);
});
command('configure', {kind: 'bonds', missionId: 'm2'});
context.fMulerSelectToggle({kind:'bond',bond:1}); flushMicro();
check('wrong-kind atom retains raw one-based bond identity', () => {
  context.fMulerSelectToggle({kind:'atom',atom:1}); flushMicro();
  assert.deepEqual(selection().bonds2D, [1]); assert.deepEqual(selection().atoms2D, []);
});
check('zoom and resize preserve attempt and return post-render state', () => {
  command('zoom', {direction:1,missionId:'m2'}); assert.equal(messages.at(-1).type,'zoom');
  command('resize', {missionId:'m2'}); assert.equal(messages.at(-1).type,'resize'); assert.deepEqual(messages.at(-1).bonds,[1]);
});
check('stale mission command cannot clear current attempt', () => {
  const count=messages.length; command('clear',{missionId:'m1'}); assert.equal(messages.length,count); assert.deepEqual(selection().bonds2D,[1]);
});
check('clear command emits fresh empty selection', () => {
  command('clear',{missionId:'m2'}); assert.equal(messages.at(-1).type,'selection'); assert.deepEqual(messages.at(-1).bonds,[]);
});
check('empty Escape also emits fresh selection', () => {
  const before=messages.at(-1).selectionRevision;
  for (const fn of listeners.get('d:keydown') || []) fn({key:'Escape',target:{tagName:'DIV'}});
  flushMicro(); assert.ok(messages.at(-1).selectionRevision>before);
});
check('configure supersedes queued prior-mission selection', () => {
  context.fMulerSelectToggle({kind:'bond',bond:1});
  command('configure',{kind:'atoms',missionId:'m3'}); const before=messages.length; flushMicro(); assert.equal(messages.length,before);
  assert.equal(messages.at(-1).missionId,'m3'); assert.deepEqual(selection().bonds2D,[]);
});
check('wrong origin/source/session and replayed request are ignored', () => {
  const before=messages.length, previous=context.NameleculeMolecularDetectiveHost.snapshot().lastId;
  command('clear',{missionId:'m3'},{origin:'http://elsewhere'});
  command('clear',{missionId:'m3'},{source:{}});
  command('clear',{session:'wrong',missionId:'m3'});
  command('clear',{requestId:previous,missionId:'m3'});
  assert.equal(messages.length,before); assert.equal(context.NameleculeMolecularDetectiveHost.snapshot().lastId,previous);
});
check('rapid loads emit only latest round and hide while loading', () => {
  command('load',{moleculeId:'butane',roundId:'rapid-a'});
  command('load',{moleculeId:'ethanol',roundId:'rapid-b'});
  assert.equal(root.dataset.molecularDetectiveVisible,'false'); const before=messages.length; flush();
  assert.deepEqual(messages.slice(before).map(message=>message.roundId),['rapid-b']);
  assert.equal(root.dataset.molecularDetectiveVisible,'true');
});
check('diagnostic snapshot reads current actual graph without changing selection', () => {
  const before=JSON.stringify(selection()); const snap=context.NameleculeMolecularDetectiveHost.getSnapshot();
  assert.equal(snap.moleculeId,'ethanol'); assert.equal(JSON.stringify(selection()),before);
});
check('name DOM mismatch fails closed', () => {
  node.textContent='wrong'; assert.throws(()=>context.NameleculeMolecularDetectiveHost.serializeName(), /roundtrip/); node.textContent=context.currentMolName;
});
check('all emitted selection revisions are globally monotonic', () => {
  const revisions=messages.filter(message=>message.selectionRevision).map(message=>message.selectionRevision);
  assert.ok(revisions.every((value,i)=>!i || value>revisions[i-1]));
});

check('ready snapshot carries exact native source MOL bytes', () => {
  assert.equal(context.NameleculeMolecularDetectiveHost.getSnapshot().sourceMOL, context.nameExamples.ethanol.structure2D_Expanded);
});
command('load'); flush();
check('configure restores and paints actual atom state before acknowledgement', () => {
  let painted;
  context.fUpdateSVG = () => { painted=selection(); };
  command('configure',{kind:'atoms',missionId:'restore-atoms',initialSelection:{atoms:[2,1],bonds:[]}});
  assert.equal(messages.at(-1).type,'configured'); assert.deepEqual(messages.at(-1).atoms,[1,2]);
  assert.deepEqual(painted.atoms2D,[2,1]); assert.equal(painted.molKey,'ethane|expanded');
  assert.deepEqual(selection().atoms2D,[2,1]); assert.deepEqual(selection().bonds2D,[]);
});
for (const [label, invalid] of [
  ['duplicate atom',{atoms:[1,1],bonds:[]}], ['duplicate bond',{atoms:[],bonds:[1,1]}],
  ['unknown atom',{atoms:[999],bonds:[]}], ['zero atom',{atoms:[0],bonds:[]}],
  ['negative atom',{atoms:[-1],bonds:[]}], ['fraction atom',{atoms:[1.2],bonds:[]}],
  ['numeric-string atom',{atoms:['1'],bonds:[]}], ['wrong kind',{atoms:[],bonds:[1]}],
  ['missing array',{atoms:[1]}], ['null',null]
]) check('invalid restore '+label+' cannot change selection or mission', () => {
  const before=JSON.stringify(selection());
  command('configure',{kind:'atoms',missionId:'bad-'+label,initialSelection:invalid});
  assert.equal(messages.at(-1).type,'error'); assert.equal(JSON.stringify(selection()),before);
  assert.equal(context.NameleculeMolecularDetectiveHost.snapshot().missionId,'restore-atoms');
});
check('same ready round reconfigure restores bond state and clears atoms', () => {
  command('configure',{kind:'bonds',missionId:'restore-bonds',initialSelection:{atoms:[],bonds:[1]}});
  assert.equal(messages.at(-1).type,'configured'); assert.deepEqual(messages.at(-1).bonds,[1]);
  assert.deepEqual(selection().atoms2D,[]); assert.deepEqual(selection().bonds2D,[1]);
});
check('stale round restore cannot alter current native state', () => {
  const before=JSON.stringify(selection());
  command('configure',{roundId:'old-round',kind:'atoms',missionId:'old',initialSelection:{atoms:[1],bonds:[]}});
  assert.equal(messages.at(-1).type,'error'); assert.equal(messages.at(-1).code,'ROUND_NOT_READY');
  assert.equal(JSON.stringify(selection()),before);
});
check('omitted restore preserves existing standalone empty configure behavior', () => {
  command('configure',{kind:'atoms',missionId:'empty'});
  assert.equal(messages.at(-1).type,'configured'); assert.deepEqual(messages.at(-1).atoms,[]); assert.deepEqual(messages.at(-1).bonds,[]);
});
check('restore cannot claim success if native repaint discards IDs', () => {
  context.fUpdateSVG=()=>{context.fMulerSelectState().atoms2D=[];};
  command('configure',{kind:'atoms',missionId:'paint-loss',initialSelection:{atoms:[1],bonds:[]}});
  assert.equal(messages.at(-1).type,'error'); assert.match(messages.at(-1).detail,/not applied/);
  context.fUpdateSVG=()=>{};
});
check('restore fails when actual loaded indexed graph differs', () => {
  const original=context.jsmeNomeclatureApplet.getBond;
  context.jsmeNomeclatureApplet.getBond=(m,id)=>id===1 ? {atoms:[1,3],order:1} : original(m,id);
  const before=JSON.stringify(selection());
  command('configure',{kind:'atoms',missionId:'bad-graph',initialSelection:{atoms:[1],bonds:[]}});
  assert.equal(messages.at(-1).type,'error'); assert.match(messages.at(-1).detail,/identity mismatch/);
  assert.equal(JSON.stringify(selection()),before); context.jsmeNomeclatureApplet.getBond=original;
});
check('stop acknowledges, hides, restores native wrappers and removes protocol listeners', () => {
  command('stop'); assert.equal(messages.at(-1).type,'stopped'); assert.equal(context.NameleculeMolecularDetectiveHost.snapshot().stopped,true);
  assert.equal(root.dataset.molecularDetectiveVisible,'false'); assert.equal((listeners.get('w:message')||[]).length,0);
});
const result={recordedUTC:new Date().toISOString(),role:'Developer controlled execution',type:'controlled native-function/protocol fixtures; not browser execution',checks,passed:checks,records};
if(process.argv.includes('--write')) fs.writeFileSync(path.join(__dirname,'host-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
