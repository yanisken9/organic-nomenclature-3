/* Standalone name assembly. The parent owns attempts; depiction never recreates them. */
(function () {
  'use strict';
  const Engine = window.NameleculeNameBuilderEngine;
  const channel = 'namelecule-name-builder-v1';
  const $ = id => document.getElementById(id);
  const frame = $('molecule-viewer');
  const nonce = Array.from(crypto.getRandomValues(new Uint8Array(18)), b => b.toString(16).padStart(2, '0')).join('');
  const forms = ['condensed', 'expanded', 'skeletal', '3d'];
  const state = { inventory: [], deck: [], round: null, bank: [], answer: [], selected: null,
    representation: '', busy: true, failed: false, solved: false, stopped: false, roundNumber: 0,
    pending: null, nextId: 0, retry: null, touch: null, suppressClickUntil: 0 };
  const representationButtons = Array.from(document.querySelectorAll('[data-representation]'));
  const startupTimer = setTimeout(() => fail('Η προβολή του μορίου άργησε να ξεκινήσει. Μπορείς να δοκιμάσεις ξανά.', () => location.reload()), 45000);

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
  async function loadRound(moleculeId) {
    if (state.stopped) return;
    cancelTouch(); state.busy = true; state.failed = false; state.solved = false;
    state.answer = []; state.selected = null; state.round = null; state.bank = [];
    $('feedback').hidden = true; $('candidate').hidden = true;
    $('bank-tiles').replaceChildren(); $('answer-tiles').replaceChildren(); $('empty-answer').hidden = false;
    mask('Ετοιμάζουμε τη δομή και τα συνθετικά.'); setStatus('Ετοιμάζουμε το επόμενο μόριο.'); updateControls();
    const roundId = nonce + '-' + (++state.roundNumber);
    try {
      const result = await request('load', { moleculeId, roundId, representation: 'condensed' });
      if (state.stopped || roundId !== nonce + '-' + state.roundNumber) return;
      const round = Engine.validateRound(result);
      if (round.moleculeId !== moleculeId || round.roundId !== roundId) throw new Error('Η απόκριση δεν αντιστοιχεί στο μόριο της άσκησης.');
      state.round = round; state.bank = Engine.createBank(round, { seed: roundId });
      state.representation = 'condensed'; state.busy = false; state.failed = false;
      mask(''); setStatus('Διάλεξε τα συνθετικά και χτίσε το όνομα.');
      render();
    } catch (error) {
      if (error.message === 'superseded' || state.stopped) return;
      fail('Δεν ήταν δυνατή η προετοιμασία αυτού του μορίου. Δοκίμασε ξανά ή διάλεξε «Άλλο μόριο».', () => loadRound(moleculeId));
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
      state.representation = representation; state.busy = false; state.failed = false;
      $('representation-note').textContent = representation === '3d'
        ? 'Σύρε το μοντέλο για να το περιστρέψεις. Η σύνθεσή σου παραμένει ίδια.'
        : 'Διαφορετική απεικόνιση του ίδιου μορίου. Η σύνθεσή σου παραμένει ίδια.';
      mask(''); setStatus(state.solved ? 'Το όνομα σχηματίστηκε σωστά.' : 'Συνέχισε τη σύνθεση του ονόματος.'); updateControls();
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
  function clearFeedback() { $('feedback').hidden = true; $('feedback').classList.remove('success'); }
  function focusTile(id, inAnswer) {
    const container = $(inAnswer ? 'answer-tiles' : 'bank-tiles');
    const button = Array.from(container.querySelectorAll('button')).find(item => item.dataset.tileId === id);
    if (button) button.focus({ preventScroll: true });
  }
  function place(id, index) {
    if (!editable() || !tileById(id)) return;
    const previous = state.answer.indexOf(id);
    if (previous >= 0) { state.answer.splice(previous, 1); if (previous < index) index--; }
    state.answer.splice(Math.max(0, Math.min(index, state.answer.length)), 0, id);
    state.selected = id; clearFeedback(); render(); focusTile(id, true);
    announce('Προστέθηκε το «' + tileById(id).text + '» στη θέση ' + (state.answer.indexOf(id) + 1) + '.');
  }
  function remove(id) {
    if (!editable()) return;
    const index = state.answer.indexOf(id); if (index < 0) return;
    state.answer.splice(index, 1); state.selected = null; clearFeedback(); render(); focusTile(id, false);
    announce('Το «' + tileById(id).text + '» επέστρεψε στα διαθέσιμα συνθετικά.');
  }
  function move(id, delta) {
    const index = state.answer.indexOf(id), target = index + delta;
    if (!editable() || index < 0 || target < 0 || target >= state.answer.length) return;
    [state.answer[index], state.answer[target]] = [state.answer[target], state.answer[index]];
    state.selected = id; clearFeedback(); render(); focusTile(id, true);
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
      else { state.selected = state.selected === tile.id ? null : tile.id; render(); focusTile(tile.id, true); }
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
  }
  function dropIndex(x, y) {
    const items = Array.from($('answer-tiles').children);
    for (let i = 0; i < items.length; i++) {
      const r = items[i].getBoundingClientRect();
      if (y < r.top || (y <= r.bottom && x < r.left + r.width / 2)) return i;
    }
    return state.answer.length;
  }
  function clearDropStyles() { $('answer-zone').classList.remove('drag-over'); $('bank-zone').classList.remove('drag-over'); }
  function startTouch(event, id, button) {
    if (!editable() || !['mouse', 'touch', 'pen'].includes(event.pointerType) || !event.isPrimary || event.button !== 0) return;
    cancelTouch();
    state.touch = { id, pointerId: event.pointerId, x: event.clientX, y: event.clientY, active: false, button, ghost: null };
    button.setPointerCapture(event.pointerId);
    button.addEventListener('pointermove', touchMove); button.addEventListener('pointerup', touchEnd);
    button.addEventListener('pointercancel', cancelTouch);
    button.addEventListener('lostpointercapture', cancelTouch);
  }
  function touchMove(event) {
    const touch = state.touch; if (!touch || event.pointerId !== touch.pointerId) return;
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
    if (event.clientY < 45) window.scrollBy(0, -14);
    else if (event.clientY > innerHeight - 45) window.scrollBy(0, 14);
  }
  function touchEnd(event) {
    const touch = state.touch; if (!touch || event.pointerId !== touch.pointerId) return;
    const active = touch.active, id = touch.id;
    const target = document.elementFromPoint(event.clientX, event.clientY);
    if (active) { event.preventDefault(); state.suppressClickUntil = Date.now() + 600; }
    cancelTouch();
    if (active && target?.closest('#answer-zone')) place(id, dropIndex(event.clientX, event.clientY));
    else if (active && target?.closest('#bank-zone')) remove(id);
  }
  function cancelTouch() {
    const touch = state.touch; if (!touch) return;
    touch.ghost?.remove(); touch.button.classList.remove('dragging');
    touch.button.removeEventListener('pointermove', touchMove); touch.button.removeEventListener('pointerup', touchEnd);
    touch.button.removeEventListener('pointercancel', cancelTouch);
    touch.button.removeEventListener('lostpointercapture', cancelTouch);
    state.touch = null;
    try { if (touch.button.hasPointerCapture(touch.pointerId)) touch.button.releasePointerCapture(touch.pointerId); } catch (_) { /* removed tile */ }
    clearDropStyles();
  }
  $('check-answer').addEventListener('click', () => {
    if (!editable() || !state.answer.length) return;
    const result = Engine.evaluate(state.round, answerTiles());
    $('feedback').replaceChildren(); $('feedback').hidden = false;
    $('feedback').classList.toggle('success', result.correct);
    if (result.correct) {
      state.solved = true; state.selected = null;
      const name = document.createElement('strong'); name.textContent = state.round.correctName;
      const message = document.createElement('span'); message.textContent = result.message;
      $('feedback').append(name, message); setStatus('Το όνομα σχηματίστηκε σωστά.');
      render();
    } else $('feedback').textContent = result.message;
    $('feedback').scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
  $('move-before').addEventListener('click', () => move(state.selected, -1));
  $('move-after').addEventListener('click', () => move(state.selected, 1));
  $('remove-tile').addEventListener('click', () => remove(state.selected));
  $('next-molecule').addEventListener('click', () => { if (!state.busy && state.inventory.length) loadRound(nextMolecule()); });
  $('retry-load').addEventListener('click', () => state.retry?.());
  representationButtons.forEach(button => button.addEventListener('click', () => changeRepresentation(button.dataset.representation)));
  $('zoom-in').addEventListener('click', () => { if (!state.busy && !state.failed) post('zoom', { roundId: state.round.roundId, moleculeId: state.round.moleculeId, direction: 1 }); });
  $('zoom-out').addEventListener('click', () => { if (!state.busy && !state.failed) post('zoom', { roundId: state.round.roundId, moleculeId: state.round.moleculeId, direction: -1 }); });
  window.addEventListener('message', receive);
  window.addEventListener('blur', cancelTouch);
  window.addEventListener('pagehide', () => {
    clearTimeout(startupTimer); cancelTouch();
    if (state.pending) { clearTimeout(state.pending.timer); state.pending.reject(new Error('superseded')); state.pending = null; }
    post('stop', {}); state.stopped = true; frame.src = 'about:blank';
  }, { once: true });
  if (!Engine) { clearTimeout(startupTimer); fail('Δεν φορτώθηκε ο μηχανισμός του παιχνιδιού. Ανανέωσε τη σελίδα.', () => location.reload()); return; }
  frame.src = 'name-builder-viewer.html?session=' + encodeURIComponent(nonce);
})();
