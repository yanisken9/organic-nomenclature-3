/* Generated lesson sets. Saved answers are rechecked against regenerated engine rounds. */
(function (global) {
  "use strict";
  const VERSION = 1;
  const ENGINE = "3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306";
  const REVISION = "275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690";
  const CATALOG_SHA = "9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724";
  const recipeKeys = ["version", "setId", "difficulty", "roundCount", "generatorVersion", "catalogRevision", "engineSHA256"];
  const levelRecipeKeys = recipeKeys.concat(["policyVersion", "allowedLevels", "requiredLevels"]);
  const prepared = new Map();
  // Optional attempts must never evict the sets used to verify earned progress.
  const practices = new Map();
  // A receipt always selects its own verified source version. The old eight
  // remain immutable; fresh standalone attempts use the separate enriched pack.
  const moduleURL = global.document && global.document.currentScript && global.document.currentScript.src;
  const CATALOGS = Object.freeze({
    legacy: Object.freeze({ id: "legacy", file: "games/data/alkane-structures.json", count: 8,
      revision: REVISION, engineSHA256: ENGINE, sha256: CATALOG_SHA,
      moleculeIds: Object.freeze(["methane", "ethane", "propane", "butane", "pentane", "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane"]) }),
    enriched: Object.freeze({ id: "enriched", file: "games/data/alkane-structures-v2.json", count: 14,
      revision: "bb48fe6cbb689c2bad82cc15d47f53e49f4f021894183c6b228f97bf6902292f", engineSHA256: ENGINE, sha256: "2c4d9a95a77291f13c4a422644aefdae7f23448c2eed7b9d2ef4913da6de92b2", moleculeIds: Object.freeze(["methane", "ethane", "propane", "butane", "pentane", "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane", "methyl_2_butane", "methyl_3_pentane", "ethyl_3_pentane", "dimethyl_2_2_propane", "dimethyl_2_2_butane", "ethyl_3_methyl_2_pentane"]) })
  });
  const sources = new Map();
  const canonicalInputs = new Map();
  function catalogDescriptor(reference) {
    if (reference === undefined || reference === null) return CATALOGS.legacy;
    const value = typeof reference === "object" ? reference.revision : reference;
    const descriptor = Object.values(CATALOGS).find(entry => entry.id === value || entry.revision === value);
    assert(descriptor, "Unsupported alkane catalog revision");
    if (reference && typeof reference === "object") {
      ["id", "file", "count", "revision", "engineSHA256", "sha256"].forEach(field => {
        if (Object.prototype.hasOwnProperty.call(reference, field)) assert(reference[field] === descriptor[field], "Catalog descriptor mismatch");
      });
    }
    return descriptor;
  }
  function catalogKey(descriptor) { return JSON.stringify([descriptor.revision, descriptor.engineSHA256, descriptor.sha256]); }
  function sourceURL(descriptor) {
    return moduleURL ? new URL("../" + descriptor.file, moduleURL).href : new URL(descriptor.file, global.document.baseURI).href;
  }
  async function sha256(bytes) {
    const digest = await global.crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  }
  function assert(condition, message) { if (!condition) throw new Error(message); }
  function cancelled() {
    const error = new Error("Η προετοιμασία ακυρώθηκε.");
    error.name = "AbortError";
    return error;
  }
  function checkSignal(signal) { if (signal && signal.aborted) throw cancelled(); }
  function levelAPI() {
    const api = global.NameleculeGameLevels;
    assert(api && api.policyVersion === "alkanes-levels-v1" && typeof api.makeContext === "function" &&
      typeof api.validateContext === "function" && typeof api.createGenerationInput === "function", "Η πολιτική επιπέδων δεν είναι διαθέσιμη.");
    return api;
  }
  function validateLevelRecipe(recipe) {
    const levels = levelAPI();
    const hasLevel = Object.prototype.hasOwnProperty.call(recipe, "level");
    const keys = hasLevel ? levelRecipeKeys.concat(["level"]) : levelRecipeKeys;
    assert(Object.keys(recipe).length === keys.length && keys.every(field => Object.prototype.hasOwnProperty.call(recipe, field)) &&
      recipe.version === 2 && ["alkanes-unbranched", "alkanes-branched"].includes(recipe.setId) &&
      recipe.difficulty === "basic" && recipe.roundCount === 3 && recipe.generatorVersion === "1.0.0" &&
      recipe.catalogRevision === CATALOGS.enriched.revision && recipe.engineSHA256 === ENGINE &&
      recipe.policyVersion === levels.policyVersion, "Unsupported level checkpoint recipe");
    const unbranched = recipe.setId === "alkanes-unbranched";
    assert(JSON.stringify(recipe.allowedLevels) === JSON.stringify(unbranched ? [1] : [1, 2, 3]) &&
      JSON.stringify(recipe.requiredLevels) === JSON.stringify(unbranched ? [1] : [1, 2]) &&
      (!hasLevel || recipe.allowedLevels.includes(recipe.level)), "Unsupported checkpoint level requirements");
    return recipe;
  }
  // The exact v1 path remains usable without loading the optional levels module.
  function validate(recipe) {
    if (recipe && typeof recipe === "object" && !Array.isArray(recipe) && recipe.version === 2) return validateLevelRecipe(recipe);
    assert(recipe && typeof recipe === "object" && !Array.isArray(recipe) &&
      Object.keys(recipe).length === recipeKeys.length && recipeKeys.every(key => Object.prototype.hasOwnProperty.call(recipe, key)) &&
      recipe.version === VERSION && ["alkanes-unbranched", "alkanes-branched"].includes(recipe.setId) &&
      recipe.difficulty === "basic" && recipe.roundCount === 3 && recipe.generatorVersion === "1.0.0" &&
      recipe.catalogRevision === REVISION && recipe.engineSHA256 === ENGINE, "Unsupported generated checkpoint recipe");
    return recipe;
  }
  function requireLevel(recipe) {
    if (recipe.version === 2) assert(Object.prototype.hasOwnProperty.call(recipe, "level") && recipe.allowedLevels.includes(recipe.level), "A selected level is required for this attempt");
  }
  function key(recipe, seed) {
    if (recipe.version === 2) {
      requireLevel(recipe);
      const levels = levelAPI();
      const context = levels.makeContext({ source: "enriched", level: recipe.level, seed });
      assert(context.seed !== null, "A valid seed is required for this attempt");
      return JSON.stringify([recipe.version, recipe.setId, recipe.difficulty, recipe.roundCount, recipe.generatorVersion,
        recipe.catalogRevision, recipe.engineSHA256, recipe.policyVersion, recipe.allowedLevels, recipe.requiredLevels,
        recipe.level, levels.contextKey(context)]);
    }
    return JSON.stringify([recipe.setId, recipe.difficulty, recipe.generatorVersion, recipe.catalogRevision, recipe.engineSHA256, seed]);
  }
  function roundRecipe(baseRecipe, value) {
    const levels = levelAPI(), context = levels.validateContext(value);
    validate(baseRecipe);
    if (context.source === "legacy") return {
      version: VERSION, setId: baseRecipe.setId, difficulty: "basic", roundCount: 3,
      generatorVersion: "1.0.0", catalogRevision: REVISION, engineSHA256: ENGINE
    };
    assert(baseRecipe.version === 2 && baseRecipe.allowedLevels.includes(context.level) &&
      (!Object.prototype.hasOwnProperty.call(baseRecipe, "level") || baseRecipe.level === context.level), "The context level is incompatible with this checkpoint");
    return validate(Object.assign({}, baseRecipe, { allowedLevels: baseRecipe.allowedLevels.slice(),
      requiredLevels: baseRecipe.requiredLevels.slice(), level: context.level }));
  }
  function seedValue(value) { return typeof value === "string" && /^[0-9]{1,20}$/.test(value) ? value : null; }
  function cleanRound(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return null;
    const result = {};
    ["selectedPartId", "selectedValue"].forEach(field => {
      if (value[field] === null || (typeof value[field] === "string" && value[field].length <= 256)) result[field] = value[field];
    });
    ["attempts", "selectionMisses"].forEach(field => {
      if (Number.isSafeInteger(value[field]) && value[field] >= 0) result[field] = value[field];
    });
    ["solved", "submitted"].forEach(field => { result[field] = value[field] === true; });
    ["order", "choiceOrder"].forEach(field => {
      if (Array.isArray(value[field]) && value[field].length <= 32 && value[field].every(entry =>
        (typeof entry === "string" && entry.length <= 128) || Number.isSafeInteger(entry))) result[field] = value[field].slice();
    });
    return result;
  }
  function restoreFromCache(recipe, previous, cache) {
    validate(recipe);
    const seed = previous && previous.version === VERSION && seedValue(previous.seed);
    if (!seed) return { version: VERSION, seed: null, currentRound: 0, states: [null, null, null], solved: false };
    const raw = Array.isArray(previous.states) && previous.states.length === 3 ? previous.states.map(cleanRound) : [null, null, null];
    const cacheKey = key(recipe, seed);
    let set = cache.get(cacheKey);
    // Cached rounds are an optimization, never proof of earned access. Once a
    // source has passed its byte/engine checks, deterministically reconstruct
    // a required receipt even if an old round was evicted from the small cache.
    if (!set && cache === prepared) {
      const descriptor = catalogDescriptor(recipe.catalogRevision);
      const input = canonicalInputs.get(catalogKey(descriptor));
      if (input) {
        set = buildSet(recipe, seed, input);
        rememberSet(cache, cacheKey, set, 32);
      }
    }
    let states = raw;
    let currentRound = Number.isInteger(previous.currentRound) && previous.currentRound >= 0 && previous.currentRound < 3 ? previous.currentRound : 0;
    let solved = false;
    if (set) {
      const engine = global.NameleculeRepairEngine;
      states = set.rounds.map((round, index) => engine.restoreRoundState(round, raw[index]));
      const first = states.findIndex(state => !state.solved);
      if (first >= 0) {
        currentRound = Math.min(currentRound, first);
        // A malformed receipt cannot pre-complete later repairs out of sequence.
        for (let index = first + 1; index < 3; index++) states[index] = engine.restoreRoundState(set.rounds[index], null);
      } else { currentRound = Math.min(currentRound, 2); solved = true; }
    }
    return { version: VERSION, seed, currentRound, states, solved };
  }
  function restore(recipe, previous) { return restoreFromCache(recipe, previous, prepared); }
  function restorePractice(recipe, previous) { return restoreFromCache(recipe, previous, practices); }
  function freshSeed(previousSeed) {
    const values = new Uint32Array(2);
    global.crypto.getRandomValues(values);
    const seed = String(values[0]) + String(values[1]);
    // Even repeated random bytes must start a different immediate attempt.
    return seed === previousSeed ? seed.slice(0, -1) + ((Number(seed.slice(-1)) + 1) % 10) : seed;
  }
  function createPractice(recipe, previous) {
    validate(recipe);
    requireLevel(recipe);
    return { version: VERSION, seed: freshSeed(seedValue(previous && previous.seed)),
      currentRound: 0, states: [null, null, null], solved: false };
  }
  async function loadSource(signal, descriptor) {
    checkSignal(signal);
    const cacheKey = catalogKey(descriptor);
    if (sources.has(cacheKey)) return sources.get(cacheKey);
    assert(global.NameleculeChemistryClient && global.NameleculeRepairGenerator &&
      global.NameleculeRepairGenerator.version === "1.0.0", "Η μηχανή του Συνεργείου δεν είναι διαθέσιμη.");
    const response = await global.fetch(sourceURL(descriptor),
      { cache: "no-cache", signal });
    assert(response.ok, "Οι δομές των αλκανίων δεν φορτώθηκαν.");
    const bytes = await response.arrayBuffer();
    checkSignal(signal);
    const actual = await sha256(bytes);
    assert(actual === descriptor.sha256, "Οι δομές του Συνεργείου άλλαξαν. Ανανέωσε το μάθημα.");
    const catalog = JSON.parse(new TextDecoder().decode(bytes));
    assert(catalog && catalog.schemaVersion === 1 && catalog.revision === descriptor.revision && catalog.engineSHA256 === descriptor.engineSHA256 &&
      (descriptor.id === "legacy" ? catalog.catalogVersion === undefined : catalog.catalogVersion === 2) &&
      Array.isArray(catalog.molecules) && catalog.molecules.length === descriptor.count &&
      JSON.stringify(catalog.molecules.map(entry => entry && entry.id)) === JSON.stringify(descriptor.moleculeIds), "Η έκδοση των δομών δεν συμφωνεί με το μάθημα.");
    for (const molecule of catalog.molecules) {
      checkSignal(signal);
      assert(molecule && typeof molecule.mol === "string" && typeof molecule.sourceSHA256 === "string" &&
        await sha256(new TextEncoder().encode(molecule.mol)) === molecule.sourceSHA256, "Η πηγή του μορίου δεν επαληθεύτηκε.");
    }
    const analyses = [];
    for (let index = 0; index < catalog.molecules.length; index += 3) {
      checkSignal(signal);
      const batch = await Promise.all(catalog.molecules.slice(index, index + 3).map(molecule =>
        global.NameleculeChemistryClient.analyze(molecule, { signal, engineSHA256: descriptor.engineSHA256 })));
      analyses.push.apply(analyses, batch);
    }
    checkSignal(signal);
    return { catalog, analyses };
  }
  function freeze(value) {
    if (value && typeof value === "object" && !Object.isFrozen(value)) {
      Object.keys(value).forEach(key => freeze(value[key]));
      Object.freeze(value);
    }
    return value;
  }
  async function loadCanonicalInput(signal, reference) {
    checkSignal(signal);
    const descriptor = catalogDescriptor(reference), inputKey = catalogKey(descriptor);
    if (canonicalInputs.has(inputKey)) return canonicalInputs.get(inputKey);
    const controller = new AbortController();
    let timedOut = false;
    let rejectAbort;
    // Reject independently of fetch/Worker cooperation: an ignored signal must
    // still leave both mounting and cold receipt preparation with a retry path.
    const aborted = new Promise((_, reject) => { rejectAbort = reject; });
    const onAbort = () => rejectAbort(timedOut ? new Error("Η προετοιμασία άργησε. Δοκίμασε ξανά.") : cancelled());
    const abort = () => controller.abort();
    controller.signal.addEventListener("abort", onAbort, { once: true });
    if (signal) signal.addEventListener("abort", abort, { once: true });
    const timer = global.setTimeout(() => { timedOut = true; abort(); }, 45000);
    try {
      const loading = (async () => {
        const input = await loadSource(controller.signal, descriptor);
        checkSignal(controller.signal);
        // The pinned generator validates names, all twelve parts, vocabulary and
        // the numbered parent/branch graph against each unchanged source MOL.
        global.NameleculeRepairEngine.validateGameData(global.NameleculeRepairGenerator.createGame(
          input.catalog, input.analyses, { seed: "0", difficulty: "basic" }));
        checkSignal(controller.signal);
        const verified = freeze(input);
        // Commit caches only while this request is still live. A late response
        // from a transport ignoring abort cannot populate either cache.
        checkSignal(controller.signal);
        sources.set(inputKey, verified);
        canonicalInputs.set(inputKey, verified);
        return verified;
      })();
      return await Promise.race([loading, aborted]);
    } catch (error) {
      controller.abort();
      throw error;
    } finally {
      global.clearTimeout(timer);
      controller.signal.removeEventListener("abort", onAbort);
      if (signal) signal.removeEventListener("abort", abort);
    }
  }
  function rememberSet(cache, cacheKey, set, limit) {
    if (!cache.has(cacheKey) && cache.size >= limit) cache.delete(cache.keys().next().value);
    cache.set(cacheKey, set);
  }
  function buildSet(recipe, seed, canonicalInput) {
    const input = recipe.version === 2 ? levelAPI().createGenerationInput(canonicalInput, recipe.level) : canonicalInput;
    const game = global.NameleculeRepairEngine.validateGameData(global.NameleculeRepairGenerator.createGame(input.catalog, input.analyses,
      { seed, difficulty: recipe.difficulty }));
    const setId = recipe.version === 2 ? (recipe.level === 1 ? "alkanes-unbranched" : "alkanes-branched") : recipe.setId;
    const set = game.sets.find(entry => entry.id === setId);
    assert(set && set.rounds.length === 3, "Repair set unavailable");
    return set;
  }
  async function generate(recipe, seed, signal, cache, limit) {
    validate(recipe);
    checkSignal(signal);
    const cacheKey = key(recipe, seed);
    if (cache.has(cacheKey)) return cache.get(cacheKey);
    const controller = new AbortController();
    const abort = () => controller.abort();
    if (signal) signal.addEventListener("abort", abort, { once: true });
    const timer = global.setTimeout(abort, 45000);
    try {
      const canonicalInput = await loadCanonicalInput(controller.signal, recipe.catalogRevision);
      checkSignal(signal);
      checkSignal(controller.signal);
      const set = buildSet(recipe, seed, canonicalInput);
      rememberSet(cache, cacheKey, set, limit);
      return set;
    } catch (error) {
      controller.abort();
      if (signal && signal.aborted) throw cancelled();
      if (controller.signal.aborted && error.name === "AbortError") throw new Error("Η προετοιμασία άργησε. Δοκίμασε ξανά.");
      throw error;
    } finally {
      global.clearTimeout(timer);
      if (signal) signal.removeEventListener("abort", abort);
    }
  }
  function prepare(recipe, previous, options) {
    const state = restore(recipe, previous);
    if (!state.seed || prepared.has(key(recipe, state.seed))) return null;
    return generate(recipe, state.seed, options && options.signal, prepared, 32).then(() => restore(recipe, state));
  }
  function preparePractice(recipe, previous, options) {
    const state = restorePractice(recipe, previous);
    if (!state.seed || practices.has(key(recipe, state.seed))) return null;
    return generate(recipe, state.seed, options && options.signal, practices, 2).then(() => restorePractice(recipe, state));
  }
  function node(tag, className, text) {
    const element = global.document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
  }
  function mountSet(host, options, practice) {
    const recipe = validate(options.round);
    requireLevel(recipe);
    const restoreState = practice ? restorePractice : restore;
    const cache = practice ? practices : prepared;
    const controller = new AbortController();
    let state = restoreState(recipe, options.initialState);
    let destroyed = false;
    let current = null;
    let token = 0;
    if (!state.seed) state.seed = freshSeed(null);
    function publish() {
      state = restoreState(recipe, state);
      if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(JSON.parse(JSON.stringify(state)));
    }
    function reportProgress(value) {
      if (!destroyed && typeof options.onProgress === "function") options.onProgress(value);
    }
    function destroyRound() { if (current) current.destroy(); current = null; }
    function render(set) {
      if (destroyed) return;
      destroyRound();
      const index = state.currentRound;
      const headerProgress = typeof options.onProgress === "function";
      const progress = node("p", "nl-quiz-set-progress", headerProgress ? set.title : "Κουίζ " + (index + 1) + " από 3 · " + set.title);
      if (!headerProgress) progress.setAttribute("role", "status");
      const roundHost = node("div", "nl-quiz-set-round");
      host.replaceChildren(progress, roundHost);
      host.setAttribute("aria-busy", "false");
      const presentation = global.NameleculeRepairGame.presentationForRound(set.rounds[index], { difficulty: recipe.difficulty });
      const roundOptions = Object.assign({}, presentation, {
        initialState: state.states[index], assetBase: options.assetBase,
        onSuccessActionsReady(ready) {
          if (!destroyed && state.currentRound === index && roundHost.isConnected &&
            typeof options.onSuccessActionsReady === "function") {
            options.onSuccessActionsReady(index === 2 && state.solved && ready === true);
          }
        },
        onReveal(request) {
          if (!destroyed && state.currentRound === index && roundHost.isConnected &&
            typeof options.onReveal === "function") options.onReveal(request);
        },
        onStateChange(roundState) {
          if (destroyed) return;
          state.states[index] = roundState;
          publish();
        },
        onSolved(result, roundState) {
          if (destroyed || !result || result.kind !== "correct") return;
          state.states[index] = roundState;
          publish();
          if (state.solved && typeof options.onSolved === "function") options.onSolved(result, JSON.parse(JSON.stringify(state)));
        },
        onContinue() {
          if (destroyed || !state.states[index] || !state.states[index].solved) return;
          if (index < 2) {
            state.currentRound = index + 1;
            publish();
            render(set);
            const heading = roundHost.querySelector("h1,h2,h3");
            if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
          } else if (state.solved && typeof options.onContinue === "function") options.onContinue();
        }
      });
      // The round reads this when creating its success footer, after publishing
      // the newly solved state. Hosts can therefore label aggregate level gates
      // from their current receipts without changing the legacy round renderer.
      Object.defineProperty(roundOptions, "continueLabel", { enumerable: true, get() {
        if (index < 2) return "Επόμενο κουίζ";
        const label = typeof options.continueLabel === "function" ? options.continueLabel() : options.continueLabel;
        return typeof label === "string" && label.trim() ? label : "Συνεχίζω τη θεωρία";
      } });
      if (index === 2 && typeof options.onNewPractice === "function") {
        roundOptions.newPracticeLabel = options.newPracticeLabel;
        roundOptions.onNewPractice = function () {
          if (!destroyed && state.currentRound === index && state.solved && roundHost.isConnected) options.onNewPractice();
        };
      }
      if (index === 2 && typeof options.onOtherGame === "function") {
        roundOptions.otherGameLabel = options.otherGameLabel;
        roundOptions.onOtherGame = function () {
          if (!destroyed && state.currentRound === index && state.solved && roundHost.isConnected) options.onOtherGame();
        };
      }
      current = global.NameleculeRepairGame.mountRound(roundHost, roundOptions);
      reportProgress({ current: index + 1, total: recipe.roundCount });
    }
    function start() {
      const request = ++token;
      destroyRound();
      reportProgress(null);
      host.setAttribute("aria-busy", "true");
      const loading = node("p", "nl-quiz-loading", "Η μηχανή ετοιμάζει τις τρεις επισκευές…");
      loading.setAttribute("role", "status");
      host.replaceChildren(loading);
      publish(); // Record the seed before any asynchronous work or refresh.
      generate(recipe, state.seed, controller.signal, cache, practice ? 2 : 32).then(set => {
        if (destroyed || request !== token) return;
        state = restoreState(recipe, state);
        publish();
        render(set);
      }).catch(error => {
        if (destroyed || request !== token || controller.signal.aborted) return;
        reportProgress(null);
        host.setAttribute("aria-busy", "false");
        const message = node("p", "nl-quiz-error", "Οι επισκευές δεν φορτώθηκαν. Δοκίμασε ξανά ή επέστρεψε στη θεωρία.");
        message.setAttribute("role", "alert");
        const retry = node("button", "nl-quiz-button", "Δοκίμασε ξανά");
        retry.type = "button";
        retry.addEventListener("click", start);
        host.replaceChildren(message, retry);
      });
    }
    start();
    return { destroy() {
      if (destroyed) return;
      reportProgress(null);
      destroyed = true;
      token++;
      controller.abort();
      destroyRound();
      host.removeAttribute("aria-busy");
      host.replaceChildren();
    } };
  }
  function mount(host, options) { return mountSet(host, options, false); }
  function mountPractice(host, options) { return mountSet(host, options, true); }
  const adapter = Object.freeze({ validate, restore, prepare, preparePractice, mount, createPractice, restorePractice, mountPractice });
  global.NameleculeGeneratedRepairCheckpoint = Object.freeze({ adapter, loadCanonicalInput, catalogDescriptor, freshSeed, roundRecipe });
  if (global.NameleculeQuizCheckpoints) global.NameleculeQuizCheckpoints.registerType("generated-name-repair-set", adapter);
})(typeof window !== "undefined" ? window : globalThis);
