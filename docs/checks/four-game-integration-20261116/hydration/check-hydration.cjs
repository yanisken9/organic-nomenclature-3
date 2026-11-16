/* Developer memory check of actual native fInitData bodies, not a browser run.
 * The fixture merges only the exact custom-registration block from native
 * fClassifyAllMolecules; no claim of running native molecular classification.
 * No product source, MOL, SDF, core or generated viewer is written here.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const ROOT = path.resolve(__dirname, '../../../..');
const H = __dirname;
const mode = process.argv.includes('--expect-before') ? 'before' : process.argv.includes('--expect-fixed') ? 'fixed' : null;
assert(mode, 'Choose --expect-before or --expect-fixed');
assert(!(process.argv.includes('--expect-before') && process.argv.includes('--expect-fixed')), 'Choose exactly one expectation');
const read = file => fs.readFileSync(path.join(ROOT,file),'utf8');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const json = value => JSON.parse(JSON.stringify(value));
const sourceBundle = 'js/MULERMOC_namelecule_alkanes_v1_data.js';
const addendum = JSON.parse(read('docs/checks/four-game-integration-20261116/hydration-addendum.json'));
const baselinePath = path.join(H,'before-functions.json');
const versions = [55,56,57];
const sourcePath = version => 'js/mulermoc-nom-molview-'+version+'.js';
const dataPath = version => 'js/jsme-nick-nomeclature-moc2-data_'+version+'.js';
function actualBody(source) {
  const match = source.match(/^function fInitData\(\) \{[\s\S]*?^\}/m);
  assert(match,'Actual native fInitData declaration must exist');
  return match[0];
}
const actual = Object.fromEntries(versions.map(version=>[version,{file:sourcePath(version),body:actualBody(read(sourcePath(version))),sha256:sha(read(sourcePath(version)))}]));
let baseline;
if (mode==='before') {
  for (const file of Object.keys(addendum.extraBeforeHashes)) assert.equal(sha(read(file)),addendum.extraBeforeHashes[file],'Before expectation requires exact four-path pre-approval baseline: '+file);
  baseline={recordedUTC:new Date().toISOString(),role:'Developer recorded source baseline',
    scope:'Actual fInitData bodies only; complete source file digests identify their pre-approval files.',
    functions:actual,extraBeforeHashes:addendum.extraBeforeHashes};
  if (fs.existsSync(baselinePath)) assert.deepEqual(JSON.parse(fs.readFileSync(baselinePath,'utf8')).functions,baseline.functions,'Do not overwrite a different before-body baseline');
  else fs.writeFileSync(baselinePath,JSON.stringify(baseline,null,2)+'\n');
} else {
  assert(fs.existsSync(baselinePath),'Run --expect-before against the genuine pre-fix source first');
  baseline=JSON.parse(fs.readFileSync(baselinePath,'utf8'));
}
let checks=0;
const records=[];
function equal(got,wanted,label) { checks++;assert.deepEqual(got,wanted,label); }
function okay(value,label) { checks++;assert.ok(value,label); }
function context(version,body) {
  // Window properties are global bindings in the browser. A separate mock
  // window object would incorrectly hide nameExamplesCustom from native code.
  const globals={};globals.window=globals;
  const env=vm.createContext(globals);
  vm.runInContext(read(dataPath(version))+'\n'+body,env);
  return env;
}
function run(env,source) { return vm.runInContext(source,env); }
function value(env,source) { return JSON.parse(run(env,'JSON.stringify('+source+')')); }
function hydrate(env) { run(env,'fInitData();'); }
function register(env) { vm.runInContext(read(sourceBundle),env); }
function mergeOnly(env) {
  // Equivalent to the actual own-key / not-already-present native merge.
  // Deliberately not the graph analysis/classification that follows that block.
  run(env,`if(typeof nameExamplesCustom!=='undefined' && nameExamplesCustom) {
    for(var fixtureKey in nameExamplesCustom) if(Object.prototype.hasOwnProperty.call(nameExamplesCustom,fixtureKey) && !nameExamples[fixtureKey]) nameExamples[fixtureKey]=nameExamplesCustom[fixtureKey];
  }`);
}
function examples(env) { return value(env,'nameExamples'); }
function sourceRecords(version) {
  const env=context(version,actual[version].body);register(env);
  return value(env,'window.nameExamplesCustom');
}
const fields=['structure2D_Condensed','structure2D_Expanded','structure2D_Skeletal','file3D'];
function assertSourceRecords(env,source,label) {
  const got=examples(env),custom=value(env,'window.nameExamplesCustom');
  equal(Object.keys(got).length,147,label+' full147 records');
  for(const id of Object.keys(source)) {
    equal(value(env,'nameExamples['+JSON.stringify(id)+']===window.nameExamplesCustom['+JSON.stringify(id)+']'),true,label+' actual registry ownership '+id);
    for(const field of fields) {
      equal(got[id][field],source[id][field],label+' exact retained '+id+'/'+field);
      equal(custom[id][field],source[id][field],label+' original alias source remains intact '+id+'/'+field);
    }
  }
}
for(const version of versions) {
  const old=context(version,baseline.functions[version].body);hydrate(old);
  const baseExpected=examples(old),baseIds=Object.keys(baseExpected);
  equal(baseIds.length,141,'v'+version+' actual base141 catalog');
  const env=context(version,actual[version].body);hydrate(env);
  equal(examples(env),baseExpected,'v'+version+' all141 complete base records equal pre-fix normal native hydration');
  register(env);
  const sources=value(env,'window.nameExamplesCustom');
  equal(Object.keys(sources).length,6,'v'+version+' six actual curated source records');
  mergeOnly(env);
  if(mode==='before') {
    assertSourceRecords(env,sources,'v'+version+' before second hydration');
    hydrate(env);
    const got=examples(env),custom=value(env,'window.nameExamplesCustom');
    for(const id of Object.keys(sources)) {
      for(const field of fields.slice(0,3)) {
        okay(typeof sources[id][field]==='string' && sources[id][field].length>0,'v'+version+' original source has '+id+'/'+field);
        equal(got[id][field],null,'v'+version+' second hydration reproduces actual NULL '+id+'/'+field);
        equal(custom[id][field],null,'v'+version+' alias source damaged to NULL '+id+'/'+field);
      }
      const wrong='mols/nomeclature-moc2/'+id+'_3D.sdf';
      equal(got[id].file3D,wrong,'v'+version+' second hydration reproduces wrong SDF route '+id);
      okay(got[id].file3D!==sources[id].file3D,'v'+version+' wrong route differs from verified curated SDF '+id);
    }
    records.push({version,reproduced:true,curatedMolecules:6,nullForms:18,wrongSDFRoutes:6});
    continue;
  }
  for(let cycle=1;cycle<=3;cycle++) {
    hydrate(env);
    assertSourceRecords(env,sources,'v'+version+' register-after-first-init cycle'+cycle);
    const got=examples(env);
    equal(Object.fromEntries(baseIds.map(id=>[id,got[id]])),baseExpected,'v'+version+' base141 complete records remain exact cycle'+cycle);
  }
  // Both actual startup orders and an already-merged registry at first hydrate.
  for(const order of ['registered-before-first-init','merged-before-first-init']) {
    const varied=context(version,actual[version].body);register(varied);
    if(order==='merged-before-first-init') mergeOnly(varied);
    hydrate(varied);
    if(order==='registered-before-first-init') mergeOnly(varied);
    for(let cycle=1;cycle<=3;cycle++) {
      hydrate(varied);assertSourceRecords(varied,sources,'v'+version+' '+order+' cycle'+cycle);
    }
  }
  const collision=context(version,actual[version].body);hydrate(collision);
  run(collision,`window.nameExamplesCustom={ethane:{structure2D_Condensed:'foreign condensed',structure2D_Expanded:'foreign expanded',structure2D_Skeletal:'foreign skeletal',file3D:'foreign.sdf'}};`);
  mergeOnly(collision);hydrate(collision);
  equal(value(collision,'nameExamples.ethane===window.nameExamplesCustom.ethane'),false,'v'+version+' colliding base ID is not registered custom owner');
  equal(examples(collision),baseExpected,'v'+version+' custom/base ID collision preserves every base record');
  const partial=context(version,actual[version].body);hydrate(partial);
  run(partial,`window.nameExamplesCustom={fixtureMissing:{structure2D_Condensed:'declared condensed',structure2D_Expanded:null,structure2D_Skeletal:null,file3D:''}};`);
  mergeOnly(partial);
  const partialBefore=value(partial,'window.nameExamplesCustom.fixtureMissing');
  for(let cycle=1;cycle<=3;cycle++) {
    hydrate(partial);
    equal(value(partial,'nameExamples.fixtureMissing'),partialBefore,'v'+version+' explicit missing forms and empty3D preserved cycle'+cycle);
    equal(value(partial,'window.nameExamplesCustom.fixtureMissing'),partialBefore,'v'+version+' partial source alias intact cycle'+cycle);
  }
  const priority=context(version,actual[version].body);hydrate(priority);register(priority);mergeOnly(priority);
  const id=Object.keys(sources)[0];
  run(priority,'window.MOL2D['+JSON.stringify(id)+']={condensed:"registry owns condensed",expanded:null,skeletal:""};');
  hydrate(priority);
  const prioritized=value(priority,'nameExamples['+JSON.stringify(id)+']');
  equal(prioritized.structure2D_Condensed,'registry owns condensed','v'+version+' existing MOL2D value owns condensed');
  equal(prioritized.structure2D_Expanded,null,'v'+version+' existing MOL2D explicit null owns expanded');
  equal(prioritized.structure2D_Skeletal,'','v'+version+' existing MOL2D empty value owns skeletal');
  equal(prioritized.file3D,sources[id].file3D,'v'+version+' registered custom retains declared SDF even with MOL2D registry');
  records.push({version,verified:true,baseMolecules:141,totalMolecules:147,curatedMolecules:6,cyclesPerStartupOrder:3,
    startupOrders:3,collisionPreserved:true,explicitMissingFormsAndEmpty3DPreserved:true,MOL2DPriority:true});
}
const result={recordedUTC:new Date().toISOString(),role:'Developer memory execution; not independent review',expectation:mode,completed:true,checks,records,
  sourceSHA256:Object.fromEntries(versions.flatMap(version=>[[sourcePath(version),sha(read(sourcePath(version)))],[dataPath(version),sha(read(dataPath(version)))]]).concat([[sourceBundle,sha(read(sourceBundle))]])),
  beforeBodyFileSHA256:sha(fs.readFileSync(baselinePath)),
  limitations:['Actual fInitData bodies and actual base data/curated bundle are executed; only the own-key/native custom merge block is fixture-equivalent, not the full fClassifyAllMolecules analysis.',
    'No browser callbacks, JSME/3D loading, user interactions, chemical naming or molecular geometry are certified by this memory test.',
    'The before case intentionally reproduces the demonstrated data loss; passing --expect-before does not indicate application correctness.']};
fs.writeFileSync(path.join(H,mode+'-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({expectation:mode,completed:true,checks,records}));
