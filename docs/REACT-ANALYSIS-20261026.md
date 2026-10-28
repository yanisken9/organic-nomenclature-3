# Namelecule React — πάνελ ανάλυσης ονόματος, 26/10/2026

Εγκεκριμένο πεδίο: όνομα σε συνθετικά, κλικ για υπάρχουσα εξήγηση/επισήμανση/
αρίθμηση, για αιθανόλη, 2,3-διμεθυλοβουτάνιο και προπανόνη στις τρεις μορφές2D.
Η προηγούμενη ελεγμένη επέκταση επιλογέα ήταν ήδη στο working tree και διατηρείται.
Βάση Git168e3cec01f941a84d40bbe0dc07156e7baa35d0, branchreact-library-pilot.
Η Κύρια έκδοση στο thesis-work3673c390 παραμένει αμετάβλητη.

## Υλοποίηση

Νέο `react-preview/src/NameAnalysis.jsx` με native buttons, `aria-pressed`,
επεξήγηση σε polite live region και περιορισμένη επικύρωση payload. Το πάνελ
εμφανίζεται δίπλα στον viewer στο desktop και κάτω του στη στενή οθόνη.
Επεκτάθηκαν `MoleculePreview.jsx`, `public/viewer-host-bridge.js`, `preview.css`
και README. Άλλα αρχεία της εφαρμογής δεν άλλαξαν σε αυτή τη φάση.

Τα labels προέρχονται από τα πραγματικά `#nameAnalysis .nameCompBox`, μαζί με την
ήδη εφαρμοσμένη ελληνική ευφωνία· π.χ. «διμεθυλο», όχι δεύτερος υπολογισμός από
τα ακατέργαστα συνθετικά. Η επεξήγηση διαβάζεται από το υπάρχον explainText.
Για τα τρία αυτά μόρια οι εξηγήσεις είναι απλό κείμενο και αποδίδονται ως React
text χωρίς rawHTML. Δεν εισάγεται νέος αλγόριθμος ονοματολογίας ή μαθησιακό υλικό.

Η γέφυραv3 προσθέτει εντολή `component` με έλεγχο υπαρκτού/ορατού componentID και
δέσμευση στο επιλεγμένο μόριο. Καλεί τον αρχικό delegatedclick handler, που
χειρίζεται το toggle-off, τα highlights και την αρίθμηση μέσα στο ίδιο iframe.
Η React αποδέχεται μόνο έγκυρα/bounded/μοναδικά IDs και labels, έως ένα επιλεγμένο
συνθετικό, κείμενο επεξήγησης και απάντηση για το τελευταίο μόριο/μορφή/requestID.
Διατηρούνται loading/error/retry/cleanup και η απόκρυψη παλιών δεδομένων στην
αλλαγή μορίου. Mode/zoom διατηρούν την υπάρχουσα επιλογή, νέο μόριο την καθαρίζει.

Η αρίθμηση χρησιμοποιεί τον αρχικό400ms timer. Δεν γράφτηκε νέος timer React ή
νέα αντιστοίχιση ατόμων. Οι παλιές εξαρτήσεις3D/JSmol παραμένουν, όπως και τα
όρια του same-origin iframe: DOM/lifecycle separation, όχι securitysandbox ή
nativeReact renderer. Δεν προστέθηκαν dependencies.

## Πραγματικοί έλεγχοι Developer

- Build Vite PASS:21modules, JS268.80kB/81.10kB gzip, CSS4.69kB/1.33kB gzip.
- **33/33 ενεργές περιπτώσεις**:11υπαρκτά συνθετικά συνολικά ×3μορφές. Ίδια
  labels/ευφωνία, επεξηγήσεις, selected state και ακριβώς ίδιο SVG geometry/
  text/styles/viewBox/highlight colors/τελικοί αριθμοί με την αμετάβλητη εφαρμογή,
  σε εξισωμένο784×420 viewport και ίδια CSS διάταξη testbaseline.
