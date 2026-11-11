/* Adapter contract tests using synthetic DOM/native-viewer doubles. These do
 * not constitute chemistry, rendering or actual JSmol verification. Run with
 * macOS JavaScriptCore from the repository root. */
const hostSource = readFile('js/namelecule-name-builder-host.js');
let assertions = 0;
function assert(value, message) {
  if (!value) throw new Error(message);
  assertions++;
}
globalThis.window = globalThis;
globalThis.location = {search: '?session=unit-test-session-0123456789', origin: 'https://example.test'};
globalThis.innerHeight = 385;
globalThis.URLSearchParams = class { get(key) { return key === 'session' ? 'unit-test-session-0123456789' : null; } };
globalThis.URL = class { constructor(path) { this.href = 'https://example.test/' + path; } };
const posted = [];
globalThis.parent = {postMessage: (data, origin) => posted.push({data, origin})};
const listeners = {};
globalThis.addEventListener = (type, fn) => { listeners[type] = fn; };
globalThis.removeEventListener = (type, fn) => { if (listeners[type] === fn) delete listeners[type]; };
let serial = 0;
const timers = new Map();
globalThis.setTimeout = fn => { const id = ++serial; timers.set(id, fn); return id; };
globalThis.clearTimeout = id => timers.delete(id);
globalThis.requestAnimationFrame = setTimeout;
globalThis.cancelAnimationFrame = clearTimeout;
function flush() {
  const pending = [...timers.entries()];
  for (const [id, fn] of pending) if (timers.delete(id)) fn();
}
function node(id, text, kind = 'nameCompBox', hidden = false) {
  return {id, textContent: text, classList: {contains: cls => cls === kind || (hidden && cls === 'comp-hidden')}};
}
let nodes = [];
globalThis.document = {
  baseURI: 'https://example.test/', documentElement: {dataset: {}, clientHeight: 385},
  querySelector: selector => selector.includes('nameCompContainer') ? {querySelectorAll: () => nodes} : {},
  addEventListener() {}, removeEventListener() {},
};
globalThis.speechSynthesis = {cancel() {}};
let nativeSelectCount = 0;
let zoomCount = 0;
let resizeCount = 0;
let nameExamples = {
  methane: {structure2D_Condensed: 'a', structure2D_Expanded: 'b', file3D: 'methane.sdf',
    classification: {seriesKey: 'alkanes', carbonCount: 1}},
  sample: {structure2D_Condensed: 'a', structure2D_Expanded: 'b', structure2D_Skeletal: 'c', file3D: 'sample.sdf',
    classification: {seriesKey: 'ester', carbonCount: 4}},
};
let selectedMol = 'methane';
let jsmeNomeclatureApplet = {};
let nameMainCompList1 = ['μεθ', 'αιθ', 'προπ', 'βουτ'];
let mainChainAtomsList = [1];
let substNamingMode, etherNamingMode, mainChainMode, nameAnalysisMode, numberingFlag,
  narrateAnalysisFlag, rotateFlag, mode2D, modeSuffix;
