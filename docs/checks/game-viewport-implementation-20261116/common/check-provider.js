"use strict";
// Developer checks against actual pinned catalog/worker/generator/round engine.
// Provider DOM is a minimal contract double; no browser QA is represented.
const fs=require("fs"),path=require("path"),vm=require("vm"),assert=require("assert/strict"),crypto=require("crypto");
const root=path.resolve(__dirname,"../../../.."),levels=require(path.join(root,"js/namelecule-game-levels.js"));
const generator=require(path.join(root,"js/namelecule-repair-generator.js"));
const engine=require(path.join(root,"docs/checks/game-levels-alkanes-implementation-20261116/before/js/namelecule-game-repair.js"));
const beforeFile="docs/checks/game-levels-alkanes-implementation-20261116/before/js/namelecule-generated-repair-checkpoint.js";
const currentFile="js/namelecule-generated-repair-checkpoint.js",beforeCode=fs.readFileSync(path.join(root,beforeFile),"utf8"),currentCode=fs.readFileSync(path.join(root,currentFile),"utf8");
const copy=value=>JSON.parse(JSON.stringify(value)),sha=bytes=>crypto.createHash("sha256").update(bytes).digest("hex");
const engineSHA="3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306";
const engineCode=fs.readFileSync(path.join(root,"js/chemistry-engines",engineSHA+".js"),"utf8");
assert.equal(sha(engineCode),engineSHA);
const workerCode=fs.readFileSync(path.join(root,"js/namelecule-chemistry-worker.js"),"utf8"),analysisCache=new Map();
function analyze(molecule){
  const key=sha(molecule.mol);if(analysisCache.has(key))return copy(analysisCache.get(key));
  let reply;const context=vm.createContext({URL,console,self:{location:{origin:"https://namelecule.invalid"},postMessage:value=>reply=value,close:()=>{}}});
  context.importScripts=()=>vm.runInContext(engineCode,context);vm.runInContext(workerCode,context);
  context.self.onmessage({data:{type:"analyze",requestId:molecule.id,molecule,engineSHA256:engineSHA,engineURL:"blob:https://namelecule.invalid/pinned"}});
  assert.equal(reply.type,"result",JSON.stringify(reply));analysisCache.set(key,copy(reply.result));return copy(reply.result);
}
const source14=JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures-v2.json"))),input14={catalog:source14,analyses:source14.molecules.map(analyze)};
const source8=JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures.json"))),input8={catalog:source8,analyses:source8.molecules.map(analyze)};
class Element{
  constructor(tag,doc){this.tagName=tag;this.ownerDocument=doc;this.childNodes=[];this.attributes={};this.parentNode=null;this.isConnected=true;this.handlers={};this._text="";}
  set textContent(value){this._text=String(value);this.childNodes=[];}get textContent(){return this._text+this.childNodes.map(row=>row.textContent).join("");}
  replaceChildren(...children){this.childNodes=children;children.forEach(child=>child.parentNode=this);}
  setAttribute(key,value){this.attributes[key]=value;}removeAttribute(key){delete this.attributes[key];}
  addEventListener(key,value){this.handlers[key]=value;}querySelector(){return null;}
}
function harness(code,{withLevels=true,fetchOverride}={}){
  const captured={mounts:[],fetches:[],analysisCalls:0,registered:null},doc={baseURI:"https://namelecule.invalid/",currentScript:{src:"https://namelecule.invalid/js/namelecule-generated-repair-checkpoint.js"}};
  doc.createElement=tag=>new Element(tag,doc);
  const globals={console,URL,TextEncoder,TextDecoder,AbortController,Uint32Array,Uint8Array,crypto:crypto.webcrypto,setTimeout,clearTimeout,document:doc,
    NameleculeRepairGenerator:generator,NameleculeRepairEngine:engine,NameleculeChemistryClient:{analyze:async molecule=>{captured.analysisCalls++;return analyze(molecule);}},
    NameleculeRepairGame:{presentationForRound:round=>({round}),mountRound:(host,options)=>{captured.mounts.push(options);return{destroy(){}};}},
    NameleculeQuizCheckpoints:{registerType:(name,adapter)=>captured.registered={name,adapter}},
    fetch:async(url,options)=>{captured.fetches.push({url,options});if(fetchOverride)return fetchOverride(url,options);
      const bytes=fs.readFileSync(path.join(root,new URL(url).pathname.slice(1)));return{ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};}
  };
  if(withLevels)globals.NameleculeGameLevels=levels;
  const context=vm.createContext(globals);vm.runInContext(code,context);
  return{provider:context.NameleculeGeneratedRepairCheckpoint,host:new Element("div",doc),captured};
}
const legacyRecipe=setId=>({version:1,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:source8.revision,engineSHA256:engineSHA});
const newRecipe=setId=>({version:2,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:source14.revision,engineSHA256:engineSHA,
  policyVersion:levels.policyVersion,allowedLevels:setId==="alkanes-unbranched"?[1]:[1,2,3],requiredLevels:setId==="alkanes-unbranched"?[1]:[1,2]});
