// Actual adapter + actual renderer + pinned engine/generator. DOM and transport
// are explicit doubles; captured callback probes adversarially simulate renderer.
Math.random=()=>0.25;
let checks=0;const labels=[];
function check(value,label){if(!value)throw Error(label);checks++;labels.push(label)}
function equal(a,b,label){check(JSON.stringify(a)===JSON.stringify(b),label)}
function clone(x){return JSON.parse(JSON.stringify(x))}
async function until(test,label){for(let i=0;i<100&&!test();i++)await Promise.resolve();check(test(),label)}
const analyses=catalog.molecules.map(m=>analyze(m,catalog.engineSHA256));
const digest=Uint8Array.from('9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724'.match(/../g).map(x=>parseInt(x,16)));
global.document.baseURI='http://memory.test/';
global.URL=class{constructor(path,base){this.href=base+path}};
global.TextDecoder=class{decode(bytes){return bytes}};
let timer=0,random=100,fetches=0,analysisRequests=0;const timers=new Map();
global.setTimeout=callback=>{timers.set(++timer,callback);return timer};global.clearTimeout=id=>timers.delete(id);
global.AbortController=class{constructor(){const listeners=new Set();this.signal={aborted:false,addEventListener:(_,cb)=>listeners.add(cb),removeEventListener:(_,cb)=>listeners.delete(cb)};this.abort=()=>{if(!this.signal.aborted){this.signal.aborted=true;Array.from(listeners).forEach(cb=>cb())}}}};
global.crypto={getRandomValues(values){values[0]=++random;values[1]=1234;return values},subtle:{digest:async()=>digest}};
global.fetch=async()=>{fetches++;return {ok:true,arrayBuffer:async()=>JSON.stringify(catalog)}};
global.NameleculeChemistryClient={analyze:async molecule=>{analysisRequests++;return clone(analyses.find(a=>a.moleculeId===molecule.id))}};
let adapter;global.NameleculeQuizCheckpoints={registerType(type,value){check(type==='generated-name-repair-set','registered generated adapter');adapter=value}};
const actualMount=NameleculeRepairGame.mountRound;const mounts=[];
NameleculeRepairGame.mountRound=(host,options)=>{const handle=actualMount(host,options),item={host,options,handle,destroyed:false};const destroy=handle.destroy;handle.destroy=()=>{item.destroyed=true;destroy()};mounts.push(item);return handle};
const recipe={version:1,setId:'alkanes-unbranched',difficulty:'basic',roundCount:3,generatorVersion:'1.0.0',catalogRevision:catalog.revision,engineSHA256:catalog.engineSHA256};
function newAdapter(source=adapterSource){eval(source);return adapter}
function buttons(h){const next=h.querySelector('.round-next');return next?next.querySelectorAll('button'):[]}
function button(h,label){const b=h.querySelectorAll('button').find(n=>n.textContent===label);if(!b)throw Error('Missing button '+label);return b}
function loaded(h){const image=h.querySelector('.diagram-image');image.naturalWidth=600;image.onload()}
function correct(r){const s=NameleculeRepairEngine.createRoundState(r);if(r.kind==='replace'){s.selectedPartId=r.targetPartId;s.selectedValue=r.correctValue}else s.order=r.correctOrder.slice();return {...s,attempts:1,submitted:true,solved:true}}
function solve(session){const item=session.current(),r=item.options.round,h=item.host;if(r.kind==='replace'){button(h,r.parts.find(p=>p.id===r.targetPartId).text).click();button(h,r.choices.find(c=>c.value===r.correctValue).label).click()}else{button(h,r.parts.find(p=>p.id===r.movablePartIds[0]).text).click();button(h,'Δεξιά →').click()}button(h,'Έλεγχος').click();check(item.handle.getState().solved,'actual rendered answer solved '+r.id)}
function mount(a,selected=recipe,initialState=null,practice=false,observe=true,allowPractice=true){const h=document.createElement('div');document.body.append(h);const session={host:h,states:[],latest:null,readiness:[],events:[],solved:0,continued:0,practiceClicks:0,current(){return mounts.findLast(item=>item.host.parentNode===h&&!item.destroyed)}};
  const options={round:selected,initialState,onStateChange(s){session.latest=clone(s);session.states.push(clone(s));session.events.push('state:'+s.currentRound+':'+s.solved)},onSolved(){session.solved++},onContinue(){session.continued++}};
  if(allowPractice)options.onNewPractice=()=>session.practiceClicks++;
  if(observe)options.onSuccessActionsReady=value=>{session.readiness.push(value);session.events.push('ready:'+value);if(value)check(session.latest.currentRound===2&&session.latest.solved&&h.isConnected&&buttons(h).length>0&&buttons(h).every(b=>!b.disabled),'forwarded true requires valid final solved enabled actual DOM')};
  session.handle=(practice?a.mountPractice:a.mount)(h,options);return session}
