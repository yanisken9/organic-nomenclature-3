"""Developer evidence, using only the explicitly owned headless Firefox."""
from pathlib import Path
import os,json,time,base64,traceback,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PROCESS=json.loads((HERE/'process.json').read_text())
STAGE=sys.argv[1] if len(sys.argv)>1 else 'local'
if STAGE=='live':PROCESS['baseURL']='https://yanisken9.github.io/organic-nomenclature-3/'
os.environ['NAMELECULE_BIDI_PORT']=str(PROCESS['bidiPort'])
os.environ['NAMELECULE_TEST_BASE_URL']=PROCESS['baseURL']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'), 'owned-name-builder-bidi', 'exec'))
call('script.addPreloadScript',{'contexts':[ctx], 'functionDeclaration':'''() => {
 window.__builderEvents=[];
 addEventListener('message',event=>{if(event.data?.channel==='namelecule-name-builder-v1')window.__builderEvents.push(event.data);});
}'''})
def read(expression):
 return json.loads(ev('JSON.stringify('+expression+')'))
def wait(expression,seconds=45):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if ev(expression):return
  time.sleep(.15)
 raise AssertionError('Timed out: '+expression)
def open_page(path):
 call('browsingContext.navigate',{'context':ctx,'url':PROCESS['baseURL']+path,'wait':'none'})
def shot(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'})
 (HERE/name).write_bytes(base64.b64decode(r['data']))
def click(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true')
 time.sleep(.1)
 point=read('(()=>{let n=document.querySelector('+json.dumps(selector)+'),r=n.getBoundingClientRect();return{x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),disabled:!!n.disabled}})()')
 assert not point['disabled'],(selector,point)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'builder-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
 time.sleep(.1)
def finish():
 try:call('browsingContext.close',{'context':ctx})
 finally:
  try:call('session.end',{})
  finally:s.close()
