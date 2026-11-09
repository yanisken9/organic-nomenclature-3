# Namelecule React — επιλογή τριών μορίων, 26/10/2026

Εγκεκριμένο βήμα: επέκταση της δοκιμής αιθανόλης με επιλογέα τριών υπαρχόντων
μορίων, διατήρηση των τριών 2D μορφών και zoom. Βάση:
`168e3cec01f941a84d40bbe0dc07156e7baa35d0`, branch `react-library-pilot`.
Η Κύρια έκδοση στο `thesis-work` παραμένει `3673c390`.

| Μόριο | Υπάρχον ID | Μοριακός τύπος |
|---|---|---|
| Αιθανόλη | `ethanol` | C₂H₆O |
| 2,3-διμεθυλοβουτάνιο | `dimethyl_2_3_butane` | C₆H₁₄ |
| Προπανόνη | `propanone` | C₃H₆O |

## Συμπεριφορά και όρια

Ο νέος κοινός κατάλογος `react-preview/src/molecules.json` χρησιμοποιείται από
React και host generator, ώστε ο επιλογέας και τα επιτρεπόμενα IDs της γέφυρας
να προέρχονται από μία πηγή. Περιέχει μόνο IDs/τίτλους/τύπους, όχι νέο μοριακό
γράφο, MOL ή συντεταγμένες. Ο υπάρχων μηχανισμός παραμένει η πηγή της δομής.

Η επιλογή μορίου καλεί το υπάρχον `fSelectMol` στο ίδιο iframe, κρατά τη μορφή
2D και επαναφέρει το zoom στο 2, όπως η Κύρια έκδοση. Μέχρι να επιβεβαιωθεί η
αλλαγή, ο προηγούμενος γράφος κρύβεται. Απάντηση εμφανίζεται μόνο όταν συμφωνούν
session/source/origin, τελευταίο request ID, επιλεγμένο μόριο και μορφή. Ο χρήστης
μπορεί να αλλάξει ξανά επιλογή όσο περιμένει, χωρίς reload του iframe.

Επεκτάθηκε μόνο το επιτρεπόμενο πρωτόκολλο σε `namelecule-viewer-v2` με εντολή
`molecule`, πέρα από `mode`/`zoom`. Διατηρούνται cleanup, αρχική προθεσμία 90s,
προθεσμία εντολής 10s, τερματικό σφάλμα, retry/fallback και `aria-busy` μόνο όσο
εκκρεμεί πραγματική εργασία. Retry/remount επαναφέρει αιθανόλη/συνεπτυγμένο/zoom2.

Αρχεία κώδικα: `MoleculePreview.jsx`, `molecules.json`, `main.jsx`, `preview.css`,
`public/viewer-host-bridge.js`, `tools/build-viewer-host.py`, εντός react-preview.
Σχετικά docs/evidence/tests προστέθηκαν· αρχικά core/viewer/data/HTML/MOL/SDF και
τα 12 εκπαιδευτικά σενάρια δεν τροποποιήθηκαν. Δεν προστέθηκαν dependencies.
Ο καταγεγραμμένος κώδικας δεν εισάγει νέα χημική ή εκπαιδευτική λειτουργία.

Παραμένει iframe με το πλήρες παλιό startup/JSmol/CDN και την υπάρχουσα διαδρομή
3D φόρτωσης, παρότι προσφέρεται μόνο 2D UI. Δεν είναι native React renderer ή
πακέτο αποκλειστικά 2D. Η απομόνωση αφορά DOM/lifecycle, όχι security sandbox.
Η κλίμακα/γραμματοσειρές/γωνίες/ρητά Η διατηρούνται από την αρχική απόδοση.

## Έλεγχοι Developer

