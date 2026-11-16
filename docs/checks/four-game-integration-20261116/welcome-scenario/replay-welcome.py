"""Prepared Developer UI proof; starts only with root's frozen-target/browser-slot grant.

Uses trusted pointer/keyboard actions for routes and dialogs. Production state,
receipts, missions and answers are never injected. Isolated headless Firefox.
"""
from pathlib import Path
import base64, datetime, hashlib, http.server, json, os, shutil, socket
import subprocess, tempfile, threading, time, traceback, urllib.request

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_FOUR_GAME_BROWSER_READY') == 'frozen', 'Root frozen target and browser slot required'
MANIFEST = Path(os.environ['NAMELECULE_FOUR_GAME_FROZEN_MANIFEST'])
FREEZE = json.loads(MANIFEST.read_text())
FROZEN = {p: (v if isinstance(v, str) else v.get('sha256', v.get('SHA256'))) for p, v in FREEZE['files'].items()}
def hashes(): return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(FROZEN)}
assert FROZEN and hashes() == FROZEN, 'Frozen target drift before browser'
DEST = HERE/('browser-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'))
DEST.mkdir(exist_ok=False)
OUT = {'role':'Developer browser execution; not independent review', 'checks':[], 'routes':[],
 'scope':'Welcome four game links, contain logos, 1500/1200/901/900/390 widths, tab order, dialogs, actual game readiness and return links',
 'sourceBefore':hashes(), 'manifest':str(MANIFEST), 'manifestSHA256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
 'harnessSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'limits':['Isolated headless Firefox with CSS viewport emulation; physical mobile/personal Firefox/conference/offline reliability unqualified.', 'Actual game answer replays belong to the parent integration suite.', 'JSmol j2s/fonts/remote services remain external dependencies.']}
server = firefox = log = profile = None

def check(ok, label, detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok: raise AssertionError((label,detail))
 print('PASS '+label, flush=True)
def read(expr): return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr, seconds=75):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if ev(expr): return
  time.sleep(.12)
 raise AssertionError('Timed out '+expr)
def page(path):
 call('browsingContext.navigate',{'context':ctx,'url':OUT['process']['baseURL']+path,'wait':'none'})
 wait('document.readyState!=="loading"');call('browsingContext.activate',{'context':ctx})
def shot(name, origin='viewport'):
 item=call('browsingContext.captureScreenshot',{'context':ctx,'origin':origin});(DEST/(name+'.png')).write_bytes(base64.b64decode(item['data']))
def viewport(width,height=1000):
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.25)
def press(value):
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'four-game-welcome-key','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]});time.sleep(.1)
def click(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');time.sleep(.15)
 q=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=Math.round(r.x+r.width/2),y=Math.round(r.y+r.height/2),h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()')
 check(q['hit'] and not q['disabled'] and 0<=q['x']<1500 and 0<=q['y']<1000,'trusted visible action '+selector,q)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'four-game-welcome-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':q['x'],'y':q['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});time.sleep(.15)

class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a): pass
 def send_error(self,code,message=None,explain=None):
  OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)

