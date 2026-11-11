/* One lesson gate, two independent games. Only a rechecked triple earns access. */
(function (global) {
  "use strict";
  const VERSION = 1;
  const CHANNEL = "namelecule-builder-lesson-v1";
  const generated = global.NameleculeGeneratedRepairCheckpoint;
  const repair = generated.adapter;
  const builder = global.NameleculeNameBuilderEngine;
  const clone = value => JSON.parse(JSON.stringify(value));
  const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
  const validGame = value => value === "repair" || value === "builder";
  const seedValue = value => typeof value === "string" && /^[0-9]{1,20}$/.test(value) ? value : null;
  let canonical = null;
  const REQUIRED = new Map();
  const PRACTICE = new Map();
  function assert(condition, message) { if (!condition) throw new Error(message); }
  function cancelled(signal) {
    if (signal && signal.aborted) { const error = new Error("Checkpoint preparation cancelled"); error.name = "AbortError"; throw error; }
  }
  function validate(recipe) { repair.validate(recipe); assert(builder, "Name builder engine unavailable"); return recipe; }
  function key(recipe, seed) { return recipe.setId + ":" + seed; }
  function hash(text) {
    let value = 2166136261;
    for (let i = 0; i < text.length; i++) value = Math.imul(value ^ text.charCodeAt(i), 16777619);
    return value >>> 0;
  }
  function shuffled(values, seed) {
    let state = hash(seed);
    const result = values.slice();
    for (let i = result.length - 1; i > 0; i--) {
      state = (state + 0x6d2b79f5) | 0;
      let n = Math.imul(state ^ (state >>> 15), state | 1);
      n ^= n + Math.imul(n ^ (n >>> 7), n | 61);
      const j = Math.floor((((n ^ (n >>> 14)) >>> 0) / 4294967296) * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }
  function explanation(analysis) {
    const count = analysis.chain.length;
    const root = analysis.parts[5];
    const bond = analysis.parts[6];
    const main = "Το «" + root + "» δηλώνει " + (count === 1 ? "το ένα άτομο C" : "τα " + count + " άτομα C") + " της κύριας αλυσίδας.";
    const bonds = analysis.carbonCount === 1
      ? " Το μεθάνιο έχει ένα άτομο C και δεν έχει δεσμούς μεταξύ ατόμων C. Ανήκει στους κορεσμένους υδρογονάνθρακες, δηλαδή στα αλκάνια, και το «" + analysis.parts[9] + "» δηλώνει τη χημική τάξη των υδρογονανθράκων."
      : " Το «" + bond + "» δηλώνει τους απλούς δεσμούς μεταξύ ατόμων C και το «" + analysis.parts[9] + "» τη χημική τάξη των υδρογονανθράκων.";
    const groups = new Map();
    analysis.branches.forEach(branch => { if (!groups.has(branch.name)) groups.set(branch.name, []); groups.get(branch.name).push(branch.locant); });
    const branches = Array.from(groups, ([name, locants]) => " Οι διακλαδώσεις «" + name + "» βρίσκονται " +
      (locants.length === 1 ? "στη θέση " : "στις θέσεις ") + locants.sort((a, b) => a - b).join(", ") + ".").join("");
    return main + bonds + branches;
  }
  function builderSet(recipe, seed, practice) {
    const cache = practice ? PRACTICE : REQUIRED;
    const cacheKey = key(recipe, seed);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    if (!canonical || !seed) return null;
    const branched = recipe.setId === "alkanes-branched";
    const eligible = canonical.analyses.filter(analysis => (analysis.branches.length > 0) === branched);
    const chosen = shuffled(eligible, JSON.stringify(["builder-v1", recipe.setId, recipe.catalogRevision, seed])).slice(0, 3);
    assert(chosen.length === 3 && new Set(chosen.map(a => a.moleculeId)).size === 3, "Three distinct structures unavailable");
    const rounds = chosen.map((analysis, index) => {
      const roundId = "lesson-builder-" + recipe.setId + "-" + seed + "-" + index;
      const pieces = analysis.parts.map((text, slot) => text ? { text: text.normalize("NFC"), separatorBefore: "", role: "slot-" + slot } : null).filter(Boolean);
      const round = builder.validateRound({ roundId, moleculeId: analysis.moleculeId, correctName: analysis.name.normalize("NFC"),
        series: "alkanes", parentLength: analysis.chain.length, pieces,
        vocabulary: { roots: analysis.rootVocabulary.slice(0, branched ? 6 : 5).map(text => text.normalize("NFC")) },
        representations: analysis.moleculeId === "methane" ? ["condensed", "expanded", "3d"] : ["condensed", "expanded", "skeletal", "3d"] });
      const bankSeed = roundId + ":bank";
      return { round, bankSeed, bank: builder.createBank(round, { seed: bankSeed }), explanation: explanation(analysis) };
    });
    const set = { rounds };
    // Required receipts never share the small optional-attempt cache.
    if (practice && cache.size >= 2) cache.delete(cache.keys().next().value);
    cache.set(cacheKey, set);
    return set;
  }
  function emptyBuilder(seed) { return { version: VERSION, seed: seed || null, currentRound: 0, states: [null, null, null], solved: false }; }
  function builderSnapshot(entry, raw) {
    const blank = { answer: [], selected: null, attempts: 0, submitted: false, solved: false };
    if (!raw || typeof raw !== "object" || !Array.isArray(raw.answer) || raw.answer.length > 128 ||
      !raw.answer.every(id => typeof id === "string" && id.length <= 128) || new Set(raw.answer).size !== raw.answer.length) return blank;
    if (!entry) return { answer: raw.answer.slice(), selected: raw.answer.includes(raw.selected) ? raw.selected : null,
      attempts: Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0, submitted: raw.submitted === true, solved: false };
    const byId = new Map(entry.bank.map(tile => [tile.id, tile]));
    if (raw.answer.some(id => !byId.has(id))) return blank;
    const attempts = Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0;
    const submitted = raw.submitted === true && attempts > 0 && raw.answer.length > 0;
    return { answer: raw.answer.slice(), selected: raw.answer.includes(raw.selected) ? raw.selected : null,
      attempts, submitted, solved: submitted && builder.evaluate(entry.round, raw.answer.map(id => byId.get(id))).correct === true };
  }
  function restoreBuilder(recipe, previous, practice) {
    const seed = previous && previous.version === VERSION && seedValue(previous.seed);
    if (!seed) return emptyBuilder(null);
    const state = emptyBuilder(seed);
    const set = builderSet(recipe, seed, practice);
    const raw = Array.isArray(previous.states) && previous.states.length === 3 ? previous.states : [null, null, null];
    state.states = raw.map((value, index) => builderSnapshot(set && set.rounds[index], value));
    state.currentRound = Number.isInteger(previous.currentRound) && previous.currentRound >= 0 && previous.currentRound < 3 ? previous.currentRound : 0;
    if (set) {
      const first = state.states.findIndex(value => !value.solved);
      if (first >= 0) {
        state.currentRound = Math.min(state.currentRound, first);
        for (let index = first + 1; index < 3; index++) state.states[index] = builderSnapshot(set.rounds[index], null);
      } else state.solved = true;
    }
    return state;
  }
  function restoreGame(recipe, game, raw, practice) {
    return game === "builder" ? restoreBuilder(recipe, raw, practice) : (practice ? repair.restorePractice : repair.restore)(recipe, raw);
  }
  function restoreComposite(recipe, previous, practice) {
    validate(recipe);
    const raw = previous && previous.version === VERSION ? previous : {};
    const games = raw.games && typeof raw.games === "object" ? raw.games : {};
    // Migrated Workshop answers remain raw evidence, never an imported boolean.
    const legacy = raw.legacyRepair;
    const state = { version: VERSION, selected: validGame(raw.selected) ? raw.selected : (legacy ? "repair" : null),
      games: { repair: restoreGame(recipe, "repair", legacy || games.repair, practice), builder: restoreGame(recipe, "builder", games.builder, practice) },
      earned: null, solved: false };
    if (raw.earned && validGame(raw.earned.game)) {
      const evidence = restoreGame(recipe, raw.earned.game, raw.earned.evidence, practice);
      state.earned = { game: raw.earned.game, evidence };
      state.solved = evidence.solved === true;
    }
    // The first verified winning triple becomes the independent receipt. Later
    // optional attempts cannot overwrite it or combine evidence across games.
    if (!state.earned) {
      const winner = [state.selected, "repair", "builder"].find(game => validGame(game) && state.games[game].solved);
      if (winner) { state.earned = { game: winner, evidence: clone(state.games[winner]) }; state.solved = true; }
    }
    return state;
  }
  function restore(recipe, previous) { return restoreComposite(recipe, previous, false); }
  function restorePractice(recipe, previous) { return restoreComposite(recipe, previous, true); }
  async function loadInput(signal) {
    canonical = await generated.loadCanonicalInput(signal);
    cancelled(signal);
  }
  function prepare(recipe, previous, options) {
    const state = restore(recipe, previous);
    const signal = options && options.signal;
    const repairEvidence = [state.games.repair, state.earned && state.earned.game === "repair" && state.earned.evidence].filter(Boolean);
    const jobs = repairEvidence.map(value => repair.prepare(recipe, value, { signal })).filter(Boolean);
    const builderEvidence = [state.games.builder, state.earned && state.earned.game === "builder" && state.earned.evidence].filter(Boolean);
    if (!canonical && builderEvidence.some(value => value.seed)) jobs.push(loadInput(signal));
    if (!jobs.length) return null;
    return Promise.all(jobs).then(() => { cancelled(signal); return restore(recipe, state); });
  }
  function createPractice(recipe, previous, options) {
    validate(recipe);
    const game = options && validGame(options.game) ? options.game : previous && validGame(previous.selected) ? previous.selected : "repair";
    const state = restorePractice(recipe, null);
    state.selected = game;
    const old = previous && previous.games && previous.games[game];
    state.games[game] = game === "repair" ? repair.createPractice(recipe, old) : emptyBuilder(generated.freshSeed(old && old.seed));
    return state;
  }
  function otherGame(recipe, state) {
    validate(recipe);
    const selected = state && (state.selected || state.earned && state.earned.game);
    return selected === "builder" ? "repair" : "builder";
  }
  function labels(_recipe, lang) {
    if (lang === "en") return { label: "Choose a name game", instruction: "Complete three different molecules in one game to continue.",
      open: "Choose a game", done: "Three molecules completed. You can continue.", revisit: "Return to the games", practiceTitle: "Optional name practice",
      practiceNote: "You have earned access. You can continue the lesson at any time." };
    return { label: "Διάλεξε παιχνίδι ονοματολογίας", instruction: "Ολοκλήρωσε τρία διαφορετικά μόρια στο ίδιο παιχνίδι για να συνεχίσεις.",
      open: "Διάλεξε παιχνίδι", done: "Η τριάδα ολοκληρώθηκε. Μπορείς να συνεχίσεις.", revisit: "Επιστροφή στα παιχνίδια", practiceTitle: "Προαιρετική εξάσκηση στα ονόματα",
      practiceNote: "Η συνέχεια έχει ανοίξει. Μπορείς να συνεχίσεις τη θεωρία οποιαδήποτε στιγμή." };
  }
  function node(tag, className, text) {
    const value = global.document.createElement(tag);
    if (className) value.className = className;
    if (text) value.textContent = text;
    return value;
  }
  function button(text, className, action) {
    const value = node("button", className, text); value.type = "button"; value.addEventListener("click", action); return value;
  }
  function mountComposite(host, options, practice) {
    const recipe = validate(options.round);
    const normalize = practice ? restorePractice : restore;
    let state = normalize(recipe, options.initialState);
    let current = null, destroyed = false, token = 0;
    function ready(value) { if (!destroyed && typeof options.onSuccessActionsReady === "function") options.onSuccessActionsReady(value === true); }
    function progress(value) { if (!destroyed && typeof options.onProgress === "function") options.onProgress(value); }
    function publish() {
      state = normalize(recipe, state);
      if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(clone(state));
    }
    function stop() { token++; if (current) current.destroy(); current = null; ready(false); progress(null); }
    function choose() {
      if (destroyed) return;
      stop(); state.selected = null; publish(); host.removeAttribute("aria-busy");
      const title = node("h2", "nl-game-choice-heading", "Με ποιο παιχνίδι θέλεις να εξασκηθείς;");
      const note = node("p", "nl-game-choice-note", "Τρία διαφορετικά μόρια στο ίδιο παιχνίδι ανοίγουν τη συνέχεια. Η πρόοδός σου κρατιέται χωριστά για κάθε παιχνίδι.");
      const grid = node("div", "nl-game-choice-grid");
      [["repair", "Συνεργείο ονομάτων", "Εντόπισε το λάθος και επισκεύασε το όνομα.", "name-repair/workshop-logo-3d-v1.png"],
        ["builder", "Χτίσε το όνομα", "Διάλεξε τα συνθετικά και βάλε τα στη σωστή σειρά.", "name-builder/name-builder-logo-3d-blank-v1.png"]].forEach(([game, label, detail, image]) => {
        const card = button("", "nl-game-choice-card", () => { state.selected = game; publish(); render(); });
        const img = node("img"); img.src = new URL("games/assets/" + image, global.document.baseURI).href; img.width = 40; img.height = 40; img.alt = ""; img.setAttribute("aria-hidden", "true");
        const copy = node("div", "nl-game-choice-copy"); copy.append(node("strong", "", label), node("span", "", detail));
        card.append(img, copy); grid.append(card);
      });
      host.replaceChildren(title, note, grid);
    }
    function render() {
      if (destroyed) return;
      if (!state.selected) { choose(); return; }
      stop();
      const game = state.selected;
      const activeToken = token;
      const switcher = button("Άλλαξε παιχνίδι", "nl-quiz-button nl-game-choice-switch", choose);
      const gameHost = node("div", game === "builder" ? "nl-builder-host" : "nl-game-choice-repair");
      host.replaceChildren(switcher, gameHost);
      function accept(raw) {
        if (destroyed || token !== activeToken) return;
        state.games[game] = restoreGame(recipe, game, raw, practice);
        publish();
      }
      const settings = Object.assign({}, options, { initialState: state.games[game], onStateChange: accept,
        onSolved(result, raw) {
          accept(raw);
          if (!destroyed && token === activeToken && state.solved && typeof options.onSolved === "function") options.onSolved(result, clone(state));
        },
        onProgress: progress,
        onSuccessActionsReady: ready,
        onOtherGame: options.onOtherGame,
        otherGameLabel: options.otherGameLabel || "Άλλο παιχνίδι"
      });
      current = game === "repair" ? (practice ? repair.mountPractice : repair.mount)(gameHost, settings) : mountBuilder(gameHost, settings, practice);
    }
    if (state.selected) render(); else choose();
    return { destroy() { if (destroyed) return; stop(); destroyed = true; host.replaceChildren(); } };
  }
  function mountBuilder(host, options, practice) {
    const recipe = options.round;
    let state = restoreBuilder(recipe, options.initialState, practice);
    if (!state.seed) state.seed = generated.freshSeed(null);
    const controller = new AbortController();
    let destroyed = false, frame = null, timeout = null, requestId = 0, active = null, footer = null;
    const values = new Uint32Array(4); global.crypto.getRandomValues(values);
    const session = Array.from(values, value => value.toString(36).padStart(7, "0")).join("");
    const attemptId = "builder-" + recipe.setId + "-" + state.seed;
    function ready(value) { if (!destroyed && typeof options.onSuccessActionsReady === "function") options.onSuccessActionsReady(value === true); }
    function progress(value) { if (!destroyed && typeof options.onProgress === "function") options.onProgress(value); }
    function publish() { state = restoreBuilder(recipe, state, practice); if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(clone(state)); }
    function clearTimer() { if (timeout) global.clearTimeout(timeout); timeout = null; }
    function stopFrame() { clearTimer(); active = null; if (frame) { frame.remove(); frame = null; } if (footer) footer.remove(); footer = null; ready(false); }
    function reveal(start, end) { if (!destroyed && typeof options.onReveal === "function") options.onReveal({ kind: "builder-feedback", start, end: end || start }); }
    function failure(message) {
      if (destroyed) return;
      stopFrame(); progress(null); host.setAttribute("aria-busy", "false");
      const error = node("p", "nl-builder-error nl-quiz-error", message); error.setAttribute("role", "alert");
      const retry = button("Δοκίμασε ξανά", "nl-quiz-button", start);
      host.replaceChildren(error, retry);
    }
    function actions(set, index, stage) {
      if (destroyed || !active || !active.loaded || !state.states[index].solved) return;
      if (footer) footer.remove();
      footer = node("div", "round-next nl-builder-actions");
      const next = button(index < 2 ? "Επόμενο κουίζ" : "Συνεχίζω τη θεωρία", "nl-quiz-button primary", () => {
        if (destroyed || !state.states[index].solved) return;
        if (index < 2) { state.currentRound = index + 1; publish(); render(set); }
        else if (state.solved && typeof options.onContinue === "function") options.onContinue();
      });
      if (index === 2) next.setAttribute("data-checkpoint-continue", "");
      footer.append(next);
      if (index === 2 && typeof options.onNewPractice === "function") footer.append(button(options.newPracticeLabel || "Άλλη τριάδα για εξάσκηση", "nl-quiz-button secondary", options.onNewPractice));
      if (index === 2 && typeof options.onOtherGame === "function") footer.append(button(options.otherGameLabel || "Άλλο παιχνίδι", "nl-quiz-button secondary", options.onOtherGame));
      stage.after(footer); ready(index === 2 && state.solved && footer.isConnected && !next.disabled);
    }
    function render(set) {
      if (destroyed) return;
      stopFrame();
      const index = state.currentRound, entry = set.rounds[index];
      const heading = node("h2", "nl-builder-heading", "Χτίσε το όνομα");
      const stage = node("div", "nl-builder-stage");
      frame = node("iframe", "nl-builder-frame"); frame.title = "Χτίσε το όνομα — μόριο " + (index + 1) + " από 3"; frame.style.height = "700px";
      const startMarker = node("span", "nl-builder-marker"), endMarker = node("span", "nl-builder-marker");
      [startMarker, endMarker].forEach(marker => { marker.setAttribute("aria-hidden", "true"); marker.style.cssText = "position:absolute;width:1px;height:1px;pointer-events:none;left:0;top:0"; });
      stage.append(frame, startMarker, endMarker); host.replaceChildren(heading, stage); host.setAttribute("aria-busy", "true");
      active = { requestId: ++requestId, index, entry, stage, startMarker, endMarker, loaded: false };
      frame.src = new URL("games/name-builder.html?lessonSession=" + session + "&v=alkanes-game-choice-20261111-r1", global.document.baseURI).href;
      progress({ current: index + 1, total: 3 });
      timeout = global.setTimeout(() => failure("Το παιχνίδι άργησε να φορτώσει. Η προσπάθειά σου διατηρήθηκε. Δοκίμασε ξανά."), 60000);
      heading.tabIndex = -1; heading.focus({ preventScroll: true });
    }
    function receive(event) {
      if (destroyed || !frame || event.origin !== global.location.origin || event.source !== frame.contentWindow) return;
      const data = event.data;
      if (!data || typeof data !== "object" || data.channel !== CHANNEL || data.session !== session || !active) return;
      const context = active;
      if (data.type === "ready") {
        frame.contentWindow.postMessage({ channel: CHANNEL, session, command: "load", requestId: context.requestId, attemptId,
          moleculeId: context.entry.round.moleculeId, round: context.entry.round, bankSeed: context.entry.bankSeed,
          initialState: builderSnapshot(context.entry, state.states[context.index]), explanation: context.entry.explanation }, global.location.origin);
        return;
      }
      if (data.requestId !== context.requestId || data.attemptId !== attemptId || data.moleculeId !== context.entry.round.moleculeId) return;
      if (data.type === "error") { failure("Δεν ήταν δυνατή η ασφαλής προετοιμασία του μορίου. Δοκίμασε ξανά."); return; }
      if (data.type === "exit") { if (typeof options.onClose === "function") options.onClose(); return; }
      if (data.type === "loaded" || data.type === "state") {
        if (data.type === "state" && !context.loaded) return;
        if (data.type === "loaded") { context.loaded = true; clearTimer(); host.setAttribute("aria-busy", "false"); }
        state.states[context.index] = builderSnapshot(context.entry, data.state); publish();
        if (state.states[context.index].solved) {
          actions(builderSet(recipe, state.seed, practice), context.index, context.stage);
          if (state.solved && typeof options.onSolved === "function") options.onSolved({ kind: "correct" }, clone(state));
        } else { if (footer) footer.remove(); footer = null; ready(false); }
      } else if (data.type === "resize" && Number.isFinite(data.height) && data.height >= 80 && data.height <= 8000) {
        frame.style.height = Math.ceil(data.height) + "px";
      } else if (data.type === "reveal" && context.loaded && Number.isFinite(data.startY) && Number.isFinite(data.endY) &&
        data.startY >= 0 && data.endY >= data.startY && data.endY <= 8000) {
        context.startMarker.style.top = data.startY + "px"; context.endMarker.style.top = data.endY + "px";
        reveal(context.startMarker, footer || context.endMarker);
      }
    }
    function start() {
      if (destroyed) return;
      stopFrame(); progress(null); host.setAttribute("aria-busy", "true"); host.replaceChildren(node("p", "nl-quiz-loading", "Ετοιμάζουμε τις τρεις δομές και τα συνθετικά…")); publish();
      loadInput(controller.signal).then(() => { if (destroyed) return; state = restoreBuilder(recipe, state, practice); publish(); render(builderSet(recipe, state.seed, practice)); })
        .catch(error => { if (!destroyed && error.name !== "AbortError") failure("Οι δομές δεν φορτώθηκαν. Δοκίμασε ξανά ή επέστρεψε στη θεωρία."); });
    }
    global.addEventListener("message", receive); start();
    return { destroy() { if (destroyed) return; stopFrame(); progress(null); destroyed = true; controller.abort(); global.removeEventListener("message", receive); host.replaceChildren(); host.removeAttribute("aria-busy"); } };
  }
  // Exact frozen authored-field projection. The controller reads only the one
  // derived legacy key and checks its complete signature; it never scans storage.
  const OLD_FIELDS = {"3":{"title":{"present":true,"value":"Συνεργείο ονομάτων"},"note":{"present":true,"value":"Ώρα για μια μικρή στάση στο <b>Συνεργείο ονομάτων</b>. Άνοιξε το σετ <b>\"Χωρίς διακλαδώσεις\"</b>&nbsp;και επισκεύασε τρία ονόματα.<br><br>Μπορείς να δοκιμάσεις ξανά και να επιστρέψεις στη θεωρία. Η συνέχεια προς τα διακλαδισμένα αλκάνια ανοίγει αφού ολοκληρώσεις σωστά <b>και τις τρεις επισκευές</b> και διαβάσεις τις εξηγήσεις."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"generated-name-repair-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"πήγαινε στο συνεργείο"}},"titleLogo":{"present":true,"value":"workshop"}},"10":{"title":{"present":true,"value":"Στο Συνεργείο: Με διακλαδώσεις"},"note":{"present":true,"value":"Επίστρεψε στο <b>Συνεργείο ονομάτων</b> για το σετ <b>«Με διακλαδώσεις»</b>. Σε κάθε κουίζ εντόπισε το λάθος συνθετικό ή τη λανθασμένη σειρά και επισκεύασε το όνομα.<br><br>Διάβασε την εξήγηση κάθε σωστής επισκευής. Μπορείς να επαναλάβεις τις προσπάθειες. Αφού ολοκληρώσεις σωστά <b>και τα τρία κουίζ</b>, ανοίγει η τελική εξερεύνηση όλων των αλκανίων."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"generated-name-repair-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"πήγαινε στο συνεργείο"}},"titleLogo":{"present":true,"value":"workshop"}}};
  const NEW_FIELDS = {"3":{"title":{"present":true,"value":"Εξάσκηση χωρίς διακλαδώσεις"},"note":{"present":true,"value":"Ώρα για μια μικρή στάση. Διάλεξε το <b>Συνεργείο ονομάτων</b> για να επισκευάσεις ονόματα ή το <b>Χτίσε το όνομα</b> για να τα σχηματίσεις από συνθετικά.\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια χωρίς διακλαδώσεις στο ίδιο παιχνίδι</b> και δες τις εξηγήσεις. Έπειτα μπορείς να συνεχίσεις τη θεωρία, να δοκιμάσεις το άλλο παιχνίδι ή να εξασκηθείς σε άλλη τριάδα."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}},"10":{"title":{"present":true,"value":"Εξάσκηση με διακλαδώσεις"},"note":{"present":true,"value":"Διάλεξε το <b>Συνεργείο ονομάτων</b> ή το <b>Χτίσε το όνομα</b> για τρία διακλαδισμένα αλκάνια. Σύνδεσε την κύρια αλυσίδα, τις θέσεις και τις ομάδες με τα συνθετικά του ονόματος.\n\nΑφού ολοκληρώσεις σωστά <b>και τα τρία μόρια στο ίδιο παιχνίδι</b> και δεις τις εξηγήσεις, μπορείς να συνεχίσεις στην τελική εξερεύνηση, να δοκιμάσεις το άλλο παιχνίδι ή να εξασκηθείς σε άλλη τριάδα."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}}};
  function same(left, right) { return JSON.stringify(left) === JSON.stringify(right); }
  function migrateRecord(scenario, options) {
    if (!scenario || !Array.isArray(scenario.steps) || scenario.steps.length !== 12 || !options || typeof options.read !== "function") return null;
    const projected = clone(scenario);
    for (const index of Object.keys(NEW_FIELDS)) {
      const step = scenario.steps[index];
      if (!step || typeof step !== "object") return null;
      for (const field of Object.keys(NEW_FIELDS[index])) {
        const expected = NEW_FIELDS[index][field];
        if (own(step, field) !== expected.present || expected.present && !same(step[field], expected.value)) return null;
        const prior = OLD_FIELDS[index][field];
        if (prior.present) projected.steps[index][field] = clone(prior.value); else delete projected.steps[index][field];
      }
    }
    const old = options.read(projected);
    if (!old || !old.states || typeof old.states !== "object") return null;
    const states = {}, practices = {};
    for (const index of Object.keys(NEW_FIELDS)) {
      if (own(old.states, index)) states[index] = { version: VERSION, selected: "repair", legacyRepair: clone(old.states[index]) };
      if (old.practices && own(old.practices, index)) practices[index] = { version: VERSION, selected: "repair", legacyRepair: clone(old.practices[index]) };
    }
    return { states, practices };
  }
  global.NameleculeQuizCheckpoints.registerType("alkane-game-choice-set", Object.freeze({ validate, restore, prepare, mount: (host, options) => mountComposite(host, options, false),
    createPractice, restorePractice, mountPractice: (host, options) => mountComposite(host, options, true), otherGame, labels, migrateRecord }));
})(typeof window !== "undefined" ? window : globalThis);
