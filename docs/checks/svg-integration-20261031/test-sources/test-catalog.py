from pathlib import Path
import os,json,gzip,time,traceback,hashlib
r=Path('/tmp/namelecule-svg-integration-20261031');repo=Path.cwd();os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
fixtures=json.loads(gzip.decompress((repo/'docs/checks/svg-general-audit-20261031/fixtures.json.gz').read_bytes()));out={'cases':[],'completed':False,'sourceSHA256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in ['mulermoc-nom-52.html','js/mulermoc-nom-molview-52.js','js/namelecule-label-metrics.js','js/vendor/jsme/namelecule-20261031-r1/FEB169D74546A3B279D22AE09AFB86BD.cache.js']}}
try:
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});navigate('main/mulermoc-nom-52.html?audit=integrated-catalog');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((r/'final-svg-probe.js').read_text())
  for i,f in enumerate(fixtures):
   first=len(js_errors);ev('selectedMol='+json.dumps(f['key'])+';mode2D='+json.dumps(f['mode'])+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
   if ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'):
    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row['owners']=json.loads(ev('JSON.stringify([...document.querySelectorAll("#jsmeNomeclatureSVG text[data-namelecule-atom]")].map(n=>({owner:n.dataset.nameleculeAtom,text:n.textContent})))'))
   else:row={'key':f['key'],'mode':f['mode'],'renderError':ev('document.getElementById("jsmeNomeclatureSVG").textContent')}
   row.update(width=width,expectedKey=f['key'],expectedMode=f['mode'],javascriptErrorCount=len(js_errors)-first);out['cases'].append(row)
   if (i+1)%30==0:print(width,i+1,'errors',sum('renderError'in x for x in out['cases']),'contacts',sum(bool(x.get('raster',{}).get('inkWithinHalfCssPixelOfBond'))for x in out['cases']),'hidden',sum(bool(x.get('raster',{}).get('fullyHiddenLineCount'))for x in out['cases']),flush=True)
   if (i+1)%100==0:(r/'catalog-progress.json.gz').write_bytes(gzip.compress(json.dumps(out).encode(),mtime=0))
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'catalog.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('catalog complete',out['completed'],'cases',len(out['cases']),'JS',len(js_errors),flush=True)
