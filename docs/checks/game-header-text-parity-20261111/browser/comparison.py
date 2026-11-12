"""Read actual comparison page in owned headless Firefox and verify its linked assets."""
from pathlib import Path
exec((Path(__file__).with_name('driver.py')).read_text())
import urllib.request,hashlib
RESULT={'checks':[],'layouts':[],'http':[]}
def check(ok,label,detail=None):
 RESULT['checks'].append({'label':label,'passed':bool(ok),'detail':detail})
 assert ok,(label,detail)
try:
 open_page('docs/checks/game-header-text-parity-20261111/comparison.html');wait('document.querySelectorAll(".capture img").length===2&&[...document.querySelectorAll(".capture img")].every(e=>e.complete&&e.naturalWidth===1500&&e.naturalHeight===1000)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
  d=read('(()=>{let a=[...document.querySelectorAll("article")].map(e=>{let r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}});return{width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,articles:a,images:[...document.querySelectorAll(".capture img")].map(e=>({src:e.currentSrc,width:e.naturalWidth,height:e.naturalHeight})),fullLinks:[...document.querySelectorAll(".large")].map(e=>({href:e.href,target:e.target,rel:e.rel,tag:e.tagName})),lesson:document.querySelector(".lesson").href}})()')
  RESULT['layouts'].append(d);check(not d['overflow'],'Comparison no horizontal overflow '+str(width),d)
  a,b=d['articles'];check((abs(a['y']-b['y'])<1 and b['x']>a['x']) if width==1500 else (abs(a['x']-b['x'])<1 and b['y']>=a['y']+a['height']),'Comparison '+('two desktop columns' if width==1500 else 'one mobile column'),d['articles'])
  check(len(d['fullLinks'])==2 and all(e['tag']=='A' and e['target']=='_blank' and 'noopener'in e['rel'] for e in d['fullLinks']),'Two native full-image links '+str(width),d['fullLinks'])
  if width==1500:shot('comparison-desktop.png')
  else:
   r=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'document'});(HERE/'comparison-mobile.png').write_bytes(base64.b64decode(r['data']))
 for url in [PROCESS['baseURL']+'docs/checks/game-header-text-parity-20261111/comparison.html']+[e['href'] for e in RESULT['layouts'][0]['fullLinks']]+[RESULT['layouts'][0]['lesson']]:
  with urllib.request.urlopen(url,timeout=20) as response:
   body=response.read();item={'url':url,'status':response.status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()};RESULT['http'].append(item);check(response.status==200,'Comparison asset/lesson HTTP200',item)
 RESULT['passed']=True
except Exception as e:
 RESULT['passed']=False;RESULT['failure']=repr(e);RESULT['traceback']=traceback.format_exc();shot('comparison-failure.png');raise
finally:
 RESULT['jsExceptions']=js_errors;(HERE/'comparison-results.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+'\n');finish()
