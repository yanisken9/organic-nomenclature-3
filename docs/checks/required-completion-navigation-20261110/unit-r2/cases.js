// Developer controller evidence. Adapter, DOM, storage and abort are declared doubles.
let checks = 0;
const labels = [];
function check(ok, label) { if (!ok) throw Error(label); checks++; labels.push(label); }
function equal(actual, expected, label) { check(JSON.stringify(actual) === JSON.stringify(expected), label); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function deferred() { let resolve, reject; const promise = new Promise((a,b) => { resolve=a;reject=b; });return {promise,resolve,reject}; }
async function turns() { for (let index=0;index<20;index++) await Promise.resolve(); }
global.AbortController = class {
  constructor() { this.signal={aborted:false}; }
  abort() { this.signal.aborted=true; }
};
FakeNode.prototype.contains=function(node){return this===node||this.children.some(child=>child.contains(node));};
FakeNode.prototype.getBoundingClientRect=function(){return {top:0,bottom:0,height:0};};

function signature(scenario) { return JSON.stringify({version:1,title:String(scenario.title||''),author:String(scenario.author||'Unknown'),steps:scenario.steps}); }
function recordKey(scenario) { const content=signature(scenario);let hash=2166136261;for(let i=0;i<content.length;i++)hash=Math.imul(hash^content.charCodeAt(i),16777619);return 'namelecule:lesson-checkpoints:v1:'+(hash>>>0).toString(16); }
function scenario(type='practice-probe') { return {title:'Optional controller contract',author:'Declared Developer double',index:0,steps:[{checkpoint:{version:1,id:'required-three',type,round:{topic:'straight',roundCount:3}}},{text:'Theory after required gate'},{checkpoint:{version:1,id:'required-three-second',type,round:{topic:'branched',roundCount:3}}},{text:'Theory after second gate'}]}; }
function receipt(seed='required-1',answers=[true,true,true],currentRound=2) { return {version:1,seed,currentRound,answers:answers.slice(),solved:true}; }
function boot(options={}) {
  const copied=options.storage ? Array.from(options.storage) : [];
  resetEnvironment();for(const [key,value] of copied)storage.set(key,value);
  NameleculeRepairGame.createResponseRevealer=()=>({stop(){},reveal(){}});
  new Function(controllerSource)();
  const C=NameleculeQuizCheckpoints,mounts=[],preparations=[],created=[];
  const requiredTrusted=new Set(options.requiredTrusted||[]),optionalTrusted=new Set(options.optionalTrusted||[]);
  const controls={prepare:null,mountError:false,optionalMountError:false};
  let practiceNumber=0;
  function restore(value,previous,optional) {
    if(previous&&previous.malformed)throw Error('malformed '+(optional?'practice':'required'));
    const seed=previous&&typeof previous.seed==='string'?previous.seed:null;
    const answers=previous&&Array.isArray(previous.answers)&&previous.answers.length===3?previous.answers.map(v=>v===true):[false,false,false];
    const trusted=(optional?optionalTrusted:requiredTrusted).has(seed);
    return {version:1,seed,currentRound:previous&&Number.isInteger(previous.currentRound)?Math.max(0,Math.min(2,previous.currentRound)):0,answers,solved:!!seed&&trusted&&answers.every(v=>v)};
  }
  function mount(host,config,optional) {
    if(optional?controls.optionalMountError:controls.mountError)throw Error('declared mount failure');
    if(controls.reportFinalThenThrow){config.onProgress({current:3,total:3});if(typeof config.onSuccessActionsReady==='function')config.onSuccessActionsReady(true);throw Error('declared failure after final progress');}
    const seed=config.initialState&&config.initialState.seed||'required-'+(config.round.topic==='branched'?'2':'1');
    (optional?optionalTrusted:requiredTrusted).add(seed);
    const mounted={host,options:config,optional,seed,destroyed:false,destroyCalls:0};
    mounted.handle={destroy(){mounted.destroyed=true;mounted.destroyCalls++;}};
    mounts.push(mounted);return mounted.handle;
  }
  const adapter={validate(value){if(!value||value.roundCount!==3)throw Error('invalid probe');return value;},restore(value,state){return restore(value,state,false);},
    prepare(value,state,config){const call={round:clone(value),state:clone(state),signal:config.signal};preparations.push(call);return controls.prepare?controls.prepare(call):null;},
    mount(host,config){return mount(host,config,false);}};
  if(options.supportsPractice!==false)Object.assign(adapter,{
    createPractice(value,previous){const result={version:1,seed:'practice-'+(++practiceNumber),currentRound:0,answers:[false,false,false],solved:false};created.push({previous:clone(previous),result:clone(result)});return result;},
    restorePractice(value,state){return restore(value,state,true);},
    mountPractice(host,config){return mount(host,config,true);}
  });
  C.registerType('practice-probe',adapter);
  const s=options.scenario||scenario();liveScenario=s;
  function step(index=0){s.index=index;liveScenario=s;C.onStep(s,index);}
  function saved(){const value=storage.get(recordKey(s));return value?JSON.parse(value):null;}
  function seed(states,practices){storage.set(recordKey(s),JSON.stringify({version:1,content:signature(s),states, ...(practices===undefined?{}:{practices})}));}
  return {C,s,step,saved,seed,controls,mounts,preparations,created,requiredTrusted,optionalTrusted,latest:()=>mounts.at(-1)};
}
function click(id){const n=body.find(id);if(!n)throw Error('missing '+id);n.fire('click');return n;}
function open(env){click('nlQuizOpen');return env.latest();}
function complete(env,mount=env.latest()){const state=receipt(mount.seed);mount.options.onStateChange(state);mount.options.onSolved({kind:'correct'},state);if(typeof mount.options.onSuccessActionsReady==='function')mount.options.onSuccessActionsReady(true);return state;}

async function main(){
  let e=boot();e.step();
  check(!e.C.isComplete(e.s,0)&&e.C.resolveTarget(e.s,3)===0,'untouched required gate remains locked');
  check(body.find('nlQuizPracticeOpen').hidden,'no optional card before required mastery');
  click('nlQuizPracticeOpen');check(e.created.length===0&&e.mounts.length===0,'forced hidden practice card cannot bypass initial gate');
  let m=open(e);check(!body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'required header exposes Return only');click('nlQuizBack');check(!body.find('nlQuizDialog').open&&!e.C.isComplete(e.s,0),'visible required Return closes without unlocking');m=open(e);check(!m.optional&&typeof m.options.onNewPractice==='function','supported required mount receives opt-in action callback');
  m.options.onNewPractice();check(e.created.length===0,'onNewPractice independently verifies original mastery');
  m.options.onSolved({kind:'correct'},{...receipt(m.seed),answers:[true,true,false]});check(!e.C.isComplete(e.s,0),'claimed success without third repair is rejected');
  for(const answers of [[true,false,false],[true,true,false]]){
    m.options.onStateChange(receipt(m.seed,answers,answers[1]?1:0));
    check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'partial required answers do not expose optional card '+answers.filter(Boolean).length);
  }
  complete(e,m);check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'required three verified successes expose optional card');
  check(e.C.resolveTarget(e.s,3)===2,'first gate mastery does not bypass second gate');
  const required=clone(e.saved().states[0]);m.options.onNewPractice();m=e.latest();
  check(m.optional&&e.created.length===1,'success action starts optional mount');
  check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional header exposes Continue only');
  body.find('nlQuizDialog').fire('cancel');click('nlQuizOpen');check(!body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'reused dialog restores Return for required review');body.find('nlQuizDialog').fire('cancel');click('nlQuizPracticeOpen');m=e.latest();check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'reused dialog hides Return again for optional resume');
  equal(e.created[0].previous,required,'initial optional creation receives original required receipt');
  equal(e.saved().states[0],required,'starting optional practice preserves original required bytes');
  check(!body.find('nlQuizPracticeContinue').hidden&&!body.find('nlQuizPracticeNotice').hidden&&body.find('nlQuizDialogTitle').textContent==='Προαιρετική εξάσκηση','optional mode exposes continue and clear status');
  check(body.find('nlQuizPracticeNotice').textContent.includes('αρχική τριάδα ολοκληρώθηκε'),'optional status explicitly states required mastery');
  m.options.onProgress({current:1,total:3});check(body.find('nlQuizProgress').textContent==='Κουίζ 1/3','optional mount retains quiz position counter');
  const optionalWrong=receipt(m.seed,[true,false,false],1);m.options.onStateChange(optionalWrong);
  check(e.C.isComplete(e.s,0),'wrong or incomplete optional answers never relock required gate');
  equal(e.saved().states[0],required,'wrong optional answer leaves required receipt unchanged');
  check(e.saved().practices[0].seed===m.seed&&!e.saved().practices[0].solved,'optional answer persists in separate practices field');
  body.find('nlQuizDialog').fire('cancel');check(m.destroyed&&!body.find('nlQuizDialog').open,'Return destroys only current optional mount');
  check(body.find('nlQuizPracticeOpen').textContent==='Συνέχισε την εξάσκηση','card offers resume after partial optional exit');
  click('nlQuizPracticeOpen');let reopened=e.latest();
  check(reopened.optional&&reopened.seed===m.seed&&reopened.options.initialState.currentRound===1,'same-page reopen restores current optional attempt');
  equal(reopened.options.initialState.answers,[true,false,false],'same-page reopen retains optional answers');
  m.options.onStateChange(receipt(m.seed));equal(e.saved().practices[0].answers,[true,false,false],'closed optional callback cannot overwrite current attempt');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1&&!body.find('nlQuizDialog').open&&e.C.isComplete(e.s,0),'header Continue advances with optional set unfinished');
  e.step(0);click('nlQuizPracticeOpen');m=e.latest();
  for(let index=0;index<40;index++){
    const old=m;m.options.onNewPractice();m=e.latest();
    check(m.optional&&m.seed!==old.seed&&old.destroyed,'repeat replaces previous optional mount '+index);
    check(Object.keys(e.saved().practices).length===1&&Object.keys(e.saved().states).length===1,'repeat storage keeps one optional and original receipt '+index);
    equal(e.saved().states[0],required,'repeat preserves original required receipt '+index);
  }
  const latestBefore=clone(e.saved()),stale=reopened.options;
  stale.onNewPractice();stale.onSolved({kind:'correct'},receipt('bad'));stale.onContinue();
  equal(e.saved(),latestBefore,'stale callbacks after repeats cannot mutate storage or create attempts');
  check(e.C.isComplete(e.s,0),'mastery remains verified after more than 32 optional replacements');
  // Both gates have independent required and current practice fields.
  body.find('nlQuizDialog').fire('cancel');e.step(2);const second=open(e);complete(e,second);second.options.onNewPractice();
  check(e.saved().states[0].seed==='required-1'&&e.saved().states[2].seed==='required-2','both required gates retain separate mastery receipts');
  check(Object.keys(e.saved().practices).length===2&&e.C.resolveTarget(e.s,3)===3,'both gates may keep one optional attempt and theory remains unlocked');

  // Refresh must verify original required answers before accepting optional access.
  const storageSnapshot=Array.from(storage);e=boot({storage:storageSnapshot});
  const prep=deferred();e.controls.prepare=call=>prep.promise.then(()=>{e.requiredTrusted.add(call.state.seed);return call.state;});e.step(0);
  check(e.preparations.length===1&&e.preparations[0].state.seed==='required-1','refresh prepares original required receipt rather than optional seed');
  check(body.find('nlQuizOpen').disabled&&body.find('nlQuizPracticeOpen').hidden&&!e.C.isComplete(e.s,0),'cold saved practice stays unavailable while required validation is pending');
  click('nlQuizOpen');click('nlQuizPracticeOpen');check(e.mounts.length===0,'synthetic clicks cannot open while preparation is pending');
  prep.resolve();await turns();
  check(!body.find('nlQuizOpen').disabled&&e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'completed required verification restores practice card');
  click('nlQuizPracticeOpen');check(e.latest().optional&&e.latest().options.initialState.seed===latestBefore.practices[0].seed,'refresh restores same optional attempt');
  equal(e.saved().states[0],required,'refresh preparation preserves original verified required receipt');
  const furtherPreparation=e.C.prepareTarget(e.s,3,{});check(!!furtherPreparation&&typeof furtherPreparation.then==='function','forward navigation prepares still-cold second required gate');await furtherPreparation;
  check(e.preparations.at(-1).state.seed==='required-2'&&e.preparations.every(call=>call.state.seed.startsWith('required-')),'forward preparation reads required receipts and never current optional seeds');
  check(e.C.resolveTarget(e.s,3)===3&&e.C.isComplete(e.s,2),'forward preparation independently validates both required gates');
  check(Object.keys(e.saved().practices).length===2,'forward required verification preserves both saved optional attempts');

  // Stored optional data cannot stand in for missing or unproven required answers.
  e=boot();e.seed({0:receipt('untrusted-required',[false,false,false])},{0:receipt('trusted-optional')});e.optionalTrusted.add('trusted-optional');e.step();
  check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'solved optional receipt cannot unlock incomplete required gate');
  open(e).options.onNewPractice();check(e.created.length===0,'direct practice callback cannot promote optional completion to required mastery');
  e=boot();e.seed({}, {0:receipt('orphan-practice')});e.step();check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'orphan practice without required receipt does not bypass gate');
  e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()},{0:{malformed:true}});e.step();
  check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'malformed optional receipt does not erase verified required mastery');
  click('nlQuizPracticeOpen');check(e.created.length===1&&e.latest().optional,'malformed optional receipt recovers as a fresh optional attempt');
  e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();
  check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'old receipt without practices field retains mastery');

  // Unsupported adapters keep their existing required-only flow.
  e=boot({supportsPractice:false});e.step();m=open(e);
  check(m.options.onNewPractice===undefined&&body.find('nlQuizPracticeOpen').hidden,'unsupported type never receives opt-in renderer action');
  complete(e,m);check(e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'unsupported type completion remains ordinary required flow');
  m.options.onContinue();check(navigation.at(-1)===1,'unsupported required type still continues');

  // Active ownership also rejects callbacks from replaced scenarios and steps.
  for(const mode of ['different-object','different-step','edited-content']){
    e=boot();e.step();m=open(e);const writesBefore=storageWrites;
    if(mode==='different-object')liveScenario={...e.s};
    else if(mode==='different-step')e.s.index=1;
    else e.s.title+=' changed';
    m.options.onStateChange(receipt(m.seed));m.options.onSolved({kind:'correct'},receipt(m.seed));m.options.onNewPractice();m.options.onContinue();
    check(storageWrites===writesBefore&&e.created.length===0&&navigation.length===0,'current-context guard rejects stale '+mode+' callbacks');e.C.onExit();
  }

  // Optional loading/error/abort may not remove the independent Continue control.
  e=boot();e.step();m=open(e);complete(e,m);e.controls.optionalMountError=true;m.options.onNewPractice();
  check(!!body.find('nlQuizHost').querySelector('.nl-quiz-error')&&!body.find('nlQuizRetry').hidden,'optional thrown generation/mount error exposes retry');
  check(!body.find('nlQuizPracticeContinue').hidden&&e.C.isComplete(e.s,0),'optional error retains Continue and mastery');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1,'learner continues during optional error');
  e.step(0);e.controls.optionalMountError=false;click('nlQuizPracticeOpen');m=e.latest();m.options.onProgress(null);
  check(!body.find('nlQuizPracticeContinue').hidden&&body.find('nlQuizProgress').hidden,'loading optional progress retains independent Continue');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1&&m.destroyed,'learner continues during optional loading');
  const count=storageWrites;m.options.onStateChange(receipt(m.seed));m.options.onSolved({kind:'correct'},receipt(m.seed));m.options.onNewPractice();
  check(storageWrites===count,'late aborted optional callbacks do not persist or start more work');

  // Preparation failures, cancellation and reset cannot authorize stale state.
  for(const mode of ['reject','exit','reset','signature-change']){
    e=boot();e.seed({0:receipt()},{0:receipt('practice-saved',[true,false,false],1)});const work=deferred();
    e.controls.prepare=call=>work.promise.then(()=>{e.requiredTrusted.add(call.state.seed);return call.state;});e.step();const signal=e.preparations[0].signal;
    if(mode==='reject')work.reject(Error('declared preparation failure'));
    else if(mode==='exit'){e.C.onExit();work.resolve();}
    else if(mode==='reset'){e.C.reset(e.s);work.resolve();}
    else{e.s.title+=' edited';work.resolve();}
    await turns();
    if(mode==='exit')check(signal.aborted&&!body.find('nlQuizDialog')?.open,'exit aborts required preparation and ignores late completion');
    if(mode==='reset')check(!e.C.isComplete(e.s,0)&&Object.keys(e.saved().states).length===0&&Object.keys(e.saved().practices).length===0,'reset clears both fields and late required preparation cannot restore them');
    if(mode==='reject')check(!e.C.isComplete(e.s,0)&&!body.find('nlQuizOpen').disabled&&body.find('nlQuizPracticeOpen').hidden,'failed required preparation stays locked and original repair can retry');
    if(mode==='signature-change')check(!e.C.isComplete(e.s,0),'authored signature change rejects late preparation');
  }

  // Reset invalidates mounted callback ownership and both optional/required records.
  e=boot();e.step();m=open(e);complete(e,m);m.options.onNewPractice();m=e.latest();e.C.reset(e.s);
  check(!e.C.isComplete(e.s,0)&&Object.keys(e.saved().states).length===0&&Object.keys(e.saved().practices).length===0&&!body.find('nlQuizDialog').open,'active reset closes practice and clears both record fields');
  const resetWrites=storageWrites;m.options.onStateChange(receipt(m.seed));m.options.onNewPractice();check(storageWrites===resetWrites&&!e.C.isComplete(e.s,0),'late callback after reset cannot recreate either record');

  // A storage write failure retains in-memory required mastery and optional exit.
  e=boot();e.step();m=open(e);global.sessionStorage.setItem=()=>{throw Error('declared unavailable storage');};complete(e,m);m.options.onNewPractice();
  check(e.C.isComplete(e.s,0)&&e.latest().optional,'unavailable storage does not remove in-memory mastery or optional access');
  check(!body.find('nlQuizCheckpoint').querySelector('.nl-quiz-storage-note').hidden,'unavailable storage is disclosed on checkpoint card');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1,'optional Continue works when tab storage is unavailable');

  // Preview has separate mastery/practice and produces no stored learner writes.
  e=boot();e.step();m=open(e);complete(e,m);m.options.onNewPractice();const learnerStorage=Array.from(storage),learnerRequired=clone(e.saved().states);
  const previewScenario=clone(e.s);e.C.beginPreview(previewScenario);liveScenario=previewScenario;e.C.onStep(previewScenario,0);
  check(e.C.isPreview(previewScenario)&&!e.C.isComplete(previewScenario,0),'preview starts without adopting learner mastery');
  const writes=storageWrites;m=open(e);complete(e,m);m.options.onNewPractice();const previewMount=e.latest();previewMount.options.onStateChange(receipt(previewMount.seed,[true,false,false],1));
  check(storageWrites===writes,'preview required and optional work never persist to learner storage');
  equal(Array.from(storage),learnerStorage,'preview preserves exact learner stored records');e.C.endPreview();liveScenario=e.s;e.step();
  check(!e.C.isPreview(e.s)&&e.C.isComplete(e.s,0),'ending preview restores original learner mastery');equal(e.saved().states,learnerRequired,'preview leaves original required receipts unchanged');
  click('nlQuizPracticeOpen');check(e.latest().optional,'ending preview restores learner optional attempt');

  // Synthetic queued native-close event: reopening must retain the new mount.
  m=e.latest();const dialog=body.find('nlQuizDialog');dialog.close=function(){this.open=false;};body.find('nlQuizDialog').fire('cancel');click('nlQuizPracticeOpen');const newMount=e.latest();
  check(dialog.open&&newMount!==m&&!newMount.destroyed,'optional dialog reopens before queued close event');dialog.fire('close');
  check(!newMount.destroyed&&dialog.open,'queued close guard preserves reopened optional mount (synthetic event only)');
  print(JSON.stringify({completed:true,checks,labels,limits:['Actual current full controller runs in system JavaScriptCore. FakeNode DOM, storage, abort, adapter completion and preparation are explicit doubles.','No native browser layout/input, generated molecular answers, real transport, real timer or native close queue claim.','Probe trusted-required and trusted-optional sets model independent receipt validation; real engine/cache reconstruction is tested separately by adapter and integration owners.']}));
}


