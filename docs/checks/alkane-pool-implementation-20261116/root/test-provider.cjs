'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {webcrypto,createHash}=require('crypto');
const R=process.cwd(),H=path.join(R,'docs/checks/alkane-pool-implementation-20261116');
const read=p=>fs.readFileSync(path.join(R,p),'utf8'),clone=o=>JSON.parse(JSON.stringify(o));
const results=[];function check(ok,label){assert.ok(ok,label);results.push({label,passed:true});}
const worker=read('js/namelecule-chemistry-worker.js');
const engine=read('js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js');
function analyze(molecule){let result;const ctx=vm.createContext({URL});ctx.self={location:{origin:'http://memory.test'},postMessage:r=>result=r,close(){}};ctx.importScripts=()=>vm.runInContext(engine,ctx);vm.runInContext(worker,ctx);ctx.self.onmessage({data:{type:'analyze',requestId:'test',molecule,engineSHA256:'3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306',engineURL:'blob:http://memory.test/exact'}});assert.equal(result.type,'result',JSON.stringify(result));return clone(result.result);}
function setup(before=false,options={}){
 const seen=[];let api;const ctx=vm.createContext({console,URL,TextEncoder,TextDecoder,AbortController,Uint8Array,crypto:webcrypto,setTimeout,clearTimeout});ctx.window=ctx;vm.runInContext("Math.random=()=>0.3141592653",ctx);
 ctx.document={baseURI:'http://memory.test/',currentScript:{src:'http://memory.test/js/namelecule-generated-repair-checkpoint.js'},getElementById:()=>null};
 ctx.NameleculeQuizCheckpoints={registerType:(t,a)=>api=a};
 ctx.fetch=async url=>{seen.push(url);if(options.hold)await options.hold;if(options.fail)throw Error('controlled transport failure');let text=read(new URL(url).pathname.slice(1));if(options.corrupt)text+=' ';return{ok:true,arrayBuffer:async()=>new TextEncoder().encode(text).buffer};};
 ctx.NameleculeChemistryClient={analyze:async m=>analyze(m)};
 vm.runInContext(read('js/namelecule-game-repair.js'),ctx);vm.runInContext(read('js/namelecule-repair-generator.js'),ctx);
 vm.runInContext(before?fs.readFileSync(path.join(H,'before/js/namelecule-generated-repair-checkpoint.js'),'utf8'):read('js/namelecule-generated-repair-checkpoint.js'),ctx);
 return{ctx,api:()=>api,provider:ctx.NameleculeGeneratedRepairCheckpoint,seen,options};
}
(async()=>{
 const old=setup(true),current=setup();const oldInput=await old.provider.loadCanonicalInput();const legacy=await current.provider.loadCanonicalInput();const enriched=await current.provider.loadCanonicalInput(null,'enriched');
 check(JSON.stringify(oldInput)===JSON.stringify(legacy),'Legacy canonical input exactly matches before-provider output');
 check(legacy.catalog.molecules.length===8&&enriched.catalog.molecules.length===14,'Legacy eight and enriched14 retain separate verified inputs');
 check(await current.provider.loadCanonicalInput()===legacy&&await current.provider.loadCanonicalInput(null,'enriched')===enriched,'Both version caches retain own object identity');
 check(current.seen.every(u=>u.startsWith('http://memory.test/games/data/')),'Script-relative verified catalog paths resolve at root');
 check(Object.isFrozen(enriched)&&Object.isFrozen(enriched.catalog.molecules[13]),'Verified input deeply frozen');
 for(const ref of['not-a-catalog',{revision:legacy.catalog.revision,file:'https://foreign.test/data.json'},{revision:enriched.catalog.revision,count:8}]){
  assert.throws(()=>current.provider.catalogDescriptor(ref));check(true,'Unknown/spoofed descriptor fails closed');
 }
 const recipe=setId=>({version:1,setId,difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:legacy.catalog.revision,engineSHA256:legacy.catalog.engineSHA256});
 const coverage=new Set();
 for(const seed of['0','1','1234567','4294967295','1010101010','1888','912312','99887'])for(const difficulty of['basic','challenge']){
  const before=old.ctx.NameleculeRepairGenerator.createGame(oldInput.catalog,oldInput.analyses,{seed,difficulty});const after=current.ctx.NameleculeRepairGenerator.createGame(legacy.catalog,legacy.analyses,{seed,difficulty});
  check(JSON.stringify(before)===JSON.stringify(after),'Exact legacy round replay '+seed+'/'+difficulty);
  const game=current.ctx.NameleculeRepairGenerator.createGame(enriched.catalog,enriched.analyses,{seed,difficulty});current.ctx.NameleculeRepairEngine.validateGameData(game);game.sets.forEach(s=>s.rounds.forEach(r=>coverage.add(r.moleculeId)));check(true,'Enriched actual pinned analyses produce valid rounds '+seed+'/'+difficulty);
 }
 for(const m of enriched.catalog.molecules.slice(8))check(coverage.has(m.id),'Deterministic enriched round choices cover new '+m.id);
 for(const setId of['alkanes-unbranched','alkanes-branched'])for(const seed of['1','11','999']){
  const rec=recipe(setId),raw={version:1,seed,currentRound:0,states:[null,null,null],solved:true};
  const a=await old.api().prepare(rec,raw),b=await current.api().prepare(rec,clone(a));if(JSON.stringify(a)!==JSON.stringify(b))fs.writeFileSync(path.join(H,'root/partial-diff.json'),JSON.stringify({a,b},null,2));check(JSON.stringify(a)===JSON.stringify(b),'Cold legacy partial normalization unchanged '+setId+'/'+seed);check(!b.solved,'Forged solved bit cannot unlock '+setId+'/'+seed);
  const game=current.ctx.NameleculeRepairGenerator.createGame(legacy.catalog,legacy.analyses,{seed,difficulty:'basic'});const rounds=game.sets.find(s=>s.id===setId).rounds;
  const states=rounds.map(round=>{const s=current.ctx.NameleculeRepairEngine.createRoundState(round);s.attempts=1;s.submitted=true;s.solved=true;if(round.kind==='replace'){s.selectedPartId=round.targetPartId;s.selectedValue=round.correctValue;}else s.order=round.correctOrder.slice();return s;});
  const earned={version:1,seed,currentRound:2,states,solved:true};const x=old.api().restore(rec,earned),y=current.api().restore(rec,earned);check(JSON.stringify(x)===JSON.stringify(y)&&y.solved,'Cold prepared earned legacy receipt remains exact '+setId+'/'+seed);
  const reset=current.api().restore(rec,{version:1,seed,currentRound:0,states:[null,null,null],solved:false});check(!reset.solved,'Reset is not resurrected from earned cache');
 }
 assert.throws(()=>current.api().validate({...recipe('alkanes-branched'),catalogRevision:enriched.catalog.revision}));check(true,'Enriched standalone catalog does not silently enable new composite lesson recipes');
 const bad=setup(false,{corrupt:true});await assert.rejects(()=>bad.provider.loadCanonicalInput(null,'enriched'));check(true,'Changed full source bytes rejected before analysis');bad.options.corrupt=false;check((await bad.provider.loadCanonicalInput(null,'enriched')).catalog.molecules.length===14,'Retry after corrupt source can recover without poisoned cache');
 const transport=setup(false,{fail:true});await assert.rejects(()=>transport.provider.loadCanonicalInput());transport.options.fail=false;check((await transport.provider.loadCanonicalInput()).catalog.molecules.length===8,'Transport failure leaves legacy cache empty and retryable');
 const abort=setup();const ac=new AbortController();ac.abort();await assert.rejects(()=>abort.provider.loadCanonicalInput(ac.signal,'enriched'),{name:'AbortError'});check(abort.seen.length===0,'Pre-aborted request performs no fetch');
 let release;const hold=new Promise(r=>release=r);const late=setup(false,{hold});const controller=new AbortController();const pending=late.provider.loadCanonicalInput(controller.signal,'enriched');controller.abort();await assert.rejects(()=>pending,{name:'AbortError'});release();await new Promise(r=>setTimeout(r,20));late.options.hold=null;const count=late.seen.length;await late.provider.loadCanonicalInput(null,'enriched');check(late.seen.length===count+1,'Late abort-ignoring transport cannot fill new catalog cache');
 const out={role:'Developer actual provider/worker/core in-memory checks, not browser or independent execution',completed:true,checks:results,legacyRoundsByteEqual:true,coveredNewMolecules:[...coverage].filter(id=>enriched.catalog.molecules.slice(8).some(m=>m.id===id)),limits:['Controlled fetch/timers/module registration; actual browser Workshop receipt continuity tested separately','No SVG/3D layout execution']};fs.writeFileSync(path.join(H,'root/provider-results.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({completed:true,checks:results.length,newCovered:out.coveredNewMolecules.length}));
})().catch(e=>{console.error(e);process.exitCode=1;});
