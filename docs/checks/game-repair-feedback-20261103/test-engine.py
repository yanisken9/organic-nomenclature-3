"""Bounded grading/state checks using macOS JavaScriptCore, no app mutation."""
from pathlib import Path
import json
import hashlib
import subprocess

ROOT = Path.cwd()
HERE = ROOT / "docs/checks/game-repair-feedback-20261103"
game = json.loads((ROOT / "games/data/name-repair-alkanes.json").read_text())
tests = r"""
const E=NameleculeRepairEngine, D=GAME;let checks=0;
function ok(value,label){checks++;if(!value)throw Error(label);}
E.validateGameData(D);
const states=D.rounds.map(r=>E.createRoundState(r));
D.rounds.forEach((r,i)=>{
 const s=states[i];
 ok(E.candidateName(r,s)!==r.correctName,'Initially faulty '+r.id);
 if(r.kind==='replace'){
  ok(E.evaluateRepair(r,s).kind==='incomplete','No selection cannot pass');
  s.selectedPartId=r.targetPartId;
  for(const choice of r.choices){
   s.selectedValue=choice.value;
   const result=E.evaluateRepair(r,s);
   ok((result.kind==='correct')===(choice.value===r.correctValue),'Every choice graded '+r.id+choice.value);
   ok(!!result.message,'Every submitted choice has feedback');
  }
  s.selectedValue=r.correctValue;
  s.selectedPartId=r.parts.find(p=>p.id!==r.targetPartId).id;
  ok(E.evaluateRepair(r,s).kind==='wrongPart','Wrong part cannot pass');
  s.selectedPartId=r.targetPartId;
 }else{
  ok(E.evaluateRepair(r,s).kind==='unchanged','Order starts wrong');
  const a=E.movePart(s.order,s.order[1],-1);
  const b=E.movePart(s.order,s.order[0],1);
  ok(a.join()===b.join(),'Both valid moves accepted');
  s.order=a;
  ok(E.movePart(a,a[0],-1).join()===a.join(),'Left boundary');
  ok(E.movePart(a,a[1],1).join()===a.join(),'Right boundary');
  ok(E.movePart(a,'absent',1).join()===a.join(),'Unknown group');
 }
 ok(E.evaluateRepair(r,s).kind==='correct','Correct repair '+r.id);
 ok(E.candidateName(r,s)===r.correctName,'Exact spelling '+r.id);
 s.attempts=3;s.selectionMisses=2;s.solved=true;
 const retry=E.createRoundState(r,s);
 ok(retry.attempts===3&&retry.selectionMisses===2&&!retry.solved,'Retry preserves evidence '+r.id);
 ok(E.candidateName(r,retry)!==r.correctName,'Retry resets candidate '+r.id);
 ok(retry.choiceOrder.join()===s.choiceOrder.join(),'Retry keeps displayed choices '+r.id);
 if(r.kind==='replace')ok([...s.choiceOrder].sort().join()===r.choices.map((_,i)=>i).join(),'Choice order is a permutation '+r.id);
});
const summary=E.summarizeGame(D.rounds,states);
ok(summary.total===4&&summary.completed===4,'Guided excluded');
ok(summary.attempts===12&&!('hints' in summary)&&!('assisted' in summary)&&!('independent' in summary),'Exact summary without removed classifications');
D.rounds.forEach(r=>ok(!('hints' in r),'No hint data remains'));
ok(D.rounds.every(r=>r.feedback.wrongPart==='Αυτό το συνθετικό συμφωνεί με τη δομή.'),'Exact minimal feedback on every round');
ok(D.rounds.every(r=>r.successText.length>80),'Explanations available after success');
function invalid(change,label){const d=JSON.parse(JSON.stringify(D));change(d);let thrown=false;try{E.validateGameData(d)}catch(e){thrown=true}ok(thrown,label)}
invalid(d=>d.rounds[0].correctName='invalid','Mismatched exact name rejected');
invalid(d=>d.rounds[0].asset='../../secret.svg','Nonlocal asset rejected');
invalid(d=>d.rounds[0].parts[1].id=d.rounds[0].parts[0].id,'Duplicate parts rejected');
invalid(d=>d.rounds[1].guided=true,'Extra guided round rejected');
invalid(d=>d.rounds[4].correctOrder=['ethylGroup','ethylGroup'],'Duplicate order rejected');
invalid(d=>d.rounds[4].correctOrder=d.rounds[4].movablePartIds.slice(),'Already correct task rejected');
invalid(d=>d.rounds[0].choices[0].value=d.rounds[0].choices[1].value,'Duplicate choice rejected');
print(JSON.stringify({completed:true,checks,rounds:D.rounds.length,summary}));
"""
source = (ROOT / "js/namelecule-game-repair.js").read_text() + "\nconst GAME=" + json.dumps(game, ensure_ascii=False) + ";\n" + tests
run = subprocess.run(["/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc", "-e", "eval(JSON.parse(readline()))"], input=json.dumps(source) + "\n", text=True, capture_output=True)
if run.returncode:
    print(run.stdout, run.stderr)
    raise SystemExit(run.returncode)
result = json.loads(run.stdout)
result['sourceSHA256'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ['js/namelecule-game-repair.js', 'games/data/name-repair-alkanes.json']}
(HERE / "engine.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(run.stdout)
