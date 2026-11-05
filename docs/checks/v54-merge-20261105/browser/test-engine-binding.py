"""Real browser SHA/Blob/Worker checks: old mismatch, immutable compatibility and new core fallback."""
from pathlib import Path
import json,time,traceback,hashlib
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
PROOF=Path('/Users/yannisskendros/Desktop/Διπλωματική - Ονοματολογία/organic-nomenclature-3/docs/checks/v54-merge-20261105')
OLD='3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306'
NEW=hashlib.sha256(Path('js/mulermoc-nom-core-54.js').read_bytes()).hexdigest()
def api(source):
 ev('(new Function("document",'+json.dumps(source)+'))({currentScript:{src:"http://127.0.0.1:8056/js/namelecule-chemistry-client.js?v=real-binding"},baseURI:document.baseURI});true')
try:
 navigate('games/name-repair.html');until('!!window.NameleculeRepairGame');call('browsingContext.activate',{'context':ctx})
 api((PROOF/'before-extension/js/namelecule-chemistry-client.js').read_text())
 failure=ev('NameleculeChemistryClient.verifyEngine('+json.dumps(OLD)+').then(()=>"unexpected-success",e=>e.code)')
 check(failure=='ENGINE_VERSION_MISMATCH','Original client reproduces old quiz pin/new main engine mismatch',failure)
 api(Path('js/namelecule-chemistry-client.js').read_text())
 check(ev('NameleculeChemistryClient.verifyEngine('+json.dumps(OLD)+')')==OLD,'Immutable old engine passes actual WebCrypto SHA check')
 check(ev('NameleculeChemistryClient.verifyEngine('+json.dumps(NEW)+')')==NEW,'Current merged engine passes404fallback and actual SHA check')
 ev('window.__bindingCatalog='+Path('games/data/alkane-structures.json').read_text()+';true')
 results=[]
 for engine in [OLD,NEW]:
  data=json.loads(ev('Promise.all(__bindingCatalog.molecules.map(m=>NameleculeChemistryClient.analyze(m,{engineSHA256:'+json.dumps(engine)+'}))).then(r=>JSON.stringify(r))'))
  check(len(data)==8 and all(row['engineSHA256']==engine for row in data),'Eight actual Workers return exact required engine '+engine[:8])
  results.append(data)
 def semantic(rows):
  return [{k:v for k,v in row.items() if k!='engineSHA256'} for row in rows]
 check(semantic(results[0])==semantic(results[1]),'Both verified engines agree on all eight existing alkane analyses')
 wrong=ev('NameleculeChemistryClient.verifyEngine("'+('0'*64)+'").then(()=>"unexpected-success",e=>e.code)')
 check(wrong=='ENGINE_VERSION_MISMATCH','Unknown digest is rejected after immutable404/current mismatch')
 invalid=ev('NameleculeChemistryClient.verifyEngine("../core").then(()=>"unexpected-success",e=>e.code)')
 check(invalid=='INVALID_ENGINE_VERSION','Invalid version path is rejected before loading')
 out['analyses']=results;out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors
 Path('docs/checks/v54-merge-20261105/browser/engine-binding-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
