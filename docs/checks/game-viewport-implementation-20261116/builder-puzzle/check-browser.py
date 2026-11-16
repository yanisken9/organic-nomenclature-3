"""Developer isolated Chrome geometry and production-input checks; no progress setters."""
from pathlib import Path
from urllib.parse import urlparse, urlsplit, unquote
import ast, base64, datetime, hashlib, http.server, json, os, shutil, socket, struct, subprocess, tempfile, threading, time, traceback, urllib.request
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_VIEWPORT_BROWSER_GRANT')=='builder-puzzle', 'Exclusive root browser grant required'
RUN_DEADLINE=time.monotonic()+540;PROTOCOL_TIMEOUT=25
connections=[];all_events=[];js_errors=[];preload=None
OUT={'role':'Developer isolated headless Chrome; not independent review','checks':[],'measurements':[],'limitations':['CSS viewport emulation; physical device/browser zoom not certified.','Native viewer/chemistry assets use actual sources; external fonts/JSmol may depend on network.']}
paths=['games/name-builder.html','games/molecular-puzzle.html','js/namelecule-name-builder.js','js/namelecule-molecular-puzzle.js','css/namelecule-name-builder.css','css/namelecule-molecular-puzzle.css','js/namelecule-game-viewport.js','css/namelecule-game-viewport.css','js/namelecule-game-levels.js','css/namelecule-game-levels.css']
OUT['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
def check_deadline(deadline=None):
 left=min(RUN_DEADLINE,deadline or RUN_DEADLINE)-time.monotonic()
 if left<=0:raise TimeoutError('Bounded browser deadline exceeded')
 return left
def load_defs(file,names):
 tree=ast.parse(file.read_text());selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
 assert {n.name for n in selected}==names
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(file),'exec'),globals())
load_defs(ROOT/'docs/checks/four-game-integration-20261116/lesson-browser/replay-chrome.py',{'CDP','configure_connection','connect_target','cdp','ev','wait_document'})
def wait(expr,seconds=100):
 end=min(RUN_DEADLINE,time.monotonic()+seconds)
 while time.monotonic()<end:
  try:
   if ev(expr):return
  except RuntimeError:pass
  time.sleep(.15)
 raise AssertionError(('Wait failed',expr))
def check(label,value,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(value),'detail':detail})
 if not value:raise AssertionError((label,detail))
def click(selector):
 point=ev('''(()=>{const e=document.querySelector(SELECTOR);if(!e)throw Error('Missing '+SELECTOR);const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return{x,y,hit:r.width>0&&r.height>0&&e.contains(document.elementFromPoint(x,y)),disabled:!!e.disabled}})()'''.replace('SELECTOR',json.dumps(selector)))
 check('Visible production control '+selector,point['hit'] and not point['disabled'],point)
 for kind,buttons in [('mouseMoved',0),('mousePressed',1),('mouseReleased',0)]:cdp('Input.dispatchMouseEvent',{'type':kind,'x':point['x'],'y':point['y'],'button':'none' if kind=='mouseMoved' else 'left','buttons':buttons,'clickCount':1})
 time.sleep(.15)
def key(key,code,virtual):
 for kind in ['keyDown','keyUp']:cdp('Input.dispatchKeyEvent',{'type':kind,'key':key,'code':code,'windowsVirtualKeyCode':virtual,'nativeVirtualKeyCode':virtual})
 time.sleep(.15)
def visible(selector):
 return ev('''(()=>{const e=document.querySelector(SELECTOR);if(!e)return false;const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return r.width>0&&r.height>0&&x>=0&&y>=0&&x<innerWidth&&y<innerHeight&&e.contains(document.elementFromPoint(x,y))})()'''.replace('SELECTOR',json.dumps(selector)))
def paged_click(selector,pager_selector):
 for _ in range(40):
  if visible(selector):click(selector);return
  next_selector=pager_selector+' .nl-vp-pager-nav button:last-child'
  if not visible(next_selector) or ev('document.querySelector('+json.dumps(next_selector)+').disabled'):
   previous=pager_selector+' .nl-vp-pager-nav button:first-child'
   while visible(previous) and not ev('document.querySelector('+json.dumps(previous)+').disabled'):click(previous)
   if visible(selector):click(selector);return
   if not visible(next_selector) or ev('document.querySelector('+json.dumps(next_selector)+').disabled'):break
  click(next_selector)
 raise AssertionError(('Explicit pager cannot reach',selector))
