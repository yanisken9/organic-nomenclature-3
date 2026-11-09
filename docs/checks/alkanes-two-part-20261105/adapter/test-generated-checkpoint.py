"""Developer headless checks: real core/generator, mocked browser transport and UI."""
from pathlib import Path
import hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[4]
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
HERE = Path(__file__).resolve().parent
catalog_path = ROOT/'games/data/alkane-structures.json'
catalog = json.loads(catalog_path.read_text())
assert hashlib.sha256(catalog_path.read_bytes()).hexdigest() == '9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'
# Reuse only the reviewed pure analysis-function definition, never execute its tests/output writes.
source = (ROOT/'docs/checks/engine-workshop-20261105/generator/test-generator.py').read_text()
body = source.split("analysis_body = ",1)[1].split("\njs = ",1)[0]
analysis_body = eval(body, {'core': (ROOT/'js/mulermoc-nom-core-54.js').read_text()})
js = 'const catalog='+json.dumps(catalog)+';\nconst analyze=new Function("molecule","engineHash",'+json.dumps(analysis_body)+');\n'
js += (ROOT/'js/namelecule-game-repair.js').read_text()+'\n'+(ROOT/'js/namelecule-repair-generator.js').read_text()+'\n'
js += 'const controllerSource='+json.dumps((ROOT/'js/namelecule-quiz-checkpoints.js').read_text())+';\n'
js += 'const adapterSource='+json.dumps((ROOT/'js/namelecule-generated-repair-checkpoint.js').read_text())+';\n'
js += r'''
let count=0;
function check(value,label){if(!value)throw Error(label);count++;}
function stable(x){return Array.isArray(x)?x.map(stable):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;}
function equal(a,b,label){check(JSON.stringify(stable(a))===JSON.stringify(stable(b)),label)}
function clone(v){return JSON.parse(JSON.stringify(v));}
function throws(fn,label){let caught=false;try{fn()}catch(_){caught=true}check(caught,label)}
const analyses=catalog.molecules.map(m=>analyze(m,catalog.engineSHA256));
const recipe={version:1,setId:'alkanes-unbranched',difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:catalog.revision,engineSHA256:catalog.engineSHA256};
const digest=Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(x=>parseInt(x,16)));
const global=globalThis;
global.window=global;
let nextTimer=0,timers=new Map(),fetches=0,analysesRequested=0,failFetch=false,fetchWait=null;
global.setTimeout=fn=>{timers.set(++nextTimer,fn);return nextTimer;};
global.clearTimeout=id=>timers.delete(id);
global.URL=class {constructor(path,base){this.href=path.startsWith('http')?path:base+path;}};
global.TextDecoder=class {decode(bytes){return bytes;}};
global.crypto={getRandomValues:values=>{values[0]=1234;values[1]=5678;return values;},subtle:{digest:()=>Promise.resolve(digest)}};
global.AbortController=class {constructor(){const listeners=new Set();this.signal={aborted:false,addEventListener:(_,fn)=>listeners.add(fn),removeEventListener:(_,fn)=>listeners.delete(fn)};this.abort=()=>{if(this.signal.aborted)return;this.signal.aborted=true;Array.from(listeners).forEach(fn=>fn());};}};
global.fetch=async(url,options)=>{fetches++;if(failFetch)throw Error('network failure');if(fetchWait)await new Promise((resolve,reject)=>{const aborted=()=>{const e=Error('cancelled');e.name='AbortError';reject(e);};options.signal.addEventListener('abort',aborted);fetchWait.then(()=>{options.signal.removeEventListener('abort',aborted);resolve();});});return {ok:true,arrayBuffer:async()=>JSON.stringify(catalog)};};
global.NameleculeChemistryClient={analyze:async(m,options)=>{analysesRequested++;if(options.signal.aborted)throw Error('aborted');return clone(analyses.find(a=>a.moleculeId===m.id));}};
class FakeNode {constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attrs={};this.handlers={};this.classList={contains:()=>false,add:()=>{},remove:()=>{}};}append(...items){this.children.push(...items);}replaceChildren(...items){this.children=items;}setAttribute(k,v){this.attrs[k]=v;}removeAttribute(k){delete this.attrs[k];}addEventListener(k,fn){this.handlers[k]=fn;}querySelector(){return null;}focus(){} }
global.document={baseURI:'http://example.test/',createElement:tag=>new FakeNode(tag)};
const storage=new Map();
global.sessionStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value)};
let adapter;
function stack(){new Function(controllerSource)();const register=NameleculeQuizCheckpoints.registerType;NameleculeQuizCheckpoints.registerType=(name,impl)=>{adapter=impl;register(name,impl);};new Function(adapterSource)();}
function stateFor(set,complete=3){return {version:1,seed:'12345678',currentRound:Math.min(complete,2),states:set.rounds.map((r,i)=>{const s=NameleculeRepairEngine.createRoundState(r);if(i<complete){s.selectedPartId=r.targetPartId||r.correctOrder[0];if(r.kind==='replace')s.selectedValue=r.correctValue;else s.order=r.correctOrder.slice();s.attempts=1;s.submitted=true;s.solved=true;}return s;}),solved:true};}
function setFor(r=recipe){return NameleculeRepairGenerator.createGame(catalog,analyses,{seed:'12345678',difficulty:'basic'}).sets.find(s=>s.id===r.setId);}
function scenario(){return {title:'test',author:'Tester',steps:[{}, {checkpoint:{version:1,id:'first',type:'generated-name-repair-set',round:clone(recipe)}}, {}, {checkpoint:{version:1,id:'second',type:'generated-name-repair-set',round:{...recipe,setId:'alkanes-branched'}}}, {}]};}
function save(scen,states){const content=JSON.stringify({version:1,title:scen.title,author:scen.author,steps:scen.steps});let h=2166136261;for(let i=0;i<content.length;i++)h=Math.imul(h^content.charCodeAt(i),16777619);const key='namelecule:lesson-checkpoints:v1:'+(h>>>0).toString(16);storage.set(key,JSON.stringify({version:1,content,states}));return key;}
async function turns(){for(let i=0;i<40;i++)await Promise.resolve();}
async function main(){
 stack();
 check(adapter.validate(recipe)===recipe,'valid bounded recipe');
 for(const changed of [{...recipe,roundCount:2},{...recipe,setId:'unknown'},{...recipe,catalogUrl:'https://elsewhere.test/'},{...recipe,engineSHA256:'0'.repeat(64)},{...recipe,difficulty:'challenge'}])throws(()=>adapter.validate(changed),'invalid recipe rejected');
 const set=setFor(), saved=stateFor(set);
 const pending=adapter.restore(recipe,saved);
 check(!pending.solved,'unprepared receipt fails closed');equal(pending.states,saved.states,'pending answer data retained');
 check(adapter.prepare(recipe,null,{})===null,'no state does not trigger engine work');
 check(adapter.restore(recipe,{...saved,seed:'x'.repeat(200)}).seed===null,'invalid seed rejected');
 const bounded=adapter.restore(recipe,{...saved,states:[{selectedValue:'x'.repeat(1000),order:Array(100).fill('x'),other:'large'},null,null]});
 check(!('selectedValue' in bounded.states[0])&&!('order' in bounded.states[0])&&!('other' in bounded.states[0]),'untrusted pending data bounded');
 const prep=adapter.prepare(recipe,saved,{});check(prep&&typeof prep.then==='function','saved receipt needs async canonical reconstruction');
 const restored=await prep;check(restored.solved,'three correct submitted canonical answers restore');check(fetches===1&&analysesRequested===8,'one catalog and eight real analyses used');check(timers.size===0,'preparation timer disposed');
 check(adapter.prepare(recipe,saved,{})===null,'prepared receipt stays synchronous');
 const forged=clone(saved);forged.states[1].submitted=false;check(!adapter.restore(recipe,forged).solved,'aggregate flag cannot bypass missing submission');
 const unsubmitted=clone(saved);unsubmitted.states[0].attempts=0;check(!adapter.restore(recipe,unsubmitted).solved,'zero attempts cannot restore');
 const partial=adapter.restore(recipe,stateFor(set,1));check(!partial.solved&&partial.currentRound===1,'partial progress kept at first unsolved');
 const skip=clone(saved);skip.states[0].solved=false;skip.currentRound=2;const noSkip=adapter.restore(recipe,skip);check(noSkip.currentRound===0&&!noSkip.states[1].solved&&!noSkip.states[2].solved,'out of order completion discarded');
 let scen=scenario();storage.clear();stack();save(scen,{1:saved,3:stateFor(setFor({...recipe,setId:'alkanes-branched'}))});
 check(NameleculeQuizCheckpoints.resolveTarget(scen,4)===1,'cold navigation cannot trust receipt');
 const p=NameleculeQuizCheckpoints.prepareTarget(scen,4,{});check(p&&typeof p.then==='function','controller returns pending preparation');await p;
 check(NameleculeQuizCheckpoints.resolveTarget(scen,4)===4,'both canonical gates restore destination');check(NameleculeQuizCheckpoints.prepareTarget(scen,4,{})===null,'reentry no duplicate async');
 check(NameleculeQuizCheckpoints.isComplete(scen,1)&&NameleculeQuizCheckpoints.isComplete(scen,3),'both restored gates complete');
 storage.clear();stack();scen=scenario();save(scen,{1:stateFor(set,1),3:stateFor(setFor({...recipe,setId:'alkanes-branched'}))});await NameleculeQuizCheckpoints.prepareTarget(scen,4,{});
 check(NameleculeQuizCheckpoints.resolveTarget(scen,4)===1,'partial first gate clamps');
 check(adapter.prepare({...recipe,setId:'alkanes-branched'},stateFor(setFor({...recipe,setId:'alkanes-branched'})),{})!==null,'later gate was not prepared before incomplete gate');await turns();
 storage.clear();stack();scen=scenario();check(NameleculeQuizCheckpoints.prepareTarget(scen,4,{})===null,'cold untouched lesson stays synchronous');
 storage.clear();stack();scen=scenario();save(scen,{1:saved});const changed=NameleculeQuizCheckpoints.prepareTarget(scen,2,{});NameleculeQuizCheckpoints.reset(scen);let aborted=false;try{await changed}catch(e){aborted=e.name==='AbortError';}check(aborted&&!NameleculeQuizCheckpoints.isComplete(scen,1),'reset prevents stale async overwrite');
 storage.clear();stack();scen=scenario();save(scen,{1:saved});const controller=new AbortController();const stopped=NameleculeQuizCheckpoints.prepareTarget(scen,2,{signal:controller.signal});controller.abort();aborted=false;try{await stopped}catch(e){aborted=e.name==='AbortError';}check(aborted&&!NameleculeQuizCheckpoints.isComplete(scen,1),'aborted preparation cannot unlock');
 storage.clear();stack();scen=scenario();save(scen,{1:saved});const replaced=NameleculeQuizCheckpoints.prepareTarget(scen,2,{});scen.title='replacement';aborted=false;try{await replaced}catch(e){aborted=e.name==='AbortError';}check(aborted,'scenario change cancels stale result');
 // Existing authored round receipts stay synchronous and retain restoration.
 storage.clear();stack();const authoredRound=set.rounds[0],authoredState=saved.states[0];
 const authored={title:'authored',author:'Tester',steps:[{}, {checkpoint:{version:1,id:'authored',type:'name-repair',round:authoredRound}}, {}]};
 save(authored,{1:authoredState});check(NameleculeQuizCheckpoints.prepareTarget(authored,2,{})===null,'authored adapter stays synchronous');check(NameleculeQuizCheckpoints.resolveTarget(authored,2)===2,'authored correct receipt preserved');
 // A claimed catalog revision alone cannot authorize altered bytes.
 stack();digest[0]^=1;let rejected=false;try{await adapter.prepare(recipe,saved,{})}catch(_){rejected=true;}digest[0]^=1;check(rejected,'catalog bytes version mismatch rejected');check(!adapter.restore(recipe,saved).solved,'mismatched catalog cannot unlock');
 // Generated mount is synchronous and owns all late callbacks and resources.
 storage.clear();stack();let roundOptions=null,destroyedRounds=0,publications=[],solvedCalls=0,continueCalls=0;
 global.NameleculeRepairGame.mountRound=(host,options)=>{roundOptions=options;return {destroy(){destroyedRounds++;}};};
 const host=new FakeNode('div');const mounted=adapter.mount(host,{round:recipe,assetBase:'games/',onStateChange:s=>publications.push(s),onSolved:()=>solvedCalls++,onContinue:()=>continueCalls++});
 check(mounted&&typeof mounted.destroy==='function','mount returns immediate disposer');check(publications.length===1&&publications[0].seed==='12345678','seed persists before async work');await turns();check(!!roundOptions,'mount asynchronously reaches first quiz');
 for(let i=0;i<3;i++){
  const round=roundOptions.round,s=stateFor({rounds:[round,round,round]}).states[0];
  roundOptions.onStateChange(s);roundOptions.onSolved({kind:'correct'},s);
  check(solvedCalls===(i===2?1:0),'only third repair publishes gate success');
  check(roundOptions.continueLabel===(i<2?'Επόμενο κουίζ':'Συνεχίζω τη θεωρία'),'internal and final continue labels');
  roundOptions.onContinue();
 }
 check(continueCalls===1&&publications[publications.length-1].solved,'third Continue requests lesson advance');mounted.destroy();check(destroyedRounds===3,'all three round mounts disposed');
 const publicationsBefore=publications.length;roundOptions.onStateChange({solved:false});check(publications.length===publicationsBefore,'destroyed mount ignores late callbacks');
 stack();fetchWait=new Promise(()=>{});let latePublications=0;const closed=adapter.mount(new FakeNode('div'),{round:recipe,onStateChange:()=>latePublications++});closed.destroy();fetchWait=null;await turns();check(latePublications===1,'closed loading mount does not publish late state');
 stack();failFetch=true;const failedHost=new FakeNode('div');const failedMount=adapter.mount(failedHost,{round:recipe});await turns();check(failedHost.attrs['aria-busy']==='false'&&failedHost.children.some(n=>n.tagName==='BUTTON'),'load failure exposes retry');failFetch=false;failedHost.children.find(n=>n.tagName==='BUTTON').handlers.click();await turns();check(failedHost.children.some(n=>n.className==='nl-quiz-set-round'),'retry recovers same mount');failedMount.destroy();
 check(timers.size===0,'all request timers disposed');
 print(JSON.stringify({checks:count,realCoreAnalyses:analyses.length,fetches,analysesRequested,limitations:['Transport, WebCrypto and DOM mocked; real Firefox flow checked separately by root.']}));
}
main().catch(e=>{print('FAIL '+e.message+' '+e.stack);throw e;});
'''
script = HERE/'generated-checkpoint-harness.js'
script.write_text(js)
result = subprocess.run([JSC,str(script.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True)
script.unlink()
print(result.stdout,end='')
print(result.stderr,end='')
if result.returncode or 'FAIL ' in result.stdout: raise SystemExit(result.returncode or 1)
report = json.loads(result.stdout.strip().splitlines()[-1])
(HERE/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