let currentMolName = '';
function fShowNameAnalysis() {
  // Deliberately neutral strings: these test serialization, not chemistry.
  nodes = selectedMol === 'methane'
    ? [node('comp5', 'Α'), node('comp6', 'β')]
    : [node('comp5', 'Γ'), node('space', '\u00a0', 'nameCompSpace'), node('comp10', 'δε')];
  currentMolName = selectedMol === 'methane' ? 'Αβ' : 'Γ δε';
}
function fSelectMol() { nativeSelectCount++; fShowNameAnalysis(); }
function fLoadMol2D() { fShowNameAnalysis(); }
function fClearHighlights() {}
function showAtomSymbols3D() {}
function rotate3D() {}
function fResizeViewers() { resizeCount++; }
function fViewerHeights2D3D() { return {h2: 115, h3: 0, full: 325}; }
function fZoom2D() { zoomCount++; }
function fZoom3D() { zoomCount++; }
function fLoadMol3D() {}
function fFetchAndParse3D() {}
let jmolAppletNomeclature = {};
let live3D = false;
let modelFile = 'methane.sdf';
let modelSymbol = 'C';
let queueMarker = 0;
let allAtomsTypeList3D = ['C'];
let bondList3D = [];
function fJSmolLive() { return live3D; }
globalThis.Jmol = {
  getPropertyAsArray(applet, property) {
    if (property === 'modelInfo') return {models: [{file: 'https://example.test/' + modelFile}]};
    if (property === 'atomInfo') return [{atomno: 1, sym: modelSymbol}];
    return [];
  },
  script(applet, command) {
    const match = /nameBuilderRevision = (\d+)/.exec(command);
    if (match) queueMarker = +match[1];
  },
  evaluateVar() { return queueMarker; },
};
fShowNameAnalysis();
eval(hostSource);
const host = window.NameleculeNameBuilderHost;
function command(data, extra = {}) {
  listeners.message?.({origin: location.origin, source: parent,
    data: {channel: 'namelecule-name-builder-v1', session: 'unit-test-session-0123456789', ...data}, ...extra});
}
function last() { return posted[posted.length - 1].data; }
assert(last().type === 'ready' && last().inventory.length === 2, 'Ready inventory');
assert(last().requestId === 0 && last().roundId === null && last().moleculeId === null, 'Ready IDs');
assert(last().inventory.every(item => !('correctName' in item)), 'No inventory target names');
const originalCount = posted.length;
command({command: 'load', requestId: 50, roundId: 'r1', moleculeId: 'sample', representation: 'condensed'}, {origin: 'https://other.test'});
command({command: 'load', requestId: 50}, {source: {}});
command({command: 'load', requestId: 50, session: 'wrong'});
assert(posted.length === originalCount && host.snapshot().lastId === 0, 'Reject foreign origin/source/session');
command({command: 'load', requestId: 1, roundId: 'r1', moleculeId: 'sample', representation: 'condensed'});
assert(last().type === 'busy' && document.documentElement.dataset.nameBuilderVisible === 'false', 'Busy hides old drawing');
flush();
assert(last().type === 'round' && last().correctName === 'Γ δε', 'Native name roundtrip');
assert(last().pieces[1].separatorBefore === ' ', 'Explicit word separator');
assert(fViewerHeights2D3D().h2 === 385 && fViewerHeights2D3D().h3 === 0, 'Short embedded frame uses actual2D viewport');
document.documentElement.clientHeight = 620;
assert(fViewerHeights2D3D().h2 === 620, 'Viewport budget follows iframe resize');
document.documentElement.clientHeight = 385;
assert(last().requestId === 1 && last().roundId === 'r1' && last().moleculeId === 'sample', 'Round correlation');
const selects = nativeSelectCount;
command({command: 'representation', requestId: 2, roundId: 'r1', moleculeId: 'sample', representation: 'skeletal'});
flush();
assert(last().type === 'representation' && nativeSelectCount === selects, 'Form switch does not generate round');
assert(last().correctName === 'Γ δε' && host.snapshot().representation === 'skeletal', 'Same target on form switch');
command({command: 'representation', requestId: 3, roundId: 'other', moleculeId: 'sample', representation: 'expanded'});
assert(last().code === 'ROUND_MISMATCH' && host.snapshot().representation === 'skeletal', 'Reject other round');
command({command: 'load', requestId: 4, roundId: 'r2', moleculeId: 'methane', representation: 'skeletal'});
assert(last().code === 'INVALID_ROUND', 'Reject missing representation');
const beforeReplay = posted.length;
command({command: 'load', requestId: 2, roundId: 'r2', moleculeId: 'methane', representation: 'condensed'});
assert(posted.length === beforeReplay, 'Reject replayed request');
command({command: 'load', requestId: 5, roundId: 'r2', moleculeId: 'methane', representation: 'condensed'});
command({command: 'load', requestId: 6, roundId: 'r3', moleculeId: 'sample', representation: 'expanded'});
flush();
assert(last().type === 'round' && last().requestId === 6, 'Latest rapid load completes');
assert(!posted.some(item => item.data.type === 'round' && item.data.requestId === 5), 'Stale completion suppressed');
command({command: 'zoom', requestId: 7, roundId: 'r3', moleculeId: 'sample', direction: 1});
assert(last().type === 'zoom' && zoomCount === 1, 'Native zoom dispatch');
command({command: 'resize', requestId: 8, roundId: 'r3', moleculeId: 'sample'});
assert(last().type === 'resize' && resizeCount > 0, 'Native resize dispatch');
command({command: 'representation', requestId: 9, roundId: 'r3', moleculeId: 'sample', representation: '3d'});
flush();
assert(last().type === 'busy' && !host.snapshot().ready, '3D canvas alone never acknowledges');
live3D = true;
flush();
assert(last().type === 'busy', 'Wrong loaded 3D file never acknowledges');
modelFile = 'sample.sdf';
modelSymbol = 'O';
flush();
assert(last().type === 'busy', 'Wrong loaded atom graph never acknowledges');
modelSymbol = 'C';
flush();
assert(last().type === 'representation' && last().requestId === 9 && queueMarker > 0, 'Loaded graph plus queue marker acknowledges');
assert(fViewerHeights2D3D().h2 === 0 && fViewerHeights2D3D().h3 === 385, '3D uses same complete iframe viewport');
nodes[0] = node('comp5', 'WRONG');
let mismatchRejected = false;
try { host.serializeName(); } catch (failure) { mismatchRejected = true; }
assert(mismatchRejected, 'Fail closed on serialized-name mismatch');
command({command: 'stop', requestId: 10, roundId: 'r3', moleculeId: 'sample'});
assert(last().type === 'stopped' && host.snapshot().stopped && !listeners.message, 'Stop cleanup');
assert(fViewerHeights2D3D().h2 === 115, 'Stop restores native budget helper');
assert(posted.every(item => item.origin === location.origin), 'Reply target origin');
print(JSON.stringify({checks: assertions, status: 'passed', evidence: 'Synthetic adapter protocol/DOM doubles only; no browser or chemistry claim'}));