function correctState(round,solved=true){return{selectedPartId:round.kind==="replace"?round.targetPartId:round.movablePartIds[0],selectedValue:round.kind==="replace"?round.correctValue:null,
  order:round.kind==="order"?round.correctOrder.slice():[],choiceOrder:round.kind==="replace"?round.choices.map((_,index)=>index):[],attempts:1,selectionMisses:0,submitted:solved,solved};}
function previousFor(set,seed,fullySolved){return{version:1,seed,currentRound:2,states:set.rounds.map((round,index)=>correctState(round,fullySolved||index<2)),solved:true};}
async function mounted(h,recipe,previous,options={}){
  const offset=h.captured.mounts.length,mount=h.provider.adapter.mount(h.host,{round:recipe,initialState:previous,...options});
  for(let index=0;index<100&&h.captured.mounts.length===offset;index++)await new Promise(resolve=>setTimeout(resolve,1));
  assert.equal(h.captured.mounts.length,offset+1,h.host.textContent);return{mount,round:h.captured.mounts.at(-1)};
}
const groups=[];async function test(name,run){await run();groups.push(name);}
(async()=>{
await test("module registration and complete legacy v1 lifecycle work without levels global",async()=>{
  const h=harness(currentCode,{withLevels:false}),recipe=legacyRecipe("alkanes-unbranched");
  assert.equal(h.captured.registered.name,"generated-name-repair-set");assert.deepEqual(copy(h.provider.adapter.validate(recipe)),recipe);
  assert.equal(h.provider.adapter.prepare(recipe,null),null);
  const set=generator.createGame(source8,input8.analyses,{seed:"123",difficulty:"basic"}).sets[0],previous=previousFor(set,"123",true);
  const cold=h.provider.adapter.prepare(recipe,previous);assert.equal(typeof cold.then,"function");assert.equal((await cold).solved,true);
  assert.equal(h.provider.adapter.prepare(recipe,previous),null);
  const view=await mounted(h,recipe,previous);assert.deepEqual(copy(view.round.round),set.rounds[2]);assert.equal(view.round.continueLabel,"Συνεχίζω τη θεωρία");view.mount.destroy();
  assert.throws(()=>h.provider.adapter.validate(newRecipe("alkanes-branched")));
});
await test("before/current v1 generated rounds and valid partial/earned states are byte-identical",async()=>{
  const old=harness(beforeCode,{withLevels:false}),now=harness(currentCode,{withLevels:false});
  for(const setId of ["alkanes-unbranched","alkanes-branched"])for(const seed of ["23","0044"]){
    const recipe=legacyRecipe(setId),set=generator.createGame(source8,input8.analyses,{seed,difficulty:"basic"}).sets.find(row=>row.id===setId);
    for(const fullySolved of [false,true]){
      const previous=previousFor(set,seed,fullySolved);
      await old.provider.adapter.prepare(recipe,previous);await now.provider.adapter.prepare(recipe,previous);
      assert.equal(JSON.stringify(old.provider.adapter.restore(recipe,previous)),JSON.stringify(now.provider.adapter.restore(recipe,previous)));
      const a=await mounted(old,recipe,previous),b=await mounted(now,recipe,previous);
      assert.equal(JSON.stringify(a.round.round),JSON.stringify(b.round.round));assert.equal(JSON.stringify(a.round.initialState),JSON.stringify(b.round.initialState));a.mount.destroy();b.mount.destroy();
    }
  }
});
await test("v2 exact recipes and round contexts reject mismatches without legacy fallback",async()=>{
  const h=harness(currentCode),base=newRecipe("alkanes-branched"),baseText=JSON.stringify(base);
  const context=levels.makeContext({source:"enriched",level:2,seed:"123"}),recipe=h.provider.roundRecipe(base,context);
  assert.deepEqual(copy(recipe),{...base,level:2});assert.equal(JSON.stringify(base),baseText);
  const legacy=levels.makeContext({source:"legacy",level:null,seed:"123"});assert.deepEqual(copy(h.provider.roundRecipe(base,legacy)),legacyRecipe(base.setId));
  for(const change of [r=>r.extra=true,r=>r.policyVersion="bad",r=>r.allowedLevels=[2,3],r=>r.requiredLevels=[2],r=>r.level=4,r=>r.level="1",r=>r.catalogRevision=source8.revision,r=>r.version=3]){
    const bad=copy(base);change(bad);assert.throws(()=>h.provider.adapter.validate(bad));
  }
  assert.throws(()=>h.provider.roundRecipe(newRecipe("alkanes-unbranched"),context));
  assert.throws(()=>h.provider.roundRecipe(base,{...context,catalogSHA256:"0".repeat(64)}));
  assert.throws(()=>h.provider.roundRecipe({...base,level:3},context));
  assert.throws(()=>h.provider.adapter.createPractice(base,null));
  assert.throws(()=>h.provider.adapter.prepare(base,{version:1,seed:"123"}));
});
await test("v2 levels use distinct cache identities, correct effective sets and synchronous warm null",async()=>{
  const h=harness(currentCode),base=newRecipe("alkanes-branched"),seed="8877";
  for(const level of [1,2,3]){
    const context=levels.makeContext({source:"enriched",level,seed}),recipe=h.provider.roundRecipe(base,context),input=levels.createGenerationInput(input14,level);
    const set=generator.createGame(input.catalog,input.analyses,{seed,difficulty:"basic"}).sets.find(row=>row.id===(level===1?"alkanes-unbranched":"alkanes-branched"));
    const previous=previousFor(set,seed,true),cold=h.provider.adapter.prepare(recipe,previous);assert.equal(typeof cold.then,"function");assert.equal((await cold).solved,true);
    assert.equal(h.provider.adapter.prepare(recipe,previous),null);const count=h.captured.fetches.length;
    for(let index=0;index<5;index++)assert.equal(h.provider.adapter.prepare(recipe,previous),null);assert.equal(h.captured.fetches.length,count);
    const view=await mounted(h,recipe,previous);assert.deepEqual(copy(view.round.round),set.rounds[2]);assert.equal(levels.levelFor(view.round.round.moleculeId),level);view.mount.destroy();
  }
  const recipe=h.provider.roundRecipe(newRecipe("alkanes-unbranched"),levels.makeContext({source:"enriched",level:1,seed}));
  const cold=h.provider.adapter.prepare(recipe,{version:1,seed});assert.equal(typeof cold.then,"function");await cold;
  assert.equal(h.captured.fetches.length,1);assert.equal(h.captured.analysisCalls,14);
});
await test("final footer reads dynamic aggregate label after state publication",async()=>{
  const h=harness(currentCode),base=newRecipe("alkanes-branched"),seed="5566",recipe=h.provider.roundRecipe(base,levels.makeContext({source:"enriched",level:1,seed}));
  const input=levels.createGenerationInput(input14,1),set=generator.createGame(input.catalog,input.analyses,{seed,difficulty:"basic"}).sets[0];
  const previous=previousFor(set,seed,false);await h.provider.adapter.prepare(recipe,previous);
  let aggregate=false,rawSolved=0,continued=0;
  const view=await mounted(h,recipe,previous,{continueLabel:()=>aggregate?"Συνεχίζω τη θεωρία":"Επόμενο υποχρεωτικό επίπεδο",onSolved:()=>rawSolved++,onContinue:()=>continued++});
  assert.equal(view.round.continueLabel,"Επόμενο υποχρεωτικό επίπεδο");aggregate=true;assert.equal(view.round.continueLabel,"Συνεχίζω τη θεωρία");
  const solved=correctState(set.rounds[2],true);view.round.onStateChange(solved);view.round.onSolved({kind:"correct"},solved);view.round.onContinue();
  assert.equal(rawSolved,1);assert.equal(continued,1);view.mount.destroy();
});
await test("source byte mismatch fails before analysis and allows a fresh retry",async()=>{
  let invalid=true;const h=harness(currentCode,{fetchOverride:async()=>{const bytes=Buffer.from(invalid?"{}":JSON.stringify(source14,null,2)+"\n");return{ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};}});
  const recipe=h.provider.roundRecipe(newRecipe("alkanes-branched"),levels.makeContext({source:"enriched",level:2,seed:"888"}));
  await assert.rejects(h.provider.adapter.prepare(recipe,{version:1,seed:"888"}),/δομές του Συνεργείου άλλαξαν/);assert.equal(h.captured.analysisCalls,0);
  invalid=false;await h.provider.adapter.prepare(recipe,{version:1,seed:"888"});assert.equal(h.captured.fetches.length,2);assert.equal(h.captured.analysisCalls,14);
});
await test("aborted cold preparation rejects promptly and late ignored-signal fetch cannot warm caches",async()=>{
  let release;const h=harness(currentCode,{fetchOverride:()=>new Promise(resolve=>{release=()=>{const bytes=fs.readFileSync(path.join(root,"games/data/alkane-structures-v2.json"));resolve({ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)});};})});
  const recipe=h.provider.roundRecipe(newRecipe("alkanes-branched"),levels.makeContext({source:"enriched",level:2,seed:"55"}));
  const controller=new AbortController(),promise=h.provider.adapter.prepare(recipe,{version:1,seed:"55"},{signal:controller.signal});
  controller.abort();await assert.rejects(promise,error=>error.name==="AbortError");release();await new Promise(resolve=>setTimeout(resolve,5));
  assert.equal(h.captured.analysisCalls,0);const retry=h.provider.adapter.prepare(recipe,{version:1,seed:"55"});assert.equal(typeof retry.then,"function");release();await retry;
  assert.equal(h.captured.fetches.length,2);assert.equal(h.provider.adapter.prepare(recipe,{version:1,seed:"55"}),null);
});
const files=["js/namelecule-game-levels.js","css/namelecule-game-levels.css",currentFile];
const report={recordedUTC:new Date().toISOString(),role:"Developer evidence",passed:true,groups,beforeProviderSHA256:sha(beforeCode),files:Object.fromEntries(files.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))])),
  beforeVsCurrent:{recipes:2,seeds:2,statesPerRecipeSeed:2,exactRoundAndStateComparisons:8,withoutLevelsGlobal:true},
  sourceAndEngine:"Actual source8/source14 bytes, pinned worker analyses and unchanged generator/round validation; fetch is local-byte injected",
  limits:["No browser/layout/keyboard or actual rendered-footer execution","Dynamic label tested through actual provider callback/getter contract and a round UI stub","Parent aggregate receipts/migration/child message guards not exercised here"],coreChanged:false,commit:false,publication:false};
fs.writeFileSync(path.join(__dirname,"provider-results.json"),JSON.stringify(report,null,2)+"\n");console.log(JSON.stringify(report,null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
