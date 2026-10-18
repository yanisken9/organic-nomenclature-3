# Μετάβαση Namelecule στη v48 — 2026-10-18

## Πηγή και αποτέλεσμα

Εγκεκριμένη από τον Γιάννη μετάβαση από την τοπική v45 (`d45c7a1`) στην
upstream v48, commit `aeb6bf0` του `nick-charistos/organic-nomenclature-3`.
Η πηγή εξετάστηκε σε ξεχωριστό clone `/tmp/namelecule-v48-review-20261018`.
Η υποδοχή και οι σύνδεσμοι της μακέτας οδηγούν πλέον στη v48. Η v45 παραμένει
διαθέσιμη. Δεν έγινε commit, push ή δημοσίευση σε αυτή τη συνεδρία.

## Μεταφορά

- Προστέθηκαν HTML, πέντε JS και δύο CSS της v48 και ξεχωριστό θέμα
  `css/namelecule-48.css`. Τα core/data/teaching είναι byte-identical upstream.
- Διατηρήθηκαν λογότυπο, αναφορά MuLERMoCs, επιστροφή στην υποδοχή, mint
  highlights, μικρότεροι teal αριθμοί. Η νέα δομή `mainAppContainer` και η
  διάταξη pinned authoring λαμβάνονται υπόψη στο θέμα.
- Το scenario module συνδυάστηκε με κοινό πρόγονο την upstream v45.
  Διατηρούνται showStepNumbers/reserveTitleSpace σε new/validate/import,
  preload, URL import και export. Η εξαγωγή αναφέρει mulermoc-nom-48.
- Διατηρήθηκε η κοινή fFit2DSVG με μετατροπή του περιθωρίου αρίθμησης από
  κλιμακωμένες συντεταγμένες JSME. Εκτελείται μετά το SVG post-processing,
  που καλείται και από το νέο resize pipeline. Δεν μεταφέρθηκε ο παλιός
  fScheduleViewer3DResize: ο νέος upstream μηχανισμός ορίζει τα μεγέθη.
- Διατηρήθηκαν η νεότερη upstream ονοματολογία/δεδομένα/γεωμετρία, οι
  ανεξάρτητοι διακόπτες highlight και οι νέες ρυθμίσεις viewerMaxHeight.
  Το 2,3-διμεθυλοβουτάνιο υπάρχει ήδη στη νέα βάση· δεν αντικαταστάθηκε με
  τις παλιότερες τοπικές συντεταγμένες ή τον παλιότερο naming κώδικα.
- Ενημερώθηκε το κοινό ui-icons.js με τα νέα εικονίδια upstream. Προστέθηκαν
  τα τέσσερα νέα 3D αρχεία και ο upstream φάκελος πηγών mols/new_molecules.

## Πραγματικοί έλεγχοι

- JavaScriptCore checkSyntax: πέντε αρχεία v48 και ui-icons.js.
- Εκτέλεση data/scenario με ελάχιστα DOM stubs: 69 κλειδιά μορίων, τα δύο
  αποθηκευμένα σενάρια επικυρώνονται χωρίς απώλεια βημάτων (5 και 7).
- Export/validate roundtrip: showStepNumbers=false, reserveTitleSpace=true,
  viewerMaxHeight=360, numberingBonds=false, legacy diagramatic→skeletal.
- Προσομοιώσεις fFit2DSVG: scaled .01 μικρό μόριο χωρίς σμίκρυνση, κέντρο,
  σταθερή επανάληψη, expanded bounds και aspect ratio. Δεν είναι JSME rendering.
- Έλεγχος τοπικών HTML asset paths, ύπαρξη και των 69 αρχείων 3D, CSS braces,
  ταύτιση upstream core/data/teaching και git diff --check.
- Η τοπική v48 στη θύρα 8001 επέστρεψε HTTP 200 (έλεγχος διαθεσιμότητας).

## Εκκρεμής αποδοχή σε browser

Δεν υπήρχε διαθέσιμο browser automation. Χρειάζεται οπτικός/λειτουργικός
έλεγχος: αιθάνιο και 2,3-διμεθυλοβουτάνιο σε όλες τις 2D μορφές, ένα μόριο
με ετεροάτομο, zoom/resize/PNG, highlights και αρίθμηση 2D/3D. Έπειτα άνοιγμα
σεναρίων, pin/unpin σε στενή και μεγάλη οθόνη, παρουσίαση/Exit, εισαγωγή και
εξαγωγή. Οι αυτοματοποιημένοι έλεγχοι δεν αποδεικνύουν οπτική αποδοχή.

Pre-commit staged review: upstream imports contain trailing whitespace and
blank EOF lines (including fixed-format MOL bond records). Preserved source
formatting; the earlier unstaged diff check did not cover untracked imports.
