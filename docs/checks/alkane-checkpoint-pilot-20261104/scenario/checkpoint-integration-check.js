// Developer JavaScriptCore integration checks. The controller is a contract
// double; actual modal, persistence and browser checks belong to the root agent.
var sourcePath = arguments[0] || 'js/mulermoc-nom-scenario-54.js';
var window = globalThis, events = {}, calls = [], toasts = [], assigned = null;
window.addEventListener = function (name, fn) { events[name] = fn; };
var nextButton = {disabled:false,setAttribute:function(k,v){this[k]=v;}};
var document = {
  readyState:'loading', addEventListener:function(){},
  getElementById:function(id){return id==='scNext' ? nextButton : null;},
  querySelectorAll:function(){return [];}
};
var location = {search:'',hash:'',pathname:'/mulermoc-nom-54.html',assign:function(url){assigned=url;calls.push(['exit-url',url]);}};
var history = {replaceState:function(a,b,url){location.hash=url.charAt(0)==='#'?url:'';calls.push(['hash',url]);}};
load('js/jsme-nick-nomeclature-moc2-data_54.js');
var VIEWER_MIN_H=150, VIEWER_MAX_H=2000, VIEWER_BOTH_MIN=300, VIEWER_BOTH_MAX=1000;
load(sourcePath);
var checks=0, failures=[];
function check(ok,label,detail){checks++;if(!ok)failures.push({label:label,detail:detail});}
function clone(v){return JSON.parse(JSON.stringify(v));}
function same(a,b){return JSON.stringify(a)===JSON.stringify(b);}
var round=JSON.parse(readFile('games/data/name-repair-alkanes.json')).rounds.filter(function(r){return r.id==='parent-not-total';})[0];
var cp={id:'alkanes-parent-chain',type:'name-repair',version:1,round:round};
var completed={};
var api={
  validateCheckpoint:function(spec){
    if(!spec || spec.type!=='name-repair' || spec.version!==1 || !spec.id || !spec.round || spec.round.id!=='parent-not-total')throw Error('Invalid checkpoint contract');
    return clone(spec);
  },
  hasCheckpoints:function(scen){return scen.steps.some(function(s){return Object.prototype.hasOwnProperty.call(s,'checkpoint');});},
  isComplete:function(scen,index){return !!completed[index];},
  resolveTarget:function(scen,requested){for(var i=0;i<requested;i++)if(scen.steps[i].checkpoint && !this.isComplete(scen,i))return i;return requested;},
  onStep:function(scen,index){calls.push(['checkpoint-step',index]);},
  onExit:function(){calls.push(['checkpoint-exit']);}
};
window.NameleculeQuizCheckpoints=api;
function lesson(){return {scenarioVersion:2,title:'Checkpoint test',steps:[{selectedMol:'methane'},{selectedMol:'methyl_2_pentane',checkpoint:clone(cp)},{selectedMol:'ethane'},{selectedMol:'propane'}]};}
function validate(input){try{return fScenarioValidate(input);}catch(e){return {ok:false,warnings:[String(e)]};}}
var input=lesson(), before=JSON.stringify(input), valid=validate(input);
check(valid.ok,'v2 checkpoint lesson accepted',valid.warnings);
check(JSON.stringify(input)===before,'Validation does not mutate source');
if(valid.ok){
  check(valid.scenarioVersion===2,'Normalized checkpoint version2');
  check(same(valid.steps[1].checkpoint,cp),'Checkpoint metadata preserved');
  valid.steps[1].checkpoint.round.parts[0].text='changed';
  check(input.steps[1].checkpoint.round.parts[0].text!=='changed','Defaults deep-copy nested checkpoint content');
}
var legacy=lesson();legacy.scenarioVersion=1;
check(!validate(legacy).ok,'v1 checkpoint rejected before silent interpretation');
delete legacy.scenarioVersion;
check(!validate(legacy).ok,'Unversioned mandatory checkpoint rejected');
var bad=lesson();bad.steps[1].checkpoint.type='future-quiz';
check(!validate(bad).ok,'Unknown checkpoint type rejects whole lesson');
bad=lesson();bad.steps[1].checkpoint=null;
check(!validate(bad).ok,'Null checkpoint rejects whole lesson');
bad=lesson();bad.steps[1].checkpoint.version=99;
check(!validate(bad).ok,'Unknown checkpoint version rejects whole lesson');
bad=lesson();bad.steps[1].selectedMol='unknown-molecule';
check(!validate(bad).ok,'Unknown checkpoint molecule rejects whole lesson');
bad=lesson();delete bad.steps[1].selectedMol;
check(!validate(bad).ok,'Unrenderable checkpoint step rejects whole lesson');
window.NameleculeQuizCheckpoints=null;
check(!validate(lesson()).ok,'Unavailable controller rejects checkpoint lesson');
var ordinary={scenarioVersion:1,title:'Ordinary',steps:[{selectedMol:'methane'}]};
check(validate(ordinary).ok,'Ordinary v1 accepts unavailable controller');
window.NameleculeQuizCheckpoints=api;
fScenarioBuildPanels=function(){};fScenarioPaintPickUi=function(){};fScenarioRenderList=function(){};
fScenarioToast=function(s){toasts.push(s);};
var captured=null;
window.Blob=function(parts){this.parts=parts;};
fScenarioSaveBlob=function(name,blob){captured=JSON.parse(blob.parts.join(''));return true;};
function makeCard(raw){var res=validate(raw),card=fScenarioNew(raw.title,true);card.steps=res.ok?res.steps:clone(raw.steps);card.index=0;return card;}
var card=makeCard(lesson());
fScenarioExport(card.id);
check(captured.scenarioVersion===2,'Checkpoint export is version2');
check(same(captured.steps[1].checkpoint,cp),'Export retains exact checkpoint content');
check(validate(captured).ok,'Checkpoint export/import validation roundtrip');
var plain=makeCard(ordinary);fScenarioExport(plain.id);
check(captured.scenarioVersion===1,'Ordinary export remains version1');
var originalCapture=fScenarioCapture;
fScenarioCapture=function(){return fScenarioDefaults({selectedMol:'methane'},0);};
fScenarioSetActive(card.id);var oldCp=card.steps[1].checkpoint;
fScenarioUpdateStep(card.id,1);
check(same(card.steps[1].checkpoint,cp),'Update preserves authored checkpoint');
if(card.steps[1].checkpoint){
  check(card.steps[1].checkpoint!==oldCp && card.steps[1].checkpoint.round!==oldCp.round,'Update checkpoint is independent nested copy');
}
fScenarioDuplicateStep(card.id,1);
check(card.steps[2].checkpoint && same(card.steps[2].checkpoint,card.steps[1].checkpoint),'Duplicate retains checkpoint metadata');
if(card.steps[2].checkpoint)check(card.steps[2].checkpoint.round!==card.steps[1].checkpoint.round,'Duplicate checkpoint copy is independent');
fScenarioCapture=originalCapture;
// Import itself, rather than validation alone, must keep version/metadata.
window.FileReader=function(){this.readAsText=function(file){this.result=JSON.stringify(file);this.onload();};};
fScenarioImportFile(lesson());var imported=fScenarioActive();
check(imported.scenarioVersion===2 && same(imported.steps[1].checkpoint,cp),'File import keeps version2 and checkpoint');
// Exercise real destination code with the molecular apply layer replaced only
// to count calls. No DOM/viewer execution is claimed by this harness.
var applied=[];
fScenarioApply=function(step){applied.push(step.selectedMol);calls.push(['apply',step.selectedMol]);return true;};
fScenarioRenderPresentMenu=function(){};fScenarioStashAuthorSettings=function(){};
fScenarioRestoreAuthorSettings=function(){};fScenarioSyncPresentClass=function(){};
fScenarioSetPinned=function(){};
card=makeCard(lesson());completed={};calls=[];applied=[];
MuLERMoCScenario.present=false;MuLERMoCScenario.presentId=null;
fScenarioPresentBegin(card.id,3);
check(card.index===1,'Direct PresentBegin clamps to first unsolved checkpoint',card.index);
check(applied.length===1 && applied[0]==='methyl_2_pentane','Direct presentation applies checkpoint only',applied);
check(location.hash==='#step=2','Direct presentation hash uses resolved target',location.hash);
check(nextButton.disabled===true,'Next disabled on unsolved current checkpoint');
check(calls.some(function(c){return c[0]==='checkpoint-step' && c[1]===1;}),'onStep called after presentation apply');
var applyCount=applied.length;
fScenarioGo(3);
check(card.index===1 && applied.length===applyCount,'Blocked forward jump at current gate does not reapply snapshot');
check(location.hash==='#step=2','Blocked forward jump retains resolved hash');
fScenarioGo(0);
check(card.index===0 && applied[applied.length-1]==='methane','Earlier theory remains accessible');
check(nextButton.disabled===false,'Next allows reaching checkpoint from preceding theory');
fScenarioGo(3);
check(card.index===1,'Jump from earlier theory cannot bypass checkpoint');
completed[1]=true;applyCount=applied.length;fScenarioPlayUi();
check(nextButton.disabled===false,'Solved notification enables Next');
check(applied.length===applyCount,'Solved UI refresh does not reapply snapshot');
fScenarioGo(3);check(card.index===3,'Solved checkpoint allows later destination');
// Fresh session / cold deep link: no previously applied marker, including a
// checkpoint at index zero, must still apply the first visible snapshot.
completed={};card=makeCard(lesson());MuLERMoCScenario.presentId=card.id;MuLERMoCScenario.present=true;
MuLERMoCScenario.checkpointApplied=null;applied=[];fScenarioGo(3);
check(card.index===1 && applied.length===1,'Cold Go clamps and applies checkpoint');
var first=lesson();first.steps[0].checkpoint=clone(cp);card=makeCard(first);
MuLERMoCScenario.presentId=card.id;MuLERMoCScenario.checkpointApplied=null;applied=[];fScenarioGo(3);
check(card.index===0 && applied.length===1,'Cold checkpoint at index0 still applies snapshot');
// Authoring Go is a preview and may inspect later snapshots.
MuLERMoCScenario.present=false;MuLERMoCScenario.presentId=null;fScenarioSetActive(card.id);fScenarioGo(3);
check(card.index===3,'Authoring preview remains ungated');
// Capture and exercise the real hashchange listener. Boot is prevented from
// fetching or changing the DOM; only listener registration runs.
fScenarioBuildUi=function(){};fScenarioWhenReady=function(){};fScenarioBoot();
card=makeCard(lesson());completed={};MuLERMoCScenario.present=true;MuLERMoCScenario.presentId=card.id;
MuLERMoCScenario.checkpointApplied=null;applied=[];fScenarioGo(1);applyCount=applied.length;
location.hash='#step=4';events.hashchange();
check(card.index===1 && location.hash==='#step=2','Hashchange jump is clamped to gate');
check(applied.length===applyCount,'Blocked hashchange does not reset current viewer');
location.hash='#step=1';events.hashchange();check(card.index===0,'Browser backward hash can reach earlier theory');
location.hash='#step=4';events.hashchange();check(card.index===1,'Browser forward hash cannot bypass unsolved gate');
completed[1]=true;location.hash='#step=4';events.hashchange();check(card.index===3,'Browser forward hash allowed after solution');
// Runtime dependency failures must not mutate index, hash or molecular state.
window.NameleculeQuizCheckpoints=null;calls=[];applyCount=applied.length;var indexBefore=card.index,hashBefore=location.hash;
fScenarioGo(0);
check(card.index===indexBefore && location.hash===hashBefore && applied.length===applyCount,'Missing controller fails closed before Go mutations');
MuLERMoCScenario.present=false;calls=[];fScenarioPresentBegin(card.id,3);
check(!MuLERMoCScenario.present && !calls.length,'Missing controller fails closed before PresentBegin mutations',calls);
// Exit/Esc calls this function and remains available even on missing quizzes.
MuLERMoCScenario.present=true;MuLERMoCScenario.presentId=card.id;MuLERMoCScenario.returnToTheoryLibrary=true;assigned=null;
fScenarioExitPresent();check(!!assigned,'Exit remains available with unavailable controller');
window.NameleculeQuizCheckpoints=api;calls=[];assigned=null;
fScenarioExitPresent();
check(calls.length===2 && calls[0][0]==='checkpoint-exit' && calls[1][0]==='exit-url','Checkpoint cleanup occurs before library Exit redirect',calls);
// Runtime changes to already imported content receive the same validation as
// file imports before any destination mutates the snapshot/index/hash.
card=makeCard(lesson());card.steps[1].checkpoint.type='future-quiz';
MuLERMoCScenario.present=true;MuLERMoCScenario.presentId=card.id;calls=[];applyCount=applied.length;hashBefore=location.hash;
fScenarioGo(3);
check(card.index===0 && applied.length===applyCount && location.hash===hashBefore,'Unknown in-memory checkpoint fails closed before destination mutation');
var storedStep=card.steps[1];fScenarioCapture=function(){return fScenarioDefaults({selectedMol:'ethane'},0);};
fScenarioUpdateStep(card.id,1);
check(card.steps[1]===storedStep,'Invalid checkpoint Update leaves stored step intact');
fScenarioCapture=originalCapture;
// Exercise both real boot copy paths with synchronous fetch/ready contract
// doubles. This covers metadata and cold destinations, not network timing.
function bootWith(raw,search,hash){
  MuLERMoCScenario.scenarios=[];MuLERMoCScenario.activeId=null;MuLERMoCScenario.presentId=null;
  MuLERMoCScenario.checkpointApplied=null;MuLERMoCScenario.authoring=false;MuLERMoCScenario.authoringOpened=false;
  MuLERMoCScenario.returnToTheoryLibrary=false;completed={};applied=[];
  location.search=search;location.hash=hash;fScenarioWhenReady=function(cb){cb();};fScenarioWhenJSmolReady=function(cb){cb();};
  window.fetch=function(){return {then:function(first){var value=first({ok:true,json:function(){return clone(raw);}});return {then:function(second){second(value);return {catch:function(){}};}};}};};
  fScenarioBoot();return fScenarioActive();
}
var cold=bootWith(lesson(),'?scenario=scenarios/pilot.json&present=1','#step=4');
check(cold.scenarioVersion===2 && same(cold.steps[1].checkpoint,cp),'Cold URL boot preserves checkpoint metadata and version');
check(cold.index===1 && applied.length===1 && applied[0]==='methyl_2_pentane','Cold URL boot gates requested later hash before apply');
var preloaded=bootWith(lesson(),'?present=1','#step=4');
check(preloaded.scenarioVersion===2 && same(preloaded.steps[1].checkpoint,cp),'Default preload preserves checkpoint metadata and version');
check(preloaded.index===1 && applied.length===1 && applied[0]==='methyl_2_pentane','Default preload presentation gates later hash');
// Restoring ordinary v1 behavior must not require any checkpoint module.
window.NameleculeQuizCheckpoints=null;
var normal=bootWith(ordinary,'?scenario=scenarios/ordinary.json&present=1','#step=1');
check(normal.steps.length===1 && normal.index===0 && applied.length===1,'Ordinary cold lesson works with unavailable checkpoint controller');
print(JSON.stringify({runtime:'JavaScriptCore',source:sourcePath,controller:'contract double; no browser/persistence claims',checks:checks,failures:failures},null,2));
if(failures.length)quit(1);
