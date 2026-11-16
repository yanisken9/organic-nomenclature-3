/* One lesson gate, four independent games. Only a rechecked triple earns access. */
(function (global) {
  "use strict";
  const VERSION = 1;
  const CHANNEL = "namelecule-builder-lesson-v1";
  const PUZZLE_CHANNEL = "namelecule-puzzle-lesson-v1";
  const generated = global.NameleculeGeneratedRepairCheckpoint;
  const repair = generated.adapter;
  const builder = global.NameleculeNameBuilderEngine;
  const puzzle = global.NameleculeMolecularPuzzleEngine;
  const clone = value => JSON.parse(JSON.stringify(value));
  const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
  const validGame = value => value === "repair" || value === "builder" || value === "puzzle" || value === "detective";
  const seedValue = value => typeof value === "string" && /^[0-9]{1,20}$/.test(value) ? value : null;
  const moduleURL = global.document?.currentScript?.src || null;
  const scripts = new Map();
  function loadScript(file, api) {
    if (global[api]) return Promise.resolve();
    if (scripts.has(file)) return scripts.get(file);
    const promise = new Promise((resolve, reject) => {
      const script = global.document.createElement("script");
      const base = moduleURL || new URL("js/namelecule-game-choice-checkpoint.js", global.document.baseURI).href;
      script.src = new URL(file + "?v=alkane-levels-20261116-r1", base).href;
      const timer = global.setTimeout(() => finish(new Error("Detective dependency timed out")), 45000);
      function finish(error) {
        global.clearTimeout(timer); script.onload = script.onerror = null;
        if (error) { scripts.delete(file); script.remove(); reject(error); }
        else if (!global[api]) { scripts.delete(file); script.remove(); reject(new Error("Detective API unavailable")); }
        else resolve();
      }
      script.onload = () => finish(); script.onerror = () => finish(new Error("Detective dependency failed"));
      global.document.head.append(script);
    });
    scripts.set(file, promise); return promise;
  }
  function loadDetective(signal, recipe) {
    return Promise.all([loadInput(signal, recipe), loadScript("namelecule-molecular-detective-engine.js", "NameleculeMolecularDetectiveEngine")
      .then(() => loadScript("namelecule-molecular-detective-lesson.js", "NameleculeMolecularDetectiveLesson"))])
      .then(() => { cancelled(signal); });
  }
  function detectivePending(raw) {
    const state = { version: VERSION, seed: raw && raw.version === VERSION && seedValue(raw.seed) || null,
      currentRound: raw && Number.isInteger(raw.currentRound) && raw.currentRound >= 0 && raw.currentRound < 3 ? raw.currentRound : 0,
      states: [null, null, null], solved: false };
    const values = raw && Array.isArray(raw.states) && raw.states.length === 3 ? raw.states : [null, null, null];
    state.states = values.map(value => {
      const blank = { atoms: [], bonds: [], attempts: 0, submitted: false, solved: false };
      if (!value || !Array.isArray(value.atoms) || !Array.isArray(value.bonds) || value.atoms.length > 40 || value.bonds.length > 39 ||
          [value.atoms, value.bonds].some(ids => ids.some(id => !Number.isSafeInteger(id) || id < 1 || id > 40) || new Set(ids).size !== ids.length)) return blank;
      const attempts = Number.isSafeInteger(value.attempts) && value.attempts >= 0 ? value.attempts : 0;
      return { atoms: value.atoms.slice(), bonds: value.bonds.slice(), attempts,
        submitted: value.submitted === true && attempts > 0 && !!(value.atoms.length || value.bonds.length), solved: false };
    });
    return state;
  }
  function mountDetective(host, options, practice) {
    const controller = new AbortController(); let inner = null, destroyed = false;
    host.setAttribute("aria-busy", "true"); host.replaceChildren(node("p", "nl-quiz-loading", "Ετοιμάζουμε τις τρεις αποστολές του Ντεντέκτιβ…"));
    loadDetective(controller.signal, options.round).then(() => {
      if (destroyed) return;
      inner = global.NameleculeMolecularDetectiveLesson.mount(host, Object.assign({}, options, { input: canonicalFor(options.round) }), practice);
    }).catch(error => {
      if (destroyed || error.name === "AbortError") return;
      host.removeAttribute("aria-busy");
      host.replaceChildren(node("p", "nl-quiz-error", "Οι αποστολές δεν φορτώθηκαν. Η προσπάθεια διατηρήθηκε. Επίλεξε ξανά τον Ντεντέκτιβ για επανάληψη."));
    });
    return { destroy() { if (destroyed) return; destroyed = true; controller.abort(); if (inner) inner.destroy(); host.replaceChildren(); host.removeAttribute("aria-busy"); } };
  }
  let canonical = null;
  const canonicalInputs = new Map();
  function canonicalFor(recipe) { return recipe && recipe.version === 2 ? canonicalInputs.get(recipe.catalogRevision) || null : canonical; }
  function levels() { assert(global.NameleculeGameLevels, "Level policy unavailable"); return global.NameleculeGameLevels; }
  const REQUIRED = new Map();
  const PRACTICE = new Map();
  const PUZZLE_REQUIRED = new Map();
  const PUZZLE_PRACTICE = new Map();
  function assert(condition, message) { if (!condition) throw new Error(message); }
  function cancelled(signal) {
    if (signal && signal.aborted) { const error = new Error("Checkpoint preparation cancelled"); error.name = "AbortError"; throw error; }
  }
  function validate(recipe) { repair.validate(recipe); assert(builder && puzzle, "Name game engines unavailable"); return recipe; }
  function key(recipe, seed) { return recipe.version === 2 ? JSON.stringify([recipe, seed]) : recipe.setId + ":" + seed; }
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
    const canonical = canonicalFor(recipe);
    const cache = practice ? PRACTICE : REQUIRED;
    const cacheKey = key(recipe, seed);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    if (!canonical || !seed) return null;
    const branched = recipe.setId === "alkanes-branched";
    const eligible = canonical.analyses.filter(analysis => recipe.version === 2 ? levels().levelFor(analysis.moleculeId) === recipe.level : (analysis.branches.length > 0) === branched);
    const chosen = shuffled(eligible, JSON.stringify(["builder-v1", recipe.setId, recipe.catalogRevision, seed])).slice(0, 3);
    assert(chosen.length === 3 && new Set(chosen.map(a => a.moleculeId)).size === 3, "Three distinct structures unavailable");
    const rounds = chosen.map((analysis, index) => {
      const roundId = "lesson-builder-" + recipe.setId + "-" + seed + "-" + index + (recipe.version === 2 ? "-" + hash(key(recipe, seed)).toString(36) : "");
      const pieces = analysis.parts.map((text, slot) => text ? { text: text.normalize("NFC"), separatorBefore: "", role: "slot-" + slot } : null).filter(Boolean);
      const round = builder.validateRound({ roundId, moleculeId: analysis.moleculeId, correctName: analysis.name.normalize("NFC"),
        series: "alkanes", parentLength: analysis.chain.length, pieces,
        vocabulary: { roots: analysis.rootVocabulary.slice(0, recipe.version === 2 ? (recipe.level === 3 ? 6 : 5) : (branched ? 6 : 5)).map(text => text.normalize("NFC")) },
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
  function puzzleSet(recipe, seed, practice) {
    const canonical = canonicalFor(recipe);
    const cache = practice ? PUZZLE_PRACTICE : PUZZLE_REQUIRED;
    const cacheKey = key(recipe, seed);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    if (!canonical || !seed) return null;
    const branched = recipe.setId === "alkanes-branched";
    const eligible = canonical.analyses.filter(analysis => recipe.version === 2 ? levels().levelFor(analysis.moleculeId) === recipe.level : (analysis.branches.length > 0) === branched);
    const chosen = shuffled(eligible, JSON.stringify(["puzzle-v1", recipe.setId, recipe.catalogRevision, seed])).slice(0, 3);
    assert(chosen.length === 3 && new Set(chosen.map(analysis => analysis.moleculeId)).size === 3, "Three distinct puzzle structures unavailable");
    const rounds = chosen.map(analysis => {
      const source = canonical.catalog.molecules.find(molecule => molecule.id === analysis.moleculeId);
      assert(source, "Puzzle source unavailable");
      return { moleculeId: analysis.moleculeId, name: analysis.name.normalize("NFC"), target: puzzle.parseMol(source.mol), explanation: explanation(analysis) };
    });
    const set = { rounds };
    if (practice && cache.size >= 2) cache.delete(cache.keys().next().value);
    cache.set(cacheKey, set);
    return set;
  }
  function emptyPuzzle(seed) { return { version: VERSION, seed: seed || null, currentRound: 0, states: [null, null, null], solved: false }; }
  function puzzleSnapshot(entry, raw) {
    const blank = { graph: { nodes: [], bonds: [] }, attempts: 0, submitted: false, solved: false };
    if (!raw || typeof raw !== "object" || !raw.graph || !Array.isArray(raw.graph.nodes) || !Array.isArray(raw.graph.bonds) ||
      raw.graph.nodes.length > 32 || raw.graph.bonds.length > 64) return blank;
    const nodes = raw.graph.nodes, bonds = raw.graph.bonds;
    const ids = new Set();
    for (const value of nodes) {
      if (!value || typeof value.id !== "string" || !value.id.length || value.id.length > 128 || ids.has(value.id) ||
        !Number.isInteger(value.hydrogens) || value.hydrogens < 0 || value.hydrogens > 4 ||
        !Number.isFinite(value.x) || value.x < 0 || value.x > 720 || !Number.isFinite(value.y) || value.y < 0 || value.y > 360) return blank;
      ids.add(value.id);
    }
    const edges = new Set();
    for (const value of bonds) {
      if (!value || typeof value.a !== "string" || typeof value.b !== "string" || value.a === value.b ||
        !ids.has(value.a) || !ids.has(value.b) || value.order !== 1) return blank;
      const edge = JSON.stringify(value.a < value.b ? [value.a, value.b] : [value.b, value.a]);
      if (edges.has(edge)) return blank;
      edges.add(edge);
    }
    const graph = { nodes: nodes.map(value => ({ id: value.id, hydrogens: value.hydrogens, x: value.x, y: value.y })),
      bonds: bonds.map(value => ({ a: value.a, b: value.b, order: 1 })) };
    const attempts = Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0;
    const submitted = raw.submitted === true && attempts > 0 && nodes.length > 0;
    return { graph, attempts, submitted, solved: !!entry && submitted && puzzle.grade(graph, entry.target).correct === true };
  }
  function restorePuzzle(recipe, previous, practice) {
    const seed = previous && previous.version === VERSION && seedValue(previous.seed);
    if (!seed) return emptyPuzzle(null);
    const state = emptyPuzzle(seed);
    const set = puzzleSet(recipe, seed, practice);
    const raw = Array.isArray(previous.states) && previous.states.length === 3 ? previous.states : [null, null, null];
    state.states = raw.map((value, index) => puzzleSnapshot(set && set.rounds[index], value));
    state.currentRound = Number.isInteger(previous.currentRound) && previous.currentRound >= 0 && previous.currentRound < 3 ? previous.currentRound : 0;
    if (set) {
      const first = state.states.findIndex(value => !value.solved);
      if (first >= 0) {
        state.currentRound = Math.min(state.currentRound, first);
        for (let index = first + 1; index < 3; index++) state.states[index] = puzzleSnapshot(set.rounds[index], null);
      } else state.solved = true;
    }
    return state;
  }
  function restoreGame(recipe, game, raw, practice) {
    if (game === "detective") return global.NameleculeMolecularDetectiveLesson
      ? global.NameleculeMolecularDetectiveLesson.restore(recipe, raw, canonicalFor(recipe), practice) : detectivePending(raw);
    if (game === "builder") return restoreBuilder(recipe, raw, practice);
    if (game === "puzzle") return restorePuzzle(recipe, raw, practice);
    return (practice ? repair.restorePractice : repair.restore)(recipe, raw);
  }
  function restoreComposite(recipe, previous, practice) {
    validate(recipe);
    const raw = previous && previous.version === VERSION ? previous : {};
    const games = raw.games && typeof raw.games === "object" ? raw.games : {};
    // Migrated Workshop answers remain raw evidence, never an imported boolean.
    const legacy = raw.legacyRepair;
    const state = { version: VERSION, selected: validGame(raw.selected) ? raw.selected : (legacy ? "repair" : null),
      games: { repair: restoreGame(recipe, "repair", legacy || games.repair, practice), builder: restoreGame(recipe, "builder", games.builder, practice), puzzle: restoreGame(recipe, "puzzle", games.puzzle, practice), detective: restoreGame(recipe, "detective", games.detective, practice) },
      earned: null, solved: false };
    if (raw.earned && validGame(raw.earned.game)) {
      const evidence = restoreGame(recipe, raw.earned.game, raw.earned.evidence, practice);
      state.earned = { game: raw.earned.game, evidence };
      state.solved = evidence.solved === true;
    }
    // The first verified winning triple becomes the independent receipt. Later
    // optional attempts cannot overwrite it or combine evidence across games.
    if (!state.earned) {
      const winner = [state.selected, "repair", "builder", "puzzle", "detective"].find(game => validGame(game) && state.games[game].solved);
      if (winner) { state.earned = { game: winner, evidence: clone(state.games[winner]) }; state.solved = true; }
    }
    return state;
  }
  function restore(recipe, previous) { return recipe.version === 2 ? restoreLevels(recipe, previous, false) : restoreComposite(recipe, previous, false); }
  function restorePractice(recipe, previous) { return recipe.version === 2 ? restoreLevels(recipe, previous, true) : restoreComposite(recipe, previous, true); }
  async function loadInput(signal, recipe) {
    const input = await generated.loadCanonicalInput(signal, recipe && recipe.catalogRevision);
    cancelled(signal);
    canonicalInputs.set(input.catalog.revision, input);
    if (input.catalog.revision === generated.catalogDescriptor("legacy").revision) canonical = input;
  }
  function prepare(recipe, previous, options) {
    if (recipe.version === 2) return prepareLevels(recipe, previous, options, false);
    const state = restore(recipe, previous);
    const signal = options && options.signal;
    const repairEvidence = [state.games.repair, state.earned && state.earned.game === "repair" && state.earned.evidence].filter(Boolean);
    const jobs = repairEvidence.map(value => repair.prepare(recipe, value, { signal })).filter(Boolean);
    const graphEvidence = [state.games.builder, state.games.puzzle,
      state.earned && (state.earned.game === "builder" || state.earned.game === "puzzle") && state.earned.evidence].filter(Boolean);
    if (!canonical && graphEvidence.some(value => value.seed)) jobs.push(loadInput(signal));
    const detectiveEvidence = [state.games.detective, state.earned && state.earned.game === "detective" && state.earned.evidence].filter(Boolean);
    // Navigation retries after asynchronous preparation. Once inputs and both
    // APIs are available, restoration above is synchronous: returning another
    // Promise here would keep scenario navigation in an endless retry loop.
    const detectiveReady = canonical && global.NameleculeMolecularDetectiveEngine && global.NameleculeMolecularDetectiveLesson;
    if (!detectiveReady && detectiveEvidence.some(value => value.seed)) jobs.push(loadDetective(signal));
    if (!jobs.length) return null;
    return Promise.all(jobs).then(() => { cancelled(signal); return restore(recipe, state); });
  }
  function createPractice(recipe, previous, options) {
    if (recipe.version === 2) return createLevelPractice(recipe, previous, options);
    validate(recipe);
    const game = options && options.game === null ? null : options && validGame(options.game) ? options.game : previous && validGame(previous.selected) ? previous.selected : "repair";
    const state = restorePractice(recipe, null);
    state.selected = game;
    if (game) {
      const old = previous && previous.games && previous.games[game];
      state.games[game] = game === "repair" ? repair.createPractice(recipe, old) : game === "detective"
        ? detectivePending({ version: VERSION, seed: generated.freshSeed(old && old.seed) })
        : (game === "puzzle" ? emptyPuzzle : emptyBuilder)(generated.freshSeed(old && old.seed));
    }
    return state;
  }
  function otherGame(recipe, state) {
    validate(recipe);
    return null;
  }
  function practiceGame(recipe, state) {
    validate(recipe);
    if (state && validGame(state.selected)) return state.selected;
    return state && state.earned && validGame(state.earned.game) ? state.earned.game : undefined;
  }
  const LEVEL_GAMES = [
    ["repair", "Συνεργείο ονομάτων", "Εντόπισε το λάθος και επισκεύασε το όνομα.", "name-repair/workshop-logo-3d-v1.png"],
    ["builder", "Χτίσε το όνομα", "Διάλεξε τα συνθετικά και βάλε τα στη σωστή σειρά.", "name-builder/name-builder-logo-3d-blank-v1.png"],
    ["puzzle", "Μοριακό παζλ", "Διάβασε το όνομα και σύνδεσε τα κομμάτια του μορίου.", "molecular-puzzle/molecular-puzzle-logo-flat-v7.png"],
    ["detective", "Μοριακός ντεντέκτιβ", "Βρες στη δομή όσα δηλώνει το συνθετικό.", "molecular-detective/molecular-detective-logo-molecule-v2.png"]
  ];
  function attemptRecipe(recipe, context) { return generated.roundRecipe(recipe, context); }
  function restoreAttempt(recipe, game, value, practice, expectedSlot) {
    assert(value && typeof value === "object" && value.context && value.progress, "Invalid saved level attempt");
    const context = levels().validateContext(value.context);
    assert(context.seed && context.seed === value.progress.seed, "Attempt seed/context mismatch");
    assert(expectedSlot === "legacy" ? context.source === "legacy" : context.source === "enriched" && context.level === Number(expectedSlot), "Attempt level/source mismatch");
    const progress = restoreGame(attemptRecipe(recipe, context), game, value.progress, practice);
    assert(progress.seed === context.seed, "Attempt source cannot be restored");
    return { context, progress, practice: practice === true };
  }
  function legacyAttempt(recipe, game, progress, practice) {
    if (!progress || !seedValue(progress.seed)) return null;
    return restoreAttempt(recipe, game, { context: levels().makeContext({ source: "legacy", level: null, seed: progress.seed }), progress }, practice, "legacy");
  }
  function restoreLevels(recipe, previous, practice) {
    validate(recipe);
    const raw = previous && typeof previous === "object" ? previous : {};
    assert(raw.version === undefined || raw.version === 1 || raw.version === 2, "Unknown level progress version");
    if (raw.version === 2) assert(raw.policyVersion === levels().policyVersion, "Unknown saved level policy");
    const state = { version: 2, policyVersion: levels().policyVersion, selected: validGame(raw.selected) ? raw.selected : null,
      selectedLevel: null, activeLevels: {}, games: { repair: {}, builder: {}, puzzle: {}, detective: {} }, receipts: {}, legacyEarned: null,
      resetOnSelect: raw.version === 2 && raw.resetOnSelect === true, solved: false };
    if (raw.version === 2) {
      for (const [game] of LEVEL_GAMES) {
        const slots = raw.games && raw.games[game];
        if (slots && typeof slots === "object") for (const slot of ["legacy", ...recipe.allowedLevels.map(String)]) {
          if (own(slots, slot)) state.games[game][slot] = restoreAttempt(recipe, game, slots[slot],
            practice || slots[slot].practice === true || slot !== "legacy" && !recipe.requiredLevels.includes(Number(slot)), slot);
        }
        const active = raw.activeLevels && raw.activeLevels[game];
        if (active === "legacy" && state.games[game].legacy || recipe.allowedLevels.includes(active)) state.activeLevels[game] = active;
      }
      for (const level of recipe.allowedLevels) {
        const receipt = raw.receipts && raw.receipts[level];
        if (receipt && validGame(receipt.game)) state.receipts[level] = { game: receipt.game, attempt: restoreAttempt(recipe, receipt.game, receipt.attempt, false, String(level)) };
      }
      if (raw.legacyEarned && validGame(raw.legacyEarned.game)) state.legacyEarned = {
        game: raw.legacyEarned.game, attempt: restoreAttempt(recipe, raw.legacyEarned.game, raw.legacyEarned.attempt, false, "legacy") };
      if (raw.selectedLevel === "legacy" && state.selected && state.games[state.selected].legacy || recipe.allowedLevels.includes(raw.selectedLevel)) state.selectedLevel = raw.selectedLevel;
    } else if (raw.version === 1) {
      for (const [game] of LEVEL_GAMES) {
        const old = game === "repair" && raw.legacyRepair || raw.games && raw.games[game];
        const attempt = legacyAttempt(recipe, game, old, practice);
        if (attempt) { state.games[game].legacy = attempt; state.activeLevels[game] = "legacy"; }
      }
      if (raw.legacyRepair) state.selected = "repair";
      if (state.selected && state.games[state.selected].legacy) state.selectedLevel = "legacy";
      if (raw.earned && validGame(raw.earned.game)) {
        const attempt = legacyAttempt(recipe, raw.earned.game, raw.earned.evidence, false);
        if (attempt) state.legacyEarned = { game: raw.earned.game, attempt };
      }
    }
    // Stored booleans never award access. Each candidate is independently regraded
    // against its own source, policy and seed before becoming a retained receipt.
    if (!state.legacyEarned || !state.legacyEarned.attempt.progress.solved) {
      for (const [game] of LEVEL_GAMES) if (state.games[game].legacy && state.games[game].legacy.progress.solved) {
        state.legacyEarned = { game, attempt: restoreAttempt(recipe, game, state.games[game].legacy, false, "legacy") }; break;
      }
    }
    for (const level of recipe.allowedLevels) if (!state.receipts[level] || !state.receipts[level].attempt.progress.solved) {
      for (const [game] of LEVEL_GAMES) {
        const attempt = state.games[game][level];
        if (attempt && attempt.progress.solved) {
          state.receipts[level] = { game, attempt: restoreAttempt(recipe, game, attempt, false, String(level)) }; break;
        }
      }
    }
    state.solved = !!(state.legacyEarned && state.legacyEarned.attempt.progress.solved) ||
      recipe.requiredLevels.every(level => state.receipts[level] && state.receipts[level].attempt.progress.solved);
    return state;
  }
  function levelEvidence(recipe, state) {
    const evidence = [];
    for (const [game] of LEVEL_GAMES) if (state.games[game].legacy) evidence.push({ game, attempt: state.games[game].legacy, practice: state.games[game].legacy.practice === true });
    if (state.selected && state.selectedLevel !== null && state.games[state.selected][state.selectedLevel]) {
      const attempt = state.games[state.selected][state.selectedLevel];
      evidence.push({ game: state.selected, attempt, practice: attempt.practice === true });
    }
    // Receipt verification always uses the required cache, even when the
    // currently displayed attempt is optional or repeats an earned level.
    for (const level of recipe.allowedLevels) if (state.receipts[level]) evidence.push(Object.assign({}, state.receipts[level], { practice: false }));
    if (state.legacyEarned) evidence.push(Object.assign({}, state.legacyEarned, { practice: false }));
    return evidence;
  }
  function prepareLevels(recipe, previous, options, practice) {
    const state = restoreLevels(recipe, previous, practice), signal = options && options.signal;
    const jobs = [], seen = new Set();
    for (const { game, attempt, practice: optional } of levelEvidence(recipe, state)) {
      const round = attemptRecipe(recipe, attempt.context), identity = game + ":" + levels().contextKey(attempt.context) + ":" + optional;
      if (seen.has(identity)) continue; seen.add(identity);
      if (game === "repair") {
        const prepareRound = optional ? repair.preparePractice : repair.prepare;
        assert(typeof prepareRound === "function", "Repair preparation API unavailable");
        const pending = prepareRound(round, attempt.progress, { signal }); if (pending) jobs.push(pending);
      }
      else if (game === "detective") {
        if (!canonicalFor(round) || !global.NameleculeMolecularDetectiveEngine || !global.NameleculeMolecularDetectiveLesson) {
          const id = "detective:" + round.catalogRevision;
          if (!seen.has(id)) { seen.add(id); jobs.push(loadDetective(signal, round)); }
        }
      } else if (!canonicalFor(round)) {
        const id = "input:" + round.catalogRevision;
        if (!seen.has(id)) { seen.add(id); jobs.push(loadInput(signal, round)); }
      }
    }
    // This synchronous boundary is essential: scenarioGo retries after a Promise.
    // Warm sources/rounds must return null, rather than enqueue another retry.
    return jobs.length ? Promise.all(jobs).then(() => { cancelled(signal); return restoreLevels(recipe, state, practice); }) : null;
  }
  function newLevelAttempt(recipe, game, level, previousSeed, practice) {
    const seed = generated.freshSeed(previousSeed || null);
    const context = levels().makeContext({ source: "enriched", level, seed });
    return { context, progress: { version: 1, seed, currentRound: 0, states: [null, null, null], solved: false }, practice: practice === true };
  }
  function createLevelPractice(recipe, previous, options) {
    const state = restoreLevels(recipe, previous, true);
    state.selected = options && options.game === null ? null : options && validGame(options.game) ? options.game : state.selected;
    state.resetOnSelect = !state.selected;
    if (state.selected) {
      const level = recipe.allowedLevels.includes(state.selectedLevel) ? state.selectedLevel : recipe.allowedLevels[0];
      const old = state.games[state.selected][level];
      state.games[state.selected][level] = newLevelAttempt(recipe, state.selected, level, old && old.context.seed, true);
      state.selectedLevel = level; state.activeLevels[state.selected] = level;
    }
    return restoreLevels(recipe, state, true);
  }
  function levelLabels(recipe, lang) {
    const two = recipe.requiredLevels.length === 2;
    if (lang === "en") return { label: "Choose a name game", instruction: two ? "Required: Levels 1 and 2, three correct molecules in each. Level 3 is optional." : "Required: Level 1, three correct molecules.",
      open: "Choose a game", done: "You can continue the lesson.", revisit: "Return to the games", practiceTitle: "Optional name practice", practiceNote: "Access remains unlocked." };
    return { label: "Διάλεξε παιχνίδι ονοματολογίας", instruction: two ? "Υποχρεωτικά τα επίπεδα 1 και 2, με τρία σωστά διαφορετικά μόρια στο καθένα. Το επίπεδο 3 είναι προαιρετικό." : "Υποχρεωτικό το επίπεδο 1, με τρία σωστά διαφορετικά μόρια.",
      open: "Διάλεξε παιχνίδι", done: "Η συνέχεια είναι διαθέσιμη.", revisit: "Επιστροφή στα παιχνίδια", practiceTitle: "Προαιρετική εξάσκηση στα ονόματα", practiceNote: "Το ξεκλείδωμα διατηρείται. Μπορείς να συνεχίσεις τη θεωρία." };
  }
  function mountLevels(host, options, practice) {
    const recipe = validate(options.round);
    let state = restoreLevels(recipe, options.initialState, practice), current = null, selector = null, destroyed = false, token = 0;
    const ready = value => { if (!destroyed && options.onSuccessActionsReady) options.onSuccessActionsReady(value === true && state.solved); };
    const progress = value => { if (!destroyed && options.onProgress) options.onProgress(value); };
    let status = null;
    const completed = () => recipe.allowedLevels.filter(level => state.receipts[level] && state.receipts[level].attempt.progress.solved);
    function publish() {
      state = restoreLevels(recipe, state, practice);
      if (selector) selector.set({ completedLevels: completed() });
      if (status) status.textContent = state.legacyEarned && state.legacyEarned.attempt.progress.solved
        ? "Η προηγούμενη προσπάθεια επαληθεύτηκε. Το ξεκλείδωμα διατηρείται."
        : levelLabels(recipe, "gr").instruction + (completed().length ? " Ολοκληρωμένα επίπεδα " + completed().join(", ") + "." : "");
      if (!destroyed && options.onStateChange) options.onStateChange(clone(state));
    }
    function stop() {
      token++; if (current) current.destroy(); current = null; if (selector) selector.destroy(); selector = null; ready(false); progress(null);
    }
    function selectLevel(level, fresh) {
      assert(recipe.allowedLevels.includes(level), "Unavailable level at this checkpoint");
      const game = state.selected, old = state.games[game][level];
      const optional = practice || !recipe.requiredLevels.includes(level) || !!(state.receipts[level] && state.receipts[level].attempt.progress.solved);
      if (!old || fresh || state.resetOnSelect) state.games[game][level] = newLevelAttempt(recipe, game, level, old && old.context.seed, optional);
      state.resetOnSelect = false; state.selectedLevel = level; state.activeLevels[game] = level; publish(); render();
    }
    function choose() { state.selected = null; state.selectedLevel = null; publish(); render(); }
    function render() {
      if (destroyed) return; stop();
      status = node("p", "nl-game-choice-note", levelLabels(recipe, "gr").instruction);
      status.setAttribute("role", "status");
      if (!state.selected) {
        const grid = node("div", "nl-game-choice-grid");
        for (const [game, title, detail, image] of LEVEL_GAMES) {
          const card = button("", "nl-game-choice-card", () => {
            state.selected = game;
            state.selectedLevel = !state.resetOnSelect ? state.activeLevels[game] || null : null;
            if (recipe.allowedLevels.length === 1 && state.selectedLevel === null) { selectLevel(recipe.allowedLevels[0], false); return; }
            publish(); render();
          });
          const img = node("img"); img.src = new URL("games/assets/" + image, global.document.baseURI).href; img.alt = ""; img.width = 56; img.height = 56;
          if (game === "puzzle") img.style.cssText = "width:120px;height:64px;object-fit:contain";
          const copy = node("div", "nl-game-choice-copy"); copy.append(node("strong", "", title), node("span", "", detail)); card.append(img, copy); grid.append(card);
        }
        host.replaceChildren(node("h2", "nl-game-choice-heading", "Με ποιο παιχνίδι θέλεις να εξασκηθείς;"), status, grid); publish(); return;
      }
      const game = state.selected, activeToken = token;
      const levelHost = node("div"), gameHost = node("div", game === "repair" ? "nl-game-choice-repair" : "nl-builder-host");
      host.replaceChildren(button("Άλλαξε παιχνίδι", "nl-quiz-button nl-game-choice-switch", choose), status, levelHost, gameHost);
      const requirements = Object.fromEntries(recipe.allowedLevels.map(level => [level, recipe.requiredLevels.includes(level) ? "required" : "optional"]));
      selector = levels().mount(levelHost, { availableIds: levels().poolFor(1).concat(levels().poolFor(2), levels().poolFor(3)), allowedLevels: recipe.allowedLevels,
        selectedLevel: Number.isInteger(state.selectedLevel) ? state.selectedLevel : null, requirements, completedLevels: completed(),
        onSelect: value => { if (value.category === "alkanes" && value.level !== null) selectLevel(value.level, false); } });
      if (state.games[game].legacy) levelHost.append(button("Προηγούμενη προσπάθεια", "nl-quiz-button secondary", () => { state.selectedLevel = "legacy"; state.activeLevels[game] = "legacy"; publish(); render(); }));
      const slot = state.selectedLevel;
      if (slot === null) { gameHost.append(node("p", "nl-game-choice-note", "Διάλεξε επίπεδο. Κάθε υποχρεωτικό επίπεδο χρειάζεται τη δική του τριάδα, με παιχνίδι της επιλογής σου.")); publish(); return; }
      if (!state.games[game][slot]) {
        if (slot === "legacy") { choose(); return; }
        state.games[game][slot] = newLevelAttempt(recipe, game, slot, null, practice || !recipe.requiredLevels.includes(slot) || !!state.receipts[slot]);
      }
      const abort = new AbortController(); current = { destroy() { abort.abort(); } }; publish();
      function start() {
        if (destroyed || token !== activeToken || abort.signal.aborted) return;
        const attempt = state.games[game][slot], context = clone(attempt.context), round = attemptRecipe(recipe, context);
        const innerPractice = practice || attempt.practice === true;
        function accept(raw) {
          if (destroyed || token !== activeToken || raw.seed !== context.seed) return;
          state.games[game][slot] = restoreAttempt(recipe, game, { context, progress: raw }, innerPractice, String(slot)); publish();
        }
        const settings = Object.assign({}, options, { round, initialState: clone(attempt.progress), onStateChange: accept,
          continueLabel: () => state.solved ? "Συνεχίζω τη θεωρία" : "Επόμενο υποχρεωτικό επίπεδο",
          onContinue() {
            if (state.solved) { if (options.onContinue) options.onContinue(); }
            else { const next = recipe.requiredLevels.find(level => !state.receipts[level] || !state.receipts[level].attempt.progress.solved); if (next) selectLevel(next, false); }
          },
          onSolved(result, raw) { accept(raw); if (!destroyed && token === activeToken && state.solved && options.onSolved) options.onSolved(result, clone(state)); },
          onProgress: progress, onSuccessActionsReady: ready,
          onNewPractice() {
            if (state.solved && options.onNewPractice) options.onNewPractice();
            else selectLevel(Number.isInteger(slot) ? slot : recipe.allowedLevels[0], true);
          },
          onOtherGame() { if (state.solved && options.onOtherGame) options.onOtherGame(); else choose(); }
        });
        current = game === "repair" ? (innerPractice ? repair.mountPractice : repair.mount)(gameHost, settings)
          : (game === "detective" ? mountDetective : game === "puzzle" ? mountPuzzle : mountBuilder)(gameHost, settings, innerPractice);
      }
      const pending = prepareLevels(recipe, state, { signal: abort.signal }, practice);
      if (!pending) start();
      else { gameHost.append(node("p", "nl-quiz-loading", "Επαληθεύουμε την προσπάθεια και την πρόοδό σου…")); pending.then(start).catch(error => {
        if (!destroyed && token === activeToken && !abort.signal.aborted) gameHost.replaceChildren(node("p", "nl-quiz-error", "Η προσπάθεια δεν επαληθεύτηκε. Δοκίμασε ξανά."), button("Δοκίμασε ξανά", "nl-quiz-button", render));
      }); }
    }
    render();
    return { destroy() { if (destroyed) return; stop(); destroyed = true; host.replaceChildren(); } };
  }

  function labels(_recipe, lang) {
    if (_recipe.version === 2) return levelLabels(_recipe, lang);
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
    if (options.round.version === 2) return mountLevels(host, options, practice);
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
        ["builder", "Χτίσε το όνομα", "Διάλεξε τα συνθετικά και βάλε τα στη σωστή σειρά.", "name-builder/name-builder-logo-3d-blank-v1.png"],
        ["puzzle", "Μοριακό παζλ", "Διάβασε το όνομα και σύνδεσε τα κομμάτια του μορίου.", "molecular-puzzle/molecular-puzzle-logo-flat-v7.png"],
        ["detective", "Μοριακός ντεντέκτιβ", "Βρες στον ανεπτυγμένο τύπο όσα δηλώνει το συνθετικό.", "molecular-detective/molecular-detective-logo-molecule-v2.png"]].forEach(([game, label, detail, image]) => {
        const card = button("", "nl-game-choice-card", () => { state.selected = game; publish(); render(); });
        const img = node("img"); img.src = new URL("games/assets/" + image, global.document.baseURI).href; img.width = 40; img.height = 40; img.alt = ""; img.setAttribute("aria-hidden", "true");
        if (game === "puzzle") { img.width = 120; img.height = 64; img.style.cssText = "width:120px;height:64px;object-fit:contain;flex-shrink:0"; }
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
      const gameHost = node("div", game === "repair" ? "nl-game-choice-repair" : "nl-builder-host");
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
      current = game === "repair" ? (practice ? repair.mountPractice : repair.mount)(gameHost, settings)
        : (game === "detective" ? mountDetective : game === "puzzle" ? mountPuzzle : mountBuilder)(gameHost, settings, practice);
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
    const wireContext = recipe.version === 2 ? levels().makeContext({ source: "enriched", level: recipe.level, seed: state.seed }) : null;
    const attemptId = "builder-" + recipe.setId + "-" + state.seed + (wireContext ? "-" + hash(levels().contextKey(wireContext)).toString(36) : "");
    function ready(value) { if (!destroyed && typeof options.onSuccessActionsReady === "function") options.onSuccessActionsReady(value === true); }
    function progress(value) { if (!destroyed && typeof options.onProgress === "function") options.onProgress(value); }
    function publish() { state = restoreBuilder(recipe, state, practice); if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(clone(state)); }
    function clearTimer() { if (timeout) global.clearTimeout(timeout); timeout = null; }
    function stopFrame() { clearTimer(); active = null; if (frame) { frame.remove(); frame = null; } if (footer) footer.remove(); footer = null; ready(false); }
    function reveal(start, end, purpose) { if (!destroyed && typeof options.onReveal === "function") options.onReveal({ kind: "builder-" + purpose, start, end: end || start }); }
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
      const next = button(index < 2 ? "Επόμενο κουίζ" : (typeof options.continueLabel === "function" ? options.continueLabel() : options.continueLabel || "Συνεχίζω τη θεωρία"), "nl-quiz-button primary", () => {
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
      const title = node("div", "nl-builder-title");
      const logo = node("img", "nl-builder-logo");
      logo.src = new URL("games/assets/name-builder/name-builder-logo-3d-blank-v1.png", global.document.baseURI).href;
      logo.width = 88; logo.height = 88; logo.alt = ""; logo.setAttribute("aria-hidden", "true");
      title.append(logo, heading);
      const stage = node("div", "nl-builder-stage");
      frame = node("iframe", "nl-builder-frame"); frame.title = "Χτίσε το όνομα — μόριο " + (index + 1) + " από 3"; frame.style.height = "700px";
      const startMarker = node("span", "nl-builder-marker"), endMarker = node("span", "nl-builder-marker");
      [startMarker, endMarker].forEach(marker => { marker.setAttribute("aria-hidden", "true"); marker.style.cssText = "position:absolute;width:1px;height:1px;pointer-events:none;left:0;top:0"; });
      stage.append(frame, startMarker, endMarker); host.replaceChildren(title, stage); host.setAttribute("aria-busy", "true");
      active = { requestId: ++requestId, index, entry, stage, startMarker, endMarker, loaded: false };
      frame.src = new URL("games/name-builder.html?lessonSession=" + session + "&v=alkane-levels-20261116-r1", global.document.baseURI).href;
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
          ...(wireContext ? { context: wireContext } : {}), moleculeId: context.entry.round.moleculeId, round: context.entry.round, bankSeed: context.entry.bankSeed,
          initialState: builderSnapshot(context.entry, state.states[context.index]), explanation: context.entry.explanation }, global.location.origin);
        return;
      }
      if (data.requestId !== context.requestId || data.attemptId !== attemptId || data.moleculeId !== context.entry.round.moleculeId) return;
      if (wireContext) { try { if (levels().contextKey(data.context) !== levels().contextKey(wireContext)) return; } catch (_) { return; } }
      if (data.type === "error") { failure("Δεν ήταν δυνατή η ασφαλής προετοιμασία του μορίου. Δοκίμασε ξανά."); return; }
      if (data.type === "exit") { if (typeof options.onClose === "function") options.onClose(); return; }
      if (data.type === "scroll-interrupt") {
        if (context.loaded && typeof options.onScrollInterrupt === "function") options.onScrollInterrupt();
        return;
      }
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
        const purpose = data.purpose === undefined ? "feedback" : data.purpose;
        if (!["entry", "construction", "feedback"].includes(purpose)) return;
        context.startMarker.style.top = data.startY + "px"; context.endMarker.style.top = data.endY + "px";
        reveal(context.startMarker, purpose === "feedback" && footer ? footer : context.endMarker, purpose);
      }
    }
    function start() {
      if (destroyed) return;
      stopFrame(); progress(null); host.setAttribute("aria-busy", "true"); host.replaceChildren(node("p", "nl-quiz-loading", "Ετοιμάζουμε τις τρεις δομές και τα συνθετικά…")); publish();
      loadInput(controller.signal, recipe).then(() => { if (destroyed) return; state = restoreBuilder(recipe, state, practice); publish(); render(builderSet(recipe, state.seed, practice)); })
        .catch(error => { if (!destroyed && error.name !== "AbortError") failure("Οι δομές δεν φορτώθηκαν. Δοκίμασε ξανά ή επέστρεψε στη θεωρία."); });
    }
    global.addEventListener("message", receive); start();
    return { destroy() { if (destroyed) return; stopFrame(); progress(null); destroyed = true; controller.abort(); global.removeEventListener("message", receive); host.replaceChildren(); host.removeAttribute("aria-busy"); } };
  }
  function mountPuzzle(host, options, practice) {
    const recipe = options.round;
    let state = restorePuzzle(recipe, options.initialState, practice);
    if (!state.seed) state.seed = generated.freshSeed(null);
    const controller = new AbortController();
    let destroyed = false, frame = null, timeout = null, requestId = 0, active = null, footer = null;
    const values = new Uint32Array(4); global.crypto.getRandomValues(values);
    const session = Array.from(values, value => value.toString(36).padStart(7, "0")).join("");
    const wireContext = recipe.version === 2 ? levels().makeContext({ source: "enriched", level: recipe.level, seed: state.seed }) : null;
    const attemptId = "puzzle-" + recipe.setId + "-" + state.seed + (wireContext ? "-" + hash(levels().contextKey(wireContext)).toString(36) : "");
    function ready(value) { if (!destroyed && typeof options.onSuccessActionsReady === "function") options.onSuccessActionsReady(value === true); }
    function progress(value) { if (!destroyed && typeof options.onProgress === "function") options.onProgress(value); }
    function publish() { state = restorePuzzle(recipe, state, practice); if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(clone(state)); }
    function clearTimer() { if (timeout) global.clearTimeout(timeout); timeout = null; }
    function stopFrame() { clearTimer(); active = null; if (frame) { frame.remove(); frame = null; } if (footer) footer.remove(); footer = null; ready(false); }
    function failure(message) {
      if (destroyed) return;
      stopFrame(); progress(null); host.setAttribute("aria-busy", "false");
      const error = node("p", "nl-builder-error nl-quiz-error", message); error.setAttribute("role", "alert");
      host.replaceChildren(error, button("Δοκίμασε ξανά", "nl-quiz-button", start));
    }
    function actions(set, index, stage) {
      if (destroyed || !active || !active.loaded || !state.states[index].solved) return;
      if (footer) footer.remove();
      footer = node("div", "round-next nl-builder-actions nl-puzzle-actions");
      const next = button(index < 2 ? "Επόμενο κουίζ" : (typeof options.continueLabel === "function" ? options.continueLabel() : options.continueLabel || "Συνεχίζω τη θεωρία"), "nl-quiz-button primary", () => {
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
      const stage = node("div", "nl-builder-stage nl-puzzle-stage");
      frame = node("iframe", "nl-builder-frame nl-puzzle-frame");
      frame.title = "Μοριακό παζλ — μόριο " + (index + 1) + " από 3"; frame.style.height = "700px";
      const startMarker = node("span", "nl-builder-marker"), endMarker = node("span", "nl-builder-marker");
      [startMarker, endMarker].forEach(marker => { marker.setAttribute("aria-hidden", "true"); marker.style.cssText = "position:absolute;width:1px;height:1px;pointer-events:none;left:0;top:0"; });
      // The child owns its logo/title; the same header is never rendered twice.
      stage.append(frame, startMarker, endMarker); host.replaceChildren(stage); host.setAttribute("aria-busy", "true");
      active = { requestId: ++requestId, index, entry, stage, startMarker, endMarker, loaded: false };
      frame.src = new URL("games/molecular-puzzle.html?embedded=1&lessonSession=" + session + "&v=alkane-levels-20261116-r1", global.document.baseURI).href;
      progress({ current: index + 1, total: 3 });
      timeout = global.setTimeout(() => failure("Το παζλ άργησε να φορτώσει. Η προσπάθειά σου διατηρήθηκε. Δοκίμασε ξανά."), 60000);
    }
    function receive(event) {
      if (destroyed || !frame || event.origin !== global.location.origin || event.source !== frame.contentWindow) return;
      const data = event.data;
      if (!data || typeof data !== "object" || data.channel !== PUZZLE_CHANNEL || data.session !== session || !active) return;
      const context = active;
      if (data.type === "ready") {
        if (context.loaded) return;
        frame.contentWindow.postMessage({ channel: PUZZLE_CHANNEL, session, command: "load", requestId: context.requestId, attemptId,
          ...(wireContext ? { context: wireContext } : {}), moleculeId: context.entry.moleculeId, correctName: context.entry.name,
          initialState: puzzleSnapshot(context.entry, state.states[context.index]), explanation: context.entry.explanation }, global.location.origin);
        return;
      }
      if (data.requestId !== context.requestId || data.attemptId !== attemptId || data.moleculeId !== context.entry.moleculeId) return;
      if (wireContext) { try { if (levels().contextKey(data.context) !== levels().contextKey(wireContext)) return; } catch (_) { return; } }
      if (data.type === "error") { failure("Δεν ήταν δυνατή η ασφαλής προετοιμασία του παζλ. Δοκίμασε ξανά."); return; }
      if (data.type === "exit") { if (typeof options.onClose === "function") options.onClose(); return; }
      if (data.type === "scroll-interrupt") {
        if (context.loaded && typeof options.onScrollInterrupt === "function") options.onScrollInterrupt();
        return;
      }
      if (data.type === "loaded" || data.type === "state") {
        if (data.type === "state" && !context.loaded) return;
        if (data.type === "loaded") { context.loaded = true; clearTimer(); host.setAttribute("aria-busy", "false"); }
        // Never trust a child solved flag: recheck its bounded graph against the
        // independently verified source MOL before recording any earned access.
        state.states[context.index] = puzzleSnapshot(context.entry, data.state); publish();
        if (state.states[context.index].solved) {
          actions(puzzleSet(recipe, state.seed, practice), context.index, context.stage);
          if (state.solved && typeof options.onSolved === "function") options.onSolved({ kind: "correct" }, clone(state));
        } else { if (footer) footer.remove(); footer = null; ready(false); }
      } else if (data.type === "resize" && Number.isFinite(data.height) && data.height >= 80 && data.height <= 8000) {
        frame.style.height = Math.ceil(data.height) + "px";
      } else if (data.type === "reveal" && context.loaded && Number.isFinite(data.startY) && Number.isFinite(data.endY) &&
        data.startY >= 0 && data.endY >= data.startY && data.endY <= 8000) {
        const purpose = data.purpose === undefined ? "feedback" : data.purpose;
        if (!["entry", "construction", "feedback"].includes(purpose)) return;
        context.startMarker.style.top = data.startY + "px"; context.endMarker.style.top = data.endY + "px";
        if (typeof options.onReveal === "function") options.onReveal({ kind: "puzzle-" + purpose, start: context.startMarker,
          end: purpose === "feedback" && footer ? footer : context.endMarker });
      }
    }
    function start() {
      if (destroyed) return;
      stopFrame(); progress(null); host.setAttribute("aria-busy", "true"); host.replaceChildren(node("p", "nl-quiz-loading", "Ετοιμάζουμε τα τρία μόρια του παζλ…")); publish();
      loadInput(controller.signal, recipe).then(() => { if (destroyed) return; state = restorePuzzle(recipe, state, practice); publish(); render(puzzleSet(recipe, state.seed, practice)); })
        .catch(error => { if (!destroyed && error.name !== "AbortError") failure("Οι δομές του παζλ δεν φορτώθηκαν. Δοκίμασε ξανά ή επέστρεψε στη θεωρία."); });
    }
    global.addEventListener("message", receive); start();
    return { destroy() { if (destroyed) return; stopFrame(); progress(null); destroyed = true; controller.abort(); global.removeEventListener("message", receive); host.replaceChildren(); host.removeAttribute("aria-busy"); } };
  }
  // Exact frozen authored-field projection. The controller reads only the one
  // derived legacy key and checks its complete signature; it never scans storage.
  const OLD_FIELDS = {"3":{"title":{"present":true,"value":"Συνεργείο ονομάτων"},"note":{"present":true,"value":"Ώρα για μια μικρή στάση στο <b>Συνεργείο ονομάτων</b>. Άνοιξε το σετ <b>\"Χωρίς διακλαδώσεις\"</b>&nbsp;και επισκεύασε τρία ονόματα.<br><br>Μπορείς να δοκιμάσεις ξανά και να επιστρέψεις στη θεωρία. Η συνέχεια προς τα διακλαδισμένα αλκάνια ανοίγει αφού ολοκληρώσεις σωστά <b>και τις τρεις επισκευές</b> και διαβάσεις τις εξηγήσεις."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"generated-name-repair-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"πήγαινε στο συνεργείο"}},"titleLogo":{"present":true,"value":"workshop"}},"10":{"title":{"present":true,"value":"Στο Συνεργείο: Με διακλαδώσεις"},"note":{"present":true,"value":"Επίστρεψε στο <b>Συνεργείο ονομάτων</b> για το σετ <b>«Με διακλαδώσεις»</b>. Σε κάθε κουίζ εντόπισε το λάθος συνθετικό ή τη λανθασμένη σειρά και επισκεύασε το όνομα.<br><br>Διάβασε την εξήγηση κάθε σωστής επισκευής. Μπορείς να επαναλάβεις τις προσπάθειες. Αφού ολοκληρώσεις σωστά <b>και τα τρία κουίζ</b>, ανοίγει η τελική εξερεύνηση όλων των αλκανίων."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"generated-name-repair-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"πήγαινε στο συνεργείο"}},"titleLogo":{"present":true,"value":"workshop"}}};
  const THREE_FIELDS = {"3":{"title":{"present":true,"value":"Εξάσκηση χωρίς διακλαδώσεις"},"note":{"present":true,"value":"Ώρα για μια μικρή στάση. Διάλεξε το <b>Συνεργείο ονομάτων</b> για να επισκευάσεις ονόματα ή το <b>Χτίσε το όνομα</b> για να τα σχηματίσεις από συνθετικά.\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια χωρίς διακλαδώσεις στο ίδιο παιχνίδι</b> και δες τις εξηγήσεις. Έπειτα μπορείς να συνεχίσεις τη θεωρία, να δοκιμάσεις το άλλο παιχνίδι ή να εξασκηθείς σε άλλη τριάδα."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}},"10":{"title":{"present":true,"value":"Εξάσκηση με διακλαδώσεις"},"note":{"present":true,"value":"Διάλεξε το <b>Συνεργείο ονομάτων</b> ή το <b>Χτίσε το όνομα</b> για τρία διακλαδισμένα αλκάνια. Σύνδεσε την κύρια αλυσίδα, τις θέσεις και τις ομάδες με τα συνθετικά του ονόματος.\n\nΑφού ολοκληρώσεις σωστά <b>και τα τρία μόρια στο ίδιο παιχνίδι</b> και δεις τις εξηγήσεις, μπορείς να συνεχίσεις στην τελική εξερεύνηση, να δοκιμάσεις το άλλο παιχνίδι ή να εξασκηθείς σε άλλη τριάδα."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}}};
  const NEW_FIELDS = {"3":{"title":{"present":true,"value":"Εξάσκηση χωρίς διακλαδώσεις"},"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια χωρίς διακλαδώσεις στο ίδιο παιχνίδι</b> και δες την εξήγηση μετά από κάθε σωστή απάντηση. Στον Ντεντέκτιβ χρειάζεται <b>μία αποστολή ανά μόριο</b>. Έπειτα μπορείς να συνεχίσεις τη θεωρία, να εξασκηθείς σε άλλη τριάδα ή να δοκιμάσεις άλλο παιχνίδι."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}},"10":{"title":{"present":true,"value":"Εξάσκηση με διακλαδώσεις"},"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια με διακλαδώσεις στο ίδιο παιχνίδι</b> και δες την εξήγηση μετά από κάθε σωστή απάντηση. Στον Ντεντέκτιβ χρειάζεται <b>μία αποστολή ανά μόριο</b>. Έπειτα μπορείς να συνεχίσεις στην τελική εξερεύνηση, να εξασκηθείς σε άλλη τριάδα ή να δοκιμάσεις άλλο παιχνίδι."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}},"titleLogo":{"present":false,"value":null}}};
  const LEVEL_FIELDS = {"3":{"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΤο <b>Επίπεδο 1 — Βασικό είναι υποχρεωτικό</b>. Ολοκλήρωσε σωστά <b>τρία διαφορετικά μόρια χωρίς διακλαδώσεις στο ίδιο παιχνίδι</b> και διάβασε την εξήγηση κάθε απάντησης για να συνεχίσεις τη θεωρία. Στον Ντεντέκτιβ χρειάζεται μία αποστολή ανά μόριο. Η νέα τριάδα και η αλλαγή παιχνιδιού παραμένουν διαθέσιμες για εξάσκηση."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":2,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"bb48fe6cbb689c2bad82cc15d47f53e49f4f021894183c6b228f97bf6902292f","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306","policyVersion":"alkanes-levels-v1","allowedLevels":[1],"requiredLevels":[1]},"openLabel":"Διάλεξε παιχνίδι"}}},"10":{"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΓια να ανοίξει η τελική εξερεύνηση είναι <b>υποχρεωτικά και τα δύο πρώτα επίπεδα</b>. Ολοκλήρωσε μία τριάδα στο <b>Επίπεδο 1 — Βασικό</b> και μία στο <b>Επίπεδο 2 — Ενδιάμεσο</b>, με τρία διαφορετικά σωστά μόρια στο καθένα. Κάθε τριάδα γίνεται στο ίδιο παιχνίδι, ενώ μπορείς να διαλέξεις άλλο παιχνίδι για το επόμενο επίπεδο.\n\nΤο <b>Επίπεδο 3 — Προχωρημένο είναι προαιρετικό</b> και δεν χρειάζεται για το ξεκλείδωμα. Περιλαμβάνει περισσότερες διακλαδώσεις. Διάβασε τις εξηγήσεις και διάλεξε θεωρία, άλλη τριάδα ή άλλο παιχνίδι όταν είσαι έτοιμος ή έτοιμη."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":2,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"bb48fe6cbb689c2bad82cc15d47f53e49f4f021894183c6b228f97bf6902292f","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306","policyVersion":"alkanes-levels-v1","allowedLevels":[1,2,3],"requiredLevels":[1,2]},"openLabel":"Διάλεξε παιχνίδι"}}},"11":{"note":{"present":true,"value":"Από το μενού διάλεξε οποιοδήποτε από τα <b>δεκατέσσερα αλκάνια</b>. Σύγκρινε συνεπτυγμένο, ανεπτυγμένο και σκελετικό τύπο με το 3D μοντέλο και επίλεξε τα συνθετικά του ονόματος για τις αντίστοιχες επισημάνσεις. Το μεθάνιο διαθέτει συνεπτυγμένο και ανεπτυγμένο τύπο, χωρίς σκελετικό.\n\nΧρησιμοποίησε τα εργαλεία 2D και 3D για μεγέθυνση και παρατήρηση. Περίστρεψε το 3D μοντέλο με το ποντίκι. Η συνδεσμολογία παραμένει ίδια, ενώ ο 2D τύπος δεν αποδίδει όλες τις γωνίες του μορίου στον χώρο."},"menuSubset":{"present":true,"value":["methane","ethane","propane","butane","pentane","methyl_2_pentane","dimethyl_2_3_butane","ethyl_3_dimethyl_2_5_hexane","methyl_2_butane","methyl_3_pentane","ethyl_3_pentane","dimethyl_2_2_propane","dimethyl_2_2_butane","ethyl_3_methyl_2_pentane"]}}};
  const LEVEL_PRIOR_FIELDS = {"3":{"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια χωρίς διακλαδώσεις στο ίδιο παιχνίδι</b> και δες την εξήγηση μετά από κάθε σωστή απάντηση. Στον Ντεντέκτιβ χρειάζεται <b>μία αποστολή ανά μόριο</b>. Έπειτα μπορείς να συνεχίσεις τη θεωρία, να εξασκηθείς σε άλλη τριάδα ή να δοκιμάσεις άλλο παιχνίδι."},"checkpoint":{"present":true,"value":{"id":"alkanes-unbranched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-unbranched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}}},"10":{"note":{"present":true,"value":"Διάλεξε ένα από τα τέσσερα παιχνίδια. <b>Συνεργείο ονομάτων</b> (επισκευή ονόματος), <b>Χτίσε το όνομα</b> (σύνθεση από συνθετικά), <b>Μοριακό παζλ</b> (από το όνομα στη δομή) ή <b>Μοριακός ντεντέκτιβ</b> (βρες στη δομή όσα δηλώνει το επισημασμένο συνθετικό του σωστού ονόματος).\n\nΟλοκλήρωσε σωστά <b>τρία διαφορετικά μόρια με διακλαδώσεις στο ίδιο παιχνίδι</b> και δες την εξήγηση μετά από κάθε σωστή απάντηση. Στον Ντεντέκτιβ χρειάζεται <b>μία αποστολή ανά μόριο</b>. Έπειτα μπορείς να συνεχίσεις στην τελική εξερεύνηση, να εξασκηθείς σε άλλη τριάδα ή να δοκιμάσεις άλλο παιχνίδι."},"checkpoint":{"present":true,"value":{"id":"alkanes-branched-workshop-v1","type":"alkane-game-choice-set","version":1,"round":{"version":1,"setId":"alkanes-branched","difficulty":"basic","roundCount":3,"generatorVersion":"1.0.0","catalogRevision":"275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690","engineSHA256":"3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306"},"openLabel":"Διάλεξε παιχνίδι"}}},"11":{"note":{"present":true,"value":"Από το μενού διάλεξε οποιοδήποτε από τα <b>οκτώ αλκάνια</b>. Σύγκρινε συνεπτυγμένο, ανεπτυγμένο και σκελετικό τύπο με το 3D μοντέλο και επίλεξε τα συνθετικά του ονόματος για τις αντίστοιχες επισημάνσεις. Το μεθάνιο διαθέτει συνεπτυγμένο και ανεπτυγμένο τύπο, χωρίς σκελετικό.\n\nΧρησιμοποίησε τα εργαλεία 2D και 3D για μεγέθυνση και παρατήρηση. Περίστρεψε το 3D μοντέλο με το ποντίκι. Η συνδεσμολογία παραμένει ίδια, ενώ ο 2D τύπος δεν αποδίδει όλες τις γωνίες του μορίου στον χώρο."},"menuSubset":{"present":true,"value":["methane","ethane","propane","butane","pentane","methyl_2_pentane","dimethyl_2_3_butane","ethyl_3_dimethyl_2_5_hexane"]}}};
  function same(left, right) { return JSON.stringify(left) === JSON.stringify(right); }
  function projectFields(scenario, from, to) {
    const projected = clone(scenario);
    for (const index of Object.keys(from)) {
      const step = scenario.steps[index];
      if (!step || typeof step !== "object") return null;
      for (const field of Object.keys(from[index])) {
        const expected = from[index][field];
        if (own(step, field) !== expected.present || expected.present && !same(step[field], expected.value)) return null;
        const prior = to[index][field];
        if (prior.present) projected.steps[index][field] = clone(prior.value); else delete projected.steps[index][field];
      }
    }
    return projected;
  }
  function migrateRecord(scenario, options) {
    if (!scenario || !Array.isArray(scenario.steps) || scenario.steps.length !== 12 || !options || typeof options.read !== "function") return null;
    const four = projectFields(scenario, LEVEL_FIELDS, LEVEL_PRIOR_FIELDS);
    if (four) {
      const present = options.read(four);
      if (present) {
        const states = {}, practices = {};
        for (const index of ["3", "10"]) {
          if (present.states && own(present.states, index)) states[index] = clone(present.states[index]);
          if (present.practices && own(present.practices, index)) practices[index] = clone(present.practices[index]);
        }
        return { states, practices };
      }
      return migrateRecord(four, options);
    }
    const three = projectFields(scenario, NEW_FIELDS, THREE_FIELDS);
    if (!three) return null;
    const current = options.read(three);
    const states = {}, practices = {};
    if (current) {
      // A present three-game reset also wins over an older Repair receipt.
      for (const index of Object.keys(NEW_FIELDS)) {
        if (current.states && own(current.states, index)) states[index] = clone(current.states[index]);
        if (current.practices && own(current.practices, index)) practices[index] = clone(current.practices[index]);
      }
      return { states, practices };
    }
    const older = projectFields(three, THREE_FIELDS, OLD_FIELDS);
    const old = older && options.read(older);
    if (!old || !old.states || typeof old.states !== "object") return null;
    for (const index of Object.keys(NEW_FIELDS)) {
      if (own(old.states, index)) states[index] = { version: VERSION, selected: "repair", legacyRepair: clone(old.states[index]) };
      if (old.practices && own(old.practices, index)) practices[index] = { version: VERSION, selected: "repair", legacyRepair: clone(old.practices[index]) };
    }
    return { states, practices };
  }
  global.NameleculeQuizCheckpoints.registerType("alkane-game-choice-set", Object.freeze({ validate, restore, prepare, mount: (host, options) => mountComposite(host, options, false),
    createPractice, restorePractice, mountPractice: (host, options) => mountComposite(host, options, true), otherGame, practiceGame, labels, migrateRecord }));
})(typeof window !== "undefined" ? window : globalThis);
