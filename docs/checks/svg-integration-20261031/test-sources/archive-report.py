# coding: utf-8
from pathlib import Path
import json, gzip, hashlib, html

d = Path('docs/checks/svg-integration-20261031')
read = lambda p: json.load(gzip.open(p, 'rt', encoding='utf-8'))
old = read('docs/checks/svg-general-audit-20261031/catalog.json.gz')
replay = read('docs/checks/svg-general-audit-20261031/corrected-replay.json.gz')
new = read(d / 'final-acceptance.json.gz')
base = {(c['key'], c['mode']): c for c in old['cases'] if c['version'] == 'baseline'}
metrics = {(c['key'], c['mode']): c['raster'] for c in replay['datasets']['catalog'] if c['version'] == 'baseline' and c['width'] == 1500}
after = {(c['key'], c['mode']): c for c in new['cases'] if c['width'] == 1500}
examples = [
    ('butene_1', 'expanded', 'Καθαρό κενό ανάμεσα στους δεσμούς και τα γράμματα', 'Οι πραγματικές διαστάσεις των χαρακτήρων καθορίζουν την προστατευμένη περιοχή τους.'),
    ('ethyl_4_isopropyl_3_methyl_2_hexanal', 'condensed', 'Κάθε προστατευτική περιοχή ανήκει στο σωστό άτομο', 'Η σύμπτυξη του CHO διατηρεί πλέον την περιοχή του γειτονικού CH₃.'),
    ('pentanoic_acid', 'condensed', 'Προστασία γραμμάτων χωρίς εξαφάνιση δεσμού', 'Περιορίζεται η υπερβολική κάλυψη δίπλα στο COOH, ώστε να φαίνεται ο τελευταίος C–C.'),
]
sections, visual = [], []
for i, (key, mode, title, explanation) in enumerate(examples, 1):
    b, a, bm = base[key, mode], after[key, mode], metrics[key, mode]
    am = a['raster']
    entry = {'key': key, 'mode': mode, 'width': 1500}
    cards = []
    for suffix, label, c, m in [('before', 'Πριν', b, bm), ('after', 'Μετά', a, am)]:
        fn = 'example-%s-%s.svg' % (i, suffix)
        (d / fn).write_text(c['rawFinalSVG'], encoding='utf-8')
        entry[suffix + 'SVGsha256'] = hashlib.sha256(c['rawFinalSVG'].encode()).hexdigest()
        entry[suffix + 'Metrics'] = {k: m[k] for k in ['inkWithinHalfCssPixelOfBond', 'fullyHiddenLineCount']}
        cards.append('<figure><figcaption>%s</figcaption><img class="molecule" src="%s" alt="%s: %s"><p class="metric">Pixels επαφής ≤0,5 CSS px: %s · Πλήρως κρυμμένες γραμμές: %s</p></figure>' % (label, fn, label, html.escape(c['name']), m['inkWithinHalfCssPixelOfBond'], m['fullyHiddenLineCount']))
    visual.append(entry)
    sections.append('<section><h2>%s</h2><p>%s · %s</p><div class="pair">%s</div></section>' % (title, html.escape(b['name']), explanation, ''.join(cards)))
(d / 'visual-examples.json').write_text(json.dumps({'sourceBefore': '../svg-general-audit-20261031/catalog.json.gz baseline raw SVG', 'sourceBeforeMetrics': '../svg-general-audit-20261031/corrected-replay.json.gz catalog baseline (corrected oracle)', 'sourceAfter': 'final-acceptance.json.gz', 'examples': visual}, ensure_ascii=False, indent=2), encoding='utf-8')

