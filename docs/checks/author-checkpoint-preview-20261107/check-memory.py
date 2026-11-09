"""Bounded Developer evidence for transient editor preview and learner isolation.

Uses actual before/current checkpoint controllers, actual repair validation and
restoration, static authored round fixtures, and extracted actual player functions.
DOM, shared round mounting, storage transport and viewer application are doubles.
No browser behavior is claimed. Private hooks exist only in evaluated strings.
Writes memory-results.json; transient JSC script lives in an ASCII /tmp path.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
CONTROLLER = 'js/namelecule-quiz-checkpoints.js'
PLAYER = 'js/mulermoc-nom-scenario-54.js'
ENGINE = 'js/namelecule-game-repair.js'
STATIC = 'games/data/name-repair-alkanes.json'
PILOT = 'scenarios/alkanes-name-repair-pilot.scenario.json'
baseline = json.loads((HERE / 'baseline.json').read_text())
before_controller = (HERE / 'before' / CONTROLLER).read_text()
current_controller = (ROOT / CONTROLLER).read_text()
before_player = (HERE / 'before' / PLAYER).read_text()
current_player = (ROOT / PLAYER).read_text()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_source(source, name):
    """Read one actual top-level function through the next top-level declaration.

    Trailing comments are allowed. No implementation is copied into the test.
    The source module uses top-level declarations on their own lines.
    """
    start = re.search(r'^([ \t]*)function ' + re.escape(name) + r'\(', source, re.M)
    assert start, 'Missing actual function: ' + name
    following = re.search(r'^' + re.escape(start.group(1)) + r'function \w+\(', source[start.end():], re.M)
    stop = start.end() + following.start() if following else len(source)
    return source[start.start():stop]


for path in (CONTROLLER, PLAYER):
    assert sha(HERE / 'before' / path) == baseline['targets'][path], 'Wrong before snapshot: ' + path
for path, digest in baseline['protected'].items():
    assert sha(ROOT / path) == digest, 'Protected source changed: ' + path
assert function_source(current_controller, 'signature') == function_source(before_controller, 'signature'), 'Learner content signature changed'
assert function_source(current_player, 'fScenarioExport') == function_source(before_player, 'fScenarioExport'), 'Scenario export implementation changed'

catalog = json.loads((ROOT / STATIC).read_text())
pilot = json.loads((ROOT / PILOT).read_text())
pilot_spec = next(step['checkpoint'] for step in pilot['steps'] if 'checkpoint' in step)
order_round = next(round for group in catalog['sets'] for round in group['rounds'] if round['kind'] == 'order')
functions = [
    'fScenarioHasCheckpoints', 'fScenarioCheckpointApi', 'fScenarioIsAuthorPreview',
    'fScenarioEndAuthorPreview', 'fScenarioResolveCheckpointTarget', 'fScenarioCheckpointError',
    'fScenarioPrepareCheckpointTarget', 'fScenarioAuthorPreviewBegin', 'fScenarioPresentBegin',
]
player_functions = '\n'.join(function_source(current_player, name) for name in functions)
js = '\n'.join([
    'const beforeSource=' + json.dumps(before_controller) + ';',
    'const currentSource=' + json.dumps(current_controller) + ';',
    'const playerSource=' + json.dumps(player_functions) + ';',
    'const functionNames=' + json.dumps(functions) + ';',
    'const pilotSpec=' + json.dumps(pilot_spec) + ';',
    'const orderRound=' + json.dumps(order_round) + ';',
    'const global=globalThis;global.window=global;',
    (ROOT / ENGINE).read_text(),
])
js += r'''
let checks=0;
const labels=[];
function check(value,label){if(!value)throw Error(label);checks++;labels.push(label);}
function clone(value){return JSON.parse(JSON.stringify(value));}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label);}
const engine=NameleculeRepairEngine;
Math.random=()=>0.5;
const fixtureJSON=JSON.stringify([pilotSpec,orderRound]);
engine.validateRoundData(pilotSpec.round);engine.validateRoundData(orderRound);
function solved(round){
 const state=engine.createRoundState(round);
 if(round.kind==='replace'){state.selectedPartId=round.targetPartId;state.selectedValue=round.correctValue;}
 else {state.order=round.correctOrder.slice();state.selectedPartId=round.correctOrder[0];}
 state.attempts=1;state.submitted=true;state.solved=true;
 check(engine.evaluateRepair(round,state).kind==='correct','fixture answer independently accepted '+round.id);
 check(engine.restoreRoundState(round,state).solved,'actual engine restores legal solved fixture '+round.id);
 return state;
}
const replacementSolved=solved(pilotSpec.round),orderSolved=solved(orderRound);
function lesson(title){return {id:title,title,author:'Developer memory test',index:0,steps:[
 {selectedMol:'methane'},
 {selectedMol:'methyl_2_pentane',checkpoint:clone(pilotSpec)},
 {selectedMol:'ethane'},
 {selectedMol:'ethane',checkpoint:{id:'memory-order',type:'name-repair',version:1,round:clone(orderRound)}},
 {selectedMol:'propane'}]};}

class FakeNode{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.handlers={};this.parentNode=null;this.className='';this.open=false;this.focusCalls=0;this.classList={toggle:()=>{},add:()=>{},remove:()=>{}};}
 get isConnected(){return this===body||!!(this.parentNode&&this.parentNode.isConnected);}
 append(...items){for(const item of items){if(item.parentNode)item.remove();item.parentNode=this;this.children.push(item);}}
 appendChild(item){this.append(item);return item;}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(x=>x!==this);this.parentNode=null;}}
 replaceChildren(...items){for(const item of this.children)item.parentNode=null;this.children=[];this.append(...items);}
 setAttribute(key,value){this.attributes[key]=String(value);}
 addEventListener(name,handler){(this.handlers[name]||(this.handlers[name]=[])).push(handler);}
 fire(name){for(const handler of this.handlers[name]||[])handler({target:this,preventDefault(){},stopPropagation(){}});}
 querySelector(selector){if(selector[0]==='#')return this.find(selector.slice(1));return null;}
 find(id){if(this.id===id)return this;for(const child of this.children){const found=child.find(id);if(found)return found;}return null;}
 showModal(){this.open=true;}
 close(){this.open=false;this.fire('close');}
 focus(){this.focusCalls++;}
}
const body=new FakeNode('body');
global.document={body,readyState:'loading',createElement:tag=>new FakeNode(tag),getElementById:id=>body.find(id),querySelectorAll:()=>[]};
let storageReads=0,storageWrites=0;
const storage=new Map();
global.sessionStorage={getItem(key){storageReads++;return storage.get(key)||null;},setItem(key,value){storageWrites++;storage.set(key,value);}};
let liveScenario=null,navigationCalls=[],uiCalls=0,destroyCalls=0;
const mounts=[];
global.MuLERMoCScenario={present:true};
global.fScenarioPresent=()=>liveScenario;
global.fScenarioPlayUi=()=>{uiCalls++;};
global.fScenarioGo=index=>navigationCalls.push(index);
global.NameleculeRepairGame={mountRound(host,options){const handle={destroyed:false,destroy(){this.destroyed=true;destroyCalls++;}};mounts.push({host,options,handle});return handle;}};
function loadController(source,inspect){
 delete global.__memoryControllerPrivate;
 if(inspect){
  const marker='  global.NameleculeQuizCheckpoints = {';
  check(source.split(marker).length===2,'one private hook insertion point');
  source=source.replace(marker,'  global.__memoryControllerPrivate={recordFor,persist,signature,hash,getActive:()=>active};\n'.replace(/\\n/g,'\n')+marker);
 }
 new Function(source)();
 return {api:global.NameleculeQuizCheckpoints,priv:global.__memoryControllerPrivate};
}
// The untouched production controller is evaluated before instrumented instances.
loadController(currentSource,false);
check(!('__memoryControllerPrivate'in global),'untouched controller exports no inspection hook');
const prior=loadController(beforeSource,true);
const current=loadController(currentSource,true),api=current.api,priv=current.priv;
const expectedOld=['registerType','validateCheckpoint','hasCheckpoints','resolveTarget','prepareTarget','isComplete','onStep','onExit','reset'];
equal(Object.keys(prior.api).sort(),expectedOld.slice().sort(),'before API recorded');
equal(Object.keys(api).sort(),expectedOld.concat(['beginPreview','endPreview','isPreview']).sort(),'only three explicit preview methods added');
const scenario=lesson('cached-learner');
const content=priv.signature(scenario),key='namelecule:lesson-checkpoints:v1:'+priv.hash(content);
equal(content,prior.priv.signature(scenario),'before/current actual content signatures identical');
equal(prior.api.resolveTarget(lesson('baseline-no-receipt'),4),1,'before source reproduces first unsolved gate');
storage.set(key,JSON.stringify({version:1,content,states:{1:replacementSolved}}));
check(api.isComplete(scenario,1),'normal learner restores populated valid receipt');
check(!api.isComplete(scenario,3),'normal second checkpoint remains incomplete');
check(api.resolveTarget(scenario,4)===3,'normal populated learner stops at second gate');
const learner=priv.recordFor(scenario),learnerBefore=JSON.stringify(learner),storageBefore=JSON.stringify([...storage]);
const readsBefore=storageReads,writesBefore=storageWrites;
api.beginPreview(scenario);
check(api.isPreview(scenario),'explicit begin establishes exact scenario preview');
check(!api.isPreview(clone(scenario)),'same-content distinct object cannot borrow preview');
const temporary=priv.recordFor(scenario);
check(temporary!==learner&&temporary.temporary===true&&temporary.key===null,'temporary record is separate from learner cache and has no storage key');
check(!api.isComplete(scenario,1)&&!api.isComplete(scenario,3),'preview starts fresh despite valid learner solution');
check(api.resolveTarget(scenario,4)===1,'controller gate semantics still use temporary completion');
check(storageReads===readsBefore&&storageWrites===writesBefore,'preview creation/completion checks never access tab storage');

function openCheckpoint(scen,index){liveScenario=scen;scen.index=index;global.MuLERMoCScenario.present=true;api.onStep(scen,index);const section=body.find('nlQuizCheckpoint');check(!!section,'checkpoint surface inserted');body.find('nlQuizOpen').fire('click');check(body.find('nlQuizDialog').open,'native modal contract opened');return mounts[mounts.length-1];}
let mounted=openCheckpoint(scenario,1);
check(mounted.options.initialState===null,'preview mount receives no learner answer');
mounted.options.onSolved({kind:'correct'},{...replacementSolved,solved:true,submitted:false});
check(!api.isComplete(scenario,1),'forged/unsubmitted solved state cannot unlock preview');
mounted.options.onStateChange(replacementSolved);mounted.options.onSolved({kind:'correct'},replacementSolved);
check(api.isComplete(scenario,1),'actual legal replacement completion recorded temporarily');
mounted.options.onContinue();
equal(navigationCalls,[2],'completed preview repair Continue delegates one next step');
const staleAfterContinue=mounted.options;
const second=openCheckpoint(scenario,3);
second.options.onStateChange(orderSolved);second.options.onSolved({kind:'correct'},orderSolved);
check(api.isComplete(scenario,3)&&api.resolveTarget(scenario,4)===4,'actual order repair completion recorded in same preview');
check(storageReads===readsBefore&&storageWrites===writesBefore,'solve/Continue/order flow performs no storage reads or writes');
equal(JSON.stringify(learner),learnerBefore,'temporary repair completion does not mutate populated learner cache');
equal(JSON.stringify([...storage]),storageBefore,'temporary repair completion does not mutate stored receipt bytes');
staleAfterContinue.onStateChange(engine.createRoundState(pilotSpec.round));
check(api.isComplete(scenario,1),'destroyed earlier mount callback cannot overwrite temporary solution');
api.reset(scenario);
check(!api.isComplete(scenario,1)&&!api.isComplete(scenario,3),'reset clears only current temporary progress');
check(!body.find('nlQuizDialog').open&&second.handle.destroyed,'reset closes and destroys preview repair mount');
check(storageReads===readsBefore&&storageWrites===writesBefore,'preview reset does not touch tab storage');
equal(JSON.stringify(learner),learnerBefore,'preview reset preserves existing learner cache');
mounted=openCheckpoint(scenario,1);
mounted.options.onStateChange(replacementSolved);
check(api.isComplete(scenario,1),'temporary replay can solve again after reset');
const endedRecord=priv.recordFor(scenario),endedStates=JSON.stringify(endedRecord.states),staleEnded=mounted.options;
const destroysBefore=destroyCalls;
api.endPreview();
check(!api.isPreview(scenario),'end clears preview identity');
check(!body.find('nlQuizCheckpoint')&&!body.find('nlQuizDialog').open&&mounted.handle.destroyed&&destroyCalls===destroysBefore+1,'end removes active surface and destroys mount');
check(priv.recordFor(scenario)===learner&&api.isComplete(scenario,1)&&!api.isComplete(scenario,3),'end restores exact cached learner state');
staleEnded.onStateChange(orderSolved);staleEnded.onSolved({kind:'correct'},replacementSolved);staleEnded.onContinue();
equal(JSON.stringify(endedRecord.states),endedStates,'late callbacks cannot mutate discarded preview record');
equal(navigationCalls,[2],'late Continue cannot navigate after end');
equal(JSON.stringify(learner),learnerBefore,'late callbacks preserve learner cache');
equal(JSON.stringify([...storage]),storageBefore,'late callbacks preserve stored receipt bytes');
api.beginPreview(scenario);
check(!api.isComplete(scenario,1)&&priv.recordFor(scenario)!==endedRecord,'reopening same scenario gets new empty temporary record');
mounted=openCheckpoint(scenario,1);
mounted.options.onStateChange(replacementSolved);
const oldPreview=priv.recordFor(scenario),oldPreviewJSON=JSON.stringify(oldPreview.states),oldOptions=mounted.options;
api.beginPreview(scenario);
check(mounted.handle.destroyed&&!api.isComplete(scenario,1),'begin again disposes active mount and resets preview');
oldOptions.onStateChange(engine.createRoundState(pilotSpec.round));oldOptions.onContinue();
equal(JSON.stringify(oldPreview.states),oldPreviewJSON,'superseded begin callbacks cannot mutate previous record');
const signatureBefore=priv.signature(scenario);
scenario.steps[0].selectedMol='ethane';
check(!api.isPreview(scenario),'authored content change invalidates preview match');
scenario.steps[0].selectedMol='methane';
equal(priv.signature(scenario),signatureBefore,'scenario content restored for remaining checks');
api.endPreview();
const uncached=lesson('uncached-learner');
const uncachedContent=priv.signature(uncached),uncachedKey='namelecule:lesson-checkpoints:v1:'+priv.hash(uncachedContent);
storage.set(uncachedKey,JSON.stringify({version:1,content:uncachedContent,states:{1:replacementSolved,3:orderSolved}}));
const uncachedReads=storageReads,uncachedWrites=storageWrites,uncachedBytes=storage.get(uncachedKey);
api.beginPreview(uncached);
check(!api.isComplete(uncached,1)&&!api.isComplete(uncached,3),'uncached stored learner receipts are never loaded into preview');
check(storageReads===uncachedReads&&storageWrites===uncachedWrites,'uncached preview never reads or writes existing receipt');
api.endPreview();
check(api.resolveTarget(uncached,4)===4&&storageReads===uncachedReads+1,'ordinary mode reads and restores same stored receipt after preview');
check(storage.get(uncachedKey)===uncachedBytes,'uncached learner receipt bytes preserved');
// Normal reset continues to persist real progress after preview has ended.
api.reset(uncached);
check(storageWrites===uncachedWrites+1&&!api.isComplete(uncached,1),'normal learner reset still writes real receipt');

// Run extracted actual policy and author wrapper functions, replacing only
// DOM/viewer surroundings. This does not exercise the complete player UI.
global.MuLERMoCScenario={present:false,presentId:null,authoring:true,pinned:false,checkpointPreparation:null};
const cards=new Map([[scenario.id,scenario]]);
let applyCalls=0,applySucceeds=true,errors=[],activeCard=scenario,cancelCalls=0,restoreCalls=0;
global.fScenarioGet=id=>cards.get(id)||null;
global.fScenarioActive=()=>activeCard;
global.fScenarioSetActive=id=>{activeCard=cards.get(id);};
global.fScenarioCancelCheckpointPreparation=()=>{cancelCalls++;};
global.fScenarioCheckpointContent=scen=>priv.signature(scen);
global.fScenarioSyncLegacy=()=>{};
global.fScenarioStashAuthorSettings=()=>{};
global.fScenarioRestoreAuthorSettings=()=>{restoreCalls++;};
global.fScenarioSyncPresentClass=()=>{};
global.fScenarioRenderPresentMenu=()=>{};
global.fScenarioApply=()=>{applyCalls++;return applySucceeds;};
global.fScenarioToast=message=>errors.push(message);
global.location={pathname:'/memory.html',hash:''};
global.history={replaceState(a,b,path){location.hash=path[0]==='#'?path:'';}};
global.AbortController=class{constructor(){this.signal={aborted:false};}abort(){this.signal.aborted=true;}};
new Function(playerSource+'\nglobalThis.__memoryPlayer={'+functionNames.join(',')+'};')();
const player=global.__memoryPlayer;
const fresh=lesson('fresh-player');cards.set(fresh.id,fresh);activeCard=fresh;
check(player.fScenarioResolveCheckpointTarget(fresh,4)===1,'actual player normal target helper retains first gate');
player.fScenarioAuthorPreviewBegin(fresh.id,4);
check(api.isPreview(fresh)&&MuLERMoCScenario.present&&fresh.index===4&&location.hash==='#step=5','actual editor wrapper launches selected later step');
check(player.fScenarioResolveCheckpointTarget(fresh,4)===4,'actual player target helper bypasses earlier temporary gates');
check(player.fScenarioPrepareCheckpointTarget(fresh,4,()=>{throw Error('preview resumed learner preparation');})===false,'actual preview prepare helper skips learner restoration');
const playerPreview=priv.recordFor(fresh),playerPreviewState=JSON.stringify(playerPreview.states);
check(!api.isComplete(fresh,1)&&JSON.stringify(playerPreview.states)===playerPreviewState,'bypass does not forge temporary solved receipts');
const appliesBeforeGuard=applyCalls;
player.fScenarioAuthorPreviewBegin(fresh.id,0);
check(fresh.index===4&&applyCalls===appliesBeforeGuard,'wrapper cannot reinitialize preview from presentation');
player.fScenarioPresentBegin(fresh.id,4);
check(!api.isPreview(fresh)&&fresh.index===1&&location.hash==='#step=2','ordinary Play ends preview before restoring learner gate');
MuLERMoCScenario.present=false;
MuLERMoCScenario.authoring=false;
player.fScenarioAuthorPreviewBegin(fresh.id,4);
check(!api.isPreview(fresh)&&fresh.index===1,'author wrapper requires editor authoring context');
MuLERMoCScenario.authoring=true;
player.fScenarioPresentBegin(fresh.id,4,true);
check(!api.isPreview(fresh)&&fresh.index===1,'third argument alone cannot manufacture a preview');
MuLERMoCScenario.present=false;
player.fScenarioAuthorPreviewBegin(fresh.id,999);
check(api.isPreview(fresh)&&fresh.index===4,'preview start is clamped to available selected steps');
MuLERMoCScenario.present=false;
api.endPreview();
const invalid=lesson('invalid-player');invalid.steps[1].checkpoint.type='unknown-checkpoint';cards.set(invalid.id,invalid);
const beforeInvalidApply=applyCalls,beforeInvalidHash=location.hash;
player.fScenarioAuthorPreviewBegin(invalid.id,4);
check(!api.isPreview(invalid)&&!MuLERMoCScenario.present&&applyCalls===beforeInvalidApply&&location.hash===beforeInvalidHash,'preview validates malformed checkpoint and fails before applying/navigating');
check(errors.length===1,'invalid checkpoint produces actual player error reporting');
applySucceeds=false;
player.fScenarioAuthorPreviewBegin(fresh.id,4);
check(!api.isPreview(fresh)&&!MuLERMoCScenario.present&&MuLERMoCScenario.presentId===null&&location.hash===''&&restoreCalls===1,'failed preview application clears context and restores author settings');
applySucceeds=true;
const foreign=lesson('foreign-player');cards.set(foreign.id,foreign);
api.beginPreview(fresh);
MuLERMoCScenario.present=false;
player.fScenarioPresentBegin(foreign.id,4,true);
check(!api.isPreview(fresh)&&!api.isPreview(foreign)&&foreign.index===1,'preview identity cannot authorize another scenario');
equal(JSON.stringify([pilotSpec,orderRound]),fixtureJSON,'canonical authored round fixtures unchanged');
equal(JSON.stringify(learner),learnerBefore,'all player policy probes preserve original learner cache');
check(storage.get(key)===JSON.parse(storageBefore).find(pair=>pair[0]===key)[1],'all player policy probes preserve original learner stored bytes');
print(JSON.stringify({status:'passed',kind:'Developer verification, not independent review',checks,labels,
 fixtures:{replace:pilotSpec.round.id,order:orderRound.id},
 actualPlayerFunctions:''' + json.dumps(functions) + r''',
 storage:{reads:storageReads,writes:storageWrites},mounts:mounts.length,destroyCalls,
 limits:['JavaScriptCore on macOS; DOM, tab-storage transport and native dialog are in-memory doubles',
 'Actual repair engine validates/restores legal answers; shared round view mounting and viewer application are doubled',
 'Two authored static round fixtures cover replacement and ordering; actual generated-set browser replay is outside this harness',
 'Actual player policy/wrapper functions are extracted from current source; surrounding player UI/lifecycle functions are doubled',
 'Private inspection hooks are inserted only into transient evaluated controller strings',
 'No real browser, network, Safari/mobile, keyboard focus, row click event binding or conference demonstration claims']}));
'''

with tempfile.NamedTemporaryFile(prefix='namelecule-author-memory-', suffix='.js', dir='/tmp', mode='w', delete=False) as stream:
    stream.write(js)
    transient = Path(stream.name)
try:
    result = subprocess.run([JSC, str(transient)], cwd=ROOT, text=True, capture_output=True)
finally:
    transient.unlink()
if result.returncode or not result.stdout.strip():
    print(result.stdout, end='')
    print(result.stderr, end='')
    raise SystemExit(result.returncode or 1)
report = json.loads(result.stdout.strip().splitlines()[-1])
report.update({
    'command': 'python3 docs/checks/author-checkpoint-preview-20261107/check-memory.py',
    'sourceSHA256': {path: sha(ROOT / path) for path in (CONTROLLER, PLAYER, ENGINE, STATIC, PILOT)},
    'beforeSHA256': {path: sha(HERE / 'before' / path) for path in (CONTROLLER, PLAYER)},
    'protectedPathsUnchanged': len(baseline['protected']),
    'signatureImplementationUnchanged': True,
    'exportImplementationUnchanged': True,
    'harnessSHA256': sha(Path(__file__)),
})
(HERE / 'memory-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('status', 'checks', 'mounts', 'destroyCalls', 'protectedPathsUnchanged')}, ensure_ascii=False))
