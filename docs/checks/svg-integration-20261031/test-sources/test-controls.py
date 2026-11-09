from pathlib import Path
import os,json,gzip,time,traceback,base64
r=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
out={'cases':[],'exports':[],'alkanes':[],'completed':False}
choices=[('propene','expanded'),('dimethyl_2_3_butane','expanded'),('ethanenitrile','condensed'),('nitroethane','skeletal'),('ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid','expanded'),('ethyl_4_isopropyl_3_methyl_2_hexanal','condensed'),('pentanoic_acid','condensed')]
def measure(width,phase):
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
 row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width,phase=phase,expectedNumbers=ev('numberingFlag?numbersSVGElements.filter(Boolean).length:0'));out['cases'].append(row);assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount'],(row['key'],phase,row['raster'])
 if phase=='numbering':assert len(row['numbers'])==row['expectedNumbers']
 return row
try:
 navigate('main/mulermoc-nom-52.html?audit=2d-controls');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((r/'final-svg-probe.js').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key,mode in choices:
   ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")['+str(['condensed','expanded','skeletal'].index(mode))+'].click();true');measure(width,'selected')
   for target,button in [(0.5,'zoomOutBtn'),(6,'zoomInBtn'),(2,'zoomOutBtn')]:
    if target==2:ev('molZoom2D=2;fReapplyZoomScale2D();true')
    else:ev('for(let i=0;i<16;i++)document.getElementById('+json.dumps(button)+').click();true')
    assert ev('molZoom2D')==target;measure(width,'zoom-'+str(target))
   ev('fClearHighlights();fShowNameAnalysis();document.getElementById("comp5").click();true');until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20);measure(width,'numbering')
   comp=ev('Array.from(document.querySelectorAll(".nameCompBox")).find(e=>["comp1","comp6","comp9"].includes(e.id))?.id||null')
   if comp:ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true');measure(width,'highlight')
   ev('document.getElementById("view2DBtn").click();document.getElementById("view2DBtn").click();fReapplyZoomScale2D();true');measure(width,'hide-show')
   if width==1500 and key in ['propene','pentanoic_acid','ethyl_4_isopropyl_3_methyl_2_hexanal']:screenshot(str(r/(key+'-main.png')))
   print('controls',width,key,'passed',flush=True)
 # Preserve approved alkane ratios and equality of visible horizontal/vertical strokes.
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in ['methane','ethane','propane','butane','pentane','methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
   for zoom in [.5,2,6]:
    ev('selectedMol='+json.dumps(key)+';mode2D="expanded";fInitProps();fLoadMol2D();molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
    row=json.loads(ev('JSON.stringify((()=>{const svg=molSvg.node,first=svg.querySelector("text"),font=parseFloat(getComputedStyle(first).fontSize),lines=[...svg.querySelectorAll("line")];return {key:selectedMol,scale:svg.dataset.alkaneFixedCCScale,font,strokes:lines.map((l,i)=>{const length=Math.hypot(+l.getAttribute("x2")-+l.getAttribute("x1"),+l.getAttribute("y2")-+l.getAttribute("y1")),b=bondList[i],type=b&&allAtomsTypeList[b[0]-1]==="C"&&allAtomsTypeList[b[1]-1]==="C"?"C-C":"C-H";return {type,length,ratio:length/font,visibleRatio:(length-1.04*font)/font}})}})())'));row.update(width=width,zoom=zoom);assert row['scale'];assert all(abs(s['ratio']-(2.6175 if s['type']=='C-C'else 1.30875))<.012 for s in row['strokes']),row
    for kind in ['C-C','C-H']:
     values=[s['visibleRatio']for s in row['strokes']if s['type']==kind]
     if values:assert max(values)-min(values)<.012,row
    out['alkanes'].append(row)
 # Two actual2DPNG exports from contrasting label contexts.
 for key,mode in [('pentanoic_acid','condensed'),('propene','expanded')]:
  ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();fClearHighlights();fShowNameAnalysis();true')
  ev('window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;window.__anchor=HTMLAnchorElement.prototype.click;URL.createObjectURL=function(b){if(b.type==="image/png")window.__png=b;if(b.type.startsWith("image/svg"))b.text().then(t=>window.__exportSvg=t);return __create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById("save2DBtn").click();true');until('!!window.__png&&!!window.__exportSvg',seconds=30)
  data=json.loads(ev('JSON.stringify({key:selectedMol,bytes:__png.size,mime:__png.type,validSVG:!new DOMParser().parseFromString(__exportSvg,"image/svg+xml").querySelector("parsererror")})'));assert data['validSVG']and data['bytes']>1000;out['exports'].append(data)
  raw=ev('new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(",")[1]);f.readAsDataURL(__png)})');(r/(key+'-2d.png')).write_bytes(base64.b64decode(raw));ev('HTMLAnchorElement.prototype.click=__anchor;URL.createObjectURL=__create;true')
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'controls.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('controls',out['completed'],'cases',len(out['cases']),'alkanes',len(out['alkanes']),'errors',len(js_errors),flush=True)
