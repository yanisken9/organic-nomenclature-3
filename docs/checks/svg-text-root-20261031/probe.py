from pathlib import Path
import os,json,time,traceback
root=Path('/tmp/namelecule-svg-root-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8024/'
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
raw=json.loads((root/'propene.json').read_text())['annotated'];result={'cases':[]}
measure=r'''(()=>{const svg=document.querySelector('#export svg'),texts=[...svg.querySelectorAll('text')],t=texts.find(t=>t.textContent==='C'),r=t.previousElementSibling,s=getComputedStyle(t),c=document.createElement('canvas').getContext('2d');c.font=`${s.fontStyle} ${s.fontWeight} ${parseFloat(s.fontSize)}px ${s.fontFamily}`;const ink=c.measureText('C'),font=a.g?.b?.F;return{fontSize:a.g?.b?.I??null,bodyFont:getComputedStyle(document.body).font,bodyLineHeight:getComputedStyle(document.body).lineHeight,cssFont:s.font,rect:{...Object.fromEntries([...r.attributes].map(v=>[v.name,v.value]))},text:{...Object.fromEntries([...t.attributes].map(v=>[v.name,v.value]))},glyphAscent:ink.actualBoundingBoxAscent,glyphDescent:ink.actualBoundingBoxDescent,maskAscent:+t.getAttribute('y')-(+r.getAttribute('y')),apiKeys:Object.keys(a).slice(0,10),metrics:font?.tS?.(),metricsFont:font?.a?{name:font.a.a,size:font.a.b,style:font.a.c}:null,resources:performance.getEntriesByType('resource').filter(v=>v.name.includes('.cache.js')).map(v=>v.name),svg:svg.outerHTML}})()'''
try:
 for case in ['plain','local','upstream','local&lineheight=normal','local&lineheight=1','plain&lineheight=2']:
  navigate('minimal.html?css='+case);until('window.loaded===true');ev('document.fonts.ready.then(()=>true)')
  ev('a.setMolecularAreaLineWidth(.6);a.setMolecularAreaScale(2);a.readMolFile('+json.dumps(raw)+');true')
  for font in ([9,10,11,12]if case in ['plain','local','upstream']else[9]):
   ev('a.setAtomMolecularAreaFontSize('+str(font)+');document.getElementById("export").innerHTML=a.getMolecularAreaGraphicsString();true')
   r=json.loads(ev('JSON.stringify('+measure+')'));r['case']=case;result['cases'].append(r)
   print(case,font,'metrics',r['metrics'],'maskAscent',r['maskAscent'],'inkAscent',r['glyphAscent'],'maskH',r['rect']['height'],flush=True)
  if case=='plain':screenshot(str(root/'plain.png'))
 result['completed']=True
except Exception as e:result['failure']=str(e);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors;(root/'probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
if not result.get('completed'):raise SystemExit(1)
