"""Developer isolated Chrome geometry and production-input checks; no progress setters."""
from pathlib import Path
from urllib.parse import urlparse, urlsplit, unquote
import ast, base64, datetime, hashlib, http.server, json, os, shutil, socket, struct, subprocess, tempfile, threading, time, traceback, urllib.request
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_VIEWPORT_BROWSER_GRANT')=='repair-detective', 'Exclusive root browser grant required'
RUN_DEADLINE=time.monotonic()+720;PROTOCOL_TIMEOUT=25
connections=[];all_events=[];js_errors=[];preload=None
OUT={'role':'Developer isolated headless Chrome; not independent review','checks':[],'measurements':[],'limitations':['CSS viewport emulation; physical device/browser zoom not certified.','Native viewer/chemistry assets use actual sources; external fonts/JSmol may depend on network.']}
paths=['games/name-repair.html','games/molecular-detective.html','js/namelecule-game-repair.js','js/namelecule-molecular-detective.js','css/namelecule-games.css','css/namelecule-repair-round.css','css/namelecule-molecular-detective.css','css/namelecule-name-builder.css','js/namelecule-game-viewport.js','css/namelecule-game-viewport.css','js/namelecule-game-levels.js','css/namelecule-game-levels.css']
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
def view(w,h):cdp('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False});time.sleep(.3)
def page(path):
 url=f'http://127.0.0.1:{server.server_port}/'+path
 cdp('Page.navigate',{'url':url});wait('document.readyState!=="loading"');time.sleep(.4)

def ready(game):
 if game=='repair':wait('!!document.querySelector(".diagram-image.is-ready")',120)
 else:wait('NameleculeMolecularDetective?.snapshot().phase==="active"',120)
def measure(game,tag):
 selectors=['.round-heading','.diagram-stage','.repair-card','.repair-part-page','.repair-choice-page','[id$="check-button"]','.repair-feedback-stage','.repair-zoom-overlay','.diagram-image'] if game=='repair' else ['.objective','.detective-workspace','.detective-clue','.detective-molecule','#viewer-wrap','#check-answer','#selection-status','#detective-feedback-stage']
 result=ev('''(()=>{const selectors=SELECTORS;return{viewport:{width:innerWidth,height:innerHeight},root:{scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,scrollX,scrollY},items:Object.fromEntries(selectors.map(s=>{const e=document.querySelector(s),r=e?.getBoundingClientRect(),c=e?getComputedStyle(e):null;return[s,e?{x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right,visible:r.width>0&&r.height>0,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,font:c.fontSize}:null]})),pagers:[...document.querySelectorAll('.nl-vp-pager')].map(e=>({overflow:e.classList.contains('is-overflow'),label:e.querySelector('nav')?.getAttribute('aria-label'),rect:e.getBoundingClientRect().toJSON(),content:e.firstElementChild.id||e.firstElementChild.className,text:e.querySelector('nav')?.textContent}))}})()'''.replace('SELECTORS',json.dumps(selectors)))
 result.update(game=game,tag=tag);OUT['measurements'].append(result);return result
def reach(selector):
 for _ in range(15):
  info=ev('''(()=>{const e=document.querySelector(SELECTOR);if(!e)throw Error('Missing '+SELECTOR);const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;const hit=r.width>0&&r.height>0&&e.contains(document.elementFromPoint(x,y));if(hit)return{hit:true};const p=e.closest('.nl-vp-page-content')?.parentNode;if(!p)return{hit:false};const c=p.firstElementChild,b=c.getBoundingClientRect(),horizontal=p.classList.contains('nl-vp-pager-x');const previous=horizontal?r.right<=b.left:r.bottom<=b.top;const nav=p.querySelector('nav'),button=nav?.querySelector(previous?'button:first-child':'button:last-child');return{hit:false,pager:button&&!button.disabled?[...document.querySelectorAll('.nl-vp-pager-nav button')].indexOf(button):null}})()'''.replace('SELECTOR',json.dumps(selector)))
  if info['hit']:click(selector);return
  if info.get('pager') is None:raise AssertionError(('No production pager route',selector,info))
  # Use the DOM index only as an input target; do not modify the document.
  expr='[...document.querySelectorAll(".nl-vp-pager-nav button")]['+str(n)+']'
  q=ev('(()=>{const e='+expr+',r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return{x,y,hit:e.contains(document.elementFromPoint(x,y))}})()')
  check('Visible production pager route',q['hit'],q)
  for kind,buttons in [('mouseMoved',0),('mousePressed',1),('mouseReleased',0)]:cdp('Input.dispatchMouseEvent',{'type':kind,'x':q['x'],'y':q['y'],'button':'none' if kind=='mouseMoved' else 'left','buttons':buttons,'clickCount':1})
  time.sleep(.15)
 raise AssertionError(('Pager route exhausted',selector))
def repair_record():return ev('(()=>{const level=sessionStorage.getItem("namelecule-repair-levels-v1-current");return JSON.parse(sessionStorage.getItem("namelecule-repair-levels-v1-"+level))})()')
def repair_oracle():
 r=repair_record()
 return ev('(async()=>{const input=await NameleculeGeneratedRepairCheckpoint.loadCanonicalInput(null,"enriched"),view=NameleculeGameLevels.createGenerationInput(input,'+str(r['level'])+');return NameleculeRepairGenerator.createGame(view.catalog,view.analyses,{seed:'+json.dumps(r['seed'])+',difficulty:"basic"}).sets.find(s=>s.id==='+json.dumps(r['setId'])+').rounds['+str(r['roundIndex'])+']})()')
def detective_pick(kind,target):
 expression='''(()=>{const f=document.getElementById('molecule-viewer'),w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg');let a;if(KIND==='atoms'){a=g.anchors.find(a=>a.atom+1===TARGET);if(!a){const i=g.vassign.findIndex(a=>a+1===TARGET);a=g.verts[i]}}else{const b=g.groups.find(b=>b.bond+1===TARGET),l=b?.rep||b?.lines[0];if(l)a={x:(l.x1+l.x2)/2,y:(l.y1+l.y2)/2}}if(!a)throw Error('Missing native target geometry');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM());const b=f.getBoundingClientRect(),x=s.x+b.x,y=s.y+b.y;return{x,y,hit:document.elementFromPoint(x,y)===f,target:TARGET,kind:KIND}})()'''
 q=ev(expression.replace('KIND',json.dumps(kind)).replace('TARGET',str(target)));before=ev('NameleculeMolecularDetective.snapshot().selectionRevision')
 check('Genuine native visible picking target '+str(target),q['hit'],q)
 for event,buttons in [('mouseMoved',0),('mousePressed',1),('mouseReleased',0)]:cdp('Input.dispatchMouseEvent',{'type':event,'x':q['x'],'y':q['y'],'button':'none' if event=='mouseMoved' else 'left','buttons':buttons,'clickCount':1})
 wait('NameleculeMolecularDetective.snapshot().selectionRevision>'+str(before),15)
 check('Genuine native raw selection '+kind+str(target),target in ev('NameleculeMolecularDetective.snapshot().'+kind))
def assert_fit(game,tag):
 m=measure(game,tag);w,h=m['viewport']['width'],m['viewport']['height'];check(game+' document fits '+tag,m['root']['scrollWidth']<=w+1 and m['root']['scrollHeight']<=h+1,m['root'])
 for selector in (['[id$="check-button"]'] if game=='repair' else ['#check-answer','#viewer-wrap']):
  item=m['items'][selector];check(game+' required control visible '+tag+' '+selector,item['visible'] and item['y']>=0 and item['bottom']<=h+1,item)
 return m
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
 profile=Path(tempfile.mkdtemp(prefix='namelecule-vp-repair-detective-',dir='/private/tmp'));log=(DEST/'chrome.log').open('w')
 browser=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1500,1000','about:blank'],stdout=log,stderr=subprocess.STDOUT)
 end=time.monotonic()+35
 while not (profile/'DevToolsActivePort').is_file():
  if browser.poll() is not None or time.monotonic()>end:raise RuntimeError('Owned Chrome failed startup')
  time.sleep(.1)
 port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);ctx,connection=connect_target()
 OUT['process']={'pid':browser.pid,'profile':str(profile),'serverPort':server.server_port,'debugPort':port};print(json.dumps(OUT['process']),flush=True)

 requested=os.environ.get('NAMELECULE_VIEWPORT_GAMES','repair,detective').split(',');assert set(requested)<=set(['repair','detective'])
 for game,file in [('repair','name-repair'),('detective','molecular-detective')]:
  if game not in requested:continue
  view(1024,1000 if game=='detective' else 640);page('__before__/games/'+file+'.html');wait('document.querySelectorAll("[data-level]").length===3',120);click('[data-level="3"]');ready(game);view(1024,640)
  m=measure(game,'exact22-before-1024x640');screenshot(game+'-before-1024');check(game+' before exceeds viewport',m['root']['scrollHeight']>640,m['root'])
  view(390,700);page('games/'+file+'.html'+('?pickSet=1' if game=='repair' else ''));wait('document.querySelectorAll("[data-level]").length===3',120);m=measure(game,'390-level-selection');screenshot(game+'-390-level-selection');check(game+' mobile selection document fits',m['root']['scrollHeight']<=701 and m['root']['scrollWidth']<=391,m['root']);reach('[data-level="3"]');ready(game)
  for w,h in [(1024,640),(1280,720),(1440,900),(390,700)]:
   view(w,h);assert_fit(game,str((w,h)));screenshot(game+'-'+str(w)+'-exercise')
   if game=='detective':
    native=ev('''(()=>{const f=document.getElementById('molecule-viewer'),w=f.contentWindow,labels=[...w.document.querySelectorAll('#jsmeNomeclatureSVG svg text')].map(e=>{const r=e.getBoundingClientRect(),m=e.getScreenCTM();return{text:e.textContent,rect:r.toJSON(),renderedFont:parseFloat(w.getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)}}).filter(e=>e.rect.width>0&&e.rect.height>0);return{width:w.innerWidth,height:w.innerHeight,minFont:Math.min(...labels.map(e=>e.renderedFont)),labels}})()''');OUT.setdefault('nativeFraming',[]).append({'viewport':[w,h],**native});check('Detective complete visible native labels fit '+str((w,h)),all(n['rect']['x']>=-1 and n['rect']['y']>=-1 and n['rect']['right']<=native['width']+1 and n['rect']['bottom']<=native['height']+1 for n in native['labels']),native)
   if game=='repair' and w==390:
    click('[data-repair-view-button="structure"]');m=measure(game,'390-structure');check('Repair narrow full molecule stage present',m['items']['.diagram-stage']['visible']);screenshot('repair-390-structure');click('[data-repair-view-button="answer"]')
   if game=='detective' and w==390:
    click('#detective-show-clue');m=measure(game,'390-clue');check('Detective narrow complete clue reachable without molecule overlay',m['items']['.detective-clue']['visible'] and not m['items']['.detective-molecule']['visible']);check('Detective clue text has actual visible hit target',ev('(()=>{const e=document.getElementById("mission-name"),r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))})()'));screenshot('detective-390-clue');click('#detective-show-structure')
  view(390,700)
  if game=='repair':
   rnd=repair_oracle();before=repair_record();
   if rnd['kind']=='replace':
    wrong=next(p['id'] for p in rnd['parts'] if p['id']!=rnd['targetPartId']);reach('[id$="part-'+wrong+'"]');wait('document.getElementById("game-root").dataset.repairStage==="feedback"');screenshot('repair-wrong-part')
    check('Wrong-part feedback does not count check attempt',repair_record()['states'][0]['attempts']==before['states'][0]['attempts']);click('.repair-feedback-stage .secondary:not([hidden])');reach('[id$="part-'+rnd['targetPartId']+'"]')
    bad=next(i for i,c in enumerate(rnd['choices']) if c['value']!=rnd['correctValue']);reach('[id$="choice-'+str(bad)+'"]');click('[id$="check-button"]');wait('document.getElementById("game-root").dataset.repairStage==="feedback"');after=repair_record();check('Wrong check counts one attempt',after['states'][0]['attempts']==before['states'][0]['attempts']+1);screenshot('repair-wrong-check');click('.repair-feedback-stage .secondary:not([hidden])');check('Return preserves wrong choice',repair_record()['states'][0]['selectedValue']==rnd['choices'][bad]['value']);good=next(i for i,c in enumerate(rnd['choices']) if c['value']==rnd['correctValue']);reach('[id$="choice-'+str(good)+'"]')
   else:
    for dest,pid in enumerate(rnd['correctOrder']):
     order=ev('[...document.querySelectorAll(".part-button")].map(e=>e.id.split("part-")[1])');position=order.index(pid)
     if position>dest:reach('[id$="part-'+pid+'"]');click('[id$="move-left"]')
   click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")');screenshot('repair-correct-feedback');check('Repair successful bottom continue reachable',ev('(()=>{const e=document.querySelector("[data-checkpoint-continue]"),r=e.getBoundingClientRect();return !e.disabled&&r.height>0&&r.bottom<=innerHeight})()'))
   click('.repair-feedback-stage .secondary:not([hidden])');check('Repair inspect hides successful footer',ev('document.querySelector("[data-checkpoint-continue]").getClientRects().length===0'));click('.repair-stage-tabs .secondary:last-child');check('Repair feedback return restores successful footer',ev('document.querySelector("[data-checkpoint-continue]").getClientRects().length>0'));click('.repair-feedback-stage .secondary:not([hidden])');click('.diagram-zoom-button');wait('!!document.querySelector(".repair-zoom-overlay")');screenshot('repair-zoom');cdp('Input.dispatchKeyEvent',{'type':'keyDown','key':'Escape','code':'Escape','windowsVirtualKeyCode':27});cdp('Input.dispatchKeyEvent',{'type':'keyUp','key':'Escape','code':'Escape','windowsVirtualKeyCode':27});wait('!document.querySelector(".repair-zoom-overlay")');check('Repair Esc restores zoom focus',ev('document.activeElement.classList.contains("diagram-zoom-button")'))
  else:
   before=ev('NameleculeMolecularDetective.snapshot()');click('#check-answer');wait('!document.getElementById("detective-feedback-stage").hidden');screenshot('detective-empty-feedback');click('#detective-feedback-back');after=ev('NameleculeMolecularDetective.snapshot()');check('Detective feedback return preserves selection and one attempt',after['atoms']==before['atoms'] and after['bonds']==before['bonds'] and after['attempts']==before['attempts']+1)
   oracle=ev('(()=>{const s=NameleculeMolecularDetective.snapshot(),snapshot=document.getElementById("molecule-viewer").contentWindow.NameleculeMolecularDetectiveHost.getSnapshot();return {snapshot,mission:NameleculeMolecularDetectiveEngine.missions(snapshot).find(m=>m.id===s.missionId)}})()');mission=oracle['mission'];accepted=mission['accepted'][-1]
   detective_pick(mission['kind'],accepted[0]);partial=ev('NameleculeMolecularDetective.snapshot()');view(1024,640);time.sleep(.3);check('Detective resize preserves genuine partial selection',ev('NameleculeMolecularDetective.snapshot().'+mission['kind'])==partial[mission['kind']]);view(390,700);time.sleep(.3)
   for target in accepted[1:]:detective_pick(mission['kind'],target)
   click('#check-answer');wait('NameleculeMolecularDetective.snapshot().correct');screenshot('detective-correct-feedback');check('Detective correct Next visible',ev('(()=>{const e=document.getElementById("next-mission"),r=e.getBoundingClientRect();return !e.hidden&&!e.disabled&&r.height>0&&r.bottom<=innerHeight})()'));prior=ev('NameleculeMolecularDetective.snapshot().moleculeId');click('#next-mission');ready('detective');check('Detective next mission production click assigns another molecule',ev('NameleculeMolecularDetective.snapshot().moleculeId')!=prior)
   cdp('Network.setBlockedURLs',{'urls':['*namelecule-molecular-detective-engine.js*']});page('games/molecular-detective.html');wait('document.getElementById("game-status").classList.contains("error")',20);check('Detective missing engine reports graceful retry',ev('document.getElementById("check-answer").disabled&&!document.getElementById("retry-load").hidden'));screenshot('detective-missing-engine');cdp('Network.setBlockedURLs',{'urls':[]})
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
