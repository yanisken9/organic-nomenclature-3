from pathlib import Path
import json,os,subprocess,hashlib,concurrent.futures
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=R/'communication/checkpoints/save-publish-20261116-state.json'
s=json.loads(S.read_text());job=Path(s['job']).resolve();assert job.is_relative_to(Path('/private/tmp')) and job.name.startswith('namelecule-save-20261116-')
env={k:v for k,v in os.environ.items()if not k.startswith('GIT_TRACE')and k!='GIT_CURL_VERBOSE'};env['GIT_TERMINAL_PROMPT']='0'
def run(args,timeout=300):
 q=subprocess.run(['git',*args],capture_output=True,env=env,timeout=timeout)
 if q.returncode:raise RuntimeError('Git operation failed: '+args[0]+' (code '+str(q.returncode)+')')
 return q.stdout
assert s['publicRemote']=='https://github.com/yanisken9/organic-nomenclature-3.git'
def clone(key):
 dst=Path(s[key]);assert dst.parent.resolve()==job and not dst.exists()
 previous=s['previousPublic'if key=='publicClone'else'previousCheckpoint']
 branch=s['publicBranch']if key=='publicClone'else'checkpoint/namelecule-20261112-115539'
 run(['clone','--quiet','--no-checkout','--single-branch','--branch',branch,s['publicRemote'],str(dst)])
 assert run(['-C',str(dst),'rev-parse','HEAD']).decode().strip()==previous
 (dst/'.git/info/attributes').write_bytes(b'* -text -eol -filter -ident\n')
 if key=='publicClone':run(['-C',str(dst),'checkout','--quiet','-B',s['publicBranch'],previous])
 else:
  run(['-C',str(dst),'symbolic-ref','HEAD','refs/heads/'+s['checkpointBranch']])
  run(['-C',str(dst),'update-ref','HEAD',previous])
  run(['-C',str(dst),'read-tree',previous])
 # Existing global identity is used without printing private credential/config output.
 for field,value in [('user.name','Yannis Skendros'),('user.email','yanisken9@users.noreply.github.com')]:
  q=subprocess.run(['git','-C',str(dst),'config','--get',field],capture_output=True,env=env)
  if q.returncode:run(['-C',str(dst),'config',field,value])
 print('Prepared owned '+key,flush=True);return str(dst)
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(clone,['publicClone','checkpointClone']))
c=Path(s['publicClone']);paths=run(['-C',str(c),'ls-files','-z']).split(b'\0');hashes={os.fsdecode(p):hashlib.sha256((c/os.fsdecode(p)).read_bytes()).hexdigest()for p in paths if p}
(H/'public-baseline-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n');s['clonesReady']=True;s['publicBaselineFiles']=len(hashes);S.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'clonesReady':True,'publicFiles':len(hashes),'sourceHEADIndexUntouched':True}),flush=True)
