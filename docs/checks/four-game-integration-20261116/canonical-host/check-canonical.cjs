/* Developer memory evidence. No browser or independent-review claim. */
'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../../..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const copy = value => JSON.parse(JSON.stringify(value));
const engine = require(path.join(root, 'js/namelecule-molecular-detective-engine.js'));
const before = require(path.join(__dirname, '../before/js/namelecule-molecular-detective-engine.js'));
const catalog = JSON.parse(read('games/data/alkane-structures.json'));
const oldSnapshots = JSON.parse(read('docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json'));
const engineFile = 'js/chemistry-engines/' + catalog.engineSHA256 + '.js';
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
let checks = 0, missionCount = 0, alternatives = 0;
const records = [], snapshots = {};
function equal(actual, expected, label) { checks++; assert.deepEqual(actual, expected, label); }
function rejects(action, label) { checks++; assert.throws(action, label); }
equal(sha(read(engineFile)), catalog.engineSHA256, 'actual pinned core54 bytes');
const core54 = vm.createContext({window: {}, selectedMol: null, mode2D: 'expanded', mainChainMode: 'algorithmic'});
vm.runInContext(read(engineFile), core54);
const native56 = vm.createContext({window: {}, selectedMol: null, mode2D: 'expanded', mainChainMode: 'algorithmic'});
vm.runInContext(read('js/jsme-nick-nomeclature-moc2-data_56.js') + '\n' + read('js/mulermoc-nom-core-56.js'), native56);
function analyze(context, molecule) {
  context.molecule = molecule;
  return JSON.parse(vm.runInContext(`
    selectedMol=molecule.id;
    var graph=fParseMolV2000(molecule.mol);
    jsmeNomeclatureApplet={totalNumberOfAtoms:()=>graph.atoms.length,totalNumberOfBonds:()=>graph.bonds.length,
      getAtom:(m,i)=>({label:graph.atoms[i-1].el}),getBond:(m,i)=>({atoms:graph.bonds[i-1].slice(0,2),order:graph.bonds[i-1][2]}),molFile:()=>molecule.mol};
    fAnalyseStructure();fDetectMolType();if(typeof fInitNamingProps==='function') fInitNamingProps();fGuessName();
    JSON.stringify({moleculeId:selectedMol,name:currentMolName,parts:nameComponentsList.slice(),classification:fGetMoleculeClassification()})
  `, context));
}
for (const molecule of catalog.molecules) {
  equal(sha(molecule.mol), molecule.sourceSHA256, molecule.id + ' catalog bytes verified');
  native56.id = molecule.id;
  equal(vm.runInContext('window.MOL2D[id].expanded', native56), molecule.mol, molecule.id + ' native56 source identical');
  const analysis = {...analyze(core54, molecule), engineSHA256: catalog.engineSHA256};
  const nativeAnalysis = analyze(native56, molecule);
  equal(analysis.name, nativeAnalysis.name, molecule.id + ' pinned54/native56 full name');
  equal(analysis.parts, nativeAnalysis.parts, molecule.id + ' pinned54/native56 parts');
  const input = JSON.stringify([molecule, analysis]);
  const expected = engine.canonicalSnapshot(molecule, analysis);
  snapshots[molecule.id] = expected;
  equal(JSON.stringify([molecule, analysis]), input, 'canonical leaves verified inputs unchanged');
  equal(expected.sourceMOL, molecule.mol, molecule.id + ' exact source preserved');
  const old = copy(expected); delete old.sourceMOL;
  equal(old, oldSnapshots[molecule.id], molecule.id + ' exact native56 full-index snapshot');
  equal(engine.assertCanonicalSnapshot(expected, copy(expected)), expected, molecule.id + ' native canonical accepted');
  equal(engine.missions(expected), before.missions(expected), molecule.id + ' unchanged missions');
  const missions = engine.missions(expected);
  missionCount += missions.length;
  for (const mission of missions) for (const accepted of mission.accepted) {
    alternatives++;
    const selection = {atoms: [], bonds: []}; selection[mission.kind] = accepted;
    equal(engine.grade(mission, selection), {correct:true,kind:'exact'}, molecule.id + ' accepted alternative');
  }
  const mutations = [
    ['source byte', value => {value.sourceMOL += '\n';}],
    ['missing source', value => {delete value.sourceMOL;}],
    ['full name', value => {value.correctName += 'x';}],
    ['recomposed false name', value => {value.pieces[0].text += 'x';value.correctName=value.pieces.map(p=>p.separatorBefore+p.text).join('');}],
    ['component ID', value => {value.pieces[0].id += 'x';}],
    ['mode', value => {value.pieces[0].mode = 'none';}],
    ['separator', value => {value.pieces[1].separatorBefore = ' ';value.correctName=value.pieces.map(p=>p.separatorBefore+p.text).join('');}],
    ['atom ID', value => {value.atoms[0].id = 999;}],
    ['atom identity', value => {value.atoms[0].element = 'O';}],
    ['bond ID', value => {value.bonds[0].id = 999;}],
    ['endpoint order', value => {const bond=value.bonds[0];[bond.a,bond.b]=[bond.b,bond.a];}],
    ['bond endpoint', value => {value.bonds[0].a=999;}],
    ['bond order', value => {value.bonds[0].order=2;}],
    ['class', value => {value.chemicalClass='wrong';}],
    ['series', value => {value.series='alkenes';}],
    ['array order', value => {value.atoms.reverse();}],
    ['duplicate atom', value => {value.atoms[1].id=value.atoms[0].id;}],
    ['duplicate bond', value => {value.bonds[1].id=value.bonds[0].id;}]
  ];
  for (const [label, mutate] of mutations) {
    const value = copy(expected); mutate(value);
    rejects(() => engine.assertCanonicalSnapshot(expected, value), molecule.id + ' reject ' + label);
  }
  records.push({moleculeId:molecule.id,sourceSHA256:molecule.sourceSHA256,correctName:expected.correctName,
    carbonIds:expected.atoms.filter(atom=>atom.element==='C').map(atom=>atom.id),missions:missions.map(mission=>({id:mission.id,accepted:mission.accepted}))});
}
// Reproduce the preflight defect using a wrong locant while retaining coherent
// name/component roundtrip; canonical equality, rather than graph-only validity,
// must reject it. This changes no chemistry rule in the existing 27 API.
const falseLocant = copy(snapshots.methyl_2_pentane);
falseLocant.pieces[0].text = '3-';
falseLocant.correctName = falseLocant.pieces.map(piece=>piece.separatorBefore+piece.text).join('');
equal(engine.validateSnapshot(falseLocant).valid, true, 'pre-existing false-locant shape/graph validation reproduced');
rejects(()=>engine.assertCanonicalSnapshot(snapshots.methyl_2_pentane, falseLocant), 'canonical rejects recomposed false locant');
equal(snapshots.propane.atoms[0], {id:1,element:'H'}, 'propane leading H retained');
equal(snapshots.butane.atoms[0], {id:1,element:'H'}, 'butane leading H retained');
equal(records.find(record=>record.moleculeId==='propane').carbonIds,[2,3,4],'propane full indexes');
equal(records.find(record=>record.moleculeId==='butane').carbonIds,[2,3,4,5],'butane full indexes');
// Existing 27 public missions, text, IDs, alternatives and grading remain exact.
equal(engine.starterIds, before.starterIds, 'old27 pool exact');
let oldMissions=0, oldAlternatives=0;
for (const id of before.starterIds) {
  const snapshot=oldSnapshots[id], missions=engine.missions(snapshot);
  equal(missions,before.missions(snapshot),id+' old27 exact mission parity');
  oldMissions+=missions.length;
  for(const mission of missions) for(const accepted of mission.accepted) {
    oldAlternatives++;
    const selection={atoms:[],bonds:[]};selection[mission.kind]=accepted;
    equal(engine.grade(mission,selection),before.grade(mission,selection),id+' old27 grade parity');
  }
}
equal([oldMissions,oldAlternatives],[69,108],'all old missions and accepted alternatives preserved');
const molecule=catalog.molecules[0], analysis={...analyze(core54,molecule),engineSHA256:catalog.engineSHA256};
for(const [label,mutate] of [
  ['outside legacy8', m=>{m.id='methyl_2_butane';}], ['no digest',m=>{delete m.sourceSHA256;}],
  ['truncated source',m=>{m.mol='bad';}], ['wrong graph',m=>{m.mol=catalog.molecules[1].mol;}]
]) { const value=copy(molecule);mutate(value);rejects(()=>engine.canonicalSnapshot(value,analysis),label); }
for(const [label,mutate] of [
  ['wrong pinned engine',a=>{a.engineSHA256='0'.repeat(64);}], ['wrong molecule',a=>{a.moleculeId='ethane';}],
  ['unhandled slot',a=>{a.parts[10]='x';}], ['missing class',a=>{delete a.classification;}]
]) { const value=copy(analysis);mutate(value);rejects(()=>engine.canonicalSnapshot(molecule,value),label); }
const result={recordedUTC:new Date().toISOString(),role:'Developer memory execution',completed:true,checks,
  molecules:records.length,missionCount,acceptedAlternatives:alternatives,old27:{missions:oldMissions,acceptedAlternatives:oldAlternatives},records,
  sourceSHA256:Object.fromEntries(['js/namelecule-molecular-detective-engine.js','js/namelecule-molecular-detective-host.js',engineFile].map(file=>[file,sha(read(file))])),
  limitations:['No browser/JSME rendering, click or responsive validation in this memory test.',
    'canonicalSnapshot expects verified catalog bytes and pinned Worker analysis from its caller; it does not independently cryptographically verify provenance.',
    'Canonical construction is limited to the approved legacy eight alkanes; existing missions/grade remain the bounded 27-molecule API.']};
if(process.argv.includes('--write')) {
  fs.writeFileSync(path.join(__dirname,'canonical-results.json'),JSON.stringify(result,null,2)+'\n');
  fs.writeFileSync(path.join(__dirname,'canonical-snapshots.json'),JSON.stringify(snapshots,null,2)+'\n');
}
console.log(JSON.stringify({completed:true,checks,molecules:records.length,missionCount,acceptedAlternatives:alternatives,old27:result.old27}));
