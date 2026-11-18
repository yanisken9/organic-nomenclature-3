/* Name assembly. This page owns its native viewer; an optional lesson parent
 * owns the saved tile evidence and completion navigation. */
(function () {
  'use strict';
  const Engine = window.NameleculeNameBuilderEngine;
  const Levels = window.NameleculeGameLevels;
  const channel = 'namelecule-name-builder-v1';
  const lessonChannel = 'namelecule-builder-lesson-v1';
  const lessonSession = new URLSearchParams(location.search).get('lessonSession');
  const lesson = parent !== window && /^[A-Za-z0-9_-]{16,128}$/.test(lessonSession || '')
    ? { current: null, lastId: 0, resizeFrame: null, lastHeight: null, observer: null } : null;
  const lessonMolecules = ['methane', 'ethane', 'propane', 'butane', 'pentane',
    'methyl_2_pentane', 'dimethyl_2_3_butane', 'ethyl_3_dimethyl_2_5_hexane'];
  const $ = id => document.getElementById(id);
  const frame = $('molecule-viewer');
  const nonce = Array.from(crypto.getRandomValues(new Uint8Array(18)), b => b.toString(16).padStart(2, '0')).join('');
  const forms = ['condensed', 'expanded', 'skeletal', '3d'];
  const practice = { category: 'alkanes', level: null, slots: new Map(), controls: null };
  const state = { inventory: [], round: null, bank: [], answer: [], selected: null,
    representation: '', busy: true, failed: false, solved: false, stopped: false, roundNumber: 0,
    pending: null, nextId: 0, retry: null, touch: null, suppressClickUntil: 0, attempts: 0, submitted: false };
  const Viewport = window.NameleculeGameViewport;
  const viewportEnabled = !!Viewport && (!lesson || new URLSearchParams(location.search).get('viewport') === '1');
  const inlineResults = !!lesson && viewportEnabled;
  let viewportUI = null;
  const scrolling = { frame: null, moving: false };
  const representationButtons = Array.from(document.querySelectorAll('[data-representation]'));
  const startupTimer = setTimeout(() => fail('Η προβολή του μορίου άργησε να ξεκινήσει. Μπορείς να δοκιμάσεις ξανά.', () => location.reload()), 45000);

  function nativeFormulaQuery() {
    if (!lesson || !viewportEnabled) return '';
    const value = getComputedStyle($('game')).getPropertyValue('--nl-game-formula-px').trim();
    const pixels = Number(value);
    return /^[0-9]+(?:[.][0-9]+)?$/.test(value) && Number.isFinite(pixels) && pixels >= 20 && pixels <= 36
      ? '&nlFormulaPx=' + encodeURIComponent(pixels) : '';
  }
  function snapshot() {
    return { answer: state.answer.slice(), selected: state.selected, attempts: state.attempts, submitted: state.submitted };
  }
  function postLesson(type, data, current = lesson?.current) {
    if (!lesson || state.stopped || (type !== 'ready' && !current)) return;
    const identity = current && type !== 'ready' ? { requestId: current.requestId, attemptId: current.attemptId, moleculeId: current.moleculeId,
      ...(current.context ? { context: current.context } : {}) } : {};
    parent.postMessage({ channel: lessonChannel, session: lessonSession, ...identity, type, ...data }, location.origin);
  }
  function publishSnapshot() {
    if (lesson?.current?.ready) postLesson('state', { state: snapshot() });
    scheduleSize();
  }
  function scheduleSize() {
    if (viewportEnabled) { viewportUI?.refresh(); return; }
    if (!lesson || lesson.resizeFrame !== null || state.stopped) return;
    lesson.resizeFrame = requestAnimationFrame(() => {
      lesson.resizeFrame = null;
      if (!lesson.current?.ready || state.stopped) return;
      // Body bounds follow content. documentElement.scrollHeight would include
      // the already expanded iframe viewport and can create a sizing loop.
      const height = Math.max(80, Math.min(8000, Math.ceil(document.body.getBoundingClientRect().height)));
      if (Number.isFinite(height) && height !== lesson.lastHeight) {
        lesson.lastHeight = height;
        postLesson('resize', { height });
      }
    });
  }
  function stopLocalReveal() {
    if (scrolling.frame !== null) cancelAnimationFrame(scrolling.frame);
    scrolling.frame = null;
    if (scrolling.moving) {
      const top = scrollY, left = scrollX;
      const max = Math.max(0, (document.scrollingElement || document.documentElement).scrollHeight - innerHeight);
      // A same-position write can leave a native animation running. Retarget
      // and restore in one turn so cancellation does not leave a position change.
      const adjacent = top < max ? Math.min(max, top + 1) : Math.max(0, top - 1);
      if (adjacent !== top) window.scrollTo({ top: adjacent, left, behavior: 'instant' });
      window.scrollTo({ top, left, behavior: 'instant' });
    }
    scrolling.moving = false;
  }
  function interruptReveal() {
    if (viewportEnabled) return;
    stopLocalReveal();
    if (lesson?.current?.ready) postLesson('scroll-interrupt', {});
  }
  function revealRange(purpose, region) {
    if (viewportEnabled) { viewportUI?.refresh(); return; }
    stopLocalReveal();
    scheduleSize();
    const current = lesson?.current;
    const round = state.round;
    // Let the content-height message reach the lesson before its range request.
    scrolling.frame = requestAnimationFrame(() => {
      scrolling.frame = requestAnimationFrame(() => {
        scrolling.frame = null;
        if (state.stopped || state.busy || state.failed || state.touch || !round || round !== state.round ||
            (lesson && (!current?.ready || current !== lesson.current))) return;
        const feedback = purpose === 'feedback';
        const start = region || (feedback ? $('feedback') : $('answer-zone'));
        const end = region || (feedback ? start : $('check-answer'));
        if (start.hidden || !start.isConnected || !end.isConnected) return;
        const first = start.getBoundingClientRect(), last = end.getBoundingClientRect();
        if (first.height <= 0 || last.height <= 0) return;
        if (lesson) {
          const body = document.body.getBoundingClientRect();
          postLesson('reveal', { purpose, startY: Math.max(0, first.top - body.top), endY: Math.max(0, last.bottom - body.top) });
          return;
        }
        const top = 12, bottom = innerHeight - 12;
        if (bottom <= top || (first.top >= top && last.bottom <= bottom)) return;
        // An oversized construction area starts at the answer and nearby bank;
        // never jump past the available pieces to a button at its far end.
        const delta = last.bottom - first.top > bottom - top || first.top < top ? first.top - top : last.bottom - bottom;
        const destination = Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, scrollY + delta));
        if (Math.abs(destination - scrollY) < 1) return;
        const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
        scrolling.moving = !reduced;
        window.scrollTo({ top: destination, left: scrollX, behavior: reduced ? 'instant' : 'smooth' });
      });
    });
  }
  function revealFeedback() { revealRange('feedback'); }
  function validateLessonContext(data) {
    if (!Object.prototype.hasOwnProperty.call(data, 'context')) return null;
    if (!Levels) throw new Error('Δεν φορτώθηκε η πολιτική των επιπέδων.');
    const context = Levels.validateContext(data.context);
    if (context.seed === null || !Levels.contextIds(context).includes(data.moleculeId)) throw new Error('Το μόριο δεν ανήκει στην προσπάθεια αυτού του επιπέδου.');
    return context;
  }
  function validateLessonLoad(data) {
    const context = validateLessonContext(data);
    const allowedIds = context ? Levels.contextIds(context) : lessonMolecules;
    if (typeof data.attemptId !== 'string' || !data.attemptId || data.attemptId.length > 160 ||
        !allowedIds.includes(data.moleculeId) || typeof data.bankSeed !== 'string' || !data.bankSeed || data.bankSeed.length > 256 ||
        typeof data.explanation !== 'string' || data.explanation.length > 8000) throw new Error('Μη έγκυρα δεδομένα άσκησης.');
    const round = Engine.validateRound(data.round);
    const rootCount = context?.source === 'enriched' ? (context.level < 3 ? 5 : 6) : lessonMolecules.indexOf(data.moleculeId) < 5 ? 5 : 6;
    if (round.moleculeId !== data.moleculeId || round.roundId.length > 128 || round.series !== 'alkanes' ||
        round.parentLength > rootCount || round.vocabulary.roots.length !== rootCount || !round.representations.includes('condensed')) {
      throw new Error('Το μόριο δεν αντιστοιχεί σε αυτή την άσκηση.');
    }
    const bank = Engine.createBank(round, { seed: data.bankSeed });
    const initial = data.initialState;
    if (!initial || !Array.isArray(initial.answer) || initial.answer.length > bank.length ||
        new Set(initial.answer).size !== initial.answer.length || initial.answer.some(id => !bank.some(tile => tile.id === id)) ||
        !(initial.selected === null || initial.answer.includes(initial.selected)) ||
        !Number.isSafeInteger(initial.attempts) || initial.attempts < 0 || typeof initial.submitted !== 'boolean' ||
        (initial.submitted && (!initial.attempts || !initial.answer.length))) throw new Error('Η αποθηκευμένη προσπάθεια δεν επαληθεύτηκε.');
    return { requestId: data.requestId, attemptId: data.attemptId, moleculeId: data.moleculeId, round,
      ...(context ? { context } : {}), bankSeed: data.bankSeed, explanation: data.explanation,
      initialState: { answer: initial.answer.slice(), selected: initial.selected, attempts: initial.attempts, submitted: initial.submitted }, ready: false };
  }
  function verifyLessonRound(actual, canonical) {
    if (actual.correctName !== canonical.correctName || actual.series !== canonical.series || actual.parentLength !== canonical.parentLength ||
        actual.pieces.length !== canonical.pieces.length || actual.pieces.some((piece, index) =>
          piece.text !== canonical.pieces[index].text || piece.separatorBefore !== canonical.pieces[index].separatorBefore) ||
        canonical.vocabulary.roots.some((root, index) => root !== actual.vocabulary.roots[index]) ||
        canonical.representations.length !== actual.representations.length ||
        canonical.representations.some(mode => !actual.representations.includes(mode))) {
      throw new Error('Το όνομα της προβολής δεν αντιστοιχεί στην επαληθευμένη άσκηση.');
    }
  }
  function receiveLesson(event) {
    if (!lesson || state.stopped || event.origin !== location.origin || event.source !== parent) return;
    const data = event.data;
    if (data?.command === 'viewport') {
      if (viewportEnabled && validViewportMessage(data)) {
        Viewport.acceptViewport($('game'), data); viewportUI?.refresh();
      }
      return;
    }
    if (!data || data.channel !== lessonChannel || data.session !== lessonSession || data.command !== 'load' ||
        !Number.isSafeInteger(data.requestId) || data.requestId <= lesson.lastId) return;
    lesson.lastId = data.requestId;
    try {
      const current = validateLessonLoad(data);
      lesson.current = current; lesson.lastHeight = null;
      if (state.inventory.length) loadRound(current.moleculeId, current);
    } catch (error) {
      if (typeof data.attemptId === 'string' && data.attemptId.length <= 160) {
        let context = null; try { context = validateLessonContext(data); } catch (_) { /* Reject unknown context without legacy fallback. */ }
        postLesson('error', { message: error.message }, { ...data, context });
      }
    }
  }
  function validViewportMessage(data) {
    const current = lesson?.current;
    if (!current || data.channel !== lessonChannel || data.session !== lessonSession ||
        data.requestId !== current.requestId || data.attemptId !== current.attemptId || data.moleculeId !== current.moleculeId ||
        !Number.isFinite(data.height) || data.height <= 0 || !Number.isFinite(data.width) || data.width <= 0) return false;
    try {
      const context = validateLessonContext(data);
      return current.context ? !!context && Levels.contextKey(context) === Levels.contextKey(current.context) : context === null;
    } catch (_) { return false; }
  }
  function builderRegionEnvelope(round, bank, width, availableHeight, metrics) {
    const compact = width < 850 || availableHeight < 440;
    const columns = compact ? 3 : 4, rows = Math.ceil(bank.length / columns);
    // Two complete natural tile rows are a usable bank. Longer banks retain
    // their existing local pager, whose row is reserved before any selection.
    const bankHeight = 28 + 12 + Math.min(2, rows) * metrics.tile + Math.max(0, Math.min(2, rows) - 1) * 5 + (rows > 2 ? 40 : 0);
    const answerWidth = Math.max(80, compact ? width - 32 : (width - 44) * 1.1 / 2.9 - 16);
    const allPiecesWidth = bank.reduce((total, tile) => total + tile.text.length * metrics.tileFont * .65 + 18, 0);
    const answerHeight = 64 + (allPiecesWidth > answerWidth ? 40 : 0);
    const controls = metrics.control * (compact && width < 600 ? 2 : 1);
    const editor = 38 + 16 + answerHeight + controls + metrics.check + 24 + 2 + (compact ? 0 : bankHeight);
    const bankView = 38 + 16 + answerHeight + bankHeight + 6 + 2;
    // Include all representations up front, including a usable 3D surface and
    // two rows of representation controls in the narrower result-side pane.
    const extraNamePieces = Math.max(0, round.pieces.length - 3);
    const diagram = 220 + Math.min(2, extraNamePieces) * 16 + (round.parentLength > 5 ? 12 : 0);
    const molecule = 46 + diagram + 88 + 2;
    const inlineResult = compact && width < 850 ? 118 + 7 : 0;
    return Math.ceil(Math.max(editor + inlineResult, compact ? bankView : 0, molecule, 220));
  }
  function createViewportUI() {
    const root = $('game'), pagers = [], buttons = new Map();
    root.classList.toggle('nl-inline-results', inlineResults);
    let mounted = null, feedbackName = null, inlineFitFrame = null;
    const nav = document.createElement('nav'); nav.className = 'builder-view-nav'; nav.setAttribute('aria-label', 'Προβολές άσκησης');
    const stages = [['editing', 'Σύνθεση'], ['bank', 'Συνθετικά'], ['molecule', 'Μόριο'], ['name', 'Όνομα'], ['help', 'Οδηγίες'], ['feedback', 'Σχόλιο']];
    stages.forEach(([key, label]) => {
      if (inlineResults && key === 'feedback') return;
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.dataset.view = key; button.addEventListener('click', () => stage(key)); nav.append(button); buttons.set(key, button);
    });
    root.querySelector('.workspace').before(nav);
    function section(className) { const el = document.createElement('section'); el.className = className; root.append(el); return el; }
    const help = section('builder-help-stage'), name = section('builder-name-stage'), feedback = section('builder-feedback-stage');
    help.setAttribute('aria-label', 'Οδηγίες χειρισμού'); help.append($('answer-help')); $('answer-help').open = true;
    name.setAttribute('aria-label', 'Επιθεώρηση ονόματος'); name.append($('candidate'));
    feedback.setAttribute('aria-label', 'Ανατροφοδότηση'); feedback.append($('feedback'));
    if (inlineResults) {
      feedback.classList.add('nl-inline-result');
      root.querySelector('.workspace').append(feedback);
      feedback.hidden = true;
    }
    const actions = document.createElement('div'); actions.className = 'builder-feedback-actions';
    const back = document.createElement('button'); back.type = 'button'; back.className = 'secondary'; back.textContent = 'Επιστροφή στη σύνθεση';
    back.addEventListener('click', () => stage('editing')); actions.append(back);
    if (!inlineResults) feedback.append(actions);
    const nextHome = $('next-molecule').parentNode;
    pagers.push(Viewport.pager($('answer-zone'), { axis: 'x', label: 'Συνθετικά του ονόματος' }));
    pagers.push(Viewport.pager($('bank-zone'), { axis: 'y', label: 'Διαθέσιμα συνθετικά' }));
    pagers.push(Viewport.pager($('candidate-name'), { axis: 'x', label: 'Πλήρες όνομα' }));
    pagers.push(Viewport.pager($('answer-help').querySelector('.helper-methods'), { axis: 'y', label: 'Οδηγίες' }));
    pagers.push(Viewport.pager($('feedback'), { axis: 'y', label: 'Ανατροφοδότηση' }));
    function fitInlineWorkspace() {
      if (!inlineResults || !root.isConnected || !state.round || state.busy || state.failed || root.dataset.builderView !== 'editing' ||
          root.classList.contains('builder-compact')) return;
      const panel = root.querySelector('.answer-panel'), content = root.querySelector('.answer-content');
      const panelStyle = getComputedStyle(panel), contentStyle = getComputedStyle(content);
      const bankStyle = getComputedStyle($('bank-zone'));
      const pixels = value => parseFloat(value) || 0;
      const bottom = panel.getBoundingClientRect().bottom - pixels(panelStyle.borderBottomWidth) - pixels(contentStyle.paddingBottom);
      const tiles = Array.from($('bank-tiles').querySelectorAll('.tile-button'));
      const tileHeight = Math.max(44, ...tiles.map(tile => tile.getBoundingClientRect().height));
      const bankHeight = $('bank-zone').clientHeight - pixels(bankStyle.paddingTop) - pixels(bankStyle.paddingBottom);
      if ($('check-answer').getBoundingClientRect().bottom <= bottom + .5 && bankHeight + .5 >= tileHeight) return;
      // Reuse the existing bank/molecule views when the actual editor cannot
      // retain both a full bank row and Check. Keep this choice until resize:
      // hiding the bank changes the measured fit and must not cause a loop.
      root.classList.add('builder-compact', 'builder-height-compact');
      pagers.forEach(pager => pager.refresh()); feedbackName?.refresh(); mounted?.refresh();
    }
    function refresh() {
      pagers.forEach(pager => pager.refresh()); feedbackName?.refresh(); mounted?.refresh();
      if (inlineResults && inlineFitFrame === null) inlineFitFrame = requestAnimationFrame(() => {
        inlineFitFrame = null; fitInlineWorkspace();
      });
    }
    function preferred() {
      const current = lesson?.current;
      if (!inlineResults || !current?.ready || !state.round || state.busy || state.failed || state.stopped) return null;
      const natural = (element, floor) => {
        const style = getComputedStyle(element), px = value => parseFloat(value) || 0;
        const line = px(style.lineHeight) || px(style.fontSize) * 1.25;
        return Math.max(floor, px(style.minHeight), line + px(style.paddingTop) + px(style.paddingBottom) + px(style.borderTopWidth) + px(style.borderBottomWidth));
      };
      const tile = $('bank-tiles').querySelector('.tile-button');
      const metrics = { tile: tile ? natural(tile, 44) : 44, tileFont: tile ? parseFloat(getComputedStyle(tile).fontSize) || 16 : 16,
        control: natural($('remove-tile'), 36), check: natural($('check-answer'), 40) };
      const height = builderRegionEnvelope(state.round, state.bank, root.clientWidth, Viewport.availableHeight(root), metrics);
      const key = ['builder', current.requestId, current.attemptId, current.moleculeId].join(':');
      return Viewport.preferred(root, root.querySelector('.workspace'), height, key, { exclude: [help, name, feedback] });
    }
    function stage(key) {
      if (inlineResults && key === 'feedback') key = root.dataset.builderView || 'editing';
      if (key === 'feedback' && $('feedback').hidden) key = 'editing';
      root.dataset.builderView = key;
      if (inlineResults) {
        feedback.hidden = $('feedback').hidden;
        root.classList.toggle('builder-inline-feedback', !feedback.hidden);
      }
      buttons.forEach((button, view) => { button.setAttribute('aria-pressed', String(view === key)); button.hidden = view === 'feedback' && $('feedback').hidden; });
      if (key === 'feedback') actions.append($('next-molecule')); else nextHome.append($('next-molecule'));
      refresh();
    }
    root.addEventListener('nl-level-stage', event => { root.classList.toggle('builder-choosing', !!event.detail.expanded); refresh(); });
    mounted = Viewport.mount(root, { kind: 'builder', preferred, onDemand(detail) { postLesson('layout-demand', detail); }, onResize({ width, height, availableHeight }) {
      root.classList.remove('builder-height-compact');
      root.classList.toggle('builder-compact', width < 850 || (inlineResults ? availableHeight : height) < 440);
      refresh();
    } });
    root.querySelector('.keyboard-note').textContent = 'Enter: προσθήκη · ← →: μετακίνηση · Delete: αφαίρεση. Για μεγάλα ονόματα χρησιμοποίησε τα κουμπιά σελίδας.';
    stage('editing');
    function clearFeedbackName() { feedbackName?.destroy(); feedbackName = null; }
    return { stage, refresh, clearFeedbackName,
      clearFeedback() {
        clearFeedbackName();
        if (inlineResults) { feedback.hidden = true; root.classList.remove('builder-inline-feedback'); refresh(); }
      },
      feedback(correct) {
        const fullName = $('feedback').querySelector('.single-line-name');
        if (fullName) feedbackName = Viewport.pager(fullName, { axis: 'x', label: 'Σωστό όνομα' });
        if (inlineResults) {
          feedback.hidden = false; root.classList.add('builder-inline-feedback'); refresh();
        } else {
          back.textContent = correct ? 'Επιθεώρηση σύνθεσης' : 'Επιστροφή στη σύνθεση'; stage('feedback');
        }
      }, destroy() {
        if (inlineFitFrame !== null) cancelAnimationFrame(inlineFitFrame);
        feedbackName?.destroy(); pagers.forEach(pager => pager.destroy()); mounted?.destroy();
      } };
  }
  function announce(text) { $('move-announcement').textContent = text; }
  function setStatus(text, error) { $('game-status').textContent = text; $('game-status').classList.toggle('error', !!error); }
  function post(command, data) {
    if (state.stopped) return;
    const requestId = ++state.nextId;
    frame.contentWindow.postMessage({ channel, session: nonce, command, requestId, ...data }, location.origin);
    return requestId;
  }
  function mask(text, failed) {
    $('viewer-mask').hidden = !text;
    $('viewer-message').textContent = text || '';
    $('retry-load').hidden = !failed;
    $('viewer-wrap').setAttribute('aria-busy', text && !failed ? 'true' : 'false');
  }
  function updateControls() {
    const enabled = !!state.round && !state.busy && !state.failed;
    representationButtons.forEach(button => {
      const available = !!state.round && state.round.representations.includes(button.dataset.representation);
      button.disabled = !state.round || state.busy || !available;
      button.setAttribute('aria-pressed', button.dataset.representation === state.representation ? 'true' : 'false');
      button.title = available ? '' : 'Αυτή η απεικόνιση δεν είναι διαθέσιμη για το συγκεκριμένο μόριο.';
    });
    $('zoom-in').disabled = $('zoom-out').disabled = !enabled;
    $('check-answer').disabled = !enabled || !state.answer.length || state.solved;
    $('next-molecule').disabled = !state.inventory.length || state.busy || (!lesson && !practiceSlot());
    document.querySelectorAll('.tile-button').forEach(button => {
      button.disabled = !enabled || state.solved;
      button.draggable = false;
    });
    const selectedIndex = state.answer.indexOf(state.selected);
    $('tile-controls').hidden = selectedIndex < 0 || !enabled || state.solved;
    $('move-before').disabled = selectedIndex <= 0;
    $('move-after').disabled = selectedIndex < 0 || selectedIndex >= state.answer.length - 1;
  }
  function fail(message, retry) {
    state.busy = false; state.failed = true; state.retry = retry || null;
    mask(message, !!retry); setStatus(message, true); updateControls();
    if (lesson?.current) postLesson('error', { message });
    scheduleSize();
  }
  function request(command, payload) {
    if (state.pending) {
      clearTimeout(state.pending.timer);
      state.pending.reject(new Error('superseded'));
      state.pending = null;
    }
    return new Promise((resolve, reject) => {
      const requestId = post(command, payload);
      const timer = setTimeout(() => {
        if (!state.pending || state.pending.requestId !== requestId) return;
        state.pending = null; reject(new Error('Η προβολή δεν ολοκληρώθηκε εγκαίρως.'));
      }, 30000);
      state.pending = { requestId, roundId: payload.roundId, moleculeId: payload.moleculeId,
        expectedType: command === 'load' ? 'round' : 'representation', timer, resolve, reject };
    });
  }
  function validInventory(raw) {
    if (!Array.isArray(raw) || !raw.length || raw.length > 1000) throw new Error('Δεν βρέθηκε έγκυρη βιβλιοθήκη μορίων.');
    const seen = new Set();
    return raw.map(entry => {
      if (!entry || typeof entry.id !== 'string' || !/^[a-zA-Z0-9_]{1,120}$/.test(entry.id) || seen.has(entry.id) ||
          !Array.isArray(entry.representations) || !entry.representations.includes('condensed') ||
          entry.representations.some(form => !forms.includes(form))) throw new Error('Τα δεδομένα της βιβλιοθήκης δεν είναι πλήρη.');
      seen.add(entry.id);
      return { ...entry, representations: [...new Set(entry.representations)] };
    });
  }
  function freshSeed() { return Array.from(crypto.getRandomValues(new Uint32Array(4)), n => n.toString(16).padStart(8, '0')).join(''); }
  function practiceKey() { return practice.category === 'other' ? 'other' : practice.level === null ? null : 'alkanes-' + practice.level; }
  function practiceSlot() { return practice.slots.get(practiceKey()); }
  function savePractice() {
    const slot = practiceSlot();
    if (slot && state.round) slot.saved = { moleculeId: state.round.moleculeId, roundId: state.round.roundId,
      initialState: snapshot(), representation: state.representation };
  }
  function invalidateRound() {
    // Invalidate the previous asynchronous response before clearing its UI.
    state.roundNumber += 1;
    if (state.pending) { clearTimeout(state.pending.timer); state.pending.reject(new Error('superseded')); state.pending = null; }
    stopLocalReveal(); cancelTouch();
  }
  function nextMolecule() { return practiceSlot()?.deck.next(); }
  function selectPractice(selection) {
    if (lesson || state.stopped) return;
    const category = selection.category, level = category === 'other' ? null : selection.level;
    if (category === practice.category && level === practice.level) return;
    savePractice(); invalidateRound();
    practice.category = category; practice.level = level;
    practice.controls.set({ category, selectedLevel: level });
    const key = practiceKey();
    if (!key) {
      state.round = null; state.bank = []; state.answer = []; state.selected = null;
      state.busy = false; state.failed = false; state.solved = false;
      $('feedback').hidden = true; $('candidate').hidden = true;
      render(); mask('Διάλεξε επίπεδο για να ανατεθεί ένα μόριο.');
      setStatus('Διάλεξε επίπεδο για αυτόματη ανάθεση μορίου.'); return;
    }
    if (!practice.slots.has(key)) {
      const ids = state.inventory.map(entry => entry.id);
      const pool = category === 'other' ? ids.filter(id => Levels.levelFor(id) === null) : Levels.poolFor(level, ids);
      practice.slots.set(key, { deck: Levels.createDeck(pool, { seed: freshSeed(), avoid: state.round?.moleculeId }), saved: null });
    }
    const saved = practiceSlot().saved;
    loadRound(saved ? saved.moleculeId : nextMolecule(), null, saved);
  }
  function preparePractice() {
    if (!Levels) throw new Error('Δεν φορτώθηκαν τα επίπεδα του παιχνιδιού. Ανανέωσε τη σελίδα.');
    const ids = state.inventory.map(entry => entry.id);
    if ([1, 2, 3].some(level => Levels.poolFor(level, ids).length !== [5, 4, 5][level - 1])) {
      throw new Error('Η βιβλιοθήκη των 14 αλκανίων δεν είναι πλήρης.');
    }
    practice.controls = Levels.mount($('game-levels'), { compact: viewportEnabled, availableIds: ids, allowedLevels: [1, 2, 3], selectedLevel: null,
      category: 'alkanes', otherCount: ids.filter(id => Levels.levelFor(id) === null).length, onSelect: selectPractice });
    state.busy = false; mask('Διάλεξε επίπεδο για να ανατεθεί ένα μόριο.');
    setStatus('Διάλεξε επίπεδο για αυτόματη ανάθεση μορίου.'); updateControls();
  }
  async function loadRound(moleculeId, controlled = null, saved = null) {
    if (state.stopped || (lesson && controlled !== lesson.current)) return;
    invalidateRound();
    state.busy = true; state.failed = false; state.solved = false;
    state.attempts = 0; state.submitted = false;
    if (controlled) controlled.ready = false;
    state.answer = []; state.selected = null; state.round = null; state.bank = [];
    viewportUI?.clearFeedback(); $('feedback').hidden = true; $('candidate').hidden = true; viewportUI?.stage('editing');
    $('bank-tiles').replaceChildren(); $('answer-tiles').replaceChildren(); $('empty-answer').hidden = false;
    $('answer-zone').scrollLeft = 0; $('candidate-name').scrollLeft = 0;
    mask('Ετοιμάζουμε τη δομή και τα συνθετικά.'); setStatus('Ετοιμάζουμε το επόμενο μόριο.'); updateControls();
    const ticket = state.roundNumber;
    const roundId = controlled ? controlled.round.roundId : saved ? saved.roundId : nonce + '-' + ticket;
    if (!lesson && practiceSlot()) practiceSlot().saved = saved || { moleculeId, roundId, initialState: snapshot(), representation: 'condensed' };
    try {
      const result = await request('load', { moleculeId, roundId, representation: 'condensed' });
      if (state.stopped || ticket !== state.roundNumber || (controlled && controlled !== lesson.current)) return;
      const actual = Engine.validateRound(result);
      if (actual.moleculeId !== moleculeId || actual.roundId !== roundId) throw new Error('Η απόκριση δεν αντιστοιχεί στο μόριο της άσκησης.');
      if (controlled) verifyLessonRound(actual, controlled.round);
      state.round = controlled ? controlled.round : actual;
      state.bank = Engine.createBank(state.round, { seed: controlled ? controlled.bankSeed : roundId });
      const initial = controlled ? controlled.initialState : saved?.initialState;
      if (initial) Object.assign(state, initial, { answer: initial.answer.slice() });
      state.representation = 'condensed'; state.busy = false; state.failed = false;
      mask(''); setStatus('Διάλεξε τα συνθετικά και χτίσε το όνομα.');
      if (state.submitted) showFeedback(Engine.evaluate(state.round, answerTiles()));
      render();
      if (controlled) {
        controlled.ready = true;
        postLesson('loaded', { state: snapshot() }); scheduleSize();
      }
      if (state.submitted) revealFeedback();
      else revealRange('entry');
      if (saved && saved.representation !== 'condensed' && state.round?.representations.includes(saved.representation)) await changeRepresentation(saved.representation);
    } catch (error) {
      if (error.message === 'superseded' || state.stopped || ticket !== state.roundNumber || (controlled && controlled !== lesson.current)) return;
      fail(lesson ? 'Δεν επαληθεύτηκε η προβολή αυτού του μορίου. Δοκίμασε ξανά ή επέστρεψε στην επιλογή παιχνιδιού.'
        : 'Δεν ήταν δυνατή η προετοιμασία αυτού του μορίου. Δοκίμασε ξανά ή διάλεξε «Άλλο μόριο».', () => loadRound(moleculeId, controlled, saved));
    }
  }
  async function changeRepresentation(representation) {
    if (!state.round || state.busy || !state.round.representations.includes(representation)) return;
    const round = state.round;
    state.busy = true; state.failed = false; cancelTouch();
    mask('Αλλάζουμε την απεικόνιση του ίδιου μορίου.'); setStatus('Η σύνθεσή σου διατηρείται.'); updateControls();
    try {
      const result = await request('representation', { roundId: round.roundId, moleculeId: round.moleculeId, representation });
      if (state.stopped || state.round !== round) return;
      if (result.representation !== representation) throw new Error('Η απεικόνιση δεν αντιστοιχεί στην επιλογή.');
      if (lesson) verifyLessonRound(Engine.validateRound(result), round);
      state.representation = representation; state.busy = false; state.failed = false;
      $('representation-note').textContent = representation === '3d'
        ? 'Σύρε το μοντέλο για να το περιστρέψεις. Η σύνθεσή σου παραμένει ίδια.'
        : 'Διαφορετική απεικόνιση του ίδιου μορίου. Η σύνθεσή σου παραμένει ίδια.';
      mask(''); setStatus(state.solved ? 'Το όνομα σχηματίστηκε σωστά.' : 'Συνέχισε τη σύνθεση του ονόματος.'); updateControls(); scheduleSize();
    } catch (error) {
      if (error.message === 'superseded' || state.stopped) return;
      fail('Δεν φόρτωσε αυτή η απεικόνιση. Η προσπάθειά σου διατηρήθηκε.', () => changeRepresentation(representation));
    }
  }
  function receive(event) {
    if (state.stopped || event.origin !== location.origin || event.source !== frame.contentWindow) return;
    const data = event.data;
    if (!data || data.channel !== channel || data.session !== nonce) return;
    if (data.type === 'error' && data.requestId === 0 && !state.inventory.length) {
      clearTimeout(startupTimer);
      fail('Η προβολή μορίου δεν μπόρεσε να ξεκινήσει. Δοκίμασε ξανά.', () => location.reload());
      return;
    }
    if (data.type === 'ready' && !state.inventory.length) {
      try {
        state.inventory = validInventory(data.inventory); clearTimeout(startupTimer);
        if (lesson) {
          if (lesson.current) loadRound(lesson.current.moleculeId, lesson.current);
          else setStatus('Ετοιμάζουμε το μόριο της άσκησης.');
          return;
        }
        preparePractice();
      } catch (error) { fail(error.message, () => location.reload()); }
      return;
    }
    const pending = state.pending;
    if (!pending || data.requestId !== pending.requestId || data.roundId !== pending.roundId || data.moleculeId !== pending.moleculeId) return;
    if (data.type === 'busy') return;
    if (data.type !== pending.expectedType && data.type !== 'error') return;
    clearTimeout(pending.timer); state.pending = null;
    if (data.type === 'error') pending.reject(new Error('Αποτυχία προβολής μορίου.'));
    else pending.resolve(data);
  }
  function tileById(id) { return state.bank.find(tile => tile.id === id); }
  function answerTiles() { return state.answer.map(tileById); }
  function editable() { return !!state.round && !state.busy && !state.failed && !state.solved; }
  function clearFeedback() {
    state.submitted = false; $('feedback').hidden = true; $('feedback').classList.remove('success');
    viewportUI?.clearFeedback();
  }
  function focusTile(id, inAnswer) {
    const container = $(inAnswer ? 'answer-tiles' : 'bank-tiles');
    const button = Array.from(container.querySelectorAll('button')).find(item => item.dataset.tileId === id);
    if (!button) return;
    if (viewportEnabled && !inAnswer) {
      const bounds = $('bank-zone').getBoundingClientRect(), tile = button.getBoundingClientRect();
      if (!bounds.width || !bounds.height) { $('answer-zone').focus({ preventScroll: true }); return; }
      if (tile.top < bounds.top) $('bank-zone').scrollTop += tile.top - bounds.top;
      else if (tile.bottom > bounds.bottom) $('bank-zone').scrollTop += tile.bottom - bounds.bottom;
    }
    button.focus({ preventScroll: true });
    if (inAnswer) {
      const viewport = $('answer-zone'), bounds = viewport.getBoundingClientRect(), tile = button.getBoundingClientRect();
      const left = bounds.left + viewport.clientLeft + 8, right = left + viewport.clientWidth - 16;
      if (tile.width > right - left || tile.left < left) viewport.scrollLeft += tile.left - left;
      else if (tile.right > right) viewport.scrollLeft += tile.right - right;
    }
  }
  function place(id, index) {
    if (!editable() || !tileById(id)) return;
    const previous = state.answer.indexOf(id);
    if (previous >= 0) { state.answer.splice(previous, 1); if (previous < index) index--; }
    state.answer.splice(Math.max(0, Math.min(index, state.answer.length)), 0, id);
    state.selected = id; clearFeedback(); render(); focusTile(id, true);
    revealRange('construction');
    announce('Προστέθηκε το «' + tileById(id).text + '» στη θέση ' + (state.answer.indexOf(id) + 1) + '.');
  }
  function remove(id) {
    if (!editable()) return;
    const index = state.answer.indexOf(id); if (index < 0) return;
    state.answer.splice(index, 1); state.selected = null; clearFeedback(); render(); focusTile(id, false);
    revealRange('construction');
    announce('Το «' + tileById(id).text + '» επέστρεψε στα διαθέσιμα συνθετικά.');
  }
  function move(id, delta) {
    const index = state.answer.indexOf(id), target = index + delta;
    if (!editable() || index < 0 || target < 0 || target >= state.answer.length) return;
    [state.answer[index], state.answer[target]] = [state.answer[target], state.answer[index]];
    state.selected = id; clearFeedback(); render(); focusTile(id, true);
    revealRange('construction');
    announce('Το «' + tileById(id).text + '» μετακινήθηκε στη θέση ' + (target + 1) + '.');
  }
  function tileButton(tile, inAnswer, index) {
    const item = document.createElement('li');
    const button = document.createElement('button'); button.type = 'button';
    button.className = 'tile-button'; button.textContent = tile.text; button.dataset.tileId = tile.id;
    button.setAttribute('aria-label', inAnswer ? 'Συνθετικό ' + (index + 1) + ': ' + tile.text : 'Πρόσθεσε το συνθετικό ' + tile.text);
    if (inAnswer) { button.setAttribute('aria-pressed', state.selected === tile.id ? 'true' : 'false'); button.classList.toggle('selected', state.selected === tile.id); }
    button.addEventListener('click', () => {
      if (!editable() || Date.now() < state.suppressClickUntil) return;
      if (!inAnswer) place(tile.id, state.answer.length);
      else { state.selected = state.selected === tile.id ? null : tile.id; render(); focusTile(tile.id, true); revealRange('construction'); }
    });
    button.addEventListener('keydown', event => {
      if (!inAnswer || !editable()) return;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); move(tile.id, event.key === 'ArrowLeft' ? -1 : 1); }
      else if (event.key === 'Delete' || event.key === 'Backspace') { event.preventDefault(); remove(tile.id); }
    });
    button.draggable = false;
    button.addEventListener('pointerdown', event => startTouch(event, tile.id, button));
    item.append(button); return item;
  }
  function render() {
    $('bank-tiles').replaceChildren(...state.bank.filter(tile => !state.answer.includes(tile.id)).map(tile => tileButton(tile, false)));
    $('answer-tiles').replaceChildren(...answerTiles().map((tile, index) => tileButton(tile, true, index)));
    $('empty-answer').hidden = !!state.answer.length;
    $('candidate').hidden = !state.answer.length;
    $('candidate-name').textContent = state.answer.length ? Engine.compose(answerTiles(), state.round) : '';
    $('selected-tile-label').textContent = state.selected ? '«' + tileById(state.selected).text + '»' : '';
    updateControls();
    publishSnapshot();
  }
  function dropIndex(x) {
    const items = Array.from($('answer-tiles').children);
    for (let i = 0; i < items.length; i++) {
      const r = items[i].getBoundingClientRect();
      if (x < r.left + r.width / 2) return i;
    }
    return state.answer.length;
  }
  function clearDropStyles() { $('answer-zone').classList.remove('drag-over'); $('bank-zone').classList.remove('drag-over'); }
  function startTouch(event, id, button) {
    if (!editable() || !['mouse', 'touch', 'pen'].includes(event.pointerType) || !event.isPrimary || event.button !== 0) return;
    cancelTouch();
    state.touch = { id, pointerId: event.pointerId, x: event.clientX, y: event.clientY,
      lastX: event.clientX, lastY: event.clientY, active: false, button, ghost: null, scrollFrame: null };
    button.setPointerCapture(event.pointerId);
    button.addEventListener('pointermove', touchMove); button.addEventListener('pointerup', touchEnd);
    button.addEventListener('pointercancel', cancelTouch);
    button.addEventListener('lostpointercapture', cancelTouch);
  }
  function touchMove(event) {
    const touch = state.touch; if (!touch || event.pointerId !== touch.pointerId) return;
    touch.lastX = event.clientX; touch.lastY = event.clientY;
    if (!touch.active && Math.hypot(event.clientX - touch.x, event.clientY - touch.y) < 8) return;
    event.preventDefault();
    if (!touch.active) {
      touch.active = true; touch.ghost = document.createElement('div');
      touch.ghost.className = 'tile-button touch-ghost'; touch.ghost.textContent = tileById(touch.id).text;
      touch.ghost.setAttribute('aria-hidden', 'true'); document.body.append(touch.ghost); touch.button.classList.add('dragging');
    }
    touch.ghost.style.left = event.clientX + 'px'; touch.ghost.style.top = event.clientY + 'px';
    clearDropStyles(); const target = document.elementFromPoint(event.clientX, event.clientY);
    if (target?.closest('#answer-zone')) $('answer-zone').classList.add('drag-over');
    if (target?.closest('#bank-zone')) $('bank-zone').classList.add('drag-over');
    if (touch.scrollFrame === null) touch.scrollFrame = requestAnimationFrame(scrollDraggedAnswer);
    if (!viewportEnabled) {
      if (event.clientY < 45) window.scrollBy(0, -14);
      else if (event.clientY > innerHeight - 45) window.scrollBy(0, 14);
    }
  }
  function scrollDraggedAnswer() {
    const touch = state.touch; if (!touch || !touch.active) return;
    touch.scrollFrame = null;
    const viewport = $('answer-zone'), bounds = viewport.getBoundingClientRect();
    if (touch.lastY < bounds.top || touch.lastY > bounds.bottom || touch.lastX < bounds.left || touch.lastX > bounds.right) return;
    const edge = Math.min(36, bounds.width / 4);
    const direction = touch.lastX < bounds.left + edge ? -1 : touch.lastX > bounds.right - edge ? 1 : 0;
    if (!direction) return;
    const previous = viewport.scrollLeft;
    viewport.scrollLeft += direction * 9;
    if (viewport.scrollLeft !== previous) touch.scrollFrame = requestAnimationFrame(scrollDraggedAnswer);
  }
  function dropContext(x, y) {
    if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
    let target = x >= 0 && y >= 0 && x < innerWidth && y < innerHeight
      ? document.elementFromPoint(x, y) : null;
    // Placement needs a visible answer hit. Removal also accepts a completed
    // release over the surrounding page, beyond this iframe or its clipping.
    let view = window;
    try {
      while (view !== view.parent) {
        const frame = view.frameElement;
        if (!frame || !frame.offsetWidth || !frame.offsetHeight) return null;
        const bounds = frame.getBoundingClientRect();
        const scaleX = bounds.width / frame.offsetWidth, scaleY = bounds.height / frame.offsetHeight;
        if (!Number.isFinite(scaleX) || !Number.isFinite(scaleY) || scaleX <= 0 || scaleY <= 0) return null;
        x = bounds.left + (frame.clientLeft + x) * scaleX;
        y = bounds.top + (frame.clientTop + y) * scaleY;
        view = view.parent;
        if (x < 0 || y < 0 || x >= view.innerWidth || y >= view.innerHeight ||
            view.document.elementFromPoint(x, y) !== frame) target = null;
      }
    } catch (_) { return null; }
    if (!Number.isFinite(x) || !Number.isFinite(y) || x < 0 || y < 0 || x >= view.innerWidth || y >= view.innerHeight) return null;
    return { target };
  }
  function touchEnd(event) {
    const touch = state.touch; if (!touch || event.pointerId !== touch.pointerId) return;
    const active = touch.active, id = touch.id, placed = state.answer.includes(id);
    const drop = active ? dropContext(event.clientX, event.clientY) : null;
    const bounds = $('answer-zone').getBoundingClientRect();
    const inside = event.clientX >= bounds.left && event.clientX <= bounds.right &&
      event.clientY >= bounds.top && event.clientY <= bounds.bottom;
    if (active) { event.preventDefault(); state.suppressClickUntil = Date.now() + 600; }
    cancelTouch();
    if (!active || !drop) return;
    if (inside && drop.target?.closest('#answer-zone')) place(id, dropIndex(event.clientX));
    else if (placed) remove(id);
  }
  function cancelTouch() {
    const touch = state.touch; if (!touch) return;
    if (touch.scrollFrame !== null) cancelAnimationFrame(touch.scrollFrame);
    touch.ghost?.remove(); touch.button.classList.remove('dragging');
    touch.button.removeEventListener('pointermove', touchMove); touch.button.removeEventListener('pointerup', touchEnd);
    touch.button.removeEventListener('pointercancel', cancelTouch);
    touch.button.removeEventListener('lostpointercapture', cancelTouch);
    state.touch = null;
    try { if (touch.button.hasPointerCapture(touch.pointerId)) touch.button.releasePointerCapture(touch.pointerId); } catch (_) { /* removed tile */ }
    clearDropStyles();
  }
  function showFeedback(result) {
    viewportUI?.clearFeedbackName();
    $('feedback').replaceChildren(); $('feedback').hidden = false;
    if (inlineResults) $('feedback').scrollTop = 0;
    $('feedback').classList.toggle('success', result.correct);
    if (result.correct) {
      state.solved = true; state.selected = null;
      const name = document.createElement('strong'); name.textContent = state.round.correctName;
      name.className = 'single-line-name'; name.tabIndex = 0;
      name.setAttribute('role', 'region'); name.setAttribute('aria-label', 'Σωστό όνομα');
      const message = document.createElement('span'); message.textContent = result.message;
      $('feedback').append(name, message); setStatus('Το όνομα σχηματίστηκε σωστά.');
      if (lesson?.current?.explanation) {
        const explanation = document.createElement('p'); explanation.className = 'lesson-explanation';
        explanation.textContent = lesson.current.explanation; $('feedback').append(explanation);
      }
    } else $('feedback').textContent = result.message;
    viewportUI?.feedback(result.correct);
  }
  $('check-answer').addEventListener('click', () => {
    if (!editable() || !state.answer.length || state.attempts >= Number.MAX_SAFE_INTEGER) return;
    state.attempts++; state.submitted = true;
    const result = Engine.evaluate(state.round, answerTiles());
    showFeedback(result);
    if (result.correct) render(); else publishSnapshot();
    revealFeedback();
  });
  $('move-before').addEventListener('click', () => move(state.selected, -1));
  $('move-after').addEventListener('click', () => move(state.selected, 1));
  $('remove-tile').addEventListener('click', () => remove(state.selected));
  $('next-molecule').addEventListener('click', () => { if (!lesson && !state.busy && practiceSlot()) loadRound(nextMolecule()); });
  $('retry-load').addEventListener('click', () => state.retry?.());
  const guidance = $('answer-help');
  const compactGuidance = matchMedia('(max-width:600px)');
  function updateGuidanceLayout() {
    if (state.stopped) return;
    guidance.open = viewportEnabled || !compactGuidance.matches;
    scheduleSize();
  }
  guidance.addEventListener('toggle', () => {
    if (state.stopped) return;
    scheduleSize();
    if (guidance.open && compactGuidance.matches) revealRange('construction', guidance);
    else if (!guidance.open) revealRange($('feedback').hidden ? 'construction' : 'feedback');
  });
  compactGuidance.addEventListener('change', updateGuidanceLayout);
  updateGuidanceLayout();
  representationButtons.forEach(button => button.addEventListener('click', () => changeRepresentation(button.dataset.representation)));
  $('zoom-in').addEventListener('click', () => { if (!state.busy && !state.failed) post('zoom', { roundId: state.round.roundId, moleculeId: state.round.moleculeId, direction: 1 }); });
  $('zoom-out').addEventListener('click', () => { if (!state.busy && !state.failed) post('zoom', { roundId: state.round.roundId, moleculeId: state.round.moleculeId, direction: -1 }); });
  window.addEventListener('message', receive);
  window.addEventListener('message', receiveLesson);
  window.addEventListener('blur', cancelTouch);
  function lessonExitKey(event) {
    if (lesson && event.key === 'Escape') { event.preventDefault(); postLesson('exit', {}); }
  }
  window.addEventListener('keydown', lessonExitKey);
  ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => {
    window.addEventListener(type, interruptReveal, { capture: true, passive: true });
  });
  frame.addEventListener('load', () => {
    // Native viewer input does not bubble to this document. Its same-origin
    // window forwards interruption and the existing lesson Escape behavior.
    try {
      frame.contentWindow.addEventListener('keydown', lessonExitKey);
      ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => {
        frame.contentWindow.addEventListener(type, interruptReveal, { capture: true, passive: true });
      });
    } catch (_) { /* viewer load failed */ }
  });
  window.addEventListener('pagehide', () => {
    clearTimeout(startupTimer); stopLocalReveal(); cancelTouch(); viewportUI?.destroy(); practice.controls?.destroy();
    compactGuidance.removeEventListener('change', updateGuidanceLayout);
    if (lesson) {
      if (lesson.resizeFrame !== null) cancelAnimationFrame(lesson.resizeFrame);
      lesson.observer?.disconnect(); lesson.current = null;
    }
    if (state.pending) { clearTimeout(state.pending.timer); state.pending.reject(new Error('superseded')); state.pending = null; }
    post('stop', {}); state.stopped = true; frame.src = 'about:blank';
  }, { once: true });
  if (!Engine) { clearTimeout(startupTimer); fail('Δεν φορτώθηκε ο μηχανισμός του παιχνιδιού. Ανανέωσε τη σελίδα.', () => location.reload()); return; }
  if (lesson) {
    document.documentElement.classList.add('lesson-mode');
    $('game-levels').hidden = true;
    $('next-molecule').hidden = true;
    if (!viewportEnabled) {
      lesson.observer = new ResizeObserver(scheduleSize); lesson.observer.observe(document.body);
      window.addEventListener('resize', scheduleSize);
    }
    postLesson('ready', {});
  }
  if (viewportEnabled) viewportUI = createViewportUI();
  frame.src = 'name-builder-viewer.html?v=uniform-games-20261118-r2&session=' + encodeURIComponent(nonce) + nativeFormulaQuery();
})();
