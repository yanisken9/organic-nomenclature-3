"""Finalize factual report content after actual runtime delivery proof."""
from pathlib import Path
import sys,importlib.util,json,re,datetime
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('release_ops',H/'release-ops.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
R=o.R;s=o.load();o.invariant(s)
assert s.get('saveComplete')and s.get('publicRuntimeLiveVerified')and s.get('publicLiveBrowserPassed')
report=R/s['reportDirectory'];runtime=s['publicRuntimeCommit'];snapshot=s['checkpointSnapshotCommit']
status=('<div class="note" id="publication-status"><strong>Η αποθήκευση και η δημοσίευση της εφαρμογής ολοκληρώθηκαν.</strong> '
 +'Η νέα έκδοση επιβεβαιώθηκε στο GitHub Pages με έλεγχο των δημόσιων αρχείων και λειτουργική δοκιμή. '
 +'Δημόσια έκδοση <code>'+runtime[:12]+'</code>, πλήρες σημείο επαναφοράς <code>'+snapshot[:12]+'</code>. '
 +'Αποθηκεύτηκαν '+str(s['sourceFileCount'])+' αρχεία πηγών και '+str(s['recoveryFileCount'])+' αρχεία ανάκτησης, '
 +'με ελεγμένα ZIP/Git bundle και αντίγραφα σε δύο χρονολογημένους φακέλους στον ίδιο υπολογιστή. '
 +'Η τελική αναφορά και οι μεταγενέστερες αποδείξεις παράδοσης αποθηκεύονται επιπλέον με χωριστό χρονικό όριο. '
 +'Δεν πρόκειται για πιστοποιημένο offline πακέτο ή εγγύηση αδιάλειπτης παρουσίασης.</div>')
p=report/'update.html';text=o.exact(p).decode();text,n=re.subn(r'<div class="note pending" id="publication-status">.*?</div>',lambda m:status,text,count=1,flags=re.S);assert n==1
text=text.replace('αντικατάσταση ερωτηματικού με κόμμα','αντικατάσταση του χαρακτήρα «;» με κόμμα')
text=text.replace('Ολοκληρώθηκαν 44 εστιασμένοι λειτουργικοί έλεγχοι Firefox: και τα δύο παιχνίδια/βήματα,','Οι τελικές εστιασμένες επαληθεύσεις περιλαμβάνουν 44 ελέγχους Firefox. Οι καταγεγραμμένες εκτελέσεις καλύπτουν και τα δύο παιχνίδια/βήματα,')
p.write_text(text)
f=json.loads(o.exact(report/'verified-facts.json'));f.update(publicationStatus='RUNTIME_LIVE_VERIFIED',runtimeCommit=runtime,publicRuntimeVerified=True,fullSnapshotCommit=snapshot,sourceFileCount=s['sourceFileCount'],recoveryFileCount=s['recoveryFileCount'],backupFolders=s['externalFolders'],finalizedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),reportDeliveryVerification='Performed after these report bytes are published; closing receipt is saved in both backup folders, outside archive cutoffs.',candidateReleaseChecks=48)
f.pop('reportPublicVerified',None)
f['limits']=[v for v in f['limits']if not v.startswith('No backup counts/')]
f['facts']=[v for v in f['facts']if v['id']!='F12']
f['deliveryEvidence']={'http':'docs/checks/save-publish-20261111-113832/public-runtime-http.json','pages':'docs/checks/save-publish-20261111-113832/runtime-pages-status.json','browser':'docs/checks/save-publish-20261111-113832/browser/live-release-results.json'};o.write(report/'verified-facts.json',f)
l=json.loads(o.exact(report/'links.json'));l['publication_status']='Runtime published and live-byte/browser verified. Final report delivery verification recorded separately after publication.';o.write(report/'links.json',l)
lines='Namelecule — 11/11/2026\nΥποδοχή: '+s['finalLink']+'\nΑναφορά καθηγητή: '+s['reportLink']+'\nΜάθημα αλκανίων: '+l['alkane_lesson']+'\nΧτίσε το όνομα: '+l['name_builder']+'\nΣυνεργείο ονομάτων: '+l['workshop']+'\nΔημόσια έκδοση: '+runtime+'\nΠλήρες σημείο επαναφοράς: '+snapshot+'\n'
for name in ['links.txt','plainlinks.txt']:(report/name).write_text(lines)
(report/'message-to-professor.txt').write_text('Η ενημερωμένη αναφορά περιγράφει το νέο «Χτίσε το όνομα», τις δύο επιλογές παιχνιδιού στην υποδοχή και στις στάσεις του μαθήματος αλκανίων, μαζί με τους ελέγχους και τους γνωστούς περιορισμούς. Δεν άλλαξε κανένα αρχείο core.\n\n'+s['reportLink']+'\n\nΥποδοχή εφαρμογής: '+s['finalLink']+'\n')
readme=R/'README.md';readme.write_text('**Namelecule — 11/11/2026, ενημερωμένη δημόσια v55.** Νέο «Χτίσε το όνομα», πρόσβαση στα δύο παιχνίδια από την υποδοχή και επιλογή παιχνιδιού στις δύο στάσεις αλκανίων, με τρία διαφορετικά σωστά μόρια στο επιλεγμένο παιχνίδι. Η υποψήφια έκδοση πέρασε 48 ελέγχους Firefox και η δημόσια παράδοση επαληθεύτηκε χωριστά. Πλήρες snapshot `'+snapshot+'`, ελεγμένα ZIP/bundle και δύο χρονολογημένοι φάκελοι αντιγράφων στον ίδιο υπολογιστή. Καμία σημερινή αλλαγή core ή νέα ενσωμάτωση upstream. Οι γνωστοί περιορισμοί JSmol και η ανάγκη ξεχωριστής συνεδριακής προετοιμασίας παραμένουν. [Αναφορά καθηγητή]('+s['reportLink']+') · [Υποδοχή]('+s['finalLink']+').\n\n'+o.exact(readme).decode())
paths=[p.relative_to(R).as_posix()for p in report.rglob('*')if p.is_file()]+['README.md','docs/checks/save-publish-20261111-113832/public-runtime-http.json','docs/checks/save-publish-20261111-113832/runtime-pages-status.json','docs/checks/save-publish-20261111-113832/browser/live-release-results.json']
o.write(H/'final-report-target.json',{'files':{p:o.sha(R/p)for p in paths},'runtimeCommit':runtime,'snapshotCommit':snapshot,'reportLiveVerificationPending':True})
print('Final report target ready:',len(paths),flush=True)
