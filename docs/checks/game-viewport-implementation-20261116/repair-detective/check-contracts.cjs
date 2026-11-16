'use strict';
// Developer evidence: unchanged pure answer logic and canonical bridge guards.
// No DOM/layout/native picking or browser execution is represented by this check.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..'),before=path.join(root,'docs/checks/game-viewport-implementation-20261116/before');
const read=(base,file)=>fs.readFileSync(path.join(base,file),'utf8');
const oldRepair=read(before,'js/namelecule-game-repair.js'),newRepair=read(root,'js/namelecule-game-repair.js');
const oldDetective=read(before,'js/namelecule-molecular-detective.js'),newDetective=read(root,'js/namelecule-molecular-detective.js');
const sha=value=>crypto.createHash('sha256').update(value).digest('hex');
function loadRepair(code){const context=vm.createContext({module:{exports:{}},Math:Object.assign(Object.create(Math),{random:()=>.31415})});vm.runInContext(code,context);return context.module.exports;}
const a=loadRepair(oldRepair),b=loadRepair(newRepair),groups=[];
assert.deepEqual(Object.keys(a),Object.keys(b));
for(const key of Object.keys(a))assert.equal(a[key].toString(),b[key].toString(),key+' pure logic changed');
groups.push('All exported repair engine functions are source-identical to the recorded pre-change baseline');
const data=JSON.parse(read(root,'games/data/name-repair-alkanes.json'));
let cases=0;
for(const round of data.sets.flatMap(s=>s.rounds)){
 assert.equal(JSON.stringify(a.createRoundState(round)),JSON.stringify(b.createRoundState(round)));
 const variants=[{},null,{solved:true,submitted:true,attempts:0}];
 if(round.kind==='replace')for(const part of round.parts)for(const choice of round.choices){variants.push({selectedPartId:part.id,selectedValue:choice.value,attempts:2,submitted:true,solved:false});}
 else for(const order of [round.movablePartIds,round.movablePartIds.slice().reverse()])variants.push({order,attempts:2,submitted:true,solved:true});
 for(const raw of variants){const x=a.restoreRoundState(round,raw),y=b.restoreRoundState(round,raw);assert.equal(JSON.stringify(x),JSON.stringify(y));assert.equal(JSON.stringify(a.evaluateRepair(round,x)),JSON.stringify(b.evaluateRepair(round,y)));assert.equal(a.candidateName(round,x),b.candidateName(round,y));cases++;}
}
groups.push('Authored rounds restore/evaluate identically for correct, incorrect, selected and forged completion states');
function section(code,name){const start=code.indexOf('  function '+name+'(');assert.ok(start>=0,name);const end=code.indexOf('\n  function ',start+1);return code.slice(start,end<0?code.length:end);}
for(const name of ['saveAssignment','resumeAssignment','selectAssignment','snapshot','postLesson','validateLessonLoad','validSelection','receive','check'])assert.equal(section(oldDetective,name),section(newDetective,name),name+' canonical behavior changed');
groups.push('Detective canonical load validation, native message receive, grading check, assignment and snapshot contracts are source-identical');
assert.match(newRepair,/options\.viewport === true && !!global\.NameleculeGameViewport/);
assert.match(newDetective,/!!window\.NameleculeGameViewport && \(!lesson \|\| params.get\('viewport'\) === '1'\)/);
assert.match(newDetective,/data\.requestId !== current\.requestId/);assert.match(newDetective,/data\.attemptId !== current\.attemptId/);assert.match(newDetective,/data\.moleculeId !== current\.moleculeId/);assert.match(newDetective,/data\.missionId !== current\.missionId/);assert.match(newDetective,/contextKey\(levels\.validateContext\(data\.context\)\)/);
groups.push('Legacy repair/lesson detective paths stay opt-in; viewport messages require current identity and normalized context');
const files=['games/name-repair.html','games/molecular-detective.html','js/namelecule-game-repair.js','js/namelecule-molecular-detective.js','css/namelecule-games.css','css/namelecule-repair-round.css','css/namelecule-molecular-detective.css'];
const report={recordedUTC:new Date().toISOString(),role:'Developer evidence',passed:true,groups,repairCases:cases,files:Object.fromEntries(files.map(file=>[file,{before:sha(read(before,file)),after:sha(read(root,file))}])),limits:['Pure/source contracts only; browser layout, focus, zoom and actual native picking pending exclusive browser slot','No independent review in this worker'],coreChanged:false,commit:false,publication:false};
fs.writeFileSync(path.join(__dirname,'contract-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
