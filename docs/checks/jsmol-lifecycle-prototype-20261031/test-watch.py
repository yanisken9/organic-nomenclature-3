from pathlib import Path
import json,os,time,traceback
root=Path('/tmp/namelecule-jsmol-lifecycle-prototype-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8029/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
out={'completed':False}
try:
 navigate('app-baseline/docs/checks/jsmol-lifecycle-prototype-20261031/watch.html')
 until("document.querySelector('video').readyState>=2",seconds=30)
 out['metadata']=json.loads(ev("JSON.stringify((()=>{let v=document.querySelector('video');return {width:v.videoWidth,height:v.videoHeight,duration:v.duration,source:v.currentSrc}})())"))
 ev("(()=>{let v=document.querySelector('video');v.muted=true;return v.play().then(()=>true)})()")
 time.sleep(1);assert ev("document.querySelector('video').currentTime>0.5")
 ev("document.querySelector('video').pause();true");out['seeks']=[]
 for t in [4,12,20]:
  ev("new Promise(resolve=>{let v=document.querySelector('video');v.addEventListener('seeked',()=>resolve(true),{once:true});v.currentTime="+str(t)+"})")
  out['seeks'].append(ev("document.querySelector('video').currentTime"))
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'])
finally:
 out['javascriptErrors']=js_errors;(root/'watch-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{});print(out,flush=True)
