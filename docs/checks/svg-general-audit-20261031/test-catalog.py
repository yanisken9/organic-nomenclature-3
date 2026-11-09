"""Whole final application catalog, unmodified viewer, baseline vs isolated vendor.
Artifacts only /tmp. Does not assert a clean verdict; records failures for triage.
"""
from pathlib import Path
import os,json,time,gzip,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
fixtures=json.loads((root/'fixtures.json').read_text());out={'cases':[],'phases':[],'completed':False}
try:
 for version,width in [('baseline',1500),('candidate',1500),('candidate',390)]:
  before=len(js_errors);call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  navigate('app-'+version+'/mulermoc-nom-52.html?audit=whole-catalog');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((here/'final-svg-probe.js').read_text())
  for i,f in enumerate(fixtures):
   first=len(js_errors)
   ev('selectedMol='+json.dumps(f['key'])+';mode2D='+json.dumps(f['mode'])+';fInitProps();fLoadMol2D();fShowNameAnalysis();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
   row=json.loads(ev('auditFinalSvg().then(r=>JSON.stringify(r))'));row.update(version=version,width=width,expectedKey=f['key'],expectedMode=f['mode'],javascriptErrorCount=len(js_errors)-first)
   out['cases'].append(row)
   if (i+1)%30==0:print(version,width,i+1,'/',len(fixtures),flush=True)
   if (i+1)%100==0:(root/'catalog-progress.json.gz').write_bytes(gzip.compress(json.dumps(out).encode(),mtime=0))
  out['phases'].append({'version':version,'width':width,'javascriptErrorCount':len(js_errors)-before,'resources':json.loads(ev('JSON.stringify(performance.getEntriesByType("resource").filter(v=>v.name.includes(".cache.js")).map(v=>v.name))'))})
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'catalog.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('completed',out['completed'],'cases',len(out['cases']),'errors',len(js_errors),flush=True)
