// Run with JavaScriptCore jsc from the repository root.
var window=this;window.addEventListener=function(){};
var document={readyState:'loading',addEventListener:function(){},getElementById:function(){return null;},body:{appendChild:function(){}},createElement:function(){return {click:function(){},remove:function(){}};}};
var exported;
function Blob(parts){exported=parts.join('');}
var URL={createObjectURL:function(){return 'test';},revokeObjectURL:function(){}};
const VIEWER_MIN_H=150,VIEWER_MAX_H=2000,VIEWER_BOTH_MIN=300,VIEWER_BOTH_MAX=1000;
function assert(ok,msg){if(!ok)throw Error(msg);}
load('js/jsme-nick-nomeclature-moc2-data_49.js');
load('js/mulermoc-nom-scenario-49.js');
const src=JSON.parse(readFile('scenarios/alkanes-nomenclature-branches.scenario.json'));
const result=fScenarioValidate(src);
assert(result.ok && !result.warnings.length && result.steps.length===22,'lesson validation');
assert(!result.showStepNumbers && result.reserveTitleSpace,'custom title flags');
assert(result.steps[14].chainIdx===1 && result.steps[15].chainIdx===1 && result.steps[16].chainIdx===1,'chain choices');
assert(result.steps[8].show.rule && result.steps[17].show.rule,'alkyl rule steps');
const scen=fScenarioNew(result.title,true);scen.steps=result.steps;scen.showStepNumbers=result.showStepNumbers;scen.reserveTitleSpace=result.reserveTitleSpace;
fScenarioExport(scen.id);
const round=fScenarioValidate(JSON.parse(exported));
assert(JSON.parse(exported).app==='mulermoc-nom-49','export app version');
assert(round.ok && JSON.stringify(round.steps)===JSON.stringify(result.steps),'roundtrip steps');
assert(!round.showStepNumbers && round.reserveTitleSpace,'roundtrip title flags');
print('PASS alkane v49 validation and export/import:22steps,chain choices,rule panels,title preferences.');
