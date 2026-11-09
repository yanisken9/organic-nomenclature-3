"""Bounded Developer evidence for the generated-quiz header progress contract.

Runs the actual before/current generated adapter, actual checkpoint controller
and actual repair validation/restoration in macOS JavaScriptCore. DOM, round UI,
network/WebCrypto/timers and generator/chemistry delivery are doubles. Generated
rounds are exact fixtures from the earlier pinned-engine verification; this does
not rerun chemical generation or claim browser/layout/accessibility verification.
Writes only memory-results.json; the temporary JSC script uses an ASCII path.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
ADAPTER = 'js/namelecule-generated-repair-checkpoint.js'
CONTROLLER = 'js/namelecule-quiz-checkpoints.js'
ENGINE = 'js/namelecule-game-repair.js'
FIXTURES = 'docs/checks/alkane-quiz-feedback-20261107/memory-fixtures.json'
CATALOG = 'games/data/alkane-structures.json'
STATIC = 'games/data/name-repair-alkanes.json'
SCENARIO = 'scenarios/alkanes-user-3.scenario.json'
baseline = json.loads((HERE / 'baseline.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path in (ADAPTER, CONTROLLER):
    assert sha(HERE / 'before' / path) == baseline['targets'][path], 'Wrong before snapshot: ' + path
for path, digest in baseline['protected'].items():
    assert sha(ROOT / path) == digest, 'Protected source changed: ' + path
fixtures = json.loads((ROOT / FIXTURES).read_text())
static_game = json.loads((ROOT / STATIC).read_text())
fixture_games = {}
for fixture in fixtures:
    game = dict(static_game)
    game['schemaVersion'] = 2
    game['sets'] = [dict(next(item for item in static_game['sets'] if item['id'] == group['id']),
                         rounds=group['rounds']) for group in fixture['sets']]
    fixture_games[fixture['seed']] = game
js = '\n'.join([
    'const beforeAdapter=' + json.dumps((HERE / 'before' / ADAPTER).read_text()) + ';',
    'const currentAdapter=' + json.dumps((ROOT / ADAPTER).read_text()) + ';',
    'const beforeController=' + json.dumps((HERE / 'before' / CONTROLLER).read_text()) + ';',
    'const currentController=' + json.dumps((ROOT / CONTROLLER).read_text()) + ';',
    'const fixtureGames=' + json.dumps(fixture_games) + ';',
    'const catalog=' + (ROOT / CATALOG).read_text() + ';',
    'const actualScenario=' + (ROOT / SCENARIO).read_text() + ';',
    'const global=globalThis;global.window=global;',
    (ROOT / ENGINE).read_text(),
])
js += r'''
let checks=0;
const labels=[];
function check(value,label){if(!value)throw Error(label);checks++;labels.push(label);}
function clone(value){return JSON.parse(JSON.stringify(value));}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label);}
function deferred(){let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return{promise,resolve,reject};}
async function turns(){for(let i=0;i<64;i++)await Promise.resolve();}
const engine=NameleculeRepairEngine;
Math.random=()=>0.5;
Object.values(fixtureGames).forEach(game=>engine.validateGameData(game));
const canonicalJSON=JSON.stringify(fixtureGames);
const recipeBySet=Object.fromEntries(actualScenario.steps.filter(step=>step.checkpoint).map(step=>[step.checkpoint.round.setId,step.checkpoint.round]));
equal(Object.keys(recipeBySet),['alkanes-unbranched','alkanes-branched'],'active scenario has the two approved generated sets');

class FakeNode{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.handlers={};this.parentNode=null;this.className='';this.open=false;this.hidden=false;this.focusCalls=0;this._text='';const names=new Set();this.classList={toggle:(name,on)=>on?names.add(name):names.delete(name),add:name=>names.add(name),remove:name=>names.delete(name),contains:name=>names.has(name)};}
 get isConnected(){return this===body||!!(this.parentNode&&this.parentNode.isConnected);}
 get textContent(){return this._text+this.children.map(child=>child.textContent).join('');}
 set textContent(value){this.replaceChildren();this._text=String(value);}
 append(...items){for(const item of items){if(item.parentNode)item.remove();item.parentNode=this;this.children.push(item);}}
 appendChild(item){this.append(item);return item;}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(item=>item!==this);this.parentNode=null;}}
 replaceChildren(...items){for(const item of this.children)item.parentNode=null;this.children=[];this._text='';this.append(...items);}
 setAttribute(key,value){this.attributes[key]=String(value);}
 removeAttribute(key){delete this.attributes[key];}
 addEventListener(name,handler){(this.handlers[name]||(this.handlers[name]=[])).push(handler);}
 fire(name,extra={}){for(const handler of this.handlers[name]||[])handler({target:this,preventDefault(){},stopPropagation(){},...extra});}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 querySelectorAll(selector){const match=node=>selector[0]==='#'?node.id===selector.slice(1):selector[0]==='.'?node.className.split(/\s+/).includes(selector.slice(1)):selector.split(',').some(tag=>node.tagName===tag.toUpperCase());const found=[];function walk(node){for(const child of node.children){if(match(child))found.push(child);walk(child);}}walk(this);return found;}
 find(id){return this.id===id?this:this.querySelector('#'+id);}
 showModal(){this.open=true;}
 close(){this.open=false;this.fire('close');}
 focus(){this.focusCalls++;}
}
let body;
const rounds=[];
let destroyCalls=0,storageReads=0,storageWrites=0;
let liveScenario=null,navigation=[];
const storage=new Map();
function resetEnvironment(){
 body=new FakeNode('body');rounds.length=0;destroyCalls=0;storageReads=0;storageWrites=0;storage.clear();liveScenario=null;navigation=[];
 global.document={body,baseURI:'http://memory.test/',readyState:'loading',createElement:tag=>new FakeNode(tag),getElementById:id=>body.find(id),querySelectorAll:selector=>body.querySelectorAll(selector)};
 global.sessionStorage={getItem(key){storageReads++;return storage.get(key)||null;},setItem(key,value){storageWrites++;storage.set(key,value);}};
 global.MuLERMoCScenario={present:true};global.fScenarioPresent=()=>liveScenario;
 global.fScenarioPlayUi=()=>{};global.fScenarioGo=index=>navigation.push(index);
 global.NameleculeRepairGame={mountRound(host,options){const handle={destroyed:false,destroy(){if(!this.destroyed){this.destroyed=true;destroyCalls++;}}};rounds.push({host,options,handle});return handle;}};
}
let fetched=0,analysisRequests=0,generationCalls=0;
const timers=new Set();let timerId=0;
global.setTimeout=()=>{timers.add(++timerId);return timerId;};global.clearTimeout=id=>timers.delete(id);
global.URL=class{constructor(path,base){this.href=base+path;}};
global.TextDecoder=class{decode(bytes){return bytes;}};
const digest=Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(value=>parseInt(value,16)));
global.crypto={subtle:{digest:async()=>digest},getRandomValues:values=>{values.fill(1);return values;}};
global.AbortController=class{constructor(){const listeners=new Set();this.signal={aborted:false,addEventListener:(_,fn)=>listeners.add(fn),removeEventListener:(_,fn)=>listeners.delete(fn)};this.abort=()=>{if(!this.signal.aborted){this.signal.aborted=true;[...listeners].forEach(fn=>fn());}};}};
function transport(){
 global.fetch=async()=>{fetched++;return {ok:true,arrayBuffer:async()=>JSON.stringify(catalog)};};
 global.NameleculeChemistryClient={analyze:async molecule=>{analysisRequests++;return {moleculeId:molecule.id};}};
 global.NameleculeRepairGenerator={version:'1.0.0',createGame:(_catalog,_analyses,{seed})=>{generationCalls++;return clone(fixtureGames[seed]||fixtureGames['1']);}};
}
function loadAdapter(source){let adapter=null;global.NameleculeQuizCheckpoints={registerType:(name,value)=>{check(name==='generated-name-repair-set','generated adapter keeps registered type');adapter=value;}};new Function(source)();return adapter;}
function solved(round){const state=engine.createRoundState(round);if(round.kind==='replace'){state.selectedPartId=round.targetPartId;state.selectedValue=round.correctValue;}else{state.selectedPartId=round.correctOrder[0];state.order=round.correctOrder.slice();}state.attempts=1;state.submitted=true;state.solved=true;return state;}
function receipt(seed,set,completed){return {version:1,seed,currentRound:Math.min(completed,2),states:set.rounds.map((round,index)=>index<completed?solved(round):engine.createRoundState(round)),solved:completed===3};}
function wrong(round){const state=engine.createRoundState(round);if(round.kind==='replace'){state.selectedPartId=round.targetPartId;state.selectedValue=round.choices.find(choice=>choice.value!==round.correctValue).value;}else{state.selectedPartId=round.movablePartIds[0];state.order=round.movablePartIds.slice();}state.attempts=1;state.submitted=true;return state;}

async function adapterFlow(source,withProgress,label){
 const evidence=[];
 for(const [setId,recipe] of Object.entries(recipeBySet)){
  resetEnvironment();transport();const adapter=loadAdapter(source),set=fixtureGames['1'].sets.find(item=>item.id===setId);
  equal(Object.keys(adapter).sort(),['mount','prepare','restore','validate'],'adapter exported API unchanged '+label+' '+setId);
  const host=new FakeNode('div'),states=[],progress=[];let solvedCalls=0,continueCalls=0;
  const initial=receipt('1',set,0),options={round:recipe,initialState:initial,onStateChange:state=>states.push(clone(state)),onSolved:()=>solvedCalls++,onContinue:()=>continueCalls++};
  if(withProgress)options.onProgress=value=>progress.push(clone(value));
  const handle=adapter.mount(host,options);
  if(withProgress)equal(progress,[null],'generated loading clears header immediately '+setId);
  await turns();
  for(let index=0;index<3;index++){
   check(rounds.length===index+1,'exact actual current round mounted '+label+' '+setId+' '+index);
   const mounted=rounds[index],callbackCount=progress.length;
   equal(mounted.options.round.id,set.rounds[index].id,'mount receives canonical fixture round '+label+' '+setId+' '+index);
   if(withProgress){equal(progress.at(-1),{current:index+1,total:recipe.roundCount},'progress follows rendered current round '+setId+' '+index);check(progress.every(item=>item===null||Object.keys(item).join(',')==='current,total'),'progress payload contains only actual current/total '+setId+' '+index);check(host.children[0].textContent===set.title&&host.children[0].attributes.role===undefined,'header mode keeps plain set title without duplicate counter live region '+setId+' '+index);}
   else check(host.children[0].textContent==='Κουίζ '+(index+1)+' από 3 · '+set.title&&host.children[0].attributes.role==='status','no-callback fallback counter/live region preserved '+label+' '+setId+' '+index);
   const wrongState=wrong(set.rounds[index]);check(engine.evaluateRepair(set.rounds[index],wrongState).kind!=='correct','wrong Check fixture rejected '+setId+' '+index);
   mounted.options.onStateChange(wrongState);mounted.options.onContinue();
   check(rounds.length===index+1&&continueCalls===0,'wrong Check cannot advance current round '+label+' '+setId+' '+index);
   const answer=solved(set.rounds[index]);check(engine.evaluateRepair(set.rounds[index],answer).kind==='correct','correct Check fixture accepted '+setId+' '+index);
   mounted.options.onStateChange(answer);mounted.options.onSolved({kind:'correct'},answer);
   check(rounds.length===index+1,'correct Check alone keeps displayed current round '+label+' '+setId+' '+index);
   if(withProgress)check(progress.length===callbackCount,'selection/wrong/correct Check never moves progress '+setId+' '+index);
   check(solvedCalls===(index===2?1:0),'completion gate requires three verified repairs '+label+' '+setId+' '+index);
   mounted.options.onContinue();
  }
  check(continueCalls===1&&states.at(-1).solved,'only final Continue advances theory '+label+' '+setId);
  const finalState=clone(states.at(-1));handle.destroy();check(destroyCalls===3,'all three shared round mounts destroyed '+label+' '+setId);
  if(withProgress)equal(progress.filter(Boolean),[{current:1,total:3},{current:2,total:3},{current:3,total:3}],'only Continue changes 1→2→3 '+setId);
  if(withProgress)check(progress.at(-1)===null,'destroy clears header '+setId);
  evidence.push({setId,states,finalState,solvedCalls,continueCalls});
 }
 return evidence;
}

async function restoration(source,label){
 const result=[];
 for(const [setId,recipe] of Object.entries(recipeBySet)){
  resetEnvironment();transport();const adapter=loadAdapter(source),set=fixtureGames['1'].sets.find(item=>item.id===setId),complete=receipt('1',set,3);
  const forged=receipt('1',set,0);forged.solved=true;forged.states.forEach(state=>{state.solved=true;state.submitted=true;state.attempts=1;});
  check(!adapter.restore(recipe,complete).solved,'cold stored completion fails closed '+label+' '+setId);
  await adapter.prepare(recipe,complete,{});
  const cases={fresh:receipt('1',set,0),partial:receipt('1',set,1),complete,forged,unsubmitted:clone(complete)};cases.unsubmitted.states[0].submitted=false;
  const restored=Object.fromEntries(Object.entries(cases).map(([name,state])=>[name,adapter.restore(recipe,state)]));
  check(restored.partial.currentRound===1&&!restored.partial.solved,'valid partial resumes at second quiz '+label+' '+setId);
  check(restored.complete.solved&&!restored.forged.solved&&!restored.unsubmitted.solved,'completion still requires actual legal submitted answers '+label+' '+setId);
  const progress=[],host=new FakeNode('div');const handle=adapter.mount(host,{round:recipe,initialState:cases.partial,onProgress:value=>progress.push(clone(value))});await turns();
  equal(rounds.at(-1).options.round.id,set.rounds[1].id,'restored mount displays second actual quiz '+label+' '+setId);
  if(label==='after')equal(progress.at(-1),{current:2,total:3},'restored initial header is 2/3 '+setId);
  handle.destroy();result.push({setId,restored});
 }
 return result;
}

async function adapterFailures(){
 resetEnvironment();transport();let fail=true;global.fetch=async()=>{fetched++;if(fail)throw Error('deliberate transport failure');return {ok:true,arrayBuffer:async()=>JSON.stringify(catalog)};};
 const adapter=loadAdapter(currentAdapter),host=new FakeNode('div'),progress=[];
 const handle=adapter.mount(host,{round:recipeBySet['alkanes-unbranched'],initialState:{version:1,seed:'1'},onProgress:value=>progress.push(clone(value))});
 await turns();check(host.children[0].className==='nl-quiz-error'&&progress.every(value=>value===null),'adapter transport error never publishes a current quiz');
 fail=false;host.children[1].fire('click');check(progress.at(-1)===null,'adapter retry clears header during loading');await turns();equal(progress.at(-1),{current:1,total:3},'adapter retry publishes only rendered current quiz');handle.destroy();check(progress.at(-1)===null,'adapter retry destroy clears header');
 resetEnvironment();transport();const pending=deferred();global.fetch=()=>pending.promise;const pendingAdapter=loadAdapter(currentAdapter),pendingProgress=[],pendingHost=new FakeNode('div');
 const pendingHandle=pendingAdapter.mount(pendingHost,{round:recipeBySet['alkanes-branched'],initialState:{version:1,seed:'1'},onProgress:value=>pendingProgress.push(clone(value))});
 pendingHandle.destroy();const count=pendingProgress.length;pending.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await turns();
 check(pendingProgress.length===count&&pendingProgress.at(-1)===null&&!pendingHost.children.length&&!rounds.length,'unmounted pending response cannot publish stale progress or render');
}

function loadController(source){new Function(source)();return global.NameleculeQuizCheckpoints;}
function open(api,scenario,index){liveScenario=scenario;scenario.index=index;global.MuLERMoCScenario.present=true;api.onStep(scenario,index);body.find('nlQuizOpen').fire('click');check(body.find('nlQuizDialog').open,'actual controller opens modal');return body.find('nlQuizProgress');}
function progressVisible(){const slot=body.find('nlQuizProgress');return !!slot&&!slot.hidden&&slot.textContent!=='';}
function progressText(){return body.find('nlQuizProgress').textContent.replace(/\s+/g,'');}

async function controllerIntegration(source,label){
 resetEnvironment();transport();const api=loadController(source);new Function(label==='before'?beforeAdapter:currentAdapter)();
 const scenario=clone(actualScenario),authored=JSON.stringify(scenario),first=3,second=10;
 open(api,scenario,first);if(label==='after')check(!progressVisible(),'controller loading starts hidden');await turns();
 const header=body.find('nlQuizProgress');if(label==='after'){check(header.attributes.role==='status','stable header slot is a status live region');check(header.parentNode===body.find('nlQuizBack').parentNode,'progress shares right group with Back');check(header.parentNode.parentNode===body.find('nlQuizDialogTitle').parentNode,'right group belongs to stable header');check(progressText()==='Κουίζ1/3','controller receives actual adapter round1 progress');}
 check(api.resolveTarget(scenario,11)===first,'normal first mandatory gate still blocks forward request');
 for(let index=0;index<3;index++){
  const mounted=rounds.at(-1),answer=solved(mounted.options.round);mounted.options.onStateChange(answer);mounted.options.onSolved({kind:'correct'},answer);
  if(label==='after')check(progressText()==='Κουίζ'+(index+1)+'/3','Check leaves controller header on displayed round '+index);
  check(api.isComplete(scenario,first)===(index===2),'actual controller first gate requires all three answers '+label+' '+index);
  if(index<2)mounted.options.onContinue();
 }
 check(api.resolveTarget(scenario,11)===second,'first completion leaves normal second mandatory gate');
 const completedBytes=JSON.stringify([...storage]);
 body.find('nlQuizBack').fire('click');if(label==='after')check(!progressVisible(),'Back clears header');
 const beforeReopen=storageWrites;open(api,scenario,first);await turns();if(label==='after')check(progressText()==='Κουίζ3/3','complete reopen reports actual restored final displayed round');
 check(api.isComplete(scenario,first),'reopen preserves valid completed receipt');
 rounds.at(-1).options.onContinue();check(navigation.at(-1)===4&&!body.find('nlQuizDialog').open,'final actual Continue closes modal and navigates theory');if(label==='after')check(!progressVisible(),'final Continue clears header');
 open(api,scenario,second);await turns();if(label==='after')check(progressText()==='Κουίζ1/3','new second set does not inherit previous final counter');
 check(!api.isComplete(scenario,second)&&api.resolveTarget(scenario,11)===second,'opening second set does not bypass second gate');
 const signatureState=clone(scenario);delete signatureState.index;
 const persisted=[...storage].map(([key,value])=>[key,JSON.parse(value)]);
 api.onExit();if(label==='after')check(!progressVisible(),'onExit clears header');
 equal(JSON.stringify({...scenario,index:actualScenario.index}),authored,'controller does not mutate authored scenario/export data');
 equal(Object.keys(api).sort(),['registerType','validateCheckpoint','hasCheckpoints','resolveTarget','prepareTarget','isComplete','onStep','onExit','reset','beginPreview','endPreview','isPreview'].sort(),'controller public API unchanged '+label);
 return {persisted,navigation,completedBytes,beforeReopen,storageWrites};
}

async function controllerGuards(){
 resetEnvironment();transport();const api=loadController(currentController),captures=[];let failMount=false;
 api.registerType('memory-progress',{validate:round=>round,restore:(_,state)=>state||{solved:false},mount:(_,options)=>{captures.push(options);if(failMount){options.onProgress({current:1,total:3});throw Error('deliberate mount failure');}return {destroy(){options.onProgress({current:9,total:9});}};}});
 const spec={id:'memory-header',type:'memory-progress',version:1,round:{test:true}};
 const scenario={title:'progress guard probes',author:'Developer test',steps:[{checkpoint:spec},{selectedMol:'ethane'}],index:0};
 let header=open(api,scenario,0),options=captures.at(-1);
 check(!progressVisible(),'new non-reporting mount starts with hidden header');options.onProgress({current:1,total:3});check(progressText()==='Κουίζ1/3','safe progress displayed');
 const invalid=[undefined,null,{},[],{current:0,total:3},{current:4,total:3},{current:1.5,total:3},{current:'1',total:3},{current:1,total:0},{current:1,total:2.5},{current:1,total:'3'},{current:NaN,total:3},{current:1,total:Infinity},{current:1,total:Number.MAX_SAFE_INTEGER+1}];
 for(let index=0;index<invalid.length;index++){options.onProgress(invalid[index]);check(!progressVisible(),'invalid/unavailable payload clears counter '+index);options.onProgress({current:2,total:3});check(progressText()==='Κουίζ2/3','valid payload restores counter after invalid '+index);}
 const stored=JSON.stringify([...storage]),reads=storageReads,writes=storageWrites;
 options.onProgress({current:3,total:3});check(storageReads===reads&&storageWrites===writes&&JSON.stringify([...storage])===stored,'progress callbacks do not read/write/mutate learner receipt');
 body.find('nlQuizBack').fire('click');check(!progressVisible(),'synchronous destroy callback cannot restore cleared closed counter');options.onProgress({current:1,total:3});check(!progressVisible(),'old callback after close ignored by token');
 open(api,scenario,0);const next=captures.at(-1);next.onProgress({current:2,total:3});options.onProgress({current:3,total:3});check(progressText()==='Κουίζ2/3','old mount callback cannot replace current mount counter');
 scenario.index=1;next.onProgress({current:3,total:3});check(progressText()==='Κουίζ2/3','index-mismatched callback ignored by currentContext');scenario.index=0;
 liveScenario={...scenario};next.onProgress({current:3,total:3});check(progressText()==='Κουίζ2/3','scenario identity mismatch ignores progress');liveScenario=scenario;
 global.MuLERMoCScenario.present=false;next.onProgress({current:3,total:3});check(progressText()==='Κουίζ2/3','inactive presentation ignores progress');global.MuLERMoCScenario.present=true;
 scenario.title='edited during open';next.onProgress({current:3,total:3});check(progressText()==='Κουίζ2/3','changed authored content ignores stale progress');scenario.title='progress guard probes';
 body.find('nlQuizDialog').close();check(!progressVisible(),'native close clears counter');
 failMount=true;open(api,scenario,0);check(!progressVisible()&&body.find('nlQuizRetry').hidden===false,'synchronous mount error clears a previously reported counter');
 failMount=false;body.find('nlQuizRetry').fire('click');check(!progressVisible(),'controller retry loading clears error counter');captures.at(-1).onProgress({current:1,total:3});check(progressText()==='Κουίζ1/3','retried controller accepts current progress');
 api.reset(scenario);check(!progressVisible(),'reset clears counter');
 open(api,scenario,0);captures.at(-1).onProgress({current:2,total:3});
 const legacy={title:'legacy single question',author:'Developer test',steps:[{checkpoint:{id:'legacy-test',type:'name-repair',version:1,round:clone(fixtureGames['1'].sets[0].rounds[0])}}],index:0};
 open(api,legacy,0);check(!progressVisible(),'legacy single repair after generated progress keeps header hidden');
 const legacyOptions=rounds.at(-1).options,answer=solved(legacyOptions.round);legacyOptions.onStateChange(answer);legacyOptions.onSolved({kind:'correct'},answer);check(api.isComplete(legacy,0),'legacy solution still completes normally');legacyOptions.onContinue();check(!progressVisible()&&navigation.at(-1)===1,'legacy Continue works with hidden progress');
 api.beginPreview(scenario);open(api,scenario,0);captures.at(-1).onProgress({current:1,total:3});check(progressText()==='Κουίζ1/3','author preview can display same generic progress contract');api.endPreview();check(!progressVisible(),'ending preview clears progress');
}

async function main(){
 const oldFlow=await adapterFlow(beforeAdapter,false,'before'),fallback=await adapterFlow(currentAdapter,false,'after-fallback'),header=await adapterFlow(currentAdapter,true,'after-header');
 equal(fallback,oldFlow,'no-callback adapter state/receipt/solutions/Continue identical before/current');equal(header,oldFlow,'header callbacks do not change adapter state/receipt/solutions/Continue');
 const oldRestore=await restoration(beforeAdapter,'before'),newRestore=await restoration(currentAdapter,'after');equal(newRestore,oldRestore,'fresh/partial/complete/forged/unsubmitted receipts restore identically');
 await adapterFailures();
 const oldController=await controllerIntegration(beforeController,'before'),newController=await controllerIntegration(currentController,'after');equal(newController,oldController,'header integration preserves exact controller persisted receipt bytes, gate behavior and navigation');
 await controllerGuards();
 check(JSON.stringify(fixtureGames)===canonicalJSON,'canonical generated fixture questions remain byte-identical');check(timers.size===0,'all preparation timers cleaned');
 print(JSON.stringify({status:'passed',kind:'Developer verification, not independent review',checks,labels,fixtureSeeds:Object.keys(fixtureGames),actualSetFlows:['alkanes-unbranched','alkanes-branched'],fetched,analysisRequests,generationCalls,invariants:['Actual before/current adapter public API and actual controller public API unchanged','Callback progress is actual displayed round and changes 1→2→3 only on Continue','Correct and wrong Check, verified three-repair gate, partial restore2/3, complete reopen3/3 and both mandatory lesson gates retained','Before/current adapter state publications/restoration and exact controller persisted receipt bytes/navigation equal','Fallback counter and status live region retained without callback; header mode keeps plain set title','Loading, network error, adapter retry, destroy, pending unmount, controller error/retry, reset/close/Exit/preview end and legacy transition clear header','Invalid safe-integer/range values are cleared; token/currentContext reject stale callbacks','Progress reports do not access/mutate stored receipts or authored scenario/export data','Actual source round validation/restoration/evaluation run on preserved generated fixtures'],limitations:['JavaScriptCore and Fake DOM: no visual/sticky/mobile/scroll/focus/screen-reader or real browser claims','Shared round UI mounting is mocked; callback actions use actual repair validation/evaluation/restoration; Firefox exercises UI separately','Network transport, WebCrypto, timers, chemistry analyses and generator delivery are mocked; no new chemical generation claims','Fixtures are earlier exact pinned-engine seeds1/4; behavioral flows use seed1 including both replacement and actual order repair','Custom test adapter supplies malformed/stale progress and synchronous destroy/error probes; production code is evaluated unmodified','Authored scenario invariance and protected source hashes cover export contract; no browser download/export performed'] }));
}
main().catch(error=>{print('FAIL '+error.message+'\n'+error.stack);throw error;});
'''
with tempfile.TemporaryDirectory(prefix='quiz-progress-memory-', dir='/private/tmp') as temp:
    script = Path(temp) / 'harness.js'
    script.write_text(js)
    result = subprocess.run([JSC, str(script)], cwd=ROOT, capture_output=True, text=True)
if result.returncode or 'FAIL ' in result.stdout or not result.stdout.strip():
    print(result.stdout, end='')
    print(result.stderr, end='')
    raise SystemExit(result.returncode or 1)
report = json.loads(result.stdout.strip().splitlines()[-1])
report['sourceSHA256'] = {path: sha(ROOT / path) for path in (ADAPTER, CONTROLLER, ENGINE, CATALOG, STATIC, SCENARIO)}
report['beforeSHA256'] = {path: sha(HERE / 'before' / path) for path in (ADAPTER, CONTROLLER)}
report['fixtureSource'] = FIXTURES
report['fixtureSHA256'] = sha(ROOT / FIXTURES)
report['harnessSHA256'] = sha(Path(__file__))
report['protectedSHA256Checks'] = len(baseline['protected'])
report['command'] = 'python3 docs/checks/quiz-header-progress-20261108/check-memory.py'
(HERE / 'memory-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('status', 'checks', 'fixtureSeeds', 'actualSetFlows', 'protectedSHA256Checks')}, ensure_ascii=False))