- Vite build PASS: 20 modules, JS267.14kB/80.67kB gzip, CSS3.66kB/1.09kB gzip.
- Source catalog parity: 9 καρτέλες/12 μαθήματα. 20 υπάρχοντες έλεγχοι αναζήτησης PASS.
- Πραγματικό Firefox στα1500px/390px: 3 μόρια ×3 μορφές, επιλογέας/τίτλος/τύπος,
  αλλαγή χωρίς reload, διατήρηση μορφής/reset zoom, όρια0.5–6, γρήγορες μικτές
  αλλαγές μορφής/μορίου, απόρριψη άγνωστων IDs/μηνυμάτων, resize/no overflow,
  βιβλιοθήκη/επιστροφή και unmount/remount/έξοδος ενώ φορτώνει.
- Εννέα raw MOL byte-identical και εννέα SVG geometry/text/styles/viewBox ακριβώς
  ίδια με την αμετάβλητη Κύρια έκδοση σε εξισωμένο958×420 viewport και ίδια CSS
  διάταξη του test baseline. Η σύγκριση δεν αφορά όλα τα126μόρια.
- Στα9MOL ελέγχθηκαν τα ουδέτερα C/H/O σθένη, οι μοριακοί τύποι και η ισομορφία
  του γράφου βαρέων ατόμων μεταξύ μορφών, με διατήρηση τάξεων δεσμών. Δεν είναι
  καθολικός MOL/IUPAC validator. Τα εμφανιζόμενα Η είναι αντίστοιχα6/14/6. Στην
  αιθανόλη διατηρείται το υπάρχον OH label και τα5ρητά Η του expandedMOL.
- Error/retry μέσω πραγματικού missing-document navigation και εισαγόμενου error
  event· αρχικό timeout με ενεργοποίηση της πραγματικής callback χωρίς αναμονή90s.
  Επιπλέον, απώλεια επιβεβαίωσης νέου μορίου με ελεγχόμενη απόκρυψη ACK: ο γράφος
  μένει κρυμμένος, λάθος molecule reply απορρίπτεται, πραγματική αναμονή10s οδηγεί
  σε σφάλμα, late ACK δεν το αναιρεί και retry επαναφέρει την αρχική κατάσταση.
  Πρόκειται για ελεγχόμενα fault injections, όχι πραγματικό CDN outage.
- Έλεγχος προστασίας1259προϋπαρχόντων αρχείων εκτός React/δύο journals, μαζί με
  core51 και stable branch· AST/JS syntax/generator parity/whitespace.
- Τελική εκτέλεση: 0 JavaScript errors. Δεν αποτελεί τεκμήριο διόρθωσης JSmol.

Αποδεικτικά: `docs/checks/react-molecules-{browser,static,graphs}-20261026.json`,
`test-react-molecules-{browser,static}-20261026.py`. Screenshots στο
`/tmp/react-molecules-*-20261026.png`. Οι καταγραφές περιέχουν τα πραγματικά errors
και αποτελέσματα· η εκτέλεση δεν πιστοποιεί διόρθωση των παλιών JSmol σφαλμάτων.
Δεν έγινε νέο πλήρες283-step/126-molecule suite, Safari, Drupal, offline ή
screen-reader test. Οι χρόνοι φόρτωσης στο JSON δεν αποτελούν benchmark.

## Ανεξάρτητος έλεγχος και αποθήκευση

Το ακριβές αντικείμενο review καταγράφεται στο
`docs/checks/react-molecules-reviewed-target-20261026.json`. Ταυτότητα Reviewer,
ευρήματα/διορθώσεις/αποτελέσματα και τελική κατάσταση αποθήκευσης καταγράφονται
στα SESSION-NOTES/YANNIS-CONTRIBUTIONS μετά το review. Το παρόν αποδίδει τα
runtime/build αποτελέσματα στον Developer. Δεν έγινε push ή δημοσίευση.
Core51 παραμένει SHA256
`096d617853646de0dfd67bcbde3e32252aebcb98e7525b05e6f7e71ccb48a5fc`.
