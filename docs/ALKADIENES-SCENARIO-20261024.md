# Θεωρία αλκαδιενίων — 24/10/2026

Εγκεκριμένο22βήματο μάθημα με βάση τα τρία υπάρχοντα σενάρια θεωρίας.
Νέο scenarios/alkadienes-nomenclature-branches.scenario.json και τέταρτη κάρτα
στη design/theory-library.html. Διατηρούνται τα προηγούμενα μαθήματα/κάρτες.
Αφετηρία1,3-βουταδιένιο, αναφορά απλούστερου προπαδιενίου, σύγκριση θέσεων,
μεθυλο-/διμεθυλο- και τελικό αιθυλο+διμεθυλο παράδειγμα, διερεύνηση8διενίων.
Ίδια προοδευτική αποκάλυψη/πίνακες2/3/4/9/18/ύψη420και840, χωρίς άνω κάτω
τελείες στα νέα κείμενα. Ρυθμίσεις με βάση πραγματικές αντιστοιχίσεις εφαρμογής.
Το6 χρησιμοποιεί compNumber1 για locantsστοcomp0 (compBondPos αφορά comp4).
Τα15–21 χρησιμοποιούν chainIdx1 για οριζόντια[1,2,3,4,5,6], όχι την ισοδύναμη
αλυσίδα με τελικόC10. Τα7–21 χρησιμοποιούν authoreddata mainChainMode.

LearningDesigner /root/diene_lesson_design και ChemistryValidator
/root/diene_lesson_chemistry έλεγξαν χωριστά σχέδιο και τελικά22κείμενα, μόνο
ανάγνωση, χωρίς ουσιώδη ευρήματα. Επιβεβαιώθηκε στην εφαρμογή το ορατό
βουτα-/πεντα-/εξα-. Αποφεύγονται ισχυρισμοί ειδικής στερεοχημείας απόconformer,
ισομέρειας βουταδιενίων με πενταδιένιο και καθολικής επιλογής αλυσίδας.
Τα highlights παρέχουν καθοδηγούμενο αυτοέλεγχο, όχι αυτόματη αξιολόγηση.
Η υπάρχουσα allene σκελετική απεικόνιση διατηρείται με οδηγία για άλλεςμορφές.

Developer πραγματικό Firefox/JSME/JSmol
- Και22βήματα ορθό μόριο/όνομα/ορατάκαικρυφάσυνθετικά/σημείωση/ρυθμίσεις.
- Σωστή οριζόντια αλυσίδα στα διακλαδισμένα, κανόνες2/3/4/9/18.
- Ακριβή σύνολα3DC για δύοC=C στα6/12/16 και 2D/3Dδιακλαδώσεις9/13/18/19/20.
- ΈξιH των δύομεθυλίων στον ανεπτυγμένο τύπο20.
- Πραγματικό exportBlob και validationεπανεισαγωγής χωρίς warnings/απώλειες.
- Μενού8μορίων, πραγματικό3Datomcount, τρεις2Dμορφές καθενός, library→μάθημα→Exit.
- Στενή προβολή700px με απόρριψη του προϋπάρχοντος μηνύματος περιστροφής.
- Καμία JavaScripterror. Οπτική επιθεώρηση screenshots1/20/στενής20.
Τεκμήριο checks/alkadienes-lesson-20261024.json, script test-alkadienes-lesson-browser-20261024.py.
Read-only hashέλεγχος17προστατευμένων αρχείων, παλιά3librarycardsαμετάβλητα.
Δεν έγιναν αλλαγές ή επανεπικύρωση μοριακώνγράφων/3Dγεωμετρίας, αφού διατηρήθηκαν.
Independent final Reviewer /root/review_alkadiene_lesson completed fresh-context
review without actionable findings. Independently checked four hashes,17protected
files/threeoldcards,22texts/settings, C/C=C counts and allC-C connectivity2Dto3D
for sixnewexamples; Python AST for browser script. Browser/export/highlight and
visual results are Developer evidence, not independent browser execution.
Final four-file frozen target:
checks/alkadienes-lesson-freeze-20261024.json. Δεν άλλαξε core/viewer/data.
Τοπική υλοποίηση χωρίς stage/commit/push/δημοσίευση.

Final narrow-only check used actual rotatePromptDismiss id after the initial
text selector missed internal newlines. Overlay gone and Exit/library pass.
No application change was needed for the existing rotation prompt.
