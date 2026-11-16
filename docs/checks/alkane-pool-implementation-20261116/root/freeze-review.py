from pathlib import Path
import datetime,hashlib,json,difflib
R=Path.cwd();H=R/'docs/checks/alkane-pool-implementation-20261116'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((H/'baseline.json').read_text());existing=list(b['beforeHashes'])+[f'js/mulermoc-nom-molview-{v}.js' for v in [55,56,57]]
paths=[];before={};diffs=[]
for p in existing:
 old=H/'before'/p;new=R/p
 assert old.exists() and new.exists(),p
 if old.read_bytes()!=new.read_bytes():
  paths.append(p);before[p]=sha(old)
  diffs.extend(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='before/'+p,tofile=p))
for p in b['newPaths']:
 assert (R/p).exists(),p
 paths.append(p)
assert len(paths)==len(set(paths))
report={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Frozen final working-tree review target, including new/untracked deliverables','baseCommit':b['HEAD'],'comparison':'Exact pre-intervention bytes under before/; Git HEAD predates pre-existing local work. Do not attribute unrelated dirty tree.','approvedPlan':'docs/ALKANE-POOL-EXPANSION-20261116.md','extraApproval':'renderer-scope-approval.json','files':{p:sha(R/p) for p in sorted(paths)},'beforeHashes':before,'newPaths':b['newPaths'],'coreChanges':False,'commit':False,'publication':False}
(H/'verification-target.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(H/'implementation.diff').write_text(''.join(diffs))
print(json.dumps({'files':len(paths),'new':len(b['newPaths']),'changedExisting':len(before),'manifestSHA256':sha(H/'verification-target.json')}))
