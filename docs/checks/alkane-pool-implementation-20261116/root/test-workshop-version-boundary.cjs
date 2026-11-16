const fs=require('fs'),vm=require('vm'),assert=require('assert');
const s=fs.readFileSync('js/namelecule-game-repair.js','utf8');let checks=0;
function extract(name){
 const re=new RegExp('^  (?:async )?function '+name+'\\(','m'),m=re.exec(s);assert(m,name);
 let start=s.indexOf('{',m.index),depth=0,quote=null,escape=false,line=false,block=false;
 for(let i=start;i<s.length;i++){
  const c=s[i],n=s[i+1];
  if(line){if(c==='\n')line=false;continue;}if(block){if(c==='*'&&n==='/'){block=false;i++;}continue;}
  if(quote){if(escape)escape=false;else if(c==='\\')escape=true;else if(c===quote)quote=null;continue;}
  if(c==='/'&&n==='/'){line=true;i++;continue;}if(c==='/'&&n==='*'){block=true;i++;continue;}
  if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;else if(c==='}'&&!--depth)return s.slice(m.index,i+1).trim();
 }
 throw Error('Unclosed function '+name);
}
function box(revision='legacy',params='catalog=legacy'){
 const b={URL,URLSearchParams,DOMException,location:{href:'https://example.test/repo/games/name-repair.html?'+params,assign(url){b.url=url}},entryParams:new URLSearchParams(params),pilot:{catalog:{revision}},pilotPhase:'results',activeSet:{id:'alkanes-branched'},states:[{solved:true}],roundIndex:2,legacyPilotStorageKey:'legacy-key',enrichedPilotStorageKey:'new-key',pilotStorageKey:'legacy-key',newSeed:()=> 'fresh',generatePilotGame:()=>{b.generated++},generated:0,saves:0,savePilotProgress:()=>{b.saves++}};
 b.global=b;b.NameleculeGeneratedRepairCheckpoint={catalogDescriptor:()=>({revision:'legacy'})};vm.createContext(b);
 return b;
}
(async()=>{
 for(const params of ['source=engine','source=engine&catalog=legacy']){
  for(const fn of ['startSet','renderSetPicker','restartGame']){
   const b=box('legacy',params);vm.runInContext(extract('redirectLegacyAttempt')+'\n'+extract(fn),b);const before=JSON.stringify({pilotPhase:b.pilotPhase,activeSet:b.activeSet,states:b.states,roundIndex:b.roundIndex});
   vm.runInContext(fn+'('+ (fn==='startSet'?'"alkanes-branched"':'') +')',b);
   const url=new URL(b.url);assert.equal(url.searchParams.get('catalog'),'enriched');assert.equal(url.searchParams.get('source'),null);assert.equal(url.searchParams.get('startSet'),fn==='startSet'?'alkanes-branched':null);assert.equal(url.searchParams.get('pickSet'),fn==='startSet'?null:'1');
   assert.equal(b.generated,0);assert.equal(b.saves,0);assert.equal(JSON.stringify({pilotPhase:b.pilotPhase,activeSet:b.activeSet,states:b.states,roundIndex:b.roundIndex}),before);checks+=8;
  }
 }
 const phases=['round','results','hub','picker','invalid',null];
 for(const explicit of [false,true])for(const phase of phases){
  const b=box('legacy',explicit?'catalog=legacy':'source=engine');b.NameleculeChemistryClient={};b.NameleculeRepairGenerator={};b.NameleculeGeneratedRepairCheckpoint={catalogDescriptor:ref=>({id:ref||'legacy',revision:ref||'legacy',engineSHA256:'engine'}),loadCanonicalInput:async(_signal,d)=>({catalog:{revision:d.revision},analyses:[]})};
  const record=phase?{version:1,catalogRevision:'legacy',engineSHA256:'engine',phase,valid:phase!=='invalid'}:null;
  b.readPilotProgress=(k=b.pilotStorageKey)=>k==='legacy-key'?record:null;b.restorePilotProgress=r=>{if(!r?.valid)return false;b.pilotPhase=r.phase;return true};
  vm.runInContext(extract('preparePilot'),b);await vm.runInContext('preparePilot({aborted:false})',b);
  const legacy=['round','results'].includes(phase);assert.equal(b.pilot.catalog.revision,legacy?'legacy':'enriched');assert.equal(b.pilotStorageKey,legacy?'legacy-key':'new-key');assert.equal(b.saves,0);checks+=3;
 }
 const out={role:'Developer actual extracted Workshop lifecycle regression',checks,passed:true,scope:'Implicit/explicit legacy partial/results restore, invalid/hub/picker fallback, start/picker/restart migration before saves/resets'};
 fs.writeFileSync('docs/checks/alkane-pool-implementation-20261116/root/workshop-version-boundary-results.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
})().catch(e=>{console.error(e);process.exitCode=1});
