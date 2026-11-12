"""Authorized dated save/publication preparation. Source checkout Git remains read-only."""
from pathlib import Path
import sys,os,json,hashlib,importlib.util,subprocess,datetime,time,re,html,urllib.parse,shutil,plistlib,concurrent.futures
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;STATE=R/'communication/checkpoints/save-publish-20261112-state.json'
spec=importlib.util.spec_from_file_location('verified_save_primitives',R/'communication/checkpoints/save-helper-20261105.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.REPORT_REL='docs/professor-20261112'
def exact(path):
 path=Path(path)
 for attempt in range(6):
  try:
   before=path.stat()
   with path.open('rb')as f:
    opened=os.fstat(f.fileno());data=f.read();closed=os.fstat(f.fileno())
   after=path.stat()
   if len(data)==before.st_size==opened.st_size==closed.st_size==after.st_size and before.st_ino==after.st_ino and before.st_mtime_ns==after.st_mtime_ns:return data
  except OSError as error:
   if error.errno!=89:raise
   if attempt==5:raise OSError(89,'Cloud read canceled after six attempts: '+str(path))from error
  if attempt<5:time.sleep(.25*(attempt+1))
 raise RuntimeError('Nonstable or short/cloud-empty read: '+str(path))
def sha(p):return hashlib.sha256(exact(p)).hexdigest()
def load():return json.loads(exact(STATE))
def write(p,v):h.atomic_bytes(h.json_bytes(v),Path(p),replace=True)
def invariant(s):
 assert h.git(R,'rev-parse','HEAD').decode().strip()==s['activeHead']
 assert h.git(R,'branch','--show-current').decode().strip()==s['activeBranch']
 assert sha(R/'.git/index')==s['indexSHA256']
 assert all(sha(R/p)==v for p,v in s['coreBaseline'].items())
 for p,v in s.get('runtimeFiles',{}).items():assert sha(R/p)==v,p
def ownclone(s,key):
 c=Path(s[key]).resolve();assert c.is_relative_to(Path(s['job']).resolve())and not c.is_relative_to(R)
 assert(c/'.git').is_dir()and not(c/'.git').is_symlink()
 assert h.git(c,'rev-parse','--show-toplevel').decode().strip()==str(c)
 assert(c/'.git/info/attributes').read_bytes()==b'* -text -eol -filter -ident\n'
 return c
def copydata(src,dst):
 data=exact(src);mode=Path(src).stat().st_mode&0o777;h.atomic_bytes(data,dst,replace=Path(dst).exists());os.chmod(dst,mode);assert Path(dst).stat().st_mode&0o777==mode;return hashlib.sha256(data).hexdigest()
def assemble():
 s=load();invariant(s);c=ownclone(s,'publicClone');assert h.git(c,'rev-parse','HEAD').decode().strip()==s['previousPublic']
 inv=json.loads(exact(H/'inventory-preflight.json'))
 runtime=inv['runtimePaths']
 assert runtime and len(runtime)==len(set(runtime))
 # The library/welcome and all runtime additions were independently reviewed before this save.
 evidence=set()
 report=R/s['reportDirectory'];reportfiles=[p.relative_to(R).as_posix()for p in report.rglob('*')if p.is_file()]
 for path in reportfiles:
  if path.endswith('.html'):urls=re.findall(r'(?:href|src)="([^"#][^"]*)"',exact(R/path).decode())
  elif path.endswith('links.json'):urls=[v for v in json.loads(exact(R/path)).values()if isinstance(v,str)and v.startswith('http')]
  else:urls=[]
  for url in urls:
   url=html.unescape(url);u=urllib.parse.urlsplit(url)
   if u.scheme:
    if u.netloc!='yanisken9.github.io' or not u.path.startswith('/organic-nomenclature-3/'):continue
    rel=urllib.parse.unquote(u.path[len('/organic-nomenclature-3/'):])
   else:rel=os.path.relpath((R/path).parent/urllib.parse.unquote(u.path),R)
   if rel.startswith(('docs/','communication/'))and rel not in reportfiles:
    assert '..'not in Path(rel).parts and(R/rel).is_file(),rel;evidence.add(rel)
 # Explicit corpus validation source and complete final technical report are part of report delivery.
 files=sorted(set(runtime)|set(reportfiles)|evidence)
 hashes={p:copydata(R/p,c/p)for p in files}
 old=json.loads(exact(H/'public-baseline-hashes.json'))
 for p,v in old.items():
  if p not in files:assert sha(c/p)==v,p
 runtimehash={p:hashes[p]for p in runtime}
 s.update(runtimeFiles=runtimehash,runtimeFileCount=len(runtimehash),releaseFiles=hashes,releaseFileCount=len(hashes),reportEvidenceFiles=sorted(evidence),candidatePrepared=True,candidateRoot=str(c),publicUnchangedOutsideOverlay=True)
 write(STATE,s);write(H/'runtime-target.json',{'files':runtimehash,'releaseFiles':hashes,'sourceHEAD':s['activeHead'],'candidateRoot':str(c),'publicPrevious':s['previousPublic'],'protectedExistingFiles':len(old)-len(set(old)&set(files))})
 invariant(s);print(json.dumps({'runtimeFiles':len(runtime),'totalReleaseOverlay':len(files),'evidenceFiles':len(evidence),'allUntargetedPublicFilesUnchanged':True}),flush=True)
def freeze(s):
 frozen=Path(s['job'])/'frozen-source';assert not frozen.exists();frozen.mkdir()
 source=h.source_paths(R);recovery=h.recovery_paths(R);allpaths=sorted(set(source+recovery));hashes={}
 def item(p):
  src=h.relative_path(R,p);dst=h.relative_path(frozen,p);digest=copydata(src,dst);return p,digest,dst.stat().st_size
 done=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  for p,d,n in pool.map(item,allpaths):
   assert n==(frozen/p).stat().st_size;hashes[p]=d;done+=1
   if done%1000==0:print('Frozen exact bytes '+str(done)+'/'+str(len(allpaths)),flush=True)
 assert not h.secret_findings(frozen,allpaths)
 assert max((frozen/p).stat().st_size for p in allpaths)<90*1024*1024
 sourcehash={p:hashes[p]for p in source};recoveryhash={p:hashes[p]for p in recovery}
 return frozen,sourcehash,recoveryhash

def commit_source(s,root,clone,hashes):
 old={os.fsdecode(p)for p in h.git(clone,'ls-files','-z').split(b'\0')if p}
 for p in old-set(hashes):h.relative_path(clone,p).unlink(missing_ok=True)
 for p,v in hashes.items():h.verified_copy(root/p,clone/p,replace=True,expected=v)
 subprocess.run(['git','-C',str(clone),'add','-A'],check=True)
 subprocess.run(['git','--literal-pathspecs','-C',str(clone),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=('\0'.join(hashes)+'\0').encode(),check=True)
 h.verify_staged_bytes(clone,hashes)
 subprocess.run(['git','-C',str(clone),'commit','--quiet','-m','Save full Namelecule sources and React WIP — 12 November 2026'],check=True)
 assert not h.git(clone,'status','--porcelain','-z')
 return h.git(clone,'rev-parse','HEAD').decode().strip()

def package(s,artifacts,sourceRoot,replace=False):
 lessons,counts=h.lesson_inventory(sourceRoot);app,appfiles=h.launcher_inventory(R,s);result=[]
 for directory in s['externalFolders']:
  dest=Path(directory);dest.mkdir(parents=True,exist_ok=True);files={}
  for p in artifacts:
   p=Path(p);files[p.name]=h.verified_copy(p,dest/p.name,replace=replace)
   files[p.name+'.sha256']=h.atomic_bytes((files[p.name]+'  '+p.name+'\n').encode(),dest/(p.name+'.sha256'),replace=replace)
  for p,data in h.portable_report(sourceRoot,s['reportLink']).items():files['Αναφορά καθηγητή/'+p]=h.atomic_bytes(data,dest/'Αναφορά καθηγητή'/p,replace=True)
  for name in ['links.txt','links.json','message-to-professor.txt']:files[name]=copydata(sourceRoot/s['reportDirectory']/name,dest/name)
  for label,url in [('Namelecule — Υποδοχή',s['finalLink']),('Αναφορά καθηγητή',s['reportLink'])]:files[label+'.webloc']=h.atomic_bytes(plistlib.dumps({'URL':url}),dest/(label+'.webloc'),replace=True)
  for p in lessons+[h.PILOT_REL]:
   rel=('Σενάρια JSON/'if p in lessons else'Χωριστός πιλότος/')+Path(p).name;files[rel]=copydata(sourceRoot/p,dest/rel)
  for name in ['SESSION-NOTES.md','YANNIS-CONTRIBUTIONS.md']:files[name]=copydata(sourceRoot/'docs'/name,dest/name)
  for p in appfiles:
   rel='Namelecule.app/'+p.relative_to(app).as_posix();files[rel]=copydata(p,dest/rel)
  text='Namelecule — Πλήρης αποθήκευση 12/11/2026\n'+s['finalLink']+'\n'+s['reportLink']+'\nΠλήρεις πηγές και React WIP, όχι πιστοποιημένο offline πακέτο. Δύο φάκελοι στον ίδιο υπολογιστή. Τα παλαιότερα αντίγραφα διατηρούνται. Μεταγενέστερα metadata/receipts έχουν χωριστό χρονικό όριο.\n'
  files['ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt']=h.atomic_bytes(text.encode(),dest/'ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt',replace=True)
  assert all(sha(dest/p)==v for p,v in files.items())
  appmodes={p.relative_to(app).as_posix():p.stat().st_mode&0o777 for p in appfiles}
  assert all((dest/'Namelecule.app'/p).stat().st_mode&0o777==mode for p,mode in appmodes.items())
  result.append({'directory':directory,'files':files,'allSHA256Verified':True,'launcherModes':appmodes,'launcherModesVerified':True})
 return result

def save():
 s=load();invariant(s);assert s.get('candidateBrowserPassed')and not s.get('saveComplete')
 mapping=json.loads(exact(R/'communication/checkpoints/alkanes-json-export-20261112-fullsave.json'));destination=Path(mapping['destination']);active=R/'scenarios/alkanes-user-3.scenario.json';assert exact(active)==exact(destination)
 frozen,sourcehash,recoveryhash=freeze(s);c=ownclone(s,'checkpointClone');assert not h.git(c,'status','--porcelain','-z')
 commit=commit_source(s,frozen,c,sourcehash)
 cutoff=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest={'cutoffUTC':cutoff,'checkpointCommit':commit,'files':sourcehash,'recoveryFiles':recoveryhash,'coreChanged':False,'scope':'All tracked/nonignored source plus explicit React public/dist. Ignored communication operational records saved separately. Private Git/browserprofiles and old recursive archives excluded. Later metadata delta separate.'}
 prefix=R/'communication/checkpoints'/('Namelecule-'+s['stamp']+'-full');artifacts=[Path(str(prefix)+x)for x in ['.zip','.bundle','-recovery.zip']]
 h.create_zip(frozen,sourcehash,artifacts[0],manifest);h.create_bundle(c,artifacts[1]);h.create_zip(frozen,recoveryhash,artifacts[2],{'cutoffUTC':cutoff,'files':recoveryhash},prefix='')
 copies=package(s,artifacts,frozen);invariant(s)
 s.update(saveComplete=True,checkpointSnapshotCommit=commit,latestLocalCheckpointCommit=commit,sourceCutoffUTC=cutoff,sourceHashes=sourcehash,recoveryHashes=recoveryhash,sourceFileCount=len(sourcehash),recoveryFileCount=len(recoveryhash),frozenSource=str(frozen),archives={str(p.relative_to(R)):sha(p)for p in artifacts},externalCopies=copies,zipCRCAndEveryEntryHashVerified=True,bundleVerified=True,rootHeadIndexCorePreserved=True,currentDesktopJSON={'source':str(active),'destination':str(destination),'sha256':sha(active),'byteIdentical':True})
 write(STATE,s);receipt=R/'communication/checkpoints'/('Namelecule-'+s['stamp']+'-save-receipt.json');write(receipt,s)
 for d in s['externalFolders']:h.verified_copy(receipt,Path(d)/receipt.name)
 print(json.dumps({'snapshot':commit,'sourceFiles':len(sourcehash),'recoveryFiles':len(recoveryhash),'externalFoldersVerified':len(copies),'archives':s['archives']},ensure_ascii=False),flush=True)

if __name__=='__main__':
 {'assemble':assemble,'save':save}[sys.argv[1]]()
