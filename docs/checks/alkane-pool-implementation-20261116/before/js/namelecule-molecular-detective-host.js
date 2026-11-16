/* Isolated Main56 bridge. Native geometry, hit testing and selection painting
 * stay native; the parent alone owns missions, answers and grading. */
(() => {
  'use strict';
  const channel = 'namelecule-molecular-detective-v1';
  const session = new URLSearchParams(location.search).get('session');
  if (parent === window || !/^[A-Za-z0-9_-]{16,128}$/.test(session || '')) return;
  const root = document.documentElement;
  let started = false, stopped = false, lastId = 0, revision = 0, selectionRevision = 0;
  let timer, resizeFrame, current = null, selectionContext = null, kind = null, missionId = null;
  let inventory = [], muted = 0, clearQueued = false;
  let nativeHeights, nativeToggle, nativeClear;
  const validToken = (value, max = 128) =>
    (typeof value === 'string' && value.length > 0 && value.length <= max) ||
    (Number.isSafeInteger(value) && value > 0);
  const send = (data, request = selectionContext || current) => {
    if (!stopped) parent.postMessage({channel, session, requestId: request?.requestId ?? 0,
      roundId: request?.roundId ?? null, moleculeId: request?.moleculeId ?? null, ...data}, location.origin);
  };
  function error(code, message, request = current, detail) {
    send({type: 'error', code, message, ...(detail ? {detail} : {})}, request);
  }
  function quiet(action) { ++muted; try { return action(); } finally { --muted; } }
  function embeddedHeights() {
    const height = Math.max(1, Math.floor(root.clientHeight || window.innerHeight));
    return {h2: height, h3: 0, full: height};
  }
  function fixConvention() {
    window.__mulerStepLang = 'gr';
    window.MULER_QUIET_FETCH = true;
    window.nameHiddenComps = [];
    window.nameEyeEdit = false;
    window.nameExpanded = false;
    window.nameCrossFlag = false;
    window.nameExplainAll = false;
    window.MulerQuizTarget = null;
    window.MulerSelectPurpose = 'free';
    substNamingMode = 'school';
    etherNamingMode = 'iupac';
    mainChainMode = 'algorithmic';
    nameAnalysisMode = 'none';
    numberingFlag = false;
    narrateAnalysisFlag = false;
    rotateFlag = false;
  }
  function serializeName() {
    const container = document.querySelector('#nameAnalysis .nameCompContainer');
    if (!container) throw new Error('Missing native name components');
    const pieces = [];
    let separatorBefore = '';
    for (const node of container.querySelectorAll('.nameCompBox, .nameCompSpace')) {
      if (node.classList.contains('nameCompSpace')) { separatorBefore = ' '; continue; }
      if (node.classList.contains('comp-hidden')) throw new Error('Hidden native name component');
      const text = node.textContent.replace(/\u00a0/g, ' ').trim().normalize('NFC');
      if (!text || !node.id) throw new Error('Empty native name component');
      pieces.push({id: node.id, text, separatorBefore: pieces.length ? separatorBefore : '',
        mode: fNameAnalysisModeForBoxId(node.id)});
      separatorBefore = '';
    }
    const correctName = String(currentMolName || '').normalize('NFC');
    const composed = pieces.map(piece => piece.separatorBefore + piece.text).join('').normalize('NFC');
    if (!pieces.length || !correctName || composed !== correctName) throw new Error('Native name roundtrip mismatch');
    return {correctName, pieces};
  }
  const element = value => String(value).replace(/^\[([A-Z][a-z]?)\]$/, '$1');
  const sameBond = (left, right) => left[2] === right[2] &&
    ((left[0] === right[0] && left[1] === right[1]) || (left[0] === right[1] && left[1] === right[0]));
  function actualGraph() {
    const source = fParseMolV2000(nameExamples[selectedMol].structure2D_Expanded);
    const loaded = fParseMolV2000(jsmeNomeclatureApplet.molFile());
    if (!source || !loaded || source.atoms.length !== allAtomsTypeList.length ||
        loaded.atoms.length !== allAtomsTypeList.length || source.bonds.length !== bondList.length ||
        loaded.bonds.length !== bondList.length) throw new Error('Expanded graph size mismatch');
    const atoms = allAtomsTypeList.map((raw, index) => {
      const native = jsmeNomeclatureApplet.getAtom(0, index + 1).label;
      if (raw !== native || element(source.atoms[index].el) !== raw || element(loaded.atoms[index].el) !== raw)
        throw new Error('Expanded atom identity mismatch');
      return {id: index + 1, element: raw};
    });
    const bonds = bondList.map((bond, index) => {
      const native = jsmeNomeclatureApplet.getBond(0, index + 1);
      if (!sameBond(bond, [native.atoms[0], native.atoms[1], native.order]) ||
          !sameBond(bond, source.bonds[index]) || !sameBond(bond, loaded.bonds[index]))
        throw new Error('Expanded bond identity mismatch');
      return {id: index + 1, a: bond[0], b: bond[1], order: bond[2]};
    });
    return {atoms, bonds};
  }
  function getSnapshot() {
    if (!current?.ready || selectedMol !== current.moleculeId || mode2D !== 'expanded')
      throw new Error('Current expanded round is not ready');
    const classification = nameExamples[selectedMol].classification;
    return {moleculeId: selectedMol, ...serializeName(), ...actualGraph(),
      chemicalClass: classification.chemicalClass, series: classification.seriesKey};
  }
  function pickGeometryReady(graph) {
    const svg = document.querySelector('#jsmeNomeclatureSVG svg');
    const host = document.getElementById('jsmeNomeclatureSVG');
    if (!svg || !host || host.clientWidth <= 0 || host.clientHeight <= 0 || !svg.getScreenCTM()) return false;
    const geom = fMulerSelectGeom();
    if (!geom || !(geom.med > 0) || !geom.groups || geom.groups.length !== graph.bonds.length) return false;
    const bondIds = new Set();
    for (const group of geom.groups) {
      if (!Number.isInteger(group.bond) || group.bond < 0 || group.bond >= graph.bonds.length ||
          !group.lines?.length || group.lines.some(line =>
            ![line.x1, line.y1, line.x2, line.y2].every(Number.isFinite))) return false;
      bondIds.add(group.bond + 1);
    }
    const atomIds = new Set((geom.anchors || []).filter(anchor =>
      anchor.w > 0 && anchor.h > 0 && Number.isInteger(anchor.atom) &&
      [anchor.x, anchor.y, anchor.w, anchor.h].every(Number.isFinite)).map(anchor => anchor.atom + 1));
    for (const atom of geom.vassign || []) if (Number.isInteger(atom) && atom >= 0) atomIds.add(atom + 1);
    return bondIds.size === graph.bonds.length && graph.atoms.every(atom => atomIds.has(atom.id));
  }
  function matchesRound(data) {
    return current && data.roundId === current.roundId && data.moleculeId === current.moleculeId;
  }
  function activeMission() {
    return !stopped && current?.ready && selectedMol === current.moleculeId && mode2D === 'expanded' &&
      !!kind && missionId !== null && !!selectionContext;
  }
  function selected() {
    const state = fMulerSelectState();
    const atoms = state.atoms2D.slice().sort((a, b) => a - b);
    const bonds = state.bonds2D.slice().sort((a, b) => a - b);
    if (atoms.some(id => !Number.isInteger(id) || id < 1 || id > allAtomsTypeList.length) ||
        bonds.some(id => !Number.isInteger(id) || id < 1 || id > bondList.length) ||
        new Set(atoms).size !== atoms.length || new Set(bonds).size !== bonds.length ||
        (kind === 'atoms' && bonds.length) || (kind === 'bonds' && atoms.length))
      throw new Error('Invalid native selection');
    return {atoms, bonds};
  }
  function sendSelection(type = 'selection', request = selectionContext, extra = {}) {
    if (!activeMission()) return;
    send({type, ...selected(), selectionRevision: ++selectionRevision, kind, missionId, ...extra}, request);
  }
  function observeSelection(extra = {}, isClear = false) {
    if (muted || !activeMission()) return;
    const ticket = revision, mission = missionId, request = selectionContext;
    if (isClear) clearQueued = true;
    // Run after the native click/Escape listener has repainted the actual SVG.
    queueMicrotask(() => {
      if (isClear) clearQueued = false;
      if (ticket !== revision || mission !== missionId || !activeMission()) return;
      try { sendSelection('selection', request, extra); }
      catch (failure) { error('SELECTION_INVALID', 'Η επιλογή δεν επαληθεύτηκε.', request, failure.message); }
    });
  }
  function restrictedToggle(pick) {
    if (!activeMission()) return;
    fixConvention();
    const allowed = kind === 'atoms' ? pick?.kind === 'atom' : pick?.kind === 'bond';
    if (!allowed) { observeSelection({note: 'WRONG_KIND'}); return; }
    const id = kind === 'atoms' ? pick.atom : pick.bond;
    const max = kind === 'atoms' ? allAtomsTypeList.length : bondList.length;
    if (!Number.isInteger(id) || id < 1 || id > max) return;
    nativeToggle(pick);
    observeSelection();
  }
  function observedClear() {
    nativeClear();
    observeSelection({}, true);
  }
  function paintSelection() { fMulerSelectRepaint(); fUpdateSVG(); }
  function synchronize(request, ticket) {
    const deadline = Date.now() + 20000;
    function check() {
      if (stopped || ticket !== revision || current !== request) return;
      try {
        if (selectedMol === request.moleculeId && mode2D !== 'expanded') throw new Error('Expanded mode changed');
        if (selectedMol === request.moleculeId && mode2D === 'expanded' && currentMolName &&
            document.querySelector('#jsmeNomeclatureSVG svg')) {
          const graph = actualGraph();
          const data = serializeName();
          if (pickGeometryReady(graph)) {
            const classification = nameExamples[selectedMol].classification;
            if (!classification?.chemicalClass || !classification.seriesKey) throw new Error('Missing native classification');
            request.ready = true;
            request.snapshot = {moleculeId: selectedMol, ...data, ...graph,
              chemicalClass: classification.chemicalClass, series: classification.seriesKey};
            root.dataset.molecularDetectiveVisible = 'true';
            send({type: 'round', snapshot: request.snapshot}, request);
            return;
          }
        }
        if (Date.now() >= deadline) {
          error('VIEWER_TIMEOUT', 'Ο ανεπτυγμένος τύπος δεν φορτώθηκε. Δοκίμασε ξανά.', request);
          return;
        }
        timer = setTimeout(check, 50);
      } catch (failure) {
        error('NAME_OR_VIEWER_INVALID', 'Η προβολή ή το όνομα δεν επαληθεύτηκε. Δοκίμασε ξανά.', request, failure.message);
      }
    }
    timer = setTimeout(check, 60);
  }
  function load(request) {
    clearTimeout(timer);
    const ticket = ++revision;
    current = request;
    selectionContext = null;
    kind = missionId = null;
    current.ready = false;
    root.dataset.molecularDetectiveVisible = 'false';
    send({type: 'busy'}, request);
    try {
      quiet(() => {
        fixConvention();
        const state = fMulerSelectState();
        state.active = false;
        fMulerSelectClear();
        selectedMol = request.moleculeId;
        mode2D = 'expanded';
        modeSuffix = '_2D_Expanded';
        fSelectMol();
        fixConvention();
        fMulerSelectClear();
        fClearHighlights();
        fResizeViewers();
      });
      synchronize(request, ticket);
    } catch (failure) {
      error('LOAD_FAILED', 'Η προβολή του μορίου απέτυχε. Δοκίμασε ξανά.', request, failure.message);
    }
  }
  function receive(event) {
    const data = event.data;
    if (stopped || event.source !== parent || event.origin !== location.origin || !data ||
        data.channel !== channel || data.session !== session || !Number.isSafeInteger(data.requestId) ||
        data.requestId <= lastId) return;
    lastId = data.requestId;
    const request = {requestId: data.requestId, roundId: data.roundId ?? null, moleculeId: data.moleculeId ?? null};
    const command = data.command || data.type;
    if (command === 'stop') { send({type: 'stopped'}, request); stop(); return; }
    if (!started) { error('NOT_READY', 'Η προβολή του μορίου ετοιμάζεται.', request); return; }
    if (command === 'load') {
      if (!validToken(data.roundId) || typeof data.moleculeId !== 'string' || !inventory.some(item => item.id === data.moleculeId)) {
        error('INVALID_ROUND', 'Μη διαθέσιμο μόριο.', request); return;
      }
      load(request);
      return;
    }
    if (!matchesRound(data) || !current.ready) { error('ROUND_NOT_READY', 'Ο γύρος έχει αλλάξει ή δεν είναι έτοιμος.', request); return; }
    try {
      if (command === 'configure') {
        if (!['atoms', 'bonds'].includes(data.kind) || !validToken(data.missionId, 256)) {
          error('INVALID_MISSION', 'Μη έγκυρη αποστολή.', request); return;
        }
        ++revision;
        kind = data.kind;
        missionId = data.missionId;
        selectionContext = request;
        quiet(() => {
          fixConvention();
          fMulerSelectClear();
          fMulerSelectState().active = true;
          document.getElementById('jsmeNomeclatureSVG').classList.add('selecting');
          paintSelection();
        });
        sendSelection('configured', request);
        return;
      }
      if (!activeMission()) { error('MISSION_NOT_READY', 'Η αποστολή δεν είναι έτοιμη.', request); return; }
      if (data.missionId !== undefined && data.missionId !== missionId) return;
      selectionContext = request;
      if (command === 'clear') {
        quiet(() => { fMulerSelectClear(); paintSelection(); });
        sendSelection('selection', request, {action: 'clear'});
      } else if (command === 'zoom' && (data.direction === 1 || data.direction === -1)) {
        fZoom2D(data.direction);
        sendSelection('zoom', request);
      } else if (command === 'resize') {
        fResizeViewers();
        sendSelection('resize', request);
      } else error('INVALID_COMMAND', 'Μη έγκυρη εντολή προβολής.', request);
    } catch (failure) {
      error('VIEWER_FAILED', 'Η εντολή προβολής απέτυχε.', request, failure.message);
    }
  }
  function resized() {
    if (stopped || !started || resizeFrame) return;
    resizeFrame = requestAnimationFrame(() => {
      resizeFrame = null;
      if (stopped) return;
      try { fResizeViewers(); }
      catch (failure) { error('RESIZE_FAILED', 'Η προβολή δεν προσαρμόστηκε.', current, failure.message); }
    });
  }
  function escaped(event) {
    const target = event.target;
    if (event.key !== 'Escape' || !activeMission() || target?.isContentEditable ||
        /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName || '')) return;
    if (!clearQueued) observeSelection({}, true);
  }
  function noMenu(event) {
    if (event.type === 'contextmenu' || event.button === 2) { event.preventDefault(); event.stopImmediatePropagation(); }
  }
  function stop() {
    if (stopped) return;
    clearTimeout(timer);
    clearTimeout(window.__molecularDetectiveStartupTimer);
    cancelAnimationFrame(resizeFrame);
    ++revision;
    stopped = true;
    root.dataset.molecularDetectiveVisible = 'false';
    try { fMulerSelectState().active = false; } catch (failure) { /* unloading */ }
    window.removeEventListener('message', receive);
    window.removeEventListener('resize', resized);
    document.removeEventListener('keydown', escaped);
    document.removeEventListener('contextmenu', noMenu, true);
    document.removeEventListener('mousedown', noMenu, true);
    if (nativeHeights && fViewerHeights2D3D === embeddedHeights) fViewerHeights2D3D = nativeHeights;
    if (nativeToggle && fMulerSelectToggle === restrictedToggle) fMulerSelectToggle = nativeToggle;
    if (nativeClear && fMulerSelectClear === observedClear) fMulerSelectClear = nativeClear;
    try { speechSynthesis.cancel(); Jmol.script(jmolAppletNomeclature, 'spin off;'); } catch (failure) { /* unloading */ }
  }
  function startup() {
    if (stopped) return;
    if (window.__molecularDetectiveStartupFailed) { stop(); return; }
    try {
      if (typeof jsmeNomeclatureApplet === 'undefined' || !jsmeNomeclatureApplet ||
          typeof nameExamples === 'undefined' || !nameExamples.methane?.classification ||
          !nameMainCompList1.length) { timer = setTimeout(startup, 50); return; }
      fixConvention();
      inventory = Object.keys(nameExamples).filter(id => !!nameExamples[id].structure2D_Expanded).map(id => ({id}));
      if (!inventory.length) throw new Error('Empty expanded inventory');
      fShowNameAnalysis();
      serializeName();
      nativeHeights = fViewerHeights2D3D;
      fViewerHeights2D3D = embeddedHeights;
      nativeToggle = fMulerSelectToggle;
      nativeClear = fMulerSelectClear;
      fMulerSelectToggle = restrictedToggle;
      fMulerSelectClear = observedClear;
      clearTimeout(window.__molecularDetectiveStartupTimer);
      window.__molecularDetectiveStarted = true;
      started = true;
      send({type: 'ready', inventory}, null);
    } catch (failure) {
      clearTimeout(window.__molecularDetectiveStartupTimer);
      window.__molecularDetectiveStarted = true;
      error('STARTUP_FAILED', 'Η προβολή μορίου δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.', null, failure.message);
      stop();
    }
  }
  window.addEventListener('message', receive);
  window.addEventListener('resize', resized);
  document.addEventListener('keydown', escaped);
  document.addEventListener('contextmenu', noMenu, true);
  document.addEventListener('mousedown', noMenu, true);
  window.addEventListener('pagehide', stop, {once: true});
  window.NameleculeMolecularDetectiveHost = Object.freeze({serializeName, getSnapshot,
    snapshot: () => ({started, stopped, lastId, revision, selectionRevision, selectedMol,
      ready: !!current?.ready, roundId: current?.roundId ?? null, moleculeId: current?.moleculeId ?? null,
      kind, missionId, mode: typeof mode2D === 'undefined' ? null : mode2D,
      selection: activeMission() ? selected() : {atoms: [], bonds: []}})});
  startup();
})();
