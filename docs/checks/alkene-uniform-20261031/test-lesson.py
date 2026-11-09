"""Replay every active alkene lesson step with actual presentation navigation."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path(__file__).resolve().parents[3];TMP=Path('/tmp/namelecule-alkene-uniform-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8032/main/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
lesson='scenarios/alkenes-nomenclature-branches.scenario.json';data=json.loads((ROOT/lesson).read_text());out={'steps':[],'completed':False}
def measure(width,index,phase):
 until('selectedMol==='+json.dumps(data['steps'][index]['selectedMol'])+'&&mode2D==='+json.dumps(data['steps'][index]['mode2D']))
 until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
 assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
 row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row.update(width=width,step=index+1,phase=phase)
 assert not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']
 if data['steps'][index]['mode2D']=='expanded':assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')
 out['steps'].append(row)
try:
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});navigate('mulermoc-nom-52.html?scenario='+lesson+'&present=1&from=theory-library&v=alkene-uniform')
  until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
  for index in range(len(data['steps'])):
   if index:
    ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index))
   measure(width,index,'forward')
   if data['steps'][index]['mode2D']=='expanded':
    before=ev('molSvg.node.outerHTML');ev('document.getElementById("scPrev").click();true');until('fScenarioPresent().index==='+str(index-1));measure(width,index-1,'backward')
    ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index));measure(width,index,'replay')
    # Highlights may serialize in a different order; geometry/mapping must agree.
    if width==1500:screenshot(TMP/'lesson-expanded-after.png')
  until('typeof mainChainPool3DKey!=="undefined"&&mainChainPool3DKey===selectedMol');out.setdefault('terminalModels',[]).append({'width':width,'key':ev('mainChainPool3DKey')})
  ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("design/theory-library.html")');out.setdefault('exits',[]).append(width)
  print('lesson',width,'passed',flush=True)
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(TMP/'lesson.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'states':len(out['steps']),'errors':len(js_errors)}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
