"""Final metadata archive and checkpoint delivery after verified public release.
The closing receipt deliberately follows the archive cutoff.
"""
from pathlib import Path
import sys,importlib.util,json,datetime,subprocess,hashlib,os,concurrent.futures
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("release_ops",H/"release-ops.py");o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
R=o.R;h=o.h

def finish():
 s=o.load();o.invariant(s)
 assert s.get("saveComplete")and s.get("publicRuntimeLiveVerified")and s.get("reportLiveVerified")and s.get("independentReviewComplete")
 assert not s.get("finalMetadataCaptured")
 c=o.ownclone(s,"checkpointClone");assert h.git(c,"rev-parse","HEAD").decode().strip()==s["checkpointSnapshotCommit"]
 assert not h.git(c,"status","--porcelain","-z")
 paths=sorted(set(h.source_paths(R))|set(h.recovery_paths(R)))
 frozen=Path(s["job"])/"frozen-final-metadata-r2";assert not frozen.exists();frozen.mkdir()
 def freeze_one(p):
  return p,o.copydata(h.relative_path(R,p),h.relative_path(frozen,p))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  hashes=dict(pool.map(freeze_one,paths))
 assert not h.secret_findings(frozen,paths)
 old={os.fsdecode(p)for p in h.git(c,"ls-files","-z").split(b"\0")if p}
 for p in old-set(paths):h.relative_path(c,p).unlink(missing_ok=True)
 for p,digest in hashes.items():
  if not(c/p).is_file()or o.sha(c/p)!=digest or(c/p).stat().st_mode&0o777!=(frozen/p).stat().st_mode&0o777:
   h.verified_copy(frozen/p,c/p,replace=True,expected=digest)
 subprocess.run(["git","-C",str(c),"add","-A"],check=True)
 subprocess.run(["git","--literal-pathspecs","-C",str(c),"add","-f","--pathspec-from-file=-","--pathspec-file-nul"],input=("\0".join(paths)+"\0").encode(),check=True)
 h.verify_staged_bytes(c,hashes)
 subprocess.run(["git","-C",str(c),"commit","--quiet","-m","Save final professor report and verified delivery receipts — 12 November 2026"],check=True)
 commit=h.git(c,"rev-parse","HEAD").decode().strip();cutoff=datetime.datetime.now(datetime.timezone.utc).isoformat()
 baseline={**s["sourceHashes"],**s["recoveryHashes"]};delta={p:v for p,v in hashes.items()if baseline.get(p)!=v}
 stem="Namelecule-"+s["stamp"]+"-final-metadata";prefix=R/"communication/checkpoints"/stem
 archive=Path(str(prefix)+".zip");bundle=Path(str(prefix)+".bundle")
 h.create_zip(frozen,delta,archive,{"cutoffUTC":cutoff,"baseSnapshot":s["checkpointSnapshotCommit"],"metadataCommit":commit,"files":delta,"fullFinalTree":hashes,"deletions":sorted(set(baseline)-set(hashes)),"note":"Apply after full source/recovery. Closing receipt is outside archive cutoffs."})
 assert not bundle.exists();temporary=bundle.with_name("."+bundle.name+".partial");assert not temporary.exists()
 subprocess.run(["git","-C",str(c),"bundle","create",str(temporary),s["checkpointBranch"],"^"+s["checkpointSnapshotCommit"]],check=True)
 subprocess.run(["git","-C",str(c),"bundle","verify",str(temporary)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True);h.publish_temporary(temporary,bundle)
 assert all(o.sha(R/p)==v for p,v in hashes.items());o.invariant(s)
 updated=o.package(s,[archive,bundle],frozen)
 before={r["directory"]:r for r in s["externalCopies"]}
 for record in updated:
  record["files"]={**before[record["directory"]]["files"],**record["files"]}
  assert all(o.sha(Path(record["directory"])/p)==v for p,v in record["files"].items())
 s.update(finalMetadataCaptured=True,latestLocalCheckpointCommit=commit,finalMetadataCutoffUTC=cutoff,finalMetadataFileCount=len(delta),finalCheckpointTreeFiles=len(hashes),finalMetadataArchives={str(p.relative_to(R)):o.sha(p)for p in [archive,bundle]},incrementalBundlePrerequisite=s["checkpointSnapshotCommit"],externalCopies=updated,closingReceiptOutsideArchiveCutoffs=True)
 o.write(o.STATE,s);receipt=Path(str(prefix)+"-receipt.json");o.write(receipt,s)
 for d in s["externalFolders"]:h.verified_copy(receipt,Path(d)/receipt.name)
 print(json.dumps({"metadataCommit":commit,"finalTreeFiles":len(hashes),"deltaFiles":len(delta),"verifiedFolders":len(updated)},ensure_ascii=False),flush=True)

def push():
 s=o.load();o.invariant(s);assert s.get("finalMetadataCaptured")and s.get("independentReviewComplete")
 c=o.ownclone(s,"checkpointClone");head=h.git(c,"rev-parse","HEAD").decode().strip();assert head==s["latestLocalCheckpointCommit"]
 branch=s["checkpointBranch"];remote=h.git(c,"ls-remote","origin","refs/heads/"+branch).decode().split()[0]
 assert remote in [s["checkpointSnapshotCommit"],head],"Checkpoint remote unexpectedly advanced"
 subprocess.run(["git","-C",str(c),"push","origin","HEAD:refs/heads/"+branch],check=True)
 assert h.git(c,"ls-remote","origin","refs/heads/"+branch).decode().split()[0]==head
 s.update(finalCheckpointRemoteVerified=True,latestRemoteCheckpointCommit=head);o.write(o.STATE,s)
 receipt=R/"communication/checkpoints"/("Namelecule-"+s["stamp"]+"-closing-delivery.json");o.write(receipt,{"recordedUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"publicRuntimeCommit":s["publicRuntimeCommit"],"publicReportCommit":s["publicReportCommit"],"checkpointCommit":head,"report":s["reportLink"],"welcome":s["finalLink"],"sourceCutoffUTC":s["sourceCutoffUTC"],"finalMetadataCutoffUTC":s["finalMetadataCutoffUTC"],"archives":{**s["archives"],**s["finalMetadataArchives"]},"coreChanged":False,"receiptOutsideArchiveCutoffs":True})
 for d in s["externalFolders"]:h.verified_copy(receipt,Path(d)/receipt.name)
 print(json.dumps({"remoteCheckpoint":head,"closingReceipt":str(receipt)},ensure_ascii=False),flush=True)

if __name__=="__main__":{"finish":finish,"push":push}[sys.argv[1]]()
