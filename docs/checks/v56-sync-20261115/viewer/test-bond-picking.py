from pathlib import Path
import re,subprocess,json,hashlib,datetime
E=Path(__file__).parent;P=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js');JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def source_functions(src):
 ms=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));funcs={m[1]:src[m.start():ms[i+1].start() if i+1<len(ms) else len(src)] for i,m in enumerate(ms)}
 return '\n'.join(funcs[n] for n in ['fMulerSelectCompactCarbonOnly','fMulerQuizHydrogenParent','fMulerSelectPick'])
reports={}
for name,path in [('before',E/'bond-pick-before.js.txt'),('after',P)]:
 s=source_functions(path.read_text())+'\n'+(E/'test-bond-picking-cases.js').read_text();p=E/('actual-bond-picking-'+name+'.js');p.write_text(s)
 r=subprocess.run([JSC,p.name],cwd=E,capture_output=True,text=True);(E/('bond-picking-'+name+'-output.txt')).write_text(r.stdout+r.stderr)
 print(name,r.stdout,r.stderr)
 reports[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'exitCode':r.returncode,'output':json.loads(r.stdout.splitlines()[0])}
report={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual extracted classifier with measured original ethane midpoint and deterministic geometry. Native pointer/browser validation remains with root.','runs':reports}
(E/'bond-picking-results.json').write_text(json.dumps(report,indent=2)+'\n')
# The captured source must reproduce the reported midpoint defect.
assert reports['before']['output']['results'][0]['pass'] is False
assert reports['after']['exitCode']==0
