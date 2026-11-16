"use strict";
// Developer MEMORY evidence: raw correct answers are constructed here from the
// actual generated rounds/graphs. This does not claim any human/UI solutions.
const fs=require("fs"),path=require("path"),vm=require("vm"),crypto=require("crypto"),assert=require("assert/strict");
const root=path.resolve(__dirname,"../../../.."),output=__dirname;
const copy=value=>JSON.parse(JSON.stringify(value)),sha=value=>crypto.createHash("sha256").update(value).digest("hex");
const runtime=["js/namelecule-game-levels.js","js/namelecule-generated-repair-checkpoint.js","js/namelecule-game-choice-checkpoint.js","js/namelecule-molecular-detective-lesson.js","js/namelecule-molecular-detective-engine.js","js/namelecule-name-builder-engine.js","js/namelecule-molecular-puzzle-engine.js","js/namelecule-repair-generator.js","scenarios/alkanes-user-3.scenario.json"];
const cuts=Object.fromEntries(runtime.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))]));
const levels=require(path.join(root,"js/namelecule-game-levels.js")),generator=require(path.join(root,"js/namelecule-repair-generator.js")),builder=require(path.join(root,"js/namelecule-name-builder-engine.js")),detective=require(path.join(root,"js/namelecule-molecular-detective-engine.js"));
require(path.join(root,"js/namelecule-molecular-puzzle-engine.js"));const puzzle=global.NameleculeMolecularPuzzleEngine;
const roundEngine=require(path.join(root,"docs/checks/game-levels-alkanes-implementation-20261116/before/js/namelecule-game-repair.js"));
const engineSHA="3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306",coreCode=fs.readFileSync(path.join(root,"js/chemistry-engines",engineSHA+".js"),"utf8"),workerCode=fs.readFileSync(path.join(root,"js/namelecule-chemistry-worker.js"),"utf8");assert.equal(sha(coreCode),engineSHA);
const analysisCache=new Map();
function analyze(molecule){const key=sha(molecule.mol);if(analysisCache.has(key))return copy(analysisCache.get(key));let reply;
  const scope=vm.createContext({URL,console,self:{location:{origin:"https://namelecule.invalid"},postMessage:value=>reply=value,close(){}}});scope.importScripts=()=>vm.runInContext(coreCode,scope);vm.runInContext(workerCode,scope);
  scope.self.onmessage({data:{type:"analyze",requestId:molecule.id,molecule,engineSHA256:engineSHA,engineURL:"blob:https://namelecule.invalid/pinned"}});assert.equal(reply.type,"result",JSON.stringify(reply));analysisCache.set(key,copy(reply.result));return copy(reply.result);}
