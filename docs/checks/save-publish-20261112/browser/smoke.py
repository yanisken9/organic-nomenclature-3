"""Bounded release smoke, after today's extensive interaction verification.
One owned headless Firefox. No changes to answer/progress fixtures or app code.
Optional NAMELECULE_RELEASE_BASE_URL tests the published origin; otherwise an
isolated local HTTP server serves NAMELECULE_RELEASE_ROOT (defaults to repo).
"""
from pathlib import Path
import base64,datetime,hashlib,http.server,json,os,socket,subprocess,tempfile,threading,time,traceback
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SOURCE=['design/welcome-proposal.html','design/theory-library.html','mulermoc-nom-55.html','js/namelecule-game-choice-checkpoint.js','games/molecular-puzzle.html','js/namelecule-molecular-puzzle.js','js/namelecule-molecular-puzzle-engine.js','css/namelecule-molecular-puzzle.css','games/name-builder.html','js/namelecule-name-builder.js','css/namelecule-name-builder.css','games/name-repair.html','js/namelecule-game-repair.js','scenarios/alkanes-user-3.scenario.json','games/assets/molecular-puzzle/molecular-puzzle-logo-flat-v7.png','js/namelecule-chemistry-client.js','js/namelecule-chemistry-worker.js','games/data/alkane-structures.json','js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js']
sha=lambda:{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCE}
OUT={'checks':[],'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceBefore':sha(),'scope':'Release smoke after completed full triple/progress/regression runs. Real welcome/library/lesson links and trusted game controls. No fabricated receipts and no repeat of all already verified triples.'}
server=firefox=log=None
PUBLIC=os.environ.get('NAMELECULE_RELEASE_BASE_URL');SERVE_ROOT=Path(os.environ.get('NAMELECULE_RELEASE_ROOT',str(ROOT)))
SUFFIX=os.environ.get('NAMELECULE_RELEASE_LABEL') or ('public' if PUBLIC else 'candidate')
def check(ok,label,detail=None):
 OUT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError((label,detail))
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def pause(sec=.18):time.sleep(sec)
def wait(expr,seconds=70):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if ev(expr):return
  pause(.15)
 raise AssertionError('Timed out '+expr)
def page(path):
 call('browsingContext.navigate',{'context':ctx,'url':OUT['baseURL']+path,'wait':'none'});wait('document.readyState!=="loading"')
def clickel(expr):
 for attempt in range(10):
  ev('('+expr+').scrollIntoView({block:"center",inline:"nearest",behavior:"instant"});true');pause(.25)
  q=read('(()=>{const e='+expr+',r=e.getBoundingClientRect();let x=r.x+r.width/2,y=r.y+r.height/2,w=e.ownerDocument.defaultView,hit=e.contains(w.document.elementFromPoint(x,y));while(w!==window){const f=w.frameElement.getBoundingClientRect();x+=f.x;y+=f.y;w=w.parent;hit=hit&&w.document.elementFromPoint(x,y)===e.ownerDocument.defaultView.frameElement}const d=document.getElementById("nlQuizDialog"),h=d?.querySelector(".nl-quiz-dialog-header").getBoundingClientRect();return{x:Math.round(x),y:Math.round(y),hit,disabled:!!e.disabled,headerBottom:h?.bottom??0,dialogBottom:d?.getBoundingClientRect().bottom??innerHeight}})()')
  if q['disabled']:raise AssertionError(('Disabled',expr,q))
  if q['hit'] and (q['y']>=q['headerBottom']+5 or 'scNext' in expr):break
  if q['y']<q['headerBottom']+10:ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['headerBottom']-25)+',behavior:"instant"});true')
  elif q['y']>q['dialogBottom']-10:ev('document.getElementById("nlQuizDialog")?.scrollBy({top:'+str(q['y']-q['dialogBottom']+25)+',behavior:"instant"});true')
  pause(.2)
 else:raise AssertionError(('No visible hit point',expr,q))
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'release-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':q['x'],'y':q['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]});pause(.1)
def click(sel):clickel('document.querySelector('+json.dumps(sel)+')')
def pc(sel):clickel('document.querySelector(".nl-puzzle-frame").contentDocument.querySelector('+json.dumps(sel)+')')
def pread(expr):return read('document.querySelector(".nl-puzzle-frame").contentWindow.eval('+json.dumps(expr)+')')
def shot(name):
 data=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(HERE/(SUFFIX+'-'+name)).write_bytes(base64.b64decode(data['data']))
def ready():wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!document.documentElement.classList.contains("lesson-loading")',100)
def open_gate():wait('!!document.getElementById("nlQuizOpen")&&!document.getElementById("nlQuizOpen").disabled');click('#nlQuizOpen');wait('document.getElementById("nlQuizDialog").open')
def bank_state():return read('({answer:[...document.querySelectorAll("#answer-tiles button")].map(e=>e.dataset.tileId),bank:[...document.querySelectorAll("#bank-tiles button")].map(e=>e.dataset.tileId)})')
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(SERVE_ROOT),**kw)
 def log_message(self,*a):pass
 def send_error(self,code,message=None,explain=None):OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)
