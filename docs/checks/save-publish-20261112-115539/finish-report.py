"""Finalize only proven public-runtime and recovery facts; metadata cutoff follows."""
from pathlib import Path
import sys,importlib.util,json,re,datetime
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('release_ops',H/'release-ops.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
R=o.R;s=o.load();o.invariant(s)
assert s.get('saveComplete')and s.get('publicRuntimeLiveVerified')and s.get('publicLiveBrowserPassed')
report=R/s['reportDirectory'];runtime=s['publicRuntimeCommit'];snapshot=s['checkpointSnapshotCommit']
status=('<div class="note" id="publication-status"><strong>Η αποθήκευση και η δημοσίευση της εφαρμογής ολοκληρώθηκαν.</strong> '
+'Η νέα έκδοση επαληθεύτηκε στο GitHub Pages με σύγκριση δημόσιων αρχείων και λειτουργική δοκιμή. '
+'Δημόσια έκδοση <code>'+runtime[:12]+'</code>, πλήρες σημείο επαναφοράς <code>'+snapshot[:12]+'</code>. '
+'Αποθηκεύτηκαν '+str(s['sourceFileCount'])+' αρχεία πηγών και '+str(s['recoveryFileCount'])+' αρχεία ανάκτησης, με ελεγμένα ZIP/Git bundle και αντίγραφα σε δύο νέους χρονολογημένους φακέλους στον ίδιο υπολογιστή. '
+'Η τελική αναφορά και οι μεταγενέστερες αποδείξεις παράδοσης αποθηκεύονται με χωριστό χρονικό όριο. '
+'Η συνεδριακή δοκιμή και η προετοιμασία χωρίς Internet παραμένουν χωριστές εργασίες.</div>')
p=report/'update.html';text=o.exact(p).decode();text,n=re.subn(r'<div class="note pending" id="publication-status">.*?</div>',lambda _:status,text,count=1,flags=re.S);assert n==1
text=text.replace('Δεν άλλαξε το ενεργό JSON του σεναρίου ούτε έγινε νέα εξαγωγή JSON.','Το ενεργό JSON του σεναρίου διατηρεί τα ίδια δεδομένα. Στην πλήρη αποθήκευση επαληθεύτηκε και το αντίστοιχο τρέχον αντίγραφο στον φάκελο «αρχεία json».')
p.write_text(text)
f=json.loads(o.exact(report/'verified-facts.json'));f.update(publicationStatus='RUNTIME_LIVE_VERIFIED',runtimeCommit=runtime,publicRuntimeVerified=True,fullSnapshotCommit=snapshot,sourceFileCount=s['sourceFileCount'],recoveryFileCount=s['recoveryFileCount'],backupFolders=s['externalFolders'],finalizedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),publicationEvidence={'http':str((H/'public-runtime-http.json').relative_to(R)),'pages':str((H/'runtime-pages-status.json').relative_to(R)),'browser':'docs/checks/save-publish-20261112/browser/live-release-results.json'},candidateReleaseChecks=s['candidateBrowserChecks'],reportDeliveryVerification='Final report HTTP verification follows publication of these bytes. Metadata delta and closing receipt use separate cutoffs.')
f['limits']=[v for v in f['limits']if not v.startswith('Publication/save/linkverification pending')]
for fact in f.get('facts',[]):
 if fact['id']=='F08':fact['claim']=fact['claim'].replace('JSON unchanged,no newexport.','JSON unchanged; current Desktop copy byte equality verified during full save.')
o.write(report/'verified-facts.json',f)
l=json.loads(o.exact(report/'links.json'));l['publication_status']='Runtime published and exact-byte/browser verified. Final report delivery proof follows these bytes.';o.write(report/'links.json',l)
lines='Namelecule — 12/11/2026\nΥποδοχή: '+s['finalLink']+'\nΑναφορά καθηγητή: '+s['reportLink']+'\nΜάθημα αλκανίων: '+l['alkane_lesson']+'\nΜοριακό παζλ: '+l['molecular_puzzle']+'\nΧτίσε το όνομα: '+l['name_builder']+'\nΣυνεργείο ονομάτων: '+l['workshop']+'\nΔημόσια έκδοση: '+runtime+'\nΠλήρες σημείο επαναφοράς: '+snapshot+'\n'
for name in ['links.txt','plainlinks.txt']:(report/name).write_text(lines)
(report/'message-to-professor.txt').write_text('Η νέα αναφορά περιγράφει τις βελτιώσεις στο «Χτίσε το όνομα» και το νέο «Μοριακό παζλ», με τρίτη επιλογή παιχνιδιού και ξεκλείδωμα με τρία σωστά μόρια στα δύο σημεία του μαθήματος αλκανίων. Περιλαμβάνονται οι έλεγχοι και οι περιορισμοί. Δεν άλλαξε κανένα αρχείο core.\n\n'+s['reportLink']+'\n\nΥποδοχή εφαρμογής: '+s['finalLink']+'\n')
p=R/'README.md';p.write_text('**Namelecule — 12/11/2026, ενημερωμένη δημόσια v55.** «Μοριακό παζλ» από το όνομα στη δομή, τρίτη επιλογή στα βήματα 4/11 των αλκανίων με τρία διαφορετικά σωστά μόρια, διατήρηση προόδου και προαιρετική εξάσκηση. Βελτιωμένος χειρισμός/οδηγίες και επιστροφή πλακιδίων στο «Χτίσε το όνομα». Η υποψήφια έκδοση και η δημόσια παράδοση επαληθεύτηκαν χωριστά. Πλήρες snapshot `'+snapshot+'`, ελεγμένα ZIP/bundle και δύο χρονολογημένοι φάκελοι αντιγράφων στον ίδιο υπολογιστή. Καμία σημερινή αλλαγή core ή νέα ενσωμάτωση upstream. Η πρόληψη του παγώματος Firefox και η συνεδριακή/offline προετοιμασία παραμένουν εκκρεμείς. [Αναφορά καθηγητή]('+s['reportLink']+') · [Υποδοχή]('+s['finalLink']+').\n\n'+o.exact(p).decode())
paths=[p.relative_to(R).as_posix()for p in report.rglob('*')if p.is_file()]+['README.md',str((H/'public-runtime-http.json').relative_to(R)),str((H/'runtime-pages-status.json').relative_to(R)),'docs/checks/save-publish-20261112/browser/live-release-results.json',str((H/'upstream-audit.json').relative_to(R))]
o.write(H/'final-report-target.json',{'files':{p:o.sha(R/p)for p in paths},'runtimeCommit':runtime,'snapshotCommit':snapshot,'reportLiveVerificationPending':True})
print('Final report target ready:',len(paths),flush=True)
