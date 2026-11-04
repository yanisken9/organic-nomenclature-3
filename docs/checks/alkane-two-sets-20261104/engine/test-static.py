"""Bounded preservation checks against this approved unit's local before copies."""
from pathlib import Path
import hashlib,json,difflib
root=Path.cwd();here=root/'docs/checks/alkane-two-sets-20261104/engine';before=here.parent/'before';js=root/'js/namelecule-game-repair.js';data=root/'games/data/name-repair-alkanes.json';bjs=(before/js.name).read_text();ajs=js.read_text();old=json.loads((before/data.name).read_text());new=json.loads(data.read_text());checks=0

def ok(v,label):
 global checks
 checks+=1
 assert v,label

def between(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
for name,end in [('createRoundState','  function candidateName'),('candidateName','  function movePart'),('movePart','  function evaluateRepair'),('evaluateRepair','  function summarizeGame'),('summarizeGame','  function assert'),('validateRoundData','  function validateGameData'),('restoreRoundState','  const engine')]:ok(between(bjs,'  function '+name+'(',end)==between(ajs,'  function '+name+'(',end),'Unchanged '+name)
identity='      if (standalone && options.setTitle) heading.append(node("p", { class: "round-set-name", text: "Αλκάνια · " + options.setTitle }));\n'
ok(between(bjs,'  function createRoundView(','  global.NameleculeRepairGame')==between(ajs,'  function createRoundView(','  global.NameleculeRepairGame').replace(identity,''),'Only optional standalone identity changed in shared renderer')
ok(between(bjs,'  global.NameleculeRepairGame','  if (typeof document')==between(ajs,'  global.NameleculeRepairGame','  if (typeof document'),'Public mount API unchanged')
pilot=root/'scenarios/alkanes-name-repair-pilot.scenario.json';base=json.loads((here/'baseline.json').read_text());ok(hashlib.sha256(pilot.read_bytes()).hexdigest()==base['embeddedPilotSHA256'],'Embedded pilot bytes unchanged')
neutral='Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.';branched=new['sets'][1]['rounds'];oldbranches=old['rounds'][1:]
for i,(newr,oldr) in enumerate(zip(branched,oldbranches)):
 ok({k:v for k,v in newr.items() if k!='objective'}=={k:v for k,v in oldr.items() if k!='objective'},'Branched content preserved except objective '+newr['id'])
 ok(newr['objective']==(neutral if i<2 else 'Οι ομάδες του ονόματος μπήκαν σε λάθος σειρά. Επίλεξε μια ομάδα και μετακίνησέ τη.'),'Branched objective approved '+newr['id'])
expected=[('unbranched-parent-four','butane',['προπ','άν','ιο'],'root','βουτ',['αιθ','βουτ','πεντ'],'βουτάνιο'),('unbranched-single-bond','ethane',['αιθ','έν','ιο'],'saturation','άν',['άν','έν','ίν'],'αιθάνιο'),('unbranched-parent-five','pentane',['εξ','άν','ιο'],'root','πεντ',['προπ','βουτ','πεντ'],'πεντάνιο')]
for r,e in zip(new['sets'][0]['rounds'],expected):
 ok((r['id'],r['moleculeId'],[p['text'] for p in r['parts']],r['targetPartId'],r['correctValue'],[c['value'] for c in r['choices']],r['correctName'])==e,'Approved linear question '+r['id'])
 ok([p['label'] for p in r['parts']]==['Μήκος κύριας αλυσίδας','Είδος δεσμών','Χημική τάξη'],'Neutral labels '+r['id'])
 ok(r['objective']==neutral and r['guided'] is False,'Neutral challenge '+r['id'])
 ok(r['feedback']['wrongPart']=='Αυτό το συνθετικό συμφωνεί με τη δομή.' and r['feedback']['unchanged']=='Διάλεξε αντικατάσταση για το λανθασμένο συνθετικό.','Approved minimal/unchanged feedback '+r['id'])
ok('parent-not-total' not in [r['id'] for s in new['sets'] for r in s['rounds']],'Parent-not-total removed only from standalone')
ok(next(s['checkpoint']['round'] for s in json.loads(pilot.read_text())['steps'] if 'checkpoint' in s)['id']=='parent-not-total','Embedded still contains parent-not-total')
for p in [js,data]:ok(p.read_text().endswith('\n') and all(line.rstrip()==line for line in p.read_text().splitlines()),'Whitespace '+p.name)
result={'completed':True,'checks':checks,'base':base['base'],'sets':[{'id':s['id'],'quizzes':len(s['rounds'])} for s in new['sets']],'sharedRendererChange':'optional standalone set identity only','sourceSHA256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [js,data]},'embeddedPilotSHA256':base['embeddedPilotSHA256'],'untested':'Actual browser/layout/image assets are root-owned checks; DOM unit checks do not verify real images'}
(here/'static.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
diff=''
for p in [js,data]:diff+=''.join(difflib.unified_diff((before/p.name).read_text().splitlines(True),p.read_text().splitlines(True),fromfile=str(p.relative_to(root))+'.before',tofile=str(p.relative_to(root))))
(here/'source.diff').write_text(diff);print(json.dumps(result,ensure_ascii=False,indent=2))
