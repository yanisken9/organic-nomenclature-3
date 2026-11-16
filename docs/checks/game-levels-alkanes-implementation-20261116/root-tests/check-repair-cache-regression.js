"use strict";
// REV-LEVELS-1: actual provider + Composite + unchanged checkpoint controller.
// All answer states are constructed MEMORY fixtures, never UI solutions.
const fs=require("fs"),path=require("path"),assert=require("assert/strict");
const {root,copy,sha,levels,baseRecipe,harness,attempt,levelState,settle,warm}=require("./check-composite.js");
const after=process.argv.includes("--after"),phase=after?"after":"before",paths=["js/namelecule-generated-repair-checkpoint.js","js/namelecule-game-choice-checkpoint.js","js/namelecule-quiz-checkpoints.js"];
const cuts=Object.fromEntries(paths.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))])),observations=[],failures=[];
function empty(seed){return{version:1,seed,currentRound:0,states:[null,null,null],solved:false};}
function context(h,recipe,level,seed){return h.provider.roundRecipe(recipe,levels.makeContext({source:"enriched",level,seed}));}
function verify(h,recipe,scenario,record,active,label,complete,receiptLevels){
  const restored=h.adapter.restore(recipe,record.states[10]),isComplete=h.scope.NameleculeQuizCheckpoints.isComplete(scenario,10),prior=h.scope.__navigation.length;
  h.scope.__controllerTest.continueLesson(active);const navigated=h.scope.__navigation.length===prior+1;
  const receipts=receiptLevels.map(level=>({level,seed:restored.receipts[level]?.attempt.context.seed,verified:restored.receipts[level]?.attempt.progress.solved===true}));
  const row={label,isComplete,navigated,aggregateSolved:restored.solved,receipts};observations.push(row);
  if(isComplete!==complete||navigated!==complete||restored.solved!==complete||receipts.some(row=>!row.verified))failures.push(row);
}
(async()=>{
  const h=harness({actualController:true}),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);
  let state=levelState("repair",1);state.games.repair[1]=attempt(h,recipe,"repair",1,"901");state=await settle(h,recipe,state);assert.equal(state.receipts[1].attempt.progress.solved,true);
  state.selectedLevel=2;state.games.repair[2]=attempt(h,recipe,"repair",2,"902");const earned=await settle(h,recipe,state);assert.equal(earned.solved,true);
  const scenario=JSON.parse(fs.readFileSync(path.join(root,"scenarios/alkanes-user-3.scenario.json")));scenario.index=10;h.scope.fScenarioPresent=()=>scenario;
  const record=h.scope.__controllerTest.recordFor(scenario);record.states[10]=copy(earned);const active={scenario,index:10,record,openButton:null};h.scope.__controllerTest.activate(active);
  const pinned=copy(record.states[10].receipts);verify(h,recipe,scenario,record,active,"required-901-902-before-churn",true,[1,2]);
  const round3=context(h,recipe,3,"930"),cycles=after?45:31;
  for(let index=0;index<cycles;index++){await h.provider.adapter.prepare(round3,empty(String(930+index)));verify(h,recipe,scenario,record,active,"L3-required-cache-generation-"+(index+1),true,[1,2]);}
  if(after){
    assert.equal(typeof h.provider.adapter.preparePractice,"function","Provider exposes isolated optional preparation");
    for(let index=0;index<45;index++){await h.provider.adapter.preparePractice(round3,empty(String(1100+index)));verify(h,recipe,scenario,record,active,"L3-practice-cache-generation-"+(index+1),true,[1,2]);}
    const beforeSecond=levelState("repair",1);beforeSecond.games.repair[1]=copy(earned.games.repair[1]);beforeSecond.receipts[1]=copy(pinned[1]);record.states[10]=beforeSecond;
    verify(h,recipe,scenario,record,active,"only-L1-before-whole-gate-complete",false,[1]);
    for(let index=0;index<45;index++){
      const seed=String(1300+index),wire=levels.makeContext({source:"enriched",level:1,seed}),round=context(h,recipe,1,seed);
      record.states[10].games.repair[1]={context:wire,progress:empty(seed)};await h.provider.adapter.prepare(round,empty(seed));
      verify(h,recipe,scenario,record,active,"L1-repeat-before-L2-"+(index+1),false,[1]);
      assert.equal(record.states[10].receipts[1].attempt.context.seed,"901");assert.deepEqual(record.states[10].receipts[1],pinned[1]);
    }
    record.states[10].games.repair[2]=copy(earned.games.repair[2]);record.states[10].receipts[2]=copy(pinned[2]);
    verify(h,recipe,scenario,record,active,"L2-earned-after-L1-repeat-churn-without-reprepare",true,[1,2]);
    const restored=h.adapter.restore(recipe,record.states[10]);assert.deepEqual(copy(restored.receipts),pinned);assert.equal(h.adapter.prepare(recipe,restored),null);
  }
  const current=Object.fromEntries(paths.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))])),sourceStable=JSON.stringify(cuts)===JSON.stringify(current);
  const report={recordedUTC:new Date().toISOString(),phase,finding:"REV-LEVELS-1",cuts,sourceStable,cyclesPerPhase:cycles,observations,failures,firstFailure:failures[0]||null,
    expected:after?"No required receipt/controller/Continue loss at any point, including repeated L1 before L2":"Reproduce original required-cache eviction without reprepare",reproduced:failures.length>0,
    passed:sourceStable&&(after?failures.length===0:failures.length>0),controller:"Actual unchanged NameleculeQuizCheckpoints.isComplete and private continueLesson; VM-only record/current-context hooks",memoryOnly:true,runtimeEdits:false};
  fs.writeFileSync(path.join(__dirname,"repair-cache-"+phase+".json"),JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({phase,passed:report.passed,sourceStable,checks:observations.length,failures:failures.length,firstFailure:report.firstFailure,cuts},null,2));
  if(!report.passed)process.exitCode=1;
})().catch(error=>{fs.writeFileSync(path.join(__dirname,"repair-cache-"+phase+"-fatal.json"),JSON.stringify({recordedUTC:new Date().toISOString(),cuts,error:error.stack||String(error)},null,2)+"\n");console.error(error);process.exitCode=1;});
