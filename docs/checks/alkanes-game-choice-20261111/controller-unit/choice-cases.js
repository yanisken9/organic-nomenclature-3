async function choiceControllerCases() {
  const start=checks;
  function migrating(options={}) {
    const s=scenario(),old=clone(s);old.title='Exact prior lesson';
    const calls=[];
    const e=boot({scenario:s,requiredTrusted:['required-1'],optionalTrusted:['prior-practice'],...options,
      customize(adapter,controls) {
        adapter.migrateRecord=(current,api)=>{
          calls.push(current);
          equal(api.signature(old),signature(old),'migration exposes existing full signature');
          const record=api.read(old);
          return record?{states:record.states,practices:record.practices}:null;
        };
        if(options.customize)options.customize(adapter,controls);
      }});
    const value={version:1,content:signature(old),states:{0:receipt()},practices:{0:receipt('prior-practice',[true,false,false],1)}};
    storage.set(recordKey(old),JSON.stringify(value));
    return {e,s,old,calls,value};
  }
  let x=migrating();const beforeOld=storage.get(recordKey(x.old));x.e.step();
  check(x.calls.length===1&&x.e.C.isComplete(x.s,0),'absent current record invokes represented adapter migration once and normalizes required evidence');
  equal(x.e.saved().practices[0].answers,[true,false,false],'migration restores independent partial optional evidence');
  check(storage.get(recordKey(x.old))===beforeOld&&x.e.saved().content===signature(x.s),'migration persists only new exact-signature key and preserves old bytes');
  x.e.C.reset(x.s);x.e.step();
  check(x.calls.length===1&&!x.e.C.isComplete(x.s,0),'in-memory reset cannot resurrect migrated progress');
  for(const present of ['', 'null', '{invalid', JSON.stringify({version:1,content:signature(scenario()),states:{},practices:{}})]) {
    x=migrating();storage.set(recordKey(x.s),present);x.e.step();
    check(x.calls.length===0&&!x.e.C.isComplete(x.s,0),'present current value suppresses migration even empty/malformed/reset '+present);
  }
  for(const change of ['wrong-content','wrong-version','wrong-answer','array-states']) {
    x=migrating();const value=clone(x.value);
    if(change==='wrong-content')value.content+=' altered';
    if(change==='wrong-version')value.version=2;
    if(change==='wrong-answer')value.states[0].answers=[true,true,false];
    if(change==='array-states')value.states=[];
    storage.set(recordKey(x.old),JSON.stringify(value));x.e.step();
    check(!x.e.C.isComplete(x.s,0),'ineligible or unverified migration stays locked '+change);
  }
  x=migrating({customize(adapter){adapter.migrateRecord=()=>{throw Error('ineligible projection')};}});x.e.step();
  check(!x.e.C.isComplete(x.s,0)&&storage.get(recordKey(x.s))===undefined,'migration exception does not create progress');
  x=migrating();const readKeys=[],get=global.sessionStorage.getItem;
  global.sessionStorage.getItem=key=>{readKeys.push(key);return get(key);};x.e.step();
  check(readKeys.every(key=>key===recordKey(x.s)||key===recordKey(x.old)),'migration reads only current and explicitly projected old key');
  x=migrating();global.sessionStorage.getItem=()=>{throw Error('denied')};x.e.step();
  check(x.calls.length===0&&!x.e.C.isComplete(x.s,0)&&!body.find('nlQuizCheckpoint').querySelector('.nl-quiz-storage-note').hidden,'denied storage never triggers migration and is disclosed');
  x=migrating();const ordinaryRead=global.sessionStorage.getItem;
  global.sessionStorage.getItem=key=>{if(key===recordKey(x.old))throw Error('old-key read denied');return ordinaryRead(key)};x.e.step();
  check(x.calls.length===1&&!x.e.C.isComplete(x.s,0)&&!body.find('nlQuizCheckpoint').querySelector('.nl-quiz-storage-note').hidden,'denied projected-old-key read is disclosed without granting migration');
  x=migrating();const writes=storageWrites;x.e.C.beginPreview(x.s);x.e.step();
  check(x.calls.length===0&&storageWrites===writes&&!x.e.C.isComplete(x.s,0),'author preview bypasses migration and learner storage');

  let otherCalls=0;
  let e=boot({customize(adapter){
    adapter.otherGame=(round,state)=>{otherCalls++;return state.seed.startsWith('practice')?'repair':'builder';};
    adapter.labels=(round,lang)=>({label:lang==='en'?'Choose a game':'Διάλεξε παιχνίδι',instruction:'Τρία σωστά',open:'Άνοιξε επιλογές',done:'Η πρόσβαση κερδήθηκε',revisit:'Δες παιχνίδια',practiceTitle:'Παιχνίδια εξάσκησης',practiceNote:'Η πρόσβαση παραμένει'});
  }});e.step();let m=open(e);
  check(body.find('nlQuizCheckpointHeading').textContent==='Διάλεξε παιχνίδι'&&body.find('nlQuizCheckpointStatus').textContent==='Τρία σωστά'&&body.find('nlQuizOpen').textContent==='Άνοιξε επιλογές','adapter labels apply to heading, instruction and open action');
  check(typeof m.options.onOtherGame==='function'&&typeof m.options.onClose==='function'&&m.options.otherGameLabel==='Άλλο παιχνίδι','supported mount receives other-game label and both guarded callbacks');
  m.options.onOtherGame();check(otherCalls===0&&e.created.length===0,'other-game action cannot bypass missing required access');
  complete(e,m);const required=clone(e.saved().states);
  m.options.onOtherGame();m=e.latest();
  check(m.optional&&e.created.at(-1).config.game==='builder'&&otherCalls===1,'other-game creates separate optional practice with requested game');
  equal(e.saved().states,required,'other-game preserves exact earned required receipt');
  check(body.find('nlQuizDialogTitle').textContent==='Παιχνίδια εξάσκησης'&&body.find('nlQuizPracticeNotice').textContent==='Η πρόσβαση παραμένει','adapter optional labels apply inside reused dialog');
  m.options.onNewPractice();check(e.created.at(-1).config.game===undefined,'same-game action retains adapter default via undefined game');
  let stale=m;m=e.latest();stale.options.onClose();
  check(body.find('nlQuizDialog').open&&!m.destroyed,'stale child close cannot close new mount');
  const count=storageWrites;stale.options.onOtherGame();check(storageWrites===count&&otherCalls===1,'stale other-game callback cannot start or persist practice');
  m.options.onClose();check(!body.find('nlQuizDialog').open&&navigation.length===0&&e.C.isComplete(e.s,0),'current child exit closes to checkpoint and keeps already earned access');
  e=boot();e.step();m=open(e);m.options.onClose();
  check(!body.find('nlQuizDialog').open&&!e.C.isComplete(e.s,0)&&navigation.length===0,'unfinished child exit never unlocks or advances theory');
  e=boot();e.step();m=open(e);
  check(m.options.onOtherGame===undefined&&body.find('nlQuizCheckpointHeading').textContent==='Μικρή στάση για επισκευή','legacy adapter retains repair copy and no third action');

  // R1: repeating the displayed required game must not inherit an older
  // optional attempt of the opposite game through createPractice's previous.
  for(const requiredGame of ['builder','repair']) {
    const opposite=requiredGame==='builder'?'repair':'builder';
    const hookReads=[];
    e=boot({customize(adapter){
      for(const key of ['restore','restorePractice']) {
        const previous=adapter[key];
        adapter[key]=(round,state)=>({...previous(round,state),game:state&&state.game});
      }
      const previous=adapter.createPractice;
      adapter.createPractice=(round,state,options)=>({...previous(round,state,options),game:options.game||(state&&state.game)||'repair'});
      adapter.otherGame=(round,state)=>state.game==='builder'?'repair':'builder';
      adapter.practiceGame=(round,state)=>{hookReads.push(state.game);return state.game;};
    }});e.step();m=open(e);
    const earned={...receipt(m.seed),game:requiredGame};
    m.options.onStateChange(earned);m.options.onSolved({kind:'correct'},earned);
    const requiredBefore=clone(e.saved().states);
    m.options.onOtherGame();m=e.latest();
    check(m.optional&&m.options.initialState.game===opposite,'opposite optional practice established before required reopen '+requiredGame);
    m.options.onClose();m=open(e);
    check(!m.optional&&m.options.initialState.game===requiredGame,'reopen displays original earned game despite opposite saved optional '+requiredGame);
    m.options.onNewPractice();m=e.latest();
    check(e.created.at(-1).config.game===requiredGame&&m.options.initialState.game===requiredGame,'R1 required same-game repeat explicitly follows displayed state '+requiredGame);
    equal(hookReads,[requiredGame],'practiceGame reads displayed required receipt only '+requiredGame);
    equal(e.saved().states,requiredBefore,'same-game routing preserves exact earned required receipt '+requiredGame);
    m.options.onOtherGame();m=e.latest();m.options.onNewPractice();m=e.latest();
    check(e.created.at(-1).config.game===opposite&&m.options.initialState.game===opposite,'R1 optional repeat explicitly follows current optional game '+opposite);
    equal(hookReads,[requiredGame,opposite],'practiceGame reads active optional store for optional repeat '+opposite);
  }
  e=boot();e.step();m=open(e);complete(e,m);m.options.onNewPractice();m=e.latest();m.options.onNewPractice();
  check(e.created.every(value=>value.config.game===undefined),'R1 adapters without practiceGame retain legacy unspecified-game default for required and optional repeats');

  function finalSetup() {
    const e=boot();e.step();const m=open(e);m.options.onProgress({current:3,total:3});
    return {e,m,footer:m.host.querySelector('[data-checkpoint-continue]'),back:body.find('nlQuizBack')};
  }
  for(const mode of ['missing','disabled','hidden','hidden-parent']) {
    const t=finalSetup();
    if(mode==='missing')t.m.host.replaceChildren();
    else if(mode==='disabled')t.footer.disabled=true;
    else if(mode==='hidden')t.footer.hidden=true;
    else t.footer.parentNode.hidden=true;
    complete(t.e,t.m);
    check(!t.back.hidden,'claimed readiness cannot hide required Return without enabled visible footer '+mode);
  }
  for(const mode of ['accepted','rejected']) {
    const t=finalSetup();document.activeElement=t.back;
    t.footer.focus=function(){this.focusCalls++;if(mode==='accepted')document.activeElement=this;};
    complete(t.e,t.m);
    check(mode==='accepted'?(t.back.hidden&&document.activeElement===t.footer):(!t.back.hidden&&document.activeElement===t.back),'required focused Return hides only after safe footer handoff '+mode);
  }
  {
    const t=finalSetup();t.footer.parentNode.className='custom-builder-actions';complete(t.e,t.m);
    check(t.back.hidden,'supported data continuation marker works outside legacy round-next');
  }
  {
    const t=finalSetup();t.footer.removeAttribute('data-checkpoint-continue');complete(t.e,t.m);
    check(t.back.hidden,'legacy round-next first-button fallback remains supported');
  }
  print(JSON.stringify({completed:true,checks,newChoiceControllerChecks:checks-start,labels,limits:[
    'Actual production controller in system JavaScriptCore. DOM, adapters, canonical receipt trust, storage, preparation and focus are declared doubles.',
    'Existing controller regression cases reused with explicit ready-footer DOM; new checks cover migration eligibility, exact key/content, reset precedence, labels, optional-game routing, child exit and guarded focus.',
    'No real chemistry, controlled iframe transport, native browser input/layout or conference reliability claim from these controller unit checks.'
  ]}));
}