try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 with socket.socket() as probe: probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-four-game-welcome-',dir='/private/tmp'));log=(DEST/'firefox.log').open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--width','1800','--height','1400','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,MOZ_HEADLESS_WIDTH='1800',MOZ_HEADLESS_HEIGHT='1400'))
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serverPort':server.server_port,'baseURL':f'http://127.0.0.1:{server.server_port}/'};print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+30
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4): break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Owned BiDi endpoint unavailable')
   time.sleep(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['process']['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-four-game-welcome-bidi','exec'))
 check({p:hashlib.sha256(urllib.request.urlopen(OUT['process']['baseURL']+p).read()).hexdigest() for p in FROZEN}==FROZEN,'HTTP serves exact frozen target')
 page('design/welcome-proposal.html')
 for width in [1500,1200,901,900,390]:
  viewport(width,844 if width==390 else 1000)
  wait('[...document.querySelectorAll(".game-action img")].every(i=>i.complete&&i.naturalWidth>0)')
  state=read('''(()=>{const box=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};return{width:innerWidth,scrollWidth:document.documentElement.scrollWidth,columns:getComputedStyle(document.querySelector('.cards')).gridTemplateColumns,links:[...document.querySelectorAll('.game-action')].map(a=>{const i=a.querySelector('img'),l=a.querySelector('.game-action-label'),s=a.querySelector('.game-action-logo');return{text:l.textContent,link:box(a),label:box(l),slot:box(s),image:box(i),imageNatural:{width:i.naturalWidth,height:i.naturalHeight},contain:getComputedStyle(i).objectFit,labelFits:l.scrollWidth<=l.clientWidth+1,stacked:getComputedStyle(s).gridColumn}})}})()''')
  check(state['width']==width and state['scrollWidth']<=width,'welcome no horizontal overflow '+str(width),state)
  check(len(state['links'])==4 and all(l['contain']=='contain' and l['labelFits'] and l['slot']['width']>60 and l['slot']['height']>=50 and l['label']['right']<=l['link']['right'] and l['label']['bottom']<=l['link']['bottom']+1 for l in state['links']),'four readable contained logo/label slots '+str(width),state['links'])
  check(len(state['columns'].split())==(1 if width<=900 else 3),'expected card breakpoint '+str(width),state['columns'])
  ev('document.querySelector(".card.two").scrollIntoView({block:"start",behavior:"instant"});true');shot('welcome-'+str(width));OUT.setdefault('viewports',[]).append(state)
 # Inspect keyboard focus order from a cold welcome navigation at mobile width.
 page('design/welcome-proposal.html');wait('document.querySelectorAll(".game-action").length===4')
 focused=[]
 for _ in range(10):
  press('\ue004')
  f=read('({text:document.activeElement.textContent.trim(),className:document.activeElement.className,href:document.activeElement.getAttribute("href"),outline:getComputedStyle(document.activeElement).outlineStyle})')
  if 'game-action' in f['className']:focused.append(f)
  if len(focused)==4:break
 check([f['text'].replace('↗','').strip() for f in focused]==['Συνεργείο ονομάτων','Χτίσε το όνομα','Μοριακό παζλ','Μοριακός ντεντέκτιβ'] and all(f['outline']!='none' for f in focused),'four game links in keyboard order with visible focus',focused)
 press('\ue007');wait('location.pathname.endsWith("/games/molecular-detective.html")')
 wait('typeof NameleculeMolecularDetective!=="undefined"&&NameleculeMolecularDetective.snapshot().phase==="active"',100)
 check(read('NameleculeMolecularDetective.snapshot().phase')=='active','keyboard Enter opens ready Detective')
 click('.back-link');wait('location.pathname.endsWith("/design/welcome-proposal.html")')
 # Exercise both existing dialog contracts at desktop width.
 viewport(1200)
 for panel,title in [('login','Σύνδεση'),('teacher','Χώρος εκπαιδευτικού')]:
  selector='[data-panel="'+panel+'"]';click(selector);wait('document.getElementById("details").open')
  check(read('document.getElementById("dialog-title").textContent')==title,'existing '+panel+' dialog opens')
  if panel=='teacher':check(read('!document.getElementById("dialog-link").hidden&&document.getElementById("dialog-link").getAttribute("href")==="../mulermoc-nom-57.html"'),'teacher dialog app route preserved')
  press('\ue00c');wait('!document.getElementById("details").open')
  check(read('document.activeElement.getAttribute("data-panel")')==panel,'Escape restores '+panel+' focus')
 for index,(filename,ready,back) in enumerate([
  ('name-repair.html','document.getElementById("game-root")?.getAttribute("aria-busy")==="false"','.exit-link'),
  ('name-builder.html','document.getElementById("viewer-mask")?.hidden&&!!document.querySelector("#bank-tiles button")','.back-link'),
  ('molecular-puzzle.html','document.getElementById("assembly-board")?.getAttribute("aria-busy")==="false"&&document.querySelectorAll("#round-select option").length===14','.back-link'),
  ('molecular-detective.html','typeof NameleculeMolecularDetective!=="undefined"&&NameleculeMolecularDetective.snapshot().phase==="active"','.back-link')]):
  click('.game-action:nth-child('+str(index+1)+')');wait('location.pathname.endsWith('+json.dumps('/games/'+filename)+')')
  wait(ready,100);check(ev(ready),'welcome actual '+filename+' ready');shot('route-'+filename.removesuffix('.html'))
  OUT['routes'].append({'game':filename,'url':read('location.href'),'ready':True})
  click(back);wait('location.pathname.endsWith("/design/welcome-proposal.html")');check(ev('document.querySelectorAll(".game-action").length===4'),'actual return '+filename)
 check(not js_errors,'no captured JavaScript exceptions',js_errors)
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-8000)')};shot('failure')
 except Exception as capture:OUT['failureCaptureError']=repr(capture)
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[])
 OUT['diagnostics']=[e for e in globals().get('all_events',[]) if e.get('method')=='log.entryAdded']
 OUT['sourceAfter']=hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceAfter']==OUT['sourceBefore']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=10)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=10)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
 OUT['ownedServerClosed']=server is None or server.fileno()==-1
 if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith('namelecule-four-game-welcome-') and not profile.is_symlink():shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
 (DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'JSexceptions':len(OUT['javascriptErrors']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
