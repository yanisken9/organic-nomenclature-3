"""Alternative-engine diagnostic; PREPARED until root's Chrome/browser grant.

Standard-library CDP transport; no dependency install or personal browser state.
Reuses the exact read-only oracles, DOM hit testing and genuine UI tests from
replay-detective.py through a narrow protocol adapter. Chrome results do not
qualify Firefox Continue or establish the Firefox failure's root cause.
"""
from pathlib import Path
import os
assert os.environ.get('NAMELECULE_FOUR_GAME_CHROME_READY') == 'frozen', 'Separate root Chrome/browser-slot grant required'
DRIVER = Path(__file__).with_name('replay-detective.py').read_text()
PREFIX = DRIVER.split('\ntry:\n server=',1)[0]
exec(compile(PREFIX,'four-game-recorded-ui-test-prefix','exec'))
import struct
from urllib.parse import urlparse

OUT['browserKind']='Google Chrome headless / direct CDP; Developer execution'
OUT['sharedDriverSHA256']=hashlib.sha256(DRIVER.encode()).hexdigest()
OUT['limits'] += ['This alternative-engine diagnostic cannot certify Firefox Continue or explain its RemoteAgent failure.']
OUT['scope'] += ' Alternative Chrome engine; final Continue remains trusted keyboard input.'
chrome=None
connections=[]
all_events=[]
js_errors=[]
preload=None

