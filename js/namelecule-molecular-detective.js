/* Parent game state; the isolated native57 child owns molecular drawing/picking. */
(() => {
  'use strict';
  const engine = window.NameleculeMolecularDetectiveEngine;
  const channel = 'namelecule-molecular-detective-v1';
  const $ = id => document.getElementById(id);
  const ui = Object.fromEntries(['molecule-viewer', 'viewer-wrap', 'viewer-mask', 'viewer-message', 'game-status', 'game-levels', 'mission-name', 'mission-prompt', 'selection-kind', 'selection-status', 'check-answer', 'clear-selection', 'next-mission', 'zoom-in', 'zoom-out', 'retry-load', 'feedback'].map(id => [id, $(id)]));
  const levels = window.NameleculeGameLevels;
  const params = new URLSearchParams(location.search);
  const lessonChannel = 'namelecule-detective-lesson-v1';
  const lessonSession = params.get('lessonSession');
  const lesson = parent !== window && /^[A-Za-z0-9_-]{16,128}$/.test(lessonSession || '')
    ? {current: null, lastId: 0, nativeReady: false, lastHeight: null, lastSnapshot: null, resizeFrame: null, observer: null} : null;
  const viewportEnabled = !!window.NameleculeGameViewport && (!lesson || params.get('viewport') === '1');
  const inlineResults = !!lesson && viewportEnabled;
  let viewport = null;
  let feedbackPager = null;
  let cluePager = null;
  let namePager = null;
  let promptPager = null;
  let feedbackView = false;
  let viewportResizeFrame = null;
  let demandTextContext = null;
  function nativeFormulaQuery() {
    if (!lesson || !viewportEnabled) return '';
    const value = getComputedStyle($('game')).getPropertyValue('--nl-game-formula-px').trim();
    const pixels = Number(value);
    return /^[0-9]+(?:[.][0-9]+)?$/.test(value) && Number.isFinite(pixels) && pixels >= 20 && pixels <= 36
      ? '&nlFormulaPx=' + encodeURIComponent(pixels) : '';
  }
  const lessonMolecules = ['methane', 'ethane', 'propane', 'butane', 'pentane', 'methyl_2_pentane', 'dimethyl_2_3_butane', 'ethyl_3_dimethyl_2_5_hexane'];
  if (params.get('embedded') === '1' || lesson) document.body.classList.add('detective-embedded');
  document.body.classList.toggle('detective-controlled', !!lesson);
  const state = {phase: 'startup', session: '', requestId: 0, roundSerial: 0, missionSerial: 0, roundId: null, moleculeId: null, snapshot: null, missions: [], mission: null, bridgeMissionId: null, loadRequestId: 0, configureRequestId: 0, selectionRevision: -1, atoms: [], bonds: [], attempts: 0, submitted: false, restoring: null, correct: false, stopped: false};
  let levelControls = null;
  const assignment = {category: 'alkanes', level: null, deck: null, nativeReady: false, slots: new Map(), slot: null, restoring: null};
  const alkaneIds = engine?.starterIds?.slice(0, 14) || [];
  const otherIds = engine?.starterIds?.slice(14) || [];
  function newSeed() { const values = new Uint32Array(2); crypto.getRandomValues(values); return values[0] + ':' + values[1]; }
  function clearAssignment() {
    clearTimeout(deadline); stopLocalReveal();
    state.roundId = 'detective-round-' + (++state.roundSerial);
    state.moleculeId = null; state.snapshot = null; state.mission = null; state.missions = []; state.bridgeMissionId = null;
    state.atoms = []; state.bonds = []; state.attempts = 0; state.submitted = false; state.restoring = null;
    state.phase = assignment.nativeReady ? 'choosing' : 'startup';
    clearFeedback();
    ui['mission-name'].textContent = 'Διάλεξε επίπεδο για να ξεκινήσεις';
    ui['mission-prompt'].textContent = 'Η εφαρμογή θα αναθέσει αυτόματα ένα μόριο και ένα στοιχείο στο όνομα.';
    ui['selection-kind'].textContent = 'Περιμένουμε την επιλογή σου';
    ui['selection-status'].textContent = 'Δεν έχεις επιλέξει ακόμη κάτι.';
    busy('Διάλεξε επίπεδο ή κατηγορία για αυτόματη ανάθεση.');
    status('Διάλεξε επίπεδο ή κατηγορία για να ξεκινήσεις.');
  }
  function saveAssignment() {
    if (!lesson && assignment.slot && state.phase === 'active' && state.mission) {
      assignment.slot.round = {moleculeId: state.moleculeId, missionId: state.mission.id, state: snapshot()};
    }
  }
  function resumeAssignment() {
    if (!assignment.nativeReady || !assignment.deck) return;
    assignment.restoring = assignment.slot.round;
    if (assignment.restoring) load(assignment.restoring.moleculeId); else draw();
  }
  function selectAssignment(choice) {
    if (lesson) return;
    saveAssignment();
    const previous = state.moleculeId;
    assignment.category = choice.category; assignment.level = choice.category === 'alkanes' ? choice.level : null;
    const ids = choice.category === 'other' ? otherIds : choice.level ? levels.poolFor(choice.level, alkaneIds) : [];
    const key = choice.category === 'other' ? 'other' : choice.level ? 'level-' + choice.level : null;
    if (key && !assignment.slots.has(key)) assignment.slots.set(key, {deck: levels.createDeck(ids, {seed: newSeed(), avoid: previous}), round: null});
    assignment.slot = key ? assignment.slots.get(key) : null;
    assignment.deck = assignment.slot?.deck || null;
    assignment.restoring = null;
    clearAssignment();
    if (assignment.nativeReady && assignment.deck) resumeAssignment();
    else if (!assignment.nativeReady) watch("Η προβολή του μορίου δεν ξεκίνησε. Δοκίμασε ξανά.", 45000);
  }
  function draw() {
    if (!lesson && assignment.nativeReady && assignment.deck) {
      assignment.slot.round = null; assignment.restoring = null;
      load(assignment.deck.next());
    }
  }
  let deadline;
  let resizeFrame;
  const scrolling = {frame: null, moving: false};
  const sameSelection = (a, b) => a.length === b.length && a.every(id => b.includes(id));
  function snapshot() { return {atoms: state.atoms.slice(), bonds: state.bonds.slice(), attempts: state.attempts, submitted: state.submitted}; }
  function postLesson(type, data = {}, current = lesson?.current) {
    if (!lesson || state.stopped || (type !== 'ready' && !current)) return;
    const identity = current ? {requestId: current.requestId, attemptId: current.attemptId, moleculeId: current.moleculeId, missionId: current.missionId, ...(current.context ? {context: current.context} : {})} : {};
    parent.postMessage({channel: lessonChannel, session: lessonSession, ...identity, type, ...data}, location.origin);
  }
  function scheduleSize() {
    if (viewportEnabled || !lesson || lesson.resizeFrame !== null || state.stopped) return;
    lesson.resizeFrame = requestAnimationFrame(() => {
      lesson.resizeFrame = null;
      if (!lesson.current?.ready || state.stopped) return;
      const height = Math.max(80, Math.min(8000, Math.ceil(document.body.getBoundingClientRect().height)));
      if (Number.isFinite(height) && height !== lesson.lastHeight) { lesson.lastHeight = height; postLesson('resize', {height}); }
    });
  }
  function publishSnapshot() {
    saveAssignment();
    if (lesson?.current?.ready && state.phase === 'active') {
      const value = snapshot(), signature = JSON.stringify(value);
      lesson.current.initialState = value;
      if (signature !== lesson.lastSnapshot) { lesson.lastSnapshot = signature; postLesson('state', {state: value, stateRevision: ++lesson.current.stateRevision}); }
    }
    scheduleSize();
  }
  function stopLocalReveal() {
    if (scrolling.frame !== null) cancelAnimationFrame(scrolling.frame);
    scrolling.frame = null;
    if (scrolling.moving) {
      const top = scrollY, left = scrollX;
      const max = Math.max(0, (document.scrollingElement || document.documentElement).scrollHeight - innerHeight);
      const adjacent = top < max ? Math.min(max, top + 1) : Math.max(0, top - 1);
      if (adjacent !== top) window.scrollTo({top: adjacent, left, behavior: 'instant'});
      window.scrollTo({top, left, behavior: 'instant'});
    }
    scrolling.moving = false;
  }
  function interruptReveal() { stopLocalReveal(); if (lesson?.current?.ready) postLesson('scroll-interrupt'); }
  function revealRange(purpose) {
    stopLocalReveal(); scheduleSize();
    if (viewportEnabled) return;
    const current = lesson?.current, roundId = state.roundId;
    scrolling.frame = requestAnimationFrame(() => {
      scrolling.frame = requestAnimationFrame(() => {
        scrolling.frame = null;
        if (state.stopped || state.phase !== 'active' || roundId !== state.roundId || (lesson && (!current?.ready || current !== lesson.current))) return;
        const firstNode = purpose === 'feedback' ? ui.feedback : $('mission-title');
        const lastNode = purpose === 'feedback' ? $('detective-feedback-end') : ui['mission-prompt'];
        if (firstNode.hidden || !firstNode.isConnected || !lastNode.isConnected) return;
        const first = firstNode.getBoundingClientRect(), last = lastNode.getBoundingClientRect();
        if (first.height <= 0 || last.height <= 0) return;
        if (lesson) {
          const body = document.body.getBoundingClientRect();
          postLesson('reveal', {purpose, startY: Math.max(0, first.top - body.top), endY: Math.max(0, last.bottom - body.top)});
          return;
        }
        const top = 12, bottom = innerHeight - 12;
        if (bottom <= top || (first.top >= top && last.bottom <= bottom)) return;
        const delta = last.bottom - first.top > bottom - top || first.top < top ? first.top - top : last.bottom - bottom;
        const destination = Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, scrollY + delta));
        const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
        scrolling.moving = !reduced;
        window.scrollTo({top: destination, left: scrollX, behavior: reduced ? 'instant' : 'smooth'});
      });
    });
  }
  function validateLessonLoad(data) {
    let context = null, allowedIds = lessonMolecules;
    if (Object.prototype.hasOwnProperty.call(data, 'context')) {
      if (!levels?.validateContext) throw new Error('Η πολιτική της άσκησης δεν φορτώθηκε.');
      context = levels.validateContext(data.context);
      if (context.seed === null) throw new Error('Η άσκηση δεν έχει έγκυρη ταυτότητα προσπάθειας.');
      allowedIds = levels.contextIds(context);
    }
    if (typeof data.attemptId !== 'string' || !data.attemptId || data.attemptId.length > 160 || !allowedIds.includes(data.moleculeId) ||
        typeof data.missionId !== 'string' || !data.missionId || data.missionId.length > 256 ||
        typeof data.explanation !== 'string' || data.explanation.length > 8000 || data.snapshot?.moleculeId !== data.moleculeId) throw new Error('Μη έγκυρα δεδομένα άσκησης.');
    // This boundary verifies the complete canonical graph, source and name;
    // the parent's accepted sets are never part of the protocol.
    engine.assertCanonicalSnapshot(data.snapshot, data.snapshot);
    const mission = engine.missions(data.snapshot).find(item => item.id === data.missionId);
    if (!mission || (context?.source === 'enriched' && context.level > 1 && mission.family === 'single-bonds')) throw new Error('Η αποστολή δεν αντιστοιχεί σε αυτή την άσκηση.');
    const raw = data.initialState || {atoms: [], bonds: [], attempts: 0, submitted: false};
    const known = (ids, all) => Array.isArray(ids) && ids.length <= all.length && new Set(ids).size === ids.length && ids.every(id => Number.isSafeInteger(id) && all.some(item => item.id === id));
    if (!known(raw.atoms, data.snapshot.atoms) || !known(raw.bonds, data.snapshot.bonds) ||
        (mission.kind === 'atoms' ? raw.bonds.length : raw.atoms.length) ||
        !Number.isSafeInteger(raw.attempts) || raw.attempts < 0 || typeof raw.submitted !== 'boolean' || (raw.submitted && !raw.attempts)) throw new Error('Η αποθηκευμένη προσπάθεια δεν επαληθεύτηκε.');
    return {context, requestId: data.requestId, attemptId: data.attemptId, moleculeId: data.moleculeId, missionId: data.missionId,
      snapshot: structuredClone(data.snapshot), explanation: data.explanation,
      initialState: {atoms: raw.atoms.slice(), bonds: raw.bonds.slice(), attempts: raw.attempts, submitted: raw.submitted}, stateRevision: 0, ready: false};
  }
  function receiveLesson(event) {
    if (!lesson || state.stopped || event.source !== parent || event.origin !== location.origin) return;
    const data = event.data;
    if (!data || data.channel !== lessonChannel || data.session !== lessonSession) return;
    if (viewportEnabled && data.command === 'viewport') {
      const current = lesson.current;
      if (!current || data.requestId !== current.requestId || data.attemptId !== current.attemptId ||
          data.moleculeId !== current.moleculeId || data.missionId !== current.missionId ||
          !Number.isFinite(data.height) || data.height < 80 || data.height > 8000 ||
          !Number.isFinite(data.width) || data.width < 80 || data.width > 16000) return;
      if (current.context) {
        try { if (!data.context || levels.contextKey(levels.validateContext(data.context)) !== levels.contextKey(current.context)) return; }
        catch (_) { return; }
      } else if (Object.prototype.hasOwnProperty.call(data, 'context')) return;
      // The iframe's actual viewport is the sole size authority; the parent owns it.
      window.NameleculeGameViewport.acceptViewport($('game'), data);
      viewport?.refresh(); refreshViewport();
      return;
    }
    if (data.command !== 'load' || !Number.isSafeInteger(data.requestId) || data.requestId <= lesson.lastId) return;
    lesson.lastId = data.requestId;
    try {
      const current = validateLessonLoad(data);
      stopLocalReveal(); lesson.current = current; lesson.lastHeight = null; lesson.lastSnapshot = null;
      if (lesson.nativeReady) load(current.moleculeId);
      // Until native startup completes this is a single bounded latest-load queue.
    } catch (error) {
      if (typeof data.attemptId === 'string' && typeof data.moleculeId === 'string' && typeof data.missionId === 'string') postLesson('error', {message: error.message}, data);
    }
  }
  function status(text, error = false, repeatedInstruction = false) {
    ui['game-status'].textContent = text;
    ui['game-status'].classList.toggle('error', error);
    ui['game-status'].classList.toggle('detective-ready-status', inlineResults && repeatedInstruction);
    if (inlineResults) refreshViewport();
  }
  function busy(message) {
    ui['viewer-mask'].hidden = false;
    ui['viewer-message'].textContent = message;
    ui['viewer-wrap'].setAttribute('aria-busy', 'true');
    updateControls();
  }
  function updateControls() {
    const ready = state.phase === 'active';
    for (const id of ['check-answer', 'zoom-in', 'zoom-out']) ui[id].disabled = !ready;
    ui['clear-selection'].disabled = !ready || !(state.atoms.length || state.bonds.length);
    ui['next-mission'].hidden = !!lesson || !ready || !state.correct;
    if (viewportEnabled && $('detective-feedback-open')) $('detective-feedback-open').hidden = inlineResults || ui.feedback.hidden;
    syncMissionPrompt();
    if (inlineResults) refreshViewport();
  }
  function watch(message, milliseconds = 30000) {
    clearTimeout(deadline);
    deadline = setTimeout(() => fail(message), milliseconds);
  }
  function send(command, extra = {}) {
    const requestId = ++state.requestId;
    ui['molecule-viewer'].contentWindow?.postMessage({channel, session: state.session, requestId, roundId: state.roundId, moleculeId: state.moleculeId, command, ...extra}, location.origin);
    return requestId;
  }
  function clearFeedback(resetSubmitted = true) {
    state.correct = false;
    if (resetSubmitted) state.submitted = false;
    ui.feedback.hidden = true;
    ui.feedback.replaceChildren();
    if (inlineResults) ui.feedback.scrollTop = 0;
    ui.feedback.classList.remove('success');
    if (viewportEnabled) setFeedbackView(false);
    updateControls();
    scheduleSize();
  }
  function fail(message) {
    clearTimeout(deadline);
    state.phase = 'error';
    busy(message);
    status(message, true);
    ui['retry-load'].hidden = !!lesson;
    if (lesson?.current) { lesson.current.ready = false; postLesson('error', {message}); }
    scheduleSize();
  }
  function renderName() {
    const fragment = document.createDocumentFragment();
    for (const piece of state.snapshot.pieces) {
      if (piece.separatorBefore) fragment.append(document.createTextNode(piece.separatorBefore));
      const span = document.createElement('span');
      span.className = 'name-piece';
      span.textContent = piece.text;
      if (piece.id === state.mission.pieceId) {
        span.classList.add('clue-piece');
        span.setAttribute('aria-label', 'Επισημασμένο συνθετικό ' + piece.text);
      }
      fragment.append(span);
    }
    ui['mission-name'].replaceChildren(fragment);
    const clue = state.snapshot.pieces.find(piece => piece.id === state.mission.pieceId);
    ui['mission-name'].setAttribute('aria-label', 'Όνομα ένωσης: ' + state.snapshot.correctName + '. Επισημασμένο συνθετικό: ' + (clue?.text || ''));
    ui['mission-prompt'].textContent = state.mission.prompt;
    ui['selection-kind'].textContent = state.mission.kind === 'atoms' ? 'Επιλογή ατόμων' : 'Επιλογή δεσμών';
    if (viewportEnabled && $('detective-show-clue')) {
      $('detective-show-clue').textContent = 'Στοιχείο: ' + (clue?.text || 'Όνομα');
      $('game').dataset.detectiveView = 'structure';
    }
    refreshViewport();
  }
  function configure(index, initialState = null) {
    if (lesson && !initialState) return;
    if (!state.snapshot || !Number.isInteger(index) || !state.missions[index]) return;
    state.phase = 'configuring';
    state.mission = state.missions[index];
    state.bridgeMissionId = state.mission.id + ':' + (++state.missionSerial);
    state.selectionRevision = -1;
    state.atoms = []; state.bonds = [];
    state.attempts = initialState?.attempts || 0;
    state.submitted = initialState?.submitted || false;
    state.restoring = initialState;
    clearFeedback(false); renderName();
    ui['selection-status'].textContent = 'Δεν έχεις επιλέξει ακόμη κάτι.';
    busy('Ετοιμάζουμε την αποστολή.');
    state.configureRequestId = send('configure', {kind: state.mission.kind, missionId: state.bridgeMissionId,
      ...(initialState ? {initialSelection: {atoms: initialState.atoms.slice(), bonds: initialState.bonds.slice()}} : {})});
    watch('Η αποστολή δεν ετοιμάστηκε. Δοκίμασε ξανά.');
  }
  function load(id) {
    if (!engine.starterIds.includes(id)) return;
    if (lesson && (!lesson.nativeReady || lesson.current?.moleculeId !== id)) return;
    stopLocalReveal();
    if (lesson) lesson.current.ready = false;
    state.phase = 'loading';
    state.moleculeId = id;
    state.roundId = 'detective-round-' + (++state.roundSerial);
    state.snapshot = null; state.missions = []; state.mission = null; state.bridgeMissionId = null;
    state.atoms = []; state.bonds = [];
    state.attempts = 0; state.submitted = false; state.restoring = null;
    clearFeedback();
    ui['mission-name'].textContent = 'Φορτώνουμε το όνομα…';
    ui['mission-prompt'].textContent = 'Σε λίγο θα εμφανιστεί η αποστολή σου.';
    ui['selection-kind'].textContent = 'Περιμένουμε το στοιχείο';
    ui['selection-status'].textContent = 'Δεν έχεις επιλέξει ακόμη κάτι.';
    busy('Φορτώνουμε τον ανεπτυγμένο τύπο.');
    status('Ετοιμάζουμε το μόριο και το στοιχείο στο όνομα.');
    state.loadRequestId = send('load', {moleculeId: id});
    watch('Το μοριακό σχέδιο δεν φορτώθηκε. Δοκίμασε ξανά.');
  }
  function validSelection(data) {
    if (!Array.isArray(data.atoms) || !Array.isArray(data.bonds) || !Number.isSafeInteger(data.selectionRevision) || data.selectionRevision < 0) return false;
    const knownAtoms = new Set(state.snapshot.atoms.map(a => a.id));
    const knownBonds = new Set(state.snapshot.bonds.map(b => b.id));
    return !(state.mission.kind === 'atoms' ? data.bonds.length : data.atoms.length) &&
      data.atoms.every(a => Number.isSafeInteger(a) && knownAtoms.has(a)) && data.bonds.every(b => Number.isSafeInteger(b) && knownBonds.has(b)) && new Set(data.atoms).size === data.atoms.length && new Set(data.bonds).size === data.bonds.length;
  }
  function receive(event) {
    const data = event.data;
    if (state.stopped || event.source !== ui['molecule-viewer'].contentWindow || event.origin !== location.origin || !data || data.channel !== channel || data.session !== state.session || !Number.isSafeInteger(data.requestId) || data.requestId < 0) return;
    if (data.type === 'ready' && state.phase === 'startup') {
      if (!Array.isArray(data.inventory) || engine.starterIds.some(id => !data.inventory.some(item => item.id === id))) { fail('Δεν είναι διαθέσιμα όλα τα μόρια της εξάσκησης.'); return; }
      clearTimeout(deadline);
      if (lesson) {
        lesson.nativeReady = true;
        postLesson('ready', {}, null);
        if (lesson.current) load(lesson.current.moleculeId);
        else { status('Περιμένουμε το μόριο του μαθήματος.'); busy('Περιμένουμε την αποστολή του μαθήματος.'); }
        return;
      }
      assignment.nativeReady = true;
      if (assignment.deck) resumeAssignment();
      else clearAssignment();
      return;
    }
    if (data.type === 'error') {
      if (state.phase === 'startup' || (data.roundId === state.roundId && data.moleculeId === state.moleculeId && data.requestId >= state.loadRequestId)) fail(data.message || 'Η προβολή δεν μπόρεσε να ολοκληρωθεί. Δοκίμασε ξανά.');
      return;
    }
    if (data.roundId !== state.roundId || data.moleculeId !== state.moleculeId) return;
    if (data.type === 'round' && state.phase === 'loading' && data.requestId === state.loadRequestId) {
      try {
        if (data.snapshot?.moleculeId !== state.moleculeId) throw new Error('Molecule mismatch');
        if (lesson) engine.assertCanonicalSnapshot(lesson.current.snapshot, data.snapshot);
        const available = engine.missions(data.snapshot).filter(mission => lesson || assignment.category !== 'alkanes' || assignment.level === 1 || mission.family !== 'single-bonds');
        if (!available.length) throw new Error('No supported missions');
        state.snapshot = data.snapshot;
        // Each standalone draw has exactly one randomly assigned valid clue.
        // All equivalent accepted atom sets remain on that immutable mission.
        if (lesson) state.missions = available;
        else {
          const previous = assignment.restoring && available.find(mission => mission.id === assignment.restoring.missionId);
          if (assignment.restoring && !previous) throw new Error('Stored mission mismatch');
          const chosenIndex = previous ? available.indexOf(previous) : Number(levels.createDeck(available.map((mission, index) => String(index)), {seed: newSeed()}).next());
          state.missions = [available[chosenIndex]];
        }
        const index = lesson ? state.missions.findIndex(mission => mission.id === lesson.current.missionId) : 0;
        if (index < 0) throw new Error('Canonical mission mismatch');
        configure(index, lesson?.current?.initialState || assignment.restoring?.state || null);
      } catch (error) { fail('Η αποστολή αυτού του μορίου δεν είναι διαθέσιμη. Δοκίμασε ξανά.'); }
      return;
    }
    if (!state.snapshot || data.missionId !== state.bridgeMissionId || data.requestId < state.configureRequestId || data.kind !== state.mission?.kind) return;
    let configured = false;
    if (data.type === 'configured' && state.phase === 'configuring' && data.requestId === state.configureRequestId) {
      if (!validSelection(data)) { fail('Η επιλογή δεν μπόρεσε να ετοιμαστεί. Δοκίμασε ξανά.'); return; }
      if (state.restoring && (!sameSelection(state.restoring.atoms, data.atoms) || !sameSelection(state.restoring.bonds, data.bonds))) { fail('Η αποθηκευμένη επιλογή δεν εμφανίστηκε σωστά. Δοκίμασε ξανά.'); return; }
      clearTimeout(deadline);
      state.phase = 'active';
      ui['viewer-mask'].hidden = true;
      ui['viewer-wrap'].setAttribute('aria-busy', 'false');
      ui['retry-load'].hidden = true;
      status('Παρατήρησε το επισημασμένο συνθετικό και επίλεξε όσα ζητά η αποστολή.', false, true);
      configured = true;
    }
    if (['configured', 'selection'].includes(data.type) && state.phase === 'active' && validSelection(data) && (data.selectionRevision > state.selectionRevision || (data.selectionRevision === state.selectionRevision && sameSelection(state.atoms, data.atoms) && sameSelection(state.bonds, data.bonds)))) {
      const changed = !sameSelection(state.atoms, data.atoms) || !sameSelection(state.bonds, data.bonds);
      state.selectionRevision = data.selectionRevision;
      state.atoms = data.atoms.slice(); state.bonds = data.bonds.slice();
      if (changed && !configured) clearFeedback();
      const count = state.mission.kind === 'atoms' ? state.atoms.length : state.bonds.length;
      ui['selection-status'].textContent = count ? (state.mission.kind === 'atoms' ? 'Επιλεγμένα άτομα: ' : 'Επιλεγμένοι δεσμοί: ') + count : 'Δεν έχεις επιλέξει ακόμη κάτι.';
      if (data.note === 'WRONG_KIND') status(state.mission.kind === 'atoms' ? 'Σε αυτή την αποστολή επίλεξε άτομα, πατώντας στα σύμβολά τους.' : 'Σε αυτή την αποστολή επίλεξε δεσμούς, πατώντας στις γραμμές τους.');
      updateControls();
      if (configured) {
        state.restoring = null;
        assignment.restoring = null; saveAssignment();
        if (state.submitted) showFeedback();
        if (lesson) {
          lesson.current.ready = true;
          lesson.current.initialState = snapshot();
          lesson.lastSnapshot = JSON.stringify(snapshot());
          lesson.current.stateRevision = 0;
          postLesson('loaded', {state: snapshot(), snapshot: state.snapshot, stateRevision: 0});
          scheduleSize(); revealRange(state.submitted ? 'feedback' : 'entry');
        }
      } else publishSnapshot();
    }
  }
  function showFeedback() {
    const result = engine.grade(state.mission, {atoms: state.atoms, bonds: state.bonds});
    state.correct = result.correct;
    const heading = document.createElement('strong');
    const message = document.createElement('p');
    heading.textContent = result.correct ? '✓ Η υπόθεση λύθηκε!' : result.kind === 'empty' ? 'Κάνε πρώτα μια επιλογή' : 'Παρατήρησε ξανά τα στοιχεία';
    message.textContent = result.correct ? (lesson?.current?.explanation || state.mission.explanation) : result.kind === 'empty' ? 'Επίλεξε στο μοριακό σχέδιο όσα ζητά η αποστολή.' : 'Η επιλογή δεν αντιστοιχεί ακόμη στο επισημασμένο συνθετικό. Μπορείς να τη διορθώσεις και να δοκιμάσεις ξανά.';
    ui.feedback.replaceChildren(heading, message);
    const end = document.createElement('span'); end.id = 'detective-feedback-end'; end.className = 'detective-feedback-end'; end.setAttribute('aria-hidden', 'true'); ui.feedback.append(end);
    ui.feedback.classList.toggle('success', result.correct);
    ui.feedback.hidden = false;
    if (inlineResults) ui.feedback.scrollTop = 0;
    if (viewportEnabled) setFeedbackView(true);
    updateControls(); scheduleSize();
  }
  function check() {
    if (state.phase !== 'active') return;
    state.attempts++; state.submitted = true;
    showFeedback(); publishSnapshot(); revealRange('feedback');
  }
  function next() {
    if (lesson || !state.correct || state.phase !== 'active') return;
    draw();
    const focusTarget = viewportEnabled && $('game').classList.contains('nl-vp-narrow') ? $('detective-show-clue') : $('mission-title');
    focusTarget.focus({preventScroll: true});
  }
  function start() {
    if (!engine?.starterIds?.length || (!lesson && !levels)) { fail('Το παιχνίδι δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.'); return; }
    clearTimeout(deadline);
    stopLocalReveal();
    assignment.nativeReady = false;
    if (lesson) { lesson.nativeReady = false; lesson.lastHeight = null; if (lesson.current) lesson.current.ready = false; }
    state.phase = 'startup'; state.session = crypto.randomUUID().replaceAll('-', ''); state.requestId = 0;
    state.snapshot = null; state.mission = null; state.bridgeMissionId = null;
    state.atoms = []; state.bonds = []; state.attempts = 0; state.submitted = false; state.restoring = null;
    clearFeedback(); busy('Φορτώνουμε τον ανεπτυγμένο τύπο.');
    status('Ετοιμάζουμε την πρώτη αποστολή.');
    ui['retry-load'].hidden = true;
    ui['molecule-viewer'].src = 'molecular-detective-viewer.html?v=adaptive-dialog-20261118-r3&session=' + state.session + nativeFormulaQuery();
    watch('Η προβολή του μορίου δεν ξεκίνησε. Δοκίμασε ξανά.', 45000);
  }
  function stop() {
    if (state.stopped) return;
    send('stop'); state.stopped = true;
    clearTimeout(deadline); cancelAnimationFrame(resizeFrame); resizeFrame = null;
    stopLocalReveal();
    if (viewportResizeFrame !== null) cancelAnimationFrame(viewportResizeFrame);
    viewportResizeFrame = null; viewport?.destroy(); viewport = null;
    if (lesson) {
      if (lesson.resizeFrame !== null) cancelAnimationFrame(lesson.resizeFrame);
      lesson.resizeFrame = null; lesson.observer?.disconnect(); lesson.nativeReady = false;
    }
    window.removeEventListener('message', receive);
    window.removeEventListener('message', receiveLesson);
  }
  ui['check-answer'].addEventListener('click', check);
  ui['clear-selection'].addEventListener('click', () => { if (state.phase === 'active') send('clear', {missionId: state.bridgeMissionId}); });
  ui['next-mission'].addEventListener('click', next);
  ui['zoom-in'].addEventListener('click', () => { if (state.phase === 'active') send('zoom', {direction: 1, missionId: state.bridgeMissionId}); });
  ui['zoom-out'].addEventListener('click', () => { if (state.phase === 'active') send('zoom', {direction: -1, missionId: state.bridgeMissionId}); });
  ui['retry-load'].addEventListener('click', () => { if (!lesson) start(); });
  window.addEventListener('message', receive);
  window.addEventListener('message', receiveLesson);
  window.addEventListener('pagehide', stop, {once: true});
  window.addEventListener('pageshow', event => {
    if (event.persisted && state.stopped) {
      state.stopped = false;
      window.addEventListener('message', receive);
      window.addEventListener('message', receiveLesson);
      window.addEventListener('pagehide', stop, {once: true});
      lesson?.observer?.observe(document.body);
      if (viewportEnabled) mountViewport();
      start();
    }
  });
  window.addEventListener('resize', () => {
    scheduleSize();
    if (resizeFrame || state.phase !== 'active') return;
    resizeFrame = requestAnimationFrame(() => { resizeFrame = null; if (!state.stopped && state.phase === 'active') send('resize', {missionId: state.bridgeMissionId}); });
  });
  function lessonExitKey(event) {
    if (viewportEnabled && event.key === 'Escape' && feedbackView) { event.preventDefault(); event.stopPropagation(); setFeedbackView(false); ui['check-answer'].focus({preventScroll: true}); return; }
    if (lesson && event.key === 'Escape') { event.preventDefault(); postLesson('exit'); }
  }
  window.addEventListener('keydown', lessonExitKey);
  ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => window.addEventListener(type, interruptReveal, {capture: true, passive: true}));
  ui['molecule-viewer'].addEventListener('load', () => {
    // Input in the native same-origin frame does not bubble through its owner.
    try {
      ui['molecule-viewer'].contentWindow.addEventListener('keydown', lessonExitKey);
      ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => ui['molecule-viewer'].contentWindow.addEventListener(type, interruptReveal, {capture: true, passive: true}));
    } catch (_) { /* The ordinary startup/retry path reports viewer failures. */ }
  });
  if (!lesson && levels) {
    levelControls = levels.mount(ui['game-levels'], {availableIds: alkaneIds, allowedLevels: [1, 2, 3], selectedLevel: null,
      category: 'alkanes', otherCount: otherIds.length, compact: viewportEnabled, onSelect: selectAssignment});
  }
  if (lesson) {
    if (ui['game-levels']) ui['game-levels'].hidden = true;
    document.documentElement.classList.add('lesson-mode');
    if (!viewportEnabled) { lesson.observer = new ResizeObserver(scheduleSize); lesson.observer.observe(document.body); }
  }
  function refreshViewport() {
    if (!viewportEnabled || state.stopped) return;
    promptPager?.refresh(); feedbackPager?.refresh(); namePager?.refresh(); cluePager?.refresh();
    if (viewportResizeFrame !== null) return;
    viewportResizeFrame = requestAnimationFrame(() => {
      viewportResizeFrame = null;
      fitNarrowWorkspace();
      if (inlineResults) viewport?.refresh();
      if (!state.stopped && state.phase === 'active' && !feedbackView) send('resize', {missionId: state.bridgeMissionId});
    });
  }
  function fitNarrowWorkspace() {
    if (!inlineResults || state.stopped) return;
    const game = $('game'), workspace = game.querySelector('.detective-workspace');
    if (!game.classList.contains('nl-vp-narrow') || game.getBoundingClientRect().width >= 760) {
      game.classList.remove('detective-result-side-pager');
      game.style.removeProperty('--nl-detective-pane-min-height');
      game.style.removeProperty('--nl-detective-result-min-height');
      return;
    }
    const pixels = value => parseFloat(value) || 0;
    const chrome = element => {
      const style = getComputedStyle(element);
      return pixels(style.borderTopWidth) + pixels(style.borderBottomWidth);
    };
    const molecule = game.querySelector('.detective-molecule'), answer = game.querySelector('.detective-answer');
    // The native SVG has a measured 150px CSS floor. Reserve its real header
    // and the complete natural answer, rather than shrinking their grid rows.
    const moleculeMinimum = molecule.querySelector('.panel-header').getBoundingClientRect().height + 150 + chrome(molecule);
    const answerMinimum = answer.querySelector('.detective-answer-content').getBoundingClientRect().height + chrome(answer);
    const paneMinimum = Math.ceil(Math.max(moleculeMinimum, answerMinimum));
    game.style.setProperty('--nl-detective-pane-min-height', paneMinimum + 'px');
    const style = getComputedStyle(ui.feedback);
    const lines = [pixels(style.lineHeight), ...Array.from(ui.feedback.querySelectorAll('strong,p,.single-line-name'),
      element => pixels(getComputedStyle(element).lineHeight))];
    const contentMinimum = Math.max(...lines) + pixels(style.paddingTop) + pixels(style.paddingBottom) + chrome(ui.feedback);
    const nav = feedbackPager.element.querySelector('.nl-vp-pager-nav');
    const buttons = Array.from(nav.querySelectorAll('button'));
    const buttonMinimum = Math.max(...buttons.map(button => pixels(getComputedStyle(button).minHeight)));
    const countLine = pixels(getComputedStyle(nav.querySelector('span')).lineHeight);
    const normalMinimum = Math.ceil(contentMinimum + 40);
    const side = !ui.feedback.hidden && workspace.getBoundingClientRect().height < paneMinimum + normalMinimum + 4;
    game.classList.toggle('detective-result-side-pager', side);
    game.style.setProperty('--nl-detective-result-min-height', Math.ceil(side
      ? Math.max(contentMinimum, buttonMinimum + countLine + 2) : normalMinimum) + 'px');
    feedbackPager.refresh(); namePager?.refresh(); cluePager?.refresh();
  }
  function syncMissionPrompt() {
    if (!inlineResults) return;
    const region = promptPager?.element || ui['mission-prompt'];
    const hidden = state.phase !== 'active' || !state.mission;
    if (region.hidden === hidden) return;
    region.hidden = hidden;
    promptPager?.refresh(); viewport?.refresh(); refreshViewport();
  }
  function setFeedbackView(enabled) {
    if (!viewportEnabled) return;
    // Lesson feedback shares the current workspace; only standalone changes view.
    feedbackView = enabled && !inlineResults;
    $('game').classList.toggle('detective-feedback-view', feedbackView);
    $('game').classList.toggle('detective-inline-feedback', enabled && inlineResults);
    if ($('detective-feedback-stage')) $('detective-feedback-stage').hidden = !enabled;
    if (enabled && !inlineResults) {
      $('detective-feedback-title').textContent = state.correct ? 'Η υπόθεση λύθηκε' : 'Παρατήρησε την εξήγηση';
      $('detective-feedback-back').textContent = state.correct ? 'Δες την επιλογή σου' : 'Επιστροφή στην προσπάθεια';
      $('detective-feedback-title').focus({preventScroll: true});
    }
    feedbackPager?.refresh(); viewport?.refresh(); refreshViewport();
  }
  function mountViewport() {
    if (viewport || !viewportEnabled) return;
    viewport = window.NameleculeGameViewport.mount($('game'), {kind: 'detective', onResize: refreshViewport,
      preferred: inlineResults ? preferredViewport : null,
      onDemand: inlineResults ? detail => postLesson('layout-demand', detail) : null});
  }
  function preferredViewport() {
    const current = lesson?.current;
    if (!inlineResults || state.stopped || state.phase !== 'active' || !current?.ready || !state.mission) return null;
    const game = $('game'), workspace = game.querySelector('.detective-workspace');
    const shared = window.NameleculeGameViewport, pixels = value => parseFloat(value) || 0;
    const width = game.getBoundingClientRect().width;
    if (!(width > 0)) return null;
    const css = element => getComputedStyle(element);
    const horizontal = style => pixels(style.paddingLeft) + pixels(style.paddingRight) + pixels(style.borderLeftWidth) + pixels(style.borderRightWidth);
    const vertical = style => pixels(style.paddingTop) + pixels(style.paddingBottom) + pixels(style.borderTopWidth) + pixels(style.borderBottomWidth);
    const line = style => pixels(style.lineHeight) || pixels(style.fontSize) * 1.5;
    if (!demandTextContext) demandTextContext = document.createElement('canvas').getContext('2d');
    const textWidth = (text, style) => {
      if (!demandTextContext) return String(text).length * pixels(style.fontSize) * .6;
      demandTextContext.font = style.fontStyle + ' ' + style.fontWeight + ' ' + style.fontSize + ' ' + style.fontFamily;
      return demandTextContext.measureText(text).width;
    };
    const textHeight = (text, style, available) => {
      const limit = Math.max(1, available - horizontal(style)), space = textWidth(' ', style);
      let rows = 1, used = 0;
      String(text).trim().split(/\s+/).forEach(word => {
        const extent = textWidth(word, style);
        if (used && used + space + extent > limit) { rows++; used = 0; }
        rows += Math.max(0, Math.ceil(extent / limit) - 1);
        used = (used ? used + space : 0) + Math.min(limit, extent);
      });
      return rows * line(style) + vertical(style);
    };
    const gameStyle = css(game), inner = Math.max(1, width - horizontal(gameStyle));
    const narrow = width < 760 || shared.availableHeight(game) < 430;
    const small = width < 760;
    const workspaceGap = pixels(css(workspace).columnGap);
    // Use the layout with feedback already present, before the first Check.
    // At small widths the two panes share a row and the result is below it.
    const moleculeWidth = small ? (inner - workspaceGap) / 2 : narrow ? (inner - workspaceGap) * 1.1 / 2 : (inner - 2 * workspaceGap) * .9 / 2.8;
    const clueWidth = small ? moleculeWidth : narrow ? moleculeWidth : (inner - 2 * workspaceGap) / 2.8;
    const answerWidth = small ? moleculeWidth : clueWidth;
    const molecule = game.querySelector('.detective-molecule'), moleculeHeader = molecule.querySelector('.panel-header');
    const headerStyle = css(moleculeHeader), headerTitle = moleculeHeader.querySelector('h2'), titleStyle = css(headerTitle);
    const zoom = moleculeHeader.querySelector('.zoom-controls'), zoomStyle = css(zoom);
    const zoomButtons = Array.from(zoom.querySelectorAll('button'));
    const zoomWidth = zoomButtons.reduce((sum, button) => { const style = css(button); return sum + Math.max(pixels(style.minWidth), pixels(style.width)); }, Math.max(0, zoomButtons.length - 1) * pixels(zoomStyle.columnGap));
    const headerHeight = Math.max(moleculeHeader.getBoundingClientRect().height, pixels(headerStyle.minHeight), vertical(headerStyle) + Math.max(34, textHeight(headerTitle.textContent, titleStyle, moleculeWidth - horizontal(css(molecule)) - horizontal(headerStyle) - zoomWidth - pixels(headerStyle.columnGap))));
    // The isolated native SVG has a real 150px floor; this envelope never
    // feeds the parent's allocation back into preferred molecular geometry.
    const moleculeHeight = headerHeight + 150 + vertical(css(molecule));
    const answer = game.querySelector('.detective-answer'), answerContent = answer.querySelector('.detective-answer-content'), answerStyle = css(answerContent);
    const answerInner = Math.max(1, answerWidth - horizontal(css(answer)) - horizontal(answerStyle));
    const help = answerContent.querySelector('.detective-help'), helpStyle = css(help), selectionStyle = css(ui['selection-status']);
    const checkRow = answerContent.querySelector('.check-row'), rowStyle = css(checkRow), buttons = Array.from(checkRow.querySelectorAll('button'));
    const buttonHeight = Math.max(...buttons.map(button => { const style = css(button); return Math.max(pixels(style.minHeight), line(style) + vertical(style)); }));
    const buttonsWidth = buttons.reduce((sum, button) => { const style = css(button); return sum + textWidth(button.textContent, style) + horizontal(style); }, Math.max(0, buttons.length - 1) * pixels(rowStyle.columnGap));
    const actionHeight = small || buttonsWidth > answerInner ? buttons.length * buttonHeight + Math.max(0, buttons.length - 1) * pixels(rowStyle.rowGap) : buttonHeight;
    const selectionText = state.mission.kind === 'atoms' ? 'Επιλεγμένα άτομα: 999' : 'Επιλεγμένοι δεσμοί: 999';
    const answerHeight = vertical(css(answer)) + Math.max(answerContent.getBoundingClientRect().height, vertical(answerStyle) + textHeight(help.textContent, helpStyle, answerInner) + pixels(helpStyle.marginBottom) + Math.max(textHeight('Δεν έχεις επιλέξει ακόμη κάτι.', selectionStyle, answerInner), textHeight(selectionText, selectionStyle, answerInner)) + pixels(rowStyle.marginTop) + actionHeight);
    const clue = game.querySelector('.detective-clue'), clueHeader = clue.querySelector('.panel-header'), clueHeaderStyle = css(clueHeader);
    const clueTitle = clueHeader.querySelector('h2'), clueContent = clue.querySelector('.detective-clue-content'), clueStyle = css(clueContent), nameStyle = css(ui['mission-name']);
    const nameInner = Math.max(1, clueWidth - horizontal(css(clue)) - horizontal(clueStyle));
    const nameHeight = line(nameStyle) + vertical(nameStyle) + (textWidth(ui['mission-name'].textContent, nameStyle) > nameInner ? 40 : 0);
    const clueHeaderInner = Math.max(1, clueWidth - horizontal(css(clue)) - horizontal(clueHeaderStyle));
    const kindStyle = css(ui['selection-kind']), kindWidth = Math.min(clueHeaderInner / 2, textWidth(ui['selection-kind'].textContent, kindStyle));
    const clueHeaderHeight = Math.max(clueHeader.getBoundingClientRect().height, pixels(clueHeaderStyle.minHeight), vertical(clueHeaderStyle) + Math.max(textHeight(clueTitle.textContent, css(clueTitle), clueHeaderInner - kindWidth - pixels(clueHeaderStyle.columnGap)), textHeight(ui['selection-kind'].textContent, kindStyle, kindWidth)));
    const clueHeight = vertical(css(clue)) + clueHeaderHeight + vertical(clueStyle) + nameHeight + 8;
    const feedbackStyle = css(ui.feedback);
    // One complete explanation line plus the existing local pager remains
    // readable in the compact pane. Wide results can show two lines at once.
    const resultHeight = Math.max(76, (small ? 1 : 2) * line(feedbackStyle) + vertical(feedbackStyle) + 40);
    const paneHeight = Math.max(moleculeHeight, answerHeight, clueHeight);
    const workspaceHeight = small ? paneHeight + resultHeight + pixels(css(workspace).rowGap) : Math.max(moleculeHeight, clueHeight + answerHeight + pixels(css(workspace).rowGap), resultHeight);
    const statusStyle = css(ui['game-status']);
    const normalStatus = Math.max(...[
      'Σε αυτή την αποστολή επίλεξε άτομα, πατώντας στα σύμβολά τους.',
      'Σε αυτή την αποστολή επίλεξε δεσμούς, πατώντας στις γραμμές τους.'
    ].map(text => textHeight(text, statusStyle, inner)));
    const actualStatus = statusStyle.position === 'absolute' || statusStyle.display === 'none' ? 0 : ui['game-status'].getBoundingClientRect().height;
    // Ready status is visually hidden, but WRONG_KIND is an ordinary supported
    // instruction. Reserve its row and gap before the first native selection.
    const statusReserve = Math.max(0, normalStatus - actualStatus) + (actualStatus ? 0 : pixels(gameStyle.rowGap));
    const key = JSON.stringify([current.requestId, current.attemptId, current.moleculeId, current.missionId]);
    return shared.preferred(game, workspace, workspaceHeight + statusReserve, key);
  }
  function configureViewport() {
    const game = $('game'); game.classList.add('detective-viewport');
    game.classList.toggle('nl-inline-results', inlineResults);
    const makeButton = (text, id, handler) => {
      const result = document.createElement('button'); result.type = 'button'; result.className = 'secondary'; result.textContent = text; result.id = id; result.addEventListener('click', handler); return result;
    };
    const stage = document.createElement('section'); stage.id = 'detective-feedback-stage'; stage.className = 'detective-feedback-stage'; stage.hidden = true;
    const heading = document.createElement('div'); heading.className = 'detective-feedback-heading';
    const title = document.createElement('h2'); title.id = 'detective-feedback-title'; title.tabIndex = -1;
    const back = makeButton('Επιστροφή στην προσπάθεια', 'detective-feedback-back', () => { setFeedbackView(false); ui['check-answer'].focus({preventScroll: true}); });
    heading.append(title, back);
    if (!inlineResults) stage.append(heading);
    stage.append(ui.feedback, ui['next-mission']);
    if (inlineResults) {
      stage.classList.add('nl-inline-result');
      document.querySelector('.detective-workspace').append(stage);
    } else game.append(stage);
    const views = document.createElement('div'); views.className = 'detective-stage-tabs';
    const showView = view => { game.dataset.detectiveView = view; for (const button of views.querySelectorAll('button')) button.setAttribute('aria-pressed', String(button.dataset.detectiveViewButton === view)); refreshViewport(); };
    const clueButton = makeButton('Στοιχείο στο όνομα', 'detective-show-clue', () => showView('clue')); clueButton.dataset.detectiveViewButton = 'clue';
    const moleculeButton = makeButton('Μόριο & επιλογή', 'detective-show-structure', () => showView('structure')); moleculeButton.dataset.detectiveViewButton = 'structure';
    views.append(clueButton, moleculeButton); document.querySelector('.detective-workspace').before(views);
    showView('structure');
    if (!inlineResults) {
      ui['check-answer'].parentNode.append(makeButton('Εξήγηση', 'detective-feedback-open', () => setFeedbackView(true)));
      $('detective-feedback-open').hidden = true;
    }
    const clue = document.querySelector('.detective-clue-content');
    if (inlineResults) {
      document.querySelector('.intro .nl-game-mission').after(ui['mission-prompt']);
      promptPager = window.NameleculeGameViewport.pager(ui['mission-prompt'], {axis: 'y', label: 'Αποστολή'});
      promptPager.element.classList.add('detective-prompt-pager');
      promptPager.element.hidden = true;
    }
    // Long names remain one line, with button paging. The highlighted piece is unchanged.
    namePager = window.NameleculeGameViewport.pager(ui['mission-name'], {axis: 'x', label: 'Πλήρες όνομα ένωσης'});
    // The inline name clue keeps its own controls; its mission prompt has one
    // separate owner in the heading. Standalone retains the original prompt.
    cluePager = window.NameleculeGameViewport.pager(inlineResults ? clue : ui['mission-prompt'], {axis: 'y', label: inlineResults ? 'Στοιχείο στο όνομα' : 'Αποστολή'});
    feedbackPager = window.NameleculeGameViewport.pager(ui.feedback, {axis: 'y', label: 'Εξήγηση αποστολής'});
    game.addEventListener('nl-level-stage', refreshViewport);
    mountViewport();
    game.classList.toggle('nl-vp-level-selection', !!game.querySelector('.nl-game-levels.is-expanded'));
  }
  if (viewportEnabled) configureViewport();
  window.NameleculeMolecularDetective = Object.freeze({snapshot: () => ({category: assignment.category, level: assignment.level, phase: state.phase, moleculeId: state.moleculeId, roundId: state.roundId, missionId: state.mission?.id, bridgeMissionId: state.bridgeMissionId, missionIndex: state.missions.indexOf(state.mission), missionCount: state.missions.length, kind: state.mission?.kind, ...snapshot(), selectionRevision: state.selectionRevision, correct: state.correct, requestId: state.requestId})});
  start();
})();
