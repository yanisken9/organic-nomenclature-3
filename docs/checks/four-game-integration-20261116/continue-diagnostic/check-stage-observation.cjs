/* Controlled memory proof of the exact recorded diagnostic wrappers. No browser. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const recorded=fs.readFileSync(path.join(__dirname,'stage-observation.js'),'utf8');
const messages=[],calls=[],listeners=[];const result={sentinel:true},failure={sameException:true};let telemetryThrows=false,speechGetterCalls=0;const speechGetterReceivers=[];
class Element {
  constructor(tag='IFRAME'){this.tagName=tag;this.id='fixture-frame';this.className='fixture';this.isConnected=true;}
  getAttribute(){return 'fixture.html';}
  remove(...args){calls.push({label:'remove',receiver:this,args});if(args[0]==='throw')throw failure;return result;}
}
const speech={cancel(...args){calls.push({label:'cancel',receiver:this,args});if(args[0]==='throw')throw failure;return result;}};
const Jmol={script(...args){calls.push({label:'Jmol.script',receiver:this,args});if(args[0]==='throw')throw failure;return result;}};
const native={Jmol,addEventListener:(...args)=>listeners.push({realm:'native',args})};
Object.defineProperty(native,'speechSynthesis',{configurable:true,enumerable:true,get(){++speechGetterCalls;speechGetterReceivers.push(this);if(this.throwSpeech)throw failure;return speech;}});
const outer={document:{getElementById:()=>({contentWindow:native})},addEventListener:(...args)=>listeners.push({realm:'outer',args})};
const doc={activeElement:{tagName:'BUTTON',innerText:'Continue'},title:'fixture',visibilityState:'visible',documentElement:{},
 querySelector:selector=>selector==='.nl-detective-frame'?{contentWindow:outer}:selector==='#nlQuizDialog'?{open:true,isConnected:true}:selector==='#scNext'?{disabled:false}:{innerText:selector==='#scPos'?'4/12':'fixture'},querySelectorAll:()=>[{},{}]};
const context={RUN_ID:'memory-only',document:doc,Element,performance:{now:()=>0},Blob:class {constructor(parts){this.body=parts.join('');}},
 navigator:{sendBeacon:(_,blob)=>{if(telemetryThrows)throw failure;messages.push(JSON.parse(blob.body));return true;}},
 fetch:()=>Promise.resolve(),MutationObserver:class {observe(){}disconnect(){}},setInterval:()=>1,clearInterval(){},setTimeout:()=>1,clearTimeout(){},queueMicrotask(){},requestAnimationFrame(){},
 addEventListener:(...args)=>listeners.push({realm:'main',args}),removeEventListener(){},
 fScenarioGo(...args){calls.push({label:'fScenarioGo',receiver:this,args});if(args[0]==='throw')throw failure;return result;}};
context.window=context;vm.createContext(context);assert.equal(vm.runInContext(recorded,context),true);
let checks=0;const records=[];function check(label,fn){fn();++checks;records.push(label);}
check('3methodwrappers+speechgetterhook+2pagehide capture observers installed',()=>{const proof=messages.find(m=>m.reason==='stage-wrappers-installed');assert.equal(proof.wrappers.length,6);assert.ok(proof.wrappers.every(p=>p.installed));assert.ok(listeners.filter(l=>l.realm!=='main').every(l=>l.args[0]==='pagehide'&&l.args[2].capture===true));});
check('setup inspects descriptors without initializing speech service or readingcancel',()=>{assert.equal(speechGetterCalls,0);assert.ok(!messages.some(m=>m.reason==='native-speech-get-before'||m.reason.startsWith('native-speech-cancel')));});
check('first application speech read calls originalgetter once with native receiver,returnsidenticalservice and lazilywrapscancel',()=>{assert.equal(native.speechSynthesis,speech);assert.equal(speechGetterCalls,1);assert.equal(speechGetterReceivers.at(-1),native);assert.ok(messages.some(m=>m.reason==='native-speech-get-before'));assert.ok(messages.some(m=>m.reason==='native-speech-get-after'));assert.ok(messages.some(m=>m.reason==='native-speech-cancel-setup-write-after'));});
check('subsequentget preserves receiver and invokesoriginalexactlyoncewithoutrewrappingcancel',()=>{const before=speechGetterCalls,cancel=speech.cancel,receiver={};assert.equal(Object.getOwnPropertyDescriptor(native,'speechSynthesis').get.call(receiver),speech);assert.equal(speechGetterCalls,before+1);assert.equal(speechGetterReceivers.at(-1),receiver);assert.equal(speech.cancel,cancel);});
check('getter exception identity ispreserved andloggedwithoutcancelcall',()=>{const before=speechGetterCalls;assert.throws(()=>Object.getOwnPropertyDescriptor(native,'speechSynthesis').get.call({throwSpeech:true}),e=>e===failure);assert.equal(speechGetterCalls,before+1);assert.equal(messages.at(-1).reason,'native-speech-get-throw');});
check('main iframe remove preserves receiver,args,return and before/after',()=>{const frame=new Element();const value={x:1};assert.equal(frame.remove(value,2),result);assert.equal(calls.at(-1).receiver,frame);assert.equal(calls.at(-1).args[0],value);assert.deepEqual(messages.slice(-2).map(m=>m.reason),['main-iframe-remove-before','main-iframe-remove-after']);});
check('noniframe remove invokes original exactlyonce without telemetry',()=>{const n=messages.length,c=calls.length;const div=new Element('DIV');assert.equal(div.remove(1),result);assert.equal(calls.length,c+1);assert.equal(messages.length,n);});
check('main fScenarioGo preserves explicit receiver,args and return',()=>{const receiver={},arg={x:2};assert.equal(context.fScenarioGo.call(receiver,5,arg),result);assert.equal(calls.at(-1).receiver,receiver);assert.equal(calls.at(-1).args[1],arg);assert.deepEqual(messages.slice(-2).map(m=>m.reason),['main-fScenarioGo-before','main-fScenarioGo-after']);});
check('native speech cancel preserves receiver,args,return',()=>{const receiver={};assert.equal(speech.cancel.call(receiver,7),result);assert.equal(calls.at(-1).receiver,receiver);assert.deepEqual(calls.at(-1).args,[7]);assert.deepEqual(messages.slice(-2).map(m=>m.reason),['native-speech-cancel-before','native-speech-cancel-after']);});
check('native Jmol script preserves receiver,applet,command and caps only loggedcommand',()=>{const receiver={},applet={},command='spin off;'+('x'.repeat(150));assert.equal(Jmol.script.call(receiver,applet,command),result);assert.equal(calls.at(-1).receiver,receiver);assert.equal(calls.at(-1).args[0],applet);assert.equal(calls.at(-1).args[1],command);assert.equal(messages.at(-1).command.length,120);});
for(const [label,call]of[['remove',()=>new Element().remove('throw')],['fScenarioGo',()=>context.fScenarioGo('throw')],['speech',()=>speech.cancel('throw')],['Jmol',()=>Jmol.script('throw')]])check(label+' propagates same originalexception',()=>{assert.throws(call,error=>error===failure);assert.ok(messages.at(-1).reason.endsWith('-throw'));});
check('telemetry exceptions never prevent/replace originalgetter,call orreturn',()=>{telemetryThrows=true;const before=calls.length,gets=speechGetterCalls;assert.equal(context.fScenarioGo(5),result);assert.equal(calls.length,before+1);assert.equal(native.speechSynthesis,speech);assert.equal(speechGetterCalls,gets+1);assert.throws(()=>speech.cancel('throw'),error=>error===failure);telemetryThrows=false;});
check('outer/nativepagehide capture records use main telemetry safely',()=>{for(const realm of ['outer','native'])listeners.find(l=>l.realm===realm).args[1]({persisted:false,eventPhase:2});assert.ok(messages.some(m=>m.reason==='outerUI-pagehide-capture'));assert.ok(messages.some(m=>m.reason==='native-pagehide-capture'));});
const out={type:'Developer controlled memory proof, no browser execution',checks,passed:checks,records};fs.writeFileSync(path.join(__dirname,'stage-observation-memory.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
