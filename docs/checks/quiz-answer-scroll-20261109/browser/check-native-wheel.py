from pathlib import Path
import json,os,time,traceback
HERE=Path('docs/checks/quiz-answer-scroll-20261109/browser');p=json.loads((HERE/'process-normal.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(p['bidi_port']);exec(compile(Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(15)'),'bidi','exec'))
out={'completed':False,'scope':'Isolated fixture with no application scripts; native wheel comparison Amanualonly/Bsmooth+passiveinstantcancel, same actualdialog sizes/owner and input as failing application trace','trials':[]}
try:
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':650},'devicePixelRatio':2});navigate('docs/checks/quiz-answer-scroll-20261109/browser/native-wheel-control.html');assert ev('!matchMedia("(prefers-reduced-motion: reduce)").matches')
 for mode in ['A','B']:
  ev('startControl('+json.dumps(mode)+','+('9.3' if mode=='A' else '0')+');true')
  if mode=='B':
   until_time=time.monotonic()+.5
   while time.monotonic()<until_time:
    if ev('d.scrollTop')>=8:break
    time.sleep(.002)
  before=ev('d.scrollTop');call('input.performActions',{'context':ctx,'actions':[{'type':'wheel','id':'answer-wheel','actions':[{'type':'scroll','x':817,'y':432,'deltaX':0,'deltaY':-120,'duration':100}]}]})
  ev('new Promise(r=>setTimeout(()=>r(true),1350))');data=json.loads(ev('JSON.stringify({events,samples,final:d.scrollTop,rect:d.getBoundingClientRect().toJSON(),clientHeight:d.clientHeight,scrollHeight:d.scrollHeight})'));data.update({'mode':mode,'scrollBeforeWheel':before});out['trials'].append(data);print(json.dumps({'mode':mode,'before':before,'final':data['final'],'events':data['events'],'trace':[(round(v['ms']),round(v['scroll'],2)) for v in data['samples']]},ensure_ascii=False),flush=True)
 out['completed']=True
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'native-wheel-control.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
