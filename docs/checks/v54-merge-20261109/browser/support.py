"""Developer evidence helper. Uses only owned isolated Firefox BiDi process."""
from pathlib import Path
import os,json,time,traceback,base64,hashlib,re
HERE=Path(__file__).resolve().parent
if HERE.name!='browser':HERE=Path('docs/checks/v54-merge-20261109/browser').resolve()
ROOT=Path.cwd();proc=json.loads((HERE/'process.json').read_text());CR=Path(proc['candidateRoot'])
os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=proc['base_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned55-bidi','exec'))
PLAN=json.loads((HERE.parent/'plan.json').read_text());FROZEN=json.loads((HERE.parent/'verification-target.json').read_text());SOURCE_PATHS=list(FROZEN['files']);START_HASHES={p:hashlib.sha256((CR/p).read_bytes()).hexdigest() for p in SOURCE_PATHS};assert START_HASHES==FROZEN['files'],'Frozen17 source mismatch before runtime'
if Path(__file__).name!='test-shell-lessons.py':call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }','contexts':[ctx]})
out={'sourceHashesAtStart':START_HASHES,'completed':False,'role':'Developer real isolated Firefox evidence; not independent review','checks':[],'limitations':['Headless Firefox and viewport emulation only; no personal Firefox interaction','Real external JSmol/fonts/oracle service failures are retained; controlled transports are explicitly labeled','No physical mobile/Safari/conference-machine/offline or uninterrupted-operation guarantee'],'base_url':proc['base_url']}
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr,sec=30):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  if ev(expr):return
  time.sleep(.1)
 raise AssertionError('Timeout '+expr)
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def pause(ms=200):ev('new Promise(r=>setTimeout(()=>r(true),'+str(ms)+'))')
def pointer_at(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'owned55-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def pointer(selector):
 for _ in range(10):
  ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
  p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()')
  if p['hit']:break
 assert p['hit'] and not p['disabled'],(selector,p);pointer_at(p)
def click(selector,touch=False):pointer(selector)
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'owned55-key','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
def visible(selector):return ev('(()=>{const n=document.querySelector('+json.dumps(selector)+'),r=n?.getBoundingClientRect();return !!r&&r.width>0&&r.height>0&&getComputedStyle(n).visibility!=="hidden"})()')
def shot(name):
 r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(name+'.png')).write_bytes(base64.b64decode(r['data']))
def screenshot_here(name):shot(Path(name).stem)
def finish(name):
 out['sourceHashesAtFinish']={p:hashlib.sha256((CR/p).read_bytes()).hexdigest() for p in SOURCE_PATHS};out['sourceChangedDuringRun']=[p for p in SOURCE_PATHS if out['sourceHashesAtFinish'][p]!=START_HASHES[p]];out['frozenTargetMatchesAtFinish']=out['sourceHashesAtFinish']==FROZEN['files']
 if not out['frozenTargetMatchesAtFinish']:out['completed']=False;out['failure']='Frozen17 source drift at finish'
 out['javascriptErrors']=js_errors;out['diagnosticEntries']=[e['params'] for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')in['error','warn']]
 try:out['resources']=read('performance.getEntriesByType("resource").map(r=>({name:r.name,initiatorType:r.initiatorType,duration:r.duration,responseStatus:r.responseStatus}))')
 except Exception:pass
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 (HERE/(name+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
