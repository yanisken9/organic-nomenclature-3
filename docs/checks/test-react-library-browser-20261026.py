"""Actual Firefox lesson checks. Artifacts only under /tmp; requires localhost8013/BiDi9237."""
import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9237),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9237\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
b=b''
while b'\r\n\r\n' not in b:b+=s.recv(1)
assert b'101' in b,b
seq=0;js_errors=[]
def exact(n):
 b=b''
 while len(b)<n:
  part=s.recv(n-len(b))
  if not part:raise RuntimeError('WebSocket closed')
  b+=part
 return b
def call(method,params):
 global seq
 seq+=1;payload=json.dumps({'id':seq,'method':method,'params':params}).encode();mask=os.urandom(4);n=len(payload)
 header=bytes([129,128|n]) if n<126 else (bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n))
 s.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(payload)))
 while True:
  h=exact(2);n=h[1]&127
  if n==126:n=struct.unpack('!H',exact(2))[0]
  elif n==127:n=struct.unpack('!Q',exact(8))[0]
  msg=json.loads(exact(n))
  if msg.get('method')=='log.entryAdded':
   item=msg.get('params',{})
   if item.get('level')=='error' and item.get('type')=='javascript':js_errors.append(item)
  if msg.get('id')==seq:
   if msg.get('type')=='error':raise RuntimeError(msg)
   return msg['result']
call('session.new',{'capabilities':{}})
ctx=call('browsingContext.create',{'type':'tab'})['context']
call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
def ev(expr):
 result=call('script.evaluate',{'expression':expr,'target':{'context':ctx},'awaitPromise':True})
 if result.get('type')=='exception':raise RuntimeError(result.get('exceptionDetails'))
 return result['result'].get('value')
def navigate(path):
 call('browsingContext.navigate',{'context':ctx,'url':os.environ.get('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8013/')+path,'wait':'complete'})
def until(expr,seconds=90):
 for _ in range(seconds*2):
  if ev(expr):return
  time.sleep(.5)
 raise AssertionError('Timed out: '+expr)
def app_ready():
 until("typeof jsmeNomeclatureApplet!=='undefined' && !!jsmeNomeclatureApplet && !!nameExamples.methyl_3_butene_1.classification")
def screenshot(path):
 result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'document'});Path(path).write_bytes(base64.b64decode(result['data']))


result={'completed':False};preview='react-preview/dist/'
def shot(name):
 data=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'})['data']
 Path('/tmp/react-library-'+name+'-20261026.png').write_bytes(base64.b64decode(data))
def query(value):
 ev("(()=>{const x=document.getElementById('lesson-search');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(x,"+json.dumps(value)+");x.dispatchEvent(new Event('input',{bubbles:true}));})()")
def category(value):
 ev("(()=>{const x=document.getElementById('lesson-category');x.value="+json.dumps(value)+";x.dispatchEvent(new Event('change',{bubbles:true}));})()")
def count(cards,lessons):
 until("document.querySelectorAll('article.lesson').length==="+str(cards)+" && document.querySelectorAll('a[href*=scenario]').length==="+str(lessons))
def clear():
 ev("document.querySelector('.catalog-clear').click()")
 count(9,12)
 assert ev("document.activeElement.id==='lesson-search'")
