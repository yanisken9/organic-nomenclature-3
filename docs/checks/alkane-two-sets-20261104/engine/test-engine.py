"""Six-round grading, state and schema boundary checks in JavaScriptCore."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path.cwd();HERE=ROOT/'docs/checks/alkane-two-sets-20261104/engine';game=json.loads((ROOT/'games/data/name-repair-alkanes.json').read_text())
tests=r'''
const E=NameleculeRepairEngine,D=GAME;let checks=0;
function ok(v,label){checks++;if(!v)throw Error(label)}
ok(E.validateGameData(D)===D,'Schema2pack accepted');
ok(D.sets.length===2&&D.sets.every(s=>s.rounds.length===3),'Exactly two sets of three');
const rounds=D.sets.flatMap(s=>s.rounds),states=rounds.map(r=>E.createRoundState(r));
rounds.forEach((r,i)=>{
 const s=states[i];ok(E.candidateName(r,s)!==r.correctName,'Starts faulty '+r.id);
 if(r.kind==='replace'){
  ok(E.evaluateRepair(r,s).kind==='incomplete','Unselected cannot pass '+r.id);s.selectedPartId=r.targetPartId;
  for(const c of r.choices){s.selectedValue=c.value;const result=E.evaluateRepair(r,s);ok((result.kind==='correct')===(c.value===r.correctValue),'Every choice graded '+r.id+c.value);ok(!!result.message,'Every submitted choice has feedback '+r.id+c.value)}
  s.selectedValue=r.correctValue;s.selectedPartId=r.parts.find(p=>p.id!==r.targetPartId).id;ok(E.evaluateRepair(r,s).kind==='wrongPart','Wrong part cannot pass '+r.id);s.selectedPartId=r.targetPartId;
 }else{
  ok(E.evaluateRepair(r,s).kind==='unchanged','Ordering begins wrong');const a=E.movePart(s.order,s.order[1],-1),b=E.movePart(s.order,s.order[0],1);ok(a.join()===b.join(),'Both valid moves accepted');s.order=a;ok(E.movePart(a,a[0],-1).join()===a.join(),'Left boundary');ok(E.movePart(a,a[1],1).join()===a.join(),'Right boundary');ok(E.movePart(a,'absent',1).join()===a.join(),'Unknown group');
 }
 ok(E.evaluateRepair(r,s).kind==='correct','Correct repair '+r.id);ok(E.candidateName(r,s)===r.correctName,'Exact spelling '+r.id);s.attempts=3;s.selectionMisses=2;s.submitted=true;s.solved=true;
 ok(E.restoreRoundState(r,s).solved,'Legal submitted success restores '+r.id);
 const retry=E.createRoundState(r,s);ok(retry.attempts===3&&retry.selectionMisses===2&&!retry.solved&&!retry.submitted,'Retry preserves evidence '+r.id);ok(E.candidateName(r,retry)!==r.correctName,'Retry resets candidate '+r.id);ok(retry.choiceOrder.join()===s.choiceOrder.join(),'Retry keeps choices '+r.id);
 if(r.kind==='replace')ok([...s.choiceOrder].sort().join()===r.choices.map((_,i)=>i).join(),'Choice permutation '+r.id);
 ok(r.guided===false&&!('hints' in r),'No rehearsal or hints '+r.id);ok(r.feedback.wrongPart==='Αυτό το συνθετικό συμφωνεί με τη δομή.','Minimal wrong-part feedback '+r.id);ok(r.successText.length>80,'Explanation available '+r.id);
});
for(let i=0;i<2;i++){const sum=E.summarizeGame(D.sets[i].rounds,states.slice(i*3,i*3+3));ok(sum.total===3&&sum.completed===3&&sum.attempts===9,'Summary isolated to active set '+i);ok(!('hints'in sum)&&!('assisted'in sum)&&!('independent'in sum),'No removed scoring classes '+i)}
const bond=D.sets[0].rounds[1],original=E.createRoundState(bond);original.selectedPartId=bond.targetPartId;original.selectedValue='έν';ok(E.evaluateRepair(bond,original).kind==='unchanged'&&E.evaluateRepair(bond,original).message===bond.feedback.unchanged,'Original bond choice uses unchanged guard');
function invalid(change,label){const d=JSON.parse(JSON.stringify(D));change(d);let thrown=false;try{E.validateGameData(d)}catch(e){thrown=true}ok(thrown,label)}
invalid(d=>d.schemaVersion=1,'Old schema rejected');invalid(d=>d.rounds=d.sets[0].rounds,'Flat mixed pack rejected');invalid(d=>delete d.sets,'Missing sets rejected');invalid(d=>d.sets.pop(),'Single set rejected');invalid(d=>d.sets.push(d.sets[0]),'Third set rejected');invalid(d=>d.sets[1].id=d.sets[0].id,'Duplicate set id rejected');invalid(d=>d.sets[1].id='unknown','Unknown set id rejected');invalid(d=>d.sets[0].description='','Missing description rejected');invalid(d=>d.sets[0].topics=[],'Missing topics rejected');invalid(d=>d.sets[0].topics=[null],'Invalid topic rejected');
for(const i of [0,1]){invalid(d=>d.sets[i].rounds.pop(),'Two-round set rejected '+i);invalid(d=>d.sets[i].rounds.push(d.sets[i].rounds[0]),'Four-round set rejected '+i);invalid(d=>d.sets[i].rounds[0].guided=true,'Guided rejected '+i);invalid(d=>delete d.sets[i].rounds[0].guided,'Missing standalone guidedfalse rejected '+i)}
invalid(d=>d.sets[1].rounds[0].id=d.sets[0].rounds[0].id,'Cross-set duplicate round rejected');invalid(d=>d.sets[0].rounds[0].id=d.sets[0].rounds[1].id,'In-set duplicate round rejected');invalid(d=>d.sets[0].rounds[0].correctName='invalid','Mismatched exact name rejected');invalid(d=>d.sets[0].rounds[0].asset='../../secret.svg','Nonlocal asset rejected');invalid(d=>d.sets[0].rounds[0].parts[1].id=d.sets[0].rounds[0].parts[0].id,'Duplicate parts rejected');invalid(d=>d.sets[0].rounds[0].choices[0].value=d.sets[0].rounds[0].choices[1].value,'Duplicate choice rejected');invalid(d=>d.sets[1].rounds[2].correctOrder=['ethylGroup','ethylGroup'],'Duplicate order rejected');invalid(d=>d.sets[1].rounds[2].correctOrder=d.sets[1].rounds[2].movablePartIds.slice(),'Already correct ordering rejected');
print(JSON.stringify({completed:true,checks,sets:2,rounds:rounds.length}));
'''
source=(ROOT/'js/namelecule-game-repair.js').read_text()+'\nconst GAME='+json.dumps(game,ensure_ascii=False)+';\n'+tests
run=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(source)+'\n',text=True,capture_output=True)
if run.returncode:print(run.stdout,run.stderr);raise SystemExit(run.returncode)
result=json.loads(run.stdout);result['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-game-repair.js','games/data/name-repair-alkanes.json']};(HERE/'engine.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(run.stdout)
