"""Standalone hub navigation/scoring with DOM double; not browser evidence."""
from pathlib import Path
import ast,hashlib,json,subprocess
root=Path.cwd();here=root/'docs/checks/workshop-hub-20261104/engine'
module=ast.parse((here/'test-mount.py').read_text());dom=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dom' for t in n.targets))
game=json.loads((root/'games/data/name-repair-alkanes.json').read_text())
setup=r'''
const gameRoot=document.createElement('main');gameRoot.id='game-root';document.body.append(gameRoot);
function fetch(){return Promise.resolve({ok:true,json(){return Promise.resolve(GAME)}})}
const console={error(){throw Error('Unexpected game load failure')}};
'''
tests=r'''
let checks=0;
function ok(v,label){checks++;if(!v)throw Error(label)}
function buttons(h){return h.querySelectorAll('button')}
function button(h,label){const b=buttons(h).find(e=>e.textContent===label);if(!b)throw Error('Missing '+label);return b}
function loaded(){const i=gameRoot.querySelector('.diagram-image');i.naturalWidth=600;i.onload()}
function start(){gameRoot.querySelector('#set-alkanes-start').click()}
function confirm(){return document.body.querySelector('.confirm-dialog')}
async function run(){
 await Promise.resolve();await Promise.resolve();await Promise.resolve();
 ok(gameRoot.querySelector('.workshop-hub')&&gameRoot.querySelector('.workshop-hero'),'Standalone boots to generic hub');
 ok(gameRoot.querySelector('.eyebrow').textContent==='ΠΑΙΧΝΙΔΙΑ ΟΝΟΜΑΤΟΛΟΓΙΑΣ','Generic hub eyebrow');
 ok(gameRoot.querySelector('.workshop-logo').getAttribute('src')==='assets/name-repair/workshop-logo-3d-v1.png','Same standalone3Dlogo');
 ok(gameRoot.querySelectorAll('.workshop-set-card').length===1,'Exactly one active card');
 ok(gameRoot.querySelector('.workshop-sets').getAttribute('aria-labelledby')==='workshop-sets-title'&&gameRoot.querySelector('#workshop-sets-title').textContent==='Διάλεξε σετ αποστολών','Accessible set section');
 ok(gameRoot.querySelector('.workshop-set-card').getAttribute('aria-labelledby')==='set-alkanes-title'&&gameRoot.querySelector('#set-alkanes-title').textContent==='Αλκάνια','Accessible Alkane card');
 ok(gameRoot.querySelector('.workshop-set-meta').textContent==='4 αποστολέςΧωρίς χρονόμετρο','Exact four-round metadata');
 ok(gameRoot.querySelector('.workshop-set-topics').querySelectorAll('li').map(x=>x.textContent).join('|')==='Κύρια αλυσίδα|Αρίθμηση|Ίδιες διακλαδώσεις|Αλφαβητική σειρά','Four topics displayed');
 ok(gameRoot.querySelector('.intro-how').querySelectorAll('.how-item').length===3,'Existing three how instructions preserved');
 ok(!/παράδειγμα|καθοδηγ|πρόβα/i.test(gameRoot.textContent),'Hub contains no rehearsal references');
 start();ok(gameRoot.querySelector('.round-heading').querySelector('h1').textContent===GAME.rounds[0].title,'Start goes directly to first actual mission');
 ok(gameRoot.querySelectorAll('.progress-dot').map(x=>x.textContent).join(',')==='1,2,3,4','Progress visibly numbered1–4');
 ok(gameRoot.querySelectorAll('.progress-label').every((x,i)=>x.textContent.startsWith('Αποστολή '+(i+1))),'Accessible labels1–4');
 ok(!gameRoot.querySelector('.guided-pill'),'No guided UI');
 button(gameRoot,'Επιστροφή στα σετ').click();ok(gameRoot.querySelector('.workshop-hub')&&!confirm(),'No-progress return immediately reaches hub');
 ok(document.activeElement===gameRoot.querySelector('h1'),'Returning hub receives heading focus');
 start();loaded();button(gameRoot,GAME.rounds[0].parts[0].text).click();button(gameRoot,'Επιστροφή στα σετ').click();
 ok(confirm()&&confirm().textContent.includes('προσπάθειες αυτού του σετ θα μηδενιστούν'),'Progress return asks before losing work');
 button(confirm(),'Συνέχισε εδώ').click();ok(!confirm()&&gameRoot.querySelector('.round-screen'),'Cancel preserves current round');
 ok(gameRoot.querySelector('.part-selection-status').textContent===GAME.rounds[0].feedback.wrongPart,'Cancel preserves previous selection feedback');
 button(gameRoot,'Επιστροφή στα σετ').click();button(confirm(),'Επιστροφή στα σετ').click();ok(gameRoot.querySelector('.workshop-hub')&&!confirm(),'Confirmed return resets and reaches hub');
 start();loaded();ok(gameRoot.querySelector('.session-row').textContent.includes('αποστολή 0'),'Starting card resets attempt count');
 for(let n=0;n<GAME.rounds.length;n++){
  const r=GAME.rounds[n];if(n)loaded();
  ok(gameRoot.querySelector('.round-heading').querySelector('h1').textContent===r.title,'Round order '+(n+1));
  if(r.kind==='replace'){
   button(gameRoot,r.parts.find(p=>p.id===r.targetPartId).text).click();
   if(n===0){const bad=r.choices.find(c=>c.value!==r.correctValue);button(gameRoot,bad.label).click();button(gameRoot,'Έλεγχος  ✓').click();ok(!gameRoot.querySelector('.success-explanation'),'Wrong attempt remains unsolved');}
   button(gameRoot,r.choices.find(c=>c.value===r.correctValue).label).click();
  }else{button(gameRoot,r.parts.find(p=>p.id===r.movablePartIds[0]).text).click();button(gameRoot,'Δεξιά →').click();}
  button(gameRoot,'Έλεγχος  ✓').click();
  ok(gameRoot.querySelector('.success-explanation').textContent===r.successText,'Unchanged authored explanation '+(n+1));
  ok(gameRoot.querySelector('.success-name').textContent===r.correctName,'Correct exact name '+(n+1));
  button(gameRoot,n===3?'Δες τις επισκευές σου  →':'Επόμενη αποστολή  →').click();
 }
 ok(gameRoot.querySelector('.results')&&gameRoot.querySelectorAll('.result-item').length===4,'Exactly four completed repairs in results');
 const scores=gameRoot.querySelectorAll('.stat-number').map(x=>x.textContent);ok(scores.join(',')==='4,5','All four rounds counted; wrong attempt included');
 ok(!/παράδειγμα|καθοδηγ|πρόβα/i.test(gameRoot.textContent),'Results contain no rehearsal references');
 ok(gameRoot.querySelector('.results-actions').querySelector('a').getAttribute('href')==='../design/welcome-proposal.html','Main-site secondary link preserved');
 button(gameRoot,'Επιστροφή στα σετ').click();ok(gameRoot.querySelector('.workshop-hub')&&document.activeElement===gameRoot.querySelector('h1'),'Results return reaches focused hub');
 start();loaded();ok(gameRoot.querySelector('.session-row').textContent.includes('αποστολή 0')&&!gameRoot.querySelector('.success-explanation'),'New card start clears finished set progress');
 print(JSON.stringify({completed:true,checks,mode:'unit DOM double; not actual browser/image evidence',rounds:4}));
}
run().catch(e=>{print(JSON.stringify({completed:false,checks,error:String(e),stack:e.stack}));});
'''
source=dom+'\nconst GAME='+json.dumps(game,ensure_ascii=False)+';\n'+setup+'\n'+(root/'js/namelecule-game-repair.js').read_text()+'\n'+tests
run=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(source)+'\n',text=True,capture_output=True)
if run.returncode:print(run.stdout,run.stderr);raise SystemExit(run.returncode)
result=json.loads(run.stdout);assert result['completed'],result
result['sourceSHA256']={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['js/namelecule-game-repair.js','games/data/name-repair-alkanes.json']}
(here/'hub-unit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(run.stdout)
