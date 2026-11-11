/* Developer evidence: JavaScriptCore mock DOM/native bridge checks, not browser
 * or chemical validation. Run from repository root with system jsc. */
'use strict';
load('js/namelecule-name-builder-engine.js');
const source = readFile('js/namelecule-name-builder.js');
new Function(source);
const checks = [];
function check(name, condition) {
  if (!condition) throw new Error(name);
  checks.push(name);
}
const roots = ['μεθ', 'αιθ', 'προπ', 'βουτ', 'πεντ', 'εξ', 'επτ', 'οκτ', 'εννε', 'δεκ'];
const forms = ['condensed', 'expanded', 'skeletal', '3d'];
function round(id = 'ethane', text = 'αιθ') {
  return { roundId: 'lesson-round-' + id, moleculeId: id, correctName: text + 'άνιο', series: 'alkanes', parentLength: 2,
    pieces: [{ text, separatorBefore: '', role: 'slot-1' }, { text: 'άν', separatorBefore: '', role: 'slot-2' },
      { text: 'ιο', separatorBefore: '', role: 'slot-3' }], representations: forms, vocabulary: { roots: roots.slice(0, 5) } };
}
function env(options = {}) {
  const elements = new Map(), posted = [], native = [], events = {}, raf = new Map(), timers = new Map();
  let nextTimer = 0, nextFrame = 0;
  class Element {
    constructor(tag = 'div', id = '') {
      this.tagName = tag; this.id = id; this.children = []; this.dataset = {}; this.events = {}; this.attributes = {};
      this.hidden = false; this.disabled = false; this.scrollLeft = 0; this.clientLeft = 0; this.clientWidth = 500;
      this.style = {}; this.classes = new Set(); this._text = '';
      this.classList = { add: (...values) => values.forEach(value => this.classes.add(value)),
        remove: (...values) => values.forEach(value => this.classes.delete(value)),
        contains: value => this.classes.has(value),
        toggle: (value, on) => { if (on === undefined) on = !this.classes.has(value); if (on) this.classes.add(value); else this.classes.delete(value); } };
    }
    set className(value) { this.classes = new Set(value.split(' ')); }
    get className() { return Array.from(this.classes).join(' '); }
    set textContent(value) { this._text = String(value); this.children = []; }
    get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    append(...children) { this.children.push(...children); }
    replaceChildren(...children) { this._text = ''; this.children = children; }
    addEventListener(type, callback) { (this.events[type] ||= []).push(callback); }
    removeEventListener() {}
    click() { if (!this.disabled) (this.events.click || []).forEach(callback => callback({})); }
    focus() {}
    scrollIntoView() { this.scrolled = true; }
    querySelectorAll(selector) {
      return this.children.flatMap(child => (selector === 'button' && child.tagName === 'button' ||
        selector === '.tile-button' && child.classList.contains('tile-button') ? [child] : []).concat(child.querySelectorAll(selector)));
    }
    getBoundingClientRect() {
      return this.id === 'body' ? { top: 0, bottom: 1234, height: 1234, left: 0, right: 500, width: 500 }
        : { top: 700, bottom: 920, height: 220, left: 0, right: 500, width: 500 };
    }
  }
  const get = id => { if (!elements.has(id)) elements.set(id, new Element('div', id)); return elements.get(id); };
  const representationButtons = forms.map(mode => { const button = new Element('button'); button.dataset.representation = mode; return button; });
  const body = get('body'), documentElement = get('html');
  const nativeEvents = {};
  const frame = get('molecule-viewer'); frame.contentWindow = { postMessage: data => native.push(data),
    addEventListener: (type, callback) => (nativeEvents[type] ||= []).push(callback) };
  const self = { addEventListener: (type, callback) => (events[type] ||= []).push(callback), NameleculeNameBuilderEngine };
  const outer = options.top ? self : { postMessage: data => posted.push(data) };
  const document = { body, documentElement, getElementById: get, createElement: tag => new Element(tag),
    querySelectorAll: selector => selector === '[data-representation]' ? representationButtons
      : [get('bank-tiles'), get('answer-tiles')].flatMap(element => element.querySelectorAll(selector)) };
  class SearchParams {
    constructor(value) { this.value = value; }
    get(key) { const match = new RegExp('(?:^|[?&])' + key + '=([^&]*)').exec(this.value); return match ? decodeURIComponent(match[1]) : null; }
  }
  const location = { origin: 'http://localhost:1234', search: options.search === undefined ? '?lessonSession=abcdefgh12345678' : options.search, reload() {} };
  const resizeObservers = [];
  class Observer { constructor(callback) { resizeObservers.push(this); this.callback = callback; } observe() {} disconnect() { this.disconnected = true; } }
  const args = ['window', 'parent', 'document', 'location', 'URLSearchParams', 'crypto', 'setTimeout', 'clearTimeout',
    'requestAnimationFrame', 'cancelAnimationFrame', 'ResizeObserver', 'matchMedia'];
  new Function(...args, source)(self, outer, document, location, SearchParams,
    { getRandomValues: array => { for (let i = 0; i < array.length; i++) array[i] = i; return array; } },
    callback => { const id = ++nextTimer; timers.set(id, callback); return id; }, id => timers.delete(id),
    callback => { const id = ++nextFrame; raf.set(id, callback); return id; }, id => raf.delete(id), Observer,
    () => ({ matches: true }));
  const emit = (data, sourceWindow, origin = location.origin) => (events.message || []).forEach(callback => callback({ data, source: sourceWindow, origin }));
  const readyNative = () => emit({ channel: 'namelecule-name-builder-v1', session: new SearchParams(frame.src.split('?')[1]).get('session'),
    type: 'ready', inventory: [{ id: 'ethane', representations: forms }, { id: 'propane', representations: forms }] }, frame.contentWindow);
  const loadLesson = (changes = {}, sourceWindow = outer, origin = location.origin) => {
    const canonical = changes.round || round();
    const payload = { channel: 'namelecule-builder-lesson-v1', session: 'abcdefgh12345678', command: 'load', requestId: 1,
      attemptId: 'attempt-ethane', moleculeId: canonical.moleculeId, round: canonical, bankSeed: 'stable-seed',
      initialState: { answer: [], selected: null, attempts: 0, submitted: false }, explanation: '<b>plain explanation</b>', ...changes };
    emit(payload, sourceWindow, origin); return payload;
  };
  const answerNative = (changes = {}, request = native.at(-1)) => {
    const actual = { ...round(request.moleculeId), roundId: request.roundId, vocabulary: { roots },
      pieces: round(request.moleculeId).pieces.map(piece => ({ ...piece, role: 'native-' + piece.role })) };
    emit({ ...actual, channel: 'namelecule-name-builder-v1', session: request.session, requestId: request.requestId,
      type: request.command === 'load' ? 'round' : 'representation', representation: request.representation, ...changes }, frame.contentWindow);
  };
  const flush = async () => { await Promise.resolve(); await Promise.resolve(); for (const [id, callback] of Array.from(raf)) { raf.delete(id); callback(); } await Promise.resolve(); };
  return { get, posted, native, outer, self, documentElement, representationButtons, loadLesson, readyNative, answerNative, flush, events, resizeObservers,
    tiles: target => get(target).querySelectorAll('button'), emit, close: () => (events.pagehide || []).forEach(callback => callback({})),
    escape: () => (events.keydown || []).forEach(callback => callback({ key: 'Escape', preventDefault() {} })),
    nativeKey: key => { (frame.events.load || []).forEach(callback => callback({}));
      (nativeEvents.keydown || []).forEach(callback => callback({ key, preventDefault() {} })); } };
}
async function main() {
  const e = env();
  check('lesson-ready-identity', e.posted.length === 1 && e.posted[0].type === 'ready' && e.posted[0].session === 'abcdefgh12345678');
  check('lesson-mode-hides-next', e.documentElement.classList.contains('lesson-mode') && e.get('next-molecule').hidden);
  e.loadLesson({}, {}, 'http://localhost:1234'); e.readyNative();
  check('wrong-parent-source-ignored', e.native.length === 0);
  e.loadLesson({}, e.outer, 'http://elsewhere');
  e.loadLesson({ session: 'wrong-session' });
  check('wrong-origin-and-session-ignored', e.native.length === 0);
  e.loadLesson();
  check('canonical-load-native-command', e.native.length === 1 && e.native[0].moleculeId === 'ethane' && e.native[0].roundId === 'lesson-round-ethane');
  e.loadLesson(); check('duplicate-request-ignored', e.native.length === 1);
  e.answerNative(); await e.flush();
  check('native-roles-ignored-bounded-root-prefix-accepted', e.posted.some(event => event.type === 'loaded') && e.tiles('bank-tiles').length > 3);
  check('finite-content-body-size', e.posted.some(event => event.type === 'resize' && event.height === 1234));
  const target = round();
  const bank = NameleculeNameBuilderEngine.createBank(target, { seed: 'stable-seed' });
  const wrong = e.tiles('bank-tiles').find(button => !target.pieces.some(piece => piece.text === button.textContent));
  wrong.click(); e.get('check-answer').click(); await e.flush();
  let snapshot = e.posted.filter(event => event.type === 'state').at(-1).state;
  check('wrong-check-records-evidence', snapshot.attempts === 1 && snapshot.submitted && !e.get('feedback').classList.contains('success'));
  e.get('remove-tile').click(); await e.flush();
  snapshot = e.posted.filter(event => event.type === 'state').at(-1).state;
  check('answer-edit-clears-submission-preserves-attempts', !snapshot.submitted && snapshot.attempts === 1 && !snapshot.answer.length);
  for (const piece of target.pieces) e.tiles('bank-tiles').find(button => button.textContent === piece.text).click();
  const beforeSwitch = e.posted.filter(event => event.type === 'state').at(-1).state;
  e.representationButtons.find(button => button.dataset.representation === 'skeletal').click();
  e.answerNative(); await e.flush();
  check('representation-preserves-answer', JSON.stringify(e.posted.filter(event => event.type === 'state').at(-1).state.answer) === JSON.stringify(beforeSwitch.answer));
  e.get('check-answer').click(); await e.flush();
  snapshot = e.posted.filter(event => event.type === 'state').at(-1).state;
  check('successful-check-records-second-attempt', snapshot.submitted && snapshot.attempts === 2 && e.get('feedback').classList.contains('success') && e.get('check-answer').disabled);
  check('explanation-appended-as-plain-text', e.get('feedback').children.at(-1).tagName === 'p' && e.get('feedback').children.at(-1).textContent === '<b>plain explanation</b>');
  check('lesson-reveal-uses-body-coordinates', e.posted.some(event => event.type === 'reveal' && event.startY === 700 && event.endY === 920) && !e.get('feedback').scrolled);
  e.escape(); check('escape-exit-contains-identities', e.posted.at(-1).type === 'exit' && e.posted.at(-1).attemptId === 'attempt-ethane');
  const preNativeEscape = e.posted.length; e.nativeKey('ArrowRight');
  check('native-arrow-keys-do-not-exit-lesson', e.posted.length === preNativeEscape);
  e.nativeKey('Escape'); check('native-focused-escape-exits-lesson', e.posted.at(-1).type === 'exit');
  const correctAnswer = target.pieces.map(piece => bank.find(tile => tile.text === piece.text).id);
  e.loadLesson({ requestId: 2, initialState: { answer: correctAnswer, selected: null, attempts: 3, submitted: true } });
  e.answerNative(); await e.flush();
  check('submitted-correct-restore-rechecks-and-locks', e.get('feedback').classList.contains('success') && e.get('check-answer').disabled && e.posted.filter(event => event.type === 'loaded').at(-1).state.attempts === 3);
  e.loadLesson({ requestId: 3, initialState: { answer: correctAnswer, selected: null, attempts: 3, submitted: false } });
  e.answerNative(); await e.flush();
  check('unsubmitted-correct-restore-does-not-solve', e.get('feedback').hidden && !e.get('check-answer').disabled);
  const preBad = e.native.length;
  e.loadLesson({ requestId: 4, initialState: { answer: [correctAnswer[0], correctAnswer[0]], selected: null, attempts: 1, submitted: true } });
  check('duplicate-answer-id-rejected', e.native.length === preBad && e.posted.at(-1).type === 'error');
  e.loadLesson({ requestId: 5, moleculeId: 'benzene' });
  check('unsupported-topic-molecule-rejected', e.native.length === preBad);
  e.loadLesson({ requestId: 6 });
  e.answerNative({ correctName: 'μεθάνιο', pieces: round('methane', 'μεθ').pieces }); await e.flush();
  check('native-canonical-mismatch-fails-closed', e.get('check-answer').disabled && e.tiles('bank-tiles').length === 0 && e.posted.at(-1).type === 'error');
  e.loadLesson({ requestId: 7 }); const stale = e.native.at(-1);
  e.loadLesson({ requestId: 8 }); const current = e.native.at(-1);
  e.answerNative({}, stale); await e.flush();
  check('stale-native-response-does-not-enable', e.get('check-answer').disabled && !e.posted.some(event => event.type === 'loaded' && event.requestId === 7));
  e.answerNative({}, current); await e.flush();
  check('latest-request-loads', e.posted.some(event => event.type === 'loaded' && event.requestId === 8));
  const postCount = e.posted.length; e.close(); e.loadLesson({ requestId: 9 }); await e.flush();
  check('pagehide-stops-native-and-late-events', e.native.at(-1).command === 'stop' && e.posted.length === postCount && e.get('molecule-viewer').src === 'about:blank' && e.resizeObservers[0].disconnected);
  const queued = env(); queued.loadLesson();
  check('parent-load-queued-before-native-ready', queued.native.length === 0);
  queued.readyNative(); queued.answerNative(); await queued.flush();
  check('queued-parent-load-activates-after-native-ready', queued.posted.some(event => event.type === 'loaded'));
  for (const options of [{ top: true }, { search: '' }, { search: '?lessonSession=bad' }]) {
    const standalone = env(options); standalone.readyNative(); standalone.answerNative(); await standalone.flush();
    check('standalone-default-preserved-' + JSON.stringify(options), !standalone.posted.length && !standalone.documentElement.classList.contains('lesson-mode') && standalone.native[0].moleculeId === 'ethane' && standalone.tiles('bank-tiles').length > 3);
  }
  print(JSON.stringify({ status: 'passed', syntax: true, checkCount: checks.length, checks,
    limitations: ['Mock DOM and synthetic message/native rounds only; no real browser, trusted input, chemistry, viewer, layout or parent persistence evidence.'] }, null, 2));
}
main().catch(error => { print(String(error) + '\n' + (error.stack || '')); quit(1); });
