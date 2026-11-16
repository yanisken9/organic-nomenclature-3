"""Save bounded post-cutoff closing notes/receipts separately; never edit runtime/Git."""
from pathlib import Path
import json,sys,importlib.util,datetime,os
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('save_ops',H/'release-ops.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
def main():
 s=o.load();o.invariant(s);assert s.get('finalCheckpointRemoteVerified')and s.get('reportLiveVerified')and s.get('finalReportVisualPassed')
 r=json.loads(o.exact(H/'combined-bundle-recovery.json'));assert r['fullBundlePlusIncrementalRecoveryVerified']and r['finalCommit']==s['latestRemoteCheckpointCommit']
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 top=('# Current resume point — 2026-11-16 — Full save and public delivery COMPLETE\n\n'
 'User request fulfilled: source/recovery archives, two dated Desktop mirrors, GitHub checkpoint and public v57/report. Runtime commit `'+s['publicRuntimeCommit']+'`; final public report commit `'+s['publicReportCommit']+'`; final remote checkpoint `'+s['latestRemoteCheckpointCommit']+'`. Source branch `'+s['activeBranch']+'`, HEAD `'+s['activeHead']+'`, original index and all13 core hashes preserved. No core authored or edited during this save; already reviewed Nov15 core56/core57 included in publication; earlier55/52 retained.\n\n'
 'Evidence: '+str(H.relative_to(o.R))+'/ (candidate224checks/6genuinecorrect; public70/3; HTTP184 initial and final overlay; independent source/backup/final-report reviews; final report visual QA). Full standalone and combined full+incremental bundle restorations verified without network/alternates, every original file SHA and exact membership checked, including restored oversized diagnostic. ZIP originals and both mirror file hashes/modes verified. Final metadata cutoff '+s['finalMetadataCutoffUTC']+'. Closing receipts, this resume point and current state are deliberately after that cutoff and saved in a separate closing-metadata ZIP plus both mirrors, without changing the frozen remote checkpoint.\n\n'
 'Public welcome: '+s['finalLink']+'\nProfessor report: '+s['reportLink']+'\nAlkane lesson: '+s['lessonLink']+'\nBackups: '+ ' ; '.join(s['externalFolders'])+'\n\n'
 'Limits retained: both folders are on the same computer, cloud/disk redundancy not established. Copied launcher uses original absolute project path, not portable/offline. Actual125/200 zoom and newviewport3D unverified; prior Firefox freeze cause unresolved; prior Puzzle announcementP3 remains. Not physicalmobile/conference-qualified. Upstream lastchecked838d8c7882b292d3e320e7d8edd636262c2649f9 vs actuallysyncedb73d8b6330cfdb9d83c000a513be7052763aa083;7pending, no further sync. Next: user review, then separately plan pending upstream synthesis and remaining lesson/levels/molecule roadmap.\n\n')
 for name in ['SESSION-NOTES.md','YANNIS-CONTRIBUTIONS.md']:
  p=o.R/'docs'/name;p.write_text(top+o.exact(p).decode())
 for record in s['externalCopies']:
  for name in ['SESSION-NOTES.md','YANNIS-CONTRIBUTIONS.md']:record['files'][name]=o.sha(o.R/'docs'/name)
 s.update(deliveryComplete=True,closingRecordedUTC=stamp,closingMetadataOutsideGitCutoff=True);o.write(o.STATE,s)
 closing={'completedUTC':stamp,'runtimeCommit':s['publicRuntimeCommit'],'reportCommit':s['publicReportCommit'],'checkpointCommit':s['latestRemoteCheckpointCommit'],'welcome':s['finalLink'],'report':s['reportLink'],'lesson':s['lessonLink'],'sourceCutoffUTC':s['sourceCutoffUTC'],'metadataCutoffUTC':s['finalMetadataCutoffUTC'],'closingAfterCutoff':True,'coreChangedDuringSave':False,'sourceHEADIndexPreserved':True,'archives':{**s['archives'],**s['finalMetadataArchives']},'combinedRecoveryVerified':True,'finalReportVisualPassed':True}
 receipt=o.R/'communication/checkpoints'/('Namelecule-'+s['stamp']+'-completed.json');o.write(receipt,closing)
 selected=['docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md',str(o.STATE.relative_to(o.R)),str(receipt.relative_to(o.R))]+[str((H/n).relative_to(o.R))for n in ['combined-bundle-recovery.json','public-final-http.json','pages-status.json','browser/final-report-results.json','final-report-review.json']]
 assert all((o.R/p).is_file()for p in selected)
 frozen=Path(s['job'])/'closing-metadata';assert not frozen.exists();frozen.mkdir();hashes={p:o.copydata(o.R/p,frozen/p)for p in selected}
 archive=o.R/'communication/checkpoints'/('Namelecule-'+s['stamp']+'-closing-metadata.zip');o.h.create_zip(frozen,hashes,archive,{'cutoffUTC':stamp,'files':hashes,'note':'Closing records after full/final-metadata Git cutoffs; no runtime edit.'})
 digest=o.sha(archive)
 for folder in s['externalFolders']:
  d=Path(folder);o.h.verified_copy(archive,d/archive.name);o.h.atomic_bytes((digest+'  '+archive.name+'\n').encode(),d/(archive.name+'.sha256'))
  for p in selected:
   target=d/('Ολοκλήρωση/'+p if not p.startswith('docs/')or Path(p).name not in ['SESSION-NOTES.md','YANNIS-CONTRIBUTIONS.md'] else Path(p).name)
   o.h.verified_copy(frozen/p,target,replace=True,expected=hashes[p])
  o.h.verified_copy(receipt,d/receipt.name)
  assert o.sha(d/archive.name)==digest
 o.invariant(s);print(json.dumps({'deliveryComplete':True,'closingArchive':str(archive),'sha256':digest,'closingRecords':len(selected),'mirrors':2,'coreChanged':False},ensure_ascii=False))
if __name__=='__main__':main()
