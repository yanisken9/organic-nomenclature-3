from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();here=root/'docs/checks/alkane-two-sets-20261104/engine';here.mkdir(parents=True,exist_ok=True);before=here.parent/'before'
paths=['js/namelecule-game-repair.js','games/data/name-repair-alkanes.json']
for n in paths:assert (root/n).read_bytes()==(before/Path(n).name).read_bytes(),n
pilot=root/'scenarios/alkanes-name-repair-pilot.scenario.json'
(here/'baseline.json').write_text(json.dumps({'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'beforeCopies':'../before/','sourceSHA256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in paths},'embeddedPilotSHA256':hashlib.sha256(pilot.read_bytes()).hexdigest()},indent=2)+'\n')
old=json.loads((root/paths[1]).read_text());neutral='Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.'
commonfeedback={'wrongPart':'Αυτό το συνθετικό συμφωνεί με τη δομή.','unchanged':'Διάλεξε αντικατάσταση για το λανθασμένο συνθετικό.','incorrect':'Το συνθετικό δεν συμφωνεί με τη δομή. Παρατήρησε το μόριο και δοκίμασε ξανά.'}
def linear(id,title,molecule,alt,parts,target,correct,name,choices,success):
 return {'id':id,'guided':False,'title':title,'objective':neutral,'moleculeId':molecule,'asset':'assets/name-repair/'+molecule+'.svg','diagramAlt':alt,'kind':'replace','parts':[{'id':i,'text':t,'label':l} for i,t,l in parts],'targetPartId':target,'correctValue':correct,'correctName':name,'choices':choices,'successText':success,'feedback':commonfeedback.copy()}
def choice(value,feedback=None):
 d={'value':value,'label':value}
 if feedback:d['feedback']=feedback
 return d
labels=['Μήκος κύριας αλυσίδας','Είδος δεσμών','Χημική τάξη']
def parts(root,saturation):return list(zip(['root','saturation','ending'],[root,saturation,'ιο'],labels))
unbranched=[
 linear('unbranched-parent-four','Πόσο μήκος δείχνει η αλυσίδα;','butane','Ανεπτυγμένος τύπος ευθείας αλυσίδας τεσσάρων ανθράκων με απλούς δεσμούς και χωρίς διακλαδώσεις.',parts('προπ','άν'),'root','βουτ','βουτάνιο',[choice('αιθ','Το «αιθ» δηλώνει δύο άνθρακες. Ακολούθησε όλη τη συνεχή αλυσίδα του σχεδίου.'),choice('βουτ'),choice('πεντ','Το «πεντ» δηλώνει πέντε άνθρακες. Μέτρησε τους άνθρακες της αλυσίδας στο σχέδιο.')],'Η συνεχής ανθρακική αλυσίδα έχει τέσσερις άνθρακες, άρα το συνθετικό του μήκους της είναι «βουτ». Έτσι το σωστό όνομα είναι βουτάνιο.'),
 linear('unbranched-single-bond','Τι δείχνει ο δεσμός;','ethane','Ανεπτυγμένος τύπος δύο ανθράκων που ενώνονται με έναν απλό δεσμό. Κάθε άνθρακας συνδέεται με τρία υδρογόνα.',parts('αιθ','έν'),'saturation','άν','αιθάνιο',[choice('άν'),choice('έν','Το «έν» δηλώνει διπλό δεσμό μεταξύ ανθράκων. Στο σχέδιο ο δεσμός μεταξύ των δύο ανθράκων είναι απλός.'),choice('ίν','Το «ίν» δηλώνει τριπλό δεσμό μεταξύ ανθράκων. Στο σχέδιο ο δεσμός μεταξύ των δύο ανθράκων είναι απλός.')],'Ο δεσμός ανάμεσα στους δύο άνθρακες είναι απλός, επομένως χρησιμοποιούμε το «άν». Με το «αιθ» για τους δύο άνθρακες, το όνομα είναι αιθάνιο.'),
 linear('unbranched-parent-five','Μέτρησε τη συνεχή αλυσίδα','pentane','Ανεπτυγμένος τύπος ευθείας αλυσίδας πέντε ανθράκων με απλούς δεσμούς και χωρίς διακλαδώσεις.',parts('εξ','άν'),'root','πεντ','πεντάνιο',[choice('προπ','Το «προπ» δηλώνει τρεις άνθρακες. Ακολούθησε όλη τη συνεχή αλυσίδα του σχεδίου.'),choice('βουτ','Το «βουτ» δηλώνει τέσσερις άνθρακες. Μέτρησε και τους δύο ακραίους άνθρακες της αλυσίδας.'),choice('πεντ')],'Η συνεχής ανθρακική αλυσίδα έχει πέντε άνθρακες, άρα το συνθετικό του μήκους της είναι «πεντ». Έτσι το σωστό όνομα είναι πεντάνιο.')]
