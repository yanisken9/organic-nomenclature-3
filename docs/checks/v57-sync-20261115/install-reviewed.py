"""Bounded reviewed installation. Adds15 named files before rerouting2 entry files."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,tempfile
ROOT=Path.cwd();H=Path(__file__).resolve().parent
B=json.loads((H/'baseline.json').read_text());P=json.loads((H/'plan.json').read_text());F=json.loads((H/'verification-target.json').read_text());C=Path(F['candidate'])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def same(paths,root=ROOT):return {p:digest(root/p) for p in paths}==paths
assert same(B['protected']) and same(B['cores']), 'Protected baseline drift'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==B['HEAD']
assert digest(ROOT/'.git/index')==B['indexSHA256']
assert same(F['files'],C),'Frozen candidate drift'
assert all(not (ROOT/p).exists() for p in P['newFiles']),'New57 already installed; investigate rather than overwrite'
assert same(B['navigationBefore']),'Current navigation changed since baseline'
R=json.loads((H/'readiness.json').read_text());assert R['independentReviewClosed'] and R['requiredRuntimeChecksPassed']
REC=H/'recovery-before57';REC.mkdir(exist_ok=False)
for p in P['navigationFiles']:
 q=REC/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((ROOT/p).read_bytes());assert digest(q)==B['navigationBefore'][p]
receipt={'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recovery':'recovery-before57','restoration':'Restore2navigation files fromrecovery-before57; old56runtimekept. New57files mayremainunused. No fullbackupcreated.','oldNavigation':B['navigationBefore'],'installed':{},'commit':False,'publication':False}
(REC/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
for p in P['newFiles']+P['navigationFiles']:
 dest=ROOT/p;data=(C/p).read_bytes();assert hashlib.sha256(data).hexdigest()==F['files'][p]
 fd,tmp=tempfile.mkstemp(prefix='.install57-',dir=dest.parent)
 try:
  with os.fdopen(fd,'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,dest)
 finally:
  if Path(tmp).exists():Path(tmp).unlink()
 receipt['installed'][p]=digest(dest)
assert receipt['installed']==F['files'];assert same(B['protected']) and same(B['cores'])
assert digest(ROOT/'.git/index')==B['indexSHA256']
receipt.update(completed=True,protectedPaths=len(B['protected']),oldCores=len(B['cores']),finishedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
(H/'installation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':True,'installed':len(receipt['installed']),'protected':receipt['protectedPaths'],'oldCores':receipt['oldCores']}))