async function ready(session,label){await until(()=>!!session.current(),label)}
function advance(session){button(session.host,'Επόμενο κουίζ').click()}
function semantic(session){const r=session.current().options.round;return {state:clone(session.latest),round:r.id,progress:session.host.querySelector('.nl-quiz-set-progress').textContent,actions:buttons(session.host).map(b=>({text:b.textContent,disabled:b.disabled,attrs:b.attributes}))}}
(async()=>{
  // Original adapter with new actual renderer: no opt-in, no readiness observer.
  // Compare receipts/default action markup with the actual new adapter at same seed.
  let oldDefault,newDefault;
  for(const source of [beforeAdapterSource,adapterSource]){
    const a=newAdapter(source),s=mount(a,recipe,{version:1,seed:'301234',currentRound:0,states:[null,null,null],solved:false},false,false,false),trace=[];
    await ready(s,'default adapter rendered');
    for(let i=0;i<3;i++){trace.push(semantic(s));loaded(s.host);solve(s);trace.push(semantic(s));if(i<2)advance(s)}
    check(s.latest.solved&&s.solved===1,'default adapter preserves verified success');
    buttons(s.host)[0].click();check(s.continued===1,'default adapter preserves continue');
    if(source===beforeAdapterSource)oldDefault=trace;else newDefault=trace;s.handle.destroy();s.host.remove();
  }
  equal(newDefault,oldDefault,'six default adapter receipt/action snapshots identical to R1');
  const a=newAdapter();
  equal(Object.keys(a.restore(recipe,null)),['version','seed','currentRound','states','solved'],'readiness adds no persisted receipt keys');
  for(const setId of ['alkanes-unbranched','alkanes-branched']){
    const selected={...recipe,setId};
    for(const practice of [false,true]){
      const tag=setId+(practice?' optional':' required'),initial=practice?a.createPractice(selected,null):null;
      const s=mount(a,selected,initial,practice);await ready(s,'initial mount '+tag);
      check(s.readiness.length===1&&s.readiness[0]===false,'first loading false only '+tag);
      const early=s.current();early.options.onSuccessActionsReady(true);check(!s.readiness.includes(true),'forged first ready rejected '+tag);
      for(let i=0;i<3;i++){
        loaded(s.host);solve(s);
        if(i<2){check(!s.readiness.includes(true),'earlier solved round ready forwarded false '+i+' '+tag);const stale=s.current().options.onSuccessActionsReady;advance(s);const count=s.readiness.length;stale(true);equal(s.readiness.length,count,'previous round callback ignored after next '+i+' '+tag)}
      }
      check(s.latest.solved&&s.solved===1&&s.readiness.at(-1)===true,'final real solve makes actions ready '+tag);
      const final=s.current(),earned=clone(s.latest);
      equal(Object.keys(earned),['version','seed','currentRound','states','solved'],'success keeps original receipt keys '+tag);
      final.host.querySelector('.diagram-image').onerror();check(s.readiness.at(-1)===false&&buttons(s.host).every(b=>b.disabled),'image error revokes final actions '+tag);
      button(s.host,'Φόρτωσε ξανά τη δομή').click();check(s.readiness.at(-1)===false,'image retry keeps false '+tag);loaded(s.host);check(s.readiness.at(-1)===true,'loaded retry restores true '+tag);
      buttons(s.host).forEach(b=>b.click());check(s.continued===1&&s.practiceClicks===1,'both existing actions work '+tag);
      const stale=final.options.onSuccessActionsReady,readies=s.readiness.length;s.handle.destroy();stale(true);stale(false);equal(s.readiness.length,readies,'destroy suppresses stale callback '+tag);s.host.remove();
      const reopened=mount(a,selected,earned,practice);await ready(reopened,'restored complete set '+tag);
      equal(reopened.readiness,[false],'complete restore loading false '+tag);check(buttons(reopened.host).length===2&&buttons(reopened.host).every(b=>b.disabled),'complete restore keeps both lower actions disabled '+tag);
      const item=reopened.current(),reveal=item.options.onSuccessActionsReady;
      // Reject non-Boolean truthy readiness, then prove detached round cannot send.
      const count=reopened.readiness.length;reveal('true');check(reopened.readiness.at(-1)===false,'nonboolean readiness rejected '+tag);
      reopened.host.remove();const disconnectedCount=reopened.readiness.length;reveal(true);equal(reopened.readiness.length,disconnectedCount,'disconnected round callback ignored '+tag);document.body.append(reopened.host);
      item.host.querySelector('.diagram-image').onerror();equal(reopened.readiness,[false,false],'restore failure has no true '+tag);
      button(reopened.host,'Φόρτωσε ξανά τη δομή').click();loaded(reopened.host);check(reopened.readiness.at(-1)===true,'restored success true only after image retry loads '+tag);check(reopened.solved===0,'restore readiness does not duplicate solved event '+tag);
      reopened.handle.destroy();reopened.host.remove();
    }
  }
  check(timers.size===0,'all generation timers cleaned');
  print(JSON.stringify({passed:true,checks,labels,defaultSnapshots:6,actualParts:['renderer','generated adapter','repair generator','original pinned chemistry engine'],doubles:['TestElement DOM','explicit image load/error events','fetch/catalog digest transport','AbortController/timers','ChemistryClient transport'],fetches,analysisRequests}));
})().catch(error=>{print('FAIL '+String(error)+'\n'+error.stack)});
