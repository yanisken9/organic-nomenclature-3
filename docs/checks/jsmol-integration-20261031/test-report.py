from pathlib import Path
import os,json,urllib.request,hashlib,time
root=Path('/tmp/namelecule-jsmol-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8030/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
out={'viewports':[],'userServer':None}
try:
 for w,h in [(1500,1000),(390,844)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1});navigate('main/docs/checks/jsmol-integration-20261031/report.html');ev('document.fonts.ready.then(()=>true)');ev('Promise.all([...document.images].map(i=>{i.loading="eager";return i.decode()})).then(()=>true)')
  v=json.loads(ev('JSON.stringify({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,images:[...document.images].map(i=>({src:i.src,width:i.naturalWidth,height:i.naturalHeight}))})'));assert v['scrollWidth']<=w and all(i['width']>0 for i in v['images']);out['viewports'].append(v)
  if w==1500:screenshot(str(root/'report-overview.png'))
 # Read-only check of the existing user server; do not alter its process/profile.
 try:
  base='http://127.0.0.1:8013/';p=Path('mulermoc-nom-52.html');html=urllib.request.urlopen(base+p.name,timeout=5).read();asset='js/vendor/jsmol/namelecule-20261031-r1/JSmol.min.js';data=urllib.request.urlopen(base+asset,timeout=5).read();out['userServer']={'HTMLMatchesWorkingTree':html==p.read_bytes(),'bundleSHA256':hashlib.sha256(data).hexdigest()};assert out['userServer']['HTMLMatchesWorkingTree'] and out['userServer']['bundleSHA256']=='d99b1168acbbd55d59073943e6fde174513e8b815ddb88ae8f1bfa927961b323'
 except Exception as e:out['userServer']={'failure':str(e)}
finally:
 out['javascriptErrors']=js_errors;(root/'report-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print(out)
