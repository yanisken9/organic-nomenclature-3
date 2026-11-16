"""Definitions only, extending proven current viewport/levels browser helpers."""
import urllib.parse
PREFIX='/organic-nomenclature-3/'
OWNED_PREFIX='namelecule-release-20261116-'

def release_args():
 p=argparse.ArgumentParser(description='Frozen candidate/public release acceptance')
 p.add_argument('--phase',choices=['candidate','public'],required=True)
 p.add_argument('--manifest',type=Path,required=True)
 p.add_argument('--release-root',type=Path,required=True)
 p.add_argument('--base-url',default='https://yanisken9.github.io/organic-nomenclature-3/')
 p.add_argument('--timeout',type=int,default=900)
 return p.parse_args()

class ReleaseHandler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(SERVE_ROOT),**kw)
 def log_message(self,*a):pass
 def send_error(self,code,message=None,explain=None):OUT.setdefault('httpErrors',[]).append({'path':self.path,'code':code});super().send_error(code,message,explain)
 def translate_path(self,path):
  url=urllib.parse.urlsplit(path);decoded=urllib.parse.unquote(url.path)
  if not decoded.startswith(PREFIX):return str(SERVE_ROOT/'__outside_repo_prefix__')
  relative=Path(decoded[len(PREFIX):]);assert not relative.is_absolute() and '..' not in relative.parts
  return str(SERVE_ROOT/relative)

def manifest_files(data):
 for name in ['files','runtimeFiles','runtime','overlayFiles']:
  values=data.get(name)
  if isinstance(values,dict):
   return {p:(v if isinstance(v,str) else v.get('sha256',v.get('SHA256'))) for p,v in values.items()}
 raise AssertionError('Release manifest needs explicit path→SHA256 files map')

def served_hashes():return {p:sha(SERVE_ROOT/p) for p in sorted(FROZEN)}

def page(path):
 marker='release-departing-'+str(time.monotonic());ev('window.__releaseDocumentGeneration='+json.dumps(marker)+';true')
 target=OUT['process']['baseURL']+path
 call('browsingContext.navigate',{'context':ctx,'url':target,'wait':'none'})
 pathname=urllib.parse.urlsplit(target).path
 wait('window.__releaseDocumentGeneration!=='+json.dumps(marker)+'&&location.pathname==='+json.dumps(pathname)+'&&document.readyState==="complete"',70)
 call('browsingContext.activate',{'context':ctx})
 OUT.setdefault('navigation',[]).append(read('({url:location.href,ready:document.readyState,width:innerWidth,height:innerHeight})'))

def nav_click(selector,path_suffix):
 marker='release-click-departing-'+str(time.monotonic());ev('window.__releaseDocumentGeneration='+json.dumps(marker)+';true')
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(.25);click(selector)
 wait('window.__releaseDocumentGeneration!=='+json.dumps(marker)+'&&location.pathname.endsWith('+json.dumps(path_suffix)+')&&document.readyState==="complete"',70)

def release_lesson(index=0):
 global INDEX
 INDEX=index;page('mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&v=release-20261116#step='+str(index+1));ready();wait('fScenarioPresent().index==='+str(index))

