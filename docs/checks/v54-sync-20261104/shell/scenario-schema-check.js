// Developer scenario/schema checks in JavaScriptCore; no browser claims.
var window = globalThis;
window.addEventListener = function () {};
var document = {readyState:'loading',addEventListener:function(){},getElementById:function(){return null;}};
load('js/jsme-nick-nomeclature-moc2-data_52.js');
// Viewer range constants supplied from upstream54 viewer (DOM layout is not exercised).
var VIEWER_MIN_H=150, VIEWER_MAX_H=2000, VIEWER_BOTH_MIN=300, VIEWER_BOTH_MAX=1000;
load('js/mulermoc-nom-scenario-54.js');
var checks=0, failures=[];
function check(ok,label,detail){checks++;if(!ok)failures.push({label:label,detail:detail});}
function same(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function compareLeaves(a,b,path,diffs){
 if(a && typeof a==='object'){
  if(Array.isArray(a) && (!Array.isArray(b) || a.length!==b.length)){diffs.push(path+': array size/type');return;}
  Object.keys(a).forEach(function(k){compareLeaves(a[k],b&&b[k],path+'.'+k,diffs);});
 }else if(!same(a,b)){diffs.push(path+': '+JSON.stringify(a)+' -> '+JSON.stringify(b));}
}
var lessons=["scenarios/alkanes-nomenclature-branches.scenario.json", "scenarios/alkenes-nomenclature-branches.scenario.json", "scenarios/alkynes-nomenclature-branches.scenario.json", "scenarios/alkadienes-nomenclature-branches.scenario.json", "scenarios/enynes-nomenclature-branches.scenario.json", "scenarios/saturated-monoalcohols-nomenclature.scenario.json", "scenarios/other-alcohols-nomenclature.scenario.json", "scenarios/saturated-monoethers-nomenclature.scenario.json", "scenarios/saturated-monoaldehydes-nomenclature.scenario.json", "scenarios/other-aldehydes-nomenclature.scenario.json", "scenarios/saturated-monoketones-nomenclature.scenario.json", "scenarios/other-ketones-nomenclature.scenario.json", "scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json", "scenarios/other-carboxylic-acids-nomenclature.scenario.json"];
var baseline=JSON.parse(readFile('docs/checks/v54-sync-20261104/shell/scenario-baseline-normalization.json'));
var lessonResults=[],total=0;
lessons.forEach(function(path){
 var source=JSON.parse(readFile(path)), before=JSON.stringify(source),res=fScenarioValidate(source),diffs=[];
 check(res.ok,path+' accepted',res.warnings);
 check(res.steps.length===source.steps.length,path+' step count');
 check(res.title===source.title,path+' title');
 check(res.showStepNumbers===(source.showStepNumbers!==false),path+' step numbering preference');
 check(res.reserveTitleSpace===(source.reserveTitleSpace===true),path+' title space preference');
 check(JSON.stringify(source)===before,path+' source not mutated');
 baseline[path].steps.forEach(function(step,i){compareLeaves(step,res.steps[i],'steps['+i+']',diffs);});
 check(!diffs.length,path+' all52 runtime step fields preserved',diffs);
 check(res.steps.every(function(s){return s.lang==='gr';}),path+' legacy Greek default');
 lessonResults.push({path:path,steps:source.steps.length,warnings:res.warnings,baseline52RuntimeDifferences:diffs});
 total+=source.steps.length;
});
check(lessons.length===14 && total===337,'14 lessons/337 steps retained');
var step={selectedMol:'methane',lang:'en',note:'schema-test',view3D:{moveto:'moveto 0.0 { 0 0 1 0} 100;',spin:false,showH:true,atomSymbols:false},show:{viewerMaxHeight:'full',viewerBothHeight:'full',nameExpanded:true,alkoxyRule:true},styleName:{hidden:['comp1']}};
var input={scenarioVersion:1,app:'mulermoc-nom-44',title:'schema-test',author:'  Test author  ',created:'2026-11-04T12:00:00.000Z',showStepNumbers:false,reserveTitleSpace:true,steps:[step]};
var v=fScenarioValidate(input);
check(v.ok,'legacy app44 marker accepted');
check(v.author==='Test author','author trimmed');
check(v.created===input.created,'creation timestamp preserved');
check(v.showStepNumbers===false && v.reserveTitleSpace===true,'custom scenario preferences retained');
check(v.steps[0].lang==='en','English step preserved');
check(v.steps[0].show.viewerMaxHeight==='full' && v.steps[0].show.viewerBothHeight==='full','full viewer heights preserved');
check(v.steps[0].show.nameExpanded===true && v.steps[0].show.alkoxyRule===true,'expanded name and local alkoxy reference preserved');
check(v.steps[0].view3D.moveto===step.view3D.moveto,'per-step camera preserved',v.steps[0].view3D.moveto);
var card=fScenarioNew(v.title,true);
card.steps=v.steps;card.author=v.author;card.created=v.created;card.showStepNumbers=v.showStepNumbers;card.reserveTitleSpace=v.reserveTitleSpace;
var captured=null;window.Blob=function(parts,opts){this.parts=parts;this.type=opts.type;};
fScenarioSaveBlob=function(name,blob){captured={name:name,payload:JSON.parse(blob.parts.join(''))};return true;};
fScenarioExport(card.id);
check(!!captured,'export delivery called');
check(captured.payload.app==='mulermoc-nom-54','export54 app marker');
check(captured.payload.scenarioVersion===1,'schemaVersion stays1');
var rt=fScenarioValidate(captured.payload);
check(rt.ok && same(rt.steps,v.steps),'export/validate roundtrip steps');
check(rt.author===v.author && rt.created===v.created,'export/validate metadata retained');
check(rt.showStepNumbers===false && rt.reserveTitleSpace===true,'export/validate custom preferences retained');
var fresh=fScenarioNew('new',true);
check(fresh.author==='Unknown' && !!fScenarioValidCreated(fresh.created),'new scenario author/date defaults');
check(fresh.showStepNumbers===true && fresh.reserveTitleSpace===false,'new scenario local preference defaults');
var invalid=fScenarioValidate({steps:[{selectedMol:'methane',lang:'xx'}],author:55,created:'bad-date'});
check(invalid.ok && invalid.author==='Unknown' && invalid.created===null,'invalid author/date normalized');
check(invalid.steps[0].lang==='gr' && invalid.warnings.some(function(w){return w.indexOf('invalid language')!==-1;}),'invalid step language normalized with warning');
var defaults=fScenarioDefaults({selectedMol:'methane'},0);
check(defaults.show.viewerMaxHeight==='full' && defaults.show.viewerBothHeight==='full','upstream full-height new-step defaults');
check(defaults.show.nameExpanded===false,'new step name-expanded defaultfalse');
// Additive box-layout contract: legacy snapshots, upstream pieces, author views.
check(fScenarioDefaults({selectedMol:'methane'},0).nameBoxLayout===1,'Missing layout uses legacy semantics');
check(fScenarioDefaults({selectedMol:'methane',nameBoxLayout:1,nameAnalysisMode:'compBranchSub1'},0).nameBoxLayout===1,'Explicit1 preserved even with future piece ID');
check(fScenarioDefaults({selectedMol:'methane',nameBoxLayout:2},0).nameBoxLayout===2,'Explicit2 preserved');
check(fScenarioDefaults({selectedMol:'methane',nameAnalysisMode:'compBranchSub2'},0).nameBoxLayout===2,'Missing version infers new branch-piece mode');
check(fScenarioDefaults({selectedMol:'methane',nameAnalysisMode:'compSuffixLocants'},0).nameBoxLayout===2,'Missing version infers new suffix-locant mode');
check(['comp3loc','comp3b','comp3loc2','comp3b2','comp9loc'].every(function(id){return fScenarioDefaults({selectedMol:'methane',styleName:{hidden:[id]}},0).nameBoxLayout===2;}),'Missing version infers explicit new hidden-piece IDs');
var invalidLayout=fScenarioValidate({steps:[{selectedMol:'methane',nameBoxLayout:99,nameAnalysisMode:'compBranchSub2'}]});
check(invalidLayout.ok && invalidLayout.steps[0].nameBoxLayout===1 && invalidLayout.warnings.some(function(w){return w.indexOf('invalid name-box layout')!==-1;}),'Invalid explicit version warns and uses safe legacy semantics');
check(lessonResults.every(function(row){return fScenarioValidate(JSON.parse(readFile(row.path))).steps.every(function(s){return s.nameBoxLayout===1;});}),'All337 existing steps default to legacy1');
MuLERMoCScenario.nameBoxLayoutContext=null;
check(!fScenarioUseLegacyNameBoxes(),'Normal free context is modern54');
fScenarioStashAuthorSettings();MuLERMoCScenario.nameBoxLayoutContext=1;fScenarioRestoreAuthorSettings();
check(MuLERMoCScenario.nameBoxLayoutContext===null && !fScenarioUseLegacyNameBoxes(),'Exit restore returns normal context before naming repaint');
MuLERMoCScenario.nameBoxLayoutContext=1;fScenarioStashAuthorSettings();MuLERMoCScenario.nameBoxLayoutContext=2;fScenarioRestoreAuthorSettings();
check(fScenarioUseLegacyNameBoxes(),'Exit restores authored legacy Go-preview context');
fScenarioClearNameBoxLayout();check(!fScenarioUseLegacyNameBoxes(),'Explicit free choice clears authored context');
var selectedMol='methane';MuLERMoCScenario.ready=true;
check(fScenarioCapture().nameBoxLayout===2,'New free capture records modern2');
MuLERMoCScenario.nameBoxLayoutContext=1;
check(fScenarioCapture().nameBoxLayout===1,'Capture of legacy live preview preserves1');
var keepCard=fScenarioNew('layout roundtrip',true);keepCard.steps=[fScenarioDefaults({selectedMol:'methane',nameBoxLayout:1},0),fScenarioDefaults({selectedMol:'ethane',nameBoxLayout:2},1)];
fScenarioExport(keepCard.id);var keepRound=fScenarioValidate(captured.payload);
check(keepRound.steps[0].nameBoxLayout===1 && keepRound.steps[1].nameBoxLayout===2,'Export/import preserves both layout versions');
var originalCapture=fScenarioCapture;fScenarioCapture=function(){return fScenarioDefaults({selectedMol:'methane',nameBoxLayout:2},0);};fScenarioRenderList=function(){};fScenarioToast=function(){};
fScenarioUpdateStep(keepCard.id,0);
check(keepCard.steps[0].nameBoxLayout===1,'Update preserves existing legacy layout version');
fScenarioCapture=originalCapture;
var result={runtime:'JavaScriptCore',checks:checks,failures:failures,lessons:lessonResults,totalSteps:total,exportPayload:captured.payload};
print(JSON.stringify(result,null,2));
if(failures.length)quit(1);
