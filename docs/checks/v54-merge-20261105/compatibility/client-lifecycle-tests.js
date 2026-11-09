// Existing controlled client lifecycle regression harness.
// Extracted from docs/checks/engine-workshop-20261105/adapter/test-adapter.py
// Source SHA256: d61c96a83f1bc3ec2cc6cf20365badd0585da0bc1f26bf5bd7a02ff677c68960
// Only expected engine fetch URL changed to SHA-addressed immutable asset.

let checks=0,fetches=0,created=[],timers=[],fetchFailure=null,fetchPending=false;
let networkBytes=[13,37,42],digested=[],blobs=new Map(),revoked=[],nextBlob=0,allBlobURLs=[];
function ok(value,label){checks++;if(!value)throw Error(label)}
function tick(){return Promise.resolve().then(()=>Promise.resolve()).then(()=>Promise.resolve())}
var URL = class URL {
 constructor(path,base){
  base=base&&base.href||base;
  if(/^https?:/.test(path))this.href=path;
  else if(path==='.')this.href=base.replace(/[?#].*$/,'').replace(/[^/]*$/,'');
  else this.href=base.replace(/[^/]*$/,'')+path;
  this.searchParams={set:(k,v)=>{this.href+='?'+k+'='+v},get:k=>{const m=new RegExp('[?&]'+k+'=([^&]*)').exec(this.href);return m?decodeURIComponent(m[1]):null}};
 }
};
URL.createObjectURL=blob=>{const url='blob:https://example.test/source-'+(++nextBlob);blobs.set(url,blob);allBlobURLs.push(url);return url};
URL.revokeObjectURL=url=>{ok(blobs.has(url),'Every revoked source URL is active');revoked.push(url);blobs.delete(url)};
var Blob=class Blob {constructor(parts,options){this.bytes=Object.freeze(Array.from(new Uint8Array(parts[0])));this.type=options.type;Object.freeze(this)}};
var Signal = class Signal {
 constructor(){this.aborted=false;this.listeners=[]}
 addEventListener(_name,fn){this.listeners.push(fn)}
 removeEventListener(_name,fn){this.listeners=this.listeners.filter(f=>f!==fn)}
};
var AbortController = class AbortController {
 constructor(){this.signal=new Signal()}
 abort(){if(this.signal.aborted)return;this.signal.aborted=true;this.signal.listeners.slice().forEach(f=>f())}
};
var FakeWorker = class FakeWorker {
 constructor(url){this.url=url;this.terminations=0;created.push(this)}
 postMessage(request){this.request=request;ok(blobs.has(request.engineURL),'Worker receives an active verified-source Blob URL');this.importedBytes=blobs.get(request.engineURL).bytes.slice()}
 terminate(){this.terminations++}
 answer(change){const result={moleculeId:this.request.molecule.id,engineSHA256:HASH,name:'measured'};
  if(change)Object.assign(result,change);
  this.onmessage({data:{type:'result',requestId:this.request.requestId,result}})}
};
var document={currentScript:{src:'https://example.test/project/js/namelecule-chemistry-client.js?v=engine-pilot-20261105-r2'},baseURI:'https://example.test/project/games/name-repair.html'};
var window={Worker:FakeWorker,URL,Blob,crypto:{subtle:{digest:(_algorithm,bytes)=>{digested.push(Array.from(new Uint8Array(bytes)));return Promise.resolve(new Uint8Array(HASH.match(/../g).map(h=>parseInt(h,16))).buffer)}}},
 setTimeout(fn){timers.push(fn);return timers.length-1},clearTimeout(id){timers[id]=null},
 fetch(url,options){fetches++;ok(url==='https://example.test/project/js/chemistry-engines/'+HASH+'.js','Measured immutable URL follows script subdirectory');
  ok(options.cache==='reload','Version verification bypasses stale cache');
  if(fetchFailure)return Promise.reject(fetchFailure);
  if(fetchPending)return new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Error('aborted fetch'))));
  return Promise.resolve({ok:true,arrayBuffer:()=>Promise.resolve(new Uint8Array(networkBytes).buffer)})}};