function finalHeaderCases() {
 const startChecks=checks;
 let e=boot();e.step();let m=open(e);
 for(const n of [1,2]) {
  m.options.onProgress({current:n,total:3});
  m.options.onStateChange(receipt(m.seed,n===1?[true,false,false]:[true,true,false],n-1));
  check(!body.find('nlQuizBack').hidden,'required earlier rendered round retains Return '+n);
 }
 m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'unsolved third round retains Return');
 m.options.onSolved({kind:'correct'},receipt(m.seed,[true,true,false]));
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,0),'unverified claimed final success cannot hide Return or unlock');
 complete(e,m);
 check(body.find('nlQuizBack').hidden&&e.C.isComplete(e.s,0),'verified live third success hides Return');
 const required=clone(e.saved().states[0]);
 m.options.onProgress(null);
 check(!body.find('nlQuizBack').hidden,'required loading or error null progress restores Return after mastery');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'restored rendered final success hides Return');
 for(const value of [{current:0,total:3},{current:4,total:3},{current:3,total:0},{current:3.5,total:3.5},{}]) {
  m.options.onProgress(value);check(!body.find('nlQuizBack').hidden,'invalid progress cannot hide Return '+JSON.stringify(value));
 }
 m.options.onProgress({current:1,total:3});
 check(!body.find('nlQuizBack').hidden,'earned mastery alone does not hide Return on earlier rendered round');
 m.options.onProgress({current:3,total:3});
 body.find('nlQuizDialog').fire('cancel');m=open(e);
 check(!body.find('nlQuizBack').hidden,'reopen resets transient final visibility before rendered progress');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'reopen hides Return when restored final content is rendered');
 m.options.onNewPractice();m=e.latest();
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'new optional set retains existing Continue-only header');
 m.options.onProgress(null);
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional loading retains Continue-only header');
 equal(e.saved().states[0],required,'header changes preserve exact verified required receipt');
 body.find('nlQuizDialog').fire('cancel');e.step(2);m=open(e);m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,2),'next required gate does not inherit hidden Return or mastery');
 const old=m;body.find('nlQuizDialog').fire('cancel');e.step(0);m=open(e);m.options.onProgress({current:1,total:3});
 old.options.onProgress({current:3,total:3});old.options.onSolved({kind:'correct'},receipt(old.seed));
 check(!body.find('nlQuizBack').hidden,'stale previous gate callbacks cannot hide active Return');
 let storageCopy=Array.from(storage);e=boot({storage:storageCopy,requiredTrusted:['required-1']});e.step();m=open(e);
 check(!body.find('nlQuizBack').hidden,'refresh required preparation retains Return before final render');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'refresh validated final render hides Return');
 e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();e.controls.reportFinalThenThrow=true;m=open(e);
 check(!body.find('nlQuizBack').hidden&&!body.find('nlQuizRetry').hidden&&body.find('nlQuizProgress').hidden,'outer mount failure after final progress restores required Return and Retry');
 e=boot({supportsPractice:false});e.step();m=open(e);m.options.onProgress({current:3,total:3});complete(e,m);
 check(!body.find('nlQuizBack').hidden,'adapter without lower practice action retains ordinary required Return');
 print(JSON.stringify({completed:true,checks,additionalFinalHeaderChecks:checks-startChecks,labels,limits:['Actual controller and shared renderer source parsed by system JavaScriptCore; DOM, adapter, storage, trusted answers, abort and loading/error events are declared doubles.','Native rendering, real engine answers, keyboard, focus and browser recovery are supplied separately.']}));
}


