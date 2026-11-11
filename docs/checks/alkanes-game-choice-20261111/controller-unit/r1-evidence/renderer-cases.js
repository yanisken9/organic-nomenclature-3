// Actual renderer; TestElement is an explicit DOM/image-event double.
let checks=0;const labels=[];
Math.random=()=>0.25;
function check(value,label){if(!value)throw Error(label);checks++;labels.push(label)}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label)}
function clone(x){return JSON.parse(JSON.stringify(x))}
function host(){const h=document.createElement('div');document.body.append(h);return h}
function buttons(h){return h.querySelectorAll('.round-next')[0].querySelectorAll('button')}
function button(h,label){const b=h.querySelectorAll('button').find(n=>n.textContent===label);if(!b)throw Error('Missing button '+label);return b}
function loaded(h){const image=h.querySelector('.diagram-image');image.naturalWidth=600;image.onload()}
function failed(h){h.querySelector('.diagram-image').onerror()}
function retry(h){button(h,'Φόρτωσε ξανά τη δομή').click()}
function correct(r){const s=NameleculeRepairEngine.createRoundState(r);if(r.kind==='replace'){s.selectedPartId=r.targetPartId;s.selectedValue=r.correctValue}else s.order=r.correctOrder.slice();return {...s,attempts:1,submitted:true,solved:true}}
function solve(h,r){if(r.kind==='replace'){button(h,r.parts.find(p=>p.id===r.targetPartId).text).click();button(h,r.choices.find(c=>c.value===r.correctValue).label).click()}else{button(h,r.parts.find(p=>p.id===r.movablePartIds[0]).text).click();button(h,'Δεξιά →').click()}button(h,'Έλεγχος').click()}
function snapshot(n){const attrs={...n.attributes};delete attrs['data-checkpoint-continue'];Object.keys(attrs).filter(k=>k==='id'||k==='aria-describedby'||k==='aria-labelledby').forEach(k=>attrs[k]=String(attrs[k]).replace(/nl-repair-\d+-/g,'nl-repair-N-'));return {tag:n.tagName,attrs,className:n.className,id:n.id.replace(/nl-repair-\d+-/g,'nl-repair-N-'),text:n._text,disabled:n.disabled,hidden:!!n.hidden,src:n.src||null,children:n.children.map(snapshot)}}
function defaultSnapshots(source){eval(source);const snapshots=[];for(const r of GAME.sets.flatMap(s=>s.rounds)){const h=host(),s=correct(r);const ui=NameleculeRepairGame.mountRound(h,{round:r,initialState:s});snapshots.push(snapshot(h));loaded(h);snapshots.push(snapshot(h));failed(h);snapshots.push(snapshot(h));retry(h);snapshots.push(snapshot(h));loaded(h);snapshots.push(snapshot(h));ui.destroy();h.remove()}return snapshots}
try{
  const oldSnapshots=defaultSnapshots(beforeRendererSource),newSnapshots=defaultSnapshots(rendererSource);
  equal(newSnapshots,oldSnapshots,'30 legacy default DOM snapshots equal except nonvisual supported continuation marker across all six static rounds');
  eval(rendererSource);
  for(const r of GAME.sets.flatMap(s=>s.rounds)){
    for(const twoActions of [false,true]){
      const h=host(),ready=[],observations=[];let continues=0,practices=0;
      const ui=NameleculeRepairGame.mountRound(h,{round:r,initialState:correct(r),onContinue(){continues++},...(twoActions?{onNewPractice(){practices++}}:{}),onSuccessActionsReady(value){ready.push(value);observations.push({value,buttonCount:buttons(h).length,enabled:buttons(h).every(b=>!b.disabled),solved:uiSafeState()})}});
      function uiSafeState(){return h.querySelector('.feedback').classList.contains('is-success')}
      const tag=r.id+(twoActions?' twoactions':' oneaction');
      equal(ready,[false],'restored loading reports false once '+tag);
      check(buttons(h).length===(twoActions?2:1)&&buttons(h).every(b=>b.disabled),'restored buttons present and disabled '+tag);
      failed(h);failed(h);retry(h);equal(ready,[false],'loading/error/retry false coalesced '+tag);
      loaded(h);equal(ready,[false,true],'restored ready reports true after load '+tag);
      check(observations[1].buttonCount===(twoActions?2:1)&&observations[1].enabled&&observations[1].solved,'true sees actual enabled success DOM '+tag);
      loaded(h);equal(ready,[false,true],'duplicate load coalesced '+tag);
      buttons(h).forEach(b=>b.click());check(continues===1&&practices===(twoActions?1:0),'ready actions preserve callback behavior '+tag);
      const staleLoad=h.querySelector('.diagram-image').onload,staleError=h.querySelector('.diagram-image').onerror;
      failed(h);equal(ready,[false,true,false],'error revokes ready '+tag);
      check(buttons(h).every(b=>b.disabled),'error disables every action '+tag);
      retry(h);equal(ready,[false,true,false],'retry remains false '+tag);
      loaded(h);equal(ready,[false,true,false,true],'successful retry restores ready '+tag);
      const beforeDestroy=clone(ready);ui.destroy();staleLoad();staleError();equal(ready,beforeDestroy,'destroy suppresses captured image callbacks '+tag);h.remove();
    }
    const h=host(),ready=[],events=[];
    const ui=NameleculeRepairGame.mountRound(h,{round:r,onStateChange(s){events.push('state:'+s.solved)},onSolved(){events.push('solved')},onSuccessActionsReady(value){ready.push(value);events.push('ready:'+value);if(value)check(buttons(h).length===1&&buttons(h).every(b=>!b.disabled),'fresh true sees rendered enabled action '+r.id)}});
    equal(ready,[false],'fresh mount reports false '+r.id);loaded(h);equal(ready,[false],'unsolved loaded still false '+r.id);
    check(buttons(h).length===0,'unsolved has no success actions '+r.id);solve(h,r);
    check(ui.getState().solved,'fresh actual UI completes '+r.id);equal(ready,[false,true],'fresh readiness emits only false to true '+r.id);
    check(events.indexOf('state:true')<events.indexOf('ready:true')&&events.indexOf('ready:true')<events.indexOf('solved'),'solved state published then actions ready then solved event '+r.id);
    ui.destroy();h.remove();
  }
  // Force a synchronous ready image to prove solved state alone cannot announce
  // readiness before showSuccess has mounted its real action buttons.
  const descriptor=Object.getOwnPropertyDescriptor(TestElement.prototype,'src');
  Object.defineProperty(TestElement.prototype,'src',{configurable:true,get(){return this._src},set(value){this._src=value;if(this.classList.contains('diagram-image')&&this.onload){this.naturalWidth=600;this.onload()}}});
  const h=host(),seen=[];const ui=NameleculeRepairGame.mountRound(h,{round:GAME.sets[0].rounds[0],initialState:correct(GAME.sets[0].rounds[0]),onSuccessActionsReady(value){seen.push({value,buttons:buttons(h).length,enabled:buttons(h).every(b=>!b.disabled)})}});
  equal(seen.map(x=>x.value),[false,true],'synchronously ready restore first reports false before success DOM');
  check(seen[0].buttons===0&&seen[1].buttons===1&&seen[1].enabled,'synchronously ready restore announces true only after actual actions');ui.destroy();h.remove();
  if(descriptor)Object.defineProperty(TestElement.prototype,'src',descriptor);else delete TestElement.prototype.src;
  for(const r of GAME.sets.flatMap(s=>s.rounds)){
    const h=host(),ready=[];let other=0,practice=0,continued=0;
    const ui=NameleculeRepairGame.mountRound(h,{round:r,initialState:correct(r),onContinue(){continued++},onNewPractice(){practice++},newPracticeLabel:'Same game',onOtherGame(state){other++;check(state.solved,'other game receives validated solved snapshot '+r.id)},otherGameLabel:'Different game',onSuccessActionsReady(value){ready.push(value)}});
    check(buttons(h).length===3&&buttons(h).every(b=>b.disabled),'three restored actions disabled before diagram '+r.id);
    check(buttons(h)[0].getAttribute('data-checkpoint-continue')==='','first continuation has supported marker '+r.id);
    buttons(h).forEach(b=>b.click());check(other===0&&practice===0&&continued===0,'loading actions cannot invoke callbacks '+r.id);
    loaded(h);check(ready.at(-1)===true&&buttons(h).every(b=>!b.disabled),'three enabled actions announce ready '+r.id);
    check(buttons(h)[1].textContent==='Same game'&&buttons(h)[2].textContent==='Different game','three action order and labels '+r.id);
    buttons(h).forEach(b=>b.click());check(other===1&&practice===1&&continued===1,'three actions dispatch distinct callbacks '+r.id);
    const captured=buttons(h)[2].handlers.click[0];failed(h);captured({});check(other===1&&ready.at(-1)===false,'other-game captured callback rejects diagram error '+r.id);
    loaded(h);ui.destroy();captured({});check(other===1,'other-game captured callback rejects destroyed renderer '+r.id);h.remove();
  }
  print(JSON.stringify({passed:true,checks,labels,unchangedDefaultSnapshots:oldSnapshots.length,roundCount:6,renderer:'actual production renderer; TestElement DOM/image events are doubles'}));
}catch(error){print('FAIL '+String(error)+'\n'+error.stack);}