branched=old['rounds'][1:]
for i,r in enumerate(branched):r['objective']=neutral if i<2 else 'Οι ομάδες του ονόματος μπήκαν σε λάθος σειρά. Επίλεξε μια ομάδα και μετακίνησέ τη.'
new={'schemaVersion':2,'title':old['title'],'description':old['description'],'sets':[{'id':'alkanes-unbranched','title':'Χωρίς διακλαδώσεις','description':'Σύνδεσε το μήκος της συνεχούς αλυσίδας και το είδος των δεσμών με τα συνθετικά του ονόματος.','topics':['Μήκος αλυσίδας','Είδος δεσμών','Σύνθεση ονόματος'],'rounds':unbranched},{'id':'alkanes-branched','title':'Με διακλαδώσεις','description':'Σύνδεσε τις θέσεις, το πλήθος και τη σειρά των διακλαδώσεων με τα κομμάτια του ονόματος.','topics':['Αρίθμηση','Ίδιες διακλαδώσεις','Αλφαβητική σειρά'],'rounds':branched}]}
(root/paths[1]).write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
p=root/paths[0];s=p.read_text();a=s.index('  function validateGameData(data) {');b=s.index('\n  // Persist only legal answer data.',a)
s=s[:a]+'''  function validateGameData(data) {
    assert(data && data.schemaVersion === 2 && text(data.title) && text(data.description), "Invalid game metadata");
    assert(!Object.prototype.hasOwnProperty.call(data, "rounds") && Array.isArray(data.sets) && data.sets.length === 2, "Expected two quiz sets");
    const setIds = new Set();
    const roundIds = new Set();
    data.sets.forEach(function (set) {
      assert(set && ["alkanes-unbranched", "alkanes-branched"].includes(set.id) && !setIds.has(set.id), "Invalid set id");
      setIds.add(set.id);
      assert(text(set.title) && text(set.description) && Array.isArray(set.topics) && set.topics.length > 0 && set.topics.every(text), "Invalid set metadata");
      assert(Array.isArray(set.rounds) && set.rounds.length === 3, "Expected three quizzes per set");
      set.rounds.forEach(function (round) {
        validateRoundData(round);
        assert(!roundIds.has(round.id), "Invalid round id");
        roundIds.add(round.id);
        assert(round.guided === false, "Standalone rounds must be challenges");
      });
    });
    return data;
  }
'''+s[b:]
# This optional identity belongs exclusively to standalone chrome.
s=s.replace('''      if (data.guided) heading.append(node("span", { class: "guided-pill", text: "Πρώτα δοκιμάζουμε μαζί" }));''','''      if (data.guided) heading.append(node("span", { class: "guided-pill", text: "Πρώτα δοκιμάζουμε μαζί" }));
      if (standalone && options.setTitle) heading.append(node("p", { class: "round-set-name", text: "Αλκάνια · " + options.setTitle }));''',1)
