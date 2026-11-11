/* Test the generated host's exact native-init delegation. No actual JSmol or
 * chemistry execution is claimed. Generator --check binds this to file bytes. */
const html = readFile('games/name-builder-viewer.html');
const config = html.match(/<script>\s*(JSmol_Applet\.script =[\s\S]*?)<\/script>/)?.[1];
if (!config) throw new Error('Missing generated init configuration');
let assertions = 0;
function assert(value, message) { if (!value) throw new Error(message); assertions++; }
globalThis.location = {href: 'https://example.test/games/name-builder-viewer.html'};
globalThis.URL = class { constructor() { this.href = 'https://example.test/'; } };
globalThis.JSmol_Applet = {};
const calls = [];
globalThis.Jmol = {script(applet, command) { calls.push({applet, command, receiver: this}); return 'native-result'; }};
eval(config);
const applet = {};
const original = 'frank off;load mols/nomeclature-moc2/ethane_3D.sdf; select all; center selected;script spt/init-55.spt;moveto 0.0 {0 0 1 0};';
assert(Jmol.script(applet, original) === 'native-result', 'Preserve native return value');
const revised = calls[0].command;
const version = revised.match(/script "spt\/init-55\.spt\?v=([a-f0-9]{64})";/)?.[1];
assert(!!version, 'Exactly native init receives content-versioned quoted URL');
assert(revised.replace('script "spt/init-55.spt?v=' + version + '";', 'script spt/init-55.spt;') === original,
  'Load, selection and camera commands unchanged');
assert(calls[0].applet === applet && calls[0].receiver === Jmol, 'Preserve native receiver and applet');
const other = 'select all;script spt/init-54.spt;nameBuilderRevision = 2;';
Jmol.script(applet, other);
assert(calls[1].command === other, 'Nonmatching command unchanged');
Jmol.script(applet, null);
assert(calls[2].command === null, 'Non-string input delegates unchanged');
assert(JSmol_Applet.script.includes('set defaultDirectory "https://example.test/";'), 'Native relative-file base preserved');
print(JSON.stringify({checks: assertions, status: 'passed', initVersion: version,
  evidence: 'Generated exact-command delegate with a native API double only'}));
