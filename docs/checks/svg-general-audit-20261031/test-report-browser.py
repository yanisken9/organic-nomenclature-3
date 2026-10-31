from pathlib import Path
import os,json,base64
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
out={}
try:
 navigate('evidence/report.html');ev('document.fonts.ready.then(()=>true)');until('document.querySelectorAll(".drawing svg").length===14')
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 for i in range(12):
  ev('document.querySelectorAll("[data-view]")['+str(i)+'].click();true')
  assert ev('[...document.querySelectorAll(".drawing svg")].every(s=>{let v=s.getAttribute("viewBox").split(/\s+/).map(Number);return v.length===4&&v.every(Number.isFinite)&&v[2]>0&&v[3]>0})')
 ev('cases.forEach((c,i)=>view(i,"focus"));true')
 assert ev('[...document.querySelectorAll(".drawing svg")].every(s=>{const b=s.getBoundingClientRect(),texts=[...s.querySelectorAll("text")];return(s.dataset.focusTargetIDs||"").split(",").filter(Boolean).every(i=>{const t=texts[+i].getBoundingClientRect();return t.left>=b.left-1&&t.right<=b.right+1&&t.top>=b.top-1&&t.bottom<=b.bottom+1})})')
 out.update(figures=14,visualReferences=6,buttonChecks=12,focusTargetsInsideFrames=True,completed=True)
 ev('cases.forEach((c,i)=>view(i,"focus"));true')
 for tag,section in [('overview',0),('residuals',3)]:
  y=ev('Math.max(0,document.getElementById("case'+str(section)+'").getBoundingClientRect().top+scrollY-20)')
  shot=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'document','clip':{'type':'box','x':0,'y':y,'width':1500,'height':1000}})
  (here/('report-'+tag+'.png')).write_bytes(base64.b64decode(shot['data']))
 out['javascriptErrors']=js_errors;assert not js_errors
finally:
 (here/'report-browser.json').write_text(json.dumps(out,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
print(json.dumps(out))
