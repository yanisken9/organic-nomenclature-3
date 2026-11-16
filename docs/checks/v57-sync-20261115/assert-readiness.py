"""Require frozen-target evidence before source activation; no application mutations."""
from pathlib import Path
import datetime,gzip,hashlib,json
H=Path(__file__).resolve().parent;F=json.loads((H/'verification-target.json').read_text());C=Path(F['candidate'])
assert all(hashlib.sha256((C/p).read_bytes()).hexdigest()==d for p,d in F['files'].items())
r=json.loads((H/'independent-review-final.json').read_text());assert r['finding']=='REV57-1' and r['status']=='closed' and r['viewerSHA256']==F['files']['js/mulermoc-nom-molview-57.js']
n=json.loads((H/'native-browser/run-native57-165722/native57.json').read_text());assert n['completed'] and len(n['checks'])==39 and not n['javascriptErrors'] and n['frozenTarget']==F['files']
a=json.loads(gzip.decompress((H/'native-browser/run-raster-165814/raster.json.gz').read_bytes()));assert a['completed'] and len(a['cases'])==562 and not a['failures'] and not a['javascriptErrors'] and a['frozenTargetMatchesAtFinish'] and a['sourceHashesAtFinish']==F['files']
b=json.loads((H/'browser/summary.json').read_text());assert b['passed'] and b['candidate']==str(C) and b['diagnostics']['javascriptExceptionsAcrossCompletedRuns']==0 and b['frozenManifestSHA256']==hashlib.sha256((H/'verification-target.json').read_bytes()).hexdigest()
choices=[]
for p in sorted((H/'native-browser').glob('run-limits57-*/limits57.json')):
 d=json.loads(p.read_text())
 if d.get('completed') and not d['javascriptErrors']:choices.append((p,d))
assert choices,'Missing actual unsupported-source/fallback check';lp,l=choices[-1]
checks={'native':{'path':'native-browser/run-native57-165722/native57.json','checks':len(n['checks'])},'raster':{'path':'native-browser/run-raster-165814/raster.json.gz','cases':len(a['cases'])},'lessonProgressDetective':{'path':'browser/summary.json','checks':b['completedChecks'],'genuineCorrectUIAttempts':b['genuineCorrectUIAttempts']},'actualFallback':{'path':str(lp.relative_to(H)),'checks':len(l['checks'])},'independentChemistry':['independent-chemistry-core.json','independent-chemistry-viewer.json','independent-raw-map-inventory.json'],'independentReviewer':['independent-review-initial.json','independent-review-final.json']}
out={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independentReviewClosed':True,'requiredRuntimeChecksPassed':True,'frozenManifestSHA256':hashlib.sha256((H/'verification-target.json').read_bytes()).hexdigest(),'checks':checks,'scope':'Approved17pathlocalprofessorsync. No conference/offline/physicalmobile/personalFirefox qualification. Stereo/queryunsupportedmappingfallsbackto2D. Priornew3Dreadbackdiagnosisnotresolved.','commit':False,'publication':False}
(H/'readiness.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
