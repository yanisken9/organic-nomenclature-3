(async()=>{
 let adapter=runtime(),stalled=deferred();fetchBehavior=()=>stalled.promise;
 const direct=observe(NameleculeGeneratedRepairCheckpoint.loadCanonicalInput());
 equal(timers.size,0,'r1 direct loader had no timer');fireTimers(45000);await drain();equal(direct.status,'pending','r1 ignoredfetch still pending after virtual45s');
 stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();equal(direct.status,'fulfilled','r1 controlled fetch eventually resolves');
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const session=mount(adapter,recipe,{version:1,selected:'builder'});equal(timers.size,0,'r1 mount beforeiframe had no timeout');fireTimers(45000);await drain();check(!session.frame(),'r1 mount remains preiframe');const retry=nodes(session.host,n=>n.className==='nl-builder-error nl-quiz-error').length;equal(retry,0,'r1 mount cannot present timeoutretry');session.handle.destroy();stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const raw={version:1,selected:'builder',games:{builder:{version:1,seed:'12345',currentRound:0,states:[null,null,null],solved:false}}};
 const prepared=observe(adapter.prepare(recipe,raw));equal(timers.size,0,'r1 coldprepare had no timeout');fireTimers(45000);await drain();equal(prepared.status,'pending','r1 coldprepare pending past virtual45s');stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();equal(prepared.status,'fulfilled','r1 coldprepare eventually resolves');
 print(JSON.stringify({reproduced:true,checks,sourceRevision:'r1 exact SHA-checked sources',conditions:'JSC virtual45s timers; deliberately stalled fetch ignoring AbortSignal',observed:{directLoadPendingAfter45s:true,mountNoTimeoutRetry:true,coldPreparePendingAfter45s:true},limitations:['Mock transport and virtual time; no actual45s browser wait']}));
})().catch(error=>{print(String(error)+'\n'+error.stack);throw error;});
