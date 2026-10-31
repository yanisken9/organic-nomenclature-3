# Προπένιο — έλεγχος επαφής κατακόρυφου C–H — 31/10/2026

Ο χρήστης προσδιόρισε ότι η φωτογραφία αφορά προπένιο, όχι αλκάνιο. Ζητά
διάγνωση της επαφής του επάνω δεσμού με τον αριστερό C σε σύγκριση με τον καθηγητή.
Έγινε μόνο έλεγχος και καταγραφή· καμία αλλαγή εφαρμογής/MOL/core ή συγχρονισμός.

Developer πραγματικός Firefox, απομονωμένο profile/server8022, τοπική πηγή και
αυτούσιο git archive του καθηγητή4e1190ab3d58f5eb384f1583bfe05e37242bef61.
Ίδιο expanded MOL byte-for-byte. ΠρώτοςC και rawJSME/finalSVG και στις δύο
πηγές: Helvetica270 SVGunits, mask width330/height240, maskTop=baseline−180.
Μετρημένα Canvas ink bounds έναντι native mask: topGap−1,663px local και
−1,361px upstream στα διαφορετικά αρχικά μεγέθη. Αρνητικό gap σημαίνει ότι
το mask τελειώνει μέσα στο πραγματικό όριο του γράμματος. Η δική μας
postprocessing ακολουθία δεν μεταβάλλει αυτά τα σχετικά όρια στο προπένιο.
Προηγούμενος fPadExpandedAlkaneLabels εξαιρεί σωστά τη σειρά alkenes.

Έγινε οπτική σύγκριση εξαγόμενων SVG σε κοινό font47px με ίδια αναλογία:
και τα δύο παρουσιάζουν την επαφή. Η αρχική προσωρινή HTML απέτυχε να εμφανίσει
namespaced SVG και διορθώθηκε μόνο ο namespace wrapper πριν την τελική εικόνα.
Δεν τεκμηριώνεται αποκλειστική τοπική παλινδρόμηση· η πραγματική σελίδα/browser/
έκδοση του καθηγητή που είδε ο ίδιος δεν δόθηκε. Δεν ισχυριζόμαστε ίδια εμφάνιση
σε κάθε browser. Αρχεία baseline/comparison/structural-proof και same-scale.png
στο docs/checks/propene-gap-investigation-20261031/. Αυτοί είναι έλεγχοι Developer,
όχι ανεξάρτητο review. Δεν υλοποιήθηκε διόρθωση που να χρειάζεται Reviewer.

Πλάνο προς έγκριση: πρώτη δοκιμή μόνο Expanded προπενίου στον viewer52,
με μικρό θετικό περιθώριο στα πραγματικά όρια των C/H και διατήρηση των native
atom anchors/γραμμών/MOL. Cache URL στο HTML52. Χρήση κοινού μηχανισμού mask
με σαφές gate, χωρίς σιωπηρή επέκταση στα υπόλοιπα μόρια. Έλεγχοι desktop/narrow,
zoom/rebuild/highlight/numbering, export, σύγκριση γραμμών/πηγών και guards
αλκανίων/άλλωνμορφών. Ένα ανεξάρτητο Reviewer μετά το εγκεκριμένο unit.
Δεν έχει εγκριθεί ούτε εφαρμοστεί ακόμη. Περαιτέρω γενίκευση νέο scope.

Έλεγχος professor upstream: προηγούμενο checked a9284c5f43e9e539674f3fa2df59b690066199b9,
νέο HEAD4e1190ab3d58f5eb384f1583bfe05e37242bef61, fetch επιτυχές.4νέαcommits:
ca9518b narrationpacing/movehelpers,5b47c49 esteracidguard/explainreserve/
voicehelper/fullstepdefaults,e44bac8 locantemphasis,4e1190a dimmedlightblue.
CHANGELOG έχει2ενότητες30/10. Επικαλύψεις core52/teaching52 narration και
esterstem, viewer52 numbering/explain και scenario52 defaults. Δεν περιέχουν
διόρθωση των native masks. Lastactuallysynced93b759f5891d7b5a1172646032d83215d60b7604
παραμένει ίδιο· δεν δηλώνεται sync νέου upstream. Ο συγχρονισμός δεν εντάχθηκε
σιωπηρά στη διάγνωση· χρειάζεται ξεχωριστή παρουσίαση με διατήρηση Namelecule.

SourceHEAD168e3cec01f941a84d40bbe0dc07156e7baa35d0 και indexSHA25c212236906eff396f0a3521653f16eea1f5d57dfc5e32ba4477ad25930f964 ίδια.
Core52SHA d2138418ff630ab77e578b80ca8ba3a10cc1b877c3ab8c0e5c2735ffcd1f24a2 ίδιο.
Καμία αλλαγή core στη συνεδρία. Χωρίς commit/push/publication. Τα χθεσινά
reviewed/saved αλκάνια παραμένουν αμετάβλητα. Επόμενο: απόφαση χρήστη για δοκιμή.

## Follow-up — strict comparison only; actual public page opened

User explicitly declines changes and proposals, requests strict comparison.
He confirms he saw the professor's display with a visible gap; this firsthand
observation is accepted. Exact demonstrated URL/browser are not remembered.
The earlier git-archive comparison does not establish what was on that screen.
The earlier proposed fix is withdrawn from the next action; no code approval.

Opened actual https://nick-charistos.github.io/organic-nomenclature-3/mulermoc-nom-52.html
in isolated Firefox, selected propene/Expanded, captured public-svg.png.
7HTTP200 served HTML/viewer/teaching/data/CSS/JSME files hash-match upstream4e1190a.
MOL equals local source. Screenshot centerline pixels independently show contact
in this specific public/Firefox run as well as the local run (samples recorded).
This result does not refute the demonstrated gap or identify its cause.
Tested default views have different font scales (~18vs22CSSpx); the previous
47px SVG comparison controlled scale but not the professor's unknown runtime.
Native/full-edit ORGNL control was also displayed via its existing checkbox:
it hides carbon labels, so is not a valid C-label-gap comparison; no cause claim.
Live run logged6cookie/tracker errors, no null-viewer message. Browser is Developer
evidence. No application/core/MOL changes, commits, sync or publication.
A strict reproduction of the observed difference remains unresolved without
the demonstrated runtime; do not present a hypothesis as proven or propose a fix.
