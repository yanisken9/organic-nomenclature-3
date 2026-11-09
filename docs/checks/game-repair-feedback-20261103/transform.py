"""Rebuild this bounded revision from the recorded before-state, for review."""
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent


def build():
    originals = json.loads((HERE / 'baseline.json').read_text())['baselineCopies']
    js = originals['js/namelecule-game-repair.js']
    js = js.replace('fetch("./data/name-repair-alkanes.json")', 'fetch("./data/name-repair-alkanes.json", { cache: "no-cache" })')
    js = js.replace('      hintsUsed: previous ? previous.hintsUsed : 0,\n', '')
    js = re.sub(r'      independent:.*?\n      assisted:.*?\n', '', js)
    js = js.replace(' }, 0),\n      hints: challenges.reduce(function (sum, entry) { return sum + (entry.state ? entry.state.hintsUsed : 0); }, 0)', ' }, 0)')
    start = js.index('      assert(Array.isArray(round.hints)')
    end = js.index('      assert(round.feedback', start)
    js = js[:start] + js[end:]
    js = js.replace('  let hintImageStatuses = [];\n', '').replace('    hintImageStatuses = [];\n', '')
    js = js.replace('mainImageStatus === "ready" && hintImageStatuses.every(function (status) { return status === "ready"; })', 'mainImageStatus === "ready"')
    start = js.index('    refs.hintButton =')
    end = js.index('    const broken =', start)
    js = js[:start] + js[end:]
    js = js.replace('[diagram, hints]', '[diagram]').replace('    renderHints(currentRender);\n', '')
    start = js.index('    refs.hintButton.disabled =')
    end = js.index('    refs.checkHelper.textContent =', start)
    js = js[:start] + js[end:]
    js = js.replace(' + current.attempts + " · Υποδείξεις " + current.hintsUsed', ' + current.attempts')
    js = js.replace('Οι επιλογές επανήλθαν. Οι προσπάθειες και οι υποδείξεις σου παραμένουν.', 'Οι επιλογές επανήλθαν. Οι προσπάθειές σου παραμένουν.')
    start = js.index('  function showHint()')
    end = js.index('  function requestRestart()', start)
    js = js[:start] + js[end:]
    js = js.replace(' || entry.hintsUsed > 0', '')
    js = js.replace('Οι επισκευές, οι προσπάθειες και οι υποδείξεις αυτού του παιχνιδιού θα μηδενιστούν.', 'Οι επισκευές και οι προσπάθειες αυτού του παιχνιδιού θα μηδενιστούν.')
    js = js.replace('Βοήθεια όποτε θέλεις', 'Εξηγήσεις μετά την επισκευή')
    js = js.replace('Η εξήγηση και οι υποδείξεις είναι δίπλα σου.', 'Μετά τη σωστή επισκευή, δες γιατί το όνομα ταιριάζει στη δομή.')
    js = js.replace('[summary.independent, "Ολοκληρώθηκαν χωρίς πρόσθετη υπόδειξη"],\n      [summary.assisted, "Ολοκληρώθηκαν με πρόσθετη υπόδειξη"],', '[summary.completed, "Αποστολές που ολοκληρώθηκαν"],')
    js = re.sub(r'\),\n            node\("span", \{ class: "result-assistance"[^\n]+', ')', js)
    js = re.sub(r'node\("p", \{ class: "results-note", text: "[^"]*«Χωρίς πρόσθετη υπόδειξη»[^\n]+', 'node("p", { class: "results-note", text: "Το καθοδηγούμενο παράδειγμα δεν προσμετράται. Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε αποστολής." }),', js)
    assert not re.search(r'hint|υπόδειξ|υποδείξ|Υποδείξ', js, re.I), 'Hint feature still referenced'

    css = originals['css/namelecule-games.css']
    css = '\n'.join(line for line in css.splitlines() if not re.search(r'\.hint-|\.result-assistance', line)) + '\n'
    css = css.replace('grid-template-columns: 1fr 1fr 1fr; gap: 13px;', 'grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 13px;')
    css = css.replace('grid-template-columns: 28px 1fr auto;', 'grid-template-columns: 28px 1fr;')

    raw = originals['games/data/name-repair-alkanes.json']
    explanations = [
        'Η κύρια αλυσίδα έχει τέσσερις άνθρακες, επομένως το πρώτο συνθετικό είναι «βουτ». Το «άν» δηλώνει απλούς δεσμούς μεταξύ των ανθράκων και το «ιο» την κατάληξη του υδρογονάνθρακα.',
        'Η μεγαλύτερη συνεχής ανθρακική αλυσίδα έχει πέντε άνθρακες και δίνει το «πεντ». Ο έκτος άνθρακας ανήκει στη μεθυλομάδα, που αναφέρεται χωριστά στη θέση 2.',
        'Οι δύο φορές αρίθμησης δίνουν στη μεθυλομάδα τις θέσεις 2 και 4. Επιλέγουμε τη θέση 2, επειδή σε αυτό το αλκάνιο η μοναδική διακλάδωση πρέπει να πάρει τον μικρότερο αριθμό.',
        'Στις θέσεις 2 και 3 υπάρχει από μία μεθυλομάδα. Επειδή οι διακλαδώσεις είναι δύο και ίδιες, χρησιμοποιούμε το «διμεθυλο». Η κύρια αλυσίδα έχει τέσσερις άνθρακες και δίνει το «βουτ».',
        'Συγκρίνουμε αλφαβητικά τα «αιθυλο» και «μεθυλο», επομένως προηγείται το «αιθυλο». Το «δι-» και οι αριθμοί θέσης δεν καθορίζουν αυτή τη σειρά. Κάθε ομάδα κρατά τις δικές της θέσεις όταν μετακινείται.'
    ]
    raw, removed = re.subn(r'      "hints": \[.*?\n      \],\n', '', raw, flags=re.S)
    assert removed == 5
    index = iter(explanations)
    raw = re.sub(r'"successText": "[^"\n]*"', lambda m: '"successText": ' + json.dumps(next(index), ensure_ascii=False), raw)
    raw = re.sub(r'"wrongPart": "[^"\n]*"', '"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή."', raw)
    raw = raw.replace('Μπορείς να δοκιμάσεις ξανά ή να ζητήσεις υπόδειξη.', 'Δοκίμασε ξανά.')
    json.loads(raw)
    html = originals['games/name-repair.html'].replace('../css/namelecule-games.css"', '../css/namelecule-games.css?v=feedback-20261103-r2"').replace('../js/namelecule-game-repair.js"', '../js/namelecule-game-repair.js?v=feedback-20261103-r2"')
    return {'js/namelecule-game-repair.js': js, 'css/namelecule-games.css': css,
            'games/data/name-repair-alkanes.json': raw, 'games/name-repair.html': html}


if __name__ == '__main__':
    for path, text in build().items():
        Path(path).write_text(text)