def root_click(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(.2);click(selector)

def standalone_start(game,path):
 page(path);wait('document.querySelectorAll("[data-level]").length===3',110)
 # Final native startup builds the real level picker. A successful input must
 # change aria-pressed/current status before native load is considered started.
 click('[data-level="1"]')
 if game=='repair':wait('!!document.querySelector(".diagram-image.is-ready")',100)
 else:wait('document.querySelector("[data-level=\\\"1\\\"]")?.getAttribute("aria-pressed")==="true"',12)
 game_ready(game,False)
 if game=='builder':
  mid=builder_info(False)['native']['selectedMol'];q=element_metrics('document.getElementById("check-answer")');check(q['visible'] and q['within'] and q['hit'],'standalone Builder required Check accessible',q)
 elif game=='puzzle':
  info=puzzle_info(False);mid=NAME_IDS[info['name']];q=element_metrics('document.getElementById("assembly-board")');check(q['visible'] and q['within'],'standalone Puzzle board accessible',q)
 elif game=='detective':
  mid=ds(False)['moleculeId'];check(game_read(game,'document.getElementById("viewer-mask").hidden'),'standalone Detective native fully loaded')
 else:
  mid=repair_oracle(False)['moleculeId'];q=element_metrics('document.querySelector("[id$=\\\"check-button\\\"]")');check(q['visible'] and q['within'],'standalone Repair Check accessible',q)
 check(mid in BANDS['1'],game+' standalone Basic actual verified assignment',mid);shot('standalone-'+game+'-basic')
 OUT.setdefault('standaloneStarts',[]).append({'game':game,'moleculeId':mid,'url':read('location.href')})

def welcome_library():
 page('design/welcome-proposal.html?v=release-20261116');wait('document.querySelectorAll(".card.two .game-action").length===4&&[...document.querySelectorAll(".card.two .game-action img")].every(i=>i.complete&&i.naturalWidth>0)')
 links=read('[...document.querySelectorAll(".card.two .game-action")].map(a=>({text:a.textContent.trim(),href:a.href,logo:a.querySelector("img").src,naturalWidth:a.querySelector("img").naturalWidth}))')
 check({urllib.parse.urlsplit(n['href']).path.rsplit('/',1)[1] for n in links}=={'name-repair.html','name-builder.html','molecular-puzzle.html','molecular-detective.html'},'welcome card2 all four exact game links and loaded logos',links);OUT['welcomeGames']=links;shot('welcome')
 nav_click('.card.one .action','/design/theory-library.html');wait('document.querySelectorAll(".lesson .action").length===14')
 lessons=read('[...document.querySelectorAll(".lesson .action")].map(a=>({text:a.textContent.trim(),href:a.href}))')
 check(len(lessons)==14 and all('mulermoc-nom-57.html?' in a['href'] for a in lessons),'library all14 lessons point to Main57',lessons);OUT['libraryLinks']=lessons
 nav_click('.lesson:first-child .action','/mulermoc-nom-57.html');ready();wait('fScenarioPresent().index===0');OUT['lessonURL']=read('location.href')
 native=read('({count:Object.keys(nameExamples).length,expanded:Object.keys(nameExamples).filter(id=>!!nameExamples[id].structure2D_Expanded).length,customCount:Object.keys(window.nameExamplesCustom||{}).length})')
 check(native['count']==147 and native['expanded']==147 and native['customCount']==6,'actual Main57 has all147 hydrated records including6custom',native);OUT['nativeInventory']=native
 pool=read('({1:NameleculeGameLevels.poolFor(1).length,2:NameleculeGameLevels.poolFor(2).length,3:NameleculeGameLevels.poolFor(3).length})')
 check(pool=={'1':5,'2':4,'3':5},'actual shared alkane14 pool has5/4/5 structural bands',pool)

def one_wrong_correct(game):
 choose(game,1)
 if game=='repair':
  rnd=repair_oracle(True);view(game,'answer')
  if rnd['kind']=='replace':
   click('[id$="part-'+rnd['targetPartId']+'"]');wrong=next(i for i,c in enumerate(rnd['choices']) if c['value']!=rnd['correctValue']);click('[id$="choice-'+str(wrong)+'"]')
  click('[id$="check-button"]');wait('document.querySelector(".nl-repair-round").dataset.repairStage==="feedback"');check(not active_attempt(game,1)['progress']['states'][0]['solved'],'real wrong Repair candidate leaves checkpoint locked');feedback_pages(game,'candidate wrong Repair');click('.repair-feedback-stage .repair-stage-heading button:first-of-type')
 elif game=='builder':
  solve_builder('candidate prefix',True,True);view(game,'editing');game_click(game,'#check-answer',True);wait('!('+window_expr(game,True)+').document.getElementById("feedback").hidden');check(not builder_info(True)['solved'],'real incomplete Builder name rejected');feedback_pages(game,'candidate wrong Builder');game_click(game,'.builder-feedback-actions button:first-child',True)
 else:
  view(game,'pieces');game_click(game,'[data-hydrogens="0"]',True);view(game,'editing');game_click(game,'#check-answer',True);wait('!('+window_expr(game,True)+').document.getElementById("feedback").hidden');check(not puzzle_info(True)['solved'],'real incompatible Puzzle group rejected');feedback_pages(game,'candidate wrong Puzzle');game_click(game,'.puzzle-feedback-actions button:first-child',True);view(game,'tools');game_click(game,'#undo-action',True);view(game,'editing');check(not puzzle_info(True)['nodes'],'actual Undo clears wrong graph before genuine solution')
 SOLVERS[game]('candidate embedded '+game+' genuine correct answer',True);wait('!!document.querySelector(".round-next button")');check(active_attempt(game,1)['progress']['states'][0]['solved'] and not gate_state()['solved'],'one real '+game+' correct answer regraded without premature unlock');feedback_pages(game,'candidate correct '+game);shot('embedded-'+game+'-correct')

def checkpoint_delivery(full):
 global INDEX
 for index in range(1,4):pause(.35);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index
 recipe=read('fScenarioPresent().steps[3].checkpoint.round');second=read('fScenarioPresent().steps[10].checkpoint.round')
 check(recipe['requiredLevels']==[1] and second['requiredLevels']==[1,2] and second['allowedLevels']==[1,2,3],'delivered lesson requires Basic at4, Basic+Intermediate at11 andoptional3',{'first':recipe,'second':second});check(read('document.getElementById("scNext").disabled'),'fresh delivered gate4 locked')
 open_gate()
 if full:
  for game in ['repair','builder','puzzle']:one_wrong_correct(game)
 choose('detective',1);OUT['gate4IDs']=viewport_triple('detective',1);earned=gate_state()['receipts'];check(gate_state()['solved'] and bool(earned['1']),'delivered genuine Detective triple unlocks gate4')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});ready();wait('fScenarioPresent().index===3');open_gate();game_ready('detective',True)
 check(gate_state()['solved'] and gate_state()['receipts']==earned,'delivered earned receipt canonical cold restore exact');activate_button('[data-checkpoint-continue]');wait('fScenarioPresent().index===4&&!document.getElementById("nlQuizDialog").open');INDEX=4;check(True,'actual delivered checkpoint Continue reaches step5');shot('delivered-step5')
 if full:
  for index in range(5,11):pause(.35);click('#scNext');wait('fScenarioPresent().index==='+str(index));INDEX=index
  open_gate();choose('builder',1);click('#nlQuizDialog .nl-game-levels__change')
  labels=read('[...document.querySelectorAll("#nlQuizDialog [data-level]")].map(b=>({level:b.dataset.level,text:b.textContent,rect:b.getBoundingClientRect().toJSON()}))')
  check(all(('Υποχρεωτικό' if x['level'] in ['1','2'] else 'Προαιρετικό') in x['text'] for x in labels),'actual gate11 selector labels required1/2 andoptional3',labels);shot('delivered-gate11-levels')

