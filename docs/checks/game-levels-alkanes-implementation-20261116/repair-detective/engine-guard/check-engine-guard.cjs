/* Developer runtime under DOM/native fixtures; this is not browser evidence. */
'use strict';
const fs=require('node:fs'), path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{webcrypto}=require('node:crypto');
const repo=path.resolve(__dirname,'../../../../..');
const Levels=require(path.join(repo,'js/namelecule-game-levels.js'));
const Engine=require(path.join(repo,'js/namelecule-molecular-detective-engine.js'));
const snapshots=require(path.join(repo,'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json'));
const full=require(path.join(repo,'games/data/alkane-structures-v2.json'));
const all=full.molecules.map(m=>m.id),clone=v=>JSON.parse(JSON.stringify(v));
let checks=0;const records=[];function check(label,fn){fn();checks++;records.push(label);}
function surface(){const events=new Map();return{events,addEventListener(t,f){const a=events.get(t)||[];a.push(f);events.set(t,a);},removeEventListener(t,f){events.set(t,(events.get(t)||[]).filter(x=>x!==f));},fire(t,e={}){return Promise.all((events.get(t)||[]).map(f=>f(e)));}};}
function boot(controlled=false,withLevels=true,sourceText=null,withEngine=true){
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
 if(!withLevels)delete context.NameleculeGameLevels;if(!withEngine)delete context.NameleculeMolecularDetectiveEngine;
 context.window=context;context.parent=controlled?{postMessage:d=>outer.push(clone(d))}:context;
 vm.createContext(context);let source=sourceText===null?fs.readFileSync(path.join(repo,'js/namelecule-molecular-detective.js'),'utf8'):sourceText;
 source=source.replace('  start();\n})();','  window.fixture={state,assignment,snapshot,validateLessonLoad,selectAssignment,receive,receiveLesson};\n  start();\n})();');
 vm.runInContext(source,context);
 const emitNative=d=>context.fire('message',{origin:context.location.origin,source:native,data:d});
 const ready=async()=>{await emitNative({channel:'namelecule-molecular-detective-v1',session:context.fixture.state.session,type:'ready',requestId:0,inventory:Engine.starterIds.map(id=>({id}))});};
 const complete=async()=>{const c=commands.at(-1);assert.equal(c.command,'load');const raw=clone(snapshots[c.moleculeId]);const canonicalSource=full.molecules.find(m=>m.id===c.moleculeId);if(canonicalSource)raw.sourceMOL=canonicalSource.mol;await emitNative({...c,type:'round',snapshot:raw});const configuration=commands.at(-1);assert.equal(configuration.command,'configure');const initial=configuration.initialSelection||{atoms:[],bonds:[]};await emitNative({...configuration,type:'configured',selectionRevision:0,...initial});return c;};

 return{context,doc,nodes,commands,outer,get mounted(){return mounted;},ready,complete,emitNative,fixture:context.fixture,select(s){mounted.onSelect(s);},click(id){return doc.getElementById(id).fire('click');},raf,timers};
}
(async()=>{
 const before=fs.readFileSync(path.join(repo,'docs/checks/game-levels-alkanes-implementation-20261116/review-before-engine-guard/js/namelecule-molecular-detective.js'),'utf8');
 const result={recordedUTC:new Date().toISOString(),role:'Developer actual controller VM under DOM/native fixtures; not browser evidence',before:[],after:[],checks:0};
 for(const controlled of [false,true]){
  let caught;try{boot(controlled,true,before,false);}catch(error){caught=error;}
  assert.ok(caught);assert.match(caught.message,/starterIds/);
  result.before.push({mode:controlled?'controlled lesson':'standalone',reproduced:true,error:caught.message});result.checks++;
 }
 if(process.argv.includes('--before-only')){fs.writeFileSync(path.join(__dirname,'before-reproduction.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));return;}
 for(const controlled of [false,true]){
  const x=boot(controlled,true,null,false);
  assert.equal(x.fixture.state.phase,'error');
  assert.equal(x.doc.getElementById('game-status').textContent,'Το παιχνίδι δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.');
  assert.equal(x.doc.getElementById('viewer-mask').hidden,false);
  assert.equal(x.doc.getElementById('retry-load').hidden,controlled);
  assert.equal(x.doc.getElementById('check-answer').disabled,true);
  assert.equal(x.commands.length,0);assert.equal(x.fixture.state.mission,null);
  if(!controlled){await x.click('retry-load');assert.equal(x.fixture.state.phase,'error');assert.equal(x.commands.length,0);}
  result.after.push({mode:controlled?'controlled lesson':'standalone',noException:true,phase:x.fixture.state.phase,greekFailureVisible:true,localRetryVisible:!x.doc.getElementById('retry-load').hidden,nativeCommands:x.commands.length,falseQuiz:false});result.checks++;
 }
 result.limitations=['The controlled lesson intentionally retains existing parent-owned retry behavior; local retry is hidden by fail().','This check does not load a browser or prove recovery after an external engine script failure resolves.'];
 fs.writeFileSync(path.join(__dirname,'after-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
