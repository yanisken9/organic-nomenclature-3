/* Developer memory checks; no DOM layout, browser or independent-review claim. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {createHash, webcrypto} = require('node:crypto');
const ROOT = path.resolve(__dirname, '../../../..');
const read = file => fs.readFileSync(path.join(ROOT, file));
const json = file => JSON.parse(read(file));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const report = [];
function check(condition, label) { assert.ok(condition, label); report.push({label, passed:true}); }
const catalog = json('games/data/alkane-structures-v2.json');
const legacy = json('games/data/alkane-structures.json');
const plan = json('docs/checks/four-games-roadmap-preflight-20261116/pool-first-plan.json');
const pack = json('data/namelecule-alkanes-v1/manifest.json');
const engineContext = vm.createContext({});
vm.runInContext(read('js/namelecule-molecular-puzzle-engine.js').toString(), engineContext);
const E = engineContext.NameleculeMolecularPuzzleEngine;
const Builder = require(path.join(ROOT, 'js/namelecule-name-builder-engine.js'));
const core = read('js/chemistry-engines/' + catalog.engineSHA256 + '.js').toString();
const worker = read('js/namelecule-chemistry-worker.js').toString();
const analyses = new Map();
for (const molecule of catalog.molecules) {
  let result;
  const context = vm.createContext({URL, console});
  context.self = {location:{origin:'http://memory.test'}, postMessage:message => {result=message;}, close(){}};
  context.importScripts = () => vm.runInContext(core, context);
  vm.runInContext(worker, context);
  context.self.onmessage({data:{type:'analyze', requestId:'memory-' + molecule.id, molecule,
    engineSHA256:catalog.engineSHA256, engineURL:'blob:http://memory.test/verified-snapshot'}});
  check(result?.type === 'result', 'actual pinned worker/core accepts ' + molecule.id);
  analyses.set(molecule.id, result.result);
}
check(hash(read('games/data/alkane-structures.json')) === '9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724', 'legacy catalog exact bytes preserved');
check(JSON.stringify(catalog.molecules.slice(0,8)) === JSON.stringify(legacy.molecules), 'all eight legacy entries imported exactly');
check(catalog.molecules.length === 14 && new Set(catalog.molecules.map(m => m.id)).size === 14, '14 unique catalog molecules');
check(catalog.source.legacy.sha256 === hash(read(catalog.source.legacy.file)) && catalog.source.legacy.revision === legacy.revision, 'legacy provenance matches actual bytes');
check(catalog.source.pack.sha256 === hash(read(catalog.source.pack.file)), 'pack provenance matches actual bytes');
const {revision, ...payload} = catalog;
function canonical(value) { return Array.isArray(value) ? value.map(canonical) : value && typeof value === 'object'
  ? Object.fromEntries(Object.keys(value).sort().map(key => [key,canonical(value[key])])) : value; }
check(hash(Buffer.from(JSON.stringify(canonical(payload)))) === revision, 'canonical version2 payload reproduces revision');
function named(parent, branches) {
  const edges=[]; for(let i=1;i<parent;i++) edges.push([i,i+1]); let count=parent;
  for(const [position,length] of branches) { let from=position; for(let j=0;j<length;j++) {edges.push([from,++count]);from=count;} }
  return fromEdges(count,edges);
}
function fromEdges(count,edges) {
  const degree=Array(count+1).fill(0); edges.forEach(([a,b])=>{degree[a]++;degree[b]++;});
  return {nodes:Array.from({length:count},(_,i)=>({id:String(i+1),hydrogens:4-degree[i+1]})),
    bonds:edges.map(([a,b])=>({a:String(a),b:String(b),order:1}))};
}
const expected=[named(1,[]),named(2,[]),named(3,[]),named(4,[]),named(5,[]),named(5,[[2,1]]),
  named(4,[[2,1],[3,1]]),named(6,[[3,2],[2,1],[5,1]]),
  ...plan.proposedBatch.map(record=>fromEdges(Number(record.formula.match(/^C(\d+)/)[1]),record.preflightCarbonEdges))];
const targets=catalog.molecules.map(m=>E.parseMol(m.mol));
for(let i=0;i<catalog.molecules.length;i++) {
  const molecule=catalog.molecules[i], target=targets[i];
  check(hash(Buffer.from(molecule.mol))===molecule.sourceSHA256,'source SHA ' + molecule.id);
  check(E.grade(target,expected[i]).correct,'MOL agrees with separately named/preflight graph ' + molecule.id);
  const ids=new Map(target.nodes.map((n,j)=>[n.id,'permuted-' + (99-j)]));
  const permuted={nodes:[...target.nodes].reverse().map(n=>({id:ids.get(n.id),hydrogens:n.hydrogens,x:-10,y:999})),
    bonds:[...target.bonds].reverse().map(b=>({a:ids.get(b.b),b:ids.get(b.a),order:1}))};
  check(E.grade(permuted,target).correct,'node/bond order and labels invariant ' + molecule.id);
  for(let j=0;j<targets.length;j++) check(E.grade(target,targets[j]).correct===(i===j),'constitutional identity ' + i + '/' + j);
}
for(const record of pack.molecules) {
  const analysis=analyses.get(record.id);
  check(analysis.name===record.nameGR,'actual pinned name ' + record.id);
  const round={roundId:'memory-' + record.id,moleculeId:record.id,correctName:analysis.name,series:analysis.classification.seriesKey,
    parentLength:analysis.chain.length,pieces:analysis.parts.filter(Boolean).map(text=>({text,separatorBefore:''})),
    representations:['condensed','expanded','skeletal','3d'],vocabulary:{roots:analysis.rootVocabulary}};
  const valid=Builder.validateRound(round), bank=Builder.createBank(valid,{seed:'same-receipt'});
  const available=bank.slice(), answer=valid.pieces.map(piece=>available.splice(available.findIndex(t=>t.text===piece.text),1)[0]);
  check(Builder.evaluate(valid,answer).correct,'Builder real native pieces solve ' + record.id);
  check(!Builder.evaluate(valid,answer.slice(1)).correct,'Builder partial native answer rejected ' + record.id);
}
for(const id of ['dimethyl_2_2_propane','dimethyl_2_2_butane']) check(targets[catalog.molecules.findIndex(m=>m.id===id)].nodes.some(n=>n.hydrogens===0),'quaternary C supported ' + id);
const bad=structuredClone(targets[1]);bad.nodes[0].hydrogens=4;
check(!E.grade(bad,targets[1]).correct,'wrong fixed hydrogen count rejected');
check(!E.grade({nodes:[],bonds:[]},targets[0]).correct,'empty construction rejected');

class FakeNode {
  constructor(tag='div') { this.tagName=tag.toUpperCase();this.children=[];this.handlers={};this.dataset={};this.attributes={};this.style={setProperty(){}};this.hidden=false;this.disabled=false;this.value='';this._text='';this.isConnected=true;
    const names=new Set();this.classList={add:(...v)=>v.forEach(x=>names.add(x)),remove:(...v)=>v.forEach(x=>names.delete(x)),contains:x=>names.has(x),toggle:(x,on)=>{if(on===undefined)on=!names.has(x);on?names.add(x):names.delete(x);return on;}}; }
  set textContent(value){this._text=String(value);this.children=[];} get textContent(){return this._text+this.children.map(n=>n.textContent).join('');}
  append(...nodes){nodes.forEach(n=>{n.parentNode=this;this.children.push(n);});} replaceChildren(...nodes){this.children=[];this._text='';this.append(...nodes);}
  setAttribute(k,v){this.attributes[k]=String(v);} removeAttribute(k){delete this.attributes[k];}
  addEventListener(type,handler){(this.handlers[type] ||= []).push(handler);} fire(type,extra={}){for(const handler of this.handlers[type]||[])handler({target:this,preventDefault(){},...extra});}
  getBoundingClientRect(){return {left:0,top:0,right:720,bottom:360,width:720,height:360};}
  closest(selector){if(selector==='[data-hydrogens]' && this.dataset.hydrogens!==undefined)return this;if(selector==='[data-node-id]' && this.dataset.nodeId)return this;return null;}
  focus(){} scrollIntoView(){} cloneNode(){const node=new FakeNode(this.tagName);node.dataset={...this.dataset};node.attributes={...this.attributes};return node;}
  querySelectorAll(){return [];} querySelector(){return null;} contains(n){return this===n || this.children.some(child=>child.contains(n));}
}
async function runtime(controlled=false, corrupt=false) {
  const nodes=new Map(), messages=[], listeners={}, fetched=[], used=[];
  const node=id=>{if(!nodes.has(id)) {const n=new FakeNode();n.id=id;nodes.set(id,n);} return nodes.get(id);};
  const pieces=Array.from({length:5},(_,hydrogens)=>{const n=new FakeNode('button');n.dataset.hydrogens=String(hydrogens);return n;});
  const url='http://memory.test/games/molecular-puzzle.html'+(controlled?'?embedded=1&lessonSession=memory_legacy_12345':'');
  const ctx=vm.createContext({console,URL,TextEncoder,TextDecoder,AbortController,crypto:webcrypto,performance,innerWidth:1280,innerHeight:900,scrollY:0,
    location:{href:url,origin:'http://memory.test'},NameleculeMolecularPuzzleEngine:E,
    document:{body:new FakeNode('body'),documentElement:{scrollHeight:360},activeElement:null,getElementById:node,
      querySelectorAll:selector=>selector==='[data-hydrogens]'?pieces:[],createElement:tag=>new FakeNode(tag),createElementNS:(_ns,tag)=>new FakeNode(tag),addEventListener(){},elementFromPoint:()=>node('assembly-board')},
    addEventListener:(type,handler)=>(listeners[type] ||= []).push(handler),requestAnimationFrame:()=>1,cancelAnimationFrame(){},
    matchMedia:()=>({matches:false,addEventListener(){}}),ResizeObserver:class{observe(){}},
    setTimeout:(fn,ms)=>{const timer=setTimeout(fn,ms);timer.unref();return timer;},clearTimeout,
    fetch:async requested=>{const file=new URL(requested).pathname.slice(1);fetched.push(file);let bytes=read(file);if(corrupt)bytes=Buffer.concat([bytes,Buffer.from(' ')]);return {ok:true,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)};},
    NameleculeChemistryClient:{analyze:async(molecule,options)=>{used.push(options.engineSHA256);return analyses.get(molecule.id);}}});
  ctx.window=ctx;ctx.parent=controlled?{innerWidth:1280,postMessage:message=>messages.push(message)}:ctx;
  vm.runInContext(read('js/namelecule-molecular-puzzle.js').toString(),ctx);
  for(let i=0;i<100;i++){await new Promise(resolve=>setImmediate(resolve));if(node('round-select').children.length || node('game-status').classList.contains('error'))break;}
  return {ctx,nodes,node,pieces,messages,fetched,used,send:data=>{for(const handler of listeners.message||[])handler({origin:'http://memory.test',source:ctx.parent,data});},
    stop:()=>{for(const handler of listeners.pagehide||[])handler({});}};
}
(async()=>{
 const standalone=await runtime();
 check(standalone.fetched[0]==='games/data/alkane-structures-v2.json' && standalone.node('round-select').children.length===14,'fresh standalone loads verified version2 with 14 choices');
 check(standalone.used.length===14 && standalone.used.every(sha=>sha===catalog.engineSHA256),'standalone analyses all 14 with immutable engine');
 for(let index=0;index<catalog.molecules.length;index++) {
   const target=targets[index];standalone.node('round-select').value=String(index);standalone.node('round-select').fire('change');
   check(standalone.node('target-name').textContent===analyses.get(catalog.molecules[index].id).name,'controller selects ' + catalog.molecules[index].id);
   for(const n of target.nodes)standalone.node('piece-bank').fire('click',{target:standalone.pieces[n.hydrogens]});
   const created=standalone.node('board-nodes').children.map(n=>n.dataset.nodeId), mapping=new Map(target.nodes.map((n,i)=>[n.id,created[i]]));
   standalone.node('bond-tool').fire('click');
   for(const bond of target.bonds)for(const id of [bond.a,bond.b]) {
     const button=standalone.node('board-nodes').children.find(n=>n.dataset.nodeId===mapping.get(id));
     standalone.node('board-nodes').fire('click',{target:button});
   }
   standalone.node('check-answer').fire('click');
   check(standalone.node('feedback').classList.contains('success') && standalone.node('check-answer').disabled,'controller genuine group/bond submission solves ' + catalog.molecules[index].id);
 }
 standalone.node('next-molecule').fire('click');
 check(standalone.node('target-name').textContent===analyses.get('methane').name && standalone.node('board-nodes').children.length===0,'last-to-first switch resets fresh standalone graph');
 standalone.stop();
 const corrupted=await runtime(false,true);
 check(corrupted.used.length===0 && corrupted.node('game-status').classList.contains('error') && !corrupted.node('retry-load').hidden,'changed catalog bytes fail closed before analysis with retry');corrupted.stop();
 const controlled=await runtime(true);
 check(controlled.fetched[0]==='games/data/alkane-structures.json' && controlled.node('round-select').children.length===8 && controlled.messages.some(m=>m.type==='ready'),'existing lesson still loads legacy8 and announces ready');
 const partial={graph:{nodes:[{id:'piece-7',hydrogens:3,x:100,y:100}],bonds:[]},attempts:0,submitted:false};
 const base={channel:'namelecule-puzzle-lesson-v1',session:'memory_legacy_12345',command:'load',requestId:1,attemptId:'legacy-partial',moleculeId:'ethane',correctName:analyses.get('ethane').name,initialState:partial};
 controlled.send(base);
 const restored=controlled.messages.filter(m=>m.type==='loaded').at(-1);
 check(restored?.state.graph.nodes.length===1 && restored.state.graph.nodes[0].id==='piece-7' && restored.state.attempts===0 && !restored.state.submitted,'legacy partial receipt graph/attempts restore without new-pool normalization');
 const earnedGraph=structuredClone(targets[1]);earnedGraph.nodes.forEach((n,i)=>Object.assign(n,{x:100+i*100,y:100}));
 controlled.send({...base,requestId:2,attemptId:'legacy-earned',initialState:{graph:earnedGraph,attempts:1,submitted:true}});
 const earned=controlled.messages.filter(m=>m.type==='loaded').at(-1);
 check(earned?.state.submitted && earned.state.attempts===1 && controlled.node('feedback').classList.contains('success') && controlled.node('check-answer').disabled,'legacy earned evidence independently regraded and remains solved');
 const loaded=controlled.messages.filter(m=>m.type==='loaded').length;
 controlled.send({...base,requestId:3,moleculeId:'dimethyl_2_2_propane',correctName:analyses.get('dimethyl_2_2_propane').name});
 check(controlled.messages.filter(m=>m.type==='loaded').length===loaded && controlled.node('feedback').classList.contains('success'),'legacy lesson rejects molecule outside its version without losing earned board');
 controlled.stop();
 const result={kind:'Developer memory verification',checks:report.length,passed:report.every(x=>x.passed),catalogSHA256:hash(read('games/data/alkane-structures-v2.json')),catalogRevision:catalog.revision,results:report,
   untested:['Real browser rendering, drag, keyboard, zoom, resize and actual native viewer representations/3D are assigned to the root/data browser pass.','No independent-review execution is claimed by this harness.']};
 fs.writeFileSync(path.join(__dirname,'memory-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({checks:result.checks,passed:result.passed,catalogSHA256:result.catalogSHA256}));
})().catch(error=>{console.error(error);process.exitCode=1;});
