"""Reuse existing suites with evidence redirected into this merge unit.
Original test files/assertions stay unchanged. Geometry run() is reused with its
same complete failure list, then evaluated with the original no-fail contract.
"""
from pathlib import Path
import hashlib,json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
# Naming uses exact pre-merge session snapshots supplied in historical /before.
p=ROOT/'docs/checks/v54-upstream-20261104/test-naming.py'
source=p.read_text()
old="(D/'naming-results.json').write_text"
assert source.count(old)==1
source=source.replace(old,"(Path("+repr(str(HERE/'naming-results.json'))+")).write_text")
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
# The geometry suite has no output option; invoke its existing pure runner so
# the exact same numerical/invariant checks write only this unit's evidence.
p=ROOT/'docs/checks/v54-upstream-20261104/geometry/test-geometry.py'
shared=runpy.run_path(str(p))
core=(ROOT/'js/mulermoc-nom-core-54.js').read_text()
result=shared['run'](core)
result['runtime']='JavaScriptCore actual naming/parser/generator'
result['coreSHA256']=hashlib.sha256(core.encode()).hexdigest()
result['summary']={'forms':len(result['rows']),'molecules':len(set(r['key']for r in result['rows'])),
 'missing':result['missing'],'generated':sum(r['generated']for r in result['rows']),
 'skipped':[{'key':r['key'],'mode':r['mode'],'reason':r['reason']}for r in result['rows']if not r['generated']],
 'angleFailures':sum(f['kind']=='angle'for f in result['failures']),
 'invariantFailures':sum(f['kind']=='invariant'for f in result['failures'])}
(HERE/'geometry-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary'],ensure_ascii=False))
assert not result['failures'],result['failures'][:3]
