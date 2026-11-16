'use strict';

// Developer regression evidence. No browser/JSME rendering is simulated here:
// core56 reads the actual embedded expanded MOL through its documented API.
// Expected raw atom/bond IDs below were read from those independent MOL tables.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../../..');
const engine = require(path.join(root, 'js/namelecule-molecular-detective-engine.js'));
const inputs = ['js/jsme-nick-nomeclature-moc2-data_56.js', 'js/mulermoc-nom-core-56.js', 'js/namelecule-molecular-detective-engine.js'];
const context = vm.createContext({console});
vm.runInContext('var window={},selectedMol,mode2D="expanded",mainChainMode="algorithmic",jsmeNomeclatureApplet;\n' +
  inputs.slice(0, 2).map(file => fs.readFileSync(path.join(root, file), 'utf8')).join('\n'), context);

const expected = {
  ethane: {'parent-chain': [[1,2]], 'single-bonds': [[1]]},
  butane: {'parent-chain': [[2,3,4,5]], 'single-bonds': [[2,3,4]]},
  methyl_2_pentane: {'parent-chain': [[1,2,3,4,6],[2,3,4,5,6]], branches: [[1],[5]], 'single-bonds': [[1,2,3,4,5]]},
  dimethyl_2_3_butane: {'parent-chain': [[1,2,3,4],[1,2,3,6],[2,3,4,5],[2,3,5,6]], branches: [[1,4],[1,6],[4,5],[5,6]], 'single-bonds': [[1,2,3,4,5]]},
  ethene: {'parent-chain': [[1,2]], 'double-bonds': [[1]]},
  butene_1: {'parent-chain': [[1,2,3,4]], 'double-bonds': [[3]]},
  butene_2: {'parent-chain': [[1,2,3,4]], 'double-bonds': [[2]]},
  butyne_1: {'parent-chain': [[1,2,3,4]], 'triple-bonds': [[3]]},
  butyne_2: {'parent-chain': [[1,2,3,4]], 'triple-bonds': [[2]]},
  butadiene_1_2: {'parent-chain': [[1,2,3,4]], 'double-bonds': [[1,2]]},
  butadiene_1_3: {'parent-chain': [[1,2,3,4]], 'double-bonds': [[1,3]]},
  ethanol: {'parent-chain': [[1,2]], 'single-bonds': [[1]], hydroxyl: [[3,9]]},
  butanol_2: {'parent-chain': [[1,2,3,4]], 'single-bonds': [[1,2,3]], hydroxyl: [[5,15]]},
  propanal: {'parent-chain': [[1,2,3]], 'single-bonds': [[1,2]], aldehyde: [[3,4,10]]},
  propanone: {'parent-chain': [[1,2,3]], 'single-bonds': [[1,2]], carbonyl: [[2,10]]},
  pentanone_3: {'parent-chain': [[1,2,3,4,5]], 'single-bonds': [[1,2,3,4]], carbonyl: [[3,6]]},
  methanoicacid: {'parent-chain': [[1]], carboxyl: [[1,2,4,5]]}
};
let checks = 0;
const records = [];
function equal(actual, wanted, label) { checks++; assert.deepEqual(actual, wanted, label); }
function okay(value, label) { checks++; assert.ok(value, label); }
function copy(value) { return JSON.parse(JSON.stringify(value)); }
function sets(value) { return value.map(ids => ids.slice().sort((a,b)=>a-b)).sort((a,b)=>a.join(',').localeCompare(b.join(','))); }
function selection(mission, ids, other = []) { return mission.kind === 'atoms' ? {atoms: ids, bonds: other} : {atoms: other, bonds: ids}; }
function buildSnapshot(key) {
  context.key = key;
  const source = vm.runInContext(`
    selectedMol=key;
    var mol=window.MOL2D[key].expanded, lines=mol.split(/\\r?\\n/), n=+lines[3].slice(0,3), nb=+lines[3].slice(3,6);
    var aa=lines.slice(4,4+n).map(l=>({label:l.slice(31,34).trim()}));
    var bb=lines.slice(4+n,4+n+nb).map(l=>({atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}));
    jsmeNomeclatureApplet={totalNumberOfAtoms:()=>n,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>mol};
    fAnalyseStructure();fDetectMolType();fInitNamingProps();fGuessName();
    JSON.stringify({moleculeId:key,correctName:currentMolName,parts:nameComponentsList,atoms:aa.map((a,i)=>({id:i+1,element:a.label})),
      bonds:bb.map((b,i)=>({id:i+1,a:b.atoms[0],b:b.atoms[1],order:b.order})),classification:fGetMoleculeClassification()})
  `, context);
  const row = JSON.parse(source);
  const modes = ['compNumber1','compSecondSub1','compNumber2','compSecondSub2','compBondPos','compCarbonsCount','compBondType','compEndNumber','compBondType2','compSuffix'];
  // Native Greek box rendering adds an euphony letter to its preceding box.
  // Browser verification must additionally cover the actual DOM serialization.
  const isConsonant = ch => /[\u0370-\u03ff\u1f00-\u1fff]/u.test(ch) && !'αεηιουωάέήίόύώ'.includes(ch);
  const pieces = row.parts.flatMap((part, i) => {
    if (!part) return [];
    let text = part;
    const next = row.parts.slice(i+1).find(Boolean);
    if (next && isConsonant(part.at(-1)) && isConsonant(next[0])) text += 'πτξ'.includes(part.at(-1)) && next[0] === 'δ' ? 'α' : 'ο';
    return [{id:'comp'+i, text, separatorBefore:'', mode:modes[i]}];
  });
  return {moleculeId:key,correctName:row.correctName,pieces,atoms:row.atoms,bonds:row.bonds,
    chemicalClass:row.classification.chemicalClass,series:row.classification.seriesKey};
}

