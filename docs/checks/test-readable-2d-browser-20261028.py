"""Main readable 22px target with adaptive fitting: actual SVG bounds, controls and lessons.
Reuses the existing Firefox BiDi harness. Writes artifacts only under /tmp.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0], 'existing-firefox-bidi-harness', 'exec'))
import hashlib
folder=Path('/tmp/namelecule-readable-2d-20261028');folder.mkdir(exist_ok=True)
result={'completed':False,'cases':[],'checks':[],'lessons':[]}
def geometry():
 return json.loads(ev("""JSON.stringify((()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),o=s.getBoundingClientRect(),labels=[...s.querySelectorAll('text:not([id^=number])')];return {key:selectedMol,mode:mode2D,zoom:molZoom2D,target:Number(s.dataset.uniformAtomFontPixels),viewport:[o.width,o.height],fonts:labels.filter(e=>/[CHO]/.test(e.textContent)).map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)}),clipped:[...s.querySelectorAll('line,text,path')].filter(e=>!e.closest('defs')).filter(e=>{const b=e.getBoundingClientRect();return b.left<o.left-1||b.right>o.right+1||b.top<o.top-1||b.bottom>o.bottom+1}).map(e=>e.textContent||e.tagName)}})())"""))
def drain_numbering():
 ev('clearInterval(myNumberingTimeout);currNumberEl=0;true')
try:
 navigate('mulermoc-nom-52.html?v=readable-2d-final');app_ready();until('window.JSmolReadyFlag===true')
 ev('document.fonts.ready.then(()=>true)');time.sleep(.6)
 assert ev("document.documentElement.getAttribute('data-namelecule-2d-font-size')==='22'")
 result['initial']=geometry();assert result['initial']['key']=='methane'
 assert abs(result['initial']['fonts'][0]-22)<.02
 screenshot(str(folder/'startup-desktop.png'))
 # Compare the prior Main factor policy without changing zoom or molecular data.
 ev("document.documentElement.removeAttribute('data-namelecule-2d-font-size');document.documentElement.setAttribute('data-namelecule-2d-scale','1.15');fUpdateSVG();true")
 old=geometry();ev("document.documentElement.removeAttribute('data-namelecule-2d-scale');document.documentElement.setAttribute('data-namelecule-2d-font-size','22');fUpdateSVG();true")
 assert old['fonts'][0]<result['initial']['fonts'][0]
 result['priorMain']=old;result['checks'].append('Startup methane 22px; prior page-factor policy remains available')
 for width in [1500,900,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.6)
  raw=ev("""(()=>{const rows=[];for(const key of Object.keys(window.MOL2D)){for(const mode of ['condensed','expanded','skeletal']){if(!window.MOL2D[key][mode])continue;selectedMol=key;mode2D=mode;nameAnalysisMode='none';numberingFlag=false;molZoom2D=MOL_ZOOM_DEFAULT;fInitNamingProps();fLoadMol2D();const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text:not([id^=number])')];const fonts=labels.filter(e=>/[CHO]/.test(e.textContent)).map(e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b));const unclipped=els=>els.filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent||e.tagName);const clipped=unclipped([...svg.querySelectorAll('line,text,path')].filter(e=>!e.closest('defs')));const original3D=fShowNumber3D;fShowNumber3D=()=>{};try{numberingFlag=true;currNumberEl=0;fShowNumbering(0)}finally{fShowNumber3D=original3D}rows.push({key,mode,fonts,target:Number(svg.dataset.uniformAtomFontPixels),clipped,numberClipped:unclipped([...svg.querySelectorAll('text[id^=number]')]),numberCount:svg.querySelectorAll('text[id^=number]').length,viewport:[outer.width,outer.height],name:currentMolName})}}return JSON.stringify(rows)})()""")
  items=json.loads(raw);assert len(items)==377 and len({r['key'] for r in items})==126
  for row in items:
   assert not row['clipped'] and not row['numberClipped'],(width,row)
   assert row['numberCount']>0,(width,row)
   assert all(0<f<=row['target']+.02 for f in row['fonts']),(width,row)
   if row['fonts']:assert max(row['fonts'])-min(row['fonts'])<.02,(width,row)
  fonts=[f for r in items for f in r['fonts']];assert max(fonts)<=22.02
  prior=json.loads(Path('docs/checks/main-2d-scale-browser-20261027.json').read_text())
  reference={(r['key'],r['mode']):r for r in prior['cases'] if r['width']==width}
  for row in items:
   before=reference[(row['key'],row['mode'])]
   assert len(row['fonts'])==len(before['fonts'])
   assert all(a>=b-.02 for a,b in zip(row['fonts'],before['fonts'])),(width,row['key'],row['mode'])
  result['cases'].extend([dict(width=width,**r) for r in items])
  print('PASS',width,'377 forms, fonts',min(fonts),max(fonts),'no clipping',flush=True)
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});time.sleep(.6)
 ev("numberingFlag=false;mode2D='condensed';selectedMol='ethyl_isopropyl_ether';fSelectMol();true")
 until("mainChainPool3DKey==='ethyl_isopropyl_ether'")
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click()')
  assert ev('mode2D')==mode and not geometry()['clipped']
 # A small condensed molecule has room to zoom: real controls must still work.
 ev("selectedMol='methane';mode2D='condensed';fSelectMol();true")
 before=geometry();ev('document.getElementById("zoomInBtn").click()');after=geometry()
 assert abs(after['fonts'][0]/before['fonts'][0]-1.25)<.01
 ev('document.getElementById("zoomOutBtn").click()');assert abs(geometry()['fonts'][0]-before['fonts'][0])<.02
 result['checks'].append('Actual three form radios and zoom +/-')
 # Intercept only the test download, preserving the real PNG encoder/export path.
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;window.__click=HTMLAnchorElement.prototype.click;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click()")
 until('!!window.__png && !!window.__exportSvg')
 assert ev("window.__png.size>1000 && !new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelector('parsererror')")
 assert ev("window.__png.arrayBuffer().then(b=>JSON.stringify([...new Uint8Array(b).slice(0,8)])==='[137,80,78,71,13,10,26,10]')")
 ev('URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click;true')
 result['checks'].append('Native 2D PNG generated and SVG export parses')
 # Snapshot a maximum-height expanded structure with numbering.
 ev("selectedMol='isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5';mode2D='expanded';fSelectMol();numberingFlag=true;currNumberEl=0;fShowNumbering(0);true")
 assert not geometry()['clipped'];screenshot(str(folder/'large-expanded-numbered-desktop.png'));drain_numbering()
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':1000},'devicePixelRatio':1});time.sleep(.6)
 ev("document.getElementById('rotatePromptDismiss').click();true")
 assert not geometry()['clipped'];screenshot(str(folder/'large-expanded-numbered-mobile.png'));drain_numbering()
 # Existing stored lesson zoom values and 2D modes are authoritative; JSON untouched.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 for scenario in ['scenarios/alkanes-nomenclature-branches.scenario.json','scenarios/other-ketones-nomenclature.scenario.json']:
  navigate('mulermoc-nom-52.html?scenario='+scenario+'&present=1#step=1')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();source=json.loads(Path(scenario).read_text());steps=source['steps']
  for index in [0,len(steps)-1]:
   ev('fScenarioGo('+str(index)+')');until('fScenarioPresent().index==='+str(index)+' && selectedMol==='+json.dumps(steps[index]['selectedMol']))
   time.sleep(.25);st=steps[index]
   assert ev('molZoom2D')==st.get('style2D',{}).get('zoom',2)
   assert ev('mode2D')==st['mode2D'];assert not geometry()['clipped']
   result['lessons'].append({'scenario':scenario,'step':index+1,'zoom':ev('molZoom2D'),'mode':ev('mode2D')})
 # Generated React host stays opt-out and keeps the old font policy.
 navigate('react-preview/public/viewer-host.html?v=readable-2d-regression');app_ready()
 assert ev("!document.documentElement.hasAttribute('data-namelecule-2d-font-size') && !document.documentElement.hasAttribute('data-namelecule-2d-scale')")
 ev("selectedMol='ethane';mode2D='condensed';fSelectMol();true");embedded=geometry()
 beforeSource=Path('/tmp/namelecule-readable-2d-20261028/before/js/mulermoc-nom-molview-52.js').read_text()
 oldFit='function fFit2DSVG() {'+beforeSource.split('function fFit2DSVG() {',1)[1].split('// JSME labels collinear',1)[0].strip()
 ev('fFit2DSVG=eval('+json.dumps('('+oldFit+')')+');fUpdateSVG();true')
 reference=geometry();assert abs(embedded['fonts'][0]-reference['fonts'][0])<.001
 result['embeddedHost']=embedded;result['checks'].append('Saved React host opt-out matches prior fit formula')
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 known={e['text'] for e in json.loads(Path('docs/checks/main-2d-scale-existing-jsmol-20261027.json').read_text())['javascriptErrors']}
 unexpected=[e for e in js_errors if e.get('text') not in known or not any('chemapps.stolaf.edu/jmol/jsmol/' in f.get('url','') for f in e.get('stackTrace',{}).get('callFrames',[]))]
 result['unexpectedJavascriptErrors']=unexpected
 Path('/tmp/readable-2d-browser-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'checks':result['checks'],'lessons':len(result['lessons']),'javascriptErrors':len(js_errors)}),flush=True)
 assert not unexpected,unexpected