function readyHeaderCases(){
 const before=checks;
 let e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();let m=open(e);
 m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'R1 completed required retains Return while final image loading and lower actions unavailable');
 const notify=(mount,value)=>{if(typeof mount.options.onSuccessActionsReady==='function')mount.options.onSuccessActionsReady(value);};
 notify(m,false);check(!body.find('nlQuizBack').hidden,'explicit image loading retains required Return');
 notify(m,true);check(body.find('nlQuizBack').hidden,'actual ready final actions hide required Return');
 const required=clone(e.saved().states[0]);
 notify(m,false);check(!body.find('nlQuizBack').hidden,'image error restores required Return despite final progress and mastery');
 notify(m,false);check(!body.find('nlQuizBack').hidden,'image retry loading retains required Return');
 notify(m,true);check(body.find('nlQuizBack').hidden,'image retry success hides required Return again');
 for(const value of ['true',1,{},null]){notify(m,value);check(!body.find('nlQuizBack').hidden,'nonboolean readiness cannot hide Return '+JSON.stringify(value));}
 notify(m,true);m.options.onProgress(null);m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'null progress clears stale readiness before new final rendering');
 notify(m,true);check(body.find('nlQuizBack').hidden,'new explicit ready event restores completed header');
 const stale=m;body.find('nlQuizDialog').fire('cancel');m=open(e);m.options.onProgress({current:3,total:3});notify(m,true);notify(stale,false);
 check(body.find('nlQuizBack').hidden,'destroyed old readiness callback cannot reopen Return on current completed round');
 equal(e.saved().states[0],required,'readiness changes never mutate exact required receipt');
 m.options.onNewPractice();m=e.latest();notify(m,false);
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional error retains independent Continue and hides Return');
 body.find('nlQuizDialog').fire('cancel');e.step(2);m=open(e);m.options.onProgress({current:3,total:3});notify(m,true);
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,2),'ready actions cannot bypass missing required answers');
 e=boot({supportsPractice:false});e.step();m=open(e);m.options.onProgress({current:3,total:3});complete(e,m);notify(m,true);
 check(!body.find('nlQuizBack').hidden,'ready single-action adapter keeps ordinary Return');
 e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();e.controls.reportFinalThenThrow=true;open(e);
 check(!body.find('nlQuizBack').hidden&&!body.find('nlQuizRetry').hidden,'outer mount failure clears ready-final state and retains Return');
 print(JSON.stringify({completed:true,checks,newReadinessChecks:checks-before,labels,limits:['Actual controller source with explicit DOM/adapter/storage/trusted-answer/readiness doubles.','Real renderer and adapter readiness propagation checked separately; native delayed503/retry checks supplied separately.']}));
}
main().then(finalHeaderCases).then(readyHeaderCases).catch(error=>{print('FAIL '+error.message+' '+error.stack);throw error;});
