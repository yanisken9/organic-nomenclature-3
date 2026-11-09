"""Lifecycle/state unit checks with a minimal DOM double, not browser evidence."""
from pathlib import Path
import json,hashlib,subprocess
root=Path.cwd(); here=root/'docs/checks/workshop-hub-20261104/engine'
game=json.loads((root/'games/data/name-repair-alkanes.json').read_text())
dom=r'''
class TestElement {
 constructor(tag){this.tagName=tag;this.children=[];this.parentNode=null;this.attributes={};this.handlers={};this.disabled=false;this.className='';this.id='';this._text='';this.naturalWidth=0;}
 get classList(){const self=this;return {contains(c){return self.className.split(' ').includes(c)},add(c){if(!this.contains(c))self.className=(self.className+' '+c).trim()},remove(c){self.className=self.className.split(' ').filter(x=>x!==c).join(' ')}}}
 set textContent(t){this._text=String(t);this.replaceChildren()}
 get textContent(){return this._text+this.children.map(c=>c.textContent).join('')}
 setAttribute(k,v){this.attributes[k]=String(v);if(k==='class')this.className=String(v);if(k==='id')this.id=String(v)}
 getAttribute(k){return k==='id'?this.id:k==='class'?this.className:this.attributes[k]}
 append(...children){for(const child of children){if(child.parentNode)child.remove();child.parentNode=this;this.children.push(child)}}
 replaceChildren(...children){for(const child of this.children)child.parentNode=null;this.children=[];this.append(...children)}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(c=>c!==this);this.parentNode=null}}
 replaceWith(next){const parent=this.parentNode;const i=parent.children.indexOf(this);this.parentNode=null;parent.children[i]=next;next.parentNode=parent}
 contains(el){return !!el&&(this===el||this.children.some(c=>c.contains(el)))}
 matches(q){if(q==='[id]')return !!this.id;if(q[0]==='.')return this.classList.contains(q.slice(1));if(q[0]==='#')return this.id===q.slice(1);return this.tagName===q}
 querySelectorAll(q){const all=[];function visit(el){for(const c of el.children){if(q.split(',').some(x=>c.matches(x.trim())))all.push(c);visit(c)}}visit(this);return all}
 querySelector(q){return this.querySelectorAll(q)[0]||null}
 addEventListener(name,fn){(this.handlers[name]||(this.handlers[name]=[])).push(fn)}
 removeEventListener(name,fn){this.handlers[name]=(this.handlers[name]||[]).filter(x=>x!==fn)}
 click(){if(!this.disabled)(this.handlers.click||[]).slice().forEach(fn=>fn({target:this}))}
 keydown(key){const e={key,target:this,defaultPrevented:false,stopped:false,preventDefault(){this.defaultPrevented=true},stopPropagation(){this.stopped=true}};let el=this;while(el){(el.handlers.keydown||[]).slice().forEach(fn=>fn(e));if(e.stopped)break;el=el.parentNode}return e}
 focus(){document.activeElement=this}
 showModal(){this.open=true}
 close(){this.open=false;(this.handlers.close||[]).slice().forEach(fn=>fn({target:this}))}
}
const document={body:new TestElement('body'),activeElement:null,createElement(t){return new TestElement(t)},createTextNode(t){const e=new TestElement('#text');e.textContent=t;return e},getElementById(id){return this.body.querySelector('#'+id)}};
let scrollCalls=0;const window={scrollTo(){scrollCalls++}};
'''
tests=r'''
const E=NameleculeRepairEngine,M=NameleculeRepairGame;let checks=0;
function ok(v,label){checks++;if(!v)throw Error(label)}
function eq(a,b,label){ok(JSON.stringify(a)===JSON.stringify(b),label)}
function clone(v){return JSON.parse(JSON.stringify(v))}
function host(){const h=document.createElement('div');document.body.append(h);return h}
function buttons(h){return h.querySelectorAll('button')}
function button(h,label){const b=buttons(h).find(e=>e.textContent===label);if(!b)throw Error('Missing button '+label);return b}
function loaded(h){const image=h.querySelector('.diagram-image');image.naturalWidth=600;image.onload()}
const r=clone(GAME.rounds[0]);delete r.guided;
ok(E.validateRoundData(r)===r,'Single question needs no guided flag');
for(const count of [0,1,3,5,6]){let threw=false;try{E.validateGameData({...GAME,rounds:Array.from({length:count},(_,i)=>GAME.rounds[i%4])})}catch(e){threw=true}ok(threw,'Standalone retains exactly four rounds '+count)}
const s=E.createRoundState(r);s.selectedPartId=r.targetPartId;s.selectedValue=r.correctValue;s.attempts=1;s.submitted=true;s.solved=true;
ok(E.restoreRoundState(r,s).solved,'Valid completion re-evaluated');
for(const bad of [{solved:true},{...s,selectedValue:'absent'},{...s,selectedPartId:'ending'},{...s,attempts:0},{...s,submitted:false},{...s,selectedValue:r.choices.find(c=>c.value!==r.correctValue).value}])ok(!E.restoreRoundState(r,bad).solved,'Unproven success rejected');
let bad=E.restoreRoundState(r,{selectedPartId:'unknown',selectedValue:r.correctValue,choiceOrder:[0,0,99],attempts:-1,selectionMisses:1.5,order:['fake']});
ok(bad.selectedPartId===null&&bad.selectedValue===null&&bad.attempts===0&&bad.selectionMisses===0,'Corrupt values discarded');
eq([...bad.choiceOrder].sort(),r.choices.map((_,i)=>i),'Bad shuffle replaced by permutation');
const order=clone(GAME.rounds[3]);
bad=E.restoreRoundState(order,{order:['absent','absent'],selectedPartId:'parent',solved:true,submitted:true,attempts:1});
eq(bad.order,order.movablePartIds,'Invalid ordering discarded');ok(!bad.solved&&bad.selectedPartId===null,'Fixed suffix cannot be selected on restore');
const h=host();const changes=[];const solved=[];const continues=[];
const view=M.mountRound(h,{round:r,assetBase:'games/',onStateChange:x=>changes.push(x),onSolved:(result,state)=>solved.push({result,state}),onContinue:x=>continues.push(x)});
ok(h.classList.contains('nl-repair-round')&&typeof view.destroy==='function','Mount public API and scoped class');
ok(h.contains(document.activeElement),'Initial focus stays in host');
ok(!h.querySelector('.intro')&&!h.querySelector('.results')&&!h.querySelector('.progress')&&!h.querySelector('.workshop-hub'),'One round skips standalone hub and screens');
ok(h.querySelector('.diagram-image').src==='games/'+r.asset,'Diagram base resolved');
ok(h.querySelector('.workshop-logo-small').getAttribute('src')==='games/assets/name-repair/workshop-logo-3d-v1.png','Logo base resolved');
ok(button(h,'Έλεγχος  ✓').disabled&&h.querySelector('.part-button').disabled,'Before image choices and submit disabled');
const initial=view.getState();initial.attempts=999;ok(view.getState().attempts===0,'getState returns copy');
h.querySelector('.diagram-image').onerror();
ok(button(h,'Έλεγχος  ✓').disabled&&button(h,'Φόρτωσε ξανά τη δομή'),'Image failure blocks assessment and offers retry');
button(h,'Φόρτωσε ξανά τη δομή').click();loaded(h);
const stalePart=button(h,r.parts[0].text);stalePart.click();
ok((stalePart.handlers.click||[]).length===0,'Replaced controls release owned handlers');
ok(h.querySelector('.part-selection-status').textContent===r.feedback.wrongPart,'Wrong-part minimal message retained');
ok(view.getState().selectionMisses===1&&view.getState().attempts===0,'Wrong-part observation is not an attempt');
button(h,r.parts.find(p=>p.id===r.targetPartId).text).click();
const wrong=r.choices.find(c=>c.value!==r.correctValue);button(h,wrong.label).click();button(h,'Έλεγχος  ✓').click();
ok(!view.getState().solved&&view.getState().attempts===1&&view.getState().submitted,'Wrong submitted attempt persisted');
ok(h.querySelector('.feedback').textContent===wrong.feedback,'Targeted incorrect feedback shared');
const choiceOrder=view.getState().choiceOrder;button(h,'Από την αρχή').click();
ok(view.getState().selectedPartId===null&&view.getState().attempts===1&&!view.getState().submitted,'Retry resets selection while preserving attempts');
eq(view.getState().choiceOrder,choiceOrder,'Retry preserves choice display order');
button(h,r.parts.find(p=>p.id===r.targetPartId).text).click();button(h,r.correctValue).click();
ok(!view.getState().solved&&solved.length===0&&!h.querySelector('.success-explanation'),'Selecting correct choice does not pass');
button(h,'Έλεγχος  ✓').click();const success=view.getState();
ok(success.solved&&success.submitted&&success.attempts===2&&solved.length===1,'Only submitted correct answer completes once');
ok(solved[0].result.kind==='correct'&&solved[0].state.solved,'Validated callback shape');
ok(h.querySelector('.success-explanation').textContent===r.successText,'Success explanation retained');
button(h,'Έλεγχος  ✓').click();ok(solved.length===1,'Repeated submit cannot double complete');
button(h,'Συνεχίζω τη θεωρία').click();ok(continues.length===1&&continues[0].solved,'Explicit Continue callback');
changes[changes.length-1].attempts=991;ok(view.getState().attempts===2,'Callback state cannot mutate component');
button(h,'Μεγέθυνση σχεδίου').click();ok(h.querySelector('.zoom-dialog')&&h.contains(document.activeElement),'Embedded zoom remains inside host');
button(h,'Κλείσιμο').click();ok(!h.querySelector('.zoom-dialog')&&h.contains(document.activeElement),'Zoom close restores host focus');
let parentKeys=0;h.addEventListener('keydown',()=>parentKeys++);
button(h,'Μεγέθυνση σχεδίου').click();const escapedZoom=h.querySelector('.zoom-dialog');
const otherKey=escapedZoom.querySelector('.zoom-viewport').keydown('ArrowRight');
ok(!otherKey.defaultPrevented&&!otherKey.stopped&&parentKeys===1&&h.querySelector('.zoom-dialog'),'Non-Escape keys remain available to viewport and parent');
const escape=escapedZoom.querySelector('.zoom-viewport').keydown('Escape');
ok(escape.defaultPrevented&&escape.stopped&&parentKeys===1,'Escape suppresses native parent cancel and propagation');
ok(!h.querySelector('.zoom-dialog')&&document.activeElement===button(h,'Μεγέθυνση σχεδίου'),'Escape closes only zoom and restores exact zoom button focus');
ok((escapedZoom.handlers.keydown||[]).length===0,'Closed embedded zoom releases its scoped key handler');
button(h,'Μεγέθυνση σχεδίου').click();const focusedEscape=document.activeElement.keydown('Escape');
ok(focusedEscape.defaultPrevented&&!h.querySelector('.zoom-dialog')&&parentKeys===1,'Escape from initially focused close control also closes only zoom');

const deadImage=h.querySelector('.diagram-image'),deadLoad=deadImage.onload,deadCheck=button(h,'Συνεχίζω τη θεωρία');const count=changes.length;
view.destroy();deadLoad();deadCheck.click();ok(h.children.length===0&&!h.classList.contains('nl-repair-round'),'Destroy removes owned DOM/class');
ok(changes.length===count&&continues.length===1&&deadImage.onload===null,'Destroy removes events and invalidates stale image callbacks');
const restored=M.mountRound(h,{round:r,assetBase:'games',initialState:success,onSolved:()=>solved.push('duplicate'),onContinue:x=>continues.push(x)});
ok(button(h,'Συνεχίζω τη θεωρία').disabled,'Restored completion waits for fresh diagram');
button(h,'Συνεχίζω τη θεωρία').click();ok(continues.length===1,'Restore cannot continue before real image load event');
loaded(h);ok(!button(h,'Συνεχίζω τη θεωρία').disabled&&solved.length===1,'Restored valid success enables continuation without fresh onSolved');
eq(restored.getState().choiceOrder,success.choiceOrder,'Refresh restores choice order');
button(h,'Συνεχίζω τη θεωρία').click();ok(continues.length===2,'Restored completion continues explicitly');
const oldLoad=h.querySelector('.diagram-image').onload;const replacement=M.mountRound(h,{round:r});oldLoad();ok(h.querySelector('.part-button').disabled,'Replacing host invalidates previous instance');
loaded(h);ok(!h.querySelector('.part-button').disabled,'Replacement alone becomes active');restored.destroy();ok(h.children.length>0,'Old destroyed handle cannot clear new mount');replacement.destroy();
const incorrectSaved=E.createRoundState(r);incorrectSaved.selectedPartId=r.targetPartId;incorrectSaved.selectedValue=wrong.value;incorrectSaved.attempts=1;incorrectSaved.submitted=true;
const wrongRestore=M.mountRound(h,{round:r,initialState:incorrectSaved});ok(h.querySelector('.feedback').textContent===wrong.feedback,'Submitted incorrect feedback restored');wrongRestore.destroy();
const h2=host();h2.classList.add('nl-repair-round');const preset=M.mountRound(h2,{round:r});preset.destroy();ok(h2.classList.contains('nl-repair-round'),'Caller-owned class retained');
const ordered=M.mountRound(h,{round:order});loaded(h);button(h,order.parts[0].text).click();button(h,'Δεξιά →').click();button(h,'Έλεγχος  ✓').click();ok(ordered.getState().solved,'Same renderer supports ordering round');ordered.destroy();
ok(scrollCalls===0,'Embedded path never scrolls window');
print(JSON.stringify({completed:true,checks,mode:'unit DOM double; not a browser or actual diagram-load check'}));
'''
source=dom+'\n'+(root/'js/namelecule-game-repair.js').read_text()+'\nconst GAME='+json.dumps(game,ensure_ascii=False)+';\n'+tests
run=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(source)+'\n',text=True,capture_output=True)
if run.returncode:
 print(run.stdout,run.stderr);raise SystemExit(run.returncode)
result=json.loads(run.stdout);result['sourceSHA256']=hashlib.sha256((root/'js/namelecule-game-repair.js').read_bytes()).hexdigest()
(here/'mount-unit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(run.stdout)
