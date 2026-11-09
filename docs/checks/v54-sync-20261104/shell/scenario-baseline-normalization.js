// Developer scenario/schema checks in JavaScriptCore; no browser claims.
var window = globalThis;
window.addEventListener = function () {};
var document = {readyState:'loading',addEventListener:function(){},getElementById:function(){return null;}};
load('js/jsme-nick-nomeclature-moc2-data_52.js');
// Viewer range constants supplied from upstream54 viewer (DOM layout is not exercised).
var VIEWER_MIN_H=150, VIEWER_MAX_H=2000, VIEWER_BOTH_MIN=300, VIEWER_BOTH_MAX=1000;
load('js/mulermoc-nom-scenario-52.js');
var lessons=["scenarios/alkanes-nomenclature-branches.scenario.json", "scenarios/alkenes-nomenclature-branches.scenario.json", "scenarios/alkynes-nomenclature-branches.scenario.json", "scenarios/alkadienes-nomenclature-branches.scenario.json", "scenarios/enynes-nomenclature-branches.scenario.json", "scenarios/saturated-monoalcohols-nomenclature.scenario.json", "scenarios/other-alcohols-nomenclature.scenario.json", "scenarios/saturated-monoethers-nomenclature.scenario.json", "scenarios/saturated-monoaldehydes-nomenclature.scenario.json", "scenarios/other-aldehydes-nomenclature.scenario.json", "scenarios/saturated-monoketones-nomenclature.scenario.json", "scenarios/other-ketones-nomenclature.scenario.json", "scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json", "scenarios/other-carboxylic-acids-nomenclature.scenario.json"];
var outputs={};lessons.forEach(function(path){outputs[path]=fScenarioValidate(JSON.parse(readFile(path)));});print(JSON.stringify(outputs,null,2));
