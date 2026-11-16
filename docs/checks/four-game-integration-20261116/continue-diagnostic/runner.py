"""One granted Firefox replay ending at the original gate4 Continue boundary.

Application source remains frozen. Reuses genuine UI solver helpers. Only the
final boundary is observed with DOM listeners/MutationObserver/200ms telemetry
to an owned loopback HTTP thread, so a failed BiDi actor cannot hide its outcome.
No application functions, state, receipts, responses or security settings change.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import ast, base64, datetime, hashlib, http.server, json, os, platform, shutil, socket
import subprocess, tempfile, threading, time, traceback, urllib.request

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent.parent/'lesson-browser'
DEST = Path(__file__).resolve().parent/('run-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'))
assert os.environ.get('NAMELECULE_FOUR_GAME_CONTINUE_DIAGNOSTIC') == 'granted', 'Explicit root one-browser-slot grant required'
MANIFEST = Path(os.environ['NAMELECULE_FOUR_GAME_FROZEN_MANIFEST'])
FREEZE = json.loads(MANIFEST.read_text())
FROZEN = {p:(v if isinstance(v,str) else v.get('sha256',v.get('SHA256'))) for p,v in FREEZE['files'].items()}
MODE = 'detective-required'
GAME = 'detective'
PRIOR = HERE.parent/'before'
helper = HERE/'replay-detective.py'
tree = ast.parse(helper.read_text())
# Compile the original helpers without running their browser startup or replay.
names = {'sha','hashes','check','read','pause','wait','page','shot','viewport','pointer','clickel','click','activate_button',
 'frame_read','frame_click','ready','rec','game_state','lesson','open_gate','game_ready','choose','footer','reload_gate',
 'ds','oracle','detective_pick','dsolve','triple'}
selected = [node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
assert {node.name for node in selected} == names
exec(compile(ast.Module(body=selected,type_ignores=[]),str(helper),'exec'))
sources_node = next(node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCES' for t in node.targets))
exec(compile(ast.Module(body=[sources_node],type_ignores=[]),str(helper),'exec'))
assert FROZEN and all(sha(ROOT/p)==v for p,v in FROZEN.items()), 'Frozen target drift'
assert sha(MANIFEST)=='908093208d0ca410c702650b51fc629fae7142d0d2afef50a74fe00a703f2c9c', 'Unexpected review target'
DEST.mkdir(exist_ok=False)
OUT = {'role':'Developer bounded diagnostic, not independent review','mode':'continue-boundary-DOM-telemetry',
 'checks':[],'correctUIAttempts':[],'sourceBefore':hashes(),'manifest':str(MANIFEST),'manifestSHA256':sha(MANIFEST),
 'harnessSHA256':sha(Path(__file__)),'originalHelperSHA256':sha(helper),
 'scope':'One actual required Detective gate4 triple, earned cold reload, keyboard Continue boundary; stop without gate11 or old3 replay.',
 'observationContract':'Read-only DOM snapshots/events/MutationObserver and bounded200ms timer. Localhost POST independent of BiDi. No application wrapper/state/receipt or browser security changes.',
 'runtime':{'platform':platform.platform(),'machine':platform.machine(),'python':platform.python_version()},
 'limits':['Headless isolated Firefox only; external JSmol/fonts/services retained.',
 'Telemetry can establish visible DOM changes or continued event-loop liveness; absence alone cannot establish application deadlock versus renderer/process loss.',
 'No stronger claim about full presentation reliability, gate11 or archived migration.']}
MOLS = {m['id']:m['mol'] for m in json.loads((ROOT/'games/data/alkane-structures.json').read_text())['molecules']}
server = firefox = log = profile = None
trace = []
trace_lock = threading.Lock()
trace_phase = 'before-observer'
TRACE = DEST/'trace.jsonl'

OBSERVE = r'''(()=>{
  const run=RUN_ID, endpoint='/__trace__', deadline=performance.now()+50000;
  let seq=0, ticks=0, mutationTimer=0, stopped=false;
  const listeners=[];
  function text(selector,n=120){const e=document.querySelector(selector);return e?String(e.innerText||e.textContent||'').replace(/\s+/g,' ').trim().slice(0,n):null;}
  function target(e){const t=e?.target;return t?{tag:t.tagName||null,id:t.id||null,text:String(t.innerText||t.textContent||'').trim().slice(0,80),connected:!!t.isConnected}:null;}
  function report(reason,extra={}){
    if(stopped)return;
    const d=document.querySelector('#nlQuizDialog'), active=document.activeElement;
    const value={run,seq:++seq,reason,utc:new Date().toISOString(),performance:performance.now(),
      counter:text('#scPos'),pageTitle:text('#pageTitle',180),documentTitle:document.title,
      dialogOpen:!!d?.open,dialogConnected:!!d?.isConnected,iframeCount:document.querySelectorAll('iframe').length,
      lessonText:text('#scStepText'),quizProgress:text('#nlQuizProgress'),
      active:{tag:active?.tagName||null,id:active?.id||null,text:String(active?.innerText||'').slice(0,80)},
      nextDisabled:document.querySelector('#scNext')?.disabled??null,visibility:document.visibilityState,...extra};
    const body=JSON.stringify(value);
    if(!navigator.sendBeacon(endpoint,new Blob([body],{type:'application/json'})))fetch(endpoint,{method:'POST',body,headers:{'Content-Type':'application/json'},keepalive:true}).catch(()=>{});
  }
  for(const type of ['keydown','keyup','pointerdown','pointerup','click']){
    for(const capture of [true,false]){
      const handler=e=>{const extra={eventType:type,eventKey:e.key||null,eventButton:e.button??null,trusted:e.isTrusted,defaultPrevented:e.defaultPrevented,target:target(e),capture};
        report(capture?'event-before':'event-after',extra);
        queueMicrotask(()=>report(capture?'before-microtask':'after-microtask',extra));
        requestAnimationFrame(()=>report(capture?'before-rAF':'after-rAF',extra));};
      window.addEventListener(type,handler,{capture,passive:true});listeners.push([type,handler,capture]);
    }
  }
  const observer=new MutationObserver(records=>{
    if(stopped||mutationTimer)return;
    const count=records.length;
    mutationTimer=setTimeout(()=>{mutationTimer=0;report('mutation',{mutationCount:count});},35);
  });
  observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['open','disabled','hidden','class']});
  const interval=setInterval(()=>{
    report('interval',{tick:++ticks});
    if(ticks>=250||performance.now()>=deadline){report('observer-ended');stopped=true;clearInterval(interval);clearTimeout(mutationTimer);observer.disconnect();listeners.forEach(([type,fn,capture])=>window.removeEventListener(type,fn,capture));}
  },200);
  report('observer-installed');return true;
})()'''

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a): pass
 def do_POST(self):
  if urlsplit(self.path).path!='/__trace__': self.send_error(404);return
  size=int(self.headers.get('Content-Length','0'))
  if size<=0 or size>65536:self.send_error(413);return
  try:value=json.loads(self.rfile.read(size))
  except Exception:self.send_error(400);return
  record={'receivedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receivedMonotonic':time.monotonic(),'serverPhase':trace_phase,'browser':value}
  with trace_lock:
   trace.append(record)
   with TRACE.open('a') as stream:stream.write(json.dumps(record,ensure_ascii=False)+'\n');stream.flush()
  self.send_response(204);self.send_header('Content-Length','0');self.end_headers()
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)

def owned_process_snapshot():
 if firefox is None:return []
 text=subprocess.check_output(['ps','-axo','pid=,ppid=,stat=,etime=,comm='],text=True)
 rows=[]
 for line in text.splitlines():
  fields=line.strip().split(None,4)
  if len(fields)==5:rows.append({'pid':int(fields[0]),'ppid':int(fields[1]),'state':fields[2],'elapsed':fields[3],'command':fields[4]})
 own={firefox.pid};changed=True
 while changed:
  added={r['pid'] for r in rows if r['ppid'] in own}-own;changed=bool(added);own|=added
 return [r for r in rows if r['pid'] in own]

try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-four-game-continue-',dir='/private/tmp'));log=(DEST/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned BiDi endpoint unavailable')
   pause(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-continue-diagnostic-bidi','exec'))
 call('session.subscribe',{'events':['network.beforeRequestSent','network.responseCompleted','network.fetchError'],'contexts':[ctx]})
 OUT['servedSHA256']={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in sorted(SOURCES)}
 check(OUT['servedSHA256']==OUT['sourceBefore'],'HTTP exact frozen/application bytes')
 viewport(1500,1000)
 lesson();OUT['replayIndices']=[0]
 for index in range(1,4):pause(.9);click('#scNext');wait('fScenarioPresent().index==='+str(index));OUT['replayIndices'].append(index)
 check(ev('document.getElementById("scNext").disabled'),'cold gate4 locked')
 open_gate();choose();OUT['gate4IDs']=triple(3,partial=False);earned=rec()['states']['3']['earned'];shot('gate4-earned')
 reload_gate();check(rec()['states']['3']['earned']==earned and rec()['states']['3']['solved'],'earned gate4 exact revalidated reload');footer('restored gate4',True)
 OUT['preBoundaryDOM']=read('({counter:document.getElementById("scPos")?.innerText,pageTitle:document.getElementById("pageTitle")?.innerText,dialogOpen:document.getElementById("nlQuizDialog")?.open,iframeCount:document.querySelectorAll("iframe").length,lessonText:document.getElementById("scStepText")?.innerText?.slice(0,120)})')
 OUT['ownedProcessesBeforeBoundary']=owned_process_snapshot()
 trace_phase='observing-before-activation'
 check(ev(OBSERVE.replace('RUN_ID',json.dumps(DEST.name))) is True,'read-only boundary observer installed')
 pause(.65)
 with trace_lock:probe_count=len(trace)
 check(probe_count>=2,'independent loopback telemetry receives before activation',probe_count)
 trace_phase='activation-pending';OUT['activationStartedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  activate_button('.round-next button:first-child')
  OUT['inputCommandReturned']=True
 except Exception:
  OUT['inputCommandReturned']=False;OUT['inputCommandFailure']=traceback.format_exc();print(OUT['inputCommandFailure'],flush=True)
 # Deliberately no script.evaluate/captureScreenshot or further BiDi call here.
 # The server thread and OS process table are independent of the failing actor.
 trace_phase='after-input-return-or-timeout';OUT['inputFinishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 OUT['ownedProcessesAfterInput']=owned_process_snapshot()
 for _ in range(20):
  pause(.25)
  if firefox.poll() is not None:break
 with trace_lock:copied=list(trace)
 OUT['traceSummary']={'count':len(copied),'first':copied[:2],'last':copied[-8:],
  'eventReasons':[r['browser'] for r in copied if r['browser'].get('eventType')],
  'counters':list(dict.fromkeys(str(r['browser'].get('counter')) for r in copied)),
  'titles':list(dict.fromkeys(str(r['browser'].get('pageTitle')) for r in copied)),
  'step5DOMObserved':any(str(r['browser'].get('counter','')).replace(' ','')=='5/12' and r['browser'].get('dialogOpen') is False and r['browser'].get('iframeCount')==0 for r in copied),
  'postInputSamples':sum(r['serverPhase']=='after-input-return-or-timeout' for r in copied),
  'lastReceivedAgeSeconds':time.monotonic()-copied[-1]['receivedMonotonic'] if copied else None}
 OUT['firefoxExitBeforeCleanup']=firefox.poll();OUT['ownedProcessesAfterObservation']=owned_process_snapshot()
 OUT['diagnosticBoundaryReached']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[])
 OUT['networkErrors']=[e for e in globals().get('all_events',[]) if e.get('method')=='network.fetchError']
 OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=10)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=10)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None;OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith('namelecule-four-game-continue-') and not profile.is_symlink():shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
 OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'boundaryReached':OUT.get('diagnosticBoundaryReached',False),'inputReturned':OUT.get('inputCommandReturned'),'checks':len(OUT['checks']),'correctUIAttempts':len(OUT['correctUIAttempts']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'step5DOMObserved':OUT.get('traceSummary',{}).get('step5DOMObserved'),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('diagnosticBoundaryReached'):raise SystemExit(1)