def drag_outside(selector):
 point=ev('(()=>{const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}})()')
 cdp('Input.dispatchMouseEvent',{'type':'mousePressed',**point,'button':'left','buttons':1,'clickCount':1})
 for x,y in [(point['x']+12,point['y']),(point['x'],point['y']-70),(20,60)]:cdp('Input.dispatchMouseEvent',{'type':'mouseMoved','x':x,'y':y,'button':'left','buttons':1});time.sleep(.1)
 cdp('Input.dispatchMouseEvent',{'type':'mouseReleased','x':20,'y':60,'button':'left','buttons':0,'clickCount':1});time.sleep(.7)
def view(w,h):cdp('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False});time.sleep(.3)
def page(path):
 url=f'http://127.0.0.1:{server.server_port}/'+path
 cdp('Page.navigate',{'url':url});wait('document.readyState!=="loading"');time.sleep(.4)
def ready(game):
 wait('document.querySelectorAll("[data-level]").length===3',120)
 if game=='builder':wait('document.getElementById("viewer-mask").hidden&&!!document.querySelector("#bank-tiles button")',120)
 else:wait('document.getElementById("assembly-board").getAttribute("aria-busy")==="false"',120)
def measure(game,tag):
 result=ev('''(()=>{const selectors=GAME==='builder'?['.objective','.builder-view-nav','.workspace','.molecule-panel','.answer-panel','#answer-zone','#bank-zone','#tile-controls','#check-answer','#candidate-name','#answer-help','#feedback']:['.objective','.puzzle-view-nav','.puzzle-name-card','#target-name','.puzzle-assembly-panel','.puzzle-board-port','#assembly-board','#piece-bank','.puzzle-tools','.puzzle-selection-controls','#check-answer','#instructions','#feedback'];return{viewport:{width:innerWidth,height:innerHeight},root:{scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,scrollX,scrollY},view:document.getElementById('game').dataset,items:Object.fromEntries(selectors.map(s=>{const e=document.querySelector(s),r=e?.getBoundingClientRect(),c=e?getComputedStyle(e):null;return[s,e?{x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right,display:c.display,visible:r.width>0&&r.height>0,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,font:c.fontSize,whiteSpace:c.whiteSpace}:null]})),pagers:[...document.querySelectorAll('.nl-vp-pager')].map(e=>({overflow:e.classList.contains('is-overflow'),label:e.querySelector('nav')?.getAttribute('aria-label'),rect:e.getBoundingClientRect().toJSON(),content:e.firstElementChild.id||e.firstElementChild.className,text:e.querySelector('nav')?.textContent}))}})()'''.replace('GAME',json.dumps(game)))
 result.update(game=game,tag=tag);OUT['measurements'].append(result);return result
def screenshot(name):
 (DEST/(name+'.png')).write_bytes(base64.b64decode(cdp('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
 def translate_path(self,path):
  target=unquote(urlsplit(path).path)
  if target.startswith('/__before__/'):
   rel=Path(target[len('/__before__/'):]);assert not rel.is_absolute() and '..' not in rel.parts
   old=HERE.parent/'before'/rel
   return str(old if old.is_file() else ROOT/rel)
  return super().translate_path(path)
DEST=HERE/('browser-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'));DEST.mkdir()
browser=server=profile=log=None
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 profile=Path(tempfile.mkdtemp(prefix='namelecule-vp-builder-puzzle-',dir='/private/tmp'));log=(DEST/'chrome.log').open('w')
 browser=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1500,1000','about:blank'],stdout=log,stderr=subprocess.STDOUT)
 end=time.monotonic()+35
 while not (profile/'DevToolsActivePort').is_file():
  if browser.poll() is not None or time.monotonic()>end:raise RuntimeError('Owned Chrome failed startup')
  time.sleep(.1)
 port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);ctx,connection=connect_target()
 OUT['process']={'pid':browser.pid,'profile':str(profile),'serverPort':server.server_port,'debugPort':port};print(json.dumps(OUT['process']),flush=True)
 for game,file in [('builder','name-builder'),('puzzle','molecular-puzzle')]:
  view(1024,640);page('__before__/games/'+file+'.html');wait('document.querySelectorAll("[data-level]").length===3',120);click('[data-level="3"]');ready(game)
  baseline=measure(game,'exact22-before-1024x640');screenshot(game+'-before-1024')
  check(game+' before reproduces vertical content beyond viewport',baseline['root']['scrollHeight']>640,baseline['root'])
  page('games/'+file+'.html');wait('document.querySelectorAll("[data-level]").length===3',120);click('[data-level="3"]');ready(game)
  for w,h in [(1024,640),(1280,720),(1440,900),(390,700)]:
   view(w,h)
   nav='.builder-view-nav' if game=='builder' else '.puzzle-view-nav'
   for stage in (['editing','bank','molecule','name','help'] if game=='builder' else ['editing','pieces','tools','name','help']):
    selector=nav+' button[data-view="'+stage+'"]'
    if not ev('(()=>{const e=document.querySelector('+json.dumps(selector)+');return e&&e.getBoundingClientRect().width>0})()'):continue
    click(selector);m=measure(game,f'{w}x{h}-{stage}')
    check(game+' document fits '+str((w,h,stage)),m['root']['scrollWidth']<=w and m['root']['scrollHeight']<=h+1,m['root'])
    for s in (['.objective',nav] + (['#check-answer'] if stage=='editing' else [])):
     item=m['items'][s]
     check(game+' visible required '+s+' '+str((w,h,stage)),item['visible'] and item['y']>=-1 and item['bottom']<=h+1,item)
    if stage in ['editing','help']:screenshot(game+'-'+str(w)+'-'+stage)
  view(390,700)
  if game=='builder':
   click('.builder-view-nav button[data-view="bank"]');click('#bank-tiles button');click('.builder-view-nav button[data-view="editing"]');click('#check-answer')
  else:
   click('.puzzle-view-nav button[data-view="pieces"]');click('[data-hydrogens="4"]');click('.puzzle-view-nav button[data-view="editing"]');click('#check-answer')
  wait('document.getElementById("game").dataset.'+('builderView' if game=='builder' else 'puzzleView')+'==="feedback"')
  m=measure(game,'390x700-wrong-feedback');screenshot(game+'-wrong-feedback')
  click(('.builder-feedback-actions' if game=='builder' else '.puzzle-feedback-actions')+' .secondary:first-child')
  check(game+' wrong feedback return preserves raw tile/node',ev('document.querySelectorAll('+json.dumps('#answer-tiles>li' if game=='builder' else '#board-nodes>button')+').length===1'))
  if game=='builder':
   # The same raw tile is removable using both pointer release and keyboard.
   drag_outside('#answer-tiles button')
   check('Builder release outside answer returns tile to bank',ev('document.querySelectorAll("#answer-tiles>li").length===0'))
   click('.builder-view-nav button[data-view="bank"]');click('#bank-tiles button');click('.builder-view-nav button[data-view="editing"]');click('#answer-tiles button');key('Delete','Delete',46)
   check('Builder keyboard Delete returns tile',ev('document.querySelectorAll("#answer-tiles>li").length===0'))
   # Fill with every available syllable to exercise a long wrong single-line name.
   click('.builder-view-nav button[data-view="bank"]')
   while ev('document.querySelectorAll("#bank-tiles button").length'):
    ident=ev('document.querySelector("#bank-tiles button").dataset.tileId')
    paged_click('#bank-tiles [data-tile-id='+json.dumps(ident)+']','.bank-panel>.nl-vp-pager')
   click('.builder-view-nav button[data-view="name"]');m=measure(game,'390-long-single-line-name');screenshot('builder-long-name')
   check('Builder long name retains single line and explicit page access',m['items']['#candidate-name']['whiteSpace']=='nowrap' and any(p['overflow'] and p['content']=='candidate-name' for p in m['pagers']),m)
   candidate='#candidate>.nl-vp-pager .nl-vp-pager-nav button:last-child'
   click(candidate);check('Builder long name page advances',ev('document.getElementById("candidate-name").scrollLeft>0'))
   click('.builder-view-nav button[data-view="editing"]');click('#next-molecule');ready(game)
   info=ev('document.getElementById("molecule-viewer").contentWindow.NameleculeNameBuilderHost.serializeName()')
   for piece in info['pieces']:
    click('.builder-view-nav button[data-view="bank"]')
    ident=ev('''[...document.querySelectorAll('#bank-tiles button')].find(e=>e.textContent===TEXT)?.dataset.tileId'''.replace('TEXT',json.dumps(piece['text'])))
    assert ident,(piece,info)
    paged_click('#bank-tiles [data-tile-id='+json.dumps(ident)+']','.bank-panel>.nl-vp-pager')
   check('Builder exact native correct composed name',ev('document.getElementById("candidate-name").textContent')==info['correctName'])
   click('.builder-view-nav button[data-view="editing"]');click('#check-answer');wait('document.getElementById("feedback").classList.contains("success")')
   measure(game,'390-correct-feedback');screenshot('builder-correct-feedback')
   click('.builder-feedback-actions .secondary:first-child');click('.builder-view-nav button[data-view="molecule"]')
   for mode in ['condensed','expanded','skeletal']:
    click('[data-representation="'+mode+'"]');wait('document.getElementById("viewer-mask").hidden&&document.querySelector("[data-representation='+mode+']").getAttribute("aria-pressed")==="true"')
   click('#zoom-in');click('#zoom-out');view(1024,640);view(390,700)
   check('Builder form/zoom/resize retains solved name',ev('document.getElementById("candidate-name").textContent')==info['correctName'])
  else:
   click('.puzzle-view-nav button[data-view="pieces"]')
   for _ in range(31):click('[data-hydrogens="4"]')
   check('Puzzle preserves exactly32 allowed nodes and disables33rd',ev('document.querySelectorAll("#board-nodes>button").length===32&&[...document.querySelectorAll("[data-hydrogens]")].every(e=>e.disabled)'))
   click('.puzzle-view-nav button[data-view="editing"]')
   seen=set();next_selector='.puzzle-assembly-content>.nl-vp-pager .nl-vp-pager-nav button:last-child'
   for _ in range(40):
    seen.update(ev('''[...document.querySelectorAll('#board-nodes button')].filter(e=>{const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return e.contains(document.elementFromPoint(x,y))}).map(e=>e.dataset.nodeId)'''))
    if not visible(next_selector) or ev('document.querySelector('+json.dumps(next_selector)+').disabled'):break
    click(next_selector)
   check('Puzzle all32 nodes reachable by explicit board pages',len(seen)==32,{'seen':len(seen)})
   measure(game,'390-max32-board-pages');screenshot('puzzle32nodes')
   click('#check-answer');wait('document.getElementById("game").dataset.puzzleView==="feedback"');click('.puzzle-feedback-actions .secondary:first-child')
   check('Puzzle wrong feedback preserves all32 raw nodes',ev('document.querySelectorAll("#board-nodes>button").length===32'))
   # Ordinary correct graph: find methane through the production level1 bag.
   click('.nl-game-levels__change');click('[data-level="1"]');ready(game)
   for _ in range(5):
    if ev('document.getElementById("target-name").textContent')=='μεθάνιο':break
    click('#next-molecule');ready(game)
   check('Puzzle genuine level1 bag reaches methane',ev('document.getElementById("target-name").textContent')=='μεθάνιο')
   click('.puzzle-view-nav button[data-view="pieces"]');click('[data-hydrogens="4"]');click('.puzzle-view-nav button[data-view="editing"]');click('#check-answer');wait('document.getElementById("feedback").classList.contains("success")')
   measure(game,'390-correct-feedback');screenshot('puzzle-correct-feedback')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 if browser and browser.poll() is None:
  try:OUT['failureState']={'url':ev('location.href'),'body':ev('document.body.innerText'),'measurement':measure(game,'failure')};screenshot('failure')
  except Exception as capture:OUT['captureFailure']=repr(capture)
finally:
 for c in connections:
  try:c.sock.close()
  except Exception:pass
 if browser:
  browser.terminate()
  try:browser.wait(timeout=12)
  except subprocess.TimeoutExpired:browser.kill();browser.wait(timeout=8)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 if profile and profile.exists():shutil.rmtree(profile)
 OUT['cleanup']={'browserExited':browser is None or browser.poll() is not None,'profileRemoved':profile is None or not profile.exists(),'serverClosed':True}
 OUT['sourceAfterSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths};OUT['sourceUnchangedDuringBrowser']=OUT['sourceAfterSHA256']==OUT['sourceSHA256'];OUT['jsErrors']=js_errors
 (DEST/'results.json').write_text(json.dumps(OUT,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'result':str(DEST/'results.json'),'cleanup':OUT['cleanup']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
