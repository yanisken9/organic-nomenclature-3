# Αρχική παραγωγή φόντου και χαρακτήρων SVG — 31/10/2026

## Εντολή και όρια

Ο χρήστης ζητά λύση στην τεκμηριωμένη αιτία, όχι επέκταση προσωρινών masks.
Εγκρίθηκε read-only διερεύνηση από Developer και ανεξάρτητη αξιολόγηση Reviewer.
Δεν εγκρίθηκε αλλαγή βιβλιοθήκης ή γενίκευση της διόρθωσης στα αλκένια. Το
προηγούμενο propene-only padding παραμένει τοπική αντιμετώπιση, όχι τεκμηρίωση
ότι διορθώθηκε ο αρχικός παραγωγός. Δεν αναιρέθηκε σιωπηρά.

## Πόρισμα Developer για το συγκεκριμένο αναπαραγόμενο φαινόμενο

Η ασυμφωνία εμφανίζεται ήδη στην ΑΡΧΙΚΗ παραγωγή SVG του JSME, με το ίδιο
annotated MOL σε ελάχιστη σελίδα που δεν φορτώνει Namelecule viewer/core/data,
JSmol ή άλλον postprocessor. Τα CSS δεν είναι αναγκαία για την αναπαραγωγή.
Επομένως το πρόβλημα του εξετασμένου rawSVG δεν εισάγεται από το δικό μας fit
ή από την επεξεργασία των λευκών φόντων. Αυτό δεν αποδεικνύει τι είχε φορτώσει
ο καθηγητής στη δική του επίδειξη· το ορατό κενό που είδε ο χρήστης γίνεται
δεκτό και η πραγματική εκείνη διεύθυνση/browser/γραμματοσειρά παραμένουν άγνωστα.

Στον εγκατεστημένο παραγωγό, το ύψος για τα labels προκύπτει από διαφορά
ascent−descent που έχει ήδη περικοπεί σε ακέραιες μονάδες. Ο ίδιος αριθμός
χρησιμοποιείται στην τοποθέτηση baseline και στον υπολογισμό του backplate.
Η πραγματική ζωγραφισμένη κεφαλαία μορφή στο SVG δεν μετριέται σε αυτό το βήμα.
Για τη συγκεκριμένη Helvetica/Firefox δοκιμή, ο υπολογισμός υποεκτιμά το άνω
όριο του C. Πρόκειται για αιτιακό μηχανισμό και ακριβή αναπαραγωγή των τιμών
του rawSVG, όχι για δοκιμασμένη γενική διόρθωση όλων των glyphs/πλατφορμών.

## Ιχνηλάτηση στον πραγματικά φορτωμένο κώδικα

Ο loader είναι jsme/jsme.nocache.js. Ο isolatedFirefox φόρτωσε
jsme/FEB169D74546A3B279D22AE09AFB86BD.cache.js (runtime resource entries σταJSON).
Το 96E40B969193BD74B8A621486920E79C.cache.js που είχε δειγματοληπτηθεί νωρίτερα
είναι Inchi auxiliary και δεν επαρκεί για έλεγχο ολόκληρου του ενεργού JSME.

Στο εγκατεστημένο compiled module (source excerpts με SHA/offset/decodedline):
- UR επιλέγει τη ζητούμενη γραμματοσειρά Helvetica και font size9.
- oL μετρά DOM font metrics με δείγμα Q στα300px. mL/nL τα αναγάγουν στο font
  size με ~~ truncation. Δεν είναι μέτρηση πραγματικού ink του τελικού C/H.
- CQ επιστρέφει mL(font)−nL(font).
- EQ χρησιμοποιεί c=CQ(...), rect height=c+4 και baseline−rectTop=c+2.
- ZP/BQ μετατρέπουν στο εσωτερικό SVG scale30. Το τελικό text ζητά270μονάδες.

Μεfont9 οι metrics αναφέρουν ascent6/descent2: c=4, άρα height8×30=240,
baseline−rectTop6×30=180. Το μετρημένο C στα270SVGunits ανεβαίνει200,4140625.
Το backplate συνεπώς υπολείπεται20,4140625SVGunits, πριν από κάθε δικό μας fit.
Αυτό προβλέπει τις παρατηρημένες τιμές. Η ταύτιση υπολογισμού/εξαγωγής εντοπίζει
τη συγκεκριμένη υποεκτίμηση· δεν αποδεικνύει ότι αρκεί μια αλλαγή rounding ή
μια νέα σταθερά. Η διάταξη κειμένου και φόντου πρέπει να παραμείνει συνεπής.

## Απομονωμένα πειράματα Developer

23native checks σε πραγματικό isolatedFirefox, αμετάβλητη εφαρμογή:
-15cases: plain/localCSS/professorCSS μεfont9/10/11/12, και3line-height variants.
  Στοfont9 όλα παράγουν ίδια geometry/metrics: maskAscent180 έναντι ink200,414.
  Οι plain σελίδες δεν περιλαμβάνουν viewer ή δικό μας φόντο/mask helper.
-8cases: installed2023-07-31 και επίσημη διανομή2024-04-29, font9/12/14/16.
  Η επίσημη έκδοση φορτώθηκε πραγματικά από τον δικό της loader/CDN, με ενεργό
  4277561D0E87B89F4DFCCC3A712D5B19.cache.js· όχι απλή αλλαγή ετικέτας έκδοσης.
  Ίδιες μετρήσεις στις δύο διανομές. Η απλή αναβάθμιση σε αυτή δεν επαρκεί.
- font12: mask270 έναντι C265,254 (μικρό θετικό υπόλοιπο4,746).
  font14: mask270 έναντι C309,463 (ξανά αρνητικό−39,463).
  font16: mask330 έναντι C353,672 (αρνητικό−23,672).
  Επομένως η αύξηση γραμματοσειράς δεν αποτελεί μονοτονική/ανθεκτική λύση.
