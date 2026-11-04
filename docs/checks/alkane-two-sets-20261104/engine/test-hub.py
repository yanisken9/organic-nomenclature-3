"""Two-set hierarchy, isolation/reset and results with a DOM double, not browser evidence."""
from pathlib import Path
import ast,hashlib,json,subprocess
root=Path.cwd();here=root/'docs/checks/alkane-two-sets-20261104/engine';module=ast.parse((here/'test-mount.py').read_text());dom=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dom' for t in n.targets));game=json.loads((root/'games/data/name-repair-alkanes.json').read_text())
setup=r'''
const gameRoot=document.createElement('main');gameRoot.id='game-root';document.body.append(gameRoot);
function fetch(){return Promise.resolve({ok:true,json(){return Promise.resolve(GAME)}})}
const console={error(){throw Error('Unexpected game load failure')}};
'''
tests=r'''
let checks=0;const originalGame=JSON.stringify(GAME);
function ok(v,label){checks++;if(!v)throw Error(label)}
function buttons(h){return h.querySelectorAll('button')}
function button(h,label){const b=buttons(h).find(e=>e.textContent===label);if(!b)throw Error('Missing '+label);return b}
function choice(value){const b=gameRoot.querySelector('.choices').querySelectorAll('button').find(e=>e.textContent===value);if(!b)throw Error('Missing choice '+value);return b}
function loaded(){const i=gameRoot.querySelector('.diagram-image');i.naturalWidth=600;i.onload()}
function family(){return gameRoot.querySelector('.workshop-set-picker')}
function select(set){gameRoot.querySelector('#set-'+set.id+'-start').click()}
function confirm(){return document.body.querySelector('.confirm-dialog')}
function prepare(r){if(r.kind==='replace'){button(gameRoot,r.parts.find(p=>p.id===r.targetPartId).text).click();choice(r.choices.find(c=>c.value===r.correctValue).label).click()}else{button(gameRoot,r.parts.find(p=>p.id===r.movablePartIds[0]).text).click();button(gameRoot,'Δεξιά →').click()}}
function solve(r){prepare(r);button(gameRoot,'Έλεγχος  ✓').click()}
function assertFamily(label){ok(family()&&gameRoot.querySelector('h1').textContent==='Αλκάνια',label);ok(gameRoot.querySelectorAll('.workshop-set-card').length===2,'Two family cards '+label)}
async function run(){
 await Promise.resolve();await Promise.resolve();await Promise.resolve();
 ok(gameRoot.querySelector('.workshop-hub')&&!family(),'Generic hub boots without a selected set');
 ok(gameRoot.querySelector('.eyebrow').textContent==='ΠΑΙΧΝΙΔΙΑ ΟΝΟΜΑΤΟΛΟΓΙΑΣ','Generic eyebrow preserved');
 ok(gameRoot.querySelector('.workshop-logo').getAttribute('src')==='assets/name-repair/workshop-logo-3d-v1.png','Original3Dlogo preserved');
 ok(gameRoot.querySelectorAll('.workshop-set-card').length===1&&gameRoot.querySelector('#set-alkanes-title').textContent==='Αλκάνια','One generic Alkane card');
 ok(gameRoot.querySelector('.workshop-set-meta').textContent==='2 σετ3 κουίζ ανά σετ','Generic metadata two sets/three quizzes');
 ok(gameRoot.querySelector('#set-alkanes-start').textContent==='Δες τα σετ →','Generic card opens family selection');
 ok(gameRoot.querySelector('.intro-how').querySelectorAll('.how-item').length===3,'Three how instructions preserved');
 gameRoot.querySelector('#set-alkanes-start').click();assertFamily('Alkane family picker');
 ok(gameRoot.contains(document.activeElement)&&document.activeElement===gameRoot.querySelector('h1'),'Family heading focus');
 for(const s of GAME.sets){const c=gameRoot.querySelector('#set-'+s.id+'-title');ok(c&&c.textContent===s.title,'Exact family title '+s.id);ok(gameRoot.querySelector('#set-'+s.id+'-start'),'Exact set start id '+s.id)}
 ok(gameRoot.querySelectorAll('.workshop-set-meta').every(x=>x.textContent==='3 κουίζΧωρίς χρονόμετρο'),'Each set advertises3untimed quizzes');
 gameRoot.querySelector('#workshop-all-sets').click();ok(gameRoot.querySelector('.workshop-hub')&&!family()&&document.activeElement===gameRoot.querySelector('h1'),'All sets returns to focused generic hub');
 gameRoot.querySelector('#set-alkanes-start').click();select(GAME.sets[0]);
 ok(gameRoot.querySelector('.round-heading').querySelector('h1').textContent===GAME.sets[0].rounds[0].title,'Unbranched starts its first actual quiz');
 ok(gameRoot.querySelector('.round-set-name').textContent==='Αλκάνια · '+GAME.sets[0].title,'Round displays selected set identity');
 ok(gameRoot.querySelectorAll('.progress-dot').map(x=>x.textContent).join(',')==='1,2,3','Progress numbered1–3');
 ok(gameRoot.querySelectorAll('.progress-label').every((x,i)=>x.textContent.startsWith('Κουίζ '+(i+1))),'Accessible quiz labels1–3');
 ok(!gameRoot.querySelector('.guided-pill'),'No rehearsal');
 button(gameRoot,'Επιστροφή στα σετ').click();assertFamily('No-progress return reaches family');ok(!confirm()&&document.activeElement===gameRoot.querySelector('h1'),'No-progress return focus without dialog');
 select(GAME.sets[0]);loaded();prepare(GAME.sets[0].rounds[0]);button(gameRoot,'Επιστροφή στα σετ').click();
 ok(confirm()&&confirm().textContent.includes('προσπάθειες αυτού του σετ θα μηδενιστούν'),'Partial answer asks before reset');button(confirm(),'Συνέχισε εδώ').click();
 ok(!confirm()&&gameRoot.querySelector('.candidate-name').textContent===GAME.sets[0].rounds[0].correctName,'Cancel preserves prepared answer');
 ok(!gameRoot.querySelector('.success-explanation'),'Prepared answer remains unsubmitted after cancel');
 button(gameRoot,'Επιστροφή στα σετ').click();button(confirm(),'Επιστροφή στα σετ').click();assertFamily('Confirmed partial return');
 for(let setIndex=0;setIndex<GAME.sets.length;setIndex++){
  const s=GAME.sets[setIndex];select(s);loaded();
  ok(gameRoot.querySelector('.session-row').textContent.includes('αποστολή 0'),'New selected set begins with0attempts '+s.id);
  ok(!gameRoot.querySelector('.candidate-name').textContent.includes('undefined')&&!gameRoot.querySelector('.success-explanation'),'Selected set begins without previous answer '+s.id);
  for(let n=0;n<s.rounds.length;n++){
   const r=s.rounds[n];if(n)loaded();
   ok(gameRoot.querySelector('.round-set-name').textContent==='Αλκάνια · '+s.title,'Set identity persists on quiz '+r.id);
   ok(gameRoot.querySelector('.round-heading').querySelector('h1').textContent===r.title,'Exact quiz order '+r.id);
   if(n===0){button(gameRoot,r.parts.find(p=>p.id===r.targetPartId).text).click();choice(r.choices.find(c=>c.value!==r.correctValue).label).click();button(gameRoot,'Έλεγχος  ✓').click();ok(!gameRoot.querySelector('.success-explanation'),'Wrong answer stays unsolved '+s.id)}
   solve(r);ok(gameRoot.querySelector('.success-name').textContent===r.correctName,'Exact correct name '+r.id);ok(gameRoot.querySelector('.success-explanation').textContent===r.successText,'Authored success explanation '+r.id);
   button(gameRoot,n===2?'Δες τις επισκευές σου  →':'Επόμενο κουίζ  →').click();
  }
  ok(gameRoot.querySelector('.results-set-name').textContent==='Αλκάνια · '+s.title,'Results show selected identity '+s.id);
  ok(gameRoot.querySelector('h1').textContent==='3 ονόματα στη θέση τους','Results title uses3 '+s.id);
  ok(gameRoot.querySelectorAll('.result-item').length===3,'Exactly3results '+s.id);
  ok(gameRoot.querySelectorAll('.result-name').map(x=>x.textContent).join('|')===s.rounds.map(r=>r.correctName).join('|'),'Only selected set names in results '+s.id);
  ok(gameRoot.querySelectorAll('.stat-number').map(x=>x.textContent).join(',')==='3,4','Isolated3completed/4attempts '+s.id);
  ok(!/παράδειγμα|καθοδηγ|πρόβα/i.test(gameRoot.textContent),'No rehearsal in results '+s.id);
  ok(gameRoot.querySelector('.results-actions').querySelector('a').getAttribute('href')==='../design/welcome-proposal.html','Main return link preserved '+s.id);
  button(gameRoot,'Επιστροφή στα σετ').click();assertFamily('Results return '+s.id);ok(document.activeElement===gameRoot.querySelector('h1'),'Family heading focus after results '+s.id);
 }
 select(GAME.sets[0]);loaded();ok(gameRoot.querySelector('.session-row').textContent.includes('αποστολή 0')&&!gameRoot.querySelector('.success-explanation'),'Revisiting earlier set starts fresh without sibling progress');
 solve(GAME.sets[0].rounds[0]);button(gameRoot,'Επόμενο κουίζ  →').click();button(gameRoot,'Επιστροφή στα σετ').click();ok(confirm(),'Earlier completed quiz triggers reset confirmation');button(confirm(),'Συνέχισε εδώ').click();ok(gameRoot.querySelector('.round-heading').querySelector('h1').textContent===GAME.sets[0].rounds[1].title,'Cancel preserves current quiz after earlier completion');
 button(gameRoot,'Επιστροφή στα σετ').click();button(confirm(),'Επιστροφή στα σετ').click();assertFamily('Final confirmed reset');
 ok(JSON.stringify(GAME)===originalGame,'Quiz/set data immutable across selection, reset and both results');
 print(JSON.stringify({completed:true,checks,mode:'unit DOM double; not actual browser/image evidence',sets:2,rounds:6}));
}
run().catch(e=>{print(JSON.stringify({completed:false,checks,error:String(e),stack:e.stack}));});
'''
source=dom+'\nconst GAME='+json.dumps(game,ensure_ascii=False)+';\n'+setup+'\n'+(root/'js/namelecule-game-repair.js').read_text()+'\n'+tests
run=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(source)+'\n',text=True,capture_output=True)
if run.returncode:print(run.stdout,run.stderr);raise SystemExit(run.returncode)
result=json.loads(run.stdout);assert result['completed'],result
result['sourceSHA256']={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['js/namelecule-game-repair.js','games/data/name-repair-alkanes.json']};(here/'hub-unit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(run.stdout)
