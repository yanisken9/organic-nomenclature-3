from pathlib import Path
import json,hashlib,difflib,datetime,subprocess
folder=Path(__file__).resolve().parent
root=folder.parents[2]
b=json.loads((folder/'baseline.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={p:sha(root/p) for p,h in b['files'].items() if sha(root/p)!=h}
for p in b['newFiles']:files[p]=sha(root/p)
protected={p:h for p,h in b['protectedDependencies'].items() if p not in b['files']}
assert all(sha(root/p)==h for p,h in protected.items())
assert all(sha(root/p)==h for p,h in b['coreBaseline'].items())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==b['baseCommit']
parts=[]
for p in files:
 before=(folder/'before'/p).read_text().splitlines(True) if p in b['files'] else []
 parts.extend(difflib.unified_diff(before,(root/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p))
(folder/'source.diff').write_text(''.join(parts))
manifest={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Frozen viewport candidate after shared stylesheet scope corrections; final browser/review pending','baseCommit':b['baseCommit'],'approvedPlan':'docs/GAME-VIEWPORT-PLAN-20261116.md','files':files,'beforeHashes':{p:b['files'][p] for p in files if p in b['files']},'newFiles':b['newFiles'],'protectedDependencies':protected,'coreBaseline':b['coreBaseline'],'corrections':['BP-P2-001','BP-P2-002','D-VIEW-01','QCP-REPAIR-VIEW-01'],'coreChanged':False,'commit':False,'publication':False}
(folder/'verification-target.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'files':len(files),'manifestSHA256':sha(folder/'verification-target.json'),'coresUnchanged':len(b['coreBaseline']),'protectedUnchanged':len(protected)}))
