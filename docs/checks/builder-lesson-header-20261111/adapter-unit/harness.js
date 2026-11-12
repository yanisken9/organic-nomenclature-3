const global=globalThis;
const analyses=catalog.molecules.map(molecule=>analyze(molecule,catalog.engineSHA256));
const digest=Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(x=>parseInt(x,16)));
const recipe={version:1,setId:'alkanes-unbranched',difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:catalog.revision,engineSHA256:catalog.engineSHA256};
const branched={...recipe,setId:'alkanes-branched'};
const clone=value=>JSON.parse(JSON.stringify(value));
let checks=0,randomId=100,timerId=0,frameCount=0,fetches=0;
const timers=new Map(),timerDelays=new Map(),listeners=new Map(),types={},mounted=[],abortControllers=[];
let fetchBehavior=null;
function check(value,label){if(!value)throw Error(label);checks++;}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label);}
function throws(fn,label){let caught=false;try{fn();}catch(_){caught=true;}check(caught,label);}
async function drain(){for(let i=0;i<100;i++)await Promise.resolve();}
async function until(predicate,label){for(let i=0;i<300&&!predicate();i++)await Promise.resolve();check(predicate(),label);}
class FakeNode{
 constructor(tag){this.tagName=tag;this.children=[];this.parent=null;this.attrs={};this.handlers={};this.style={};if(tag==='iframe'){frameCount++;this.contentWindow={messages:[],postMessage(data){this.messages.push(clone(data));}};}}
 get isConnected(){return this.root===true||!!(this.parent&&this.parent.isConnected);}
 append(...children){children.forEach(child=>{child.remove();child.parent=this;this.children.push(child);});}
 replaceChildren(...children){this.children.forEach(child=>child.parent=null);this.children=[];this.append(...children);}
 remove(){if(this.parent){const index=this.parent.children.indexOf(this);if(index>=0)this.parent.children.splice(index,1);this.parent=null;}}
 after(child){if(this.parent){child.remove();const index=this.parent.children.indexOf(this);this.parent.children.splice(index+1,0,child);child.parent=this.parent;}}
 setAttribute(k,v){this.attrs[k]=v;} removeAttribute(k){delete this.attrs[k];} addEventListener(e,fn){this.handlers[e]=fn;}
 querySelector(){return null;} focus(){global.document.activeElement=this;}
}
global.window=global;global.document={baseURI:'http://memory.test/',createElement:tag=>new FakeNode(tag)};global.location={origin:'http://memory.test'};
global.setTimeout=(fn,delay)=>{timers.set(++timerId,fn);timerDelays.set(timerId,delay);return timerId;};global.clearTimeout=id=>{timers.delete(id);timerDelays.delete(id);};
function fireTimers(delay){for(const [id,fn] of Array.from(timers)){if(timerDelays.get(id)===delay&&timers.has(id)){timers.delete(id);timerDelays.delete(id);fn();}}}
function abortListenerCount(){return abortControllers.reduce((n,controller)=>n+controller.signal.__listeners.size,0);}
function deferred(){let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return{promise,resolve,reject};}
function observe(promise){const result={status:"pending"};Promise.resolve(promise).then(value=>{result.status="fulfilled";result.value=value;},error=>{result.status="rejected";result.error=error;});return result;}
global.addEventListener=(name,fn)=>{if(!listeners.has(name))listeners.set(name,new Set());listeners.get(name).add(fn);};
global.removeEventListener=(name,fn)=>listeners.get(name)?.delete(fn);
global.URL=class{constructor(path,base){this.href=base+path;}};global.TextDecoder=class{decode(bytes){return bytes;}};
global.crypto={getRandomValues(values){values.forEach((_,i)=>values[i]=++randomId);return values;},subtle:{digest:async()=>digest}};
global.AbortController=class{constructor(){const list=new Map();this.signal={aborted:false,__listeners:list,addEventListener:(_,fn,options)=>list.set(fn,options),removeEventListener:(_,fn)=>list.delete(fn)};abortControllers.push(this);this.abort=()=>{if(this.signal.aborted)return;this.signal.aborted=true;for(const [fn,options] of Array.from(list)){if(options?.once)list.delete(fn);fn();}};}};
global.fetch=async(...args)=>{fetches++;return fetchBehavior?fetchBehavior(...args):{ok:true,arrayBuffer:async()=>JSON.stringify(catalog)};};
global.NameleculeChemistryClient={analyze:async molecule=>clone(analyses.find(analysis=>analysis.moleculeId===molecule.id))};
global.NameleculeQuizCheckpoints={registerType(name,adapter){types[name]=adapter;}};
global.NameleculeRepairGame={...NameleculeRepairGame,mountRound(host,options){const item={host,options,destroyed:false};mounted.push(item);return{destroy(){item.destroyed=true;}};}};
function runtime(){eval(generatedSource);eval(choiceSource);return types['alkane-game-choice-set'];}
function nodes(root,predicate){return[predicate(root)?root:null,...root.children.flatMap(child=>nodes(child,predicate))].filter(Boolean);}
function mount(adapter,r=recipe,raw=null,practice=false){
 const host=new FakeNode('div');host.root=true;
 const session={host,latest:null,changes:0,solved:0,continued:0,other:0,newPractice:0,ready:[],progress:[],closed:0};
 const options={round:r,initialState:raw,onStateChange(value){session.latest=clone(value);session.changes++;},onSolved(){session.solved++;},onContinue(){session.continued++;},onNewPractice(){session.newPractice++;},onOtherGame(){session.other++;},onClose(){session.closed++;},onSuccessActionsReady(value){session.ready.push(value);},onProgress(value){session.progress.push(value);}};
 session.handle=(practice?adapter.mountPractice:adapter.mount)(host,options);
 session.choose=game=>{const cards=nodes(host,node=>node.className==='nl-game-choice-card');cards[game==='repair'?0:1].handlers.click();};
 session.repair=()=>mounted.findLast(item=>!item.destroyed&&item.host.isConnected);
 session.frame=()=>nodes(host,node=>node.tagName==='iframe')[0];
 session.footer=()=>nodes(host,node=>node.className==='round-next nl-builder-actions')[0];
 return session;
}
function correctRepair(round){const state=NameleculeRepairEngine.createRoundState(round);if(round.kind==='replace'){state.selectedPartId=round.targetPartId;state.selectedValue=round.correctValue;}else state.order=round.correctOrder.slice();return{...state,attempts:1,submitted:true,solved:true};}
function solveRepair(session){const view=session.repair(),raw=correctRepair(view.options.round);view.options.onStateChange(raw);view.options.onSolved({kind:'correct'},raw);}
function message(session,data,override={}){const frame=session.frame();for(const fn of listeners.get('message')||[])fn({origin:location.origin,source:frame.contentWindow,data:{channel:'namelecule-builder-lesson-v1',session:frame.src.match(/lessonSession=([^&]+)/)[1],...data},...override});}
function loadBuilder(session){message(session,{type:'ready'});const load=session.frame().contentWindow.messages.at(-1);check(load?.command==='load','canonical parent load sent');message(session,{type:'loaded',requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,state:load.initialState});return load;}
function stateMessage(session,load,state){message(session,{type:'state',requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,state});}
function correctBuilder(load){const bank=NameleculeNameBuilderEngine.createBank(load.round,{seed:load.bankSeed});const used=new Set();return{answer:load.round.pieces.map(piece=>{const tile=bank.find(tile=>!used.has(tile.id)&&tile.text===piece.text);used.add(tile.id);return tile.id;}),selected:null,attempts:1,submitted:true};}
function finishBuilder(session){const ids=[];for(let i=0;i<3;i++){const load=loadBuilder(session);ids.push(load.moleculeId);stateMessage(session,load,correctBuilder(load));check(session.footer(),'verified builder footer '+i);if(i<2)session.footer().children[0].handlers.click();}equal(new Set(ids).size,3,'three distinct builder molecules');check(session.latest.solved,'builder verified triple earns');return ids;}
(async()=>{
 let adapter=runtime();
 check(Object.isFrozen(NameleculeGeneratedRepairCheckpoint)&&Object.isFrozen(NameleculeGeneratedRepairCheckpoint.adapter),'narrow generated API immutable');
 equal(Object.keys(NameleculeGeneratedRepairCheckpoint),['adapter','loadCanonicalInput','freshSeed'],'narrow API exact exports');
 throws(()=>adapter.validate({...recipe,extra:true}),'composite retains seven-key recipe');
 check(!adapter.restore(recipe,{version:1,solved:true,games:{repair:{solved:true},builder:{solved:true}},earned:{game:'builder',evidence:{solved:true}}}).solved,'bare flags fail');
 const s=mount(adapter);equal(nodes(s.host,n=>n.tagName==='img').length,2,'two accepted logos');
 check(!s.latest.selected&&!s.latest.solved,'initial choice honest');
 s.choose('builder');await until(()=>!!s.frame(),'builder frame ready');
 let load=loadBuilder(s),valid=correctBuilder(load);
 check(load.round.vocabulary.roots.length===5,'unbranched bounded roots');
 check(load.round.representations.includes('skeletal')===(load.moleculeId!=='methane'),'methane skeletal excluded');
 const before=s.changes;
 stateMessage(s,{...load,requestId:load.requestId+1},valid);equal(s.changes,before,'stale request ignored');
 message(s,{type:'state',requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,state:valid},{origin:'http://wrong.test'});equal(s.changes,before,'wrong origin ignored');
 message(s,{type:'state',requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,state:valid},{source:{}});equal(s.changes,before,'wrong source ignored');
 stateMessage(s,load,{...valid,submitted:false,solved:true});check(!s.latest.games.builder.states[0].solved,'tile placement does not count');
 stateMessage(s,load,{...valid,attempts:0});check(!s.latest.games.builder.states[0].solved,'zero checks do not count');
 stateMessage(s,load,{...valid,answer:[valid.answer[0],valid.answer[0]]});check(!s.latest.games.builder.states[0].solved,'duplicate IDs reject');
 stateMessage(s,load,{...valid,answer:['tile-forged']});check(!s.latest.games.builder.states[0].solved,'unknown IDs reject');
 stateMessage(s,load,valid);check(s.latest.games.builder.states[0].solved&&!s.latest.solved,'first success not triple');
 s.footer().children[0].handlers.click();load=loadBuilder(s);stateMessage(s,load,correctBuilder(load));
 check(!s.latest.solved,'two builder successes not triple');
 const builderPartial=clone(s.latest);
 nodes(s.host,n=>n.className==='nl-quiz-button nl-game-choice-switch')[0].handlers.click();s.choose('repair');await until(()=>!!s.repair(),'repair ready');
 const repairRound=s.repair();check(!repairRound.options.onOtherGame,'repair othergame only final');solveRepair(s);
 check(!s.latest.solved,'mixed2builder+1repair never unlocks');
 const mixed=clone(s.latest);s.handle.destroy();
 const framesBeforePrepare=frameCount;adapter=runtime();const cold=adapter.restore(recipe,mixed);check(!cold.solved,'cold mixed incomplete');await adapter.prepare(recipe,cold);equal(frameCount,framesBeforePrepare,'restore uses no hidden viewer');
 const restored=adapter.restore(recipe,cold);equal(restored.games.builder.states.filter(value=>value.solved).length,2,'two builder successes revalidated');equal(restored.games.repair.states.filter(value=>value&&value.solved).length,1,'one repair revalidated');
 const resumed=mount(adapter,recipe,{...restored,selected:'builder'});await until(()=>!!resumed.frame(),'resume builder frame');load=loadBuilder(resumed);equal(load.round.roundId.includes(restored.games.builder.seed),true,'restored stable round');resumed.footer().children[0].handlers.click();load=loadBuilder(resumed);stateMessage(resumed,load,correctBuilder(load));
 check(resumed.latest.solved&&resumed.latest.earned.game==='builder','builder winner receipt');
 equal(resumed.footer().children.length,3,'three builder final actions');check(resumed.footer().children[0].attrs['data-checkpoint-continue']==='','supported continue focus marker');check(resumed.ready.at(-1)===true,'ready only with real final footer');
 resumed.footer().children[0].handlers.click();equal(resumed.continued,1,'continue action');resumed.footer().children[1].handlers.click();equal(resumed.newPractice,1,'same game practice action');resumed.footer().children[2].handlers.click();equal(resumed.other,1,'other game action');
 const earned=clone(resumed.latest),winnerBytes=JSON.stringify(earned.earned);resumed.handle.destroy();
 adapter=runtime();const coldEarned=adapter.restore(recipe,earned);check(!coldEarned.solved,'cold earned needs revalidation');await adapter.prepare(recipe,coldEarned);const verified=adapter.restore(recipe,coldEarned);check(verified.solved,'cold builder earned revalidates');equal(JSON.stringify(verified.earned),winnerBytes,'earned receipt stable after revalidation');
 const optional=adapter.createPractice(recipe,null,{game:'repair'});check(optional.selected==='repair'&&!optional.solved,'othergame optional separate');check(adapter.restore(recipe,earned).solved,'optional cannot relock');
 for(let i=0;i<5;i++) {const fresh=adapter.createPractice(recipe,optional,{game:'builder'});check(!fresh.solved&&fresh.selected==='builder','fresh optional builder '+i);check(adapter.restore(recipe,earned).solved,'earned survives optional '+i);}
 const tampered=clone(earned);tampered.earned.evidence.states[0].answer=['tile-forged'];check(!adapter.restore(recipe,tampered).solved,'tampered winner fails closed');
 const optionalBuilder=mount(adapter,branched,adapter.createPractice(branched,null,{game:'builder'}),true);await until(()=>!!optionalBuilder.frame(),'branched optional frame');const branchLoad=loadBuilder(optionalBuilder);check(branchLoad.round.vocabulary.roots.length===6,'branched bounded roots');optionalBuilder.handle.destroy();
 const all=mount(adapter,branched);all.choose('builder');await until(()=>!!all.frame(),'branched builder frame');const ids=finishBuilder(all);check(ids.every(id=>analyses.find(a=>a.moleculeId===id).branches.length>0),'branched topic exact');const branchedEarned=clone(all.latest);all.handle.destroy();
 const selectedRaw=clone(builderPartial);const chosen=selectedRaw.games.builder.states[1];chosen.selected=chosen.answer[0];chosen.submitted=false;check(adapter.restore(recipe,selectedRaw).games.builder.states[1].selected===chosen.selected,'answer tile selection restores');
 // Exact blueprint migration and old complete signature property order.
 const signature=scenario=>JSON.stringify({version:1,title:String(scenario.title||''),author:String(scenario.author||'Unknown'),steps:scenario.steps});
 let reads=0;const legacy={version:1,content:signature(oldScenario),states:{3:mixed.games.repair},practices:{}};
 const migration=adapter.migrateRecord(newScenario,{signature,read(projected){reads++;equal(signature(projected),signature(oldScenario),'projected full old signature exact');return legacy;}});
 equal(reads,1,'single derived legacy lookup');check(migration.states[3].legacyRepair&&!migration.states[3].solved,'migration wraps raw repair evidence');
 const changed=clone(newScenario);changed.steps[3].note+=' changed';check(adapter.migrateRecord(changed,{read(){throw Error('must not read');}})===null,'edited approved gate rejects migration before lookup');
 const changedOther=clone(newScenario);changedOther.steps[0].note+=' changed';let strictRead=0;check(adapter.migrateRecord(changedOther,{read(projected){strictRead++;return signature(projected)===signature(oldScenario)?legacy:null;}})===null,'unrelated step change fails full signature');equal(strictRead,1,'unrelated edit only one exact read');
 const legacyNormalized=adapter.restore(recipe,migration.states[3]);await adapter.prepare(recipe,legacyNormalized);check(!adapter.restore(recipe,legacyNormalized).solved,'legacy partial not complete');
 const repairSession=mount(adapter,recipe,{version:1,selected:'repair'});await until(()=>!!repairSession.repair(),'repair full session');for(let i=0;i<3;i++){const view=repairSession.repair();check(!!view.options.onOtherGame===(i===2),'repair optional third action bounded '+i);solveRepair(repairSession);if(i<2)view.options.onContinue();}
 check(repairSession.latest.solved&&repairSession.latest.earned.game==='repair','repair independently wins');const oldCompleted=clone(repairSession.latest.games.repair);repairSession.handle.destroy();
 adapter=runtime();const migratedComplete=adapter.restore(recipe,{version:1,selected:'repair',legacyRepair:oldCompleted});check(!migratedComplete.solved,'cold migrated complete not trusted');await adapter.prepare(recipe,migratedComplete);check(adapter.restore(recipe,migratedComplete).solved,'old complete revalidated before unlock');
 const errorSession=mount(adapter,recipe,{version:1,selected:'builder'});await until(()=>!!errorSession.frame(),'error frame');load=loadBuilder(errorSession);message(errorSession,{type:'error',requestId:load.requestId,attemptId:load.attemptId,moleculeId:load.moleculeId,message:'canonical mismatch'});check(!errorSession.frame()&&nodes(errorSession.host,n=>n.className==='nl-builder-error nl-quiz-error').length===1,'canonical native mismatch retry state');check(!errorSession.latest.solved,'native mismatch never unlocks');errorSession.handle.destroy();
 const cancelled=mount(adapter,recipe,{version:1,selected:'builder'});const changes=cancelled.changes;cancelled.handle.destroy();await drain();equal(cancelled.changes,changes,'no late writes after teardown');equal((listeners.get('message')||new Set()).size,0,'all bridge listeners removed');equal(timers.size,0,'all timeout handles removed');
 // R1: the displayed game, rather than an older optional attempt, owns repeat.
 const builderWinner={...earned,selected:'builder'},repairWinner={version:1,selected:'repair',earned:{game:'repair',evidence:oldCompleted}};
 const oldOptionalRepair=adapter.createPractice(recipe,null,{game:'repair'}),oldOptionalBuilder=adapter.createPractice(recipe,null,{game:'builder'});
 equal(adapter.practiceGame(recipe,builderWinner),'builder','R1 displayed required Builder selected');
 equal(adapter.createPractice(recipe,oldOptionalRepair,{game:adapter.practiceGame(recipe,builderWinner)}).selected,'builder','R1 Builder repeat overrides stale optional Repair');
 equal(adapter.practiceGame(recipe,repairWinner),'repair','R1 displayed required Repair selected');
 equal(adapter.createPractice(recipe,oldOptionalBuilder,{game:adapter.practiceGame(recipe,repairWinner)}).selected,'repair','R1 Repair repeat overrides stale optional Builder');
 equal(adapter.practiceGame(recipe,{selected:null,earned:{game:'builder'}}),'builder','R1 winner fallback');
 equal(adapter.practiceGame(recipe,{selected:'invalid',earned:{game:'repair'}}),'repair','R1 invalid selected uses validated winner');
 check(adapter.practiceGame(recipe,{selected:'invalid',earned:{game:'invalid'}})===undefined,'R1 invalid game yields no override');
 throws(()=>adapter.practiceGame({...recipe,extra:true},builderWinner),'R1 hook validates pinned recipe');
 equal(builderWinner.selected,'builder','R1 hook pure');
 // R2: each cold canonical request has a deadline, even if transport ignores abort.
 adapter=runtime();let stalled=deferred();fetchBehavior=()=>stalled.promise;
 const directController=new AbortController(),direct=observe(NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(directController.signal));
 equal(Array.from(timerDelays.values()),[45000],'R2 direct loader owns45s timeout');
 await drain();equal(direct.status,'pending','R2 fetch is actually stalled');fireTimers(45000);await drain();
 equal(direct.status,'rejected','R2 stalled direct fetch rejects at deadline');check(direct.error.name!=='AbortError'&&direct.error.message.includes('άργησε'),'R2 timeout has recoverable error');
 equal(timers.size,0,'R2 direct timeout timer cleanup');equal(abortListenerCount(),0,'R2 direct timeout abort-listener cleanup');
 stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();
 fetchBehavior=null;let beforeFetches=fetches;await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();equal(fetches,beforeFetches+1,'R2 late timed-out fetch did not populate caches');
 equal(timers.size,0,'R2 successful direct retry timer cleanup');equal(abortListenerCount(),0,'R2 successful direct retry listener cleanup');
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const stalledMount=mount(adapter,recipe,{version:1,selected:'builder'}),mountSeed=stalledMount.latest.games.builder.seed;
 check(!stalledMount.frame(),'R2 Builder stalls before iframe startup');equal(Array.from(timerDelays.values()),[45000],'R2 mount bounded before native60s timer');
 fireTimers(45000);await until(()=>nodes(stalledMount.host,n=>n.className==='nl-builder-error nl-quiz-error').length===1,'R2 stalled mount renders retry');
 equal(stalledMount.latest.games.builder.seed,mountSeed,'R2 timeout preserves attempt seed');check(!stalledMount.latest.solved,'R2 timeout never unlocks');
 const changesAfterTimeout=stalledMount.changes;stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();equal(stalledMount.changes,changesAfterTimeout,'R2 late mount response no state write');check(!stalledMount.frame(),'R2 late mount response no viewer');
 equal(timers.size,0,'R2 mount timeout timer cleanup');equal(abortListenerCount(),0,'R2 mount timeout listener cleanup');
 fetchBehavior=null;beforeFetches=fetches;nodes(stalledMount.host,n=>n.className==='nl-quiz-button'&&n.tagName==='button')[0].handlers.click();await until(()=>!!stalledMount.frame(),'R2 mount retry loads after stalledfetch');equal(fetches,beforeFetches+1,'R2 mount retry refetches uncached source');equal(stalledMount.latest.games.builder.seed,mountSeed,'R2 retry same attempt');stalledMount.handle.destroy();
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const rawCold=adapter.restore(recipe,{...earned,games:{repair:null,builder:earned.games.builder}}),beforePrepareFrames=frameCount,prepareResult=observe(adapter.prepare(recipe,rawCold));
 fireTimers(45000);await drain();equal(prepareResult.status,'rejected','R2 cold prepare rejects at deadline');equal(frameCount,beforePrepareFrames,'R2 stalled prepare no hidden viewer');check(!adapter.restore(recipe,rawCold).solved,'R2 timed-out prepare cannot trust earned boolean');
 equal(timers.size,0,'R2 prepare timeout timer cleanup');equal(abortListenerCount(),0,'R2 prepare timeout listener cleanup');
 stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();check(!adapter.restore(recipe,rawCold).solved,'R2 late prepare response does not trust receipt');
 fetchBehavior=null;beforeFetches=fetches;await adapter.prepare(recipe,rawCold);equal(fetches,beforeFetches+1,'R2 coldprepare retry refetches after ignoredabort');check(adapter.restore(recipe,rawCold).solved,'R2 coldprepare retry revalidates earned receipt');
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const external=new AbortController(),abortedLoad=observe(NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(external.signal));external.abort();await drain();
 equal(abortedLoad.status,'rejected','R2 external abort rejects ignoredfetch immediately');equal(abortedLoad.error.name,'AbortError','R2 external abort keeps AbortError');equal(timers.size,0,'R2 external abort timer cleanup');equal(abortListenerCount(),0,'R2 external abort listener cleanup');
 stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();fetchBehavior=null;beforeFetches=fetches;await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();equal(fetches,beforeFetches+1,'R2 late externally-aborted fetch no cache');
 adapter=runtime();const alreadyAborted=new AbortController();alreadyAborted.abort();beforeFetches=fetches;const early=observe(NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(alreadyAborted.signal));await drain();equal(early.status,'rejected','R2 preaborted request rejects');equal(fetches,beforeFetches,'R2 preaborted request no fetch');equal(timers.size,0,'R2 preaborted request no timer');
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const destroyDuringLoad=mount(adapter,recipe,{version:1,selected:'builder'}),destroyCount=destroyDuringLoad.changes;destroyDuringLoad.handle.destroy();await drain();equal(timers.size,0,'R2 mount destroy aborts canonical timer');equal(abortListenerCount(),0,'R2 mount destroy removes canonical listeners');stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();equal(destroyDuringLoad.changes,destroyCount,'R2 ignoredfetch afterdestroy no latewrites');check(!destroyDuringLoad.frame(),'R2 ignoredfetch afterdestroy no iframe');
 fetchBehavior=null;beforeFetches=fetches;await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput();equal(fetches,beforeFetches+1,'R2 destroyed request no latecache');
 adapter=runtime();stalled=deferred();fetchBehavior=()=>stalled.promise;
 const oldRepair=NameleculeGeneratedRepairCheckpoint.adapter,repairPending=observe(oldRepair.prepare(recipe,{version:1,seed:'12345',currentRound:0,states:[null,null,null],solved:false}));
 equal(Array.from(timerDelays.values()),[45000,45000],'R2 generated set keeps outer deadline plus shared load deadline');fireTimers(45000);await drain();equal(repairPending.status,'rejected','R2 old Repair prepare bounded with ignoredfetch');check(repairPending.error.name!=='AbortError'&&repairPending.error.message.includes('άργησε'),'R2 old Repair timeout retains friendly error');equal(timers.size,0,'R2 generated timeout timers cleaned');equal(abortListenerCount(),0,'R2 generated timeout listeners cleaned');stalled.resolve({ok:true,arrayBuffer:async()=>JSON.stringify(catalog)});await drain();fetchBehavior=null;
 const retryOld=await oldRepair.prepare(recipe,{version:1,seed:'12345',currentRound:0,states:[null,null,null],solved:false});check(retryOld.seed==='12345'&&!retryOld.solved,'R2 old Repair retry retains original contract');
 equal(timers.size,0,'R2 all final timeout handles removed');equal(abortListenerCount(),0,'R2 all final abort listeners removed');
 print(JSON.stringify({passed:true,checks,fetches,frameCount,analyses:analyses.length,distinctBranchedIds:ids,reviewCorrections:['R1 displayed-game repeat hook','R2 bounded canonical loader including ignored abort']}));
})().catch(error=>{print(String(error)+'\n'+error.stack);throw error;});
