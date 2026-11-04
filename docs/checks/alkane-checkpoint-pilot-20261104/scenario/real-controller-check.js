// Developer cross-module checks in JavaScriptCore. No browser/DOM claims.
var window=globalThis, document, stored=null;
window.addEventListener=function(){};
window.sessionStorage={getItem:function(){return stored;},setItem:function(key,value){stored=value;}};
load('js/namelecule-game-repair.js');
load('js/namelecule-quiz-checkpoints.js');
document={readyState:'loading',addEventListener:function(){},getElementById:function(){return null;},querySelectorAll:function(){return [];}};
load('js/jsme-nick-nomeclature-moc2-data_54.js');
var VIEWER_MIN_H=150,VIEWER_MAX_H=2000,VIEWER_BOTH_MIN=300,VIEWER_BOTH_MAX=1000;
load('js/mulermoc-nom-scenario-54.js');
var checks=0,failures=[];
function check(ok,label){checks++;if(!ok)failures.push(label);}
function clone(v){return JSON.parse(JSON.stringify(v));}
var round=JSON.parse(readFile('games/data/name-repair-alkanes.json')).rounds.filter(function(r){return r.id==='parent-not-total';})[0];
var spec={id:'alkanes-parent-chain',type:'name-repair',version:1,round:round};
function raw(){return {scenarioVersion:2,title:'Real modules',author:'Unknown',steps:[{selectedMol:'methane'},{selectedMol:'methyl_2_pentane',checkpoint:clone(spec)},{selectedMol:'ethane'},{selectedMol:'propane'}]};}
var data=raw(),before=JSON.stringify(data),res=fScenarioValidate(data);
check(res.ok && res.scenarioVersion===2,'Real controller/engine accept pilot v2');
check(JSON.stringify(data)===before,'Real validation preserves source input');
check(res.steps[1].checkpoint.round!==data.steps[1].checkpoint.round,'Real checkpoint normalization deep-copies round');
var invalid=raw();invalid.steps[1].checkpoint.round.targetPartId='missing';
check(!fScenarioValidate(invalid).ok,'Real engine rejects invalid authored question');
var scenario={title:res.title,author:res.author,steps:res.steps};
check(fScenarioResolveCheckpointTarget(scenario,3)===1,'Real modules gate unsolved checkpoint');
var state=NameleculeRepairEngine.createRoundState(round);
state.selectedPartId=round.targetPartId;state.selectedValue=round.correctValue;
state.attempts=1;state.submitted=true;state.solved=true;
check(NameleculeRepairEngine.evaluateRepair(round,state).kind==='correct','Stored solution uses real engine correct answer');
function content(scen){return JSON.stringify({version:1,title:String(scen.title||''),author:String(scen.author||'Unknown'),steps:scen.steps});}
function reloadWith(scen,states){
 stored=JSON.stringify({version:1,content:content(scen),states:states});
 load('js/namelecule-quiz-checkpoints.js');
 return NameleculeQuizCheckpoints;
}
var api=reloadWith(scenario,{1:{solved:true}});
check(!api.isComplete(scenario,1),'Forged completion flag cannot unlock pilot');
check(fScenarioResolveCheckpointTarget(scenario,3)===1,'Invalid saved answer keeps destination gated');
api=reloadWith(scenario,{1:state});
check(api.isComplete(scenario,1),'Real validated saved answer restores completion');
check(fScenarioResolveCheckpointTarget(scenario,3)===3,'Restored completion unlocks later destination');
var revisited=clone(scenario);load('js/namelecule-quiz-checkpoints.js');
check(NameleculeQuizCheckpoints.isComplete(revisited,1),'Identical lesson reload restores content-scoped progress');
var edited=clone(scenario);edited.steps[1].note='Changed lesson';load('js/namelecule-quiz-checkpoints.js');
check(!NameleculeQuizCheckpoints.isComplete(edited,1),'Changed lesson content invalidates saved completion');
var duplicated=clone(scenario);duplicated.steps[2].checkpoint=clone(spec);
api=reloadWith(duplicated,{1:state});
check(api.isComplete(duplicated,1) && !api.isComplete(duplicated,2),'Duplicate authored IDs retain independent index receipts');
check(fScenarioResolveCheckpointTarget(duplicated,3)===2,'Second duplicate checkpoint still gates destination');
window.sessionStorage={getItem:function(){throw Error('unavailable');},setItem:function(){throw Error('unavailable');}};
load('js/namelecule-quiz-checkpoints.js');
check(!NameleculeQuizCheckpoints.isComplete(scenario,1),'Unavailable session storage does not unlock checkpoint');
print(JSON.stringify({runtime:'JavaScriptCore',modules:['scenario54','NameleculeRepairEngine','NameleculeQuizCheckpoints'],checks:checks,failures:failures,untested:'Actual DOM, dialog, browser, network and physical storage persistence are verified separately by root.'},null,2));
if(failures.length)quit(1);
