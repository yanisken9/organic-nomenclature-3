"""Actual before/current controller in JSC; DOM and quiz adapter are declared doubles.

Browser evidence separately checks layout, real generation, answers and gates.
This probe covers callbacks which cannot safely be replayed in a learner's page.
"""
from pathlib import Path
import json,subprocess,tempfile,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
path='js/namelecule-quiz-checkpoints.js'
before=(HERE/'before'/path).read_text();after=(ROOT/path).read_text()
js='const global=globalThis;global.window=global;\n'
js+='const beforeSource='+json.dumps(before)+';\nconst afterSource='+json.dumps(after)+';\n'
js+='let checks=0;const labels=[];function check(ok,label){if(!ok)throw Error(label);checks++;labels.push(label);}\n'
js+=(HERE/'fake-dom.js').read_text()
js+=r'''
Object.defineProperty(FakeNode.prototype,'scrollTop',{get(){return this._scrollTop||0;},set(v){this._scrollTop=v;}});
function exercise(source,current){
 resetEnvironment();new Function(source)();
 const mounts=[];
 NameleculeQuizCheckpoints.registerType('scroll-probe',{
  validate(value){if(!value||value.version!==1)throw Error('bad probe');return value;},
  restore(_round,state){return state||{solved:false};},
  mount(host,options){mounts.push(options);return{destroy(){}};}
 });
 liveScenario={title:'Controller scroll regression probe',author:'Developer test',index:0,
  steps:[{checkpoint:{id:'scroll-probe-1',type:'scroll-probe',version:1,round:{version:1}}}]};
 NameleculeQuizCheckpoints.onStep(liveScenario,0);
 body.find('nlQuizOpen').fire('click');
 const dialog=body.find('nlQuizDialog'),counter=body.find('nlQuizProgress');
 const first=mounts[0];
 const prefix=current?'after: ':'before: ';
 function at(value){dialog.scrollTop=value;}
 function progress(value){first.onProgress(value);}
 at(321);progress({current:1,total:3});
 check(dialog.scrollTop===(current?0:321),prefix+'first rendered round '+(current?'starts at top':'retains old scroll'));
 check(!counter.hidden&&counter.textContent==='Κουίζ 1/3',prefix+'counter remains correct');
 at(183);progress({current:1,total:3});
 check(dialog.scrollTop===183,prefix+'same round progress preserves manual scrolling');
 progress({current:1,total:3,additional:'ignored'});
 check(dialog.scrollTop===183,prefix+'equivalent progress object does not jump');
 progress({current:2,total:3});
 check(dialog.scrollTop===(current?0:183),prefix+'round1→2 '+(current?'reveals new instructions':'reproduces retained scroll'));
 at(204);progress({current:3,total:3});
 check(dialog.scrollTop===(current?0:204),prefix+'round2→3 '+(current?'reveals new instructions':'reproduces retained scroll'));
 at(177);progress({current:3,total:3});
 check(dialog.scrollTop===177,prefix+'last-round updates preserve manual scroll');
 progress({current:3,total:4});
 check(dialog.scrollTop===(current?0:177),prefix+'new total is a distinct round context');
 for(const invalid of [null,{}, {current:0,total:3},{current:4,total:3},{current:1.5,total:3},{current:1,total:Infinity},{current:'1',total:3}]){
  at(137);progress(invalid);
  check(counter.hidden&&counter.textContent===''&&dialog.scrollTop===137,prefix+'invalid/loading progress clears counter without scroll');
 }
 progress({current:1,total:3});
 check(dialog.scrollTop===(current?0:137),prefix+'first valid round after loading starts afresh');
 at(145);body.find('nlQuizBack').fire('click');
 check(!dialog.open,prefix+'Back closes dialog');
 progress({current:2,total:3});
 check(dialog.scrollTop===145&&counter.hidden,prefix+'stale closed-mount callback is ignored');
 body.find('nlQuizOpen').fire('click');
 const second=mounts[1];at(199);
 first.onProgress({current:3,total:3});
 check(dialog.scrollTop===199&&counter.hidden,prefix+'stale earlier mount cannot scroll reopened dialog');
 second.onProgress({current:2,total:3});
 check(dialog.scrollTop===(current?0:199)&&counter.textContent==='Κουίζ 2/3',prefix+'new mount initializes restored round position');
 at(129);second.onProgress({current:2,total:3});
 check(dialog.scrollTop===129,prefix+'restored round keeps later manual scroll');
 const owned=liveScenario;liveScenario={...owned};
 second.onProgress({current:3,total:3});
 check(dialog.scrollTop===129&&counter.textContent==='Κουίζ 2/3',prefix+'different active scenario rejects old callback');
 liveScenario=owned;liveScenario.index=1;
 second.onProgress({current:3,total:3});
 check(dialog.scrollTop===129,prefix+'different step rejects old callback');
 liveScenario.index=0;NameleculeQuizCheckpoints.onExit();
 second.onProgress({current:3,total:3});
 check(!dialog.open&&dialog.scrollTop===129&&counter.hidden,prefix+'Exit rejects callbacks and closes dialog');
 return {expectedReset:current,checks:labels.filter(v=>v.startsWith(prefix)).length};
}
const runs=[exercise(beforeSource,false),exercise(afterSource,true)];
print(JSON.stringify({completed:true,checks,labels,runs,limitations:['Actual before/current controller; reused FakeNode DOM, tab storage and custom quiz adapter doubles.','No browser/layout/chemical or physical-keyboard proof from this probe.']}));
'''
with tempfile.TemporaryDirectory(prefix='namelecule-scroll-jsc-',dir='/private/tmp') as temp:
 p=Path(temp)/'check.js';p.write_text(js)
 result=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',str(p)],capture_output=True,text=True)
 if result.returncode:
  (HERE/'memory-failure.txt').write_text(result.stdout+result.stderr)
  raise SystemExit(result.stdout+result.stderr)
 data=json.loads(result.stdout)
 data['controller_sha256']=hashlib.sha256(after.encode()).hexdigest()
 (HERE/'memory-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':data['completed'],'checks':data['checks'],'runs':data['runs']}))
