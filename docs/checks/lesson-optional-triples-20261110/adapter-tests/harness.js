const global = globalThis;
const analyses = catalog.molecules.map(m => analyze(m, catalog.engineSHA256));
const digest = Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(x => parseInt(x, 16)));
const recipe = { version: 1, setId: 'alkanes-unbranched', difficulty: 'basic', roundCount: 3,
  generatorVersion: '1.0.0', catalogRevision: catalog.revision, engineSHA256: catalog.engineSHA256 };
const branched = { ...recipe, setId: 'alkanes-branched' };
let checks = 0;
function check(value, label) { if (!value) throw Error(label); checks++; }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function equal(a, b, label) { check(JSON.stringify(a) === JSON.stringify(b), label); }
function equalActiveReceipt(a, b, label) {
  equal({ ...a, states: a.states.slice(0, a.currentRound + 1) },
    { ...b, states: b.states.slice(0, b.currentRound + 1) }, label);
}
function throws(fn, label) { let caught = false; try { fn(); } catch (_) { caught = true; } check(caught, label); }
async function until(predicate, label) { for (let i = 0; i < 100 && !predicate(); i++) await Promise.resolve(); check(predicate(), label); }
async function drain() { for (let i = 0; i < 30; i++) await Promise.resolve(); }
class FakeNode {
  constructor(tag) { this.tagName = tag; this.children = []; this.attrs = {}; this.handlers = {}; this.parent = null; }
  get isConnected() { return this.root === true || !!(this.parent && this.parent.isConnected); }
  replaceChildren(...children) { this.children.forEach(c => c.parent = null); this.children = children; children.forEach(c => c.parent = this); }
  setAttribute(key, value) { this.attrs[key] = value; }
  removeAttribute(key) { delete this.attrs[key]; }
  addEventListener(event, callback) { this.handlers[event] = callback; }
  querySelector() { return null; }
}
global.window = global;
global.document = { baseURI: 'http://memory.test/', createElement: tag => new FakeNode(tag) };
let timerId = 0, timers = new Map(), randomId = 100, fixedRandom = false, fetches = 0, analysisRequests = 0;
let failFetch = false, fetchWait = null, currentAdapter, currentCaches, mounted = [], generatedCount = 0;
global.setTimeout = callback => { timers.set(++timerId, callback); return timerId; };
global.clearTimeout = id => timers.delete(id);
global.URL = class { constructor(path, base) { this.href = base + path; } };
global.TextDecoder = class { decode(bytes) { return bytes; } };
global.crypto = { getRandomValues(values) { values[0] = fixedRandom ? 1234 : ++randomId; values[1] = 5678; return values; }, subtle: { digest: async () => digest } };
global.AbortController = class {
  constructor() {
    const listeners = new Set();
    this.signal = { aborted: false, addEventListener: (_, callback) => listeners.add(callback), removeEventListener: (_, callback) => listeners.delete(callback) };
    this.abort = () => { if (!this.signal.aborted) { this.signal.aborted = true; Array.from(listeners).forEach(callback => callback()); } };
  }
};
global.fetch = async (_, options) => {
  fetches++;
  if (failFetch) throw Error('forced network failure');
  if (fetchWait) await new Promise((resolve, reject) => {
    const abort = () => { const error = Error('cancelled'); error.name = 'AbortError'; reject(error); };
    options.signal.addEventListener('abort', abort);
    fetchWait.then(() => { options.signal.removeEventListener('abort', abort); resolve(); });
  });
  return { ok: true, arrayBuffer: async () => JSON.stringify(catalog) };
};
global.NameleculeChemistryClient = { analyze: async molecule => { analysisRequests++; return clone(analyses.find(a => a.moleculeId === molecule.id)); } };
const realCreateGame = NameleculeRepairGenerator.createGame;
global.NameleculeRepairGenerator = { ...NameleculeRepairGenerator, createGame(...args) { generatedCount++; return realCreateGame(...args); } };
NameleculeRepairGame.mountRound = (host, options) => {
  const item = { host, options, destroyed: false };
  const handle = { destroy() { item.destroyed = true; } };
  mounted.push(item);
  return handle;
};
global.NameleculeQuizCheckpoints = { registerType(type, adapter) { check(type === 'generated-name-repair-set', 'registered type'); currentAdapter = adapter; } };
function freshAdapter() {
  // Observe cache sizes only; production cache access/behavior is unchanged.
  eval(adapterSource.replace('const practices = new Map();', 'const practices = new Map(); global.__adapterCaches = { prepared, practices };'));
  currentCaches = global.__adapterCaches;
  return currentAdapter;
}
function mount(adapter, selectedRecipe, state, practice, extra = {}) {
  const host = new FakeNode('div'); host.root = true;
  const session = { host, changes: [], solved: 0, continued: 0, practiceClicks: 0, progress: [], latestState: null };
  const options = { round: selectedRecipe, initialState: state,
    onStateChange(value) { session.latestState = value; session.changes.push(clone(value)); },
    onSolved() { session.solved++; }, onContinue() { session.continued++; },
    onProgress(value) { session.progress.push(value); }, ...extra };
  session.handle = (practice ? adapter.mountPractice : adapter.mount)(host, options);
  session.round = () => mounted.findLast(item => item.host.parent === host && !item.destroyed);
  return session;
}
function correctState(round) {
  const state = NameleculeRepairEngine.createRoundState(round);
  if (round.kind === 'replace') { state.selectedPartId = round.targetPartId; state.selectedValue = round.correctValue; }
  else state.order = round.correctOrder.slice();
  return { ...state, solved: true, submitted: true, attempts: 1 };
}
function solve(session) {
  const view = session.round();
  const correct = correctState(view.options.round);
  view.options.onStateChange(correct);
  view.options.onSolved({ kind: 'correct' }, correct);
}
async function ready(session, label) { await until(() => !!session.round(), label); }
function complete(session, checkPractice = false) {
  for (let index = session.latestState.currentRound; index < 3; index++) {
    const options = session.round().options;
    check(options.continueLabel === (index < 2 ? 'Επόμενο κουίζ' : 'Συνεχίζω τη θεωρία'), 'continue label ' + index);
    if (checkPractice) check((typeof options.onNewPractice === 'function') === (index === 2), 'new practice last question only ' + index);
    if (index === 2 && options.onNewPractice) { const count = session.practiceClicks; options.onNewPractice(); equal(session.practiceClicks, count, 'new practice guarded until solved'); }
    solve(session);
    if (index < 2) options.onContinue();
  }
  check(session.latestState.solved, 'completed receipt verified');
}
(async function () {
  const adapter = freshAdapter(), caches = currentCaches;
  equal(Object.keys(adapter.restore(recipe, null)), ['version', 'seed', 'currentRound', 'states', 'solved'], 'original receipt keys');
  equal(adapter.restore(recipe, null), { version: 1, seed: null, currentRound: 0, states: [null, null, null], solved: false }, 'original blank state');
  equal(adapter.prepare(recipe, null), null, 'original prepare null on blank');
  throws(() => adapter.createPractice({ ...recipe, bogus: true }, null), 'practice keeps exact recipe validation');
  fixedRandom = true;
  const reset1 = adapter.createPractice(recipe, { seed: '12345678', states: [{ solved: true }], solved: true });
  equal(reset1, { version: 1, seed: '12345679', currentRound: 0, states: [null, null, null], solved: false }, 'fresh practice seed differs on repeated random bytes');
  fixedRandom = false;
  const required = mount(adapter, recipe, null, false, { newPracticeLabel: 'Another triple', onNewPractice() { required.practiceClicks++; } });
  check(required.latestState.seed && required.host.attrs['aria-busy'] === 'true', 'required seed published before loading');
  await ready(required, 'required ready');
  complete(required, true);
  const earned = clone(required.latestState), requiredSet = Array.from(caches.prepared.values())[0];
  check(required.solved === 1, 'required set solved callback once');
  equal(adapter.restore(recipe, earned), earned, 'earned receipt unchanged');
  equal(adapter.prepare(recipe, earned), null, 'earned prepare synchronous cache hit');
  equal(caches.prepared.size, 1, 'required one cache entry');
  check(required.round().options.newPracticeLabel === 'Another triple', 'practice label forwarded');
  required.round().options.onNewPractice(); equal(required.practiceClicks, 1, 'required success new practice callback');
  required.round().options.onContinue(); equal(required.continued, 1, 'required success continue callback');
  const detachedCallback = required.round().options.onNewPractice;
  required.handle.destroy(); detachedCallback(); equal(required.practiceClicks, 1, 'destroy blocks new practice callback');

  const requiredBranched = mount(adapter, branched, null, false);
  await ready(requiredBranched, 'branched required ready'); complete(requiredBranched);
  const branchedEarned = clone(requiredBranched.latestState);
  check(!('onNewPractice' in requiredBranched.round().options), 'old mount opt-in absent by default');
  requiredBranched.handle.destroy();
  let previous = earned;
  for (let index = 0; index < 40; index++) {
    const selectedRecipe = index % 2 ? branched : recipe;
    const fresh = adapter.createPractice(selectedRecipe, previous);
    check(fresh.seed !== previous.seed, 'successive seed differs ' + index);
    equal(fresh.states, [null, null, null], 'fresh three empty answers ' + index);
    const session = mount(adapter, selectedRecipe, fresh, true);
    await ready(session, 'optional ready ' + index);
    check(!session.latestState.solved && session.latestState.currentRound === 0, 'optional starts unsolved question1 ' + index);
    check(caches.practices.size <= 2, 'optional cache bound ' + index);
    equal(caches.prepared.size, 2, 'optional never populates required cache ' + index);
    equal(adapter.restore(recipe, earned), earned, 'required verification survives optional ' + index);
    equal(adapter.restore(branched, branchedEarned), branchedEarned, 'branched verification survives optional ' + index);
    previous = clone(session.latestState); session.handle.destroy();
  }
  check(caches.prepared.get(JSON.stringify([recipe.setId, recipe.difficulty, recipe.generatorVersion, recipe.catalogRevision, recipe.engineSHA256, earned.seed])) === requiredSet, 'original required set identity retained beyond32');

  const extra = mount(adapter, branched, adapter.createPractice(branched, previous), true, { onNewPractice() { extra.practiceClicks++; } });
  await ready(extra, 'optional replay ready');
  const wrong = correctState(extra.round().options.round);
  if (extra.round().options.round.kind === 'replace') wrong.selectedValue = 'not a legal choice';
  else wrong.order.reverse();
  extra.round().options.onStateChange(wrong);
  check(!extra.latestState.solved && !extra.latestState.states[0].solved, 'forged incorrect optional answer not solved');
  solve(extra); extra.round().options.onContinue();
  equal(extra.latestState.currentRound, 1, 'optional partial question2');
  const partial = clone(extra.latestState); extra.handle.destroy();
  const reopened = mount(adapter, branched, partial, true, { onNewPractice() { reopened.practiceClicks++; } });
  await ready(reopened, 'optional reopen ready');
  equalActiveReceipt(reopened.latestState, partial, 'optional partial answers/current question stable on reopen');
  complete(reopened, true);
  reopened.round().options.onNewPractice(); equal(reopened.practiceClicks, 1, 'optional successful repeat action');
  const optionalEarned = clone(reopened.latestState); reopened.handle.destroy();
  check(adapter.restorePractice(branched, optionalEarned).solved, 'optional success independently restored');
  check(!adapter.restore(branched, optionalEarned).solved, 'optional receipt cannot use required cache');
  const forged = { ...optionalEarned, solved: true, states: [{ solved: true }, { solved: true }, { solved: true }] };
  check(!adapter.restorePractice(branched, forged).solved, 'solved booleans never grant success');
  const outOfOrder = clone(optionalEarned); outOfOrder.states[0] = null;
  const cleaned = adapter.restorePractice(branched, outOfOrder);
  check(cleaned.currentRound === 0 && cleaned.states.every(s => !s.solved), 'out of order optional solved answers reset');
  for (const malformed of [null, [], {}, { version: 9, seed: '10' }, { version: 1, seed: 'bad' }, { version: 1, seed: '1'.repeat(21) }]) {
    equal(adapter.restorePractice(recipe, malformed), { version: 1, seed: null, currentRound: 0, states: [null, null, null], solved: false }, 'malformed optional reset');
  }

  const freshRuntime = freshAdapter(), refreshCaches = currentCaches;
  check(!freshRuntime.restore(recipe, earned).solved, 'cold receipt requires regeneration');
  check(freshRuntime.prepare(recipe, earned) instanceof Promise, 'original prepare contract promise on cold receipt');
  await until(() => freshRuntime.restore(recipe, earned).solved, 'old required receipt regenerated');
  const beforeOptional = generatedCount;
  check(!freshRuntime.restorePractice(branched, partial).solved, 'cold optional not trusted');
  const refresh = mount(freshRuntime, branched, partial, true);
  await ready(refresh, 'same-tab refresh reconstructs optional');
  equalActiveReceipt(refresh.latestState, partial, 'cold optional active question/answers recovered');
  check(generatedCount === beforeOptional + 1, 'optional generated separately');
  check(refreshCaches.prepared.size === 1 && refreshCaches.practices.size === 1, 'cold optional uses separate cache');
  refresh.handle.destroy();
  equal(freshRuntime.prepare(recipe, earned), null, 'required prepare independent of optional cache');

  const abortAdapter = freshAdapter();
  let release; fetchWait = new Promise(resolve => release = resolve);
  const pending = mount(abortAdapter, recipe, abortAdapter.createPractice(recipe, null), true);
  const published = pending.changes.length, mountedBefore = mounted.length;
  pending.handle.destroy(); pending.handle.destroy(); release(); fetchWait = null;
  await drain();
  equal(pending.changes.length, published, 'cancelled generation no later state');
  equal(mounted.length, mountedBefore, 'cancelled generation never mounts');
  equal(currentCaches.practices.size, 0, 'cancelled generation not cached');
  equal(pending.host.children.length, 0, 'destroy clears host');

  const failedAdapter = freshAdapter(); failFetch = true;
  const failed = mount(failedAdapter, recipe, failedAdapter.createPractice(recipe, null), true);
  await until(() => failed.host.children.some(node => node.className === 'nl-quiz-error'), 'failure recoverable error rendered');
  check(!failed.latestState.solved && failed.latestState.seed, 'failed generation retains current seed unsolved');
  const retry = failed.host.children.find(node => node.tagName === 'button');
  failFetch = false;
  retry.handlers.click(); retry.handlers.click();
  await ready(failed, 'rapid retry latest request mounts');
  equal(mounted.filter(item => item.host.parent === failed.host && !item.destroyed).length, 1, 'rapid retry single live mount');
  failed.handle.destroy();
  equal(timers.size, 0, 'all adapter generation timers cleaned');
  check(analysisRequests >= 16 && fetches >= 4, 'real source analysis paths exercised');
  print(JSON.stringify({ passed: true, checks, generatedCount, requiredCacheSizeAfter40Optional: caches.prepared.size,
    practiceCacheSizeAfter40Optional: caches.practices.size, optionalGenerationsInStress: 40, fetches, analysisRequests }));
})().catch(error => { print(String(error) + '\n' + error.stack); throw error; });
