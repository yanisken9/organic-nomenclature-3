from pathlib import Path
import json,subprocess,concurrent.futures,hashlib,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
s=json.loads((H/'baseline.json').read_text());old=json.loads((R/'communication/checkpoints/save-publish-20261110-state.json').read_text());audit=json.loads((H/'upstream-and-public-audit.json').read_text());job=Path(s['job']);origin='https://github.com/yanisken9/organic-nomenclature-3.git'
def clone(name,src,branch=None):
 dst=job/name;assert not dst.exists();args=['git','clone','--quiet','--no-hardlinks']
 if branch:args+=['--single-branch','--branch',branch]
 subprocess.run(args+[src,str(dst)],check=True)
 subprocess.run(['git','-C',str(dst),'remote','set-url','origin',origin],check=True)
 attr=dst/'.git/info/attributes';attr.write_bytes(b'* -text -eol -filter -ident\n')
 return dst
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 a=pool.submit(clone,'public',old['publicClone'],'thesis-work');b=pool.submit(clone,'checkpoint',old['checkpointClone']);public=a.result();checkpoint=b.result()
head=lambda p:subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
assert head(public)==audit['publicHEAD']
branch='checkpoint/namelecule-'+s['stamp'];subprocess.run(['git','-C',str(checkpoint),'checkout','--quiet','-b',branch],check=True)
files=[p for p in public.rglob('*')if p.is_file()and'.git'not in p.parts and not p.is_symlink()]
publicHashes={p.relative_to(public).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
(H/'public-baseline-hashes.json').write_text(json.dumps(publicHashes,indent=2)+'\n')
s.update(publicClone=str(public),checkpointClone=str(checkpoint),checkpointBranch=branch,publicBranch='thesis-work',previousPublic=head(public),previousCheckpoint=head(checkpoint),publicRemote=origin,lastActuallySyncedUpstream=audit['lastActuallySynchronized'],lastCheckedUpstream=audit['upstreamHEAD'],reportDirectory='docs/professor-20261111',finalLink='https://yanisken9.github.io/organic-nomenclature-3/design/welcome-proposal.html?v=release-20261111',reportLink='https://yanisken9.github.io/organic-nomenclature-3/docs/professor-20261111/update.html',externalFolders=[str(R.parent/'Αποθηκεύσεις'/('2026-11-11-'+s['stamp'].split('-')[1])),'/Users/yannisskendros/Desktop/αρχεία  json/Namelecule_11-11-2026'])
state=R/'communication/checkpoints/save-publish-20261111-state.json';state.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:s[k]for k in ['publicClone','checkpointClone','checkpointBranch','previousPublic','previousCheckpoint','externalFolders']},ensure_ascii=False))
