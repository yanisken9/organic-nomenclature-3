"""Bounded Developer regression evidence for the approved lesson feedback copy.

Run with Python 3 on macOS. Uses the actual pinned quiz chemistry core, catalog,
generator, repair engine and before/current adapters. Transport/DOM/WebCrypto are
mocked; Firefox interaction evidence is recorded separately. Private inspection
hooks exist only in the transient evaluated source, never in production files.
Writes only memory-results.json and memory-fixtures.json; the transient
memory-harness.js is removed.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
ENGINE = '3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306'
ADAPTER = 'js/namelecule-generated-repair-checkpoint.js'
CATALOG = 'games/data/alkane-structures.json'
REPAIR = 'js/namelecule-game-repair.js'
GENERATOR = 'js/namelecule-repair-generator.js'
CORE = 'js/chemistry-engines/' + ENGINE + '.js'
baseline = json.loads((HERE / 'baseline.json').read_text())
before_path = HERE / 'before' / ADAPTER
before = before_path.read_text()
current = (ROOT / ADAPTER).read_text()
catalog = json.loads((ROOT / CATALOG).read_text())
plan_messages = json.loads((ROOT / 'docs/checks/alkane-quiz-feedback-preflight-20261107/plan.json').read_text())['messages']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(before_path) == baseline['targets_before'][ADAPTER], 'Wrong before adapter snapshot'
assert sha(ROOT / CORE) == catalog['engineSHA256'] == ENGINE, 'Wrong pinned quiz engine'
for path in (CATALOG, REPAIR, GENERATOR):
    assert sha(ROOT / path) == baseline['protected'][path], 'Protected quiz input changed: ' + path

# The same narrow engine-to-generator extraction as the existing reviewed harness.
# The full pinned core is evaluated; no current-main core substitution is allowed.
analysis_body = """
var selectedMol=molecule.id,mode2D='expanded',mainChainMode='algorithmic',jsmeNomeclatureApplet;
""" + (ROOT / CORE).read_text() + """
const parsed=fParseMolV2000(molecule.mol);
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>parsed.atoms.length,
 totalNumberOfBonds:()=>parsed.bonds.length,getAtom:(_,i)=>({label:parsed.atoms[i-1].el}),
 getBond:(_,i)=>({atoms:parsed.bonds[i-1].slice(0,2),order:parsed.bonds[i-1][2]}),
 molFile:()=>molecule.mol};
fAnalyseStructure();fDetectMolType();fGuessName();
return {moleculeId:molecule.id,name:currentMolName,parts:nameComponentsList.slice(),
 chain:mainChainAtomsList.slice(),branches:fGetHydrocarbonSubstituentInfo(),
 classification:fGetMoleculeClassification(),carbonCount:parsed.atoms.filter(a=>a.el==='C').length,
 rootVocabulary:nameMainCompList1.slice(),engineSHA256:engineHash};