s=s.replace('  let game = null;\n  let roundIndex', '  let game = null;\n  let activeSet = null;\n  let roundIndex',1)
s=s.replace('      states = game.rounds.map(function (round) { return createRoundState(round); });','      states = [];\n      activeSet = null;',1)
s=s.replace('text: "Διάλεξε ένα σετ αποστολών. Παρατήρησε κάθε δομή, επισκεύασε το όνομα και δες την εξήγηση μετά από κάθε σωστή απάντηση."','text: "Διάλεξε μια κατηγορία και έπειτα ένα σύντομο σετ. Παρατήρησε κάθε δομή, επισκεύασε το όνομα και δες την εξήγηση μετά από κάθε σωστή απάντηση."',1)
a=s.index('    const start = button(',s.index('  function renderWelcome()'));b=s.index('    const card =',a)
s=s[:a]+'''    const start = button("Δες τα σετ →", "primary workshop-set-start intro-start", function () {
      renderSetPicker();
      focusHeading();
    }, { id: "set-alkanes-start" });
'''+s[b:]
s=s.replace('text: "Τέσσερις μικρές επισκευές για να συνδέσεις τη δομή των αλκανίων με τα κομμάτια του ονόματος."','text: "Δύο σύντομα σετ για να συνδέσεις τη δομή των αλκανίων με τα κομμάτια του ονόματος."',1)
s=s.replace('[node("span", { text: "4 αποστολές" }), node("span", { text: "Χωρίς χρονόμετρο" })]','[node("span", { text: "2 σετ" }), node("span", { text: "3 κουίζ ανά σετ" })]',1)
s=s.replace('["Κύρια αλυσίδα", "Αρίθμηση", "Ίδιες διακλαδώσεις", "Αλφαβητική σειρά"].map','["Χωρίς διακλαδώσεις", "Με διακλαδώσεις"].map',1).replace('text: "Διάλεξε σετ αποστολών"','text: "Διάλεξε κατηγορία"',1)
a=s.index('  function progressList() {')
s=s[:a]+'''  function renderSetPicker() {
    renderId += 1;
    const cards = game.sets.map(function (set) {
      const titleId = "set-" + set.id + "-title";
      return node("article", { class: "workshop-set-card", "aria-labelledby": titleId }, [
        node("span", { class: "workshop-set-kind", text: "ΣΕΤ ΑΠΟΣΤΟΛΩΝ" }),
        node("h3", { id: titleId, text: set.title }),
        node("p", { text: set.description }),
        node("div", { class: "workshop-set-meta" }, [node("span", { text: "3 κουίζ" }), node("span", { text: "Χωρίς χρονόμετρο" })]),
        node("ul", { class: "workshop-set-topics" }, set.topics.map(function (text) { return node("li", { text: text }); })),
        button("Ξεκίνα το σετ →", "primary workshop-set-start", function () {
          activeSet = set;
          roundIndex = 0;
          states = set.rounds.map(function (round) { return createRoundState(round); });
          renderRound();
        }, { id: "set-" + set.id + "-start" })
      ]);
    });
    replaceRoot(node("div", { class: "workshop-hub workshop-set-picker" }, [
      node("section", { class: "workshop-hero" }, [
        button("← Όλα τα σετ", "secondary workshop-all-sets", function () { renderWelcome(); focusHeading(); }, { id: "workshop-all-sets" }),
        node("p", { class: "eyebrow", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" }),
        node("h1", { text: "Αλκάνια" }),
        node("p", { class: "workshop-description", text: "Διάλεξε αλκάνια χωρίς ή με διακλαδώσεις. Κάθε σετ έχει τρία σύντομα κουίζ." })
      ]),
      node("section", { class: "workshop-sets", "aria-labelledby": "alkane-sets-title" }, [
        node("h2", { id: "alkane-sets-title", text: "Διάλεξε σετ" }),
        node("div", { class: "workshop-set-grid" }, cards)
      ])
    ]));
  }

'''+s[a:]
# Only the standalone shell now uses the selected set's rounds.
a=s.index('  function progressList() {');s=s[:a]+s[a:].replace('game.rounds','activeSet.rounds')
s=s.replace('const label = "Αποστολή " + (index + 1);','const label = "Κουίζ " + (index + 1);',1)
s=s.replace('round: round(), initialState: state(), assetBase: "", progressList: progressList,','round: round(), initialState: state(), assetBase: "", progressList: progressList, setTitle: activeSet.title,',1)
s=s.replace('"Επόμενη αποστολή  →"','"Επόμενο κουίζ  →"',1)
s=s.replace('''    states = activeSet.rounds.map(function (data) { return createRoundState(data); });
    renderWelcome();''','''    states = [];
    activeSet = null;
    renderSetPicker();''',1)
s=s.replace('[summary.completed, "Αποστολές που ολοκληρώθηκαν"]','[summary.completed, "Κουίζ που ολοκληρώθηκαν"]',1)
s=s.replace('node("h1", { text: "Τέσσερα ονόματα στη θέση τους" }),','node("p", { class: "results-set-name", text: "Αλκάνια · " + activeSet.title }),\n        node("h1", { text: summary.total + " ονόματα στη θέση τους" }),',1)
s=s.replace('text: "Ολοκλήρωσες και τις τέσσερις αποστολές. Κράτησε τη σύνδεση ανάμεσα στη δομή, την αρίθμηση και τα κομμάτια κάθε ονόματος."','text: "Ολοκλήρωσες και τα " + summary.total + " κουίζ του σετ. Κράτησε τη σύνδεση ανάμεσα στη δομή και τα κομμάτια κάθε ονόματος."',1)
s=s.replace('text: "Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε αποστολής."','text: "Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε κουίζ."',1)
p.write_text(s)
