from pathlib import Path
import re,subprocess,json,hashlib,datetime
E=Path(__file__).parent;P=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js/mulermoc-nom-molview-56.js');JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def source_functions(src):
 ms=list(re.finditer(r'^(?:async )?function (\w+)\(',src,re.M));funcs={m[1]:src[m.start():ms[i+1].start() if i+1<len(ms) else len(src)] for i,m in enumerate(ms)}
 return '\n'.join(funcs[n] for n in ['fMulerSelectCompactCarbonOnly','fMulerQuizHydrogenParent','fMulerSelectPick'])
reports={}
for name,path in [('initial5f86',E/'bond-pick-before.js.txt'),('before9a0d',E/'bond-pick-before-vertex-ownership.js.txt'),('after',P)]:
 s=source_functions(path.read_text())+'\n'+(E/'test-visible-gap-cases.js').read_text();p=E/('actual-visible-gap-'+name+'.js');p.write_text(s)
 r=subprocess.run([JSC,p.name],cwd=E,capture_output=True,text=True);(E/('visible-gap-'+name+'-output.txt')).write_text(r.stdout+r.stderr);print(name,r.stdout,r.stderr)
 reports[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'exitCode':r.returncode,'output':json.loads(r.stdout.splitlines()[0])}
report={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual extracted classifier with real measured full559px-svg-unit glyphs, independent visible bond gap and explicit/implicit ownership variations; browser pointer validation remains with root.','runs':reports}
(E/'visible-gap-results.json').write_text(json.dumps(report,indent=2)+'\n')
assert reports['before9a0d']['output']['results'][1]['pass'] is False
assert reports['after']['exitCode']==0
