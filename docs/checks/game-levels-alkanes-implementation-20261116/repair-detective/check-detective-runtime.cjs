/* Developer runtime under DOM/native fixtures; this is not browser evidence. */
'use strict';
const fs=require('node:fs'), path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{webcrypto}=require('node:crypto');
const repo=path.resolve(__dirname,'../../../..');
const Levels=require(path.join(repo,'js/namelecule-game-levels.js'));
const Engine=require(path.join(repo,'js/namelecule-molecular-detective-engine.js'));
const snapshots=require(path.join(repo,'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json'));
const full=require(path.join(repo,'games/data/alkane-structures-v2.json'));
const all=full.molecules.map(m=>m.id),clone=v=>JSON.parse(JSON.stringify(v));
let checks=0;const records=[];function check(label,fn){fn();checks++;records.push(label);}
function surface(){const events=new Map();return{events,addEventListener(t,f){const a=events.get(t)||[];a.push(f);events.set(t,a);},removeEventListener(t,f){events.set(t,(events.get(t)||[]).filter(x=>x!==f));},fire(t,e={}){return Promise.all((events.get(t)||[]).map(f=>f(e)));}};}
function boot(controlled=false,withLevels=true){
 const nodes=new Map(),commands=[],outer=[],raf=new Map(),timers=new Map();let serial=0, mounted=null;
 const doc=Object.assign(surface(),{});
 function node(tag='div',id='') {const attrs={},classes=new Set();const n=Object.assign(surface(),{id,tagName:tag.toUpperCase(),dataset:{},style:{setProperty(){}},hidden:false,disabled:false,children:[],isConnected:true,ownerDocument:doc,
 classList:{add(...a){a.forEach(x=>classes.add(x));},remove(...a){a.forEach(x=>classes.delete(x));},toggle(k,f){const v=f===undefined?!classes.has(k):f;v?classes.add(k):classes.delete(k);return v;},contains(k){return classes.has(k);}},
 setAttribute(k,v){attrs[k]=v;},getAttribute(k){return attrs[k];},append(...a){a.forEach(x=>{x.parentNode=this;this.children.push(x);});},appendChild(a){this.append(a);return a;},replaceChildren(...a){this.children=[];this.append(...a);},remove(){this.isConnected=false;},cloneNode(){return node(tag);},querySelectorAll(){return[];},querySelector(){return null;},focus(){doc.activeElement=this;},getBoundingClientRect(){return{top:0,bottom:360,left:0,right:720,width:720,height:360};},setPointerCapture(){},releasePointerCapture(){},hasPointerCapture(){return false;}});return n;}
 Object.assign(doc,{body:node('body'),documentElement:node('html'),createElement:t=>node(t),createElementNS:(_,t)=>node(t),createTextNode:t=>({textContent:t}),querySelectorAll(){return[];},getElementById(id){if(!nodes.has(id))nodes.set(id,node('div',id));return nodes.get(id);}});doc.documentElement.scrollHeight=2000;doc.scrollingElement=doc.documentElement;
 const html=fs.readFileSync(path.join(repo,'games/molecular-detective.html'),'utf8');for(const m of html.matchAll(/\bid="([^"]+)"/g))doc.getElementById(m[1]);
 const native=Object.assign(surface(),{postMessage(d){commands.push(clone(d));}});doc.getElementById('molecule-viewer').contentWindow=native;
 doc.createDocumentFragment=()=>node('fragment');
 const media=Object.assign(surface(),{matches:false});
 const url='http://localhost:57116/games/'+'molecular-detective.html'+(controlled?'?lessonSession=fixture_lesson_0123456789':'?molecule=ethane');
 const context=Object.assign(surface(),{document:doc,location:{href:url,search:new URL(url).search,origin:new URL(url).origin,reload(){}},URL,URLSearchParams,crypto:webcrypto,structuredClone,Uint8Array,Uint32Array,TextEncoder,TextDecoder,AbortController,console,
 NameleculeMolecularDetectiveEngine:Engine,NameleculeGameLevels:{...Levels,mount(host,opts){mounted=opts;return{set(p){Object.assign(mounted,p);},destroy(){}};}},
 NameleculeChemistryClient:{async analyze(m){return{name:snapshots[m.id].correctName};}},async fetch(url){const bytes=fs.readFileSync(path.join(repo,new URL(url).pathname));return{ok:true,async arrayBuffer(){return bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);}};},
 innerWidth:1200,innerHeight:800,scrollX:0,scrollY:0,matchMedia:()=>media,scrollTo(){},setTimeout(f){const id=++serial;timers.set(id,f);return id;},clearTimeout:id=>timers.delete(id),requestAnimationFrame(f){const id=++serial;raf.set(id,f);return id;},cancelAnimationFrame:id=>raf.delete(id),ResizeObserver:class{constructor(f){}observe(){}disconnect(){}}});
 if(!withLevels)delete context.NameleculeGameLevels;
 context.window=context;context.parent=controlled?{postMessage:d=>outer.push(clone(d))}:context;
 vm.createContext(context);let source=fs.readFileSync(path.join(repo,'js/namelecule-molecular-detective.js'),'utf8');
 source=source.replace('  start();\n})();','  window.fixture={state,assignment,snapshot,validateLessonLoad,selectAssignment,receive,receiveLesson};\n  start();\n})();');
 vm.runInContext(source,context);
 const emitNative=d=>context.fire('message',{origin:context.location.origin,source:native,data:d});
 const ready=async()=>{await emitNative({channel:'namelecule-molecular-detective-v1',session:context.fixture.state.session,type:'ready',requestId:0,inventory:Engine.starterIds.map(id=>({id}))});};
 const complete=async()=>{const c=commands.at(-1);assert.equal(c.command,'load');const raw=clone(snapshots[c.moleculeId]);const canonicalSource=full.molecules.find(m=>m.id===c.moleculeId);if(canonicalSource)raw.sourceMOL=canonicalSource.mol;await emitNative({...c,type:'round',snapshot:raw});const configuration=commands.at(-1);assert.equal(configuration.command,'configure');const initial=configuration.initialSelection||{atoms:[],bonds:[]};await emitNative({...configuration,type:'configured',selectionRevision:0,...initial});return c;};

 return{context,doc,nodes,commands,outer,get mounted(){return mounted;},ready,complete,emitNative,fixture:context.fixture,select(s){mounted.onSelect(s);},click(id){return doc.getElementById(id).fire('click');},raf,timers};
}
(async()=>{
 const d=boot();await d.ready();
 check('No default level or molecule query bypass',()=>{assert.equal(d.commands.length,0);assert.equal(d.fixture.state.phase,'choosing');assert.equal(d.mounted.selectedLevel,null);assert.equal(d.mounted.otherCount,13);});
 const seenMissions=new Set();
 for(const level of [1,2,3]){
  d.select({category:'alkanes',level});await d.complete();const size=Levels.poolFor(level).length,seen=[];
  for(let i=0;i<size*3;i++){
   const {state}=d.fixture;seen.push(state.moleculeId);seenMissions.add(state.mission.id);
   check('Level '+level+' draw '+i+' has one allowed mission and preserves alternatives',()=>{assert.equal(state.missions.length,1);assert.ok(level===1||state.mission.family!=='single-bonds');assert.deepEqual(clone(state.mission),Engine.missions(snapshots[state.moleculeId]).find(m=>m.id===state.mission.id));if(state.moleculeId==='methane')assert.equal(state.mission.family,'parent-chain');});
   const mission=state.mission,picks={atoms:[],bonds:[]};picks[mission.kind]=mission.accepted[0];const config=d.commands.at(-1);
   await d.emitNative({...config,type:'selection',selectionRevision:state.selectionRevision+1,...picks});await d.click('check-answer');
   assert.equal(d.fixture.state.correct,true);
   if(i<size*3-1){await d.click('next-mission');await d.complete();}
  }
  check('Level '+level+' exhausts three bags without immediate repeat',()=>{assert.ok(seen.every(id=>Levels.levelFor(id)===level));for(let i=0;i<3;i++)assert.equal(new Set(seen.slice(size*i,size*(i+1))).size,size);assert.ok(seen.every((id,i)=>!i||id!==seen[i-1]));});
 }
 // Round IDs reject old replies even when a later draw uses the same molecule.
 d.select({category:'alkanes',level:1});const abandoned=d.commands.at(-1);d.select({category:'alkanes',level:2});const active=d.commands.at(-1);
 await d.emitNative({...abandoned,type:'round',snapshot:clone(snapshots[abandoned.moleculeId])});
 check('Level switch invalidates delayed native reply',()=>{assert.equal(d.fixture.state.phase,'loading');assert.equal(d.fixture.state.roundId,active.roundId);assert.equal(d.fixture.state.snapshot,null);});await d.complete();
 const partial=clone(d.fixture.state);await d.emitNative({...d.commands.at(-1),type:'selection',selectionRevision:1,atoms:partial.mission.kind==='atoms'?[partial.mission.accepted[0][0]]:[],bonds:partial.mission.kind==='bonds'?[partial.mission.accepted[0][0]]:[]});await d.click('check-answer');const expected=clone(d.fixture.snapshot());
 d.select({category:'alkanes',level:3});await d.complete();d.select({category:'alkanes',level:2});await d.complete();
 check('Level switch preserves its current raw selection and exact mission in bounded memory',()=>{assert.equal(d.fixture.state.moleculeId,partial.moleculeId);assert.equal(d.fixture.state.mission.id,partial.mission.id);assert.deepEqual(clone(d.fixture.snapshot()),expected);assert.equal(d.fixture.assignment.slots.size,3);});
 d.select({category:'other',level:null});await d.complete();const seen=[];
 for(let i=0;i<26;i++){const s=d.fixture.state;seen.push(s.moleculeId);check('Other draw '+i+' uses an existing unfiltered valid mission',()=>{assert.ok(!all.includes(s.moleculeId));assert.equal(s.missions.length,1);assert.deepEqual(clone(s.mission),Engine.missions(snapshots[s.moleculeId]).find(m=>m.id===s.mission.id));});if(i<25){s.correct=true;await d.click('next-mission');await d.complete();}}
 check('Other13 category exhausts twice and has no levels',()=>{assert.equal(new Set(seen.slice(0,13)).size,13);assert.equal(new Set(seen.slice(13)).size,13);assert.equal(d.fixture.assignment.level,null);assert.equal(d.fixture.assignment.slots.size,4);assert.ok(seen.every((id,i)=>!i||id!==seen[i-1]));});
 d.select({category:'alkanes',level:null});check('Returning to alkanes waits for explicit level',()=>{assert.equal(d.fixture.state.moleculeId,null);assert.equal(d.nodes.get('check-answer').disabled,true);});
 const old=boot(true,false);await old.ready();
 const packet=id=>{const s=clone(snapshots[id]);s.sourceMOL=full.molecules.find(m=>m.id===id).mol;return{requestId:1,attemptId:'fixture-attempt',moleculeId:id,snapshot:s,missionId:Engine.missions(s)[0].id,explanation:'fixture explanation'};};
 check('Legacy parent loads known8 without common module',()=>{assert.equal(old.fixture.validateLessonLoad(packet('ethane')).moleculeId,'ethane');assert.throws(()=>old.fixture.validateLessonLoad(packet('methyl_2_butane')));});
 const modern=boot(true);await modern.ready();
 for(const id of all){const p=packet(id);p.context=Levels.makeContext({source:'enriched',level:Levels.levelFor(id),seed:'71'});check('Controlled14 accepts exact source band '+id,()=>{assert.equal(modern.fixture.validateLessonLoad(p).moleculeId,id);});for(const [key,value]of[['catalogSHA256','0'.repeat(64)],['level',Levels.levelFor(id)===1?2:1],['seed',null],['extra','x']]){const bad=clone(p);bad.context[key]=value;check('Controlled context rejects '+id+' '+key,()=>assert.throws(()=>modern.fixture.validateLessonLoad(bad)));}}
 const bad=packet('methyl_2_butane');bad.context=Levels.makeContext({source:'enriched',level:2,seed:'1'});bad.missionId=Engine.missions(bad.snapshot).find(m=>m.family==='single-bonds').id;
 check('Controlled L2/3 cannot inject a single-bond mission',()=>assert.throws(()=>modern.fixture.validateLessonLoad(bad)));
 check('Legacy input cannot silently fallback from present invalid context',()=>{const p=packet('ethane');p.context={};assert.throws(()=>modern.fixture.validateLessonLoad(p));});
 const controlled=packet('ethyl_3_pentane');controlled.context=Levels.makeContext({source:'enriched',level:2,seed:'123'});
 modern.fixture.receiveLesson({origin:modern.context.location.origin,source:modern.context.parent,data:{channel:'namelecule-detective-lesson-v1',session:'fixture_lesson_0123456789',command:'load',...controlled}});await modern.complete();
 check('Controlled loaded echoes exact normalized context and ignores child solved',()=>{const loaded=modern.outer.findLast(x=>x.type==='loaded');assert.ok(loaded);assert.equal(Levels.contextKey(loaded.context),Levels.contextKey(controlled.context));assert.equal(loaded.state.submitted,false);assert.equal(modern.fixture.state.correct,false);});
 const selected=modern.fixture.state.mission.accepted[0],raw={atoms:[],bonds:[]};raw[modern.fixture.state.mission.kind]=selected;await modern.emitNative({...modern.commands.at(-1),type:'selection',selectionRevision:1,...raw});await modern.click('check-answer');
 check('Controlled state publishes raw accepted picks with context for parent regrading',()=>{const update=modern.outer.findLast(x=>x.type==='state');assert.ok(update);assert.equal(Levels.contextKey(update.context),Levels.contextKey(controlled.context));assert.deepEqual(update.state[modern.fixture.state.mission.kind],selected);assert.equal(update.state.submitted,true);assert.equal(update.state.solved,undefined);});
 const result={recordedUTC:new Date().toISOString(),role:'Developer',scope:'Actual Detective controller in DOM/native fixtures; no browser, visual or physical-device claim',checks,passed:checks,distinctMissionsSeen:seenMissions.size,records};fs.writeFileSync(path.join(__dirname,'detective-runtime-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({checks,passed:checks}));
})().catch(e=>{console.error(e);process.exitCode=1;});
