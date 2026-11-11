"""Guarded selective rollback. Default is read-only; use --apply intentionally."""
from pathlib import Path
import argparse,json,hashlib
BACKUP=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def restore(root,apply=False):
 root=root.resolve();m=json.loads((BACKUP/'rollback-manifest.json').read_text())
 if not m['postStateRecorded']:raise ValueError('Installation hashes not recorded')
 def target(name):
  p=root/name
  if p.is_symlink()or root not in (p.resolve(),*p.resolve().parents):raise ValueError('Unsafe target path: '+name)
  return p
 originals=[];new=[]
 # All guards run before any write/removal.
 for name,row in m['originals'].items():
  p=target(name);b=BACKUP/'original'/name
  if sha(b)!=row['beforeSHA256']:raise ValueError('Backup changed: '+name)
  if not p.is_file()or sha(p)!=row['installedSHA256']:raise ValueError('Newer or unexpected edit: '+name)
  originals.append((p,b))
 for name,digest in m['newFiles'].items():
  p=target(name)
  if p.exists():
   if not p.is_file()or sha(p)!=digest:raise ValueError('Newer or unexpected file: '+name)
   new.append(p)
 if apply:
  for p,b in originals:p.write_bytes(b.read_bytes())
  for p in new:p.unlink()
 return {'originalFiles':len(originals),'newFiles':len(new),'applied':apply}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--root',type=Path);args=parser.parse_args();m=json.loads((BACKUP/'rollback-manifest.json').read_text());print(json.dumps(restore(args.root or Path(m['repo']),args.apply)))