-0καταγεγραμμένα JavaScript errors στα δύο native runs. Δεν φορτώνουν JSmol,
  άρα δεν ελέγχουν ούτε επιλύουν την ξεχωριστή null-viewer εκκρεμότητα.
- Το πρώτο probe κάλεσε ανύπαρκτο getter και σταμάτησε· διορθώθηκε μόνο ο
  διαγνωστικός κώδικας για ανάγνωση της εγκατεστημένης δομής. Η εφαρμογή δεν
  άλλαξε. Τα final23cases είναι οι ολοκληρωμένες εκτελέσεις, όχι το failedprobe.
- Canvas TextMetrics παρέχει το τελικό ink bound· δεν έγινε νέο raster test
  όλων των glyphs/γραμμών σε αυτή τη μονάδα. Τα παλαιότερα raster ευρήματα
  παραμένουν χωριστά. Δεν παρουσιάζονται ως εκτέλεση του Reviewer.

## Επίσημες πηγές και ρυθμίσεις

https://jsme-editor.github.io/dist/doc.html περιγράφει atombgsize ως μέγεθος
του background CIRCLE επισήμανσης. Δεν είναι ρύθμιση της λευκής αποκοπής γύρω
από το glyph. Η δοκιμή δεν το μπέρδεψε με το white backplate.
https://jsme-editor.github.io/dist/api_javadoc/export/client/JSME.html περιγράφει
getMolecularAreaGraphicsString ως το graphics που χρησιμοποιεί το molecular
area. setAtomMolecularAreaFontSize είναι διαθέσιμο, όπως επιβεβαιώθηκε runtime.
Δεν εντοπίστηκε documentedAPI για διόρθωση των συγκεκριμένων font-metric/white-
backplate υπολογισμών· δεν ισχυριζόμαστε ότι εξαντλήθηκε κάθε πιθανή επέκταση.
Officialbootstrap/permutation downloads καταγράφονται μεURL/HTTP/SHA. Η δοκιμή
jme/JME.html επέστρεψε404· η export/client/JSME.html ήτανHTTP200 και χρησιμοποιήθηκε.
Δεν έγινε install/update dependency ή αποστολή issue/μηνύματος στους δημιουργούς.

## Επόμενο πλάνο — προς διατύπωση/έγκριση, όχι υλοποιημένο

Δεν συνιστάται να επεκταθεί το per-series padding ως δήθεν root fix, να επιλεγεί
τυχαίο μεγαλύτεροfont ή να αναβαθμιστεί η βιβλιοθήκη χωρίς επιβεβαίωση.
Χρειάζεται απομονωμένο prototype στον κοινό παραγωγό label geometry, ώστε
θέση κειμένου και backplate να υπολογίζονται από συνεπή πραγματικά font bounds.
Πριν από παραγωγική αλλαγή, πρέπει να οριστούν συγκεκριμένα αρχεία/συντήρηση
της βιβλιοθήκης, fallback όταν metrics δεν διατίθενται, κόστος/σταθερότητα και
έλεγχοι για C/H αλλά και N/O/halogens/subscripts/superscripts, όλα τα modes,
shortenedalkanes, highlights, atom mapping και presentation/export. Ένας γενικός
υπολογισμός δεν αποδεικνύεται σωστός μόνο από το προπένιο. Δεν γράφτηκε patch
σε compiled vendor/module ή στον viewer σε αυτή την έρευνα.

## Όρια και κατάσταση

Επαληθευμένα5runtime/policy αρχεία και Gitindex παρέμειναν ίδια. SourceHEAD
168e3cec01f941a84d40bbe0dc07156e7baa35d0. Core52SHA
d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2, ίδιο σε όλητησυνεδρία.
Δεν γενικεύουμε το πόρισμα σε πραγματικό Windows/Safari/Chrome ή κάθε resolved
font face· αυτά δεν εκτελέστηκαν. Δεν επαληθεύτηκε conference-ready release.
Τα αρχεία είναι έρευνα/τεκμήρια, όχι νέα παραγωγική λειτουργία. No commit/push/
publication/upstreamsync. Ανεξάρτητος Reviewer ολοκλήρωσε τον έλεγχο αιτιολόγησης/ορίων χωρίς ευρήματα.

## Ολοκλήρωση ανεξάρτητου ελέγχου

Reviewer /root/review_svg_root_20261031, ROLE_ID NAMELECULE_REVIEWER_V1_20261023,
σε νέο context: κανένα actionableP0/P1/P2/P3 εύρημα. ManifestSHA
b2f9119f5da07e0f912f1de9619826bd59c0674efba79f827eb0bb7dfad1b6f6.
Ανεξάρτητα επαλήθευσε hashes12deliverables/5runtime/5temporarysources πριν/μετά,
αποκωδικοποίησηstringliterals,23case αριθμητικές σχέσεις και πραγματικές vendor/
viewer κλήσεις. Επίσημο atombgsize/API επιβεβαιώθηκαν. Native browser observations
είναι Developer evidence, όχι ανεξάρτητο runtime. Άλλοιbrowser/font/raster και
JSmol/καθολικήετοιμότητα συνεδρίου δεν πιστοποιούνται. Πόρισμα κατάλληλο για νέο
συγκεκριμένο πλάνο, όχι claimέτοιμηςδιόρθωσης. Μετά το review άλλαξαν μόνο
παρούσα statusενότητα και continuityrecords· ερευνητικά τεκμήρια/παραγωγικές
πηγές διατηρήθηκαν. Ακριβές reviewrecord στο checks/svg-text-root-20261031/.
