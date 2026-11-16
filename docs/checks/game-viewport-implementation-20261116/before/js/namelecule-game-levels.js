/* Shared, audited alkane levels. Hosts own lesson gates and attempt history. */
(function (global) {
  "use strict";

  const POLICY = "alkanes-levels-v1";
  const SOURCE_REVISION = "bb48fe6cbb689c2bad82cc15d47f53e49f4f021894183c6b228f97bf6902292f";
  const SOURCE_SHA256 = "2c4d9a95a77291f13c4a422644aefdae7f23448c2eed7b9d2ef4913da6de92b2";
  const ENGINE = "3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306";
  const BANDS = Object.freeze({
    1: Object.freeze(["methane", "ethane", "propane", "butane", "pentane"]),
    2: Object.freeze(["methyl_2_butane", "methyl_2_pentane", "methyl_3_pentane", "ethyl_3_pentane"]),
    3: Object.freeze(["dimethyl_2_2_propane", "dimethyl_2_2_butane", "dimethyl_2_3_butane", "ethyl_3_methyl_2_pentane", "ethyl_3_dimethyl_2_5_hexane"])
  });
  const LABELS = Object.freeze({ 1: "Επίπεδο 1 — Βασικό", 2: "Επίπεδο 2 — Ενδιάμεσο", 3: "Επίπεδο 3 — Προχωρημένο" });
  const DESCRIPTIONS = Object.freeze({ 1: "Χωρίς αλκυλομάδες", 2: "Μία αλκυλομάδα", 3: "Δύο ή περισσότερες αλκυλομάδες" });
  const ALL_IDS = [].concat(BANDS[1], BANDS[2], BANDS[3]);
  const LEGACY_IDS = Object.freeze(["methane", "ethane", "propane", "butane", "pentane", "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane"]);
  const CONTEXT_KEYS = Object.freeze(["version", "source", "catalogRevision", "catalogSHA256", "engineSHA256", "generatorVersion", "policyVersion", "level", "seed"]);
  const CONTEXT_SOURCES = Object.freeze({
    legacy: Object.freeze({ revision: "275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690",
      sha256: "9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724", policyVersion: "legacy-8-v1" }),
    enriched: Object.freeze({ revision: SOURCE_REVISION, sha256: SOURCE_SHA256, policyVersion: POLICY })
  });
  const LEVEL_BY_ID = Object.create(null);
  ALL_IDS.forEach(function (id) { LEVEL_BY_ID[id] = [1, 2, 3].find(function (level) { return BANDS[level].includes(id); }); });

  function assert(condition, message) { if (!condition) throw new Error("Game levels: " + message); }
  function validLevel(level) { assert(level === 1 || level === 2 || level === 3, "Invalid level"); return level; }
  function validId(id) { return typeof id === "string" && /^[a-zA-Z0-9_-]+$/.test(id); }
  function checkedIds(ids, allowEmpty) {
    assert(Array.isArray(ids) && (allowEmpty || ids.length > 0), "Expected a nonempty ID array");
    assert(ids.every(validId) && new Set(ids).size === ids.length, "Invalid or duplicate IDs");
    return ids.slice();
  }
  function label(level) { return LABELS[validLevel(level)]; }
  function levelFor(id) { return typeof id === "string" && Object.prototype.hasOwnProperty.call(LEVEL_BY_ID, id) ? LEVEL_BY_ID[id] : null; }
  function poolFor(level, availableIds) {
    const band = BANDS[validLevel(level)];
    if (availableIds === undefined) return band.slice();
    const available = new Set(checkedIds(availableIds, true));
    return band.filter(function (id) { return available.has(id); });
  }

  // Descriptor identity is metadata, not proof of source-byte/chemistry checks.
  function makeContext(options) {
    assert(options && typeof options === "object" && !Array.isArray(options) &&
      Object.keys(options).every(function (key) { return ["source", "level", "seed"].includes(key); }), "Invalid context options");
    assert(options.source === "legacy" || options.source === "enriched", "Unknown context source");
    const source = CONTEXT_SOURCES[options.source];
    const level = options.level === undefined ? null : options.level;
    if (options.source === "legacy") assert(level === null, "Legacy context has no structural level");
    else validLevel(level);
    const seed = options.seed === undefined ? null : options.seed;
    assert(seed === null || (typeof seed === "string" && /^[0-9]{1,20}$/.test(seed)), "Invalid context seed");
    return { version: 1, source: options.source, catalogRevision: source.revision, catalogSHA256: source.sha256,
      engineSHA256: ENGINE, generatorVersion: "1.0.0", policyVersion: source.policyVersion, level: level, seed: seed };
  }
  function validateContext(value) {
    assert(value && typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === CONTEXT_KEYS.length &&
      CONTEXT_KEYS.every(function (key) { return Object.prototype.hasOwnProperty.call(value, key); }), "Invalid context fields");
    const normalized = makeContext({ source: value.source, level: value.level, seed: value.seed });
    assert(CONTEXT_KEYS.every(function (key) { return value[key] === normalized[key]; }), "Unsupported or mismatched context");
    return normalized;
  }
  function contextKey(value) { return JSON.stringify(validateContext(value)); }
  function contextIds(value) {
    const context = validateContext(value);
    return context.source === "legacy" ? LEGACY_IDS.slice() : poolFor(context.level);
  }

  function hash(value) {
    let result = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      result ^= value.charCodeAt(index);
      result = Math.imul(result, 16777619);
    }
    return result >>> 0;
  }
  function randomSource(seed) {
    let state = hash(seed);
    return function () {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }
  function normalizeSeed(seed) {
    if (seed === undefined) return "0";
    assert((typeof seed === "string" && seed.length > 0 && seed.length <= 128) ||
      (Number.isSafeInteger(seed) && seed >= 0), "Invalid deck seed");
    return String(seed);
  }
  // Single-round games use this bag. A Workshop/lesson triple has its own seed
  // and must not consume or infer any cross-triple exhaustion history here.
  function createDeck(ids, options) {
    const values = checkedIds(ids, false);
    options = options === undefined ? {} : options;
    assert(options && typeof options === "object" && !Array.isArray(options), "Invalid deck options");
    assert(options.avoid === undefined || options.avoid === null || validId(options.avoid), "Invalid avoided ID");
    const random = randomSource(JSON.stringify([POLICY, values, normalizeSeed(options.seed)]));
    let previous = options.avoid || null, bag = [], position = 0;
    function refill() {
      bag = values.slice();
      for (let index = bag.length - 1; index > 0; index -= 1) {
        const destination = Math.floor(random() * (index + 1));
        const value = bag[index]; bag[index] = bag[destination]; bag[destination] = value;
      }
      if (bag.length > 1 && bag[0] === previous) {
        const destination = 1 + Math.floor(random() * (bag.length - 1));
        const value = bag[0]; bag[0] = bag[destination]; bag[destination] = value;
      }
      position = 0;
    }
    return Object.freeze({ next: function () {
      if (position === bag.length) refill();
      previous = bag[position++];
      return previous;
    } });
  }

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function checkedAnalyses(analyses) {
    const list = Array.isArray(analyses) ? analyses : analyses && typeof analyses === "object" ? Object.keys(analyses).map(function (id) {
      const analysis = analyses[id];
      assert(analysis && analysis.moleculeId === id, "Mismatched analysis key");
      return analysis;
    }) : null;
    assert(list && list.length === ALL_IDS.length, "Expected full14 analyses");
    const ids = checkedIds(list.map(function (analysis) { return analysis && analysis.moleculeId; }), false);
    assert(ids.every(function (id) { return levelFor(id) !== null; }), "Unknown full14 analysis");
    assert(list.every(function (analysis) { return analysis.engineSHA256 === undefined || analysis.engineSHA256 === ENGINE; }), "Analysis engine mismatch");
  }
  // The caller must verify the full source bytes and chemistry before this pure
  // projection. Source SHA identifies those full bytes, never this derived view.
  function createGenerationInput(input, level) {
    validLevel(level);
    const catalog = input && input.catalog;
    assert(catalog && catalog.schemaVersion === 1 && catalog.catalogVersion === 2 &&
      catalog.revision === SOURCE_REVISION && catalog.engineSHA256 === ENGINE, "Expected verified full14 source catalog");
    const ids = checkedIds(Array.isArray(catalog.molecules) ? catalog.molecules.map(function (molecule) { return molecule && molecule.id; }) : null, false);
    assert(ids.length === ALL_IDS.length && ids.every(function (id) { return levelFor(id) !== null; }), "Expected exactly the audited14 molecules");
    assert(input.sourceRevision === undefined || input.sourceRevision === SOURCE_REVISION, "Source revision mismatch");
    assert(input.sourceSHA256 === undefined || input.sourceSHA256 === SOURCE_SHA256, "Source SHA mismatch");
    checkedAnalyses(input.analyses);
    const view = clone(input);
    // Keep both legacy set groups viable for the unchanged RepairGenerator.
    const eligible = new Set(level === 1 ? ALL_IDS : BANDS[1].concat(BANDS[level]));
    view.catalog.molecules = view.catalog.molecules.filter(function (molecule) { return eligible.has(molecule.id); });
    if (Array.isArray(view.analyses)) view.analyses = view.analyses.filter(function (analysis) { return eligible.has(analysis.moleculeId); });
    else Object.keys(view.analyses).forEach(function (id) { if (!eligible.has(id)) delete view.analyses[id]; });
    const metadata = { policyVersion: POLICY, level: level, sourceRevision: SOURCE_REVISION,
      sourceSHA256: SOURCE_SHA256, viewRevision: SOURCE_REVISION + ":" + POLICY + ":level-" + level };
    Object.keys(metadata).forEach(function (key) { view[key] = metadata[key]; });
    view.catalog.revision = metadata.viewRevision;
    view.catalog.gameLevels = clone(metadata);
    return view;
  }

  function checkedLevels(levels) {
    assert(Array.isArray(levels) && new Set(levels).size === levels.length, "Invalid allowed levels");
    levels.forEach(validLevel);
    return levels.slice();
  }
  function checkedState(options) {
    assert(options && typeof options === "object" && !Array.isArray(options), "Invalid controls options");
    const availableIds = options.availableIds === undefined ? ALL_IDS.slice() : checkedIds(options.availableIds, true);
    const allowedLevels = options.allowedLevels === undefined ? [1, 2, 3] : checkedLevels(options.allowedLevels);
    const category = options.category === undefined ? "alkanes" : options.category;
    assert(category === "alkanes" || category === "other", "Invalid category");
    const otherCount = options.otherCount === undefined ? 0 : options.otherCount;
    assert(Number.isSafeInteger(otherCount) && otherCount >= 0, "Invalid other molecule count");
    assert(options.onSelect === undefined || typeof options.onSelect === "function", "Invalid selection handler");
    let selectedLevel = options.selectedLevel === undefined ? null : options.selectedLevel;
    if (selectedLevel !== null) validLevel(selectedLevel);
    if (!allowedLevels.includes(selectedLevel) || (selectedLevel !== null && !poolFor(selectedLevel, availableIds).length)) selectedLevel = null;
    const completedLevels = options.completedLevels === undefined ? [] : checkedLevels(options.completedLevels);
    let requirements = null;
    if (options.requirements !== undefined && options.requirements !== null) {
      assert(typeof options.requirements === "object" && !Array.isArray(options.requirements), "Invalid level requirements");
      requirements = {};
      Object.keys(options.requirements).forEach(function (key) {
        assert(["1", "2", "3"].includes(key) && ["required", "optional"].includes(options.requirements[key]), "Invalid level requirement");
        requirements[key] = options.requirements[key];
      });
    }
    return { availableIds: availableIds, allowedLevels: allowedLevels, selectedLevel: selectedLevel,
      category: category === "other" && !otherCount ? "alkanes" : category, otherCount: otherCount,
      onSelect: options.onSelect, requirements: requirements, completedLevels: completedLevels };
  }

  function mount(host, options) {
    assert(host && typeof host.appendChild === "function" && host.ownerDocument, "Invalid controls host");
    let state = checkedState(options || {}), destroyed = false;
    const doc = host.ownerDocument;
    function node(tag, className, text) {
      const result = doc.createElement(tag);
      if (className) result.className = className;
      if (text !== undefined) result.textContent = text;
      return result;
    }
    const root = node("section", "nl-game-levels");
    root.setAttribute("aria-label", "Επίπεδα παιχνιδιού");
    const categories = node("div", "nl-game-levels__categories");
    categories.setAttribute("role", "group"); categories.setAttribute("aria-label", "Κατηγορία ενώσεων");
    const alkaneButton = node("button", "nl-game-levels__category", "Αλκάνια");
    const otherButton = node("button", "nl-game-levels__category");
    [alkaneButton, otherButton].forEach(function (button) { button.type = "button"; categories.appendChild(button); });
    const title = node("p", "nl-game-levels__heading", "Επίλεξε επίπεδο");
    const levels = node("div", "nl-game-levels__buttons");
    levels.setAttribute("role", "group"); levels.setAttribute("aria-label", "Επίλεξε επίπεδο");
    const levelButtons = {};
    [1, 2, 3].forEach(function (level) {
      const button = node("button", "nl-game-levels__button"); button.type = "button";
      button.setAttribute("data-level", String(level));
      const name = node("span", "nl-game-levels__name", label(level));
      const detail = node("span", "nl-game-levels__description", DESCRIPTIONS[level]);
      const count = node("span", "nl-game-levels__count");
      const status = node("span", "nl-game-levels__status");
      [name, detail, count, status].forEach(function (child) { button.appendChild(child); });
      button.addEventListener("click", function () { select("alkanes", level); });
      levelButtons[level] = { button: button, count: count, status: status };
      levels.appendChild(button);
    });
    const note = node("p", "nl-game-levels__note"); note.setAttribute("aria-live", "polite");
    [categories, title, levels, note].forEach(function (child) { root.appendChild(child); });
    host.appendChild(root);
    function select(category, level) {
      if (destroyed) return;
      if (category === "other" && !state.otherCount) return;
      if (level !== null && (!state.allowedLevels.includes(level) || !poolFor(level, state.availableIds).length)) return;
      state = checkedState(Object.assign({}, state, { category: category, selectedLevel: level }));
      render();
      if (state.onSelect) state.onSelect({ category: state.category, level: state.selectedLevel });
    }
    alkaneButton.addEventListener("click", function () { select("alkanes", state.selectedLevel); });
    otherButton.addEventListener("click", function () { select("other", null); });
    function render() {
      categories.hidden = !state.otherCount;
      alkaneButton.setAttribute("aria-pressed", String(state.category === "alkanes"));
      otherButton.setAttribute("aria-pressed", String(state.category === "other"));
      otherButton.textContent = "Άλλες διαθέσιμες ενώσεις — χωρίς επίπεδα ακόμη (" + state.otherCount + ")";
      title.hidden = levels.hidden = state.category !== "alkanes";
      [1, 2, 3].forEach(function (level) {
        const entry = levelButtons[level], count = poolFor(level, state.availableIds).length;
        entry.button.hidden = !state.allowedLevels.includes(level);
        entry.button.disabled = !count;
        entry.button.setAttribute("aria-pressed", String(state.category === "alkanes" && state.selectedLevel === level));
        entry.count.textContent = count === 1 ? "1 διαθέσιμο μόριο" : count + " διαθέσιμα μόρια";
        const requirement = state.requirements && state.requirements[level];
        const statuses = [];
        if (requirement) statuses.push(requirement === "required" ? "Υποχρεωτικό" : "Προαιρετικό");
        if (state.completedLevels.includes(level)) statuses.push("Ολοκληρώθηκε");
        entry.status.hidden = !statuses.length;
        entry.status.textContent = statuses.join(" · ");
      });
      if (state.category === "other") note.textContent = "Η εφαρμογή αναθέτει αυτόματα μία από τις άλλες διαθέσιμες ενώσεις.";
      else if (state.selectedLevel === null) note.textContent = state.allowedLevels.some(function (level) { return poolFor(level, state.availableIds).length; }) ?
        "Επίλεξε επίπεδο για αυτόματη ανάθεση μορίου." : "Δεν υπάρχουν διαθέσιμα μόρια για αυτά τα επίπεδα.";
      else note.textContent = label(state.selectedLevel) + " · Αυτόματη ανάθεση μορίου.";
    }
    render();
    return Object.freeze({
      set: function (patch) {
        assert(!destroyed, "Controls were destroyed");
        assert(patch && typeof patch === "object" && !Array.isArray(patch), "Invalid controls patch");
        state = checkedState(Object.assign({}, state, patch)); render();
      },
      destroy: function () { if (!destroyed) { destroyed = true; if (root.parentNode) root.parentNode.removeChild(root); } }
    });
  }

  const api = Object.freeze({ policyVersion: POLICY, label: label, levelFor: levelFor, poolFor: poolFor,
    createDeck: createDeck, createGenerationInput: createGenerationInput, mount: mount,
    makeContext: makeContext, validateContext: validateContext, contextKey: contextKey, contextIds: contextIds });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.NameleculeGameLevels = api;
}(typeof globalThis !== "undefined" ? globalThis : this));
