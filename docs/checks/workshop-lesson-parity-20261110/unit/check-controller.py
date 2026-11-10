"""Full current controller with declared DOM/adapter doubles; native motion is tested separately."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent
ROOT=Path.cwd()
source=(ROOT/'js/namelecule-quiz-checkpoints.js').read_text()
js='const global=globalThis;global.window=global;\n'+(ROOT/'js/namelecule-game-repair.js').read_text()+'\nconst realRevealerFactory=NameleculeRepairGame.createResponseRevealer;\n'+(HERE/'fake-dom.js').read_text()
js+='\nconst controllerSource='+json.dumps(source)+';\n'
js+=r'''
let checks=0;const labels=[];
function check(ok,label){if(!ok)throw Error(label);checks++;labels.push(label);}
FakeNode.prototype.contains=function(node){return this===node||this.children.some(child=>child.contains(node));};
FakeNode.prototype.getBoundingClientRect=function(){return this.rect||{top:0,bottom:0,height:0};};
resetEnvironment();NameleculeRepairGame.createResponseRevealer=realRevealerFactory;new Function(controllerSource)();
const mounts=[];
NameleculeQuizCheckpoints.registerType('response-probe',{
 validate(v){return v;},restore(_r,s){return s||{solved:false};},
 mount(host,options){mounts.push({host,options});return{destroy(){}};}
});
liveScenario={title:'Response visibility guard probe',author:'Declared developer double',index:0,
 steps:[{checkpoint:{id:'response-probe',version:1,type:'response-probe',round:{}}}]};
NameleculeQuizCheckpoints.onStep(liveScenario,0);body.find('nlQuizOpen').fire('click');
const d=body.find('nlQuizDialog'),header=d.querySelector('.nl-quiz-dialog-header');
d.rect={top:10,bottom:610,height:600};d.clientTop=1;d.clientHeight=598;d.scrollHeight=2400;d.scrollTop=0;
header.rect={top:11,bottom:110,height:99};
const calls=[];d.scrollTo=function(value){calls.push({...value});this.scrollTop=value.top;};
let reduce=false;global.matchMedia=()=>({matches:reduce});
const first=mounts[0].options,host=mounts[0].host;
function target(y,height=50){const node=new FakeNode('div');node.getBoundingClientRect=()=>({top:11+y-d.scrollTop,bottom:11+y+height-d.scrollTop,height});host.append(node);return node;}
function clean(){first.onProgress(null);first.onProgress({current:1,total:3});calls.length=0;}
function reveal(start,end){first.onReveal({start,end:end||start,reason:'test-response'});}
clean();const visible=target(200);reveal(visible);
check(d.scrollTop===0&&calls.length===0,'already-visible range does not scroll');
const low=target(800);reveal(low);
check(calls.at(-1).behavior==='smooth'&&calls.at(-1).top===264,'below-view response uses minimum measured-header-safe smooth destination');
check(low.getBoundingClientRect().bottom===597,'short range ends above viewport margin');
const saved=d.scrollTop;reveal(low);
check(d.scrollTop===saved&&calls.at(-1).behavior==='instant','already-visible later response stops obsolete motion without another smooth jump');
clean();const tall=target(800,1000);reveal(tall);
check(d.scrollTop===689&&tall.getBoundingClientRect().top===122,'tall explanation starts below sticky header rather than skipping to end');
clean();const end=target(950,60);reveal(low,end);
check(d.scrollTop===424,'container range includes the following action');
clean();reduce=true;reveal(low);
check(calls.at(-1).behavior==='instant','reduced-motion preference requests no smooth animation');
reduce=false;clean();
const active=new FakeNode('button');document.activeElement=active;reveal(low);
check(document.activeElement===active&&active.focusCalls===0,'visibility request does not move focus');
const detached=target(1500);detached.remove();const before=calls.length;reveal(detached);
check(calls.length===before,'detached target is ignored');
const outside=new FakeNode('div');body.append(outside);outside.rect={top:900,bottom:950,height:50};reveal(outside);
check(calls.length===before,'connected target outside mounted host is ignored');
first.onReveal(null);first.onReveal({});check(calls.length===before,'missing target requests are ignored');
clean();const hidden=target(800,0);reveal(hidden);check(calls.length===0,'hidden target ignored');
const invalid=target(NaN);reveal(invalid);check(calls.length===0,'nonfinite geometry ignored');
clean();d.clientHeight=100;reveal(low);check(calls.length===0,'no usable viewport is ignored');d.clientHeight=598;
clean();const beyond=target(5000);reveal(beyond);check(d.scrollTop===1802,'destination clamped to actual scroll extent');
clean();d.scrollTop=500;reveal(visible);check(d.scrollTop===89,'target above header reveals its start safely');
for(const event of ['wheel','touchstart','pointerdown','keydown']){
 clean();reveal(low);const n=calls.length;d.fire(event);
 check(calls.length===n+1&&calls.at(-1).behavior==='instant',event+' hands control back to the learner');
}
clean();reveal(low);first.onProgress({current:1,total:3});
check(d.scrollTop===264,'same-round progress does not reset response position');
first.onProgress({current:2,total:3});check(d.scrollTop===0&&calls.at(-1).behavior==='instant','new round cancels motion and starts at top');
clean();reveal(low);first.onProgress(null);check(calls.at(-1).behavior==='instant','loading progress cancels obsolete motion');
clean();reveal(low);body.find('nlQuizBack').fire('click');const closedCalls=calls.length;
check(!d.open&&calls.at(-1).behavior==='instant','Back stops motion before closing');
first.onReveal({start:low});check(calls.length===closedCalls,'closed-mount callback ignored');
body.find('nlQuizOpen').fire('click');const second=mounts[1];
const reopenedCalls=calls.length;first.onReveal({start:low});check(calls.length===reopenedCalls,'earlier mount cannot move reopened dialog');
second.options.onProgress({current:2,total:3});check(d.scrollTop===0,'reopened restored round begins at top');
const newTarget=new FakeNode('div');newTarget.rect={top:900,bottom:950,height:50};second.host.append(newTarget);
const owned=liveScenario;liveScenario={...owned};second.options.onReveal({start:newTarget});
check(calls.length===reopenedCalls,'different active scenario rejects response');
liveScenario=owned;liveScenario.index=1;second.options.onReveal({start:newTarget});
check(calls.length===reopenedCalls,'different active step rejects response');
liveScenario.index=0;NameleculeQuizCheckpoints.onExit();second.options.onReveal({start:newTarget});
check(!d.open&&calls.length===reopenedCalls,'Exit rejects later response callbacks');
// A browser without Element.scrollTo still reveals immediately.
NameleculeQuizCheckpoints.onStep(liveScenario,0);body.find('nlQuizOpen').fire('click');
const third=mounts[2];third.options.onProgress({current:1,total:3});d.scrollTo=undefined;
const fallback=new FakeNode('div');fallback.rect={top:811,bottom:861,height:50};third.host.append(fallback);
third.options.onReveal({start:fallback});check(d.scrollTop===264,'missing native scroll API falls back to direct dialog position');
check(storageWrites===0,'visibility alone never persists an answer or awards progress');
print(JSON.stringify({completed:true,checks,labels,limits:['Actual full controller; supplied FakeNode DOM/storage and custom response adapter doubles.','Fake scrollTo applies destinations synchronously; no native animation or browser layout proof.','Real game interactions, generated forwarding and motion are checked separately in browser.']}));
'''
with tempfile.TemporaryDirectory(prefix='namelecule-response-jsc-',dir='/private/tmp') as temp:
 p=HERE/'controller-harness.js';p.write_text(js)
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',str(p.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
 if r.returncode:
  (HERE/'controller-failure.txt').write_text(r.stdout+r.stderr)
  raise SystemExit(r.stdout+r.stderr)
 result=json.loads(r.stdout);result['controller_sha256']=hashlib.sha256(source.encode()).hexdigest()
 (HERE/'controller-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':True,'checks':result['checks']}))