- **9/9 αρχικές απεικονίσεις** και9rawMOL byte-identical, διατήρηση εμφανώνΗ6/14/6.
- Πραγματικά Enter/Space, επιλογή/ακύρωση, διατήρηση μετά mode/zoom, reset κατά
  αλλαγή μορίου και γρήγορες εντολές συνθετικών/μορίων/μορφών PASS.
- Η αιθανόλη απέκτησε σταδιακά0→1→2 αριθμούς σε0.01/0.44/0.85s στην καταγραφή.
  Οι προηγούμενοι αριθμοί παραμένουν. Πρόκειται για παρατήρηση της υπάρχουσας
  animation, όχι νέο timing requirement ή benchmark.
- Firefox1500px/390px: λειτουργία πάνελ/επιλογέα/zoom0.5–6, resize/nooverflow,
  library9cards/12links, unmount/remount και έξοδος κατά loading PASS.
- Απορρίφθηκαν άγνωστα/wrong-molecule componentIDs και malformed analysis
  (null/empty, μη-stringID, duplicateIDs, δύοactivecomponents, υπερμεγέθες κείμενο).
- Missing-document error event και αρχικό timeout ελέγχθηκαν με faultinjection.
  Πραγματική10s απώλεια ACK: wrong-molecule/malformed payload δεν εμφανίζει παλιό
  γράφο, lateACK δεν αναιρεί failure και retry επαναφέρει defaults. Αυτά δεν
  αποτελούν πραγματικόCDNoutage test.
- Τελική πλήρης εκτέλεση:0JavaScript errors. Source/host parity,20προϋπάρχοντες
  έλεγχοι αναζήτησης, JSsyntax/AST/whitespace/protectedfilehashes PASS.
- Μετά την πλήρη εκτέλεση προσαρμόστηκαν μόνο τα CSS padding/min-width/font του
  πάνελ για να μένουν όλα τα συνθετικά σε μία γραμμή στα1500/390px. Το δοκιμασμένο
  JavaScript παραμένει byte-identical(SHA25622b1592f6fbb6d6ba77815383f18be223729b63708fdf5e830570bd7677295cd).
  Ακολούθησαν6στοχευμένοι έλεγχοι τελικήςδιάταξης: ίδιεςεξηγήσεις, μίαγραμμή,
  targets≥44×48, χωρίςoverflow, ίδιοviewportviewer.

Αποδεικτικά: `docs/checks/react-analysis-{browser,layout,static}-20261026.json`,
`test-react-analysis-browser-20261026.py` (πλήρης εκτέλεση ή `--layout-only`).
Screenshots: `/tmp/react-analysis-*-20261026.png`.

Αμετάβλητα1266προϋπάρχοντα nonReactαρχεία εκτός δύοjournals έναντι του snapshot
πριν από αυτή τη φάση, μαζί με core/viewer/data/MOL/SDF/HTML και12scenarioJSONs.
Τα προϋπάρχοντα μη-committed αρχεία επιλογέα δεν αποδίδονται ως νέα συνεισφορά.
Δεν επαναλήφθηκε πλήρες126molecule/283step chemistry/lesson suite ούτε έγιναν
Safari/Drupal/offline/screen-reader tests. Δεν τεκμαίρεται γενική IUPAC ή
παιδαγωγική πιστοποίηση από τους ελέγχους συμβατότητας αμετάβλητου περιεχομένου.

## Ανεξάρτητο review / αποθήκευση

Το ακριβές τελικό αντικείμενο review, περιλαμβάνοντας τα προγενέστερα αρχεία
επιλογέα που παραμένουν στο workingtree, καταγράφεται στο
`docs/checks/react-analysis-reviewed-target-20261026.json`. Αποτελέσματα Reviewer,
ταυτότητα και αποθήκευση καταγράφονται στα SESSION-NOTES/YANNIS-CONTRIBUTIONS.
Τα παραπάνω browser/build αποτελέσματα αποδίδονται στον Developer.
Δεν έγινε νέο commit/push/publication. Core51 παραμένει SHA256
`096d617853646de0dfd67bcbde3e32252aebcb98e7525b05e6f7e71ccb48a5fc`.