const catalogs={legacy:JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures.json"))),enriched:JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures-v2.json")))};
const inputs=Object.fromEntries(Object.entries(catalogs).map(([id,catalog])=>[id,{catalog,analyses:catalog.molecules.map(analyze)}]));
const baseRecipe=setId=>({version:2,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:catalogs.enriched.revision,engineSHA256:engineSHA,policyVersion:levels.policyVersion,allowedLevels:setId==="alkanes-unbranched"?[1]:[1,2,3],requiredLevels:setId==="alkanes-unbranched"?[1]:[1,2]});
const legacyRecipe=setId=>({version:1,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:catalogs.legacy.revision,engineSHA256:engineSHA});
const games=["repair","builder","puzzle","detective"],groups=[],failures=[],stats={canonicalTriples:0,rawAnswers:0,contextTamperCases:0,legacyMigrations:0,readinessChecks:0};
function harness({archived=false,withLevels=true}={}){
  const adapters={},doc={baseURI:"https://namelecule.invalid/",currentScript:{src:"https://namelecule.invalid/js/namelecule-game-choice-checkpoint.js"}};
  const globals={console,URL,TextEncoder,TextDecoder,AbortController,Uint32Array,Uint8Array,crypto:crypto.webcrypto,setTimeout,clearTimeout,document:doc,
    NameleculeRepairGenerator:generator,NameleculeRepairEngine:roundEngine,NameleculeNameBuilderEngine:builder,NameleculeMolecularPuzzleEngine:puzzle,NameleculeMolecularDetectiveEngine:detective,NameleculeChemistryClient:{analyze:async molecule=>analyze(molecule)},
    NameleculeQuizCheckpoints:{registerType:(name,adapter)=>adapters[name]=adapter},fetch:async url=>{const bytes=fs.readFileSync(path.join(root,new URL(url).pathname.slice(1)));return{ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};}};
  if(withLevels)globals.NameleculeGameLevels=levels;
  const scope=vm.createContext(globals),prefix=archived?"docs/checks/game-levels-alkanes-implementation-20261116/before/":"";
  vm.runInContext(fs.readFileSync(path.join(root,prefix+"js/namelecule-generated-repair-checkpoint.js"),"utf8"),scope);
  vm.runInContext(fs.readFileSync(path.join(root,prefix+"js/namelecule-molecular-detective-lesson.js"),"utf8"),scope);
  const source=fs.readFileSync(path.join(root,prefix+"js/namelecule-game-choice-checkpoint.js"),"utf8"),marker='  global.NameleculeQuizCheckpoints.registerType("alkane-game-choice-set",';assert.ok(source.includes(marker));
  const hook='  global.__compositeTest = {builderSet,puzzleSet,restoreBuilder,restorePuzzle,restoreComposite,restoreGame,loadInput'+(archived?'':',canonicalFor,restoreLevels,prepareLevels,newLevelAttempt')+'};\n';
  vm.runInContext(source.replace(marker,hook+marker),scope);
  return{scope,adapter:adapters["alkane-game-choice-set"],provider:scope.NameleculeGeneratedRepairCheckpoint,lesson:scope.NameleculeMolecularDetectiveLesson,x:scope.__compositeTest};
}
function entrySet(h,recipe,context,game){const round=recipe.version===1?recipe:h.provider.roundRecipe(recipe,context),input=inputs[context.source];
  if(game==="repair"){const view=context.source==="legacy"?input:levels.createGenerationInput(input,context.level);const setId=context.source==="legacy"?round.setId:context.level===1?"alkanes-unbranched":"alkanes-branched";return generator.createGame(view.catalog,view.analyses,{seed:context.seed,difficulty:"basic"}).sets.find(set=>set.id===setId);}
  if(game==="builder")return h.x.builderSet(round,context.seed,false);
  if(game==="puzzle")return h.x.puzzleSet(round,context.seed,false);
  return h.lesson.getSet(round,context.seed,input,false);
}
function correctRaw(game,entry){stats.rawAnswers++;
  if(game==="repair"){const raw={selectedPartId:entry.kind==="replace"?entry.targetPartId:entry.movablePartIds[0],selectedValue:entry.kind==="replace"?entry.correctValue:null,order:entry.kind==="order"?entry.correctOrder.slice():[],choiceOrder:entry.kind==="replace"?entry.choices.map((_,index)=>index):[],attempts:1,selectionMisses:0,submitted:true,solved:true};assert.equal(roundEngine.evaluateRepair(entry,raw).kind,"correct");return raw;}
  if(game==="builder"){const used=new Set(),answer=entry.round.pieces.map(piece=>{const tile=entry.bank.find(tile=>!used.has(tile.id)&&tile.text===piece.text);assert.ok(tile);used.add(tile.id);return tile.id;});assert.equal(builder.evaluate(entry.round,answer.map(id=>entry.bank.find(tile=>tile.id===id))).correct,true);return{answer,selected:null,attempts:1,submitted:true,solved:false};}
  if(game==="puzzle"){const graph={nodes:entry.target.nodes.map((node,index)=>({...node,x:60+index*35,y:150})),bonds:copy(entry.target.bonds)};assert.equal(puzzle.grade(graph,entry.target).correct,true);return{graph,attempts:1,submitted:true,solved:false};}
  const accepted=entry.mission.accepted[0].slice();return{atoms:entry.mission.kind==="atoms"?accepted:[],bonds:entry.mission.kind==="bonds"?accepted:[],attempts:1,submitted:true,solved:false};
}
function attempt(h,recipe,game,level,seed,count=3,source="enriched"){
  const context=levels.makeContext({source,level:source==="legacy"?null:level,seed}),set=entrySet(h,recipe,context,game);assert.ok(set&&set.rounds.length===3);
  const states=set.rounds.map((entry,index)=>{const raw=correctRaw(game,entry);if(index>=count){raw.attempts=0;raw.submitted=false;raw.solved=true;}return raw;});
  return{context,progress:{version:1,seed,currentRound:Math.min(count,2),states,solved:true}};
}
function levelState(game=null,level=null){return{version:2,policyVersion:levels.policyVersion,selected:game,selectedLevel:level,activeLevels:game?{[game]:level}:{},games:Object.fromEntries(games.map(game=>[game,{}])),receipts:{},legacyEarned:null,solved:true,resetOnSelect:false};}
async function settle(h,recipe,state,practice=false){let current=state;for(let pass=0;pass<4;pass++){const pending=h.adapter.prepare(recipe,current);if(!pending)return(practice?h.adapter.restorePractice:h.adapter.restore)(recipe,current);current=await pending;}throw new Error("prepare did not reach synchronous null within four rounds");}
async function warm(h,recipe){await h.x.loadInput(undefined,recipe);}
async function test(name,fn){try{await fn();groups.push({name,passed:true});}catch(error){const failure={name,passed:false,error:error.stack||String(error)};groups.push(failure);failures.push(failure);console.error(name+"\n"+failure.error);fs.writeFileSync(path.join(output,"failures.json"),JSON.stringify({recordedUTC:new Date().toISOString(),cuts,failures},null,2)+"\n");}}
(async()=>{
await test("all four games and all three levels regrade three distinct actual canonical molecules",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);
  for(const game of games)for(const level of [1,2,3]){const state=levelState(game,level),value=attempt(h,recipe,game,level,"100"+level);state.games[game][level]=value;
    const set=entrySet(h,recipe,value.context,game),ids=set.rounds.map(entry=>game==="repair"?entry.moleculeId:game==="builder"?entry.round.moleculeId:game==="puzzle"?entry.moleculeId:entry.snapshot.moleculeId);
    assert.equal(new Set(ids).size,3);ids.forEach(id=>assert.equal(levels.levelFor(id),level));const restored=await settle(h,recipe,state);assert.equal(restored.games[game][level].progress.solved,true);assert.equal(restored.receipts[level].game,game);assert.equal(restored.solved,false);stats.canonicalTriples++;}
});
await test("second gate requires both levels1/2; different games can earn distinct complete receipts",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);
  const first=attempt(h,recipe,"builder",1,"201"),second=attempt(h,recipe,"puzzle",2,"202"),third=attempt(h,recipe,"detective",3,"203");
  for(const levelsPresent of [[3],[1,3],[2],[1]]){const state=levelState();for(const level of levelsPresent){const game=level===1?"builder":level===2?"puzzle":"detective";state.games[game][level]=copy({1:first,2:second,3:third}[level]);}const restored=await settle(h,recipe,state);assert.equal(restored.solved,false);}
  const state=levelState("puzzle",2);state.games.builder[1]=first;state.games.puzzle[2]=second;const restored=await settle(h,recipe,state);assert.equal(restored.solved,true);assert.equal(restored.receipts[1].game,"builder");assert.equal(restored.receipts[2].game,"puzzle");assert.equal(Object.hasOwn(restored.receipts,3),false);
  const reverse=levelState("puzzle",2);reverse.games.puzzle[2]=copy(second);const afterTwo=await settle(h,recipe,reverse);assert.equal(afterTwo.solved,false);assert.equal(afterTwo.receipts[2].game,"puzzle");afterTwo.games.builder[1]=copy(first);afterTwo.selected="builder";afterTwo.selectedLevel=1;assert.equal((await settle(h,recipe,afterTwo)).solved,true);
  const gate4=baseRecipe("alkanes-unbranched"),only=levelState("builder",1);only.games.builder[1]=attempt(h,gate4,"builder",1,"204");assert.equal((await settle(h,gate4,only)).solved,true);
});
await test("partial work and mixed game/seed answers cannot combine into a level receipt",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);const state=levelState("builder",1);
  state.games.builder[1]=attempt(h,recipe,"builder",1,"301",2);state.games.puzzle[1]=attempt(h,recipe,"puzzle",1,"302",2);state.games.detective[2]=attempt(h,recipe,"detective",2,"303",2);
  assert.equal((await settle(h,recipe,state)).solved,false);assert.equal(Object.keys((await settle(h,recipe,state)).receipts).length,0);
  const a=attempt(h,recipe,"builder",1,"304"),b=attempt(h,recipe,"builder",1,"305");a.progress.states[1]=b.progress.states[1];const mixed=levelState("builder",1);mixed.games.builder[1]=a;const restored=await settle(h,recipe,mixed);assert.equal(restored.games.builder[1].progress.solved,false);assert.equal(Object.hasOwn(restored.receipts,1),false);
});
await test("first winning receipts survive active replacement, new practice and optional-level work",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);const state=levelState("builder",1);state.games.builder[1]=attempt(h,recipe,"builder",1,"401");state.games.puzzle[2]=attempt(h,recipe,"puzzle",2,"402");
  const earned=await settle(h,recipe,state),receipt=JSON.stringify(earned.receipts);assert.equal(earned.solved,true);
  earned.games.builder[1]=attempt(h,recipe,"builder",1,"403",1);const restored=await settle(h,recipe,earned);assert.equal(restored.solved,true);assert.equal(JSON.stringify(restored.receipts),receipt);
  const practice=h.adapter.createPractice(recipe,restored,{game:"builder"});assert.notEqual(practice.games.builder[1].context.seed,"403");assert.equal(practice.solved,true);assert.equal(JSON.stringify(practice.receipts),receipt);
  practice.selected="detective";practice.selectedLevel=3;practice.games.detective[3]=attempt(h,recipe,"detective",3,"404");const optional=await settle(h,recipe,practice,true);assert.equal(optional.solved,true);assert.equal(optional.receipts[1].attempt.context.seed,"401");assert.equal(optional.receipts[2].attempt.context.seed,"402");
});
await test("strict saved contexts reject every unknown/missing identity and incompatible slot",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);const original=levelState("builder",1);original.games.builder[1]=attempt(h,recipe,"builder",1,"501");
  for(const field of Object.keys(original.games.builder[1].context)){const bad=copy(original);bad.games.builder[1].context[field]="unknown";assert.throws(()=>h.adapter.restore(recipe,bad));stats.contextTamperCases++;}
  for(const change of [v=>delete v.games.builder[1].context.policyVersion,v=>v.games.builder[1].context.extra=true,v=>v.games.builder[1].progress.seed="different",v=>v.games.builder[2]=v.games.builder[1],v=>v.policyVersion="unknown",v=>v.version=3]){const bad=copy(original);change(bad);assert.throws(()=>h.adapter.restore(recipe,bad));stats.contextTamperCases++;}
  assert.equal(h.adapter.restore(recipe,copy(original)).games.builder[1].context.seed,"501");
});
await test("same seed at different levels preserves separate contexts, rounds and caches",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);const state=levelState("builder",2);
  state.games.builder[1]=attempt(h,recipe,"builder",1,"600");state.games.builder[2]=attempt(h,recipe,"builder",2,"600");const restored=await settle(h,recipe,state);assert.equal(restored.solved,true);assert.notEqual(levels.contextKey(restored.games.builder[1].context),levels.contextKey(restored.games.builder[2].context));
  const mixed=copy(state);mixed.games.builder[2].progress=copy(mixed.games.builder[1].progress);const rejected=await settle(h,recipe,mixed);assert.equal(rejected.games.builder[2].progress.solved,false);assert.equal(rejected.solved,false);
});
await test("forged solved flags with empty or invalid raw answers award no receipt in any game",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);
  for(const game of games){const state=levelState(game,1),value=attempt(h,recipe,game,1,"650");
    value.progress.states.forEach(raw=>{raw.solved=true;if(game==="repair"){raw.selectedPartId=null;raw.selectedValue=null;}else if(game==="builder")raw.answer=[];else if(game==="puzzle")raw.graph={nodes:[],bonds:[]};else{raw.atoms=[];raw.bonds=[];}});
    state.games[game][1]=value;const restored=await settle(h,recipe,state);assert.equal(restored.solved,false);assert.equal(Object.keys(restored.receipts).length,0);assert.equal(restored.games[game][1].progress.solved,false);}
});
await test("small optional caches do not evict required receipts during repeated in-level practice",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched");await warm(h,recipe);const initial=levelState("builder",1);initial.games.builder[1]=attempt(h,recipe,"builder",1,"661");initial.games.puzzle[2]=attempt(h,recipe,"puzzle",2,"662");let state=await settle(h,recipe,initial),receipts=JSON.stringify(state.receipts);
  for(let index=0;index<12;index++){const game=games[index%games.length];state.selected=game;state.selectedLevel=3;state.games[game][3]=attempt(h,recipe,game,3,String(670+index),1);state=h.adapter.restorePractice(recipe,state);state=h.adapter.createPractice(recipe,state,{game});assert.equal(state.solved,true);assert.equal(JSON.stringify(state.receipts),receipts);}
});
await test("legacy8 partial/earned attempts remain their original contract for all four games",async()=>{
  const h=harness(),old=harness({archived:true,withLevels:false}),recipe=baseRecipe("alkanes-branched"),legacy=legacyRecipe(recipe.setId);await warm(h,legacy);await warm(old,legacy);
  for(const game of games)for(const count of [2,3]){const context=levels.makeContext({source:"legacy",level:null,seed:"70"+count}),value=attempt(h,recipe,game,null,context.seed,count,"legacy");
    const raw={version:1,selected:game,games:{[game]:copy(value.progress)},earned:count===3?{game,evidence:copy(value.progress)}:null,solved:true};
    await old.adapter.prepare(legacy,raw);const prior=old.adapter.restore(legacy,raw),current=await settle(h,recipe,raw);assert.equal(current.games[game].legacy.context.policyVersion,"legacy-8-v1");
    const progress=copy(current.games[game].legacy.progress),expected=copy(prior.games[game]);assert.equal(JSON.stringify(progress),JSON.stringify(expected));assert.equal(current.solved,count===3);assert.equal(current.selectedLevel,"legacy");if(count===3){assert.equal(current.legacyEarned.game,game);assert.equal(Object.keys(current.receipts).length,0);}stats.legacyMigrations++;}
});
await test("cold preparation resolves to synchronous warm null, including cache-churn recovery",async()=>{
  const h=harness(),recipe=baseRecipe("alkanes-branched"),warmHarness=harness();await warm(warmHarness,recipe);const state=levelState("repair",1);state.games.repair[1]=attempt(warmHarness,recipe,"repair",1,"801");state.games.builder[2]=attempt(warmHarness,recipe,"builder",2,"802");
  const earnedFixture=await settle(warmHarness,recipe,state);assert.equal(earnedFixture.solved,true);const pending=h.adapter.prepare(recipe,earnedFixture);assert.ok(pending&&typeof pending.then==="function");let ready=await pending;ready=await settle(h,recipe,ready);assert.equal(ready.solved,true);for(let i=0;i<4;i++){assert.equal(h.adapter.prepare(recipe,ready),null);stats.readinessChecks++;}
  const receipt=copy(ready.receipts),round=h.provider.roundRecipe(recipe,ready.games.repair[1].context);
  for(let i=0;i<35;i++)await h.provider.adapter.prepare(round,{version:1,seed:String(810+i),currentRound:0,states:[null,null,null],solved:false});
  ready=await settle(h,recipe,ready);assert.equal(ready.solved,true);assert.equal(JSON.stringify(ready.receipts),JSON.stringify(receipt));assert.equal(h.adapter.prepare(recipe,ready),null);stats.readinessChecks++;
});
await test("migration recognizes exact current four-game and older three-game records, reset wins",async()=>{
  const h=harness(),scenario=JSON.parse(fs.readFileSync(path.join(root,"scenarios/alkanes-user-3.scenario.json"))),four=JSON.parse(fs.readFileSync(path.join(root,"docs/checks/game-levels-alkanes-implementation-20261116/before/scenarios/alkanes-user-3.scenario.json"))),three=JSON.parse(fs.readFileSync(path.join(root,"docs/checks/four-game-integration-20261116/before/scenarios/alkanes-user-3.scenario.json")));
  const record={states:{3:{version:1,selected:"builder",games:{builder:{version:1,seed:"99",states:[null,null,null]}}}},practices:{10:{version:1,selected:"puzzle",games:{puzzle:{version:1,seed:"98",states:[null,null,null]}}}}};
  for(const older of [four,three]){const calls=[],result=h.adapter.migrateRecord(scenario,{read:requested=>{calls.push(sha(JSON.stringify(requested)));return JSON.stringify(requested)===JSON.stringify(older)?copy(record):null;}});assert.ok(result,"exact archived record not found");assert.deepEqual(copy(result),record);assert.ok(calls.length);}
  const reset={states:{3:{}},practices:{}};const result=h.adapter.migrateRecord(scenario,{read:requested=>JSON.stringify(requested)===JSON.stringify(four)?copy(reset):JSON.stringify(requested)===JSON.stringify(three)?copy(record):null});assert.deepEqual(copy(result),reset);
  const changed=copy(scenario);changed.steps[5].note=(changed.steps[5].note||"")+"unrelated change";assert.equal(h.adapter.migrateRecord(changed,{read:requested=>JSON.stringify(requested)===JSON.stringify(four)?copy(record):null}),null);
  const workshop=JSON.parse(fs.readFileSync(path.join(root,"docs/checks/alkanes-game-choice-20261111/before/scenarios/alkanes-user-3.scenario.json"))),oldRecipe=baseRecipe("alkanes-branched"),value=attempt(h,oldRecipe,"repair",null,"905",3,"legacy");
  const oldest={states:{10:copy(value.progress)},practices:{}};const migrated=h.adapter.migrateRecord(scenario,{read:requested=>JSON.stringify(requested)===JSON.stringify(workshop)?copy(oldest):null});assert.ok(migrated);assert.equal(migrated.states[10].selected,"repair");assert.deepEqual(copy(migrated.states[10].legacyRepair),value.progress);assert.equal((await settle(h,oldRecipe,migrated.states[10])).solved,true);
});
const after=Object.fromEntries(runtime.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))]));
const report={recordedUTC:new Date().toISOString(),role:"Developer MEMORY evidence",passed:failures.length===0,groups,stats,cuts,sourceStable:JSON.stringify(cuts)===JSON.stringify(after),after,
  proof:"Actual registered Composite/provider adapters and pinned Worker/real pure game engines; private helpers exposed only by in-memory VM source instrumentation",
  limits:["Raw correct answers constructed for memory tests; no UI solutions or browser execution","No child/rendering/viewer/desktop export checks","Tests do not replace independent review"],coreChanged:false,commit:false,publication:false};
fs.writeFileSync(path.join(output,"results.json"),JSON.stringify(report,null,2)+"\n");console.log(JSON.stringify(report,null,2));if(failures.length||!report.sourceStable)process.exitCode=1;
})().catch(error=>{const report={recordedUTC:new Date().toISOString(),cuts,fatal:error.stack||String(error)};fs.writeFileSync(path.join(output,"fatal.json"),JSON.stringify(report,null,2)+"\n");console.error(error);process.exitCode=1;});
