from pathlib import Path
import tempfile,subprocess,socket,os,time,json,traceback,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
profile=tempfile.mkdtemp(prefix='namelecule-name-clearance-')
with socket.socket()as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
log_path=HERE/'clearance-firefox.log';log=log_path.open('w')
ff=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--headless','--no-remote','--profile',profile,'--remote-debugging-port',str(port)],stdout=log,stderr=subprocess.STDOUT)
(HERE/'clearance-process.json').write_text(json.dumps({'firefoxPID':ff.pid,'profile':profile,'bidiPort':port,'baseURL':'http://127.0.0.1:49897/','purpose':'Targeted NB-SL-01 correction verification only'},indent=2)+'\n')
out={'completed':False,'checks':[],'geometry':[],'role':'Developer targeted actual-browser evidence; correction NB-SL-01'}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def log_snapshot():
 b=log_path.read_bytes();s=b.decode('utf-8',errors='replace');return{'bytes':len(b),'timeoutWarnings':s.count('Script terminated by timeout'),'bidiWeakMapErrors':s.count('WeakMap key null')}
try:
 for _ in range(150):
  try:
   with socket.create_connection(('127.0.0.1',port),timeout=.1):break
  except OSError:time.sleep(.1)
 exec((HERE/'driver.py').read_text().replace("HERE/'process.json'","HERE/'clearance-process.json'"),globals())
 open_page('games/name-builder.html?v=single-line-20261111-r2&molecule=ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid');wait('document.querySelectorAll("#bank-tiles button").length>0',60)
 ev('(()=>{for(let p of __builderEvents.findLast(e=>e.type==="round").pieces)[...document.querySelectorAll("#bank-tiles button")].find(b=>b.textContent===p.text).click();document.getElementById("check-answer").click();return true})()')
 check(ev('document.querySelector("#feedback").classList.contains("success")'),'Longest exact answer still succeeds')
 for width,height in [(1280,900),(390,844),(320,700)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.15)
  for selector in ['#candidate-name','#feedback strong']:
   ev('(()=>{let n=document.querySelector('+json.dumps(selector)+');n.scrollIntoView({block:"center",behavior:"instant"});n.scrollLeft=0;n.focus({preventScroll:true});return true})()')
   call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'clearance-keyboard','actions':sum(([{'type':'keyDown','value':'\ue014'},{'type':'keyUp','value':'\ue014'}]for _ in range(5)),[])}]});time.sleep(.12)
   g=read('(()=>{let n=document.querySelector('+json.dumps(selector)+'),r=document.createRange();r.selectNodeContents(n);let box=n.getBoundingClientRect(),text=r.getBoundingClientRect();return{selector:'+json.dumps(selector)+',viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,name:n.textContent,scroll:n.scrollLeft,clientWidth:n.clientWidth,scrollWidth:n.scrollWidth,padding:getComputedStyle(n).paddingBottom,bottomClearance:box.bottom-text.bottom,textLines:[...new Set([...r.getClientRects()].map(b=>Math.round(b.top)))].length}})()');out['geometry'].append(g)
   check((g['scrollWidth']<=g['clientWidth'] or g['scroll']>0) and g['textLines']==1 and g['bottomClearance']>=10 and g['pageWidth']<=width,'Scrollbar clearance and scrolling when needed '+selector+' '+str(width),g)
  ev('document.querySelector("#feedback").scrollIntoView({block:"center",behavior:"instant"});true');shot('clearance-'+str(width)+'.png')
 out['javascriptErrors']=js_errors;out['sourceHashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in ['games/name-builder.html','css/namelecule-name-builder.css','js/namelecule-name-builder.js']};out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('clearance-failure.png')
 except Exception:pass
finally:
 out['beforeContextCloseLog']=log_snapshot();started=time.monotonic()
 try:finish()
 except Exception as e:out['contextCloseFailure']=str(e)
 out['contextCloseSeconds']=time.monotonic()-started;time.sleep(.2);out['afterContextCloseLog']=log_snapshot()
 ff.terminate()
 try:ff.wait(timeout=10)
 except subprocess.TimeoutExpired:ff.kill();ff.wait(timeout=5)
 log.close();out['afterOwnedFirefoxStopLog']=log_snapshot();out['onlyOwnedHeadlessStopped']=ff.poll()is not None;out['personalFirefoxControlled']=False
 (HERE/'clearance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'beforeClose':out['beforeContextCloseLog'],'afterClose':out['afterContextCloseLog'],'closeSeconds':out['contextCloseSeconds']},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
