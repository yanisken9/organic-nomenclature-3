"""Bounded Main57 regression: old141 Expanded and new6 all forms at two widths."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'browser-support.py').read_text(),'owned-old-expanded-support','exec'))
import gzip
source_paths=['mulermoc-nom-57.html','js/mulermoc-nom-molview-55.js','js/mulermoc-nom-molview-56.js','js/mulermoc-nom-molview-57.js','js/MULERMOC_namelecule_alkanes_v1_data.js']
out['sourceHashesAtStart']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in source_paths};out['cases']=[];out['failures']=[];out['expected']={'oldExpanded':282,'newAllForms':36};out['chemicalCertification']=False
try:
 call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
 navigate('mulermoc-nom-57.html?audit=old-expanded-alkane-pool');app_ready();ev('document.fonts.ready.then(()=>true)')
 fixtures=read('Object.entries(window.MOL2D).filter(([key,forms])=>typeof forms.expanded==="string"&&forms.expanded.trim()).map(([key])=>key)');check(len(fixtures)==141,'Old library contains141 availableExpanded source forms')
 fixtures=[{'key':key,'mode':'expanded','pool':'old'}for key in fixtures]+[{'key':m['id'],'mode':mode,'pool':'new'}for m in json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text())['molecules']for mode in ['condensed','expanded','skeletal']]
 ev((ROOT/'tools/2d-label-probe.js').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for i,fixture in enumerate(fixtures):
   key,mode=fixture['key'],fixture['mode']
   ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
   if ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'):
    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));owners=read('[...document.querySelectorAll("#jsmeNomeclatureSVG text:not([id^=number])")].map(n=>Number(n.dataset.nameleculeAtom))')
    owner_error=any(not isinstance(n,(int,float))or not float(n).is_integer()or n<1 or n>len(row['atomSymbols'])for n in owners)or len(set(owners))!=len(owners)
    row['passed']=not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount']and not owner_error;row['owners']=owners
   else:row={'key':key,'mode':mode,'renderError':ev('document.getElementById("jsmeNomeclatureSVG").textContent'),'passed':False}
   row['width']=width;row['pool']=fixture['pool'];out['cases'].append(row)
   if not row['passed']:out['failures'].append({'key':key,'mode':mode,'width':width});print('FAIL '+key+' '+str(width),flush=True)
   if (i+1)%30==0:print('OldExpanded raster',width,i+1,'/',len(fixtures),'failures',len(out['failures']),flush=True)
 check(not out['failures'],'All282 oldExpanded +36 newForm raster cases preserve labels/bonds/frame/ownership',out['failures'])
 check(all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in out['sourceHashesAtStart'].items()),'Renderer/bundle source hashes unchanged during oldExpanded audit')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:
 finish('old-expanded');(OUT/'old-expanded.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
if not out['completed']or out['failures']or js_errors:raise SystemExit(1)
