"""Exercise guarded selective restore only in an isolated temporary copy."""
from pathlib import Path
import importlib.util,tempfile,json,hashlib,shutil
repo=Path.cwd();backup=repo/'communication/checkpoints/jsmol-integration-20261031';manifest=json.loads((backup/'rollback-manifest.json').read_text());spec=importlib.util.spec_from_file_location('guarded_restore',backup/'restore.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='namelecule-restore-check-') as d:
 root=Path(d)
 def populate():
  for n in [*manifest['originals'],*manifest['newFiles']]:
   p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/n,p)
 populate();assert not mod.restore(repo,False)['applied'];r=mod.restore(root,True)
 assert all(sha(root/n)==v['beforeSHA256'] for n,v in manifest['originals'].items());assert all(not (root/n).exists()for n in manifest['newFiles']);assert r=={'originalFiles':3,'newFiles':6,'applied':True}
 populate();(root/'js/vendor/README.md').write_text('new user edit');before={str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()}
 try:mod.restore(root,True)
 except ValueError as e:assert 'Newer or unexpected edit'in str(e)
 else:raise AssertionError('Newer edit was not refused')
 after={str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()};assert before==after
out={'isolatedRestorePassed':True,'originalFilesRestored':3,'newFilesRemoved':6,'newerEditBlocksBeforeAnyMutation':True,'MainRolledBack':False};Path('/tmp/namelecule-jsmol-integration-20261031/rollback-verification.json').write_text(json.dumps(out,indent=2));print(out)
