from pathlib import Path
import runpy,json,base64,urllib.request,hashlib,sys
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;R=H.parents[2]
d=runpy.run_path(str(H/'browser/driver.py'));call=d['call'];read=d['read'];wait=d['wait'];ctx=d['ctx'];result={}
try:
 url=json.loads((H/'preview-server.json').read_text())['baseURL']+'docs/checks/builder-lesson-header-20261111/comparison.html'
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 call('browsingContext.navigate',{'context':ctx,'url':url,'wait':'complete'})
 wait('document.images.length===3&&[...document.images].every(i=>i.complete&&i.naturalWidth===1500&&i.naturalHeight===1000)')
 result['desktop']=read('({viewport:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,cards:[...document.querySelectorAll("article")].map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y})),headings:[...document.querySelectorAll("article h2")].map(e=>e.textContent),links:[...document.querySelectorAll(".large")].map(e=>e.href)})')
 assert not result['desktop']['overflow'];assert len({e['y']for e in result['desktop']['cards']})==1;assert len(result['desktop']['links'])==3
 image=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/'comparison-desktop.png').write_bytes(base64.b64decode(image['data']))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 result['mobile']=read('({overflow:document.documentElement.scrollWidth>innerWidth,cards:[...document.querySelectorAll("article")].map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y}))})')
 assert not result['mobile']['overflow'];assert len({e['x']for e in result['mobile']['cards']})==1
 image=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(H/'comparison-mobile.png').write_bytes(base64.b64decode(image['data']))
 result['imageHTTP']=[]
 for link in result['desktop']['links']:
  with urllib.request.urlopen(link,timeout=15)as response:
   data=response.read();assert response.status==200;result['imageHTTP'].append({'url':link,'HTTP':200,'sha256':hashlib.sha256(data).hexdigest()})
 result.update(passed=True,URL=url,scope='Developer actual ownedFirefox; comparisondesktop/mobileimage-loading/layout/nativeimageURLchecks.')
finally:
 (H/'comparison-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');d['finish']()
print(json.dumps(result,ensure_ascii=False))