def protected_smoke():
 page('mulermoc-nom-52.html');wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&typeof nameExamples==="object"&&Object.keys(nameExamples).length>0',100)
 check(read('document.title.length>0&&!!document.querySelector("#jsmeNomeclatureSVG")'),'preserved Main52 native host loads');shot('preserved-main52')
 page('react-preview/dist/index.html');wait('document.querySelector("#root")?.innerText.trim().length>50',90)
 text=read('document.getElementById("root").innerText.slice(0,1500)');check('Namelecule' in text or 'ονομ' in text.lower(),'preserved React build renders substantive interface',text);shot('preserved-react')

def full_shot(name):
 metrics=cdp('Page.getLayoutMetrics');height=int(metrics['cssContentSize']['height']);width=int(metrics['cssContentSize']['width'])
 data=cdp('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'fromSurface':True,'clip':{'x':0,'y':0,'width':width,'height':height,'scale':1}})
 (DEST/(name+'.png')).write_bytes(base64.b64decode(data['data']));return {'width':width,'height':height}

def report_qa():
 page('docs/professor-20261116/update.html');wait('document.querySelectorAll("h2").length>=6&&!!document.querySelector("footer")')
 links=read('[...document.querySelectorAll("a[href]")].map(a=>({text:a.textContent,href:a.href}))');targets=[]
 for item in links:
  url=urllib.parse.urlsplit(item['href'])
  if url.path.startswith(PREFIX):
   relative=url.path[len(PREFIX):];response=urllib.request.urlopen(OUT['process']['baseURL']+relative,timeout=min(20,check_deadline()));targets.append({'text':item['text'],'relative':relative,'status':response.status,'bytes':len(response.read())})
 check(targets and all(t['status']==200 and t['bytes']>0 for t in targets),'all report repository link targets load under actual delivery prefix',targets);OUT['reportLinks']=links
 views=[]
 for media,width,height in [('screen',1440,1000),('print',794,1123)]:
  cdp('Emulation.setEmulatedMedia',{'media':media});viewport(width,height);pause(.4)
  proof=read('(()=>{const first=document.querySelector("h1").getBoundingClientRect(),last=document.querySelector("footer").getBoundingClientRect();return{media:matchMedia("print").matches?"print":"screen",width:innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,first:first.toJSON(),last:last.toJSON(),headings:[...document.querySelectorAll("h2")].map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON()}))}})()')
  check(proof['scrollWidth']<=proof['clientWidth']+1 and proof['first']['top']>=0 and proof['last']['bottom']<=proof['scrollHeight']+1,'report first/last section and width unclipped '+media,proof);proof['capture']=full_shot('report-'+media+'-full');views.append(proof)
 cdp('Emulation.setEmulatedMedia',{'media':'screen'});viewport(1280,720);OUT['reportVisual']=views

def release_flow():
 welcome_library();checkpoint_delivery(ARGS.phase=='candidate')
 for game,path in [('repair','games/name-repair.html'),('builder','games/name-builder.html'),('puzzle','games/molecular-puzzle.html'),('detective','games/molecular-detective.html')]:
  if ARGS.phase=='candidate' or game=='detective':standalone_start(game,path+'?v=release-20261116')
 if ARGS.phase=='candidate':protected_smoke()
 report_qa()

def split_runtime_logs():
 tracker_tokens=['google-analytics','googletagmanager','doubleclick','clarity.ms','connect.facebook.net','cloudflareinsights']
 app=[];tracker=[]
 for error in js_errors:
  detail=error.get('exceptionDetails',{});urls=[detail.get('url','')]+[f.get('url','') for f in detail.get('stackTrace',{}).get('callFrames',[])]
  if any(any(token in url for token in tracker_tokens) for url in urls) and not any(PREFIX in url for url in urls):tracker.append(error)
  else:app.append(error)
 requests={e.get('params',{}).get('requestId'):e.get('params',{}).get('request',{}).get('url') for e in all_events if e.get('method')=='Network.requestWillBeSent'}
 network=[]
 for event in all_events:
  if event.get('method')!='Network.loadingFailed':continue
  params=event.get('params',{});url=requests.get(params.get('requestId'));network.append({'url':url,'details':params,'kind':'external-tracker' if url and any(token in url for token in tracker_tokens) else 'document-canceled' if params.get('canceled') and params.get('type')=='Document' else 'application-or-external-dependency'})
 return {'applicationOrUnattributedExceptions':app,'externalTrackerExceptions':tracker,'consoleEntries':[e['params'] for e in all_events if e.get('method')=='Log.entryAdded'],'networkFailures':network}

def release_main():
 global ARGS,OUT,DEST,FROZEN,SERVE_ROOT,RUN_TIMEOUT,RUN_DEADLINE,PROTOCOL_TIMEOUT,MODE,GAME,INDEX,MOLS,NAME_IDS,BANDS,ALL_IDS,ctx,connection,port,preload,connections,all_events,js_errors
 ARGS=release_args();assert os.environ.get('NAMELECULE_RELEASE_BROWSER_GRANT')=='frozen','Root assembled frozen target + exclusive slot grant required'
 assert 0<ARGS.timeout<=1200;RUN_TIMEOUT=ARGS.timeout;RUN_DEADLINE=time.monotonic()+RUN_TIMEOUT;PROTOCOL_TIMEOUT=30
 SERVE_ROOT=ARGS.release_root.resolve();freeze=json.loads(ARGS.manifest.read_text());FROZEN=manifest_files(freeze);assert FROZEN and all(FROZEN.values());assert served_hashes()==FROZEN,'Frozen assembled candidate drift before browser'
 MODE=ARGS.phase;GAME='detective';INDEX=0;MOLS={m['id']:m['mol'] for m in json.loads((SERVE_ROOT/'games/data/alkane-structures-v2.json').read_text())['molecules']};facts=json.loads((CODE_ROOT/'docs/checks/alkane-pool-implementation-20261116/detective/snapshots.json').read_text());NAME_IDS={facts[mid]['correctName']:mid for mid in MOLS};BANDS={'1':['methane','ethane','propane','butane','pentane'],'2':['methyl_2_butane','methyl_2_pentane','methyl_3_pentane','ethyl_3_pentane'],'3':['dimethyl_2_2_propane','dimethyl_2_2_butane','dimethyl_2_3_butane','ethyl_3_methyl_2_pentane','ethyl_3_dimethyl_2_5_hexane']};ALL_IDS=sum(BANDS.values(),[])
 DEST=HERE/('run-'+MODE+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S'));DEST.mkdir(exist_ok=False)
 OUT={'role':'Developer release acceptance; not independent browser execution','phase':MODE,'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest':str(ARGS.manifest),'manifestSHA256':sha(ARGS.manifest),'sourceBefore':served_hashes(),'checks':[],'correctUIAttempts':[],'puzzlePointerDrag':{'skipped':'Existing local full regression evidence reused; delivery run does not repeat drag matrix.'},'limits':['Bounded delivery acceptance reuses prior full local chemistry/game/viewer regressions.','Headless100% CSS viewport only; actual3D, browser zoom125/200, physical mobile, offline and conference reliability unqualified.','Report print evidence is HTML print-media/A4-width screenshot; no PDF/pagination proof.'],'helperSHA256':{str(p.relative_to(CODE_ROOT)):sha(p) for p in [REUSED,REUSED.parent/'lesson-checks.py',CODE_ROOT/'docs/checks/game-levels-alkanes-implementation-20261116/browser/replay-levels.py']}}
 for p in [Path(__file__),HERE/'release-checks.py',ARGS.manifest]:shutil.copyfile(p,DEST/p.name)
 browser=server=profile=log=None;connections=[];all_events=[];js_errors=[];preload=None;lock=HERE/'.owned-browser.lock'
 try:
  fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,json.dumps({'pid':os.getpid(),'run':str(DEST)}).encode());os.close(fd)
  if MODE=='candidate':server=http.server.ThreadingHTTPServer(('127.0.0.1',0),ReleaseHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'+PREFIX
  else:base=ARGS.base_url.rstrip('/')+'/'
  profile=Path(tempfile.mkdtemp(prefix=OWNED_PREFIX+MODE+'-',dir='/private/tmp'));log=(DEST/'chrome.log').open('w');load_functions(RECORDED/'replay-chrome.py',{'configure_connection','connect_target','cdp','ev','wait_document','call'},include_classes={'CDP'})
  browser=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--no-first-run','--no-default-browser-check','--user-data-dir='+str(profile),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--window-size=1800,1400','about:blank'],stdout=log,stderr=subprocess.STDOUT)
  deadline=min(RUN_DEADLINE,time.monotonic()+35)
  while not (profile/'DevToolsActivePort').is_file():
   if browser.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Owned Chrome startup failed')
   time.sleep(.1)
  port=int((profile/'DevToolsActivePort').read_text().splitlines()[0]);ctx,connection=connect_target();OUT['process']={'ownedPID':browser.pid,'profile':str(profile),'debugPort':port,'serverPort':server.server_port if server else None,'baseURL':base,'serveRoot':str(SERVE_ROOT)};print(json.dumps(OUT['process']),flush=True)
  call('script.addPreloadScript',{'functionDeclaration':PRELOAD});viewport(1280,720);release_flow();classified=split_runtime_logs();check(not classified['applicationOrUnattributedExceptions'],'no captured application or unattributed JavaScript exceptions',classified);OUT['completed']=True
 except Exception:
  OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
  if browser:
   try:OUT['failureState']={'url':read('location.href'),'body':read('document.body.innerText.slice(-7000)'),'gate':rec() if read('typeof fScenarioPresent==="function"') else None};shot('failure')
   except Exception as error:OUT['failureCaptureError']=repr(error)
 finally:
  OUT['javascriptErrors']=js_errors;OUT['events']=all_events;OUT['classifiedLogs']=split_runtime_logs();OUT['sourceAfter']=served_hashes();OUT['sourceUnchangedDuringRun']=OUT['sourceBefore']==OUT['sourceAfter']
  if not OUT['sourceUnchangedDuringRun']:OUT['completed']=False
  for item in connections:
   try:item.sock.close()
   except OSError:pass
  if browser and browser.poll() is None:
   browser.terminate()
   try:browser.wait(timeout=8)
   except subprocess.TimeoutExpired:browser.kill();browser.wait(timeout=5)
  if server:server.shutdown();server.server_close()
  if log:log.close()
  OUT['ownedBrowserExited']=browser is None or browser.poll() is not None;OUT['ownedServerClosed']=server is None or server.fileno()==-1
  if profile and OUT['ownedBrowserExited'] and profile.parent==Path('/private/tmp') and profile.name.startswith(OWNED_PREFIX) and not profile.is_symlink():shutil.rmtree(profile);OUT['ownedProfileRemoved']=not profile.exists()
  if lock.exists() and json.loads(lock.read_text()).get('pid')==os.getpid():lock.unlink()
  OUT['finishedUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(DEST/'results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':OUT.get('completed',False),'phase':MODE,'checks':len(OUT['checks']),'correctUIAnswers':len(OUT['correctUIAttempts']),'sourceUnchanged':OUT['sourceUnchangedDuringRun'],'ownedBrowserExited':OUT['ownedBrowserExited']}),flush=True)
 if not OUT.get('completed'):raise SystemExit(1)
