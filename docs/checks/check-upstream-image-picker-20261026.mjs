// Read-only execution of the actual upstream picker functions in a small VM.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync('js/mulermoc-nom-scenario-51.js', 'utf8');
const code = source.slice(source.indexOf('var fScenarioNoteImageInputEl = null;'),
  source.indexOf('function fScenarioInsertNoteTable('));
assert.ok(code.length > 4000);
let cases = 0;

function fixture(options = {}) {
  const events = [], notices = [], inserts = [], appended = [];
  const input = { value: '', files: [], style: {}, listeners: {},
    setAttribute() {}, addEventListener(k, fn) { this.listeners[k] = fn; },
    click() { events.push('click'); } };
  class Reader {
    readAsDataURL() {
      if (options.readError) { this.onerror(); return; }
      this.result = options.url ?? 'data:image/png;base64,AAAA';
      this.onload();
    }
  }
  const ctx = {
    document: { body: { contains: el => appended.includes(el),
      appendChild: el => appended.push(el) }, getElementById: () => null,
      createElement: () => input },
    window: { FileReader: options.noReader ? null : Reader,
      prompt: () => Object.hasOwn(options, 'alt') ? options.alt : 'A "quoted" & image' },
    FileReader: Reader,
    Event: class { constructor(type) { this.type = type; } },
    fScenarioToast: msg => notices.push(msg),
    fScenarioEscapeNoteAttr: text => String(text).replaceAll('&', '&amp;').replaceAll('"', '&quot;'),
    fScenarioInsertNoteSnippet: (noteInput, state, snippet) => {
      inserts.push(snippet); noteInput.value = snippet; state.note = snippet;
    },
  };
  vm.createContext(ctx); vm.runInContext(code, ctx);
  const textarea = { value: '', dispatchEvent: e => events.push(e.type) };
  const state = {};
  function read(file = { type: 'image/png', size: 100, name: 'pixel.png' }) {
    input.files = file ? [file] : [];
    input.value = 'C:/fakepath/pixel.png';
    ctx.fScenarioNoteImagePending = { noteInput: textarea, st: state };
    ctx.fScenarioReadNoteImageFile(input);
    assert.equal(input.value, '');
    assert.equal(ctx.fScenarioNoteImagePending, null);
  }
  return { ctx, input, textarea, state, events, notices, inserts, appended, read };
}

for (const type of ['image/png', 'image/jpeg', 'image/gif', 'image/webp']) {
  const f = fixture({ url: `data:${type};base64,AAAA` });
  f.read({ type, size: 512000, name: 'image' });
  assert.equal(f.inserts.length, 1);
  assert.ok(f.state.note.includes('alt="A &quot;quoted&quot; &amp; image"'));
  assert.equal(f.textarea.value, f.state.note);
  assert.deepEqual(f.events, ['input']);
  cases++;
}
for (const [options, file] of [
  [{}, { type: 'image/svg+xml', size: 100 }],
  [{}, { type: 'application/pdf', size: 100 }],
  [{}, { type: 'image/png', size: 512001 }],
  [{ noReader: true }, { type: 'image/png', size: 100 }],
  [{ readError: true }, { type: 'image/png', size: 100 }],
  [{ url: 'data:image/svg+xml;base64,AAAA' }, { type: '', size: 100 }],
  [{ url: 'data:image/png;base64,' + 'A'.repeat(700000) }, { type: 'image/png', size: 100 }],
  [{ alt: '   ' }, { type: 'image/png', size: 100 }],
]) {
  const f = fixture(options); f.read(file);
  assert.equal(f.inserts.length, 0); assert.equal(f.notices.length, 1); cases++;
}
for (const options of [{ alt: null }, {}]) {
  const f = fixture(options); f.read(options.alt === null ? undefined : null);
  assert.equal(f.inserts.length, 0); assert.equal(f.notices.length, 0); cases++;
}
{
  const f = fixture();
  f.ctx.fScenarioInsertNoteImage(null, {}); assert.equal(f.appended.length, 0);
  f.ctx.fScenarioInsertNoteImage(f.textarea, f.state);
  assert.equal(f.input.type, 'file'); assert.ok(f.input.accept.includes('.webp'));
  assert.deepEqual(f.events, ['click']);
  assert.equal(f.ctx.fScenarioGetNoteImageInput(), f.input);
  assert.equal(f.appended.length, 1);
  f.input.listeners.cancel(); assert.equal(f.ctx.fScenarioNoteImagePending, null);
  cases++;
}
for (const url of ['http://example.org/image.png', '//example.org/image.png',
  'data:image/svg+xml;base64,AAAA']) {
  const f = fixture(); let calls = 0;
  f.ctx.window.prompt = () => ++calls === 1 ? url : 'Description';
  f.ctx.fScenarioInsertNoteImageByUrl(f.textarea, f.state);
  assert.equal(f.inserts.length, 0); assert.equal(f.notices.length, 1); cases++;
}
console.log(JSON.stringify({ passed: true, cases, nativeOSPickerTested: false,
  scope: 'Actual picker/URL functions; guard, cancellation, reuse and input-event cases' }));