load(CLIENT);
const client=window.NameleculeChemistryClient, molecule={id:'probe',mol:'test'};
async function rejectCode(p,code,label){let error;try{await p}catch(e){error=e}ok(error&&error.code===code,label+': '+(error&&error.code))}
async function run(){
 ok(await client.verifyEngine(HASH)===HASH,'Returns actually measured hash');
 ok(await client.verifyEngine(HASH)===HASH&&fetches===1,'Successful measured version cached once');
 ok(JSON.stringify(digested[0])===JSON.stringify(networkBytes),'Digest receives exact fetched source bytes');
 networkBytes=[99,88,77];
 const a=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const first=created[0];ok(first.url==='https://example.test/project/js/namelecule-chemistry-worker.js?v=engine-pilot-20261105-r2','Worker follows script subdirectory and adapter cache version');
 ok(JSON.stringify(first.importedBytes)===JSON.stringify(digested[0])&&JSON.stringify(first.importedBytes)!==JSON.stringify(networkBytes),'Changed network source cannot replace the actually verified engine bytes');
 first.onmessage({data:{type:'result',requestId:'stale',result:{}}});ok(first.terminations===0,'Stale request ID cannot settle current promise');
 first.answer();ok((await a).name==='measured'&&first.terminations===1,'Success terminates one-shot Worker');
 ok(first.onmessage===null&&first.onerror===null,'Success releases event handlers');
 const b=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const second=created[1];second.answer({moleculeId:'wrong'});await rejectCode(b,'INVALID_ENGINE_RESULT','Wrong molecule rejected');ok(second.terminations===1,'Invalid result terminates Worker');
 const c=client.analyze(molecule,{engineSHA256:HASH});await tick();
 const third=created[2];third.onmessage({data:{type:'error',requestId:third.request.requestId,error:{code:'UNSUPPORTED_MOLECULE',message:'bounded'}}});
 await rejectCode(c,'UNSUPPORTED_MOLECULE','Worker rejection propagated');ok(third.terminations===1,'Worker error terminates');
 const ctrl=new AbortController(), d=client.analyze(molecule,{engineSHA256:HASH,signal:ctrl.signal});await tick();
 const fourth=created[3],oldHandler=fourth.onmessage;ctrl.abort();
 await rejectCode(d,'ABORTED','Abort rejects');ok(fourth.terminations===1&&ctrl.signal.listeners.length===0,'Abort terminates and releases signal listener');
 oldHandler({data:{type:'result',requestId:fourth.request.requestId,result:{}}});ok(fourth.terminations===1,'Stale reply after cancellation stays inert');
 const already=new AbortController();already.abort();await rejectCode(client.analyze(molecule,{engineSHA256:HASH,signal:already.signal}),'ABORTED','Already aborted request');
 ok(created.length===4,'Already aborted request creates no Worker');
 const e=client.analyze(molecule,{engineSHA256:HASH});await tick();const fifth=created[4];timers.filter(Boolean).forEach(f=>f());
 await rejectCode(e,'ENGINE_TIMEOUT','Timeout bounded');ok(fifth.terminations===1,'Timeout terminates Worker');
 const f=client.analyze(molecule,{engineSHA256:HASH});await tick();const sixth=created[5];sixth.onerror({preventDefault(){}});
 await rejectCode(f,'ENGINE_FAILED','Worker startup/runtime error bounded');ok(sixth.terminations===1,'Runtime error terminates Worker');
 const g=client.analyze(molecule,{engineSHA256:HASH});await tick();const seventh=created[6];seventh.onmessageerror();
 await rejectCode(g,'INVALID_ENGINE_RESULT','Unreadable message bounded');ok(seventh.terminations===1,'Message error terminates Worker');
 await rejectCode(client.analyze(molecule,{engineSHA256:'declared'}),'INVALID_ENGINE_VERSION','No unmeasured declaration accepted');
 await rejectCode(client.analyze(null,{engineSHA256:HASH}),'INVALID_MOLECULE','Missing structure rejected');
 await rejectCode(client.analyze(molecule,{engineSHA256:HASH,timeoutMs:0}),'INVALID_TIMEOUT','Invalid timeout rejected');
 const oldWorker=window.Worker;window.Worker=undefined;await rejectCode(client.analyze(molecule,{engineSHA256:HASH}),'ENGINE_UNAVAILABLE','Unsupported Worker bounded');window.Worker=oldWorker;
 const changing={id:'original',mol:'original MOL'},snap=client.analyze(changing,{engineSHA256:HASH});
 changing.id='mutated';changing.mol='mutated MOL';await tick();
 const snapshot=created[7];ok(snapshot.request.molecule.id==='original'&&snapshot.request.molecule.mol==='original MOL','Caller mutation cannot retarget an asynchronous request');
 snapshot.answer();ok((await snap).moleculeId==='original'&&snapshot.terminations===1,'Snapshot validates the original reply');
 ok(created.every(w=>JSON.stringify(w.importedBytes)===JSON.stringify(digested[0]))&&fetches===1,'Every analysis imports the same measured bytes with no second network request');
 window.Worker=function(){throw Error('Worker constructor blocked')};let constructorFailed=false;
 try{await client.analyze(molecule,{engineSHA256:HASH})}catch(e){constructorFailed=true}ok(constructorFailed,'Worker constructor failure is bounded');window.Worker=oldWorker;
 window.Worker=class extends FakeWorker {postMessage(){throw Error('postMessage failed')}};let postFailed=false;
 try{await client.analyze(molecule,{engineSHA256:HASH})}catch(e){postFailed=true}ok(postFailed&&created[8].terminations===1,'Failed message dispatch terminates its Worker');window.Worker=oldWorker;
 ok(blobs.size===0&&revoked.length===allBlobURLs.length&&new Set(revoked).size===revoked.length,'Success, rejection, abort, timeout, runtime/message/constructor/dispatch failures revoke every Blob URL once');
 // Reload the client to clear its successful version cache.
 load(CLIENT);const fresh=window.NameleculeChemistryClient;
 window.crypto.subtle.digest=()=>Promise.resolve(new Uint8Array(32).buffer);
 await rejectCode(fresh.verifyEngine(HASH),'ENGINE_VERSION_MISMATCH','Actual byte hash mismatch rejected');
 fetchFailure=Error('offline');let failed=false;try{await fresh.verifyEngine(HASH)}catch(e){failed=true}ok(failed,'Offline fetch rejected');fetchFailure=null;
 fetchPending=true;const stalled=fresh.analyze(molecule,{engineSHA256:HASH});await tick();timers.filter(Boolean).forEach(f=>f());
 await rejectCode(stalled,'ENGINE_TIMEOUT','Timeout also covers engine fetch');
 return {checks,workerRequests:created.length,allCreatedWorkersTerminated:created.every(w=>w.terminations===1),exactVerifiedBytesBoundToImports:true,blobURLsCreated:allBlobURLs.length,blobURLsRevoked:revoked.length,adapterVersionPropagated:true,limitations:'Controlled API doubles; real browser/network tests are separate'};
}
run().then(x=>print(JSON.stringify(x))).catch(e=>{print(String(e.stack||e));quit(1)});
