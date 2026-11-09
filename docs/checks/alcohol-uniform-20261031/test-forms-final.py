"""Actual forms, representative unchanged categories and 3D visibility check."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
key='isopropyl_4_dimethyl_3_5_heptanol_2';out={'cases':[],'completed':False,'interactionMethod':'Actualmoleculeandmodeclicks;checkedradioindex;awaitcorresponding3Dkeyandlargest39atoms'}
prior=json.load(gzip.open(HERE/'after-16.json.gz','rt'))['cases']
def selectUI(k,mode):
 index=['condensed','expanded','skeletal'].index(mode)
 ev('document.getElementById('+json.dumps(k)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 until('selectedMol==='+json.dumps(k)+'&&mode2D==='+json.dumps(mode))
 until('mainChainPool3DKey==='+json.dumps(k))
 assert ev('[...document.querySelectorAll("#radio2DMode .mode2DOption")].findIndex(n=>n.classList.contains("selectedRadio"))')==index
 if k==key:until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===39',seconds=30)

try:
 navigate('mulermoc-nom-52.html?audit=alcohol-final-forms');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for mode in ['condensed','expanded','skeletal']:
   selectUI(key,mode)
   row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width)
   assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']
   old=next(c for c in prior if c['key']==key and c['mode']==mode and c['width']==width)
   assert all(row[k]==old[k]for k in ['name','atomSymbols','bondGraph'])
   if mode=='expanded':
    assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')
    if width==1500:screenshot(HERE/'largest-applied-expanded.png')
   out['cases'].append(row)
 for k in ['methane','propene','propyne','butadiene_1_2','penten_3_yne_1']:
  selectUI(k,'expanded')
  row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=390)
  assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount'];out['cases'].append(row)
 ev('document.getElementById('+json.dumps(key)+').click();true');until('mainChainPool3DKey==='+json.dumps(key));assert ev('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))')==39
 before=ev('document.getElementById("view3DBtn").classList.contains("active")');ev('document.getElementById("view3DBtn").click();true');assert ev('document.getElementById("view3DBtn").classList.contains("active")')!=before
 ev('document.getElementById("view3DBtn").click();true');assert ev('document.getElementById("view3DBtn").classList.contains("active")')==before
 out['3Dtoggle']={'key':key,'atomCount':39,'restoredVisibility':True};out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(HERE/'forms-final.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'cases':len(out['cases']),'errors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
