from pathlib import Path
import json
p=Path('games/data/name-repair-alkanes.json');before=p.read_text();a=before.index('    {\n      "id": "guided-parent",');b=before.index('    {\n      "id": "parent-not-total",',a);after=before[:a]+before[b:];assert json.loads(after)['rounds']==json.loads(before)['rounds'][1:];p.write_text(after)
p=Path('js/namelecule-game-repair.js');s=p.read_text();s=s.replace('assert(Array.isArray(data.rounds) && data.rounds.length === 5, "Expected one example and four challenges");','assert(Array.isArray(data.rounds) && data.rounds.length === 4, "Expected four challenges");',1).replace('data.rounds.forEach(function (round, index) {\n      validateRoundData(round);','data.rounds.forEach(function (round) {\n      validateRoundData(round);',1).replace('assert(round.guided === (index === 0), "The first round must be the only guided example");','assert(round.guided === false, "Standalone rounds must be challenges");',1)
a=s.index('  function renderWelcome() {');b=s.index('    const steps = [',a)
s=s[:a]+'''  function renderWelcome() {
    renderId += 1;
    const hero = node("section", { class: "workshop-hero", "aria-label": "Καλώς ήρθες στο Συνεργείο ονομάτων" }, [
      node("p", { class: "eyebrow", text: "ΠΑΙΧΝΙΔΙΑ ΟΝΟΜΑΤΟΛΟΓΙΑΣ" }),
      node("div", { class: "workshop-title" }, [workshopLogo("workshop-logo"), node("h1", {}, ["Συνεργείο", node("span", { text: "ονομάτων" })])]),
      node("p", { class: "workshop-description", text: "Διάλεξε ένα σετ αποστολών. Παρατήρησε κάθε δομή, επισκεύασε το όνομα και δες την εξήγηση μετά από κάθε σωστή απάντηση." })
    ]);
    const start = button("Ξεκίνα το σετ →", "primary workshop-set-start intro-start", function () {
      roundIndex = 0;
      states = game.rounds.map(function (data) { return createRoundState(data); });
      renderRound();
    }, { id: "set-alkanes-start" });
    const card = node("article", { class: "workshop-set-card", "aria-labelledby": "set-alkanes-title" }, [
      node("span", { class: "workshop-set-kind", text: "ΣΕΤ ΑΠΟΣΤΟΛΩΝ" }),
      node("h3", { id: "set-alkanes-title", text: "Αλκάνια" }),
      node("p", { text: "Τέσσερις μικρές επισκευές για να συνδέσεις τη δομή των αλκανίων με τα κομμάτια του ονόματος." }),
      node("div", { class: "workshop-set-meta" }, [node("span", { text: "4 αποστολές" }), node("span", { text: "Χωρίς χρονόμετρο" })]),
      node("ul", { class: "workshop-set-topics" }, ["Κύρια αλυσίδα", "Αρίθμηση", "Ίδιες διακλαδώσεις", "Αλφαβητική σειρά"].map(function (text) { return node("li", { text: text }); })),
      start
    ]);
    const sets = node("section", { class: "workshop-sets", "aria-labelledby": "workshop-sets-title" }, [
      node("h2", { id: "workshop-sets-title", text: "Διάλεξε σετ αποστολών" }),
      node("div", { class: "workshop-set-grid" }, [card])
    ]);
'''+s[b:]
s=s.replace('''    const welcome = node("div", {}, [
      node("section", { class: "intro", "aria-label": "Καλώς ήρθες στο Συνεργείο ονομάτων" }, [copy, art]),''','''    const welcome = node("div", { class: "workshop-hub" }, [
      hero, sets,''',1)
s=s.replace('const label = round.guided ? "Καθοδηγούμενο παράδειγμα" : "Αποστολή " + index;','const label = "Αποστολή " + (index + 1);',1).replace('text: complete ? "✓" : round.guided ? "Π" : String(index)','text: complete ? "✓" : String(index + 1)',1)
s=s.replace('[button("Νέο παιχνίδι", "quiet", options.requestRestart)]','[button("Επιστροφή στα σετ", "quiet", options.requestRestart)]',1)
s=s.replace('text: "Να ανοίξουμε νέο παιχνίδι;"','text: "Επιστροφή στα σετ;"',1).replace('text: "Οι επισκευές και οι προσπάθειες αυτού του παιχνιδιού θα μηδενιστούν."','text: "Οι επισκευές και οι προσπάθειες αυτού του σετ θα μηδενιστούν."',1).replace('const restart = button("Νέο παιχνίδι", "primary", function ()','const restart = button("Επιστροφή στα σετ", "primary", function ()',1)
s=s.replace('text: "Το καθοδηγούμενο παράδειγμα δεν προσμετράται. Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε αποστολής."','text: "Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε αποστολής."',1).replace('button("Νέο παιχνίδι  ↻", "primary", restartGame)','button("Επιστροφή στα σετ", "primary", restartGame)',1)
p.write_text(s)