try:
 navigate(preview)
 until("!!document.querySelector('.hero h1')")
 ev("Promise.all([...document.images].map(i=>i.decode()))")
 ev("document.querySelector('[data-panel=login]').click()")
 until("!!document.querySelector('dialog[open]')")
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':'\ue00c'},{'type':'keyUp','value':'\ue00c'}]}]})
 until("!document.querySelector('dialog')")
 ev("document.querySelector('a[href=\"#/library\"]').click()")
 count(9,12)
 assert ev("document.querySelectorAll('#lesson-category option').length===10")
 parity=json.loads(ev("""(async()=>{
 const original=new DOMParser().parseFromString(await(await fetch('../../design/theory-library.html')).text(),'text/html');
 const norm=x=>x.textContent.replace(/\s+/g,' ').trim();
 const fields=(el,selector)=>[...el.querySelectorAll(selector)].map(norm);
 const old=[...original.querySelectorAll('article.lesson')],now=[...document.querySelectorAll('article.lesson')];
 const semanticParity=old.every((a,i)=>{
  const b=now[i];
  const descriptions=el=>[...el.querySelectorAll('.content > p,.lesson-part > p')].filter(p=>!p.classList.contains('series-formula')&&!p.querySelector('.count')).map(norm);
  return norm(a.querySelector('.illustration .formula'))===norm(b.querySelector('.illustration .formula'))
   &&JSON.stringify(fields(a,'.content h2,.content h3'))===JSON.stringify(fields(b,'.content h3'))
   &&JSON.stringify(descriptions(a))===JSON.stringify(descriptions(b))
   &&JSON.stringify(fields(a,'.series-formula'))===JSON.stringify(fields(b,'.series-formula'))
   &&JSON.stringify(fields(a,'.topics li'))===JSON.stringify(fields(b,'.topics li'))
   &&JSON.stringify(fields(a,'.count'))===JSON.stringify(fields(b,'.count'));
 });
 const links=[...original.querySelectorAll('a[href*=scenario]')].map(a=>new URL(a.getAttribute('href'),new URL('../../design/theory-library.html',location.href)).href);
 return JSON.stringify({semanticParity,linksParity:links.every((href,i)=>href===document.querySelectorAll('a[href*=scenario]')[i].href),cards:old.length,lessons:links.length});
 })()"""))
 assert parity['semanticParity'] and parity['linksParity'],parity
 result['sourceParity']=parity
 assert ev("document.querySelector('[role=status]').textContent.includes('12 μαθήματα')")
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 shot('desktop-all')
 for ident,cards,lessons in [('alkanes',1,1),('alkenes',1,1),('alkynes',1,1),('alkadienes',1,1),('enynes',1,1),('alcohols',1,2),('monoethers',1,1),('aldehydes',1,2),('ketones',1,2)]:
  category(ident);count(cards,lessons)
 clear()
 for value,cards,lessons in [('ΑΛΚΟΟΛΕΣ',1,2),('αλδευδεσ',1,2),('άλλες',3,3),('κορεσμενες',3,3),('αλφαβητικη σειρα',6,6)]:
  query(value);count(cards,lessons)
 clear();query('αλλες');count(3,3);category('ketones');count(1,1)
 assert ev("document.querySelector('a[href*=scenario]').href.includes('other-ketones')")
 assert ev("document.querySelector('.illustration .count').textContent==='1 από 2 μαθήματα'")
 assert ev("document.querySelector('[role=status]').textContent.includes('1 μάθημα σε 1 κατηγορία')")
 shot('desktop-filtered')
 ev("document.querySelector('a.back').click()")
 until("!!document.querySelector('.hero h1')")
 ev("document.querySelector('a[href=\"#/library\"]').click()")
 count(1,1)
 assert ev("document.getElementById('lesson-search').value==='αλλες' && document.getElementById('lesson-category').value==='ketones'")
 call('browsingContext.reload',{'context':ctx,'wait':'complete'})
 count(9,12)
 assert ev("document.getElementById('lesson-search').value==='' && document.getElementById('lesson-category').value===''")
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 shot('mobile-all')
 query('αλλες');category('ketones');count(1,1)
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 shot('mobile-filtered')
 query('αλκοολες');count(0,0)
 assert ev("document.querySelector('.catalog-empty').textContent.includes('Δεν βρέθηκαν')")
 assert ev("document.querySelector('[role=status]').textContent.includes('0 μαθήματα')")
 shot('mobile-empty')
 clear();query('<script>alert(1)</script>');count(0,0)
 assert ev("!document.querySelector('main script')")
 clear();query('αλκυλια');count(6,6)
 href=ev('location.href')
 ev("document.querySelector('form[role=search]').requestSubmit()")
 assert ev('location.href')==href
 clear()
 assert ev("document.querySelector('.catalog-clear').disabled")
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 result['previewConsoleErrors']=list(js_errors);assert not js_errors,js_errors
 category('ketones');count(1,2);query('αλλες');count(1,1)
 ev("document.querySelector('a[href*=other-ketones-nomenclature]').click()")
 until("typeof fScenarioPresent==='function' && fScenarioPresent().steps.length===28 && !document.documentElement.classList.contains('lesson-loading')")
 app_ready();assert ev("Object.keys(nameExamples).length===126")
 ev("document.getElementById('scNext').click()")
 until('fScenarioPresent().index===1')
 ev("document.getElementById('scExit').click()")
 until("location.pathname.endsWith('/design/theory-library.html')")
 known=[e for e in js_errors if 'this.viewer is null' in e.get('text','') and any('chemapps.stolaf.edu' in f.get('url','') for f in e.get('stackTrace',{}).get('callFrames',[]))]
 unexpected=[e for e in js_errors if e not in known]
 result['consoleCategories']={'previewErrors':len(result['previewConsoleErrors']),'knownLegacyJSmolErrors':len(known),'unexpected':len(unexpected)}
 assert not unexpected,unexpected
 result.update(completed=True,categoriesChecked=9,greekSearch=True,combinedFilters=True,partialDualCard=True,resultCounts=True,emptyAndClearFocus=True,desktopAndMobile=True,queryAsText=True,submitDoesNotNavigate=True,filtersSurviveInternalNavigation=True,reloadResetsFilters=True,legacyLessonEntryNextExit=True,molecules=126,dialogEscapeRegression=True)
 print('PASS structured React library: source parity,9category filters,Greek search/combinations/empty/clear/history/mobile and legacy lesson smoke')
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/react-library-browser-20261026.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
