'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const {webcrypto,createHash}=require('crypto'),R=process.cwd(),H=path.join(R,'docs/checks/four-game-integration-20261116');
const read=p=>fs.readFileSync(path.join(R,p),'utf8'),copy=x=>JSON.parse(JSON.stringify(x));
let checks=0;const records=[];function check(ok,label){assert.ok(ok,label);checks++;records.push(label);}
const worker=read('js/namelecule-chemistry-worker.js'),core=read('js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js');
function analyze(molecule){let result;const box=vm.createContext({URL});box.self={location:{origin:'http://memory.test'},postMessage:r=>result=r,close(){}};box.importScripts=()=>vm.runInContext(core,box);vm.runInContext(worker,box);box.self.onmessage({data:{type:'analyze',requestId:'probe',molecule,engineSHA256:'3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306',engineURL:'blob:http://memory.test/exact'}});assert.equal(result.type,'result');return copy(result.result);}
function setup(old=false){
 const ctx=vm.createContext({console,URL,TextEncoder,TextDecoder,AbortController,Uint8Array,crypto:webcrypto,setTimeout,clearTimeout});ctx.window=ctx;const types={},scripts=[];
 ctx.document={baseURI:'http://memory.test/',currentScript:null,getElementById:()=>null,createElement:tag=>({tag,remove(){}}),head:{append(script){scripts.push(script.src);queueMicrotask(()=>{try{load(new URL(script.src).pathname.slice(1));script.onload();}catch(e){script.onerror(e);}});}}};
 function load(p){ctx.document.currentScript={src:'http://memory.test/'+p};vm.runInContext(read(p),ctx,{filename:p});ctx.document.currentScript=null;}
 ctx.NameleculeQuizCheckpoints={registerType:(t,a)=>types[t]=a};
 ctx.fetch=async url=>({ok:true,arrayBuffer:async()=>new TextEncoder().encode(read(new URL(url).pathname.slice(1))).buffer});
 ctx.NameleculeChemistryClient={analyze:async m=>analyze(m)};
 for(const p of ['js/namelecule-game-repair.js','js/namelecule-repair-generator.js','js/namelecule-name-builder-engine.js','js/namelecule-molecular-puzzle-engine.js','js/namelecule-generated-repair-checkpoint.js'])load(p);
 const expose=text=>text.replace('  global.NameleculeQuizCheckpoints.registerType(', '  global.__choiceOracle={builderSet,puzzleSet};\n  global.NameleculeQuizCheckpoints.registerType(');
 if(old)vm.runInContext(expose(fs.readFileSync(path.join(H,'before/js/namelecule-game-choice-checkpoint.js'),'utf8')),ctx);else{ctx.document.currentScript={src:'http://memory.test/js/namelecule-game-choice-checkpoint.js'};vm.runInContext(expose(read('js/namelecule-game-choice-checkpoint.js')),ctx);ctx.document.currentScript=null;}
 return {ctx,types,scripts,load,api:types['alkane-game-choice-set'],provider:ctx.NameleculeGeneratedRepairCheckpoint};
}
(async()=>{
 const a=setup();const input=await a.provider.loadCanonicalInput();
 a.load('js/namelecule-molecular-detective-engine.js');a.load('js/namelecule-molecular-detective-lesson.js');const lesson=a.ctx.NameleculeMolecularDetectiveLesson;
 const recipe=id=>({version:1,setId:id,difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:input.catalog.revision,engineSHA256:input.catalog.engineSHA256});
 const coverage=new Set();
 for(const id of ['alkanes-unbranched','alkanes-branched'])for(const seed of ['0','1','11','999','782372','18446744073709551615']){
  const r=recipe(id),set=lesson.getSet(r,seed,input,false),set2=lesson.getSet(r,seed,input,true);
  check(JSON.stringify(set)===JSON.stringify(set2),'required/practice same deterministic seed '+id+'/'+seed);
  check(new Set(set.rounds.map(x=>x.snapshot.moleculeId)).size===3,'three distinct '+id+'/'+seed);
  const states=[];
  for(const e of set.rounds){
   coverage.add(e.snapshot.moleculeId);const valid={atoms:[],bonds:[],attempts:1,submitted:true};valid[e.mission.kind]=e.mission.accepted[0].slice();states.push(valid);
   check(lesson.snapshot(e,valid).solved,'canonical correct '+e.mission.id);
   for(const accepted of e.mission.accepted){const v=copy(valid);v[e.mission.kind]=accepted.slice().reverse();check(lesson.snapshot(e,v).solved,'equivalent reversed target '+e.mission.id);}
   check(!lesson.snapshot(e,{...valid,submitted:false,solved:true}).solved,'unsubmitted cannot earn');
   check(!lesson.snapshot(e,{...valid,attempts:0,solved:true}).solved,'no attempt cannot earn');
   const dup=copy(valid);dup[e.mission.kind].push(dup[e.mission.kind][0]);check(!lesson.snapshot(e,dup).solved,'duplicate IDs rejected');
   const unknown=copy(valid);unknown[e.mission.kind]=[999];check(!lesson.snapshot(e,unknown).solved,'unknown IDs rejected');
   check(!lesson.snapshot(e,{atoms:[],bonds:[],attempts:1,submitted:true,solved:true}).solved,'forged solved cannot earn');
   if(valid[e.mission.kind].length>1){const partial=copy(valid);partial[e.mission.kind].pop();check(!lesson.snapshot(e,partial).solved,'partial target rejected');}
   const wrong=copy(valid);wrong[e.mission.kind==='atoms'?'bonds':'atoms']=[e.mission.kind==='atoms'?e.snapshot.bonds[0].id:e.snapshot.atoms[0].id];check(!lesson.snapshot(e,wrong).solved,'mixed kinds rejected');
  }
  const raw={version:1,seed,currentRound:2,states,solved:false};const restored=lesson.restore(r,raw,input,false);check(restored.solved&&restored.currentRound===2,'triple replay independently earns');
  const broken=copy(raw);broken.states[0]={atoms:[],bonds:[],attempts:0,submitted:false,solved:true};const reset=lesson.restore(r,broken,input,false);check(!reset.solved&&reset.currentRound===0&&reset.states[2].attempts===0,'cannot skip earlier unsolved round');
  const composite=a.api.restore(r,{version:1,selected:'detective',games:{detective:raw}});const preparation=a.api.prepare(r,composite,{signal:new AbortController().signal});const prepared=preparation?await preparation:a.api.restore(r,composite);check(prepared.solved&&prepared.earned.game==='detective','composite earns Detector only after canonical prepare');check(a.api.prepare(r,prepared,{})===null,'warm Detective preparation synchronous ready boundary prevents navigation retry loop');
  const practice=a.api.createPractice(r,prepared,{game:'detective'});check(practice.selected==='detective'&&!practice.solved&&practice.games.detective.seed!==seed,'new practice independent seed/no imported unlock');
 }
 check(coverage.size===8,'seed matrix covers all eight legacy molecules');
 const cold=setup(),r=recipe('alkanes-branched'),seed='11',set=lesson.getSet(r,seed,input,false),states=set.rounds.map(e=>{const raw={atoms:[],bonds:[],attempts:1,submitted:true};raw[e.mission.kind]=e.mission.accepted[0];return raw;});
 const record={version:1,selected:'detective',games:{detective:{version:1,seed,currentRound:2,states}}};const pending=cold.api.restore(r,record);check(!pending.solved,'cold record never trusts solved before dependencies');const earned=await cold.api.prepare(r,pending,{signal:new AbortController().signal});check(earned.solved&&earned.earned.game==='detective','cold lazy restoration retains and regrades earned evidence');check(cold.scripts.length===2,'only Detector selection loads two specific dependencies');
 const newScenario=JSON.parse(read('scenarios/alkanes-user-3.scenario.json')),before=JSON.parse(fs.readFileSync(path.join(H,'before/scenarios/alkanes-user-3.scenario.json'),'utf8'));
 const rawOld={states:{3:{version:1,selected:'builder',games:{builder:{seed:'101',answer:['raw']}}},10:{version:1,selected:'puzzle',earned:{game:'repair',evidence:{seed:'102'}}}},practices:{3:{version:1,selected:'repair',games:{repair:{seed:'103'}}}}};let seen=[];
 const migrated=a.api.migrateRecord(newScenario,{read:s=>{seen.push(s);return JSON.stringify(s)===JSON.stringify(before)?copy(rawOld):null;}});check(JSON.stringify(migrated)===JSON.stringify(rawOld),'exact current three-game raw states/practices/earned copied');check(seen.length===1&&JSON.stringify(seen[0])===JSON.stringify(before),'only exact before scenario key read first');
 seen=[];const empty=a.api.migrateRecord(newScenario,{read:s=>{seen.push(s);return{states:{},practices:{}};}});check(Object.keys(empty.states).length===0&&seen.length===1,'present old reset wins over older Repair key');
 const altered=copy(newScenario);altered.steps[3].note+='x';check(a.api.migrateRecord(altered,{read:()=>{throw Error('must not scan');}})===null,'unrecognized authored note never scans storage');
 seen=[];const older=a.api.migrateRecord(newScenario,{read:s=>{seen.push(s);return seen.length===2?{states:{3:{version:1,seed:'31'}},practices:{}}:null;}});check(seen.length===2&&older.states[3].legacyRepair.seed==='31','older Repair migration retained as exact fallback');
 const original=setup(true);check(original.api.validate(r)===r&&a.api.validate(r)===r,'old recipe validates unchanged');

 for(const setId of ['alkanes-unbranched','alkanes-branched'])for(const game of ['repair','builder','puzzle']){
  const old=setup(true),cur=setup(),rec=recipe(setId),seed='113355';
  const empty={version:1,selected:game,games:{[game]:{version:1,seed,currentRound:0,states:[null,null,null]}}};
  await old.api.prepare(rec,empty,{});await cur.api.prepare(rec,empty,{});
  let states;
  if(game==='builder')states=old.ctx.__choiceOracle.builderSet(rec,seed,false).rounds.map(e=>{
   const available=e.bank.slice(),answer=e.round.pieces.map(p=>available.splice(available.findIndex(t=>t.text===p.text),1)[0].id);
   return{answer,selected:null,attempts:1,submitted:true};
  });
  else if(game==='puzzle')states=old.ctx.__choiceOracle.puzzleSet(rec,seed,false).rounds.map(e=>({graph:{nodes:e.target.nodes.map((n,i)=>({...copy(n),x:50+i*60,y:100})),bonds:copy(e.target.bonds)},attempts:1,submitted:true}));
  else{
   const g=old.ctx.NameleculeRepairGenerator.createGame(input.catalog,input.analyses,{seed,difficulty:'basic'});
   states=g.sets.find(s=>s.id===setId).rounds.map(round=>{const state=old.ctx.NameleculeRepairEngine.createRoundState(round);state.attempts=1;state.submitted=true;state.solved=true;if(round.kind==='replace'){state.selectedPartId=round.targetPartId;state.selectedValue=round.correctValue;}else state.order=round.correctOrder.slice();return state;});
  }
  const raw={version:1,selected:game,games:{[game]:{version:1,seed,currentRound:2,states}}};
  const before=old.api.restore(rec,raw),after=cur.api.restore(rec,raw);
  check(before.solved&&after.solved,'old '+game+' earned triple still independently grades '+setId);
  check(JSON.stringify(before.games[game])===JSON.stringify(after.games[game])&&JSON.stringify(before.earned)===JSON.stringify(after.earned),'old '+game+' raw game and receipt byte-equivalent '+setId);
  const forged=copy(raw);forged.games[game].states=[null,null,null];forged.games[game].solved=true;
  check(!cur.api.restore(rec,forged).solved,'old '+game+' empty forged receipt rejected '+setId);
 }

 // Actual controller integration: cold receipts prepare once, then navigation's
 // next synchronous pass must see null, never a newly resolved Promise.
 const scenario=JSON.parse(read('scenarios/alkanes-user-3.scenario.json'));
 const sig=sc=>JSON.stringify({version:1,title:String(sc.title||''),author:String(sc.author||'Unknown'),steps:sc.steps});
 const storageKey=sc=>{const text=sig(sc);let value=2166136261;for(let i=0;i<text.length;i++)value=Math.imul(value^text.charCodeAt(i),16777619);return 'namelecule:lesson-checkpoints:v1:'+(value>>>0).toString(16);};
 const store=new Map(),reads=[];
 const earnedStates={};
 for(const index of [3,10]){
  const rec=scenario.steps[index].checkpoint.round,seed='224466',entries=lesson.getSet(rec,seed,input,false).rounds;
  const values=entries.map(e=>{const raw={atoms:[],bonds:[],attempts:1,submitted:true};raw[e.mission.kind]=e.mission.accepted[0];return raw;});
  earnedStates[index]=a.api.restore(rec,{version:1,selected:'detective',games:{detective:{version:1,seed,currentRound:2,states:values}}});
 }
 store.set(storageKey(scenario),JSON.stringify({version:1,content:sig(scenario),states:earnedStates,practices:{}}));
 function controller(){const e=setup();e.ctx.sessionStorage={getItem:k=>{reads.push(k);return store.get(k)||null},setItem:(k,v)=>store.set(k,v)};vm.runInContext(read('js/namelecule-quiz-checkpoints.js'),e.ctx);for(const[t,adapter]of Object.entries(e.types))e.ctx.NameleculeQuizCheckpoints.registerType(t,adapter);return e.ctx.NameleculeQuizCheckpoints;}
 const c=controller();check(!c.isComplete(scenario,3),'actual controller cold receipt awaits verified inputs');const first=c.prepareTarget(scenario,11,{});check(first&&typeof first.then==='function','actual controller first cold pass prepares asynchronously');await first;
 check(c.isComplete(scenario,3)&&c.isComplete(scenario,10),'actual controller cold earned receipts both gates verified');
 check(c.prepareTarget(scenario,11,{})===null&&c.resolveTarget(scenario,11)===11,'actual controller next navigation pass is synchronously ready');
 store.set(storageKey(before),JSON.stringify({version:1,content:sig(before),states:{3:{solved:true}},practices:{}}));
 c.reset(scenario);check(c.resolveTarget(scenario,11)===3,'public controller reset re-locks earned gate');const oldReads=reads.filter(k=>k===storageKey(before)).length;
 const reloaded=controller();check(reloaded.resolveTarget(scenario,11)===3,'fresh controller preserves explicit current reset');check(reads.filter(k=>k===storageKey(before)).length===oldReads,'current reset never reads older scenario receipt');
 const checkJSON={role:'Developer memory tests using actual pinned Worker/provider/engines/composite and newadapter; no browser qualification',completed:true,checks,covered:[...coverage],records};fs.writeFileSync(path.join(H,'root/adapter-results.json'),JSON.stringify(checkJSON,null,2)+'\n');console.log(JSON.stringify({completed:true,checks,coverage:coverage.size}));
})().catch(e=>{console.error(e);process.exitCode=1;});
