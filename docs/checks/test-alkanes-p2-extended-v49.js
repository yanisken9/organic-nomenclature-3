// Run from repository root with macOS JavaScriptCore jsc. No files are written.
// Production core/viewer/data are executed; only DOM, JSME input and repaint
// APIs are stubbed here. Actual DOM/JSmol behavior requires the browser test.
const sources = ['js/jsme-nick-nomeclature-moc2-data_49.js',
 'js/mulermoc-nom-core-49.js','js/mulermoc-nom-molview-49.js'].map(p=>readFile(p)).join('\n');
const run = new Function('fixture','sdf','options', `
 var window={}, console={warn:function(){},log:function(){},error:function(){}},
 document={getElementById:function(){return null;},addEventListener:function(){}};
 ${sources}
 var MOL2D=window.MOL2D;
 selectedMol=options.key || '__p2_fixture'; mode2D=options.mode || 'condensed';
 mainChainMode=options.chainMode || 'algorithmic';
 if(options.stored) nameExamples[selectedMol]={mainChain_Condensed:options.stored.slice(),
  mainChain_Expanded:options.stored.slice(),mainChain_Skeletal:options.stored.slice()};
 var text=fixture || MOL2D[selectedMol][mode2D], lines=text.split('\\n');
 var na=Number(lines[3].slice(0,3)),nb=Number(lines[3].slice(3,6));
 var aa=lines.slice(4,4+na).map(x=>({label:x.slice(31,34).trim()}));
 var bb=lines.slice(4+na,4+na+nb).map(x=>({atoms:[Number(x.slice(0,3)),Number(x.slice(3,6))],order:Number(x.slice(6,9))}));
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1]};
 fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
 var initial={name:currentMolName,parts:nameComponentsList.slice(),chain:mainChainAtomsList.slice(),common:currentMolCommonName};
 if(options.key && functionalGroupObj.ether){nameExamples[selectedMol].classification=fGetMoleculeClassification();initial.etherParts=fGetEtherCommonParts();}
 fParseSDF3D(sdf || text);fDetectMolType3D();fCalcMainChain3D();
 if(options.parent){mainChainAtomsList=options.parent.slice();mainChainAtoms3D=options.parent3D.slice();fGuessName(true);}
 var group2=fGetHydrocarbonBranchGroup(2);
 var highlights=[1,2].map(slot=>({two:fGetHydrocarbonBranchHighlight(slot),three:fGetHydrocarbonBranchHighlight3D(slot)}));
 var branchInfo=fGetHydrocarbonSubstituentInfo();
 var explanation=group2 ? [fHydrocarbonBranchExplanation(group2,true),fHydrocarbonBranchExplanation(group2,false)] : [];
 var poolSize=mainChainPool.length, pool3Size=mainChainPool3D.length;
 var variants=mainChainPool.map(p=>{mainChainAtomsList=p.chain.slice();fGuessName(true);return {name:currentMolName,signature:fCarbonChainSignature(p.chain,atomConnectivityList,allAtomsTypeList)};});
 var signatures3=mainChainPool3D.map(p=>fCarbonChainSignature(p.chain,atomConnectivityList3D,allAtomsTypeList3D));
 // Exercise actual stepper selection with a deliberately misordered 3D pool:
 // insert a wrong numbering direction at index zero, before the good matches.
 // Merely choosing the same ordinal would fail this test.
 var stepResults=[];
 if(options.stepper){
  mainChainPool3D.unshift({chain:mainChainPool3D[0].chain.slice().reverse()});
  mainChainPool3DKey=selectedMol;
  fClearHighlights=function(){};fUpdateSVG=function(){};fExplainNameComp=function(){};
  for(var i=0;i<mainChainPool.length;i++){
   mainChainPoolIdx=i;fApplyChainStep();
   stepResults.push({name:currentMolName,two:fCarbonChainSignature(mainChainAtomsList,atomConnectivityList,allAtomsTypeList),three:fCarbonChainSignature(mainChainAtoms3D,atomConnectivityList3D,allAtomsTypeList3D)});
  }
 }
 return {initial,variants,signatures3,poolSize,pool3Size,branchInfo,highlights,explanation,stepResults};
`);
let checks=0;
function assert(value,label){checks++;if(!value)throw Error(label);}
function same(a,b,label){assert(JSON.stringify(a)===JSON.stringify(b),label+' expected '+JSON.stringify(b)+' got '+JSON.stringify(a));}
function chain(n){return Array.from({length:n-1},(_,i)=>[i+1,i+2,1]);}
function graph(n,edges){return {types:Array(n).fill('C'),edges};}
function mol(g){
 return 'P2 regression fixture\n  Test 3D\n\n'+String(g.types.length).padStart(3)+String(g.edges.length).padStart(3)+'  0  0  0  0  0  0  0999 V2000\n'+
 g.types.map((t,i)=>(i*1.5).toFixed(4).padStart(10)+'    0.0000    0.0000 '+t.padEnd(3)+' 0  0  0  0  0  0  0  0  0  0  0  0').join('\n')+'\n'+
 g.edges.map(e=>e.map(n=>String(n).padStart(3)).join('')+'  0  0  0  0').join('\n')+'\nM  END\n$$$$\n';
}
function hydrogens(g){
 const h={types:g.types.slice(),edges:g.edges.map(e=>e.slice())};
 g.types.forEach((t,i)=>{if(t!=='C')return;const val=g.edges.reduce((a,e)=>a+(e[0]===i+1||e[1]===i+1?e[2]:0),0);
  for(let j=val;j<4;j++){h.types.push('H');h.edges.push([i+1,h.types.length,1]);}});return h;
}
let seed=23049;
function permute(g){
 const order=g.types.map((_,i)=>i+1);
 for(let j=order.length-1;j>0;j--){seed=(seed*1664525+1013904223)>>>0;const k=seed%(j+1);[order[j],order[k]]=[order[k],order[j]];}
 const map={};order.forEach((old,i)=>map[old]=i+1);
 return {graph:{types:order.map(n=>g.types[n-1]),edges:g.edges.map(e=>[map[e[1]],map[e[0]],e[2]]).reverse()},map};
}
const fixtures=[
 {id:'straight propyl',g:graph(13,chain(10).concat([[5,11,1],[11,12,1],[12,13,1]])),name:'5-προπυλοδεκάνιο'},
 {id:'isopropyl',g:graph(13,chain(10).concat([[5,11,1],[11,12,1],[11,13,1]])),name:'5-ισοπροπυλοδεκάνιο'},
 {id:'alphabetical tie',g:graph(10,chain(7).concat([[5,8,1],[8,9,1],[3,10,1]])),name:'3-αιθυλο-5-μεθυλοεπτάνιο',pool:2},
 {id:'three groups',g:graph(16,chain(10).concat([[2,11,1],[4,12,1],[12,13,1],[5,14,1],[14,15,1],[14,16,1]])),name:'4-αιθυλο-5-ισοπροπυλο-2-μεθυλοδεκάνιο'},
 {id:'four groups',g:graph(19,chain(10).concat([[2,11,1],[4,12,1],[12,13,1],[5,14,1],[14,15,1],[14,16,1],[6,17,1],[17,18,1],[18,19,1]])),name:'4-αιθυλο-5-ισοπροπυλο-2-μεθυλο-6-προπυλοδεκάνιο'},
 {id:'neopentane',g:graph(5,[[1,2,1],[2,3,1],[2,4,1],[2,5,1]]),name:'2,2-διμεθυλοπροπάνιο',pool:6},
 {id:'trimethyloctane',g:graph(11,chain(8).concat([[2,9,1],[3,10,1],[6,11,1]])),name:'2,3,6-τριμεθυλοοκτάνιο'},
];
for(const f of fixtures){
 for(const expanded of [false,true]){
  const g=expanded?hydrogens(f.g):f.g;
  for(let i=0;i<8;i++){
   const two=permute(g),three=permute(g);
   const r=run(mol(two.graph),mol(three.graph),{mode:expanded?'expanded':'condensed',stepper:true});
   same(r.initial.name,f.name,f.id+' name');same(r.initial.parts.length,12,'fixed slots');
   if(f.pool){same(r.poolSize,f.pool,f.id+' all winning2D');same(r.pool3Size,f.pool,f.id+' all winning3D');}
   assert(r.variants.every(v=>v.name===f.name),f.id+' all paths name');
   assert(r.variants.every(v=>r.signatures3.includes(v.signature)),f.id+' independently permuted SDF signatures');
   assert(r.stepResults.every(v=>v.two===v.three&&v.name===f.name),f.id+' stepper graph matching');
   const d=run(mol(two.graph),mol(three.graph),{mode:expanded?'expanded':'condensed',chainMode:'data',stored:r.initial.chain});
   same(d.initial.chain,r.initial.chain,f.id+' authored chain preserved');same(d.initial.name,f.name,f.id+' algorithm/data');
  }
 }
 print('PASS '+f.id+': 16 independent2D/3D permutations, explicitH, allwinningpaths, stepper, algorithm/data');
}
// Same-parent equal-sized branches: only their rooted shape distinguishes them.
const identity=graph(16,chain(10).concat([[5,11,1],[11,12,1],[12,13,1],[5,14,1],[14,15,1],[14,16,1]]));
for(const expanded of [false,true]){
 const g=expanded?hydrogens(identity):identity,three=permute(g),parent=Array.from({length:10},(_,i)=>i+1);
 const r=run(mol(g),mol(three.graph),{parent,parent3D:parent.map(n=>three.map[n])});
 for(let slot=0;slot<2;slot++){
  const carbon=slot===0?[14,15,16]:[11,12,13],atoms=carbon.slice();
  if(expanded)g.edges.forEach(e=>{if(carbon.includes(e[0])&&g.types[e[1]-1]==='H')atoms.push(e[1]);});
  same(r.highlights[slot].two.atoms.slice().sort((a,b)=>a-b),atoms.sort((a,b)=>a-b),'equal-size2D identity+H');
  same(r.highlights[slot].three.atoms.slice().sort((a,b)=>a-b),carbon.map(n=>three.map[n]).sort((a,b)=>a-b),'equal-size3D identity');
 }
}
const grouped=run(mol(fixtures[3].g),null,{});
same(grouped.initial.parts.slice(0,4),['4-','αιθυλο','-5-','ισοπροπυλο-2-μεθυλο'],'interleaved fixed slots');
assert(grouped.explanation[0].includes('5')&&grouped.explanation[0].includes('2'),'mixed position explanation');
assert(grouped.explanation[1].includes('Ομαδοποιημένο')&&grouped.explanation[1].includes('ενδιάμεσες θέσεις'),'mixed label explanation');
// All actual ether and ester entries exercise fragment metadata and common parts.
for(const [key,name,common] of [
 ['ethyl_methyl_ether','μεθοξυαιθάνιο','αιθυλομεθυλαιθέρας'],
 ['dimethylether','μεθοξυμεθάνιο','διμεθυλαιθέρας'],
 ['diethyl_ether','αιθοξυαιθάνιο','διαιθυλαιθέρας'],
 ['isopropyl_methyl_ether','2-μεθοξυπροπάνιο','ισοπροπυλομεθυλαιθέρας'],
 ['ethanoic_methyl_ester','αιθανικός μεθυλεστέρας'],
 ['propanoic_methyl_ester','προπανικός μεθυλεστέρας']]){
 const r=run(null,null,{key});same(r.initial.name,name,key);
 if(common){same(r.initial.common,common,key+' common');assert(r.initial.etherParts.parts.some(p=>p.label.includes(key.includes('isopropyl')?'ισοπροπυλ':key==='diethyl_ether'?'αιθυλ':'μεθυλ')),key+' viewer common');}
}
// Heteroatom attachment leaves the same three-carbon fragment classification.
for(const iso of [false,true]){
 const e=graph(6,[[1,2,1],[2,3,1],[3,4,1],[4,5,1],iso?[4,6,1]:[5,6,1]]);e.types[2]='O';
 const r=run(mol(e),null,{});assert(r.initial.common.includes(iso?'ισοπροπυλ':'προπυλ'),'synthetic ether fragment');
 const es=graph(7,[[1,2,2],[1,3,1],[3,4,1],[4,5,1],iso?[4,6,1]:[5,6,1],[1,7,1]]);es.types[1]='O';es.types[2]='O';
 const s=run(mol(es),null,{});same(s.initial.name,iso?'αιθανικός ισοπροπυλεστέρας':'αιθανικός προπυλεστέρας','synthetic ester fragment');
}
print('PASS same-parent equal-size2D/3D identities+H, fixed grouped slots/explanations, ether/ester controls.');
print('RESULT '+checks+' assertions passed.');
