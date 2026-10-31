from pathlib import Path
import os,json,gzip,time,traceback
root=Path('/tmp/namelecule-jsmol-lifecycle-prototype-20261031');frames=root/'video-frames';frames.mkdir(exist_ok=True);os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8029/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1280,'height':800},'devicePixelRatio':1})
manifest=[];out={'completed':False};start=None;errorIndex=0

def grab():
 global errorIndex
 tree=call('browsingContext.getTree',{'root':ctx,'maxDepth':1})['contexts'][0];owners={c['context']:('candidate'if'version=candidate'in c['url']else'baseline') for c in tree.get('children',[]) or []}
 for e in js_errors[errorIndex:]:
  owner=owners.get(e.get('source',{}).get('context'))
  if owner:ev('browserMessage('+json.dumps(owner)+','+json.dumps(e['text'])+');true')
 errorIndex=len(js_errors)
 file=frames/('%04d.png'%len(manifest));stamp=time.monotonic()-start;screenshot(str(file));manifest.append({'path':str(file),'seconds':stamp})

def capture_for(seconds):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  before=time.monotonic();grab();time.sleep(max(0,.2-(time.monotonic()-before)))
try:
 navigate('video.html');until('readyFlags.baseline===true&&readyFlags.candidate===true',seconds=60);start=time.monotonic()
 for i,kind in enumerate(['raf','resize','entryAfterDestroy']):
  if i:
   ev('loadCase('+json.dumps(kind)+');true')
   deadline=time.monotonic()+45
   while not ev('readyFlags.baseline===true&&readyFlags.candidate===true'):
    if time.monotonic()>deadline:raise RuntimeError('video applet load timeout')
    capture_for(.4)
  capture_for(1.5);ev('startCase();true');capture_for(.7);ev('finishCase();true');capture_for(3)
  print('video case',kind,ev('JSON.stringify(caseResults[caseResults.length-1])'),flush=True)
 ev('document.getElementById("stage").textContent="Το πρωτότυπο απέτρεψε τα σφάλματα στις τρεις ελεγχόμενες δοκιμές.";true');capture_for(2)
 out['caseResults']=json.loads(ev('JSON.stringify(caseResults)'));assert all(r['counts']['baseline']>0 and r['counts']['candidate']==0 for r in out['caseResults'])
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['frames']=len(manifest);out['javascriptErrors']=js_errors;out['bidiEvents']=all_events;out['recordingMethod']='Actual sequential Firefox viewport PNG captures, monotonic timestamps; encoded without synthetic intermediate frames. Controlled teardown illustration, not Main production UI.'
 (root/'video-frames.json').write_text(json.dumps(manifest,indent=2)+'\n');(root/'video-evidence.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('video recorded',out['completed'],len(manifest),'frames',flush=True)
