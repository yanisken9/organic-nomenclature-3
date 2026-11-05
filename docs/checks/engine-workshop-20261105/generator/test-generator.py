"""Real core54 -> pure generator -> existing repair validation, macOS JSC only.

Run from the repository root with Python 3. No dependencies or browser required.
This is Developer headless evidence; browser/Worker checks are separate.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
OUT = Path(__file__).with_name('results.json')
core_path = ROOT / 'js/mulermoc-nom-core-54.js'
catalog_path = ROOT / 'games/data/alkane-structures.json'
generator_path = ROOT / 'js/namelecule-repair-generator.js'
repair_path = ROOT / 'js/namelecule-game-repair.js'
catalog = json.loads(catalog_path.read_text())
core = core_path.read_text()
assert hashlib.sha256(core_path.read_bytes()).hexdigest() == catalog['engineSHA256']

# Independently authored chemical expectations are tests, never runtime answers.
EXPECTED = {
    'methane': ('μεθάνιο', 1, 1, 0),
    'ethane': ('αιθάνιο', 2, 2, 0),
    'propane': ('προπάνιο', 3, 3, 0),
    'butane': ('βουτάνιο', 4, 4, 0),
    'pentane': ('πεντάνιο', 5, 5, 0),
    'methyl_2_pentane': ('2-μεθυλοπεντάνιο', 5, 6, 1),
    'dimethyl_2_3_butane': ('2,3-διμεθυλοβουτάνιο', 4, 6, 2),
    'ethyl_3_dimethyl_2_5_hexane': ('3-αιθυλο-2,5-διμεθυλοεξάνιο', 6, 10, 3),
}

analysis_body = '''
var selectedMol=molecule.id,mode2D='expanded',mainChainMode='algorithmic',jsmeNomeclatureApplet;
''' + core + r'''
const parsed=fParseMolV2000(molecule.mol);
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>parsed.atoms.length,
 totalNumberOfBonds:()=>parsed.bonds.length,getAtom:(_,i)=>({label:parsed.atoms[i-1].el}),
 getBond:(_,i)=>({atoms:parsed.bonds[i-1].slice(0,2),order:parsed.bonds[i-1][2]}),
 molFile:()=>molecule.mol};
fAnalyseStructure();fDetectMolType();fGuessName();
return {moleculeId:molecule.id,name:currentMolName,parts:nameComponentsList.slice(),
 chain:mainChainAtomsList.slice(),branches:fGetHydrocarbonSubstituentInfo(),
 classification:fGetMoleculeClassification(),carbonCount:parsed.atoms.filter(a=>a.el==='C').length,
 rootVocabulary:nameMainCompList1.slice(),
 engineSHA256:engineHash};
'''

js = ('const catalog=' + json.dumps(catalog) + ';\n' +
      'const expected=' + json.dumps(EXPECTED) + ';\n' +
      'const analyze=new Function("molecule","engineHash",' + json.dumps(analysis_body) + ');\n' +
      repair_path.read_text() + '\n' + generator_path.read_text() + '\n')
js += r'''
function check(value,label){if(!value)throw Error(label)}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label)}
function clone(value){return JSON.parse(JSON.stringify(value))}
function throws(action,label){let failed=false;try{action()}catch(e){failed=true}check(failed,label)}
function freeze(value){Object.freeze(value);Object.keys(value).forEach(k=>{if(value[k]&&typeof value[k]==='object'&&!Object.isFrozen(value[k]))freeze(value[k])});return value}
const analyses=catalog.molecules.map(m=>analyze(m,catalog.engineSHA256));
analyses.forEach(a=>equal([a.name,a.chain.length,a.carbonCount,a.branches.length],expected[a.moleculeId],'independent name/graph oracle '+a.moleculeId));
const engine=NameleculeRepairEngine,generator=NameleculeRepairGenerator;
const original=JSON.stringify([catalog,analyses]);
freeze(catalog);freeze(analyses);
const analysisById=Object.fromEntries(analyses.map(a=>[a.moleculeId,a]));
const allVariants=new Set(),allMolecules=new Set(),allFamilies=new Set(),questionOrders=new Set(),choiceOrders=new Map();
const familyCounts={},exampleByFamily={};
let roundsChecked=0,repairsChecked=0,restoreChecks=0;
const engineRoots=[''].concat(analyses[0].rootVocabulary);
const largestCarbonCount=Math.max(...analyses.map(a=>a.carbonCount));
function inspect(round,difficulty){
  roundsChecked++;
  engine.validateRoundData(round);
  const a=analysisById[round.moleculeId];
  check(round.correctName===expected[round.moleculeId][0],'correct name independent oracle');
  check(round.guided===false,'no guided rounds');
  check(round.feedback.wrongPart==='Αυτό το συνθετικό συμφωνεί με τη δομή.','wrong-part feedback');
  check(!/\d/.test(round.diagramAlt)&&!round.diagramAlt.includes(a.name),'diagram alt has no answer or locants');
  if(difficulty==='challenge')check(round.objective==='Ένα μέρος του ονόματος δεν συμφωνεί με τη δομή. Εντόπισέ το και επισκεύασέ το.','challenge neutral');
  else check(round.objective!=='Ένα μέρος του ονόματος δεν συμφωνεί με τη δομή. Εντόπισέ το και επισκεύασέ το.','basic feature prompt');
  allVariants.add(round.fault.signature);allMolecules.add(round.moleculeId);allFamilies.add(round.fault.kind);
  familyCounts[round.fault.kind]=(familyCounts[round.fault.kind]||0)+1;
  exampleByFamily[round.fault.kind]=exampleByFamily[round.fault.kind]||round;
  const initial=engine.createRoundState(round);
  check(engine.evaluateRepair(round,initial).kind!=='correct','starts faulty');
  let solutions=0;
  if(round.kind==='replace'){
    const pristine=a.parts.map((text,slot)=>text?{id:'component-'+slot,text}:null).filter(Boolean);
    const changed=round.parts.filter((p,index)=>p.text!==pristine[index].text);
    check(changed.length===1&&changed[0].id===round.targetPartId,'exactly one changed engine component');
    equal(round.parts.map(p=>p.id),pristine.map(p=>p.id),'all other engine components retained');
    check(a.parts[+round.targetPartId.split('-')[1]]===round.correctValue,'correct fragment comes from engine');
    round.parts.forEach(part=>round.choices.forEach(choice=>{
      const state=engine.createRoundState(round);state.selectedPartId=part.id;state.selectedValue=choice.value;
      const result=engine.evaluateRepair(round,state);repairsChecked++;
      if(result.kind==='correct'){solutions++;check(result.name===a.name,'accepted repair matches chemical engine')}
      if(part.id!==round.targetPartId)check(result.kind==='wrongPart','correct fragment rejected as target');
    }));
    const choiceKey=round.id+':'+round.choices.map(c=>c.value).slice().sort().join('|');
    if(!choiceOrders.has(choiceKey))choiceOrders.set(choiceKey,new Set());
    choiceOrders.get(choiceKey).add(round.choices.map(c=>c.value).join('|'));
    if(round.fault.kind==='parent-length'){
      const maxLocant=a.branches.reduce((max,b)=>Math.max(max,b.locant),0);
      round.choices.filter(c=>c.value!==round.correctValue).forEach(c=>{
        check(engineRoots.indexOf(c.value)>maxLocant,'root distractor preserves branch locants');
        check(engineRoots.indexOf(c.value)<=largestCarbonCount,'root distractor stays in pilot carbon range');
      });
      check(engineRoots.indexOf(changed[0].text)>maxLocant,'faulty root preserves branch locants');
      check(engineRoots.indexOf(changed[0].text)<=largestCarbonCount,'faulty root stays in pilot carbon range');
    }
    if(round.fault.kind==='bond-type')check(a.branches.length===0&&[2,3].includes(a.chain.length),'no methane or second missing bond locant');
    if(round.fault.kind==='branch-locants'){
      const slot=+round.targetPartId.split('-')[1];
      const correct=a.parts[slot].replace(/^-|-$/g,'').split(',').map(Number);
      const reverse=correct.map(n=>a.chain.length+1-n).sort((x,y)=>x-y).join(',');
      if(round.moleculeId==='dimethyl_2_3_butane')check(changed[0].text!=='2,3-','symmetric reverse never fault');
      round.choices.forEach(c=>{
        const locants=c.value.replace(/^-|-$/g,'').split(',').map(Number);
        check(locants.length===correct.length&&locants.every(n=>n>1&&n<a.chain.length),'valid interior locants and fixed count');
        const occupancy={};
        a.branches.filter(b=>!correct.includes(b.locant)||!a.parts[slot+1].endsWith(b.name)).forEach(b=>{occupancy[b.locant]=(occupancy[b.locant]||0)+1});
        locants.forEach(n=>{occupancy[n]=(occupancy[n]||0)+1});
        check(Object.values(occupancy).every(n=>n<=2),'locant choices respect carbon valence');
      });
    }
  }else{
    check(round.moleculeId==='ethyl_3_dimethyl_2_5_hexane','order only for two different groups');
    [round.movablePartIds,round.movablePartIds.slice().reverse()].forEach(order=>{
      const state=engine.createRoundState(round);state.order=order.slice();
      const result=engine.evaluateRepair(round,state);repairsChecked++;
      if(result.kind==='correct'){solutions++;check(result.name===a.name,'correct order preserves exact engine name')}
    });
  }
  check(solutions===1,'exactly one legal solution '+round.id);
  const solved=engine.createRoundState(round);
  solved.selectedPartId=round.targetPartId||round.correctOrder[0];
  if(round.kind==='replace')solved.selectedValue=round.correctValue;else solved.order=round.correctOrder.slice();
  solved.attempts=2;solved.submitted=true;solved.solved=true;
  const restored=engine.restoreRoundState(round,clone(solved));
  check(restored.solved&&engine.evaluateRepair(round,restored).kind==='correct','legitimate restore');restoreChecks++;
  const forged=clone(solved);
  if(round.kind==='replace')forged.selectedValue=round.choices.find(c=>c.value!==round.correctValue).value;
  else forged.order=round.movablePartIds.slice();
  check(!engine.restoreRoundState(round,forged).solved,'forged completion not restored');restoreChecks++;
}
for(const difficulty of ['basic','challenge'])for(let seed=0;seed<256;seed++){
  const game=generator.createGame(catalog,analyses,{seed,difficulty});
  engine.validateGameData(game);
  equal(game,generator.createGame(catalog,analyses,{seed:String(seed),difficulty}),'same seed deterministic including choices');
  equal(game,generator.createGame(catalog,analysisById,{seed,difficulty}),'analysis array/map same output');
  const ids=game.sets.flatMap(s=>s.rounds.map(r=>r.id));
  check(new Set(ids).size===6,'unique round ids');
  check(new Set(game.sets.flatMap(s=>s.rounds.map(r=>r.fault.signature))).size===6,'unique fault signatures');
  game.sets.forEach(s=>{
    check(new Set(s.rounds.map(r=>r.moleculeId)).size===3,'prefer three different structures');
    if(s.id==='alkanes-branched')equal(s.rounds.map(r=>r.moleculeId).sort(),['dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane','methyl_2_pentane'].sort(),'all three branched structures');
    questionOrders.add(s.id+':'+s.rounds.map(r=>r.moleculeId).join('|'));
    s.rounds.forEach(r=>inspect(r,difficulty));
  });
}
equal(JSON.stringify([catalog,analyses]),original,'generation never mutates inputs');
check(allMolecules.size===8,'all eight available structures sampled');
equal(Array.from(allFamilies).sort(),['parent-length','bond-type','branch-locants','branch-multiplier','alphabetical-order'].sort(),'every supported fault family exercised');
check(questionOrders.size>10,'seed changes structure selection and question order');
check(Array.from(choiceOrders.values()).some(orders=>orders.size>1),'same fault choices shuffle between seeds');
// Prove the generator consumes the chemical result rather than a molecule-ID key.
const changed=clone(analyses);
changed.find(a=>a.moleculeId==='methane').parts[5]='δοκιμή';
changed.find(a=>a.moleculeId==='methane').name='δοκιμήάνιο';
changed.forEach(a=>{a.rootVocabulary[0]='δοκιμή'});
let sensitivity=false;
for(let seed=0;seed<32&&!sensitivity;seed++){
 const game=generator.createGame(catalog,changed,{seed});
 const round=game.sets[0].rounds.find(r=>r.moleculeId==='methane');
 if(round){check(round.correctName==='δοκιμήάνιο'&&round.correctValue==='δοκιμή','engine output sensitivity');sensitivity=true}
}
check(sensitivity,'sensitivity molecule sampled');
const broken=clone(analyses);broken[0].name='authored answer';
throws(()=>generator.createGame(catalog,broken,{seed:1}),'reject inconsistent name/components');
const wrongHash=clone(analyses);wrongHash[0].engineSHA256='0'.repeat(64);
throws(()=>generator.createGame(catalog,wrongHash),'reject engine revision mismatch');
const wrongGraph=clone(analyses);wrongGraph.find(a=>a.branches.length).branches[0].attach=999;
throws(()=>generator.createGame(catalog,wrongGraph),'reject corrupt graph attachment');
const missingVocabulary=clone(analyses);delete missingVocabulary[0].rootVocabulary;
throws(()=>generator.createGame(catalog,missingVocabulary),'reject missing engine grammar');
const mixedVocabulary=clone(analyses);mixedVocabulary[0].rootVocabulary[19]='δοκιμή';
throws(()=>generator.createGame(catalog,mixedVocabulary),'reject inconsistent engine grammar');
throws(()=>generator.createGame(catalog,analyses.slice(1)),'reject missing analysis');
throws(()=>generator.createGame(catalog,analyses.concat([analyses[0]])),'reject duplicate analysis');
throws(()=>generator.createGame(catalog,analyses,{difficulty:'expert'}),'reject unsupported difficulty');
throws(()=>generator.createGame(catalog,analyses,{seed:{}}),'reject invalid seed');
const reordered=clone(catalog);reordered.molecules.reverse();
equal(generator.createGame(catalog,analyses,{seed:42}),generator.createGame(reordered,analyses.slice().reverse(),{seed:42}),'input enumeration order does not change recipe');
equal(generator.normalizeSeed(42),'42','seed normalized as string');
const basic=generator.createGame(catalog,analyses,{seed:42,difficulty:'basic'}),challenge=generator.createGame(catalog,analyses,{seed:42,difficulty:'challenge'});
equal(basic.sets.flatMap(s=>s.rounds.map(r=>r.id)),challenge.sets.flatMap(s=>s.rounds.map(r=>r.id)),'difficulty changes guidance, not seed or structures');
print(JSON.stringify({status:'pass',generatorVersion:generator.version,seedCount:256,difficulties:['basic','challenge'],gamesChecked:512,
 roundsChecked,repairsChecked,restoreChecks,independentNames:analyses.map(a=>({moleculeId:a.moleculeId,name:a.name,parentLength:a.chain.length,carbonCount:a.carbonCount})),
 uniqueFaultVariants:allVariants.size,availableMoleculesSampled:allMolecules.size,questionOrders:questionOrders.size,
 choiceSetsWithMultipleOrders:Array.from(choiceOrders.values()).filter(orders=>orders.size>1).length,familyCounts,exampleByFamily,
 deterministic:true,inputImmutable:true,engineOutputSensitive:true,invalidInputChecks:9,
 limitations:['Headless JavaScriptCore; not an actual browser Worker or UI replay.','Eight fixed structures; random fault/choice/order variants do not create new molecular structures.','Parent-length alternatives come from the actual core rootVocabulary, bounded to the catalog maximum total carbon count (10); correct fragments come from real core54 parts.']}));
'''
result = subprocess.run([JSC, '-e', 'eval(JSON.parse(readline()))'],
                        input=json.dumps(js) + '\n', text=True, capture_output=True)
if result.returncode:
    raise AssertionError((result.returncode, result.stdout[-6000:], result.stderr[-3000:]))
evidence = json.loads(result.stdout)
evidence['sha256'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in [core_path, catalog_path, generator_path, repair_path]}
OUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in evidence.items()
                  if key not in ['exampleByFamily', 'independentNames']}, ensure_ascii=False, indent=2))
