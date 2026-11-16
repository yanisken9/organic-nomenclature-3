"use strict";
// Developer evidence: pure policy/generator and small DOM contract checks only.
// This is not a browser, rendering, keyboard, chemistry-validator or gate test.
const fs = require("fs"), path = require("path"), vm = require("vm"), crypto = require("crypto");
const assert = require("assert/strict");
const root = path.resolve(__dirname, "../../../..");
const levels = require(path.join(root, "js/namelecule-game-levels.js"));
const generator = require(path.join(root, "js/namelecule-repair-generator.js"));
const bands = {
  1: ["methane", "ethane", "propane", "butane", "pentane"],
  2: ["methyl_2_butane", "methyl_2_pentane", "methyl_3_pentane", "ethyl_3_pentane"],
  3: ["dimethyl_2_2_propane", "dimethyl_2_2_butane", "dimethyl_2_3_butane", "ethyl_3_methyl_2_pentane", "ethyl_3_dimethyl_2_5_hexane"]
};
const all = Object.values(bands).flat(), completed = [];
function test(name, check) { check(); completed.push(name); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function copy(value) { return JSON.parse(JSON.stringify(value)); }
function freeze(value) { if (value && typeof value === "object") { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }

test("audited 5/4/5 mapping, unsupported IDs and immutable API", () => {
  assert.equal(levels.policyVersion, "alkanes-levels-v1"); assert.ok(Object.isFrozen(levels));
  for (const level of [1,2,3]) {
    assert.deepEqual(levels.poolFor(level), bands[level]);
    bands[level].forEach(id => assert.equal(levels.levelFor(id), level));
    assert.match(levels.label(level), new RegExp("^Επίπεδο " + level + " — "));
    const returned = levels.poolFor(level); returned.pop(); assert.deepEqual(levels.poolFor(level), bands[level]);
  }
  for (const id of ["ethene", "constructor", "__proto__", undefined, null]) assert.equal(levels.levelFor(id), null);
  assert.deepEqual(levels.poolFor(2, ["ethene", "ethyl_3_pentane", "methyl_2_butane"]), ["methyl_2_butane", "ethyl_3_pentane"]);
  assert.deepEqual(levels.poolFor(1, []), []);
});
test("invalid pools, duplicate IDs and levels fail explicitly", () => {
  for (const bad of [0,4,"1",null,NaN]) assert.throws(() => levels.poolFor(bad));
  for (const ids of [null,{},["methane", "methane"],[""],[null],["<script>"]]) assert.throws(() => levels.poolFor(1,ids));
});
test("exact context identities normalize deterministically and reject unknown or mixed metadata", () => {
  const cases = [{source:"legacy",level:null,seed:null},...[1,2,3].map(level=>({source:"enriched",level,seed:"01234567890123456789"}))];
  const keys = ["version","source","catalogRevision","catalogSHA256","engineSHA256","generatorVersion","policyVersion","level","seed"];
  for (const options of cases) {
    const context=levels.makeContext(options);
    assert.deepEqual(Object.keys(context),keys);assert.deepEqual(levels.validateContext(context),context);
    assert.deepEqual(levels.validateContext(Object.fromEntries(Object.entries(context).reverse())),context);
    assert.equal(levels.contextKey(Object.fromEntries(Object.entries(context).reverse())),JSON.stringify(context));
    const ids=levels.contextIds(context);assert.equal(ids.length,options.source==="legacy"?8:bands[options.level].length);
    if(options.source==="enriched")assert.deepEqual(ids,bands[options.level]);
    ids.pop();assert.equal(levels.contextIds(context).length,options.source==="legacy"?8:bands[options.level].length);
    for(const field of keys){const bad=copy(context);delete bad[field];assert.throws(()=>levels.validateContext(bad));}
    for(const field of ["version","source","catalogRevision","catalogSHA256","engineSHA256","generatorVersion","policyVersion","level","seed"]){
      const bad=copy(context);bad[field]="unknown";assert.throws(()=>levels.validateContext(bad));
    }
    assert.throws(()=>levels.validateContext({...context,extra:true}));
  }
  assert.equal(levels.makeContext({source:"legacy"}).seed,null);
  for(const options of [{source:"unknown"},{source:"legacy",level:1},{source:"enriched",level:null},{source:"enriched",level:"1"},
    {source:"enriched",level:1,seed:0},{source:"enriched",level:1,seed:"1".repeat(21)},
    {source:"enriched",level:1,seed:""},{source:"enriched",level:1,seed:"1x"},{source:"legacy",extra:true}]) assert.throws(()=>levels.makeContext(options));
});
test("seeded single-round bags exhaust then refill without immediate repeats", () => {
  for (const ids of [["a","b"],bands[2],bands[1]]) {
    const a = levels.createDeck(ids,{seed:"replay",avoid:ids[0]});
    const b = levels.createDeck(ids,{seed:"replay",avoid:ids[0]});
    const sequence = Array.from({length:ids.length * 8}, () => a.next());
    assert.deepEqual(sequence, Array.from({length:sequence.length}, () => b.next()));
    assert.notEqual(sequence[0],ids[0]);
    for (let index=1;index<sequence.length;index++) assert.notEqual(sequence[index],sequence[index-1]);
    for (let index=0;index<sequence.length;index+=ids.length) assert.deepEqual(sequence.slice(index,index+ids.length).sort(),ids.slice().sort());
  }
  const singleton = levels.createDeck(["one"], {seed:7,avoid:"one"});
  assert.deepEqual([singleton.next(),singleton.next(),singleton.next()],["one","one","one"]);
  const ids = ["a","b"]; const deck = levels.createDeck(ids); ids.splice(0,2,"changed");
  assert.deepEqual([deck.next(),deck.next()].sort(),["a","b"]);
});
test("invalid deck inputs, seeds and avoided IDs fail explicitly", () => {
  for (const bad of [[],null,["a","a"],[1],[""]]) assert.throws(() => levels.createDeck(bad));
  for (const seed of ["",-1,NaN,{},null]) assert.throws(() => levels.createDeck(["a"],{seed}));
  for (const options of [null,[],{avoid:[]},{avoid:""}]) assert.throws(() => levels.createDeck(["a"],options));
  assert.equal(levels.createDeck(["a"],{avoid:"absent"}).next(),"a");
});

const catalogBytes = fs.readFileSync(path.join(root,"games/data/alkane-structures-v2.json"));
const catalog = JSON.parse(catalogBytes);
const engineBytes = fs.readFileSync(path.join(root,"js/chemistry-engines",catalog.engineSHA256 + ".js"));
assert.equal(sha(engineBytes),catalog.engineSHA256);
assert.equal(sha(catalogBytes),"2c4d9a95a77291f13c4a422644aefdae7f23448c2eed7b9d2ef4913da6de92b2");
const workerCode = fs.readFileSync(path.join(root,"js/namelecule-chemistry-worker.js"),"utf8");
function analyze(molecule) {
  let response;
  const context = vm.createContext({URL,console,self:{location:{origin:"https://namelecule.invalid"},postMessage:value=>{response=value;},close:()=>{}}});
  context.importScripts = () => vm.runInContext(engineBytes.toString("utf8"),context);
  vm.runInContext(workerCode,context);
  context.self.onmessage({data:{type:"analyze",requestId:molecule.id,molecule,engineSHA256:catalog.engineSHA256,engineURL:"blob:https://namelecule.invalid/pinned"}});
  assert.equal(response.type,"result",JSON.stringify(response)); return copy(response.result);
}
const input = freeze({catalog, analyses:catalog.molecules.map(analyze)}), before=JSON.stringify(input);
const originalGame = JSON.stringify(generator.createGame(input.catalog,input.analyses,{seed:"unchanged",difficulty:"basic"}));
const viewSummaries = [];
test("full14 views preserve canonical bytes, per-record values and independent identities", () => {
  for (const level of [1,2,3]) {
    const view = levels.createGenerationInput(input,level);
    const expected = level===1 ? all : bands[1].concat(bands[level]);
    assert.deepEqual(view.catalog.molecules.map(row=>row.id).sort(),expected.slice().sort());
    assert.deepEqual(view.analyses.map(row=>row.moleculeId).sort(),expected.slice().sort());
    for (const row of view.catalog.molecules) assert.deepEqual(row,input.catalog.molecules.find(original=>original.id===row.id));
    for (const row of view.analyses) assert.deepEqual(row,input.analyses.find(original=>original.moleculeId===row.moleculeId));
    assert.equal(view.policyVersion,levels.policyVersion); assert.equal(view.level,level);
    assert.equal(view.sourceRevision,input.catalog.revision); assert.equal(view.sourceSHA256,sha(catalogBytes));
    assert.notEqual(view.viewRevision,view.sourceRevision); assert.equal(view.catalog.revision,view.viewRevision);
    assert.deepEqual(view.catalog.gameLevels,{policyVersion:view.policyVersion,level,sourceRevision:view.sourceRevision,sourceSHA256:view.sourceSHA256,viewRevision:view.viewRevision});
    assert.deepEqual(view,levels.createGenerationInput(input,level));
    view.catalog.molecules[0].mol="changed in clone"; view.analyses[0].chain[0]=-1;
    assert.equal(JSON.stringify(input),before);
    viewSummaries.push({level,molecules:expected.length,viewRevision:view.viewRevision,sourceSHA256:view.sourceSHA256});
  }
  assert.equal(new Set(viewSummaries.map(row=>row.viewRevision)).size,3);
});
test("object-form full analyses project without mutating or dropping the retained group", () => {
  const keyed = {catalog:input.catalog,analyses:Object.fromEntries(input.analyses.map(row=>[row.moleculeId,row]))};
  const snapshot=JSON.stringify(keyed), view=levels.createGenerationInput(keyed,2);
  assert.equal(Object.keys(view.analyses).length,9); assert.equal(JSON.stringify(keyed),snapshot);
  view.analyses.methane.parts[5]="changed"; assert.equal(JSON.stringify(keyed),snapshot);
});
test("missing, mixed, duplicate or forged source inputs reject before projection", () => {
  const mutations = [
    value=>{value.catalog.molecules.pop();}, value=>{value.analyses.pop();},
    value=>{value.catalog.molecules[1].id=value.catalog.molecules[0].id;},
    value=>{value.analyses[1].moleculeId=value.analyses[0].moleculeId;},
    value=>{value.catalog.molecules[0].id="unknown";}, value=>{value.analyses[0].moleculeId="unknown";},
    value=>{value.catalog.revision="changed";},value=>{value.catalog.engineSHA256="0".repeat(64);},
    value=>{value.analyses[0].engineSHA256="0".repeat(64);},value=>{value.sourceSHA256="0".repeat(64);},
    value=>{value.sourceRevision="changed";},value=>{value.catalog.catalogVersion=1;}
  ];
  mutations.forEach(change=>{const value=copy(input);change(value);assert.throws(()=>levels.createGenerationInput(value,2));});
  assert.throws(()=>levels.createGenerationInput(input,4));
  assert.throws(()=>levels.createGenerationInput(levels.createGenerationInput(input,2),2));
});
test("unchanged generator accepts all three views with distinct band-correct triples", () => {
  for (const level of [1,2,3]) {
    const view=levels.createGenerationInput(input,level), setId=level===1?"alkanes-unbranched":"alkanes-branched";
    for (const seed of ["0","repeatable","447"]) {
      const game=generator.createGame(view.catalog,view.analyses,{seed,difficulty:"basic"});
      const replay=generator.createGame(view.catalog,view.analyses,{seed,difficulty:"basic"});
      assert.deepEqual(game,replay); assert.equal(game.sets.length,2);
      const set=game.sets.find(row=>row.id===setId), ids=set.rounds.map(row=>row.moleculeId);
      assert.equal(new Set(ids).size,3); ids.forEach(id=>assert.equal(levels.levelFor(id),level));
    }
  }
  assert.equal(JSON.stringify(input),before);
  assert.equal(JSON.stringify(generator.createGame(input.catalog,input.analyses,{seed:"unchanged",difficulty:"basic"})),originalGame);
});

// A deliberately small DOM double checks the component contract, not layout or
// browser event semantics. Actual responsive/focus interaction belongs to host QA.
class Element {
  constructor(tag,doc){this.tagName=tag;this.ownerDocument=doc;this.childNodes=[];this.attributes={};this.handlers={};this.parentNode=null;this.hidden=false;this.disabled=false;this._text="";}
  appendChild(child){child.parentNode=this;this.childNodes.push(child);return child;}
  append(...children){children.forEach(child=>this.appendChild(child));}
  get classList(){return {toggle:()=>{},remove:()=>{},add:()=>{}};}
  closest(){return null;}
  removeChild(child){this.childNodes.splice(this.childNodes.indexOf(child),1);child.parentNode=null;return child;}
  setAttribute(key,value){this.attributes[key]=value;}
  addEventListener(key,handler){this.handlers[key]=handler;}
  set textContent(text){this._text=String(text);this.childNodes=[];}
  get textContent(){return this._text+this.childNodes.map(child=>child.textContent).join("");}
  click(){if(!this.disabled&&!this.hidden&&this.handlers.click)this.handlers.click();}
}
const doc={createElement:tag=>new Element(tag,doc)}, host=new Element("div",doc);
function find(node,predicate){if(predicate(node))return node;for(const child of node.childNodes){const found=find(child,predicate);if(found)return found;}return null;}
test("controls are unselected initially, expose counts and remain caller-driven", () => {
  const events=[], controls=levels.mount(host,{availableIds:all,allowedLevels:[1,2,3],selectedLevel:null,onSelect:event=>events.push(event)});
  const group=host.childNodes[0], button=level=>find(group,node=>node.attributes["data-level"]===String(level));
  for(const level of [1,2,3]) {assert.equal(button(level).attributes["aria-pressed"],"false");assert.match(button(level).textContent,new RegExp(bands[level].length+" διαθέσιμα μόρια"));}
  assert.doesNotMatch(group.textContent,/Υποχρεωτικό|Προαιρετικό/);assert.equal(events.length,0);
  button(2).click();assert.deepEqual(events,[{category:"alkanes",level:2}]);
  controls.set({allowedLevels:[1],requirements:{1:"required",2:"required",3:"optional"},completedLevels:[1]});
  assert.ok(button(2).hidden);assert.equal(button(1).attributes["aria-pressed"],"false");assert.match(button(1).textContent,/Υποχρεωτικό · Ολοκληρώθηκε/);
  assert.equal(events.length,1);button(2).click();assert.equal(events.length,1);
  controls.set({allowedLevels:[1,2,3],otherCount:133});
  const other=find(group,node=>node.tagName==="button"&&node.textContent.startsWith("Άλλες διαθέσιμες"));other.click();
  assert.deepEqual(events.at(-1),{category:"other",level:null});
  assert.ok(find(group,node=>node.className==="nl-game-levels__buttons").hidden);
  const alkane=find(group,node=>node.tagName==="button"&&node.textContent==="Αλκάνια");alkane.click();assert.deepEqual(events.at(-1),{category:"alkanes",level:null});
  controls.set({availableIds:["methane"]});assert.equal(button(2).disabled,true);assert.match(button(1).textContent,/1 διαθέσιμο μόριο/);
  assert.throws(()=>controls.set({requirements:{3:"unrecognized"}}));
  controls.destroy();controls.destroy();assert.equal(host.childNodes.length,0);assert.throws(()=>controls.set({}));
});
test("new JavaScript has no HTML interpolation and CSS stays within the component",()=>{
  const source=fs.readFileSync(path.join(root,"js/namelecule-game-levels.js"),"utf8");
  assert.doesNotMatch(source,/innerHTML|outerHTML|insertAdjacentHTML/);
  const css=fs.readFileSync(path.join(root,"css/namelecule-game-levels.css"),"utf8");
  assert.match(css,/@media\(max-width:600px\)/);assert.match(css,/grid-template-columns:1fr/);
  assert.doesNotMatch(css,/(?:^|\n)(?:body|button|:root|\*)[\s{]/);
});

const files=["js/namelecule-game-levels.js","css/namelecule-game-levels.css","js/namelecule-generated-repair-checkpoint.js"];
const report={recordedUTC:new Date().toISOString(),role:"Developer supplied evidence",passed:true,groups:completed,
  pinnedSourceSHA256:sha(catalogBytes),pinnedEngineSHA256:sha(engineBytes),analyses:input.analyses.length,views:viewSummaries,
  generator:{unchangedSHA256:sha(fs.readFileSync(path.join(root,"js/namelecule-repair-generator.js"))),seedsPerLevel:3,setsGenerated:18,compatibleTriplesChecked:9},
  files:Object.fromEntries(files.map(file=>[file,sha(fs.readFileSync(path.join(root,file)))])),
  scope:"Only common policy/UI module; no unlock rules or cross-triple Workshop history",
  seedContract:"createDeck fallback seed 0 is deterministic for helpers/tests; standalone hosts must supply fresh crypto seeds for fresh normal assignments.",
  sourceContract:"sourceSHA256 in the projection is descriptor metadata. Caller must verify full source bytes and chemistry first; this module does not hash or chemically validate them.",
  limits:["No browser/layout/focus/keyboard checks; DOM double checks component contracts only","No independent review executed by this worker","No host integration, lesson replay, migration, gate aggregation or scenario export checks"],coreChanged:false,commit:false,publication:false};
fs.writeFileSync(path.join(__dirname,"results.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report,null,2));
