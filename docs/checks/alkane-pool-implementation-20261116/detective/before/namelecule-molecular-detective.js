/* Parent game state; the isolated native56 child owns molecular drawing/picking. */
(() => {
  'use strict';
  const engine = window.NameleculeMolecularDetectiveEngine;
  const channel = 'namelecule-molecular-detective-v1';
  const $ = id => document.getElementById(id);
  const ui = Object.fromEntries(['molecule-viewer', 'viewer-wrap', 'viewer-mask', 'viewer-message', 'game-status', 'molecule-select', 'mission-select', 'mission-name', 'mission-prompt', 'selection-kind', 'selection-status', 'check-answer', 'clear-selection', 'next-mission', 'zoom-in', 'zoom-out', 'retry-load', 'feedback'].map(id => [id, $(id)]));
  const labels = {ethane: 'Αιθάνιο', butane: 'Βουτάνιο', methyl_2_pentane: '2-μεθυλοπεντάνιο', dimethyl_2_3_butane: '2,3-διμεθυλοβουτάνιο', ethene: 'Αιθένιο', butene_1: '1-βουτένιο', butene_2: '2-βουτένιο', butyne_1: '1-βουτίνιο', butyne_2: '2-βουτίνιο', butadiene_1_2: '1,2-βουταδιένιο', butadiene_1_3: '1,3-βουταδιένιο', ethanol: 'Αιθανόλη', butanol_2: '2-βουτανόλη', propanal: 'Προπανάλη', propanone: 'Προπανόνη', pentanone_3: '3-πεντανόνη', methanoicacid: 'Μεθανικό οξύ'};
  const familyLabels = {'parent-chain': 'Κύρια αλυσίδα', 'single-bonds': 'Απλοί δεσμοί', 'double-bonds': 'Διπλοί δεσμοί', 'triple-bonds': 'Τριπλοί δεσμοί', branches: 'Διακλαδώσεις', hydroxyl: 'Υδροξύλιο', aldehyde: 'Αλδεϋδομάδα', carbonyl: 'Καρβονύλιο', carboxyl: 'Καρβοξύλιο'};
  const params = new URLSearchParams(location.search);
  if (params.get('embedded') === '1') document.body.classList.add('detective-embedded');
  const state = {phase: 'startup', session: '', requestId: 0, roundSerial: 0, missionSerial: 0, roundId: null, moleculeId: null, snapshot: null, missions: [], mission: null, bridgeMissionId: null, loadRequestId: 0, configureRequestId: 0, selectionRevision: -1, atoms: [], bonds: [], correct: false, stopped: false};
  let deadline;
  let resizeFrame;
  const sameSelection = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  function status(text, error = false) { ui['game-status'].textContent = text; ui['game-status'].classList.toggle('error', error); }
  function busy(message) {
    ui['viewer-mask'].hidden = false;
    ui['viewer-message'].textContent = message;
    ui['viewer-wrap'].setAttribute('aria-busy', 'true');
    updateControls();
  }
  function updateControls() {
    const ready = state.phase === 'active';
    ui['molecule-select'].disabled = !['active', 'configuring'].includes(state.phase);
    ui['mission-select'].disabled = !ready;
    for (const id of ['check-answer', 'zoom-in', 'zoom-out']) ui[id].disabled = !ready;
    ui['clear-selection'].disabled = !ready || !(state.atoms.length || state.bonds.length);
    ui['next-mission'].hidden = !ready || !state.correct;
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
  function clearFeedback() {
    state.correct = false;
    ui.feedback.hidden = true;
    ui.feedback.replaceChildren();
    ui.feedback.classList.remove('success');
    updateControls();
  }
  function fail(message) {
    clearTimeout(deadline);
    state.phase = 'error';
    busy(message);
    status(message, true);
    ui['retry-load'].hidden = false;
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
  }
  function configure(index) {
    if (!state.snapshot || !Number.isInteger(index) || !state.missions[index]) return;
    state.phase = 'configuring';
    state.mission = state.missions[index];
    state.bridgeMissionId = state.mission.id + ':' + (++state.missionSerial);
    state.selectionRevision = -1;
    state.atoms = []; state.bonds = [];
    ui['mission-select'].value = String(index);
    clearFeedback(); renderName();
    ui['selection-status'].textContent = 'Δεν έχεις επιλέξει ακόμη κάτι.';
    busy('Ετοιμάζουμε την αποστολή.');
    state.configureRequestId = send('configure', {kind: state.mission.kind, missionId: state.bridgeMissionId});
    watch('Η αποστολή δεν ετοιμάστηκε. Δοκίμασε ξανά.');
  }
  function load(id) {
    if (!engine.starterIds.includes(id)) return;
    state.phase = 'loading';
    state.moleculeId = id;
    state.roundId = 'detective-round-' + (++state.roundSerial);
    state.snapshot = null; state.missions = []; state.mission = null; state.bridgeMissionId = null;
    state.atoms = []; state.bonds = [];
    clearFeedback();
    ui['molecule-select'].value = id;
    ui['mission-select'].replaceChildren();
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
    return data.atoms.every(a => Number.isSafeInteger(a) && knownAtoms.has(a)) && data.bonds.every(b => Number.isSafeInteger(b) && knownBonds.has(b)) && new Set(data.atoms).size === data.atoms.length && new Set(data.bonds).size === data.bonds.length;
  }
  function receive(event) {
    const data = event.data;
    if (state.stopped || event.source !== ui['molecule-viewer'].contentWindow || event.origin !== location.origin || !data || data.channel !== channel || data.session !== state.session || !Number.isSafeInteger(data.requestId) || data.requestId < 0) return;
    if (data.type === 'ready' && state.phase === 'startup') {
      if (!Array.isArray(data.inventory) || engine.starterIds.some(id => !data.inventory.some(item => item.id === id))) { fail('Δεν είναι διαθέσιμα όλα τα μόρια της εξάσκησης.'); return; }
      clearTimeout(deadline);
      const first = engine.starterIds.includes(params.get('molecule')) ? params.get('molecule') : engine.starterIds[0];
      load(first);
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
        state.missions = engine.missions(data.snapshot);
        if (!state.missions.length) throw new Error('No supported missions');
        state.snapshot = data.snapshot;
        const option = Array.from(ui['molecule-select'].options).find(item => item.value === state.moleculeId);
        if (option) option.textContent = state.snapshot.correctName;
        ui['mission-select'].replaceChildren(...state.missions.map((mission, index) => {
          const item = document.createElement('option'); item.value = String(index);
          const piece = state.snapshot.pieces.find(part => part.id === mission.pieceId);
          item.textContent = (familyLabels[mission.family] || 'Στοιχείο στο όνομα') + ' — ' + (piece?.text || '');
          return item;
        }));
        configure(0);
      } catch (error) { fail('Η αποστολή αυτού του μορίου δεν είναι διαθέσιμη. Δοκίμασε ξανά.'); }
      return;
    }
    if (!state.snapshot || data.missionId !== state.bridgeMissionId || data.requestId < state.configureRequestId || data.kind !== state.mission?.kind) return;
    if (data.type === 'configured' && state.phase === 'configuring') {
      if (!validSelection(data)) { fail('Η επιλογή δεν μπόρεσε να ετοιμαστεί. Δοκίμασε ξανά.'); return; }
      clearTimeout(deadline);
      state.phase = 'active';
      ui['viewer-mask'].hidden = true;
      ui['viewer-wrap'].setAttribute('aria-busy', 'false');
      ui['retry-load'].hidden = true;
      status('Παρατήρησε το επισημασμένο συνθετικό και επίλεξε όσα ζητά η αποστολή.');
    }
    if (['configured', 'selection'].includes(data.type) && state.phase === 'active' && validSelection(data) && (data.selectionRevision > state.selectionRevision || (data.selectionRevision === state.selectionRevision && sameSelection(state.atoms, data.atoms) && sameSelection(state.bonds, data.bonds)))) {
      const changed = !sameSelection(state.atoms, data.atoms) || !sameSelection(state.bonds, data.bonds);
      state.selectionRevision = data.selectionRevision;
      state.atoms = data.atoms.slice(); state.bonds = data.bonds.slice();
      if (changed) clearFeedback();
      const count = state.mission.kind === 'atoms' ? state.atoms.length : state.bonds.length;
      ui['selection-status'].textContent = count ? (state.mission.kind === 'atoms' ? 'Επιλεγμένα άτομα: ' : 'Επιλεγμένοι δεσμοί: ') + count : 'Δεν έχεις επιλέξει ακόμη κάτι.';
      if (data.note === 'WRONG_KIND') status(state.mission.kind === 'atoms' ? 'Σε αυτή την αποστολή επίλεξε άτομα, πατώντας στα σύμβολά τους.' : 'Σε αυτή την αποστολή επίλεξε δεσμούς, πατώντας στις γραμμές τους.');
      updateControls();
    }
  }
  function revealFeedback() {
    requestAnimationFrame(() => {
      const bounds = ui.feedback.getBoundingClientRect();
      if (bounds.bottom > innerHeight || bounds.top < 0) ui.feedback.scrollIntoView({block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
    });
  }
  function check() {
    if (state.phase !== 'active') return;
    const result = engine.grade(state.mission, {atoms: state.atoms, bonds: state.bonds});
    state.correct = result.correct;
    const heading = document.createElement('strong');
    const message = document.createElement('p');
    heading.textContent = result.correct ? '✓ Η υπόθεση λύθηκε!' : result.kind === 'empty' ? 'Κάνε πρώτα μια επιλογή' : 'Παρατήρησε ξανά τα στοιχεία';
    message.textContent = result.correct ? state.mission.explanation : result.kind === 'empty' ? 'Επίλεξε στο μοριακό σχέδιο όσα ζητά η αποστολή.' : 'Η επιλογή δεν αντιστοιχεί ακόμη στο επισημασμένο συνθετικό. Μπορείς να τη διορθώσεις και να δοκιμάσεις ξανά.';
    ui.feedback.replaceChildren(heading, message);
    ui.feedback.classList.toggle('success', result.correct);
    ui.feedback.hidden = false;
    updateControls(); revealFeedback();
  }
  function next() {
    if (!state.correct || state.phase !== 'active') return;
    const index = state.missions.indexOf(state.mission);
    if (index + 1 < state.missions.length) configure(index + 1);
    else load(engine.starterIds[(engine.starterIds.indexOf(state.moleculeId) + 1) % engine.starterIds.length]);
    $('mission-title').focus({preventScroll: true});
  }
  function start() {
    if (!engine?.starterIds?.length) { fail('Το παιχνίδι δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.'); return; }
    clearTimeout(deadline);
    state.phase = 'startup'; state.session = crypto.randomUUID().replaceAll('-', ''); state.requestId = 0;
    state.snapshot = null; state.mission = null; state.bridgeMissionId = null;
    state.atoms = []; state.bonds = [];
    clearFeedback(); busy('Φορτώνουμε τον ανεπτυγμένο τύπο.');
    status('Ετοιμάζουμε την πρώτη αποστολή.');
    ui['retry-load'].hidden = true;
    ui['molecule-select'].replaceChildren(...engine.starterIds.map(id => { const option = document.createElement('option'); option.value = id; option.textContent = labels[id] || id; return option; }));
    ui['molecule-viewer'].src = 'molecular-detective-viewer.html?session=' + state.session;
    watch('Η προβολή του μορίου δεν ξεκίνησε. Δοκίμασε ξανά.', 45000);
  }
  function stop() {
    if (state.stopped) return;
    send('stop'); state.stopped = true;
    clearTimeout(deadline); cancelAnimationFrame(resizeFrame);
    window.removeEventListener('message', receive);
  }
  ui['molecule-select'].addEventListener('change', () => load(ui['molecule-select'].value));
  ui['mission-select'].addEventListener('change', () => configure(Number(ui['mission-select'].value)));
  ui['check-answer'].addEventListener('click', check);
  ui['clear-selection'].addEventListener('click', () => { if (state.phase === 'active') send('clear', {missionId: state.bridgeMissionId}); });
  ui['next-mission'].addEventListener('click', next);
  ui['zoom-in'].addEventListener('click', () => { if (state.phase === 'active') send('zoom', {direction: 1, missionId: state.bridgeMissionId}); });
  ui['zoom-out'].addEventListener('click', () => { if (state.phase === 'active') send('zoom', {direction: -1, missionId: state.bridgeMissionId}); });
  ui['retry-load'].addEventListener('click', start);
  window.addEventListener('message', receive);
  window.addEventListener('pagehide', stop, {once: true});
  window.addEventListener('pageshow', event => {
    if (event.persisted && state.stopped) {
      state.stopped = false;
      window.addEventListener('message', receive);
      window.addEventListener('pagehide', stop, {once: true});
      start();
    }
  });
  window.addEventListener('resize', () => {
    if (resizeFrame || state.phase !== 'active') return;
    resizeFrame = requestAnimationFrame(() => { resizeFrame = null; if (!state.stopped && state.phase === 'active') send('resize', {missionId: state.bridgeMissionId}); });
  });
  window.NameleculeMolecularDetective = Object.freeze({snapshot: () => ({phase: state.phase, moleculeId: state.moleculeId, roundId: state.roundId, missionId: state.mission?.id, bridgeMissionId: state.bridgeMissionId, missionIndex: state.missions.indexOf(state.mission), missionCount: state.missions.length, kind: state.mission?.kind, atoms: state.atoms.slice(), bonds: state.bonds.slice(), selectionRevision: state.selectionRevision, correct: state.correct, requestId: state.requestId})});
  start();
})();