try:
 if not PUBLIC:
  OUT['servedSourceBefore']={p:hashlib.sha256((SERVE_ROOT/p).read_bytes()).hexdigest() if (SERVE_ROOT/p).is_file() else None for p in SOURCE}
  check(OUT['servedSourceBefore']==OUT['sourceBefore'],'isolated candidate runtime files match exact reviewed working-tree bytes',{'serveRoot':str(SERVE_ROOT),'fileCount':len(SOURCE)})
 if PUBLIC:OUT['baseURL']=PUBLIC.rstrip('/')+'/'
 else:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();OUT['baseURL']=f'http://127.0.0.1:{server.server_port}/'
 with socket.socket() as p:p.bind(('127.0.0.1',0));port=p.getsockname()[1]
 profile=Path(tempfile.mkdtemp(prefix='namelecule-release-smoke-20261112-'));log=(HERE/(SUFFIX+'-firefox.log')).open('w')
 firefox=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',str(profile),'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
 OUT['process']={'ownedPID':firefox.pid,'profile':str(profile),'bidiPort':port,'serveRoot':str(SERVE_ROOT),'ownedServerPort':server.server_port if server else None};print(json.dumps(OUT['process']),flush=True)
 deadline=time.monotonic()+25
 while True:
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.4):break
  except OSError:
   if firefox.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned BiDi endpoint unavailable')
   pause(.2)
 os.environ['NAMELECULE_BIDI_PORT']=str(port);os.environ['NAMELECULE_TEST_BASE_URL']=OUT['baseURL']
 exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-release-smoke','exec'))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1440,'height':1000},'devicePixelRatio':1})
 page('design/welcome-proposal.html');wait('!!document.querySelector(".card.one .action")')
 check(ev('document.title.includes("Namelecule")&&document.querySelector(".brand img").complete'),'welcome title and brand loaded');OUT['welcomeGames']=read('[...document.querySelectorAll(".game-action")].map(e=>({text:e.textContent.trim(),href:e.href}))');shot('welcome.png')
 click('.card.one .action');wait('location.pathname.endsWith("/design/theory-library.html")&&!!document.querySelector("#alkanes-title")')
 link=read('document.querySelector(".lesson:first-child .action").href');check('mulermoc-nom-55.html?' in link and 'alkanes-user-3.scenario.json' in link,'library alkane entry points to active Main55',link)
 click('.lesson:first-child .action');ready();check(read('fScenarioPresent().index')==0,'welcome/library actual clicks open lesson at step1');OUT['lessonURL']=read('location.href')
 for index in range(1,4):pause(.85);click('#scNext');wait('fScenarioPresent().index==='+str(index))
 check(ev('document.getElementById("scNext").disabled'),'cold gate4 requires earned triple');open_gate();wait('document.querySelectorAll(".nl-game-choice-card").length===3')
 cards=read('[...document.querySelectorAll(".nl-game-choice-card")].map(e=>e.textContent)');check(any('Μοριακό παζλ' in x for x in cards),'lesson exposes all three games',cards);shot('third-game-choice.png')
 click('.nl-game-choice-card:nth-child(3)');wait('!!document.querySelector(".nl-puzzle-frame")?.contentDocument?.querySelector("#assembly-board[aria-busy=false]")')
 check(read('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','puzzle embedded round counter correct')
 check(pread('document.getElementById("round-select").offsetParent===null&&document.getElementById("next-molecule").offsetParent===null'),'embedded puzzle uses parent controlled rounds')
 check(pread('!!document.getElementById("target-name").textContent&&document.querySelector(".puzzle-logo").complete'),'embedded verified target and logo ready');OUT['embeddedTarget']=pread('document.getElementById("target-name").textContent');shot('lesson-puzzle.png')
 pc('[data-hydrogens="0"]');pc('#check-answer');check(pread('!document.getElementById("feedback").hidden&&!document.getElementById("feedback").classList.contains("success")'),'real wrong embedded graph gives feedback');check(ev('document.getElementById("scNext").disabled'),'wrong graph leaves gate locked')
 OUT['gate11Configuration']=read('fScenarioPresent().steps[10].checkpoint');check(OUT['gate11Configuration']['type']=='alkane-game-choice-set' and OUT['gate11Configuration']['round']['setId']=='alkanes-branched','gate11 keeps reviewed branched three-game adapter')
 print('welcome/library/Main55/embedded puzzle passed',flush=True)
 page('games/molecular-puzzle.html');wait('document.querySelector("#round-select").options.length===8&&!document.querySelector("#next-molecule").disabled')
 check(read('document.getElementById("target-name").textContent')=='μεθάνιο','standalone puzzle opens verified methane');click('[data-hydrogens="4"]');click('#check-answer');check(ev('document.getElementById("feedback").classList.contains("success")'),'standalone genuine methane construction accepted');shot('standalone-puzzle.png')
 page('games/name-builder.html');wait('!!document.querySelector("#bank-tiles button")&&!document.querySelector("#bank-tiles button").disabled',85)
 instructions=read('document.getElementById("builder-instructions")?.textContent||document.querySelector(".helper").textContent')
 check(all(word in instructions for word in ['Προσθήκη','Αλλαγή σειράς','Αφαίρεση','Delete']) and 'Tab' not in instructions,'Builder release has requested three control instructions',instructions)
 original=bank_state();tid=original['bank'][0];click('#bank-tiles [data-tile-id='+json.dumps(tid)+']');check(bank_state()['answer']==[tid],'Builder actual click adds chosen tile')
 ev('document.getElementById("bank-tiles").scrollIntoView({block:"center",behavior:"instant"});true');pause(.3)
 coords=read('(()=>{const a=document.querySelector("#answer-tiles button").getBoundingClientRect(),b=document.getElementById("bank-tiles").getBoundingClientRect();return{from:{x:Math.round(a.left+a.width/2),y:Math.round(a.top+a.height/2)},to:{x:Math.round(b.right-18),y:Math.round(b.top+b.height/2)},height:innerHeight}})()')
 check(all(0<=p['y']<=coords['height'] for p in [coords['from'],coords['to']]),'Builder drag source and bank destination actually visible',coords)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'release-drag','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove',**coords['from'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerMove',**coords['to'],'duration':350},{'type':'pointerUp','button':0}]}]});pause(.3)
 check(bank_state()==original,'Builder trusted outside drop restores exact original bank order');shot('builder-return.png')
 page('games/name-repair.html');wait('document.getElementById("game-root").getAttribute("aria-busy")==="false"&&!!document.querySelector(".workshop-set-card")',70)
 check(ev('document.title.includes("Συνεργείο")'),'Workshop entry ready');OUT['workshopCards']=read('[...document.querySelectorAll(".workshop-set-card")].map(e=>e.textContent)');shot('workshop-entry.png')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureLocation']=read('location.href');shot('failure.png')
 except Exception:pass
finally:
 OUT['javascriptErrors']=globals().get('js_errors',[]);OUT['sourceAfter']=sha();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
 if firefox is not None and firefox.poll() is None:
  firefox.terminate()
  try:firefox.wait(timeout=8)
  except subprocess.TimeoutExpired:firefox.kill();firefox.wait(timeout=5)
 if server:server.shutdown();server.server_close()
 if log:log.close()
 OUT['ownedBrowserExited']=firefox is None or firefox.poll() is not None
 (HERE/(SUFFIX+'-results.json')).write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'completed':OUT.get('completed',False),'checks':len(OUT['checks']),'javascriptErrors':len(OUT['javascriptErrors']),'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
if not OUT.get('completed'):raise SystemExit(1)
