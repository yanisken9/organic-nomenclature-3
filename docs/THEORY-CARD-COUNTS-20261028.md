# Πλήθος μορίων στις καρτέλες θεωρίας — 28/10/2026

Ο χρήστης ενέκρινε να εμφανίζεται «Χ βήματα · Υ μόρια» σε κάθε μάθημα,
όπως στο μάθημα άλλων καρβοξυλικών οξέων. Άλλαξαν μόνο 13 κείμενα badge στο
`design/theory-library.html`. Το ήδη σωστό 14ο badge διατηρήθηκε. Μετρήθηκαν
τα διαφορετικά selectedMol των βημάτων κάθε συνδεδεμένου JSON, μία φορά το
καθένα. Πλήθη κατά σειρά καρτελών 5/5/5/6/6/7/10/11/9/8/7/7/8/7.
Παραμένουν 14 ενεργά μαθήματα και 337 βήματα. Δεν άλλαξαν μαθήματα ή μόρια.

Developer επαλήθευση: όλες οι 14 ενδείξεις αντιστοιχούν στα JSON. Πραγματικός
Firefox σε 1500/900/390/320 px, όλα τα badges εντός κάρτας και οθόνης,
χωρίς οριζόντια υπερχείλιση σελίδας ή JS errors. git diff --check PASS.
Screenshots μόνο /tmp/namelecule-theory-card-counts-20261028. Δεν προστέθηκαν
runtime tests ή ευρύτερες επανεκτελέσεις για αυτή την αλλαγή κειμένων.

Ανεξάρτητος Reviewer /root/theory_card_counts_review,
ROLE_ID=NAMELECULE_REVIEWER_V1_20261023, fork_turns none, χωρίς ιστορικό Developer.
Έλεγξε task-specific diff και frozen HTML, ανακατασκεύασε το πριν με ίδιο
καταγεγραμμένο hash, επιβεβαίωσε ακριβώς 13 αντικαταστάσεις και όλα τα υπόλοιπα
HTML bytes ίδια. Ανεξάρτητη μέτρηση των 14 JSON και 18 protected hashes PASS.
Κανένα actionable P0/P1/P2/P3. Δεν απαιτήθηκε διόρθωση ή δεύτερος έλεγχος.
Browser αποτελέσματα είναι Developer evidence, όχι εκτέλεση Reviewer.
Δεν απαιτούνται νέοι χημικοί/μαθησιακοί ή lesson-runtime έλεγχοι για labels.
Η απαγόρευση εγγραφών Reviewer ήταν συμπεριφορική, όχι enforced απομόνωση.

Frozen HTML SHA256
`c5cf051a2bb8479b282ed6694c700a83c2fe2b0e8c851edfecce682310a2b5f6`.
Manifest, source diff και browser evidence στο docs/checks/theory-card-counts-*.
Μετά το review επιβεβαιώθηκαν ξανά το target και τα 18 protected hashes.
Κανένα core δεν άλλαξε έναντι έναρξης αυτής της εργασίας. Core52 SHA256
`7e944c6f30abd4cae66a4c1ee0f413f21582b2058b7d3c7679a7a1a463d8a998`.
Η αναφορά και τα journals καταγράφουν το αποτέλεσμα μετά το review.
Τοπικά μόνο, χωρίς commit/push/δημοσίευση.