class CDP:
 def __init__(self,url):
  parsed=urlparse(url)
  assert parsed.scheme=='ws' and parsed.hostname=='127.0.0.1', 'Only owned loopback debugger allowed'
  self.sock=socket.create_connection(('127.0.0.1',parsed.port),timeout=30);self.sock.settimeout(30)
  self.deadline=min(RUN_DEADLINE,time.monotonic()+PROTOCOL_TIMEOUT)
  key=base64.b64encode(os.urandom(16)).decode()
  self.sock.sendall(('GET '+parsed.path+' HTTP/1.1\r\nHost: 127.0.0.1:'+str(parsed.port)+'\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
  header=b''
  while b'\r\n\r\n' not in header:
   self.sock.settimeout(check_deadline(self.deadline));header+=self.sock.recv(1)
  assert b'101' in header, ('Owned CDP WebSocket upgrade failed',header)
  self.seq=0;connections.append(self)
  self.deadline=RUN_DEADLINE
 def exact(self,count):
  result=b''
  while len(result)<count:
   self.sock.settimeout(check_deadline(self.deadline))
   chunk=self.sock.recv(count-len(result))
   if not chunk: raise RuntimeError('Owned CDP WebSocket closed')
   result+=chunk
  return result
 def send(self,payload,opcode=1):
  mask=os.urandom(4);count=len(payload)
  header=bytes([128|opcode,128|count]) if count<126 else bytes([128|opcode,254])+struct.pack('!H',count) if count<65536 else bytes([128|opcode,255])+struct.pack('!Q',count)
  self.sock.sendall(header+mask+bytes(value^mask[i%4] for i,value in enumerate(payload)))
 def receive(self):
  parts=[]
  while True:
   head=self.exact(2);length=head[1]&127;opcode=head[0]&15
   if length==126: length=struct.unpack('!H',self.exact(2))[0]
   elif length==127: length=struct.unpack('!Q',self.exact(8))[0]
   mask=self.exact(4) if head[1]&128 else None
   payload=self.exact(length)
   if mask: payload=bytes(value^mask[i%4] for i,value in enumerate(payload))
   if opcode==8: raise RuntimeError('Owned CDP sent WebSocket close')
   if opcode==9: self.send(payload,10);continue
   if opcode==10: continue
   if opcode not in [0,1]: raise RuntimeError('Unexpected owned CDP WebSocket opcode '+str(opcode))
   parts.append(payload)
   if head[0]&128: return json.loads(b''.join(parts))
 def call(self,method,params=None):
  self.deadline=min(RUN_DEADLINE,time.monotonic()+PROTOCOL_TIMEOUT)
  self.seq+=1;request=self.seq
  self.send(json.dumps({'id':request,'method':method,'params':params or {}}).encode())
  while True:
   check_deadline(self.deadline)
   message=self.receive()
   if message.get('method'):
    all_events.append(message)
    if message['method']=='Runtime.exceptionThrown': js_errors.append(message.get('params',{}))
   if message.get('id')==request:
    if message.get('error'): raise RuntimeError(message['error'])
    return message.get('result',{})

def configure_connection(connection):
 for method in ['Page.enable','Runtime.enable','Log.enable','Network.enable']: connection.call(method)
 if preload: connection.call('Page.addScriptToEvaluateOnNewDocument',{'source':preload})
 return connection
def connect_target(target_id=None):
 targets=json.loads(urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/json/list').read())
 target=next(item for item in targets if item.get('type')=='page' and (target_id is None or item['id']==target_id))
 return target['id'],configure_connection(CDP(target['webSocketDebuggerUrl']))
def cdp(method,params=None): return connection.call(method,params)
def ev(expression):
 result=cdp('Runtime.evaluate',{'expression':expression,'awaitPromise':True,'returnByValue':True,'userGesture':False})
 if result.get('exceptionDetails'): raise RuntimeError(result['exceptionDetails'])
 return result.get('result',{}).get('value')
def wait_document(url=None,old_loader=None):
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  tree=cdp('Page.getFrameTree')['frameTree']['frame']
  actual_url=tree['url']+tree.get('urlFragment','')
  if (old_loader is None or tree.get('loaderId')!=old_loader) and (url is None or actual_url==url):
   try:
    if ev('document.readyState!=="loading"'): return
   except RuntimeError: pass
  time.sleep(.1)
 raise AssertionError('Owned Chrome document navigation did not complete')
def call(method,params):
 global connection,ctx,preload
 if method=='browsingContext.navigate':
  result=cdp('Page.navigate',{'url':params['url']});wait_document(params['url']);return result
 if method=='browsingContext.reload':
  old=cdp('Page.getFrameTree')['frameTree']['frame'].get('loaderId');result=cdp('Page.reload',{'ignoreCache':False});wait_document(old_loader=old);return result
 if method=='browsingContext.activate': return cdp('Page.bringToFront')
 if method=='browsingContext.setViewport':
  viewport=params['viewport'];return cdp('Emulation.setDeviceMetricsOverride',{'width':viewport['width'],'height':viewport['height'],'deviceScaleFactor':1,'mobile':False})
 if method=='browsingContext.captureScreenshot': return cdp('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})
 if method=='browsingContext.create':
  target=cdp('Target.createTarget',{'url':'about:blank'})['targetId'];new_id,new_connection=connect_target(target);connection=new_connection;return {'context':new_id}
 if method=='browsingContext.close': return cdp('Target.closeTarget',{'targetId':params['context']})
 if method=='session.subscribe': return {}
 if method=='script.addPreloadScript':
  preload='('+params['functionDeclaration']+')();';return cdp('Page.addScriptToEvaluateOnNewDocument',{'source':preload})
 if method=='input.performActions':
  for source in params['actions']:
   point={'x':0,'y':0}
   for action in source['actions']:
    if source['type']=='pointer':
     if action['type']=='pointerMove':
      point={'x':action['x'],'y':action['y']};cdp('Input.dispatchMouseEvent',{'type':'mouseMoved',**point,'button':'none','buttons':0})
     elif action['type']=='pointerDown': cdp('Input.dispatchMouseEvent',{'type':'mousePressed',**point,'button':'left','buttons':1,'clickCount':1})
     elif action['type']=='pointerUp': cdp('Input.dispatchMouseEvent',{'type':'mouseReleased',**point,'button':'left','buttons':0,'clickCount':1})
     else: raise RuntimeError('Unsupported trusted CDP pointer action')
    elif source['type']=='key':
     assert action['value']=='\ue007', 'Only required trusted Enter is mapped'
     value={'type':'keyDown' if action['type']=='keyDown' else 'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13,'nativeVirtualKeyCode':13}
     if action['type']=='keyDown': value['text']='\r'
     cdp('Input.dispatchKeyEvent',value)
    else: raise RuntimeError('Unsupported trusted CDP input source')
  return {}
 raise RuntimeError('Unmapped bounded protocol method '+method)

try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 profile=Path(tempfile.mkdtemp(prefix='namelecule-four-game-chrome-',dir='/private/tmp'));log=(DEST/'chrome.log').open('w')
 executable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
 chrome=subprocess.Popen([executable,'--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1800,1400','about:blank'],stdout=log,stderr=subprocess.STDOUT)
 deadline=time.monotonic()+40
 while not (profile/'DevToolsActivePort').is_file():
  if chrome.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Owned Chrome debugger startup failed')
  time.sleep(.1)
 port=int((profile/'DevToolsActivePort').read_text().splitlines()[0])
 ctx,connection=connect_target()
 OUT['process']={'ownedPID':chrome.pid,'profile':str(profile),'cdpPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 OUT['browserVersion']=json.loads(urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/json/version').read())
 call('script.addPreloadScript',{'functionDeclaration':'''()=>{window.__lessonMessages=[];addEventListener('message',e=>{if(e.origin!==location.origin)return;const d=e.data;if(d?.channel==='namelecule-builder-lesson-v1'&&d.command==='load')window.__lessonLoad=d;if(d?.channel==='namelecule-puzzle-lesson-v1'&&d.command==='load')window.__puzzleLoad=d;if(d?.channel==='namelecule-detective-lesson-v1')window.__lessonMessages.push(d);});}'''})
 OUT['servedSHA256']={p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in sorted(SOURCES)}
 check(OUT['servedSHA256']==OUT['sourceBefore'],'Chrome HTTP exact frozen/application bytes')
 if MODE.startswith('old3-'):
  for item in ['js/namelecule-game-choice-checkpoint.js','scenarios/alkanes-user-3.scenario.json']:
   check(hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+'__prior__/'+item).read()).hexdigest()==sha(PRIOR/item),'Chrome prior alias exact '+item)
 viewport(1500,1000);OUT['inputSurface']=read('({innerWidth,innerHeight,outerWidth,outerHeight})')
 check(OUT['inputSurface']['outerWidth']>=1500 and OUT['inputSurface']['outerHeight']>=1000,'owned Chrome physical surface covers CSS1500x1000',OUT['inputSurface'])
 if MODE.startswith('detective'): detective_replay(MODE=='detective-required')
 else: legacy_replay()
 check(not js_errors,'Chrome no captured runtime JavaScript exceptions',js_errors);OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try: OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-10000)'),'record':rec(),'messages':read('window.__lessonMessages??null')};shot('failure')
 except Exception as capture: OUT['failureCaptureError']=repr(capture)
finally:
 OUT['javascriptErrors']=js_errors;OUT['cdpEvents']=all_events
 OUT['networkErrors']=[event for event in all_events if event.get('method')=='Network.loadingFailed']
 OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 for item in connections:
  try: item.sock.close()
  except OSError: pass
 if chrome is not None and chrome.poll() is None:
  chrome.terminate()
  try: chrome.wait(timeout=10)
  except subprocess.TimeoutExpired: chrome.kill();chrome.wait(timeout=10)
 if server: server.shutdown();server.server_close()
 if log: log.close()
 OUT['ownedBrowserExited']=chrome is None or chrome.poll() is not None;OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith('namelecule-four-game-chrome-') and not profile.is_symlink(): shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
 OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'chrome-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'engine':'Chrome','mode':MODE,'checks':len(OUT['checks']),'correctUIAttempts':len(OUT['correctUIAttempts']),'JSexceptions':len(js_errors),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'): raise SystemExit(1)
