"use strict";
// Developer canonical/message contract checks. No browser or child rendering.
const fs=require("fs"),path=require("path"),vm=require("vm"),crypto=require("crypto"),assert=require("assert/strict");
const root=path.resolve(__dirname,"../../../.."),levels=require(path.join(root,"js/namelecule-game-levels.js")),engine=require(path.join(root,"js/namelecule-molecular-detective-engine.js"));
const currentFile="js/namelecule-molecular-detective-lesson.js",beforeFile="docs/checks/game-levels-alkanes-implementation-20261116/before/js/namelecule-molecular-detective-lesson.js";
const code=fs.readFileSync(path.join(root,currentFile),"utf8"),oldCode=fs.readFileSync(path.join(root,beforeFile),"utf8"),providerCode=fs.readFileSync(path.join(root,"js/namelecule-generated-repair-checkpoint.js"),"utf8");
const copy=value=>JSON.parse(JSON.stringify(value)),sha=value=>crypto.createHash("sha256").update(value).digest("hex");
const engineSHA="3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306",coreCode=fs.readFileSync(path.join(root,"js/chemistry-engines",engineSHA+".js"),"utf8");assert.equal(sha(coreCode),engineSHA);
const workerCode=fs.readFileSync(path.join(root,"js/namelecule-chemistry-worker.js"),"utf8");
function analyze(molecule){let response;const context=vm.createContext({URL,console,self:{location:{origin:"https://namelecule.invalid"},postMessage:value=>response=value,close(){}}});
  context.importScripts=()=>vm.runInContext(coreCode,context);vm.runInContext(workerCode,context);
  context.self.onmessage({data:{type:"analyze",requestId:molecule.id,molecule,engineSHA256:engineSHA,engineURL:"blob:https://namelecule.invalid/pinned"}});assert.equal(response.type,"result",JSON.stringify(response));return copy(response.result);}
