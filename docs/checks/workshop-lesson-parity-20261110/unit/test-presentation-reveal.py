"""Behavioral checks of actual shared exports; synthetic page geometry, no native animation."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
TARGET = ROOT / 'docs/checks/workshop-lesson-parity-20261110/verification-target.json'
SOURCE_PATH = ROOT / 'js/namelecule-game-repair.js'
DATA_PATH = ROOT / 'games/data/name-repair-alkanes.json'
source = SOURCE_PATH.read_text()
data = json.loads(DATA_PATH.read_text())
expected = json.loads(TARGET.read_text())
source_hash = hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()
data_hash = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
assert source_hash == expected['targetFiles']['js/namelecule-game-repair.js']
assert data_hash == expected['protected']['games/data/name-repair-alkanes.json']
js = 'const global = globalThis;\nglobal.window = global;\n' + source + '\n'
js += 'const authoredData = ' + json.dumps(data, ensure_ascii=False) + ';\n'
js += r'''
let checks = 0;
const labels = [];
function check(ok, label) { if (!ok) throw Error(label); checks++; labels.push(label); }
function equal(a, b, label) { check(JSON.stringify(a) === JSON.stringify(b), label); }
function clone(v) { return JSON.parse(JSON.stringify(v)); }
function freeze(v) { if (v && typeof v === 'object') { Object.values(v).forEach(freeze); Object.freeze(v); } return v; }
let focusCalls = 0, storageCalls = 0;
for (const key of ['localStorage', 'sessionStorage']) global[key] = {
  getItem() { storageCalls++; throw Error('unexpected storage read'); },
  setItem() { storageCalls++; throw Error('unexpected storage write'); },
  removeItem() { storageCalls++; throw Error('unexpected storage delete'); }
};
const E = NameleculeRepairEngine, G = NameleculeRepairGame;
check(typeof document === 'undefined' && typeof G.presentationForRound === 'function' && typeof G.createResponseRevealer === 'function',
  'actual exports load with document undefined');
const authored = freeze(authoredData.sets.flatMap(set => set.rounds));
const expectedMissions = {
  'unbranched-parent-four': 'parent-length', 'unbranched-parent-five': 'parent-length',
  'unbranched-single-bond': 'bond-type', 'number-from-nearest': 'branch-locants',
  'two-methyl-groups': 'branch-multiplier', 'alphabetical-branches': 'alphabetical-order'
};
const expectedObjectives = {
  'parent-length': 'Έλεγξε το μήκος της κύριας αλυσίδας και το συνθετικό που το δηλώνει.',
  'bond-type': 'Έλεγξε το είδος των δεσμών μεταξύ ατόμων C.',
  'branch-locants': 'Έλεγξε τα σημεία σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
  'branch-multiplier': 'Έλεγξε πόσες ίδιες διακλαδώσεις υπάρχουν και πώς δηλώνεται το πλήθος τους.',
  'alphabetical-order': 'Έλεγξε την αλφαβητική σειρά των διαφορετικών διακλαδώσεων.'
};
const expectedReminders = {
  'parent-length': 'Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.',
  'bond-type': 'Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.',
  'branch-locants': 'Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
  'branch-multiplier': 'Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων.'
};
function solution(round) {
  const state = E.createRoundState(round);
  if (round.kind === 'replace') { state.selectedPartId = round.targetPartId; state.selectedValue = round.correctValue; }
  else state.order = round.correctOrder.slice();
  return state;
}
for (const original of authored) {
  const prefix = original.id + ': ', snapshot = JSON.stringify(original);
  const preset = G.presentationForRound(original, {difficulty: 'basic'}), shown = preset.round;
  check(shown !== original && preset.emphasizeObjective && preset.compactDiagramZoom, prefix + 'shared prominent objective and compact zoom flags');
  check(shown.objective === expectedObjectives[expectedMissions[original.id]] && shown.objective !== original.objective,
    prefix + 'authored basic mission objective is explicit');
  const reminder = expectedReminders[expectedMissions[original.id]];
  check(shown.feedback.wrongPart === original.feedback.wrongPart + (original.kind === 'replace' && reminder ? ' ' + reminder : ''),
    prefix + 'wrong-part feedback adds only approved non-answer mission reminder');
  equal(E.evaluateRepair(original, solution(original)), E.evaluateRepair(shown, solution(shown)), prefix + 'exact correct evaluation and success text unchanged');
  check(E.evaluateRepair(shown, solution(shown)).kind === 'correct' && E.candidateName(shown, solution(shown)) === original.correctName,
    prefix + 'correct repair still assembles canonical correct name');
  equal(E.evaluateRepair(original, E.createRoundState(original)), E.evaluateRepair(shown, E.createRoundState(shown)),
    prefix + 'initial/incomplete evaluation unchanged');
  if (original.kind === 'replace') {
    const selections = original.choices.map(choice => {
      const s = E.createRoundState(original); s.selectedPartId = original.targetPartId; s.selectedValue = choice.value; return s;
    });
    equal(selections.map(s => E.evaluateRepair(original, s)), selections.map(s => E.evaluateRepair(shown, s)),
      prefix + 'every authored replacement choice evaluation unchanged');
  } else {
    const wrong = E.createRoundState(original); wrong.order.reverse();
    equal(E.evaluateRepair(original, wrong), E.evaluateRepair(shown, wrong), prefix + 'reordered evaluation unchanged');
  }
  const restored = clone(shown);
  restored.objective = original.objective; restored.asset = original.asset; restored.diagramAlt = original.diagramAlt;
  restored.feedback = clone(original.feedback);
  equal(restored, original, prefix + 'all canonical non-display fields unchanged');
  equal(G.presentationForRound(shown, {difficulty:'basic'}), preset, prefix + 'presentation and reminder are idempotent');
  const challenge = G.presentationForRound(original, {difficulty:'challenge'}).round;
  check(challenge.objective === original.objective && challenge.feedback === original.feedback,
    prefix + 'challenge preserves original objective and neutral wrong-part feedback');
  equal(original, JSON.parse(snapshot), prefix + 'frozen canonical input remains byte-equivalent');
}
check(authored.length === 6, 'all six canonical authored questions tested');
for (const [family, reminder] of Object.entries(expectedReminders)) {
  const generated = clone(authored[0]);
  generated.id = 'generated-variable-id-' + family; generated.fault = {kind:family};
  generated.objective = 'Βρες και διόρθωσε το μέρος που διαφωνεί με τη δομή.';
  const snapshot = JSON.stringify(generated); freeze(generated);
  const shown = G.presentationForRound(generated, {difficulty:'basic'}).round;
  check(shown.objective === generated.objective && shown.feedback.wrongPart === generated.feedback.wrongPart + ' ' + reminder,
    family + ': generated semantic fault metadata controls reminder independently of authored ID');
  equal(G.presentationForRound(generated).round, shown, family + ': omitted options use basic presentation');
  equal(G.presentationForRound(generated, {difficulty:'challenge'}).round, generated,
    family + ': generated challenge objective/feedback remain neutral');
  equal(G.presentationForRound(shown, {difficulty:'basic'}).round, shown, family + ': generated reminder idempotent');
  check(JSON.stringify(generated) === snapshot, family + ': generated canonical input unchanged');
}
for (const id of ['future-question', '__proto__', 'constructor', 'toString']) {
  const unknown = clone(authored[0]); unknown.id = id;
  equal(G.presentationForRound(freeze(unknown), {difficulty:'basic'}).round, unknown, id + ': unknown/prototype-like ID cannot invent a mission');
  for (const family of ['future-family', '__proto__', 'constructor']) {
    const unknownFamily = clone(unknown); unknownFamily.fault = {kind:family};
    equal(G.presentationForRound(freeze(unknownFamily), {difficulty:'basic'}).round, unknownFamily,
      id + '/' + family + ': unsupported metadata cannot invent a mission');
  }
}
const orderWithMetadata = clone(authored[5]); orderWithMetadata.id = 'generated-order'; orderWithMetadata.fault = {kind:'parent-length'};
equal(G.presentationForRound(freeze(orderWithMetadata)).round.feedback, orderWithMetadata.feedback, 'order presentation does not append replacement-only reminder');
const largest = G.presentationForRound(authored[5]);
check(largest.diagramRepresentation === 'condensed' && largest.round.asset === 'assets/name-repair/condensed/ethyl_3_dimethyl_2_5_hexane.svg',
  'exact existing largest-molecule condensed asset selected');
check(largest.round.diagramAlt === 'Συνεπτυγμένος συντακτικός τύπος αλκανίου. Φαίνονται οι δεσμοί μεταξύ ατόμων C και οι ομάδες CH₃, CH₂ και CH.',
  'condensed alt names representation without numerical/name solution');
for (const round of authored.slice(0, 5)) {
  const p = G.presentationForRound(round);
  check(p.diagramRepresentation === 'expanded' && p.round.asset === round.asset && p.round.diagramAlt === round.diagramAlt,
    round.id + ': ordinary molecule asset/alt/expanded representation preserved');
}
const arbitraryLarge = clone(authored[0]); arbitraryLarge.id = 'new-largest-round'; arbitraryLarge.moleculeId = authored[5].moleculeId;
check(G.presentationForRound(arbitraryLarge).diagramRepresentation === 'condensed', 'largest representation depends on molecule, not question ID/kind');

function fixture(config = {}) {
  let current = config.current || 0, maximum = config.maximum === undefined ? 2400 : config.maximum;
  let active = true, reduced = !!config.reduced;
  const calls = [], entries = [], removals = [], handlers = new Map(), nodes = new Set();
  const target = {
    addEventListener(type, handler, options) { entries.push({type,handler,options}); handlers.set(type,handler); },
    removeEventListener(type, handler, options) {
      removals.push({type,handler,options});
      if (handlers.get(type) === handler) handlers.delete(type);
    },
    emit(type) { const callback = handlers.get(type); if (callback) callback({type}); }
  };
  const host = { contains(node) { return nodes.has(node); } };
  const viewport = {top:12,bottom:588};
  global.matchMedia = query => ({matches: query === '(prefers-reduced-motion: reduce)' && reduced});
  const options = {
    host, active:() => active, interruptTarget:target,
    viewport:() => viewport, scrollTop:() => current, maxScroll:() => maximum,
    scrollTo(destination, behavior) { calls.push({destination,behavior}); current = destination; }
  };
  const api = G.createResponseRevealer(options);
  function node(y, height=50) {
    const result = {isConnected:true, focus() { focusCalls++; },
      getBoundingClientRect() { return {top:y-current,bottom:y+height-current,height}; }};
    nodes.add(result); return result;
  }
  return {api,calls,target,entries,removals,handlers,nodes,viewport,node,
    y:() => current, setY:y => {current=y;}, setMax:y => {maximum=y;},
    setActive:v => {active=v;}, setReduced:v => {reduced=v;}};
}
function request(f, start, end) { f.api.reveal({start,end:end || start,reason:'pure-page-response'}); }
{
  const f = fixture(), visible = f.node(200);
  request(f,visible); check(f.calls.length === 0 && f.y() === 0, 'page: already-visible response is a no-op');
  check(f.entries.map(e=>e.type).join(',') === 'wheel,touchstart,pointerdown,keydown,pagehide' && f.entries.every(e=>e.options.passive === true),
    'page: exactly five passive manual-interruption listeners installed');
  f.api.destroy();
}
{
  const f=fixture(), low=f.node(700); request(f,low);
  equal(f.calls,[{destination:162,behavior:'smooth'}], 'page: short below response moves only enough to show its bottom');
  check(low.getBoundingClientRect().top >= 12 && low.getBoundingClientRect().bottom === 588, 'page: short below range fully fits viewport');
  request(f,low); equal(f.calls.at(-1),{destination:162,behavior:'instant'}, 'page: next visible request cancels prior motion without new smooth jump');
  const n=f.calls.length;request(f,low);check(f.calls.length===n,'page: repeated visible request after cancellation writes nothing');f.api.destroy();
}
{
  const f=fixture({current:500}), high=f.node(200);request(f,high);
  check(f.y()===188 && high.getBoundingClientRect().top===12 && high.getBoundingClientRect().bottom<=588,
    'page: response above viewport aligns its start and fits');f.api.destroy();
}
{
  const f=fixture(), start=f.node(700,30), end=f.node(820,40);request(f,start,end);
  check(f.y()===272 && start.getBoundingClientRect().top>=12 && end.getBoundingClientRect().bottom===588,
    'page: short response through following action fits as one measured range');f.api.destroy();
}
{
  const f=fixture(), tall=f.node(800,1000);request(f,tall);
  check(f.y()===788 && tall.getBoundingClientRect().top===12, 'page: tall explanation reveals its start rather than skipping to end');f.api.destroy();
}
{
  const f=fixture({maximum:100});request(f,f.node(5000));check(f.y()===100,'page: destination clamps to measured lower scroll extent');f.api.destroy();
  const top=fixture({current:10});request(top,top.node(0));check(top.y()===0,'page: destination clamps to zero');top.api.destroy();
  const tiny=fixture({maximum:.5});request(tiny,tiny.node(800));check(tiny.calls.length===0,'page: subpixel-only destination does not write');tiny.api.destroy();
}
{
  const f=fixture({reduced:true});request(f,f.node(800));
  equal(f.calls,[{destination:262,behavior:'instant'}], 'page: reduced motion uses immediate measured destination');
  const n=f.calls.length;f.target.emit('pointerdown');f.api.stop();check(f.calls.length===n,'page: no pending animation to cancel after reduced-motion reveal');f.api.destroy();
}
for (const failure of ['inactive','missing','disconnected-start','disconnected-end','outside-start','outside-end','hidden-start','hidden-end','nonfinite-start','nonfinite-end','nonfinite-viewport','invalid-viewport','nonfinite-extent','nonfinite-current','missing-rect']) {
  const f=fixture(), start=f.node(800), end=f.node(950);
  if(failure==='inactive')f.setActive(false);
  if(failure==='disconnected-start')start.isConnected=false;
  if(failure==='disconnected-end')end.isConnected=false;
  if(failure==='outside-start')f.nodes.delete(start);
  if(failure==='outside-end')f.nodes.delete(end);
  if(failure==='hidden-start')start.getBoundingClientRect=()=>({top:800,bottom:800,height:0});
  if(failure==='hidden-end')end.getBoundingClientRect=()=>({top:950,bottom:950,height:0});
  if(failure==='nonfinite-start')start.getBoundingClientRect=()=>({top:NaN,bottom:NaN,height:NaN});
  if(failure==='nonfinite-end')end.getBoundingClientRect=()=>({top:Infinity,bottom:Infinity,height:NaN});
  if(failure==='nonfinite-viewport')f.viewport.top=NaN;
  if(failure==='invalid-viewport')f.viewport.bottom=f.viewport.top;
  if(failure==='nonfinite-extent')f.setMax(NaN);
  if(failure==='nonfinite-current')f.setY(NaN);
  if(failure==='missing-rect')start.getBoundingClientRect=undefined;
  if(failure==='missing'){f.api.reveal(null);f.api.reveal({});}else request(f,start,end);
  check(f.calls.length===0,'page: rejects '+failure+' request');f.api.destroy();
}
for (const event of ['wheel','touchstart','pointerdown','keydown','pagehide']) {
  const f=fixture();f.target.emit(event);check(f.calls.length===0,event+': idle interruption writes nothing');
  request(f,f.node(900));const y=f.y();f.target.emit(event);
  equal(f.calls,[{destination:362,behavior:'smooth'},{destination:y,behavior:'instant'}],event+': pending motion cancelled at current position');
  f.target.emit(event);check(f.calls.length===2,event+': repeated interruption does not cancel twice');f.api.destroy();
}
{
  const f=fixture(), low=f.node(1000);request(f,low);const y=f.y();f.api.destroy();
  equal(f.calls.at(-1),{destination:y,behavior:'instant'},'page: destroy cancels pending motion');
  check(f.removals.length===5&&f.handlers.size===0&&f.removals.every((entry,i)=>entry.type===f.entries[i].type&&entry.handler===f.entries[i].handler&&entry.options===f.entries[i].options),
    'page: destroy removes all five listeners with matching handler/options');
  const n=f.calls.length;f.api.reveal({start:f.node(2000)});f.api.stop();f.api.destroy();f.target.emit('pointerdown');
  check(f.calls.length===n&&f.removals.length===5,'page: destroyed helper ignores later reveal/stop/events and repeat destroy');
}
check(focusCalls===0&&storageCalls===0,'pure presentation/reveal helpers produce no focus or storage side effects');
print(JSON.stringify({completed:true,checks,authoredRounds:authored.length,labels,
  limits:['Actual frozen NameleculeRepairGame exports and canonical authored data execute in system JavaScriptCore with document undefined.',
    'Page viewport, element rectangles, connected/containment state, event target, matchMedia and scrollTo are declared doubles.',
    'Synthetic scrollTo applies destinations synchronously; no native animation, browser layout, rendering or interaction claim.']}));
'''
script = HERE / 'presentation-reveal-harness.js'
script.write_text(js)
result = subprocess.run([JSC, str(script.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
if result.returncode:
    (HERE / 'presentation-reveal-failure.txt').write_text(result.stdout + result.stderr)
    raise SystemExit(result.stdout + result.stderr)
report = json.loads(result.stdout.strip().splitlines()[-1])
assert hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() == source_hash, 'production source changed during check'
assert hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() == data_hash, 'canonical authored data changed during check'
report['sourceSHA256'] = {'js/namelecule-game-repair.js': source_hash,
                          'games/data/name-repair-alkanes.json': data_hash}
report['harnessSHA256'] = hashlib.sha256(script.read_bytes()).hexdigest()
report['runnerSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
report['retainedHarnessFailure'] = 'presentation-reveal-failure.txt: initial test expectation included the intentional largest condensed asset change; corrected to compare feedback only. No production correction.'
(HERE / 'presentation-reveal-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'completed': True, 'checks': report['checks'], 'authoredRounds': report['authoredRounds']}))
