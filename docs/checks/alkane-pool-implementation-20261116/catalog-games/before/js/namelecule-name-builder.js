/* Name assembly. This page owns its native viewer; an optional lesson parent
 * owns the saved tile evidence and completion navigation. */
(function () {
  'use strict';
  const Engine = window.NameleculeNameBuilderEngine;
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
  const state = { inventory: [], deck: [], round: null, bank: [], answer: [], selected: null,
    representation: '', busy: true, failed: false, solved: false, stopped: false, roundNumber: 0,
    pending: null, nextId: 0, retry: null, touch: null, suppressClickUntil: 0, attempts: 0, submitted: false };
  const scrolling = { frame: null, moving: false };
  const representationButtons = Array.from(document.querySelectorAll('[data-representation]'));
  const startupTimer = setTimeout(() => fail('Η προβολή του μορίου άργησε να ξεκινήσει. Μπορείς να δοκιμάσεις ξανά.', () => location.reload()), 45000);

  function snapshot() {
    return { answer: state.answer.slice(), selected: state.selected, attempts: state.attempts, submitted: state.submitted };
  }
  function postLesson(type, data, current = lesson?.current) {
    if (!lesson || state.stopped || (type !== 'ready' && !current)) return;
    const identity = current ? { requestId: current.requestId, attemptId: current.attemptId, moleculeId: current.moleculeId } : {};
    parent.postMessage({ channel: lessonChannel, session: lessonSession, ...identity, type, ...data }, location.origin);
  }
  function publishSnapshot() {
    if (lesson?.current?.ready) postLesson('state', { state: snapshot() });
    scheduleSize();
  }
  function scheduleSize() {
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
    stopLocalReveal();
    if (lesson?.current?.ready) postLesson('scroll-interrupt', {});
  }
  function revealRange(purpose, region) {
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
  function validateLessonLoad(data) {
    if (typeof data.attemptId !== 'string' || !data.attemptId || data.attemptId.length > 160 ||
        !lessonMolecules.includes(data.moleculeId) || typeof data.bankSeed !== 'string' || !data.bankSeed || data.bankSeed.length > 256 ||
        typeof data.explanation !== 'string' || data.explanation.length > 8000) throw new Error('Μη έγκυρα δεδομένα άσκησης.');
    const round = Engine.validateRound(data.round);
    const rootCount = lessonMolecules.indexOf(data.moleculeId) < 5 ? 5 : 6;
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
      bankSeed: data.bankSeed, explanation: data.explanation,
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
    if (!data || data.channel !== lessonChannel || data.session !== lessonSession || data.command !== 'load' ||
        !Number.isSafeInteger(data.requestId) || data.requestId <= lesson.lastId) return;
    lesson.lastId = data.requestId;
    try {
      const current = validateLessonLoad(data);
      lesson.current = current; lesson.lastHeight = null;
      if (state.inventory.length) loadRound(current.moleculeId, current);
    } catch (error) {
      if (typeof data.attemptId === 'string' && data.attemptId.length <= 160 && lessonMolecules.includes(data.moleculeId)) {
        postLesson('error', { message: error.message }, data);
      }
    }
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
    $('next-molecule').disabled = !state.inventory.length || state.busy;
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
  function randomIndex(length) { const n = new Uint32Array(1); crypto.getRandomValues(n); return n[0] % length; }
  function nextMolecule() {
    if (!state.deck.length) {
      state.deck = state.inventory.map(entry => entry.id);
      for (let i = state.deck.length - 1; i > 0; i--) {
        const j = randomIndex(i + 1); [state.deck[i], state.deck[j]] = [state.deck[j], state.deck[i]];
      }
      if (state.round && state.deck.length > 1 && state.deck.at(-1) === state.round.moleculeId) state.deck.reverse();
    }
    return state.deck.pop();
  }
  async function loadRound(moleculeId, controlled = null) {
    if (state.stopped || (lesson && controlled !== lesson.current)) return;
    stopLocalReveal(); cancelTouch(); state.busy = true; state.failed = false; state.solved = false;
    state.attempts = 0; state.submitted = false;
    if (controlled) controlled.ready = false;
    state.answer = []; state.selected = null; state.round = null; state.bank = [];
    $('feedback').hidden = true; $('candidate').hidden = true;
    $('bank-tiles').replaceChildren(); $('answer-tiles').replaceChildren(); $('empty-answer').hidden = false;
    $('answer-zone').scrollLeft = 0; $('candidate-name').scrollLeft = 0;
    mask('Ετοιμάζουμε τη δομή και τα συνθετικά.'); setStatus('Ετοιμάζουμε το επόμενο μόριο.'); updateControls();
    const ticket = ++state.roundNumber;
    const roundId = controlled ? controlled.round.roundId : nonce + '-' + ticket;
    try {
      const result = await request('load', { moleculeId, roundId, representation: 'condensed' });
      if (state.stopped || ticket !== state.roundNumber || (controlled && controlled !== lesson.current)) return;
      const actual = Engine.validateRound(result);
      if (actual.moleculeId !== moleculeId || actual.roundId !== roundId) throw new Error('Η απόκριση δεν αντιστοιχεί στο μόριο της άσκησης.');
      if (controlled) verifyLessonRound(actual, controlled.round);
      state.round = controlled ? controlled.round : actual;
      state.bank = Engine.createBank(state.round, { seed: controlled ? controlled.bankSeed : roundId });
      if (controlled) Object.assign(state, controlled.initialState, { answer: controlled.initialState.answer.slice() });
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
    } catch (error) {
      if (error.message === 'superseded' || state.stopped || ticket !== state.roundNumber || (controlled && controlled !== lesson.current)) return;
      fail(lesson ? 'Δεν επαληθεύτηκε η προβολή αυτού του μορίου. Δοκίμασε ξανά ή επέστρεψε στην επιλογή παιχνιδιού.'
        : 'Δεν ήταν δυνατή η προετοιμασία αυτού του μορίου. Δοκίμασε ξανά ή διάλεξε «Άλλο μόριο».', () => loadRound(moleculeId, controlled));
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
        const requested = new URLSearchParams(location.search).get('molecule');
        const initial = state.inventory.some(entry => entry.id === requested) ? requested
          : state.inventory.some(entry => entry.id === 'ethane') ? 'ethane' : state.inventory[0].id;
        loadRound(initial);
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
  function clearFeedback() { state.submitted = false; $('feedback').hidden = true; $('feedback').classList.remove('success'); }
  function focusTile(id, inAnswer) {
    const container = $(inAnswer ? 'answer-tiles' : 'bank-tiles');
    const button = Array.from(container.querySelectorAll('button')).find(item => item.dataset.tileId === id);
    if (!button) return;
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
    if (event.clientY < 45) window.scrollBy(0, -14);
    else if (event.clientY > innerHeight - 45) window.scrollBy(0, 14);
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
    $('feedback').replaceChildren(); $('feedback').hidden = false;
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
  $('next-molecule').addEventListener('click', () => { if (!state.busy && state.inventory.length) loadRound(nextMolecule()); });
  $('retry-load').addEventListener('click', () => state.retry?.());
  const guidance = $('answer-help');
  const compactGuidance = matchMedia('(max-width:600px)');
  function updateGuidanceLayout() {
    if (state.stopped) return;
    guidance.open = !compactGuidance.matches;
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
    clearTimeout(startupTimer); stopLocalReveal(); cancelTouch();
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
    $('next-molecule').hidden = true;
    lesson.observer = new ResizeObserver(scheduleSize); lesson.observer.observe(document.body);
    window.addEventListener('resize', scheduleSize);
    postLesson('ready', {});
  }
  frame.src = 'name-builder-viewer.html?session=' + encodeURIComponent(nonce);
})();
