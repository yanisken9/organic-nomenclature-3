# 3-αιθυλο-2,5-διμεθυλο-2-εξένιο — προσθήκη υπό δοκιμή, 2026-10-20

## Update 2026-10-20: approved viewer fix implemented locally

User approved group-specific highlights/explanations. New helpers in molview
mirror core alphabetical grouping (first group / remaining groups) and map
live parent locants plus branch sizes to carbon subtrees in 2D and 3D.
No molecule-specific atom IDs. No-slot callers retain all-branch behavior.
Hydrocarbon component explanations now identify branch type, position, count.

Actual Firefox tests with real component clicks passed:
- Four forms: disjoint ethyl/dimethyl carbon sets, 2 carbons each, in 2D/3D.
- Expanded: ethyl H5 (7 atoms total), dimethyl H6 (8 atoms total).
- Exact IDs delivered to JSME setAtomBackgroundColors match expected atoms;
  JmolSelection includes exactly the corresponding branch carbons.
- Components comp0/1/2/3 have correct explanations, positions 3 vs 2,5,
  and the molecule name remains correct.
- All four stepper candidates and stored mode remap the groups correctly.
- Existing methylpropene/methylbutene/dimethylbutane retain names and branch
  counts. Chlorobutane bypasses the new hydrocarbon path and highlights Cl.
- Viewer syntax/data/scenario roundtrip/diff checks passed. Expanded screenshot
  visually inspected; evidence in design/assets/*-groups.png.

Still local: no commit or publication. User visual acceptance pending.
The original issue/approval notes below are superseded by this update.

Εγκρίθηκε το σχέδιο δημιουργίας 3 MOL/αναζήτησης 3D/τοπικής ενσωμάτωσης
και ελέγχου διαφορετικών κλάδων. Δεν δημοσιεύτηκε και δεν έγινε commit.

## Πηγές και δομή

Key: ethyl_3_dimethyl_2_5_hexene_2. Δεδομένα στο data_48.js (72 entries).
MOL πηγές στο mols/new_molecules/ με suffix _2D_Condensed/Expanded/Skeletal.
C1..C6 = βασική αλυσίδα από δεξιά προς αριστερά, double 2–3.
Μethyl C7 στο C2, ethyl C8–C9 στο C3, methyl C10 στο C5.
Stored 2D chain [1,2,3,4,5,6]. Η automatic ισοδύναμη chain είναι
[1,2,3,4,5,10]. Στον ανεπτυγμένο προστίθενται H11..H30.

Condensed/Expanded: C–C1.17/C–H.78, οριζόντια βασική αλυσίδα και
ορθογώνια H. Ethyl πάνω και δύο methyl κάτω για αποφυγή επικαλύψεων.
Skeletal: ομοιόμορφο zigzag C–C≈.78, διακλαδώσεις στην εξωτερική
κατεύθυνση της αντίστοιχης κορυφής για γωνίες≈120°.

PubChem CID56988951, ίδιος χημικός γράφος C10H20:
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/3-ethyl-2,5-dimethylhex-2-ene/SDF?record_type=3d
Αυτούσιο SDF στο mols/nomeclature-moc2/ethyl_3_dimethyl_2_5_hexene_2_3D.sdf.
Stored 3D [9,5,3,2,1,6]. Μethyl C10/C7, ethyl C4–C8.
Ελέγχθηκε ρητή αμφιμονοσήμαντη αντιστοιχία όλων των δεσμών C–C μεταξύ
MOL και SDF, πλήρη σθένη, 10C/20H και ένας διπλός δεσμός.

## Πραγματικοί έλεγχοι

Firefox πλήρης τοπική v48: σωστό 3-αιθυλο-2,5-διμεθυλο-2-εξένιο σε
4 μορφές, κύρια αλυσίδα μήκους6, έξι αριθμοί ανά μορφή, 3D φόρτωση.
Επιθεωρήθηκε screenshot ανεπτυγμένου, αποθηκεύτηκαν draft εικόνες.
Ονομασία components: 3-/αιθυλο/-2,5-/διμεθυλο/-2-/εξ/έν/ιο.

## Ανοιχτό πρόβλημα και συγκεκριμένο σχέδιο επέκτασης

Τα κλικ comp1 (αιθυλο) και comp3 (διμεθυλο) αναδεικνύουν ΟΛΟΥΣ τους
κλάδους και σε 2D και σε 3D. Το fGetHydrocarbonBranchHighlight[/3D] μαζεύει
κάθε C εκτός κύριας αλυσίδας, ενώ τα fHighlightFG[/3D] αγνοούν FGno στο
hydrocarbon fallback. Τα κείμενα επίσης λένε Χαρακτηριστική Ομάδα.
Αναμενόμενο: αιθυλο μόνο C8–C9, διμεθυλο μόνο τις δύο methyl έξω από
την επιλεγμένη αλυσίδα. Το ποια ισοδύναμη methyl ανήκει στην κύρια αλυσίδα
εξαρτάται από stepper/stored mode· δεν επιτρέπεται hardcoded atom list.

Προτεινόμενη αλλαγή μόνο js/mulermoc-nom-molview-48.js: ταξινόμηση ομάδων
κλάδων όπως το core, επιλογή πρώτης/δεύτερης ομάδας με βάση το πατημένο
component, φίλτρο carbon subtrees σε 2D/3D, με τα προσδεδεμένα expanded H
και εσωτερικούς δεσμούς. Διόρθωση των σχετικών επεξηγήσεων για αριθμό,
τύπο και πλήθος αλκυλοκλάδων. Διατήρηση υφιστάμενων functional-group paths.

Έλεγχοι μετά έγκριση: δύο διακριτά σύνολα carbon/H σε τέσσερις μορφές,
2D/3D parent locants, stepper και stored mode, methyl-only προηγούμενα
μόρια και ένα μόριο με πραγματικές χαρακτηριστικές ομάδες.
Αναμονή έγκρισης για επέκταση του viewer· δεν θεωρείται ολοκληρωμένη
προσθήκη πριν διορθωθεί το διδακτικά εσφαλμένο highlight.
