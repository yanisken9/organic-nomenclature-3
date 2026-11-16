/* Developer VM controller checks. DOM/native/analysis are fixtures; no browser claim. */
'use strict';
const fs=require('node:fs'), path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{webcrypto}=require('node:crypto');
const repo=path.resolve(__dirname,'../../../..');
const Levels=require(path.join(repo,'js/namelecule-game-levels.js'));
const Builder=require(path.join(repo,'js/namelecule-name-builder-engine.js'));
const Pctx={};vm.createContext(Pctx);vm.runInContext(fs.readFileSync(path.join(repo,'js/namelecule-molecular-puzzle-engine.js'),'utf8'),Pctx);const Puzzle=Pctx.NameleculeMolecularPuzzleEngine;
const snapshots=require(path.join(repo,'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json'));
const full=require(path.join(repo,'games/data/alkane-structures-v2.json'));
const all=full.molecules.map(m=>m.id),clone=v=>JSON.parse(JSON.stringify(v));
let checks=0;const records=[];function check(label,fn){fn();checks++;records.push(label);}
function surface(){const events=new Map();return{events,addEventListener(t,f){const a=events.get(t)||[];a.push(f);events.set(t,a);},removeEventListener(t,f){events.set(t,(events.get(t)||[]).filter(x=>x!==f));},fire(t,e={}){return Promise.all((events.get(t)||[]).map(f=>f(e)));}};}
function boot(game,controlled=false,options={}){
 const nodes=new Map(),commands=[],outer=[],raf=new Map(),timers=new Map();let serial=0, mounted=null;
 const doc=Object.assign(surface(),{});
 function node(tag='div',id='') {const attrs={},classes=new Set();const n=Object.assign(surface(),{id,tagName:tag.toUpperCase(),dataset:{},style:{setProperty(){}},hidden:false,disabled:false,children:[],isConnected:true,ownerDocument:doc,
 classList:{add(...a){a.forEach(x=>classes.add(x));},remove(...a){a.forEach(x=>classes.delete(x));},toggle(k,f){const v=f===undefined?!classes.has(k):f;v?classes.add(k):classes.delete(k);return v;},contains(k){return classes.has(k);}},
 setAttribute(k,v){attrs[k]=v;},getAttribute(k){return attrs[k];},removeAttribute(k){delete attrs[k];},append(...a){a.forEach(x=>{x.parentNode=this;this.children.push(x);});},appendChild(a){this.append(a);return a;},replaceChildren(...a){this.children=[];this.append(...a);},remove(){this.isConnected=false;},cloneNode(){return node(tag);},querySelectorAll(){return[];},querySelector(){return null;},focus(){doc.activeElement=this;},getBoundingClientRect(){return{top:0,bottom:360,left:0,right:720,width:720,height:360};},setPointerCapture(){},releasePointerCapture(){},hasPointerCapture(){return false;}});return n;}
 Object.assign(doc,{body:node('body'),documentElement:node('html'),createElement:t=>node(t),createElementNS:(_,t)=>node(t),createTextNode:t=>({textContent:t}),querySelectorAll(){return[];},getElementById(id){if(!nodes.has(id))nodes.set(id,node('div',id));return nodes.get(id);}});doc.documentElement.scrollHeight=2000;doc.scrollingElement=doc.documentElement;
 const html=fs.readFileSync(path.join(options.before?path.join(repo,'docs/checks/game-levels-alkanes-implementation-20261116/before'):repo,game==='builder'?'games/name-builder.html':'games/molecular-puzzle.html'),'utf8');for(const m of html.matchAll(/\bid="([^"]+)"/g))doc.getElementById(m[1]);
 const native=Object.assign(surface(),{postMessage(d){commands.push(clone(d));}});doc.getElementById('molecule-viewer').contentWindow=native;
 const media=Object.assign(surface(),{matches:false});
 const url='http://localhost:57116/games/'+(game==='builder'?'name-builder.html':'molecular-puzzle.html')+(controlled?'?lessonSession=fixture_lesson_0123456789':'?molecule=ethane');
 const context=Object.assign(surface(),{document:doc,location:{href:url,search:new URL(url).search,origin:new URL(url).origin,reload(){}},URL,URLSearchParams,crypto:webcrypto,Uint8Array,Uint32Array,TextEncoder,TextDecoder,AbortController,console,
 NameleculeNameBuilderEngine:Builder,NameleculeMolecularPuzzleEngine:Puzzle,NameleculeGameLevels:{...Levels,mount(host,opts){mounted=opts;return{set(p){Object.assign(mounted,p);},destroy(){}};}},
 NameleculeChemistryClient:{async analyze(m){return{name:snapshots[m.id].correctName};}},async fetch(url){const bytes=fs.readFileSync(path.join(repo,new URL(url).pathname));return{ok:true,async arrayBuffer(){return bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);}};},
 innerWidth:1200,innerHeight:800,scrollX:0,scrollY:0,matchMedia:()=>media,scrollTo(){},setTimeout(f){const id=++serial;timers.set(id,f);return id;},clearTimeout:id=>timers.delete(id),requestAnimationFrame(f){const id=++serial;raf.set(id,f);return id;},cancelAnimationFrame:id=>raf.delete(id),ResizeObserver:class{constructor(f){}observe(){}disconnect(){}}});
 context.window=context;context.parent=controlled?{postMessage:d=>outer.push(clone(d))}:context;
 if(options.noLevels)context.NameleculeGameLevels=undefined;
 vm.createContext(context);let source=fs.readFileSync(path.join(options.before?path.join(repo,'docs/checks/game-levels-alkanes-implementation-20261116/before'):repo,game==='builder'?'js/namelecule-name-builder.js':'js/namelecule-molecular-puzzle.js'),'utf8');
 const end=game==='builder'?'})();':'}());';const at=source.lastIndexOf(end);source=source.slice(0,at)+(options.before?(game==='builder'?'window.fixture={state,snapshot};':'window.fixture={snapshot,get current(){return current;},get catalog(){return catalog;},get busy(){return busy;}};'):(game==='builder'?'window.fixture={state,practice,snapshot,validateLessonLoad};':'window.fixture={practice,snapshot,get current(){return current;},get catalog(){return catalog;},get busy(){return busy;},setGraph(value){graph=value;}};'))+source.slice(at);
 vm.runInContext(source,context);
 const emitNative=d=>context.fire('message',{origin:context.location.origin,source:native,data:d});
 const ready=async()=>{if(game==='builder'){const session=new URL(doc.getElementById('molecule-viewer').src,'http://localhost/games/').searchParams.get('session');await emitNative({channel:'namelecule-name-builder-v1',session,type:'ready',inventory:[...all,...Array.from({length:133},(_,i)=>'other_'+i)].map(id=>({id,representations:['condensed','expanded','skeletal','3d']}))});}else{for(let i=0;i<150&&!mounted&&!outer.some(x=>x.type==='ready');i++)await new Promise(r=>setImmediate(r));}};
 const complete=async(override=null)=>{const c=commands.at(-1),s=snapshots[c.moleculeId]||snapshots.ethane;assert.equal(c.command,'load');const raw={...clone(s),...c,roundId:c.roundId,moleculeId:c.moleculeId,series:all.includes(c.moleculeId)?'alkanes':'other',parentLength:2,vocabulary:{roots:['μεθ','αιθ','προπ','βουτ','πεντ','εξ']},representations:['condensed','expanded','skeletal','3d'],...(override||{})};await emitNative({...raw,type:'round'});await new Promise(r=>setImmediate(r));return c;};
 const lessonLoad=async(data,extra={})=>context.fire('message',{origin:context.location.origin,source:context.parent,data:{channel:game==='builder'?'namelecule-builder-lesson-v1':'namelecule-puzzle-lesson-v1',session:'fixture_lesson_0123456789',command:'load',...data},...extra});
 return{context,doc,nodes,commands,outer,lessonLoad,get mounted(){return mounted;},ready,complete,emitNative,fixture:context.fixture,select(s){mounted.onSelect(s);},click(id){return doc.getElementById(id).fire('click');},raf,timers};
}
(async()=>{
 const beforeBuilder=boot('builder',false,{before:true});await beforeBuilder.ready();const beforePuzzle=boot('puzzle',false,{before:true});await beforePuzzle.ready();
 check('Recorded before Builder eagerly assigns ethane and accepts URL molecule selection',()=>{assert.equal(beforeBuilder.commands.at(-1).command,'load');assert.equal(beforeBuilder.commands.at(-1).moleculeId,'ethane');});
 check('Recorded before Puzzle eagerly starts methane and exposes full molecule dropdown',()=>{assert.equal(beforePuzzle.fixture.current.id,'methane');assert.equal(beforePuzzle.nodes.get('round-select').children.length,14);});
 const b=boot('builder');await b.ready();
 check('Builder waits for explicit level and ignores former molecule URL bypass',()=>{assert.equal(b.commands.length,0);assert.equal(b.fixture.state.round,null);assert.equal(b.mounted.selectedLevel,null);assert.equal(b.mounted.otherCount,133);assert.equal(b.nodes.get('next-molecule').disabled,true);});
 for(const level of [1,2,3]){
  b.select({category:'alkanes',level});await b.complete();const size=Levels.poolFor(level).length,seen=[];
  for(let i=0;i<size*2;i++){seen.push(b.fixture.state.round.moleculeId);if(i<size*2-1){await b.click('next-molecule');await b.complete();}}
  check('Builder level '+level+' uses two complete bags without immediate repeats',()=>{assert.ok(seen.every(id=>Levels.levelFor(id)===level));assert.equal(new Set(seen.slice(0,size)).size,size);assert.equal(new Set(seen.slice(size)).size,size);assert.ok(seen.every((id,i)=>!i||id!==seen[i-1]));});
 }
 const before=clone(b.fixture.state.round);const first=b.fixture.state.bank[0];b.fixture.state.answer=[first.id];b.fixture.state.selected=first.id;b.fixture.state.attempts=2;
 b.select({category:'alkanes',level:1});const abandoned=b.commands.at(-1);b.select({category:'alkanes',level:2});const active=b.commands.at(-1);
 await b.emitNative({...abandoned,type:'round',...snapshots[abandoned.moleculeId]});await new Promise(r=>setImmediate(r));
 check('Builder rejects stale native response after level change',()=>{assert.equal(b.fixture.state.round,null);assert.equal(b.commands.at(-1).roundId,active.roundId);});await b.complete();
 b.select({category:'alkanes',level:3});await b.complete();
 check('Builder restores partial tile evidence and same bank for level',()=>{assert.equal(b.fixture.state.round.moleculeId,before.moleculeId);assert.equal(b.fixture.state.round.roundId,before.roundId);assert.deepEqual(clone(b.fixture.state.answer),[first.id]);assert.equal(b.fixture.state.selected,first.id);assert.equal(b.fixture.state.attempts,2);});
 b.select({category:'other',level:null});await b.complete();check('Builder preserves other133 through automatic assignment',()=>{assert.match(b.fixture.state.round.moleculeId,/^other_/);assert.equal(b.fixture.practice.slots.size,4);});
 b.select({category:'alkanes',level:null});check('Returning to alkane category waits for level',()=>{assert.equal(b.fixture.state.round,null);assert.equal(b.nodes.get('next-molecule').disabled,true);});
 const p=boot('puzzle');await p.ready();
 check('Puzzle waits for explicit level and removes molecule dropdown',()=>{assert.ok(p.mounted);assert.equal(p.fixture.current,null);assert.equal(p.fixture.catalog.length,14);assert.equal(p.fixture.busy,true);assert.ok(!fs.readFileSync(path.join(repo,'games/molecular-puzzle.html'),'utf8').includes('round-select'));});
 for(const level of [1,2,3]){
  p.select({category:'alkanes',level});const size=Levels.poolFor(level).length,seen=[];
  for(let i=0;i<size*2;i++){seen.push(p.fixture.current.id);if(i<size*2-1)await p.click('next-molecule');}
  check('Puzzle level '+level+' uses two complete bags without immediate repeats',()=>{assert.ok(seen.every(id=>Levels.levelFor(id)===level));assert.equal(new Set(seen.slice(0,size)).size,size);assert.equal(new Set(seen.slice(size)).size,size);assert.ok(seen.every((id,i)=>!i||id!==seen[i-1]));});
 }
 const expected={nodes:[{id:'piece-1',hydrogens:3,x:120,y:130}],bonds:[]},id=p.fixture.current.id;p.fixture.setGraph(expected);
 p.select({category:'alkanes',level:1});p.select({category:'alkanes',level:3});
 check('Puzzle restores graph in bounded3slots after level switch',()=>{assert.equal(p.fixture.current.id,id);assert.deepEqual(clone(p.fixture.snapshot().graph),expected);assert.equal(p.fixture.practice.slots.size,3);});
 function roundFor(id,context,roundId='lesson-round'){
  const roots=['μεθ','αιθ','προπ','βουτ','πεντ','εξ'];const fact=snapshots[id];const rootText=fact.pieces.find(p=>p.mode==='compCarbonsCount').text;
  const rootCount=context?.source==='enriched'?(context.level<3?5:6):(all.indexOf(id)<5?5:6);
  return{moleculeId:id,roundId,correctName:fact.correctName,pieces:fact.pieces,series:'alkanes',parentLength:roots.indexOf(rootText)+1,vocabulary:{roots:roots.slice(0,rootCount)},representations:['condensed','expanded','skeletal','3d']};
 }
 function builderPacket(id,context,requestId){const round=roundFor(id,context,'lesson-round-'+requestId),bankSeed='bank-'+requestId,bank=Builder.createBank(round,{seed:bankSeed}),used=new Set();const answer=round.pieces.map(p=>{const t=bank.find(t=>t.text===p.text&&!used.has(t.id));used.add(t.id);return t.id;});return{requestId,attemptId:'attempt-'+requestId,moleculeId:id,round,bankSeed,explanation:'Εξήγηση.',...(context?{context}:{}),initialState:{answer,selected:null,attempts:1,submitted:true}};}
 function puzzlePacket(id,context,requestId){const target=Puzzle.parseMol(full.molecules.find(m=>m.id===id).mol);target.nodes.forEach((n,i)=>{n.x=70+i*30;n.y=130;});return{requestId,attemptId:'attempt-'+requestId,moleculeId:id,correctName:snapshots[id].correctName,...(context?{context}:{}),initialState:{graph:target,attempts:1,submitted:true}};}
 const bl=boot('builder',true);await bl.ready();let requestId=0;
 for(const id of all){const context=Levels.makeContext({source:'enriched',level:Levels.levelFor(id),seed:String(++requestId)}),packet=builderPacket(id,context,requestId);await bl.lessonLoad(packet);await bl.complete(packet.round);check('Builder controlled full14 native/fullname/pieces/context and raw solved restore: '+id,()=>{const loaded=bl.outer.findLast(m=>m.type==='loaded');assert.equal(loaded.moleculeId,id);assert.equal(Levels.contextKey(loaded.context),Levels.contextKey(context));assert.deepEqual(loaded.state,packet.initialState);assert.equal(bl.fixture.state.solved,true);assert.equal(bl.nodes.get('game-levels').hidden,true);});}
 const nativeCount=bl.commands.length,previous=bl.fixture.state.round.moleculeId;
 for(const context of [{...Levels.makeContext({source:'enriched',level:2,seed:'50'}),catalogSHA256:'0'.repeat(64)},null,{...Levels.makeContext({source:'enriched',level:2,seed:'50'}),extra:true},Levels.makeContext({source:'enriched',level:1,seed:'50'})]){
  const packet=builderPacket('methyl_2_butane',Levels.makeContext({source:'enriched',level:2,seed:'50'}),++requestId);packet.context=context;await bl.lessonLoad(packet);
 }
 check('Builder rejects present null/unknown/mixed/SHA-invalid contexts without legacy fallback',()=>{assert.equal(bl.commands.length,nativeCount);assert.equal(bl.fixture.state.round.moleculeId,previous);});
 const legacyBuilder=boot('builder',true,{noLevels:true});await legacyBuilder.ready();const oldB=builderPacket('dimethyl_2_3_butane',null,1);await legacyBuilder.lessonLoad(oldB);await legacyBuilder.complete(oldB.round);
 check('Builder legacy8 old-parent load works without Levels module',()=>{assert.equal(legacyBuilder.outer.findLast(m=>m.type==='loaded').moleculeId,'dimethyl_2_3_butane');assert.equal(legacyBuilder.outer.findLast(m=>m.type==='loaded').context,undefined);});
 const noCtxNew=builderPacket('methyl_2_butane',null,2);await legacyBuilder.lessonLoad(noCtxNew);check('Builder absent context cannot expand legacy8 allowlist',()=>{assert.equal(legacyBuilder.outer.at(-1).type,'error');assert.equal(legacyBuilder.fixture.state.round.moleculeId,'dimethyl_2_3_butane');});
 const pl=boot('puzzle',true);await pl.ready();requestId=0;
 check('Puzzle controlled startup pins legacy8 before new context',()=>{assert.equal(pl.fixture.catalog.length,8);assert.equal(pl.outer.findLast(m=>m.type==='ready').context,undefined);});
 for(const id of all){const context=Levels.makeContext({source:'enriched',level:Levels.levelFor(id),seed:String(++requestId)}),packet=puzzlePacket(id,context,requestId);await pl.lessonLoad(packet);check('Puzzle controlled full14 verified catalog/graph/name/context and raw solved restore: '+id,()=>{const loaded=pl.outer.findLast(m=>m.type==='loaded');assert.equal(loaded.moleculeId,id);assert.equal(Levels.contextKey(loaded.context),Levels.contextKey(context));assert.equal(loaded.state.submitted,true);assert.equal(Puzzle.grade(loaded.state.graph,pl.fixture.current.target).correct,true);assert.equal(pl.fixture.catalog.length,14);assert.equal(pl.nodes.get('game-levels').hidden,true);});}
 const loadedCount=pl.outer.filter(m=>m.type==='loaded').length;
 const wrongIdentity=puzzlePacket('methyl_2_butane',Levels.makeContext({source:'enriched',level:2,seed:'50'}),requestId+1);await pl.lessonLoad(wrongIdentity,{origin:'http://wrong'});await pl.lessonLoad(wrongIdentity,{source:{}});await pl.lessonLoad({...wrongIdentity,session:'wrong'});await pl.lessonLoad({...wrongIdentity,requestId});
 check('Puzzle ignores wrong origin/source/session and replayed parent request',()=>{assert.equal(pl.outer.filter(m=>m.type==='loaded').length,loadedCount);assert.equal(pl.fixture.current.id,all.at(-1));});
 for(const context of [null,{...Levels.makeContext({source:'enriched',level:2,seed:'50'}),engineSHA256:'0'.repeat(64)},Levels.makeContext({source:'enriched',level:1,seed:'50'})]){const packet=puzzlePacket('methyl_2_butane',null,++requestId);packet.context=context;await pl.lessonLoad(packet);}
 check('Puzzle rejects null, wrong engine and wrong-level context without new loaded response',()=>{assert.equal(pl.outer.filter(m=>m.type==='loaded').length,loadedCount);});
 const forged=puzzlePacket('methyl_2_butane',Levels.makeContext({source:'enriched',level:2,seed:'50'}),++requestId);forged.correctName='λάθος';await pl.lessonLoad(forged);
 check('Puzzle mismatched canonical parent name is rejected after verified source analysis',()=>{assert.equal(pl.outer.filter(m=>m.type==='loaded').length,loadedCount);assert.equal(pl.outer.at(-1).type,'error');});
 const legacyCtx=Levels.makeContext({source:'legacy',level:null,seed:'60'}),oldP=puzzlePacket('dimethyl_2_3_butane',legacyCtx,++requestId);await pl.lessonLoad(oldP);
 check('Puzzle can switch verified14 back to exact legacy8 context',()=>{assert.equal(pl.fixture.catalog.length,8);assert.equal(pl.outer.findLast(m=>m.type==='loaded').moleculeId,'dimethyl_2_3_butane');assert.equal(Levels.contextKey(pl.outer.findLast(m=>m.type==='loaded').context),Levels.contextKey(legacyCtx));});
 const legacyPuzzle=boot('puzzle',true,{noLevels:true});await legacyPuzzle.ready();await legacyPuzzle.lessonLoad(puzzlePacket('ethane',null,1));
 check('Puzzle legacy8 old-parent load works without Levels module',()=>{assert.equal(legacyPuzzle.outer.findLast(m=>m.type==='loaded').moleculeId,'ethane');assert.equal(legacyPuzzle.outer.findLast(m=>m.type==='loaded').context,undefined);});
 const race=boot('puzzle',true);await race.ready();let release;let firstAnalysis=true;race.context.NameleculeChemistryClient.analyze=async m=>{if(firstAnalysis){firstAnalysis=false;await new Promise(r=>release=r);}return{name:snapshots[m.id].correctName};};
 const oldPending=race.lessonLoad(puzzlePacket('methyl_2_butane',Levels.makeContext({source:'enriched',level:2,seed:'80'}),1));for(let i=0;i<30&&!release;i++)await new Promise(r=>setImmediate(r));assert.ok(release);await race.lessonLoad(puzzlePacket('butane',null,2));release();await oldPending;
 check('Puzzle late enriched source response cannot replace newer warm legacy context',()=>{assert.equal(race.fixture.catalog.length,8);assert.equal(race.fixture.current.id,'butane');assert.equal(race.outer.findLast(m=>m.type==='loaded').requestId,2);assert.ok(!race.outer.some(m=>m.type==='loaded'&&m.requestId===1));});
 check('Both runtimes remain syntax-valid',()=>{new vm.Script(fs.readFileSync(path.join(repo,'js/namelecule-name-builder.js'),'utf8'));new vm.Script(fs.readFileSync(path.join(repo,'js/namelecule-molecular-puzzle.js'),'utf8'));});
 const result={recordedUTC:new Date().toISOString(),role:'Developer',scope:'Actual runtime controllers under DOM/native/analysis fixtures; not browser/visual verification',checks,passed:checks,records};fs.writeFileSync(path.join(__dirname,'runtime-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