const catalog14=JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures-v2.json"))),input14={catalog:catalog14,analyses:catalog14.molecules.map(analyze)};
const catalog8=JSON.parse(fs.readFileSync(path.join(root,"games/data/alkane-structures.json"))),input8={catalog:catalog8,analyses:catalog8.molecules.map(analyze)};
const recipe1=setId=>({version:1,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:catalog8.revision,engineSHA256:engineSHA});
const recipe2=(level,setId="alkanes-branched")=>({version:2,setId,difficulty:"basic",roundCount:3,generatorVersion:"1.0.0",catalogRevision:catalog14.revision,engineSHA256:engineSHA,policyVersion:levels.policyVersion,allowedLevels:setId==="alkanes-unbranched"?[1]:[1,2,3],requiredLevels:setId==="alkanes-unbranched"?[1]:[1,2],level});
class Element{
  constructor(tag,doc){this.tagName=tag;this.ownerDocument=doc;this.childNodes=[];this.attributes={};this.parentNode=null;this.handlers={};this.style={};this.isConnected=true;this._text="";if(tag==="iframe")this.contentWindow={sent:[],postMessage(value,origin){this.sent.push({value,origin});}};}
  set textContent(value){this._text=String(value);this.childNodes=[];}get textContent(){return this._text+this.childNodes.map(child=>child.textContent).join("");}
  append(...children){children.forEach(child=>{child.parentNode=this;this.childNodes.push(child);});}
  replaceChildren(...children){this.childNodes.forEach(child=>{child.parentNode=null;});this.childNodes=[];this.append(...children);}
  setAttribute(key,value){this.attributes[key]=value;}removeAttribute(key){delete this.attributes[key];}addEventListener(key,handler){this.handlers[key]=handler;}
  remove(){if(this.parentNode){this.parentNode.childNodes.splice(this.parentNode.childNodes.indexOf(this),1);this.parentNode=null;}this.isConnected=false;}
  after(child){const index=this.parentNode.childNodes.indexOf(this);this.parentNode.childNodes.splice(index+1,0,child);child.parentNode=this.parentNode;}
  focus(){}click(){if(this.handlers.click)this.handlers.click();}
}
function harness(source=code,withLevels=true){const listeners=new Map(),doc={baseURI:"https://namelecule.invalid/",currentScript:{src:"https://namelecule.invalid/js/namelecule-generated-repair-checkpoint.js"}};doc.createElement=tag=>new Element(tag,doc);
  const globals={console,URL,Uint32Array,crypto:crypto.webcrypto,location:{origin:"https://namelecule.invalid"},document:doc,setTimeout,clearTimeout,
    NameleculeMolecularDetectiveEngine:engine,addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:(name,fn)=>{if(listeners.get(name)===fn)listeners.delete(name);}};
  if(withLevels)globals.NameleculeGameLevels=levels;const context=vm.createContext(globals);vm.runInContext(providerCode,context);vm.runInContext(source,context);
  return{lesson:context.NameleculeMolecularDetectiveLesson,host:new Element("div",doc),listeners,send:(frame,data,origin=globals.location.origin,sourceWindow=frame.contentWindow)=>{const fn=listeners.get("message");if(fn)fn({data,source:sourceWindow,origin});}};
}
function find(node,predicate){if(predicate(node))return node;for(const child of node.childNodes){const hit=find(child,predicate);if(hit)return hit;}return null;}
function selection(entry,accepted=entry.mission.accepted[0]){return{atoms:entry.mission.kind==="atoms"?accepted.slice():[],bonds:entry.mission.kind==="bonds"?accepted.slice():[],attempts:1,submitted:true,solved:false};}
function saved(set,seed,all=false){return{version:1,seed,currentRound:2,states:set.rounds.map((entry,index)=>index<2||all?selection(entry):{atoms:[],bonds:[],attempts:0,submitted:false,solved:true}),solved:true};}
function connect(h,frame){const session=new URL(frame.src).searchParams.get("lessonSession"),base={channel:"namelecule-detective-lesson-v1",session};h.send(frame,{...base,type:"ready"});assert.equal(frame.contentWindow.sent.length,1);return{base,load:frame.contentWindow.sent[0].value};}
function echo(base,load,type,stateRevision=0,state=load.initialState){return{...base,type,requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,missionId:load.missionId,...("context"in load?{context:copy(load.context)}:{}),stateRevision,snapshot:copy(load.snapshot),state:copy(state)};}
const groups=[],counters={legacySets:0,newSets:0,acceptedVariants:0,wireIgnored:0};function test(name,fn){fn();groups.push(name);}
test("legacy set/mission assignment and partial/earned raw states exactly match archived source without levels",()=>{
  const old=harness(oldCode,false),now=harness(code,false);
  for(const setId of ["alkanes-unbranched","alkanes-branched"])for(const seed of ["1","0034","999"]){const recipe=recipe1(setId),a=old.lesson.getSet(recipe,seed,input8,false),b=now.lesson.getSet(recipe,seed,input8,false);assert.equal(JSON.stringify(a),JSON.stringify(b));counters.legacySets++;
    for(const all of [false,true]){const raw=saved(a,seed,all);assert.equal(JSON.stringify(old.lesson.restore(recipe,raw,input8,false)),JSON.stringify(now.lesson.restore(recipe,raw,input8,false)));}}
});
test("all14 canonical source graphs retain raw indexes and valid nonempty missions",()=>{
  for(const molecule of catalog14.molecules){const analysis=input14.analyses.find(row=>row.moleculeId===molecule.id),snapshot=engine.canonicalSnapshot(molecule,analysis);assert.equal(engine.validateSnapshot(snapshot).valid,true);assert.equal(snapshot.sourceMOL,molecule.mol);assert.ok(engine.missions(snapshot).length);
    if(["propane","butane"].includes(molecule.id)){assert.equal(snapshot.atoms[0].element,"H");assert.equal(snapshot.atoms[1].element,"C");}}
});
test("new levels choose three distinct band molecules and compatible mission families",()=>{
  const h=harness(),source=JSON.stringify(input14);
  for(const level of [1,2,3])for(const seed of ["1","0034","999"]){const recipe=recipe2(level),set=h.lesson.getSet(recipe,seed,input14,false);assert.equal(new Set(set.rounds.map(row=>row.snapshot.moleculeId)).size,3);assert.equal(JSON.stringify(set),JSON.stringify(h.lesson.getSet(copy(recipe),seed,input14,false)));counters.newSets++;
    set.rounds.forEach(entry=>{assert.equal(levels.levelFor(entry.snapshot.moleculeId),level);assert.ok(level===1?["parent-chain","single-bonds"].includes(entry.mission.family):["parent-chain","branches","ethyl-branches"].includes(entry.mission.family));});}
  assert.equal(JSON.stringify(input14),source);
});
test("full14 identity is checked before returning warmed v2 cache entries",()=>{
  const h=harness(),recipe=recipe2(2);h.lesson.getSet(recipe,"123",input14,false);
  for(const change of [v=>v.catalog.revision="unknown",v=>v.catalog.engineSHA256="0".repeat(64),v=>v.catalog.catalogVersion=1,v=>v.catalog.molecules.pop(),v=>v.analyses.pop(),v=>v.analyses[0].engineSHA256="0".repeat(64),v=>v.analyses.reverse(),v=>v.catalog.molecules[0].id="unknown"]){const bad=copy(input14);change(bad);assert.throws(()=>h.lesson.getSet(recipe,"123",bad,false));}
  assert.throws(()=>h.lesson.getSet({...recipe,level:4},"123",input14,false));assert.throws(()=>h.lesson.getSet({...recipe,policyVersion:"unknown"},"123",input14,false));
});
test("parent canonical regrading accepts valid alternatives and rejects forged/invalid raw selections",()=>{
  const h=harness();for(const level of [1,2,3])for(const entry of h.lesson.getSet(recipe2(level),"21345",input14,false).rounds){
    for(const accepted of entry.mission.accepted){const raw=selection(entry,accepted.slice().reverse());assert.equal(h.lesson.snapshot(entry,raw).solved,true);counters.acceptedVariants++;}
    assert.equal(h.lesson.snapshot(entry,{atoms:[],bonds:[],attempts:1,submitted:true,solved:true}).solved,false);
    assert.equal(h.lesson.snapshot(entry,{...selection(entry),submitted:false,solved:true}).solved,false);
    assert.equal(h.lesson.snapshot(entry,{...selection(entry),atoms:[999],solved:true}).solved,false);
    const raw=selection(entry),field=entry.mission.kind==="atoms"?"atoms":"bonds";raw[field].push(raw[field][0]);assert.equal(h.lesson.snapshot(entry,raw).solved,false);
    const wrongKind=selection(entry);wrongKind[entry.mission.kind==="atoms"?"bonds":"atoms"]=[1];assert.equal(h.lesson.snapshot(entry,wrongKind).solved,false);
  }
});
test("v2 compact wire attempt has full context, rejects mismatched/late echoes and labels current aggregate gate",()=>{
  const h=harness(),recipe=recipe2(1),seed="12345678901234567890",set=h.lesson.getSet(recipe,seed,input14,false),changes=[],ready=[];let solved=0,continued=0;
  const mounted=h.lesson.mount(h.host,{round:recipe,input:input14,initialState:saved(set,seed,false),onStateChange:value=>changes.push(copy(value)),onSuccessActionsReady:value=>ready.push(value),onSolved:()=>solved++,onContinue:()=>continued++,continueLabel:()=>changes.at(-1)?.solved?"Επόμενο υποχρεωτικό επίπεδο":"waiting"},false);
  const frame=find(h.host,node=>node.tagName==="iframe"),{base,load}=connect(h,frame);assert.ok(load.attemptId.length<160);assert.match(load.attemptId,/^[a-zA-Z0-9_-]+$/);assert.deepEqual(copy(load.context),levels.makeContext({source:"enriched",level:1,seed}));assert.ok(levels.contextIds(load.context).includes(load.moleculeId));
  const entry=set.rounds[2],loaded=echo(base,load,"loaded",0,selection(entry)),before=changes.length;
  for(const change of [v=>delete v.context,v=>v.context.level=2,v=>v.context.catalogSHA256="0".repeat(64),v=>v.attemptId+="x",v=>v.moleculeId="unknown",v=>v.missionId="unknown",v=>v.requestId++,v=>v.session+="x"]){const bad=copy(loaded);change(bad);h.send(frame,bad);assert.equal(changes.length,before);counters.wireIgnored++;}
  h.send(frame,loaded,"https://other.invalid");h.send(frame,loaded,undefined,{});assert.equal(changes.length,before);counters.wireIgnored+=2;
  h.send(frame,loaded);assert.equal(changes.at(-1).solved,true);assert.equal(solved,1);assert.equal(ready.at(-1),true);
  const next=find(h.host,node=>node.tagName==="button"&&node.attributes["data-checkpoint-continue"]!==undefined);assert.equal(next.textContent,"Επόμενο υποχρεωτικό επίπεδο");next.click();assert.equal(continued,1);
  const count=changes.length;h.send(frame,echo(base,load,"state",0,selection(entry)));assert.equal(changes.length,count);counters.wireIgnored++;
  const wrong=echo(base,load,"state",1,{atoms:[],bonds:[],attempts:1,submitted:true,solved:true});h.send(frame,wrong);assert.equal(changes.at(-1).solved,false);assert.equal(ready.at(-1),false);
  mounted.destroy();assert.equal(h.listeners.has("message"),false);assert.equal(h.host.childNodes.length,0);h.send(frame,echo(base,load,"state",2,selection(entry)));assert.equal(changes.length,count+1);
});
test("legacy load messages omit context, remain compatible and reject forged solved flags",()=>{
  const h=harness(code,false),recipe=recipe1("alkanes-branched"),seed="123",set=h.lesson.getSet(recipe,seed,input8,false),states=[];
  const mounted=h.lesson.mount(h.host,{round:recipe,input:input8,initialState:saved(set,seed,false),onStateChange:value=>states.push(copy(value))},false);
  const frame=find(h.host,node=>node.tagName==="iframe"),{base,load}=connect(h,frame);assert.equal(Object.hasOwn(load,"context"),false);assert.equal(load.attemptId,"detective-alkanes-branched-123");
  h.send(frame,echo(base,load,"loaded",0,{atoms:[],bonds:[],attempts:1,submitted:true,solved:true}));assert.equal(states.at(-1).solved,false);mounted.destroy();
});
const files=["js/namelecule-game-levels.js","css/namelecule-game-levels.css","js/namelecule-generated-repair-checkpoint.js",currentFile];
const report={recordedUTC:new Date().toISOString(),role:"Developer evidence",passed:true,groups,counters,beforeDetectiveLessonSHA256:sha(oldCode),files:Object.fromEntries(files.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))])),
  suppliedDependencies:{detectiveEngineSHA256:sha(fs.readFileSync(path.join(root,"js/namelecule-molecular-detective-engine.js"))),pinnedEngineSHA256:engineSHA},
  limits:["No browser or actual native child/viewer rendering","Parent aggregate receipt policy is supplied through callback contract only","Full14 input bytes are verified upstream; lesson shape/identity guards are not SHA verification"],coreChanged:false,commit:false,publication:false};
fs.writeFileSync(path.join(__dirname,"detective-lesson-results.json"),JSON.stringify(report,null,2)+"\n");console.log(JSON.stringify(report,null,2));
