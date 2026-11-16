/* A verified, seeded three-molecule Detective attempt inside a lesson gate. */
(function (global) {
  "use strict";
  const VERSION = 1, CHANNEL = "namelecule-detective-lesson-v1";
  const required = new Map(), optional = new Map();
  const clone = value => JSON.parse(JSON.stringify(value));
  const engine = () => global.NameleculeMolecularDetectiveEngine;
  const validSeed = value => typeof value === "string" && /^[0-9]{1,20}$/.test(value);
  function assert(ok, message) { if (!ok) throw new Error(message); }
  function contextToken(value) {
    let result = 2166136261;
    for (let index = 0; index < value.length; index++) result = Math.imul(result ^ value.charCodeAt(index), 16777619);
    return (result >>> 0).toString(36);
  }
  function levelContext(recipe, seed) {
    const levels = global.NameleculeGameLevels, provider = global.NameleculeGeneratedRepairCheckpoint;
    assert(levels && provider && provider.adapter, "Detective level policy unavailable");
    provider.adapter.validate(recipe);
    assert(recipe.version === 2 && recipe.allowedLevels.includes(recipe.level), "A selected Detective level is required");
    return levels.makeContext({ source: "enriched", level: recipe.level, seed });
  }
  function checkLevelInput(recipe, input) {
    const descriptor = global.NameleculeGeneratedRepairCheckpoint.catalogDescriptor(recipe.catalogRevision);
    assert(input.catalog.catalogVersion === 2 && Array.isArray(input.catalog.molecules) && Array.isArray(input.analyses) &&
      JSON.stringify(input.catalog.molecules.map(molecule => molecule && molecule.id)) === JSON.stringify(descriptor.moleculeIds) &&
      JSON.stringify(input.analyses.map(analysis => analysis && analysis.moleculeId)) === JSON.stringify(descriptor.moleculeIds) &&
      input.analyses.every(analysis => analysis.engineSHA256 === descriptor.engineSHA256), "Detective full14 source identity mismatch");
  }
  function shuffle(values, seed) {
    let state = 2166136261;
    for (let i = 0; i < seed.length; i++) state = Math.imul(state ^ seed.charCodeAt(i), 16777619);
    const out = values.slice();
    for (let i = out.length - 1; i > 0; i--) {
      state = (state + 0x6d2b79f5) | 0;
      let n = Math.imul(state ^ (state >>> 15), state | 1);
      n ^= n + Math.imul(n ^ (n >>> 7), n | 61);
      const j = Math.floor((((n ^ (n >>> 14)) >>> 0) / 4294967296) * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }
  function getSet(recipe, seed, input, practice) {
    assert(validSeed(seed) && input && engine(), "Detective canonical input unavailable");
    assert(input.catalog.revision === recipe.catalogRevision && input.catalog.engineSHA256 === recipe.engineSHA256,
      "Detective catalog does not match the required recipe");
    const context = recipe.version === 2 ? levelContext(recipe, seed) : null;
    if (context) checkLevelInput(recipe, input);
    const cache = practice ? optional : required;
    const key = context ? JSON.stringify([recipe, global.NameleculeGameLevels.contextKey(context), input.catalog.revision, input.catalog.engineSHA256]) :
      JSON.stringify([recipe.setId, recipe.catalogRevision, recipe.engineSHA256, seed]);
    if (cache.has(key)) return cache.get(key);
    const branched = recipe.setId === "alkanes-branched";
    const eligible = input.analyses.filter(a => recipe.version === 2
      ? global.NameleculeGameLevels.poolFor(recipe.level).includes(a.moleculeId)
      : (a.branches.length > 0) === branched);
    const chosen = shuffle(eligible, JSON.stringify(["detective-v1", recipe.setId, recipe.catalogRevision, seed])).slice(0, 3);
    assert(chosen.length === 3 && new Set(chosen.map(a => a.moleculeId)).size === 3, "Three distinct Detective molecules unavailable");
    const used = new Map();
    const rounds = chosen.map((analysis, index) => {
      const molecule = input.catalog.molecules.find(m => m.id === analysis.moleculeId);
      assert(molecule, "Missing Detective molecule");
      const snapshot = engine().canonicalSnapshot(molecule, analysis);
      const available = engine().missions(snapshot).filter(m => recipe.version !== 2 || recipe.level === 1 || m.family !== "single-bonds");
      const missions = shuffle(available, JSON.stringify([recipe.version === 2 ? "mission-levels-v1" : "mission-v1", seed, index, analysis.moleculeId]));
      const minimum = Math.min(...missions.map(m => used.get(m.family) || 0));
      const mission = missions.find(m => (used.get(m.family) || 0) === minimum);
      assert(mission && mission.accepted.length && mission.accepted.every(set => set.length), "Empty Detective mission");
      used.set(mission.family, (used.get(mission.family) || 0) + 1);
      return { snapshot, mission };
    });
    const set = { rounds };
    if (cache.size >= (practice ? 2 : 32)) cache.delete(cache.keys().next().value);
    cache.set(key, set);
    return set;
  }
  function blank() { return { atoms: [], bonds: [], attempts: 0, submitted: false, solved: false }; }
  function snapshot(entry, raw) {
    const out = blank();
    if (!raw || typeof raw !== "object" || !Array.isArray(raw.atoms) || !Array.isArray(raw.bonds) ||
        raw.atoms.length > 40 || raw.bonds.length > 39 ||
        [raw.atoms, raw.bonds].some(ids => ids.some(id => !Number.isSafeInteger(id) || id < 1 || id > 40) || new Set(ids).size !== ids.length)) return out;
    if (entry) {
      const atoms = new Set(entry.snapshot.atoms.map(a => a.id)), bonds = new Set(entry.snapshot.bonds.map(b => b.id));
      if (raw.atoms.some(id => !atoms.has(id)) || raw.bonds.some(id => !bonds.has(id))) return out;
    }
    out.atoms = raw.atoms.slice(); out.bonds = raw.bonds.slice();
    out.attempts = Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0;
    out.submitted = raw.submitted === true && out.attempts > 0 && !!(out.atoms.length || out.bonds.length);
    out.solved = !!(entry && out.submitted && engine().grade(entry.mission, out).correct === true);
    return out;
  }
  function restore(recipe, raw, input, practice) {
    const state = { version: VERSION, seed: raw && raw.version === VERSION && validSeed(raw.seed) ? raw.seed : null,
      currentRound: 0, states: [blank(), blank(), blank()], solved: false };
    if (!state.seed) return state;
    const set = input && engine() ? getSet(recipe, state.seed, input, practice) : null;
    const values = raw && Array.isArray(raw.states) && raw.states.length === 3 ? raw.states : [null, null, null];
    state.states = values.map((value, index) => snapshot(set && set.rounds[index], value));
    state.currentRound = Number.isInteger(raw.currentRound) && raw.currentRound >= 0 && raw.currentRound < 3 ? raw.currentRound : 0;
    if (set) {
      const first = state.states.findIndex(s => !s.solved);
      if (first >= 0) {
        state.currentRound = Math.min(state.currentRound, first);
        for (let i = first + 1; i < 3; i++) state.states[i] = blank();
      } else { state.solved = true; state.currentRound = 2; }
    }
    return state;
  }
  function node(tag, className, text) {
    const value = global.document.createElement(tag);
    if (className) value.className = className;
    if (text !== undefined) value.textContent = text;
    return value;
  }
  function button(text, className, action) {
    const value = node("button", className, text); value.type = "button"; value.addEventListener("click", action); return value;
  }
  function mount(host, options, practice) {
    const recipe = options.round, input = options.input;
    const viewport = options.viewport === true && !!global.NameleculeGameViewport;
    let state = restore(recipe, options.initialState, input, practice);
    if (!state.seed) state.seed = global.NameleculeGeneratedRepairCheckpoint.freshSeed(null);
    let destroyed = false, frame = null, active = null, timer = null, footer = null, requestId = 0;
    let viewportFrame = null;
    const random = new Uint32Array(4); global.crypto.getRandomValues(random);
    const session = Array.from(random, n => n.toString(36).padStart(7, "0")).join("");
    const wireContext = recipe.version === 2 ? levelContext(recipe, state.seed) : null;
    // Compact transport ID only; the complete separate context remains the
    // authority for every echoed response, so hash collisions grant no access.
    const attemptId = "detective-" + recipe.setId + "-" + state.seed + (wireContext ? "-" + contextToken(global.NameleculeGameLevels.contextKey(wireContext)) : "");
    const ready = value => { if (!destroyed && typeof options.onSuccessActionsReady === "function") options.onSuccessActionsReady(value === true); };
    const progress = value => { if (!destroyed && typeof options.onProgress === "function") options.onProgress(value); };
    function publish() {
      state = restore(recipe, state, input, practice);
      if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(clone(state));
    }
    function stopFrame() {
      if (viewportFrame) viewportFrame.destroy(); viewportFrame = null;
      if (timer) global.clearTimeout(timer); timer = null;
      active = null;
      if (frame) frame.remove(); frame = null;
      if (footer) footer.remove(); footer = null;
      ready(false);
    }
    function fail(message) {
      if (destroyed) return;
      stopFrame(); progress(null); host.removeAttribute("aria-busy");
      const error = node("p", "nl-quiz-error", message); error.setAttribute("role", "alert");
      host.replaceChildren(error, button("Δοκίμασε ξανά", "nl-quiz-button", render));
    }
    function actions(context) {
      if (destroyed || active !== context || !context.loaded || !state.states[context.index].solved) return;
      if (footer) footer.remove();
      footer = node("div", "round-next nl-detective-actions");
      const index = context.index;
      const providedLabel = index === 2 && (typeof options.continueLabel === "function" ? options.continueLabel() : options.continueLabel);
      const continueLabel = typeof providedLabel === "string" && providedLabel.trim() ? providedLabel : "Συνεχίζω τη θεωρία";
      const next = button(index < 2 ? "Επόμενο κουίζ" : continueLabel, "nl-quiz-button primary", () => {
        if (destroyed || !state.states[index].solved) return;
        if (index < 2) { state.currentRound = index + 1; publish(); render(); }
        else if (state.solved && typeof options.onContinue === "function") options.onContinue();
      });
      if (index === 2) next.setAttribute("data-checkpoint-continue", "");
      footer.append(next);
      if (index === 2 && typeof options.onNewPractice === "function") footer.append(button(options.newPracticeLabel || "Άλλη τριάδα για εξάσκηση", "nl-quiz-button secondary", options.onNewPractice));
      if (index === 2 && typeof options.onOtherGame === "function") footer.append(button(options.otherGameLabel || "Άλλο παιχνίδι", "nl-quiz-button secondary", options.onOtherGame));
      context.stage.after(footer);
      ready(index === 2 && state.solved && footer.isConnected && !next.disabled);
    }
    function render() {
      if (destroyed) return;
      stopFrame(); publish();
      const set = getSet(recipe, state.seed, input, practice), index = state.currentRound, entry = set.rounds[index];
      const heading = node("h2", "nl-detective-heading", "Μοριακός ντεντέκτιβ"); heading.tabIndex = -1;
      const stage = node("div", "nl-detective-stage");
      frame = node("iframe", "nl-detective-frame"); frame.title = "Μοριακός ντεντέκτιβ — μόριο " + (index + 1) + " από 3";
      frame.setAttribute("sandbox", "allow-scripts allow-same-origin"); frame.style.height = "850px";
      const start = node("span", "nl-detective-marker"), end = node("span", "nl-detective-marker");
      [start, end].forEach(marker => { marker.setAttribute("aria-hidden", "true"); });
      stage.append(frame, start, end); host.replaceChildren(heading, stage); host.setAttribute("aria-busy", "true");
      active = { requestId: ++requestId, index, entry, stage, start, end, loaded: false, sent: false, stateRevision: -1 };
      frame.src = new URL("games/molecular-detective.html?lessonSession=" + session + "&embedded=1&v=game-viewport-20261116-r1" + (viewport ? "&viewport=1" : "") + "", global.document.baseURI).href;
      if (viewport) viewportFrame = global.NameleculeGameViewport.fitFrame(frame, { stage, channel: CHANNEL, session,
        identity: () => active && ({ requestId: active.requestId, attemptId,
          moleculeId: active.entry.snapshot.moleculeId, missionId: active.entry.mission.id,
          ...(wireContext ? { context: wireContext } : {}) }) });
      progress({ current: index + 1, total: 3 });
      timer = global.setTimeout(() => fail("Ο Ντεντέκτιβ άργησε να φορτώσει. Η προσπάθειά σου διατηρήθηκε. Δοκίμασε ξανά."), 90000);
      heading.focus({ preventScroll: true });
    }
    function receive(event) {
      if (destroyed || !frame || !active || event.source !== frame.contentWindow || event.origin !== global.location.origin) return;
      const data = event.data, context = active;
      if (!data || data.channel !== CHANNEL || data.session !== session) return;
      if (data.type === "ready") {
        if (context.sent) return;
        context.sent = true;
        frame.contentWindow.postMessage({ channel: CHANNEL, session, command: "load", requestId: context.requestId, attemptId,
          ...(wireContext ? { context: wireContext } : {}), moleculeId: context.entry.snapshot.moleculeId, snapshot: context.entry.snapshot, missionId: context.entry.mission.id,
          initialState: (({ atoms, bonds, attempts, submitted }) => ({ atoms, bonds, attempts, submitted }))(snapshot(context.entry, state.states[context.index])), explanation: context.entry.mission.explanation }, global.location.origin);
        return;
      }
      if (data.requestId !== context.requestId || data.attemptId !== attemptId || data.moleculeId !== context.entry.snapshot.moleculeId || data.missionId !== context.entry.mission.id) return;
      if (wireContext) { try { if (global.NameleculeGameLevels.contextKey(data.context) !== global.NameleculeGameLevels.contextKey(wireContext)) return; } catch (_) { return; } }
      if (data.type === "error") { fail("Η αποστολή δεν μπόρεσε να επαληθευτεί. Η προσπάθεια διατηρήθηκε. Δοκίμασε ξανά."); return; }
      if (data.type === "exit") { if (typeof options.onClose === "function") options.onClose(); return; }
      if (data.type === "loaded" || data.type === "state") {
        if (data.type === "state" && !context.loaded || data.type === "loaded" && context.loaded) return;
        if (!Number.isSafeInteger(data.stateRevision) || data.stateRevision < 0 || data.stateRevision <= context.stateRevision) return;
        if (data.type === "loaded") {
          try { engine().assertCanonicalSnapshot(context.entry.snapshot, data.snapshot); }
          catch (_) { fail("Το σχέδιο δεν συμφωνεί με το μόριο της αποστολής. Δοκίμασε ξανά."); return; }
          context.loaded = true;
          if (timer) global.clearTimeout(timer); timer = null; host.removeAttribute("aria-busy");
        }
        context.stateRevision = data.stateRevision;
        state.states[context.index] = snapshot(context.entry, data.state); publish();
        if (state.states[context.index].solved) {
          actions(context);
          if (state.solved && typeof options.onSolved === "function") options.onSolved({ kind: "correct" }, clone(state));
        } else { if (footer) footer.remove(); footer = null; ready(false); }
      } else if (data.type === "resize" && Number.isFinite(data.height) && data.height >= 80 && data.height <= 8000) {
        if (!viewport) frame.style.height = Math.ceil(data.height) + "px";
        else if (viewportFrame) viewportFrame.refresh();
      } else if (data.type === "scroll-interrupt" && context.loaded) {
        if (typeof options.onScrollInterrupt === "function") options.onScrollInterrupt();
      } else if (data.type === "reveal" && context.loaded && Number.isFinite(data.startY) && Number.isFinite(data.endY) &&
          data.startY >= 0 && data.endY >= data.startY && data.endY <= 8000 && ["entry", "feedback"].includes(data.purpose)) {
        context.start.style.top = data.startY + "px"; context.end.style.top = data.endY + "px";
        if (typeof options.onReveal === "function") options.onReveal({ kind: "detective-" + data.purpose, start: context.start,
          end: data.purpose === "feedback" && footer ? footer : context.end });
      }
    }
    global.addEventListener("message", receive); render();
    return { destroy() { if (destroyed) return; stopFrame(); progress(null); destroyed = true;
      global.removeEventListener("message", receive); host.replaceChildren(); host.removeAttribute("aria-busy"); } };
  }
  global.NameleculeMolecularDetectiveLesson = Object.freeze({ restore, getSet, snapshot, mount });
})(typeof window !== "undefined" ? window : globalThis);
