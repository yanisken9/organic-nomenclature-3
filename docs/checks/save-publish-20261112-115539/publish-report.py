"""Publish only the frozen factual report and proof overlay, after runtime proof."""
from pathlib import Path
import sys,importlib.util,json,subprocess,datetime,urllib.request,urllib.parse,hashlib,concurrent.futures
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('delivery',H/'deliver.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
o=d.ops;h=o.h;R=o.R
def target(s):
 t=json.loads(o.exact(H/'final-report-target.json'));assert t['runtimeCommit']==s['publicRuntimeCommit']
 assert all(o.sha(R/p)==v for p,v in t['files'].items())
 return t
def prepare():
 s=o.load();o.invariant(s);assert s.get('publicRuntimeLiveVerified')and s.get('publicLiveBrowserPassed')
 c=d.clone(s,'publicClone',s['publicBranch']);assert d.git(c,'rev-parse','HEAD').decode().strip()==s['publicRuntimeCommit']
 assert not d.git(c,'status','--porcelain','-z');t=target(s);_,expected=d.target(s)
 d.worktree(c,expected)
 for p,v in t['files'].items():assert o.copydata(R/p,c/p)==v
 expected.update(t['files']);d.worktree(c,expected)
 d.git(c,'add','-A');d.git(c,'--literal-pathspecs','add','-f','--pathspec-from-file=-','--pathspec-file-nul',input=('\0'.join(expected)+'\0').encode());h.verify_staged_bytes(c,expected)
 d.git(c,'commit','--quiet','-m','Publish verified professor report and delivery evidence — 12 November 2026')
 commit=d.git(c,'rev-parse','HEAD').decode().strip();assert not d.git(c,'status','--porcelain','-z');o.invariant(s)
 s.update(publicReportCommit=commit,publicReleaseCommit=commit,finalPublicTreeHashes=expected);o.write(o.STATE,s)
 o.write(H/'report-prepare.json',{'commit':commit,'parent':s['publicRuntimeCommit'],'files':t['files'],'everyStagedBlobVerified':True});print(commit,flush=True)
def push():
 s=o.load();o.invariant(s);assert s.get('finalReportReviewComplete')and s.get('publicReportCommit')
 c=d.clone(s,'publicClone',s['publicBranch']);target(s);head=d.git(c,'rev-parse','HEAD').decode().strip();assert head==s['publicReportCommit']and not d.git(c,'status','--porcelain','-z')
 d.worktree(c,s['finalPublicTreeHashes']);h.verify_staged_bytes(c,s['finalPublicTreeHashes'])
 ref='refs/heads/'+s['publicBranch'];assert d.refs(c,s).get(ref)in[s['publicRuntimeCommit'],head]
 d.git(c,'push','origin',head+':'+ref);assert d.refs(c,s).get(ref)==head
 s['reportRemoteUploaded']=True;s['latestUploadedPublicCommit']=head;o.write(o.STATE,s);print('Report remote verified '+head,flush=True)
def verify():
 s=o.load();o.invariant(s);c=d.delivery_guard(s);t=target(s)
 protected=json.loads(o.exact(R/'communication/checkpoints/save-publish-20261110-state.json'))['publicProtected']
 hashes={**t['files'],**s['runtimeFiles'],**protected}
 def item(p):
  request=urllib.request.Request(d.PUBLIC+urllib.parse.quote(p,safe='/')+'?final='+s['stamp'],headers={'Cache-Control':'no-cache','Accept-Encoding':'identity','User-Agent':'Namelecule-final-report-verification'})
  with urllib.request.build_opener(d.NoRedirect).open(request,timeout=30)as r:
   data=r.read((c/p).stat().st_size+1);v={'status':r.status,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'expectedSHA256':hashes[p]};v['ok']=r.status==200 and v['sha256']==hashes[p]and len(data)==(c/p).stat().st_size;return p,v
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:results=dict(pool.map(item,hashes))
 passed=all(v['ok']for v in results.values());o.write(H/'public-final-http.json',{'checkedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':s['publicReportCommit'],'files':results,'allSHA256Verified':passed})
 assert passed,'Final HTTP content differs';s.update(reportLiveVerified=True,finalPublicHTTPCount=len(results),reportVerifiedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());o.write(o.STATE,s);print('Final exact public files '+str(len(results)),flush=True)
if __name__=='__main__':{'prepare':prepare,'push':push,'verify':verify}[sys.argv[1]]()