equal(engine.starterIds, Object.keys(expected), 'explicit approved pool');
okay(Object.isFrozen(engine) && Object.isFrozen(engine.starterIds), 'frozen API and pool');
const snapshots = Object.fromEntries(engine.starterIds.map(id => [id, buildSnapshot(id)]));
let missionCount = 0, alternatives = 0;
for (const [id, snapshot] of Object.entries(snapshots)) {
  equal(engine.validateSnapshot(snapshot), {valid:true,code:'valid'}, id+' validated expanded MOL');
  const before = JSON.stringify(snapshot);
  const missions = engine.missions(snapshot);
  equal(JSON.stringify(snapshot), before, id+' input unchanged');
  equal(missions.length, Object.keys(expected[id]).length, id+' mission count');
  equal(sets(missions.map(m => [Object.keys(expected[id]).indexOf(m.family)])), sets(Object.keys(expected[id]).map((_,i)=>[i])), id+' families');
  for (const mission of missions) {
    missionCount++;
    equal(sets(mission.accepted), sets(expected[id][mission.family]), id+'/'+mission.family+' independently authored targets');
    okay(snapshot.pieces.some(piece => piece.id === mission.pieceId), id+' native piece linked');
    okay(mission.prompt.includes(mission.kind === 'atoms' ? 'άτομα' : 'δεσμούς μεταξύ ατόμων C'), 'explicit kind prompt');
    equal(engine.grade(mission, {atoms:[],bonds:[]}), {correct:false,kind:'empty'}, id+' empty');
    equal(engine.grade(mission, selection(mission,[],[1])), {correct:false,kind:'wrong-kind'}, id+' wrong kind');
    for (const accepted of expected[id][mission.family]) {
      alternatives++;
      equal(engine.grade(mission, selection(mission,accepted.slice().reverse())), {correct:true,kind:'exact'}, id+' reverse order');
      equal(engine.grade(mission, selection(mission,[...accepted,accepted[0]])), {correct:true,kind:'exact'}, id+' set duplicates');
      equal(engine.grade(mission, selection(mission,accepted,[1])), {correct:false,kind:'wrong-kind'}, id+' mixed kinds');
      const missing = accepted.slice(1);
      equal(engine.grade(mission, selection(mission,missing)), {correct:false,kind:missing.length ? 'incorrect' : 'empty'}, id+' missing');
      const available = mission.kind === 'atoms' ? snapshot.atoms : snapshot.bonds;
      const extra = available.find(value => !accepted.includes(value.id));
      if (extra) equal(engine.grade(mission,selection(mission,[...accepted,extra.id])), {correct:false,kind:'incorrect'}, id+' extra');
      if (mission.kind === 'atoms') {
        const h = snapshot.atoms.find(a => a.element === 'H' && !accepted.includes(a.id));
        if (h) equal(engine.grade(mission,selection(mission,[h.id,...accepted.slice(1)])), {correct:false,kind:'incorrect'}, id+' raw H not C');
      } else {
        const ch = snapshot.bonds.find(b => snapshot.atoms.find(a => a.id===b.a).element === 'H' || snapshot.atoms.find(a=>a.id===b.b).element === 'H');
        equal(engine.grade(mission,selection(mission,[ch.id,...accepted.slice(1)])), {correct:false,kind:'incorrect'}, id+' C-H not C-C');
      }
    }
  }
  // Deterministic complete re-numbering plus reversed arrays. The expected
  // answers transform the independent oracle, rather than rerun target logic.
  const atomMap = new Map(snapshot.atoms.map(a => [a.id, snapshot.atoms.length+1-a.id]));
  const bondMap = new Map(snapshot.bonds.map(b => [b.id, snapshot.bonds.length+1-b.id]));
  const permuted = {...copy(snapshot), atoms:snapshot.atoms.map(a=>({...a,id:atomMap.get(a.id)})).reverse(),
    bonds:snapshot.bonds.map(b=>({...b,id:bondMap.get(b.id),a:atomMap.get(b.b),b:atomMap.get(b.a)})).reverse()};
  for (const mission of engine.missions(permuted)) {
    const map = mission.kind === 'atoms' ? atomMap : bondMap;
    equal(sets(mission.accepted), sets(expected[id][mission.family].map(set=>set.map(value=>map.get(value)))), id+' ID permutation '+mission.family);
  }
  records.push({moleculeId:id,correctName:snapshot.correctName,missions:missions.map(m=>({id:m.id,pieceId:m.pieceId,kind:m.kind,family:m.family,accepted:m.accepted}))});
}

