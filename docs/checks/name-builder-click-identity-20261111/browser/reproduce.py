from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'completed':False,'checks':[],'attempts':[],'mismatches':[],'role':'Developer read-only product reproduction using trusted pointer input'}
call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'''() => {
 window.__tileInput=[];
 const tile=n=>{let b=n?.closest?.('.tile-button');return b?{id:b.dataset.tileId,text:b.textContent,bank:!!b.closest('#bank-tiles')}:null};
 for(let type of ['pointerdown','pointerup','click','lostpointercapture'])addEventListener(type,e=>{
  if(!tile(e.target))return;
  const row={type,target:tile(e.target),hit:tile(document.elementFromPoint(e.clientX,e.clientY)),x:e.clientX,y:e.clientY,scrollY,active:tile(document.activeElement),time:performance.now(),trusted:e.isTrusted};
  __tileInput.push(row);
  queueMicrotask(()=>{row.answer=[...document.querySelectorAll('#answer-tiles button')].map(b=>({id:b.dataset.tileId,text:b.textContent}));row.candidate=document.querySelector('#candidate-name')?.textContent;});
 },true);
}'''})
try:
 for width,height in [(1280,900),(1024,900),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  open_page('games/name-builder.html?v=click-investigation&molecule=dimethyl_4_5_hexen_5_yn_1_one_3');wait('document.querySelectorAll("#bank-tiles button").length>0',60)
  initial=read('[...document.querySelectorAll("#bank-tiles button")].map(b=>({id:b.dataset.tileId,text:b.textContent}))')
  for i in range(min(12,len(initial))):
   target=initial[i]
   selector='#bank-tiles button[data-tile-id="'+target['id']+'"]'
   before=read('[...document.querySelectorAll("#answer-tiles button")].map(b=>({id:b.dataset.tileId,text:b.textContent}))')
   click(selector)
   after=read('[...document.querySelectorAll("#answer-tiles button")].map(b=>({id:b.dataset.tileId,text:b.textContent}))')
   events=read('__tileInput.splice(0)')
   expected=before+[target]
   row={'width':width,'index':i,'intended':target,'before':before,'after':after,'expected':expected,'events':events}
   out['attempts'].append(row)
   if after!=expected:out['mismatches'].append(row)
   print(('MATCH ' if after==expected else 'MISMATCH ')+str(width)+' '+str(i)+' '+target['text'],flush=True)
  out['checks'].append({'width':width,'bankIdsUnique':len({t['id'] for t in initial})==len(initial),'finalCandidate':read('document.querySelector("#candidate-name").textContent')})
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('reproduce-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'reproduce.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
print(json.dumps({'completed':out['completed'],'attempts':len(out['attempts']),'mismatches':len(out['mismatches']),'errors':len(js_errors)},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
