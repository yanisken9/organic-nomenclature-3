const fs=require('fs'),vm=require('vm'),assert=require('assert');
const sources=[55,56,57].map(v=>({v,s:fs.readFileSync(`js/mulermoc-nom-molview-${v}.js`,'utf8')}));
const cases=[
 ['registered alkane',{},true],
 ['old molecule remains original gate',{nameExamples:{test:{}}},false],
 ['unknown display policy',{nameExamples:{test:{displayPolicy:'other'}}},false],
 ['condensed unchanged',{mode2D:'condensed'},false],
 ['skeletal unchanged',{mode2D:'skeletal'},false],
 ['heteroatom rejected',{allAtomsTypeList:['C','O','H']},false],
 ['multiple bond rejected',{bondList:[[1,2,2]]},false],
 ['other class rejected',{fGetMoleculeClassification:()=>({seriesKey:'alkenes'})},false],
 ['missing class rejected',{fGetMoleculeClassification:undefined},false],
 ['empty structure rejected',{allAtomsTypeList:[]},false],
 ['classifier error fails closed',{fGetMoleculeClassification:()=>{throw Error('probe')}},false]
];let checks=0;
for(const {v,s} of sources){
 const start=s.indexOf('  const registeredAlkaneScale = '),end=s.indexOf('\n  const esterScale = ',start);assert(start>0&&end>start);
 for(const [label,overrides,expected]of cases){
  const box={selectedMol:'test',mode2D:'expanded',nameExamples:{test:{displayPolicy:'namelecule-alkane-20261030'}},allAtomsTypeList:['C','C','H'],bondList:[[1,2,1],[1,3,1]],fGetMoleculeClassification:()=>({seriesKey:'alkanes'}),...overrides};
  vm.createContext(box);assert.strictEqual(vm.runInContext(s.slice(start,end)+'\nregisteredAlkaneScale',box),expected,`${v} ${label}`);checks++;
 }
}
const out={role:'Developer extracted actual shared-gate regression',checks,viewers:sources.map(x=>x.v),passed:true};
fs.writeFileSync('docs/checks/alkane-pool-implementation-20261116/root/calibration-gate-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