function mission(id, family) { return engine.missions(snapshots[id]).find(m=>m.family===family); }
equal(engine.grade(mission('dimethyl_2_3_butane','parent-chain'), {atoms:[1,2,3,5],bonds:[]}), {correct:false,kind:'incorrect'}, 'invalid mixed parent alternatives');
equal(engine.grade(mission('dimethyl_2_3_butane','branches'), {atoms:[1,5],bonds:[]}), {correct:false,kind:'incorrect'}, 'two leaves at same branch anchor invalid');
equal(engine.grade(mission('dimethyl_2_3_butane','branches'), {atoms:[1,4,5,6],bonds:[]}), {correct:false,kind:'incorrect'}, 'alternative union rejected');
const diene = mission('butadiene_1_3','double-bonds');
equal(engine.grade(diene,{atoms:[],bonds:[1,2,3]}), {correct:false,kind:'incorrect'}, 'butadiene endpoint union false positive rejected');
equal(engine.grade(mission('propanone','carbonyl'), {atoms:[1,2,3,10],bonds:[]}), {correct:false,kind:'incorrect'}, 'native alpha-C region rejected');
equal(engine.grade(mission('methanoicacid','carboxyl'), {atoms:[1,2,3,4,5],bonds:[]}), {correct:false,kind:'incorrect'}, 'acid formyl H excluded');
okay(!engine.missions(snapshots.methanoicacid).some(m=>m.kind==='bonds'), 'no empty acid bond task');
const slot8 = copy(snapshots.butanol_2), suffix = slot8.pieces.find(p=>p.text==='όλη');
suffix.id='comp8'; suffix.mode='compBondType2';
equal(engine.missions(slot8).find(m=>m.family==='hydroxyl').pieceId, 'comp8', 'literal alcohol recognized at native slot8');
for (const [label, mutate, code] of [
  ['unsupported', s=>{s.moleculeId='ethyl_3_dimethyl_2_5_hexane';},'unsupported-molecule'],
  ['roundtrip', s=>{s.correctName+='x';},'name-roundtrip'],
  ['duplicate atom', s=>{s.atoms[1].id=s.atoms[0].id;},'atom'],
  ['duplicate bond', s=>{s.bonds[1].id=s.bonds[0].id;},'bond'],
  ['dangling bond', s=>{s.bonds[0].a=999;},'bond'],
  ['self bond', s=>{s.bonds[0].a=s.bonds[0].b;},'bond'],
  ['invalid valence', s=>{s.bonds[0].order=2;},'expanded-valence'],
  ['implicit H', s=>{s.atoms.pop();s.bonds.pop();},'expanded-valence'],
  ['classification', s=>{s.series='alkenes';},'classification'],
  ['wrong graph identity', s=>{s.moleculeId='butane';},'molecule-identity']
]) {
  const value=copy(snapshots.ethane); mutate(value);
  equal(engine.validateSnapshot(value).code,code,label+' fails closed');
  checks++; assert.throws(()=>engine.missions(value), problem=>problem.code===code,label+' cannot make missions');
}
const wrongPiece=copy(snapshots.ethane);
wrongPiece.pieces.find(p=>p.mode==='compBondType').text='έν';wrongPiece.correctName=wrongPiece.pieces.map(p=>p.text).join('');
checks++; assert.throws(()=>engine.missions(wrongPiece),e=>e.code==='bond-text','contradictory bond constituent');
equal(engine.grade(diene,{atoms:[],bonds:['1',3]}), {correct:false,kind:'incorrect'}, 'raw numeric IDs required');
// The engine file is browser-loadable without CommonJS.
const browser={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,inputs[2]),'utf8'),browser);
okay(Object.isFrozen(browser.window.NameleculeMolecularDetectiveEngine), 'browser IIFE API');
const out={recordedUTC:new Date().toISOString(),role:'Developer execution',completed:true,checks,moleculeCount:records.length,
  missionCount,acceptedAlternatives:alternatives,records,
  inputSHA256:Object.fromEntries(inputs.map(file=>[file,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')])),
  limitations:['No browser/DOM/JSME click or typography execution in this engine test. Name pieces use actual core56 output plus the native Greek euphony rule; host/browser validation is separate.',
    'Only the approved 17 starter molecules are supported; no general library or IUPAC certification is claimed.']};
if (process.argv.includes('--write')) {
  fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(out,null,2)+'\n');
  fs.writeFileSync(path.join(__dirname,'snapshots.json'),JSON.stringify(snapshots,null,2)+'\n');
}
console.log(JSON.stringify({completed:out.completed,checks,molecules:records.length,missionCount,acceptedAlternatives:alternatives}));