summary = {
    'date': '2026-10-31', 'state': 'implemented locally; independent review pending',
    'baseHEAD': '168e3cec01f941a84d40bbe0dc07156e7baa35d0',
    'coreChangedToday': False, 'committed': False, 'published': False,
    'catalog': {'forms': 422, 'molecules': 141, 'widths': [1500, 390], 'cases': 844, 'failures': 0, 'javascriptErrors': 0, 'invariantDifferences': 0},
    'controls': {'states': 98, 'alkaneRatioCases': 48, 'native2DExports': 2},
    'nativeProducer': {'cases': 92, 'fonts': [9, 12, 14, 16], 'invariantsPreserved': True},
    'lessons': {'entries': 14, 'sampledStates': 70, 'terminalModels': 14, 'exits': 14, 'all337StepsTested': False},
    'future': {'cases': 18, 'accepted': 12, 'safelyRejectedCrowdedInputs': 6},
    'webkit': {'engine': 'native WKWebView, not Safari application', 'representativeCases': 28, 'javascriptErrors': 0},
    'loader': {'variants': 3, 'dpr2Cases': 6, 'javascriptErrors': 0},
    'metrics': ['Canvas raster fallback', 'Failure clears stale diagram and PNG', 'Real late FontFace cache invalidation', 'Progressive numbering retains timer/index', 'Font refresh after native 3D destruction emits no Jmol script', 'Pagehide/pageshow controller cancellation; not full BFCache certification'],
    'limitations': ['Finite catalog/browser/interaction sample; no guarantee for arbitrary future geometry/fonts/OS.', 'No Chrome/Windows/Safari application/full BFCache certification.', 'WebKit and normal controls preceded final pure-2D font callback correction; callback targeted-tested and full 844-case catalog rerun on final frozen runtime.', 'Extremely crowded inputs display controlled unavailable status; no silent geometry rewrite.', 'Original native quirks module unchanged; active standards module tested.', 'Offline package deferred; no publication/conference rehearsal claim.'],
    'developerCorrections': [
        {'id': 'D1', 'issue': 'Initial 1.2px mask floor hid pentanoic-acid bond at minimum zoom', 'resolution': 'Shared floor 0.6px; controls and complete catalog passed'},
        {'id': 'D2', 'issue': 'First font redraw called 3D numbering after applet teardown', 'resolution': 'Pure 2D redraw preserves progress and timer; owns/cancels RAF; lifecycle and loader passed'},
        {'id': 'D3', 'issue': 'Probe read live line geometry after await; detached SVG could yield invalid metrics', 'resolution': 'Freeze line visibility before await. Final acceptance uses corrected probe; debug counters are not final evidence.'},
    ],
}
(d / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
page = '''<!doctype html><html lang="el"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Namelecule · Διόρθωση γραμμάτων 2D</title>
<style>body{font:18px/1.55 system-ui,sans-serif;color:#254c50;background:#f8f7f2;margin:0}main{max-width:1160px;margin:auto;padding:28px}h1{font-size:2rem}h2{font-size:1.35rem}section{margin:28px 0;padding:22px;background:white;border:1px solid #cdded9;border-radius:16px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0;border:1px solid #cdded9;border-radius:12px;overflow:hidden;background:white}figcaption{padding:10px 16px;background:#e2f0eb;font-weight:700}.molecule{width:100%;height:auto;display:block}.metric{font-size:13px;padding:0 12px}a{color:#126e72}table{border-collapse:collapse;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid #d6e1dc}.shot{width:100%;height:auto}code{overflow-wrap:anywhere}li{margin:8px 0}@media(max-width:700px){main{padding:14px}section{padding:14px}.pair{grid-template-columns:1fr}table{font-size:15px}}</style>
<main><h1>Διόρθωση γραμμάτων 2D</h1><p>31 Οκτωβρίου 2026 · Κύρια έκδοση Namelecule · Τοπική ενσωμάτωση</p>
<p id="review-status">Η υλοποίηση και οι έλεγχοι Developer ολοκληρώθηκαν. Εκκρεμεί ο ανεξάρτητος τελικός έλεγχος.</p>
<p>Η σχεδίαση μετρά τα πραγματικά γράμματα και τους δείκτες τους. Κάθε λευκή περιοχή συνδέεται ρητά με το άτομό της. Έτσι διατηρείται καθαρό κενό από τους δεσμούς, χωρίς υπερβολικές περιοχές που κρύβουν συνδέσεις. Η ίδια διαδρομή χρησιμοποιείται στην ελεύθερη εξερεύνηση και στα μαθήματα.</p>
''' + ''.join(sections) + '''
<section><h2>Τι ελέγχθηκε</h2><table><tr><th>Πεδίο</th><th>Πραγματική κάλυψη</th></tr>
<tr><td>Βιβλιοθήκη</td><td>141 μόρια, 422 διαθέσιμες μορφές × 2 πλάτη = 844 περιπτώσεις. Καμία επαφή ≤0,5 CSS px, κρυμμένη γραμμή, περικοπή ή σφάλμα JavaScript.</td></tr>
<tr><td>Διατήρηση δεδομένων</td><td>Ίδια ονόματα, κείμενα ετικετών, σύμβολα και γράφοι. Core, MOL/SDF, σενάρια JSON, React και αρχικό JSME αμετάβλητα.</td></tr>
<tr><td>Χειριστήρια</td><td>98 καταστάσεις zoom/επισήμανσης/αρίθμησης/απόκρυψης. 48 έλεγχοι διατήρησης αναλογιών αλκανίων. Πραγματικές εξαγωγές PNG 2D και 3D.</td></tr>
<tr><td>Παραγωγός JSME</td><td>92 περιπτώσεις σε 4 μεγέθη γραμμάτων, με διατήρηση atom IDs, φορτίων, ισοτόπων, δεσμών, σχετικών συντεταγμένων και MOL body.</td></tr>
<tr><td>Μαθήματα</td><td>14 είσοδοι, 70 επιλεγμένες καταστάσεις, 14 τελικά μοντέλα 3D και 14 έξοδοι. Δεν εκτελέστηκαν και τα 337 βήματα.</td></tr>
<tr><td>Γραμματοσειρές και ανάκαμψη</td><td>Πραγματικό late FontFace, εναλλακτική μέτρηση, ασφαλής αποτυχία/ανάκτηση, διατήρηση προοδευτικής αρίθμησης και καμία κλήση 3D από την ανανέωση γραμμάτων.</td></tr>
<tr><td>Δεύτερη μηχανή browser</td><td>28 αντιπροσωπευτικές περιπτώσεις σε native WKWebView, χωρίς επαφές/κρυμμένες γραμμές/περικοπή/JS errors. Έλεγχος WebKit, όχι πιστοποίηση της εφαρμογής Safari.</td></tr>
<tr><td>Νέα δεδομένα</td><td>18 συνθετικές περιπτώσεις περιστροφής/απόστασης: 12 εμφανίστηκαν σωστά, 6 ακραία συνωστισμένες απορρίφθηκαν με ελεγχόμενο μήνυμα.</td></tr></table>
<p>Οι αρχικές δοκιμές εντόπισαν υπερβολική κάλυψη στο ελάχιστο zoom και κλήση αρίθμησης 3D μετά από έξοδο μαθήματος. Διορθώθηκαν πριν από τον τελικό έλεγχο. Διορθώθηκε επίσης ασύγχρονο σφάλμα του εργαλείου μέτρησης· τα αρχικά διαγνωστικά δεν χρησιμοποιούνται ως τελική απόδειξη.</p>
<img class="shot" src="actual-numbering-main.png" alt="Πραγματική κύρια εφαρμογή με αρίθμηση 2D και 3D"></section>
<section><h2>Όρια και επαναφορά</h2><p>Τα αποτελέσματα αφορούν την υπάρχουσα βιβλιοθήκη και τις καταγεγραμμένες δοκιμές. Δεν αποτελούν εγγύηση για κάθε μελλοντική γεωμετρία, γραμματοσειρά ή λειτουργικό σύστημα. Ο έλεγχος μελλοντικών προσθηκών είναι διαθέσιμος στο <code>tools/check-2d-labels.py</code>. Σε αποτυχία μέτρησης καθαρίζεται το παλιό διάγραμμα και εμφανίζεται μήνυμα, ώστε να μην εξάγεται παραπλανητικό PNG.</p>
<p>Ο WebKit και οι συνηθισμένοι έλεγχοι χειριστηρίων προηγήθηκαν της τελικής διόρθωσης του callback γραμματοσειρών. Το callback ελέγχθηκε στοχευμένα και όλος ο κατάλογος επανελέγχθηκε στον τελικό κώδικα. Δεν ελέγχθηκαν Chrome/Windows, πλήρες BFCache ή κάθε βήμα/μοντέλο 3D. Το offline πακέτο παραμένει για αργότερα.</p>
<p>Υπάρχει ελεγχόμενη επιλεκτική επαναφορά, με προστασία νεότερων αλλαγών. Δοκιμάστηκε σε απομονωμένο αντίγραφο· η εφαρμογή δεν επανήλθε στην προηγούμενη έκδοση. Καμία αλλαγή core σήμερα, κανένα commit ή δημοσίευση.</p>
<p><a href="summary.json">Σύνοψη ελέγχων</a> · <a href="final-invariant-comparison.json">Σύγκριση δεδομένων</a> · <a href="visual-examples.json">Προέλευση οπτικών παραδειγμάτων</a> · <a href="rollback-source.zip">Αρχεία επιλεκτικής επαναφοράς</a></p>
<p><a href="../../../mulermoc-nom-52.html">Άνοιγμα Namelecule</a> · <a href="../../../design/theory-library.html">Βιβλιοθήκη θεωρίας</a></p></section></main></html>
'''
(d / 'report.html').write_text(page, encoding='utf-8')
print('Report and exact stored-SVG examples created.')
