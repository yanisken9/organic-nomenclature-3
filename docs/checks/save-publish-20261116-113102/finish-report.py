"""Finalize the factual delivery section only after measured release evidence."""
from pathlib import Path
import sys, importlib.util, json, re, datetime, ast
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('release_ops',H/'release-ops.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
def main():
 s=o.load();o.invariant(s)
 assert s.get('saveComplete') and s.get('publicRuntimeLiveVerified') and s.get('publicLiveBrowserPassed') and s.get('independentReviewComplete')
 report=o.R/s['reportDirectory'];runtime=s['publicRuntimeCommit'];snapshot=s['checkpointSnapshotCommit']
 status=('<section id="delivery" class="note" aria-label="Κατάσταση παράδοσης"><strong>Η αποθήκευση και η δημοσίευση της εφαρμογής ολοκληρώθηκαν.</strong> '
 'Η v57 επαληθεύτηκε στο GitHub Pages με σύγκριση αρχείων και πραγματική πλοήγηση. Δημόσια έκδοση <code>'+runtime+'</code>, πλήρες σημείο επαναφοράς <code>'+snapshot+'</code>. '
 'Αποθηκεύτηκαν '+str(s['sourceFileCount'])+' αρχεία πηγών και '+str(s['recoveryFileCount'])+' αρχεία ανάκτησης, με ελεγμένα ZIP/Git bundle και δύο νέους χρονολογημένους φακέλους στον ίδιο υπολογιστή. '
 'Το μεγάλο διαγνωστικό αρχείο παραμένει αυτούσιο στο ZIP· στο Git αποθηκεύεται αναστρέψιμα συμπιεσμένο με οδηγία επαναφοράς λόγω του ορίου μεγέθους του GitHub. '
 'Η τελική αναφορά και οι μεταγενέστερες αποδείξεις παράδοσης συμπληρώνονται με χωριστό χρονικό όριο. Τα αντίγραφα είναι στον ίδιο υπολογιστή· ο αντιγραμμένος εκκινητής αναφέρεται στην αρχική θέση του έργου. Δεν αποτελούν ανεξάρτητο δίσκο ή πιστοποιημένο πακέτο χωρίς Internet.</section>')
 p=report/'update.html';text,n=re.subn(r'<section id="delivery".*?</section>',lambda _:status,o.exact(p).decode(),count=1,flags=re.S);assert n==1;p.write_text(text)
 f=json.loads(o.exact(report/'verified-facts.json'));f.update(publicationStatus='RUNTIME_LIVE_VERIFIED',delivery={'runtimeCommit':runtime,'snapshotCommit':snapshot,'sourceFiles':s['sourceFileCount'],'recoveryFiles':s['recoveryFileCount'],'folderNames':[Path(v).name for v in s['externalFolders']],'publicHTTPFiles':s['publicRuntimeHTTPCount'],'browserEvidence':s['publicBrowserEvidence'],'metadataCutoffSeparate':True,'checkpointLargeFilesLosslesslyEncoded':True,'launcherReferencesOriginalProject':True},finalizedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());f['core']['publicationPending']=False
 f['scenarioExport']='Current source scenario and existing Desktop export are byte-identical, verified during full save; no lesson data edited by this save.'
 f['reportChecksPending']=['Final report bytes after this factual update require their own publication and HTTP verification; closing receipt follows metadata cutoff.']
 f['reportAuthorChecks'].append('Release coordinator completed candidate visual QA and independent release review; actual public runtime/browser and two mirror proofs recorded separately.')
 o.write(report/'verified-facts.json',f)
 l=json.loads(o.exact(report/'links.json'));l['publication_status']='Runtime published and exact-byte/browser verified; final report proof follows its own publication.';o.write(report/'links.json',l)
 lines='Namelecule — 16/11/2026\nΥποδοχή: '+s['finalLink']+'\nΑναφορά καθηγητή: '+s['reportLink']+'\nΜάθημα αλκανίων: '+s['lessonLink']+'\n'+''.join(k+': '+l[k]+'\n'for k in ['molecular_detective','molecular_puzzle','name_builder','workshop'])+'\nΔημόσια έκδοση: '+runtime+'\nΠλήρες σημείο επαναφοράς: '+snapshot+'\n'
 for name in ['links.txt','plainlinks.txt']:(report/name).write_text(lines)
 # Only explicit public evidence; do not expose source bookkeeping or backup state.
 paths=[p.relative_to(o.R).as_posix()for p in report.iterdir()if p.is_file()]+[str((H/n).relative_to(o.R))for n in ['public-runtime-http.json','runtime-pages-status.json','browser/public-results.json','release-review.json']]
 assert all((o.R/p).is_file()for p in paths)
 o.write(H/'final-report-target.json',{'files':{p:o.sha(o.R/p)for p in paths},'runtimeCommit':runtime,'snapshotCommit':snapshot,'reportLiveVerificationPending':True})
 print(json.dumps({'finalReportFiles':len(paths),'runtime':runtime,'snapshot':snapshot}))
if __name__=='__main__': main()
