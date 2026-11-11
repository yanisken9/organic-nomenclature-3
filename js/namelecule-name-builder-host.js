/* Same-origin adapter around the native Main55 viewer. Answer state lives in
 * the parent game. No molecule data, naming rules or drawing code is copied. */
(() => {
  'use strict';
  const channel = 'namelecule-name-builder-v1';
  const session = new URLSearchParams(location.search).get('session');
  if (parent === window || !/^[A-Za-z0-9_-]{16,128}$/.test(session || '')) return;
  const root = document.documentElement;
  const fields = {condensed: 'structure2D_Condensed', expanded: 'structure2D_Expanded', skeletal: 'structure2D_Skeletal'};
  const suffix = {condensed: '_2D_Condensed', expanded: '_2D_Expanded', skeletal: '_2D_Skeletal'};
  let stopped = false;
  let started = false;
  let lastId = 0;
  let revision = 0;
  let timer;
  let resizeFrame;
  let current = null;
  let inventory = [];
  let nativeViewerHeights;
  const send = (data, request = current) => {
    if (stopped) return;
    parent.postMessage({channel, session, requestId: request?.requestId ?? 0,
      roundId: request?.roundId ?? null, moleculeId: request?.moleculeId ?? null, ...data}, location.origin);
  };
  function error(code, message, request = current) { send({type: 'error', code, message}, request); }
  function representations(entry) {
    return Object.keys(fields).filter(key => !!entry[fields[key]])
      .concat(entry.file3D || entry.sdf3D ? ['3d'] : []);
  }
  function embeddedViewerHeights(raw) {
    const representation = root.dataset.nameBuilderRepresentation;
    if (representation !== '2d' && representation !== '3d') return nativeViewerHeights(raw);
    // The native Main-page budget reserves page chrome and caps short phone
    // viewports to30% height. A385px embedded frame is also "short", but it
    // contains only one viewer. Supply its actual viewport budget to the
    // unchanged native fitter; molecular scale/geometry still belongs there.
    const height = Math.max(1, Math.floor(root.clientHeight || window.innerHeight));
    return {h2: representation === '2d' ? height : 0,
      h3: representation === '3d' ? height : 0, full: height};
  }
  function fixConvention() {
    window.__mulerStepLang = 'gr';
    window.MULER_QUIET_FETCH = true;
    window.nameHiddenComps = [];
    window.nameEyeEdit = false;
    window.nameExpanded = false;
    window.nameCrossFlag = false;
    substNamingMode = 'school';
    etherNamingMode = 'iupac';
    mainChainMode = 'algorithmic';
    nameAnalysisMode = 'none';
    numberingFlag = false;
    narrateAnalysisFlag = false;
    rotateFlag = false;
  }
  function clearAnswerCues() {
    nameAnalysisMode = 'none';
    numberingFlag = false;
    fClearHighlights();
    // Element symbols remain useful chemical information; chain numbers,
    // selected-atom halos and explanatory echo text are never shown.
    showAtomSymbols3D(false);
    rotate3D();
  }
  function serializeName() {
    const container = document.querySelector('#nameAnalysis .nameCompContainer');
    if (!container) throw new Error('Missing native name components');
    const pieces = [];
    let separatorBefore = '';
    for (const node of container.querySelectorAll('.nameCompBox, .nameCompSpace')) {
      if (node.classList.contains('nameCompSpace')) {
        separatorBefore = ' ';
        continue;
      }
      if (node.classList.contains('comp-hidden')) throw new Error('Hidden name component');
      const text = node.textContent.replace(/\u00a0/g, ' ').trim();
      if (!text) throw new Error('Empty name component');
      pieces.push({text, separatorBefore: pieces.length ? separatorBefore : '', role: node.id});
      separatorBefore = '';
    }
    const correctName = String(currentMolName || '').normalize('NFC');
    const composed = pieces.map(piece => piece.separatorBefore + piece.text).join('').normalize('NFC');
    if (!pieces.length || !correctName || composed !== correctName) throw new Error('Native name roundtrip mismatch');
    return {correctName, pieces};
  }
  function roundData() {
    const entry = nameExamples[selectedMol];
    const data = serializeName();
    return {...data, representations: representations(entry), series: entry.classification.seriesKey,
      parentLength: mainChainAtomsList.length, vocabulary: {roots: nameMainCompList1.slice()}};
  }
  // Read the actual loaded model and graph, rather than considering a canvas
  // or a successful script submission evidence that the requested 3D is ready.
  function modelReady() {
    if (!fJSmolLive()) return false;
    const entry = nameExamples[selectedMol];
    const models = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'modelInfo')?.models || [];
    if (models.length !== 1) return false;
    if (entry.file3D && models[0].file !== new URL(entry.file3D, document.baseURI).href) return false;
    const atoms = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'atomInfo', 'all') || [];
    const bonds = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'bondInfo', 'all') || [];
    if (!atoms.length || atoms.length !== allAtomsTypeList3D.length || bonds.length !== bondList3D.length ||
        atoms.some((atom, i) => atom.atomno !== i + 1 || atom.sym !== allAtomsTypeList3D[i])) return false;
    const edge = (a, b, order) => [Math.min(a, b), Math.max(a, b), order].join(':');
    const expected = new Set(bondList3D.map(bond => edge(...bond)));
    return bonds.every(bond => expected.has(edge(bond.atom1.atomno, bond.atom2.atomno, bond.order)));
  }
  function synchronize(request, type, ticket) {
    const deadline = Date.now() + 20000;
    let markerSent = false;
    function check() {
      if (stopped || ticket !== revision || current !== request) return;
      try {
        let loaded = selectedMol === request.moleculeId && !!document.querySelector('#jsmeNomeclatureSVG svg') && !!currentMolName;
        if (request.representation === '3d') {
          loaded = loaded && modelReady();
          if (loaded) {
            if (!markerSent) {
              markerSent = true;
              clearAnswerCues();
              Jmol.script(jmolAppletNomeclature, 'nameBuilderRevision = ' + ticket + ';');
            }
            loaded = +Jmol.evaluateVar(jmolAppletNomeclature, 'nameBuilderRevision') === ticket;
          }
        }
        if (loaded) {
          const data = roundData();
          if (request.target && data.correctName !== request.target) throw new Error('Name changed on representation switch');
          request.target = data.correctName;
          request.ready = true;
          root.dataset.nameBuilderVisible = 'true';
          send({type, representation: request.representation, ...data}, request);
          return;
        }
        if (Date.now() >= deadline) {
          error('VIEWER_TIMEOUT', 'Η μορφή του μορίου δεν φορτώθηκε. Δοκίμασε άλλη μορφή ή ξανά.', request);
          return;
        }
        timer = setTimeout(check, 50);
      } catch (failure) {
        error('NAME_OR_VIEWER_INVALID', 'Η προβολή ή το όνομα δεν επαληθεύτηκε. Δοκίμασε ξανά.', request);
      }
    }
    // Let native SVG sizing and queued applet rendering settle first.
    timer = setTimeout(check, 60);
  }
  function apply(request, type) {
    clearTimeout(timer);
    const ticket = ++revision;
    current = request;
    request.ready = false;
    root.dataset.nameBuilderVisible = 'false';
    root.dataset.nameBuilderRepresentation = request.representation === '3d' ? '3d' : '2d';
    send({type: 'busy', representation: request.representation}, request);
    try {
      fixConvention();
      const isLoad = type === 'round';
      if (isLoad) {
        selectedMol = request.moleculeId;
        // Every new round begins from the requested original source MOL.
        mode2D = request.representation === '3d' ? 'condensed' : request.representation;
        modeSuffix = suffix[mode2D];
        fSelectMol();
      } else if (request.representation !== '3d') {
        mode2D = request.representation;
        modeSuffix = suffix[mode2D];
        fLoadMol2D();
        fShowNameAnalysis();
      } else if (!modelReady()) {
        fLoadMol3D();
        fFetchAndParse3D();
      }
      clearAnswerCues();
      fResizeViewers();
      synchronize(request, type, ticket);
    } catch (failure) {
      error('LOAD_FAILED', 'Η προβολή του μορίου απέτυχε. Δοκίμασε ξανά.', request);
    }
  }
  function matchesRound(data) {
    return current && data.roundId === current.roundId && data.moleculeId === current.moleculeId;
  }
  function receive(event) {
    const data = event.data;
    if (stopped || event.source !== parent || event.origin !== location.origin || !data ||
        data.channel !== channel || data.session !== session || !Number.isSafeInteger(data.requestId) || data.requestId <= lastId) return;
    lastId = data.requestId;
    const request = {requestId: data.requestId, roundId: data.roundId ?? null, moleculeId: data.moleculeId ?? null};
    if (data.command === 'stop') { send({type: 'stopped'}, request); stop(); return; }
    if (!started) { error('NOT_READY', 'Η προβολή του μορίου ετοιμάζεται.', request); return; }
    if (data.command === 'load' || data.command === 'representation') {
      const validRoundId = (typeof data.roundId === 'string' && !!data.roundId && data.roundId.length <= 128) ||
        (Number.isSafeInteger(data.roundId) && data.roundId > 0);
      if (!validRoundId ||
          typeof data.moleculeId !== 'string' || !inventory.some(item => item.id === data.moleculeId) ||
          !representations(nameExamples[data.moleculeId]).includes(data.representation)) {
        error('INVALID_ROUND', 'Μη διαθέσιμο μόριο ή μορφή.', request); return;
      }
      if (data.command === 'representation' && !matchesRound(data)) {
        error('ROUND_MISMATCH', 'Ο γύρος έχει αλλάξει.', request); return;
      }
      request.representation = data.representation;
      if (data.command === 'representation') request.target = current.target;
      apply(request, data.command === 'load' ? 'round' : 'representation');
      return;
    }
    if (!matchesRound(data) || !current.ready) { error('ROUND_NOT_READY', 'Περίμενε να φορτωθεί ο γύρος.', request); return; }
    try {
      if (data.command === 'zoom' && (data.direction === 1 || data.direction === -1)) {
        if (current.representation === '3d') fZoom3D(data.direction);
        else fZoom2D(data.direction);
        send({type: 'zoom', representation: current.representation}, request);
      } else if (data.command === 'resize') {
        fResizeViewers();
        send({type: 'resize', representation: current.representation}, request);
      } else error('INVALID_COMMAND', 'Μη έγκυρη εντολή προβολής.', request);
    } catch (failure) { error('VIEWER_FAILED', 'Η εντολή προβολής απέτυχε.', request); }
  }
  function resized() {
    if (stopped || !started || resizeFrame) return;
    resizeFrame = requestAnimationFrame(() => {
      resizeFrame = null;
      if (!stopped) fResizeViewers();
    });
  }
  function noMenu(event) {
    if (event.type === 'contextmenu' || event.button === 2) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }
  function stop() {
    if (stopped) return;
    clearTimeout(timer);
    clearTimeout(window.__nameBuilderStartupTimer);
    cancelAnimationFrame(resizeFrame);
    ++revision;
    stopped = true;
    root.dataset.nameBuilderVisible = 'false';
    window.removeEventListener('message', receive);
    window.removeEventListener('resize', resized);
    document.removeEventListener('contextmenu', noMenu, true);
    document.removeEventListener('mousedown', noMenu, true);
    if (nativeViewerHeights && fViewerHeights2D3D === embeddedViewerHeights) fViewerHeights2D3D = nativeViewerHeights;
    try { speechSynthesis.cancel(); Jmol.script(jmolAppletNomeclature, 'spin off;'); } catch (failure) { /* unloading */ }
  }
  function startup() {
    if (stopped) return;
    if (window.__nameBuilderStartupFailed) { stop(); return; }
    try {
      if (typeof jsmeNomeclatureApplet === 'undefined' || !jsmeNomeclatureApplet ||
          typeof nameExamples === 'undefined' || !nameExamples.methane?.classification ||
          !nameMainCompList1.length) { timer = setTimeout(startup, 50); return; }
      fixConvention();
      inventory = Object.keys(nameExamples).map(id => ({id, series: nameExamples[id].classification?.seriesKey,
        carbonCount: nameExamples[id].classification?.carbonCount, representations: representations(nameExamples[id])}));
      if (!inventory.length || inventory.some(item => !item.series || !Number.isInteger(item.carbonCount) || !item.representations.includes('condensed'))) {
        throw new Error('Invalid native molecule inventory');
      }
      // Validate the same real DOM adapter before announcing host readiness.
      fShowNameAnalysis();
      serializeName();
      nativeViewerHeights = fViewerHeights2D3D;
      fViewerHeights2D3D = embeddedViewerHeights;
      clearTimeout(window.__nameBuilderStartupTimer);
      window.__nameBuilderStarted = true;
      started = true;
      send({type: 'ready', inventory}, null);
    } catch (failure) {
      clearTimeout(window.__nameBuilderStartupTimer);
      window.__nameBuilderStarted = true;
      error('STARTUP_FAILED', 'Η προβολή μορίου δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.', null);
      stop();
    }
  }
  window.addEventListener('message', receive);
  window.addEventListener('resize', resized);
  document.addEventListener('contextmenu', noMenu, true);
  document.addEventListener('mousedown', noMenu, true);
  window.addEventListener('pagehide', stop, {once: true});
  // Read-only diagnostics for actual-browser acceptance checks. These use the
  // current native DOM/model, never a fabricated target or a solver shortcut.
  window.NameleculeNameBuilderHost = Object.freeze({serializeName, modelReady,
    snapshot: () => ({started, stopped, lastId, revision, selectedMol,
      representation: current?.representation ?? null, ready: !!current?.ready})});
  startup();
})();