"""
js = '\n'.join([
    'const catalog=' + json.dumps(catalog) + ';',
    'const expectedMessages=' + json.dumps(plan_messages, ensure_ascii=False) + ';',
    'const beforeSource=' + json.dumps(before) + ';',
    'const currentSource=' + json.dumps(current) + ';',
    'const analyze=new Function("molecule","engineHash",' + json.dumps(analysis_body) + ');',
    (ROOT / REPAIR).read_text(),
    (ROOT / GENERATOR).read_text(),
])
js += r'''
let checks=0;
function check(value,label){if(!value)throw Error(label);checks++;}
function stable(value){return Array.isArray(value)?value.map(stable):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,stable(value[k])])):value;}
function equal(a,b,label){check(JSON.stringify(stable(a))===JSON.stringify(stable(b)),label);}
function clone(value){return JSON.parse(JSON.stringify(value));}
function freeze(value){if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.keys(value).forEach(k=>freeze(value[k]));Object.freeze(value);}return value;}
function diffs(a,b,path=''){if(a===b)return [];if(a&&b&&typeof a==='object'&&typeof b==='object'){const keys=new Set(Object.keys(a).concat(Object.keys(b)));return [...keys].flatMap(k=>diffs(a[k],b[k],path?path+'.'+k:k));}return [path];}
const global=globalThis;
global.window=global;
// The generator owns its seeded RNG. Only unrelated UI choice shuffling is fixed
// to compare identical receipt restoration in two separate adapter instances.
Math.random=()=>0.5;
const engine=NameleculeRepairEngine;
const originalGenerator=NameleculeRepairGenerator;
const analyses=freeze(catalog.molecules.map(m=>analyze(m,catalog.engineSHA256)));
const seeds=['1','4'];
const games=Object.fromEntries(seeds.map(seed=>[seed,freeze(originalGenerator.createGame(catalog,analyses,{seed,difficulty:'basic'}))]));
freeze(catalog);
const generatedSummary=seeds.map(seed=>({seed,sets:games[seed].sets.map(set=>({id:set.id,rounds:set.rounds.map(r=>({id:r.id,family:r.fault.kind,kind:r.kind}))}))}));
const examples={};
seeds.forEach(seed=>games[seed].sets.forEach(set=>set.rounds.forEach(round=>{examples[round.fault.kind]=examples[round.fault.kind]||round;})));
equal(Object.keys(examples).sort(),['alphabetical-order',...Object.keys(expectedMessages)].sort(),'two bounded seeds cover all four reminder families and real order fallback');
check(originalGenerator.version==='1.0.0'&&seeds.every(seed=>games[seed].generatorVersion==='1.0.0'),'generator version preserved');

class FakeNode{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attrs={};this.handlers={};}
 replaceChildren(...children){this.children=children;}
 setAttribute(k,v){this.attrs[k]=v;}
 removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.handlers[k]=fn;}
 querySelector(){return null;}
}
global.document={baseURI:'http://memory.test/',createElement:tag=>new FakeNode(tag)};
global.URL=class{constructor(path,base){this.href=base+path;}};
global.TextDecoder=class{decode(bytes){return bytes;}};
const digest=Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(x=>parseInt(x,16)));
global.crypto={subtle:{digest:async()=>digest},getRandomValues:values=>{values.fill(123);return values;}};
global.AbortController=class{
 constructor(){const listeners=new Set();this.signal={aborted:false,addEventListener:(_,fn)=>listeners.add(fn),removeEventListener:(_,fn)=>listeners.delete(fn)};
 this.abort=()=>{if(this.signal.aborted)return;this.signal.aborted=true;[...listeners].forEach(fn=>fn());};}
};
let timerId=0;
const timers=new Set();
global.setTimeout=()=>{timers.add(++timerId);return timerId;};
global.clearTimeout=id=>timers.delete(id);
let fetched=0,analysisRequests=0;
global.fetch=async()=>{fetched++;return {ok:true,arrayBuffer:async()=>JSON.stringify(catalog)};};
global.NameleculeChemistryClient={analyze:async molecule=>{analysisRequests++;return clone(analyses.find(a=>a.moleculeId===molecule.id));}};
function loadAdapter(source,inspect){
 let adapter=null,registration=null;
 global.NameleculeQuizCheckpoints={registerType:(name,value)=>{registration=name;adapter=value;}};
 delete global.__memoryPrivate;
 if(inspect){
  const marker='  global.NameleculeQuizCheckpoints.registerType(';
  check(source.split(marker).length===2,'single private instrumentation insertion');
  const hook='  global.__memoryPrivate={getPrepared:(recipe,seed)=>prepared.get(key(recipe,seed))'+
   (source.includes('function lessonRoundForDisplay(')?',display:lessonRoundForDisplay':'')+'};\n';
  source=source.replace(marker,hook.replace(/\\n/g,'\n')+marker);
 }
 new Function(source)();
 check(registration==='generated-name-repair-set','same registered checkpoint type');
 equal(Object.keys(adapter).sort(),['mount','prepare','restore','validate'],'no new exported adapter API');
 return {adapter,private:global.__memoryPrivate};
}
// First execute the untouched production source: instrumentation is not needed
// for registration and does not become an added production API.
loadAdapter(currentSource,false);
check(!('__memoryPrivate' in global),'unmodified production source exposes no private hook');
const {private:inspection}=loadAdapter(currentSource,true);
const display=inspection.display;
const mappingEvidence=[];
for(const family of Object.keys(expectedMessages)){
 const round=examples[family],beforeJSON=JSON.stringify(round),shown=display(round);
 check(Object.isFrozen(round)&&Object.isFrozen(round.feedback),'frozen canonical fixture '+family);
 check(shown!==round&&shown.feedback!==round.feedback,'only round/feedback copied '+family);
 equal(diffs(round,shown),['feedback.wrongPart'],'only wrongPart value differs '+family);
 equal(Object.keys(shown),Object.keys(round),'round keys preserved '+family);
 equal(Object.keys(shown.feedback),Object.keys(round.feedback),'feedback keys preserved '+family);
 equal(shown.feedback.wrongPart,expectedMessages[family],'approved general mission message '+family);
 for(const field of Object.keys(round).filter(k=>k!=='feedback'))check(shown[field]===round[field],'non-feedback reference/value contract '+family+' '+field);
 check(JSON.stringify(round)===beforeJSON,'canonical input unchanged '+family);
 equal(display(round).feedback.wrongPart,shown.feedback.wrongPart,'repeat from canonical does not accumulate '+family);
 // A generic reminder cannot depend on identifying or answer-bearing fields.
 const secret=clone(round);
 secret.id='PRIVATE_ID';secret.correctName='PRIVATE_FULL_ANSWER';secret.correctValue='PRIVATE_FRAGMENT_ANSWER';
 secret.targetPartId='PRIVATE_TARGET';secret.parts=[{id:'PRIVATE_PART',text:'PRIVATE_TEXT'}];secret.choices=[{value:'PRIVATE_CHOICE'}];
 equal(display(secret).feedback.wrongPart,shown.feedback.wrongPart,'message independent of answers/target/choices '+family);
 check(!/\d/.test(shown.feedback.wrongPart)&&!shown.feedback.wrongPart.includes(round.correctName),'no numeric or full-name answer disclosure '+family);
 shown.feedback.wrongPart='LOCAL_DISPLAY_CHANGE';
 check(JSON.stringify(round)===beforeJSON,'display feedback mutation cannot alter canonical '+family);
 mappingEvidence.push({family,roundId:round.id,message:display(round).feedback.wrongPart});
}
const fallbackBase=examples['parent-length'];
const fallbacks=[null,undefined,{...fallbackBase,fault:undefined},{...fallbackBase,fault:{kind:'unknown'}},
 {...fallbackBase,fault:{kind:'toString'}},{...fallbackBase,fault:{kind:'__proto__'}},
 {...fallbackBase,feedback:undefined},{...fallbackBase,feedback:{wrongPart:42}},
 {...examples['alphabetical-order'],fault:{kind:'parent-length'}},examples['alphabetical-order']];
fallbacks.forEach((round,i)=>check(display(round)===round,'unchanged default/unknown/order fallback '+i));
const custom={...fallbackBase,feedback:{...fallbackBase.feedback,wrongPart:'Custom baseline.'}};
check(display(custom).feedback.wrongPart.startsWith('Custom baseline. '),'existing feedback prefix preserved');

// Evaluate all visible repair combinations within the 12 actual rounds, using
// the same engine contract. Only wrong-part messages may differ after copying.
let replaceCases=0,orderCases=0;
for(const seed of seeds)for(const set of games[seed].sets)for(const round of set.rounds){
 const shown=display(round);
 engine.validateRoundData(shown);
 if(round.kind==='replace'){
  let canonicalSolutions=0,displaySolutions=0;
  for(const part of round.parts)for(const choice of round.choices){
   const state=engine.createRoundState(round);state.selectedPartId=part.id;state.selectedValue=choice.value;
   const old=engine.evaluateRepair(round,state),next=engine.evaluateRepair(shown,state);
   if(old.kind==='correct')canonicalSolutions++;if(next.kind==='correct')displaySolutions++;
   if(old.kind==='wrongPart'){
    equal({...next,message:old.message},old,'wrong-part evaluation preserves kind/name '+round.id);
    equal(next.message,expectedMessages[round.fault.kind],'wrong-part evaluation uses mission reminder '+round.id);
   }else equal(next,old,'answer outcome/feedback unchanged '+round.id);
   replaceCases++;
  }
  check(canonicalSolutions===1&&displaySolutions===1,'same single accepted solution '+round.id);
 }else{
  check(shown===round,'actual order round passes through by identity');
  for(const order of [round.movablePartIds,round.correctOrder]){
   const state={...engine.createRoundState(round),order:order.slice()};
   equal(engine.evaluateRepair(shown,state),engine.evaluateRepair(round,state),'order semantics unchanged '+round.id);orderCases++;
  }
 }
}

function recipeFor(setId){return {version:1,setId,difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:catalog.revision,engineSHA256:catalog.engineSHA256};}
function solvedState(round){
 const s=engine.createRoundState(round);
 if(round.kind==='replace'){s.selectedPartId=round.targetPartId;s.selectedValue=round.correctValue;}
 else {s.selectedPartId=round.correctOrder[0];s.order=round.correctOrder.slice();}
 s.attempts=1;s.selectionMisses=2;s.submitted=true;s.solved=true;return s;
}
function receiptFor(seed,set,completed){return {version:1,seed,currentRound:Math.min(completed,2),states:set.rounds.map((r,i)=>i<completed?solvedState(r):engine.createRoundState(r)),solved:completed===3};}
function receiptCases(seed,set){
 const fresh=receiptFor(seed,set,0),wrong=clone(fresh),partial=receiptFor(seed,set,1),complete=receiptFor(seed,set,3),forged=clone(fresh),unsubmitted=clone(complete);
 const first=set.rounds[0];
 wrong.states[0].selectedPartId=first.parts.find(p=>p.id!==first.targetPartId).id;
 wrong.states[0].selectionMisses=3;
 forged.solved=true;forged.states.forEach(s=>{s.solved=true;s.submitted=true;s.attempts=1;});
 unsubmitted.states[0].submitted=false;
 return {fresh,wrongSelection:wrong,partial,complete,forged,unsubmitted};
}
async function turns(){for(let i=0;i<64;i++)await Promise.resolve();}
async function adapterRun(source,label){
 const results=[];
 for(const seed of seeds)for(const fixtureSet of games[seed].sets){
  const generated=[];
  global.NameleculeRepairGenerator={...originalGenerator,createGame:(...args)=>{const game=freeze(originalGenerator.createGame(...args));generated.push(game);return game;}};
  const {adapter,private:priv}=loadAdapter(source,true),recipe=recipeFor(fixtureSet.id),cases=receiptCases(seed,fixtureSet);
  const pending=Object.fromEntries(Object.entries(cases).map(([name,receipt])=>[name,adapter.restore(recipe,receipt)]));
  check(!pending.complete.solved,label+' cold receipt fails closed');
  await adapter.prepare(recipe,cases.complete,{});
  check(generated.length===1,label+' one canonical game prepared');
  equal(generated[0],games[seed],label+' same-seed generated game untouched');
  const canonical=priv.getPrepared(recipe,seed),canonicalJSON=JSON.stringify(canonical);
  check(canonical===generated[0].sets.find(s=>s.id===recipe.setId),label+' prepared cache retains generator set');
  check(Object.isFrozen(canonical)&&canonical.rounds.every(r=>Object.isFrozen(r)&&Object.isFrozen(r.feedback)),label+' frozen canonical cache');
  const restored=Object.fromEntries(Object.entries(cases).map(([name,receipt])=>[name,adapter.restore(recipe,receipt)]));
  check(restored.complete.solved,label+' complete receipt restored');
  check(!restored.forged.solved&&!restored.unsubmitted.solved,label+' false completion flags do not unlock');
  check(restored.partial.currentRound===1&&!restored.partial.solved,label+' partial progress remains next unsolved round');
  check(restored.wrongSelection.states[0].selectedPartId===cases.wrongSelection.states[0].selectedPartId&&restored.wrongSelection.states[0].selectionMisses===3,label+' wrong selection and miss count preserved');
  canonical.rounds.forEach((round,i)=>equal(engine.restoreRoundState(round,cases.complete.states[i]),engine.restoreRoundState(display(round),cases.complete.states[i]),label+' displayed round restores same legal answer '+round.id));
  const mounted=[],publications=[];let solvedCalls=0,continueCalls=0,destroyCalls=0;
  global.NameleculeRepairGame.mountRound=(host,options)=>{mounted.push(options);return {destroy(){destroyCalls++;}};};
  const handle=adapter.mount(new FakeNode('div'),{round:recipe,initialState:cases.wrongSelection,assetBase:'games/',onStateChange:s=>publications.push(clone(s)),onSolved:()=>solvedCalls++,onContinue:()=>continueCalls++});
  await turns();
  for(let index=0;index<3;index++){
   check(mounted.length===index+1,label+' shared mount reached exact next round');
   const options=mounted[index],round=canonical.rounds[index];
   const expected=label==='before'?round:display(round);
   equal(options.round,expected,label+' shared mount receives intended display round '+round.id);
   if(label==='after'&&round.kind==='replace')check(options.round!==round&&options.round.feedback!==round.feedback,label+' mounted replacement is temporary copy');
   else check(options.round===round,label+' unaltered round identity at mount');
   check(priv.getPrepared(recipe,seed)===canonical&&JSON.stringify(canonical)===canonicalJSON,label+' canonical retained during render');
   const answer=solvedState(round);
   options.onStateChange(answer);options.onSolved({kind:'correct'},answer);
   check(solvedCalls===(index===2?1:0),label+' gate waits for all three verified repairs');
   options.onContinue();
  }
  check(continueCalls===1&&publications[publications.length-1].solved,label+' final Continue advances theory once');
  check(JSON.stringify(canonical)===canonicalJSON&&generated.length===1,label+' rendering/progress never replaces or modifies canonical questions');
  handle.destroy();check(destroyCalls===3,label+' three round mounts disposed');
  results.push({seed,setId:recipe.setId,pending,restored,publications,solvedCalls,continueCalls});
 }
 return results;
}
async function main(){
 const before=await adapterRun(beforeSource,'before'),after=await adapterRun(currentSource,'after');
 equal(after,before,'all baseline/current receipt restoration and progress publications identical');
 check(timers.size===0,'no outstanding preparation timers');
 const screenshot=games['4'].sets[0].rounds[0];
 equal(screenshot.parts.map(p=>p.text),['προπ','ίν','ιο'],'exact original screenshot example reproduced');
 const wrong=engine.createRoundState(screenshot);wrong.selectedPartId=screenshot.parts[0].id;wrong.selectedValue=screenshot.correctValue;
 const prior=engine.evaluateRepair(screenshot,wrong),next=engine.evaluateRepair(display(screenshot),wrong);
 check(prior.kind==='wrongPart'&&prior.message==='Αυτό το συνθετικό συμφωνεί με τη δομή.','original generic feedback reproduced');
 check(next.kind==='wrongPart'&&next.message===expectedMessages['bond-type'],'original failure gains approved bond mission reminder');
 print(JSON.stringify({status:'passed',kind:'Developer verification, not independent review',checks,realPinnedEngineAnalyses:analyses.length,seeds,canonicalRounds:12,replaceChoiceCases:replaceCases,orderCases,fixtures:seeds.map(seed=>({seed,sets:games[seed].sets.map(set=>({id:set.id,rounds:set.rounds}))})),preparedAdapterRuns:8,receiptCasesPerRun:6,fetched,analysisRequests,mappings:mappingEvidence,generatedSummary,originalExample:{seed:'4',roundId:screenshot.id,parts:screenshot.parts.map(p=>p.text),selected:screenshot.parts[0].text,before:prior.message,after:next.message},invariants:['Exact before/current adapter registered API preserved','Only display feedback.wrongPart differs; canonical rounds and feedback frozen and unchanged','All four messages match approved wording and are independent of answer/target/choice values','Unknown/missing/order cases retain original object and feedback','Same-seed full games and generatorVersion unchanged','Fresh, wrong-selection, partial, complete, forged and unsubmitted receipts restore identically','Both three-round sets mount display copies while cache retains canonical sets','Progress publications and unlock/continue behavior match baseline'],limitations:['JSC macOS execution; DOM, network transport, WebCrypto, timers and chemistry-client delivery mocked','Actual pinned chemistry calculations and actual generator/repair/adapter code executed; UI choice RNG fixed for deterministic receipt comparison','Only seeds 1 and 4, selected to cover all four affected families, real ordering fallback and original propane example; not exhaustive generator enumeration','Private inspection hooks inserted only into evaluated in-memory adapter strings','Firefox selection/reopen/reload/narrow-layout and lesson navigation are outside this harness and owned by root; no browser claims from this harness']}));
}
main().catch(error=>{print('FAIL '+error.message+'\n'+error.stack);throw error;});
'''
script = HERE / 'memory-harness.js'
script.write_text(js)
try:
    result = subprocess.run([JSC, str(script.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
finally:
    script.unlink()
if result.returncode or 'FAIL ' in result.stdout or not result.stdout.strip():
    print(result.stdout, end='')
    print(result.stderr, end='')
    raise SystemExit(result.returncode or 1)
report = json.loads(result.stdout.strip().splitlines()[-1])
fixtures = report.pop('fixtures')
(HERE / 'memory-fixtures.json').write_text(json.dumps(fixtures, ensure_ascii=False, separators=(',', ':')) + '\n')
report['fixtureSHA256'] = sha(HERE / 'memory-fixtures.json')
report['sourceSHA256'] = {path: sha(ROOT / path) for path in (ADAPTER, CATALOG, REPAIR, GENERATOR, CORE)}
report['beforeAdapterSHA256'] = sha(before_path)
report['harnessSHA256'] = sha(Path(__file__))
report['command'] = 'python3 docs/checks/alkane-quiz-feedback-20261107/check-memory.py'
(HERE / 'memory-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('status', 'checks', 'realPinnedEngineAnalyses', 'canonicalRounds', 'replaceChoiceCases', 'orderCases', 'preparedAdapterRuns')}, ensure_ascii=False))
