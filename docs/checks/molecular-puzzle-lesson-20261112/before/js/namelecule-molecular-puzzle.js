/* Isolated prototype: name -> carbon-group graph. No lesson/progress integration. */
(function () {
  'use strict';
  const E = window.NameleculeMolecularPuzzleEngine;
  const $ = id => document.getElementById(id);
  const board = $('assembly-board'), nodesLayer = $('board-nodes'), svg = $('board-svg');
  const W = 720, H = 360, SVG_NS = 'http://www.w3.org/2000/svg';
  const embedded = new URL(location.href).searchParams.get('embedded') === '1';
  document.body.classList.toggle('puzzle-embedded', embedded);
  function presentationType() {
    let width = innerWidth;
    // Existing lesson game headings live in the parent page. Preserve their
    // viewport-based size when this prototype's heading lives inside its frame.
    if (embedded && parent !== window) { try { width = parent.innerWidth; } catch (_) { /* Standalone size for cross-origin hosts. */ } }
    document.body.style.setProperty('--puzzle-title-size', (width <= 760 ? 28 : Math.min(40, Math.max(28.8, width * .03))) + 'px');
  }
  presentationType();
  addEventListener('resize', presentationType);
  let catalog = [], current = null, graph = { nodes: [], bonds: [] }, undo = [];
  let selected = null, bonding = false, bondStart = null, solved = false, busy = true;
  let serial = 0, drag = null, ignoreClickUntil = 0, loadController = null;
  let revealTimer = 0, loadingSerial = 0;
  const clone = value => JSON.parse(JSON.stringify(value));
  const label = n => n === 0 ? 'C' : 'CH' + (n === 1 ? '' : ['₀', '₁', '₂', '₃', '₄'][n]);

  function announce(text) { $('interaction-status').textContent = text; }
  function clearFeedback() {
    $('feedback').hidden = true;
    $('feedback').textContent = '';
    $('feedback').classList.remove('success');
  }
  function saveChange(before) {
    undo.push(before || clone(graph));
    if (undo.length > 50) undo.shift();
    clearFeedback();
  }
  function bounds() {
    const r = board.getBoundingClientRect();
    const halfWidth = (matchMedia('(max-width:650px)').matches ? 26 : 34) * W / Math.max(1, r.width);
    const halfHeight = 25 * H / Math.max(1, r.height);
    return { r, halfWidth, halfHeight, x: halfWidth + 8, y: halfHeight + 8 };
  }
  function fitPoint(point) {
    const b = bounds();
    return { x: Math.max(b.x, Math.min(W - b.x, point.x)), y: Math.max(b.y, Math.min(H - b.y, point.y)) };
  }
  function localPoint(x, y) {
    const r = board.getBoundingClientRect();
    return { x: (x - r.left) * W / r.width, y: (y - r.top) * H / r.height };
  }
  function insideBoard(x, y) {
    const r = board.getBoundingClientRect();
    const hit = document.elementFromPoint(x, y);
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom &&
      x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight && !!hit && board.contains(hit);
  }
  function freePoint(wanted, except) {
    const b = bounds(), stepX = b.halfWidth * 2 + 18, stepY = b.halfHeight * 2 + 24;
    const free = point => !graph.nodes.some(n => n.id !== except &&
      Math.abs(n.x - point.x) < stepX && Math.abs(n.y - point.y) < stepY);
    const first = fitPoint(wanted);
    if (free(first)) return first;
    let best = null, distance = Infinity;
    for (let y = b.y; y <= H - b.y; y += stepY) {
      for (let x = b.x; x <= W - b.x; x += stepX) {
        const p = { x, y }, d = Math.hypot(x - first.x, y - first.y);
        if (free(p) && d < distance) { best = p; distance = d; }
      }
    }
    return best;
  }
  function setFocus(nodeId) {
    const el = [...nodesLayer.children].find(n => n.dataset.nodeId === nodeId);
    if (el) el.focus({ preventScroll: true });
  }
  function frameNodes() {
    if (!graph.nodes.length) { board.style.minHeight = ''; return; }
    let r = board.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    const width = matchMedia('(max-width:650px)').matches ? 50 : 64;
    const columns = Math.max(1, Math.floor((r.width - 24 + 16) / (width + 16)));
    const rows = Math.ceil(graph.nodes.length / columns);
    // Grow the construction surface for unusually many learner-added pieces;
    // never discard a piece or shrink a chemical label to fit a smaller screen.
    const minimum = rows * 60 - 16 + 24;
    if (board.style.minHeight !== minimum + 'px') board.style.minHeight = minimum + 'px';
    r = board.getBoundingClientRect();
    const fitted = graph.nodes.map(n => ({ ...n, ...fitPoint(n) }));
    const separated = fitted.every((n, i) => Number.isFinite(n.x) && Number.isFinite(n.y) &&
      fitted.every((other, j) => i === j || Math.abs(n.x - other.x) * r.width / W >= width + 8 ||
        Math.abs(n.y - other.y) * r.height / H >= 52));
    if (separated) {
      fitted.forEach((n, i) => { graph.nodes[i].x = n.x; graph.nodes[i].y = n.y; });
      return;
    }
    // Sequential nearest-free placement can strand the last piece. Pack the
    // complete candidate in one bounded pass instead; IDs, groups and bonds stay
    // identical. The packing uses only the learner's graph, never the target.
    const ordered = graph.nodes.slice().sort((a, b) => a.y - b.y || a.x - b.x || a.id.localeCompare(b.id));
    ordered.forEach((n, i) => {
      const row = Math.floor(i / columns), count = Math.min(columns, graph.nodes.length - row * columns);
      const cell = (r.width - 24) / columns, start = (r.width - cell * count) / 2;
      n.x = (start + cell * (i % columns + .5)) * W / r.width;
      n.y = (12 + (r.height - 24) / rows * (row + .5)) * H / r.height;
    });
  }
  function bondEnd(a, b) {
    const box = bounds(), dx = b.x - a.x, dy = b.y - a.y;
    const t = Math.min(dx ? box.halfWidth / Math.abs(dx) : Infinity,
      dy ? box.halfHeight / Math.abs(dy) : Infinity, .45);
    return { x: a.x + dx * t, y: a.y + dy * t };
  }
  function renderBonds() {
    svg.replaceChildren();
    graph.bonds.forEach((edge, i) => {
      const a = graph.nodes.find(n => n.id === edge.a), b = graph.nodes.find(n => n.id === edge.b);
      if (!a || !b) return;
      const start = bondEnd(a, b), end = bondEnd(b, a);
      const line = document.createElementNS(SVG_NS, 'line');
      Object.entries({ x1: start.x, y1: start.y, x2: end.x, y2: end.y }).forEach(([k, v]) => line.setAttribute(k, v));
      line.classList.add('puzzle-bond');
      if (selected && selected.kind === 'bond' && selected.index === i) line.classList.add('is-selected');
      line.dataset.bondIndex = i;
      line.setAttribute('tabindex', solved ? '-1' : '0');
      line.setAttribute('role', 'button');
      line.setAttribute('aria-label', 'Δεσμός ' + (i + 1) + ', μεταξύ ομάδων ' +
        (graph.nodes.indexOf(a) + 1) + ' και ' + (graph.nodes.indexOf(b) + 1));
      line.setAttribute('aria-pressed', String(!!selected && selected.kind === 'bond' && selected.index === i));
      // SVG hit area is wide, while its visible stroke remains a chemical bond.
      const hit = line.cloneNode();
      hit.classList.add('puzzle-bond-hit');
      hit.removeAttribute('tabindex'); hit.removeAttribute('role'); hit.removeAttribute('aria-label');
      hit.setAttribute('aria-hidden', 'true');
      svg.append(hit, line);
    });
  }
  function controls() {
    $('check-answer').disabled = busy || solved || !graph.nodes.length;
    $('next-molecule').disabled = busy;
    $('round-select').disabled = busy;
    $('undo-action').disabled = busy || solved || !undo.length;
    $('bond-tool').disabled = busy || solved || graph.nodes.length < 2;
    $('bond-tool').setAttribute('aria-pressed', String(bonding));
    $('remove-selection').disabled = busy || solved || !selected;
    const node = selected && selected.kind === 'node' && graph.nodes.find(n => n.id === selected.id);
    $('selection-label').textContent = node ? label(node.hydrogens) :
      selected ? 'δεσμός' : 'κανένα';
    document.querySelectorAll('[data-move]').forEach(b => { b.disabled = busy || solved || !node; });
    document.querySelectorAll('[data-hydrogens]').forEach(b => { b.disabled = busy || solved || graph.nodes.length >= E.MAX_NODES; });
    if ($('fit-board')) $('fit-board').disabled = busy || !graph.nodes.length;
    board.classList.toggle('is-bonding', bonding);
    board.setAttribute('aria-busy', String(busy));
  }
  function render(focusId) {
    if (!drag) frameNodes();
    const active = document.activeElement && document.activeElement.dataset.nodeId;
    nodesLayer.replaceChildren();
    graph.nodes.forEach((node, i) => {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'puzzle-node';
      button.dataset.nodeId = node.id;
      button.textContent = label(node.hydrogens);
      button.style.left = (node.x / W * 100) + '%'; button.style.top = (node.y / H * 100) + '%';
      button.setAttribute('aria-label', 'Ομάδα ' + (i + 1) + ': ' + label(node.hydrogens));
      const isSelected = selected && selected.kind === 'node' && selected.id === node.id;
      button.setAttribute('aria-pressed', String(!!isSelected));
      button.classList.toggle('is-selected', !!isSelected);
      button.classList.toggle('is-bond-start', node.id === bondStart);
      button.disabled = solved;
      nodesLayer.append(button);
    });
    renderBonds(); controls();
    $('empty-board').hidden = !!graph.nodes.length;
    if (focusId || active) setFocus(focusId || active);
    postSize();
  }
  function postSize() {
    if (embedded && parent !== window) parent.postMessage({ type: 'namelecule-puzzle-size', height: document.documentElement.scrollHeight }, location.origin);
  }
  function cancelReveal() { clearTimeout(revealTimer); }
  function reveal(el) {
    cancelReveal();
    revealTimer = setTimeout(() => {
      const r = el.getBoundingClientRect();
      if (r.bottom > innerHeight - 14 || r.top < 10) {
        el.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth' });
      }
    }, 180);
  }
  ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => addEventListener(type, cancelReveal, { passive: true }));

  function addGroup(hydrogens, point) {
    if (busy || solved || graph.nodes.length >= E.MAX_NODES) return;
    const wanted = point || { x: W / 2, y: H / 2 };
    const p = freePoint(wanted) || fitPoint(wanted);
    saveChange();
    const id = 'piece-' + (++serial);
    graph.nodes.push({ id, hydrogens, x: p.x, y: p.y });
    selected = { kind: 'node', id }; bondStart = null;
    announce('Προστέθηκε ' + label(hydrogens) + '.'); render();
    reveal($('check-answer'));
  }
  function chooseNode(id) {
    if (busy || solved) return;
    selected = { kind: 'node', id };
    if (bonding) {
      if (!bondStart || bondStart === id) {
        bondStart = id; announce('Διάλεξε τη δεύτερη ομάδα για τον δεσμό.');
      } else {
        if (graph.bonds.some(e => e.a === bondStart && e.b === id || e.a === id && e.b === bondStart)) {
          announce('Οι δύο ομάδες έχουν ήδη δεσμό.');
        } else {
          saveChange(); graph.bonds.push({ a: bondStart, b: id, order: 1 });
          announce('Προστέθηκε απλός δεσμός.');
        }
        bondStart = null;
      }
    } else announce('Επιλέχθηκε ' + label(graph.nodes.find(n => n.id === id).hydrogens) + '.');
    render(id);
  }
  function removeSelected() {
    if (!selected || solved || busy) return;
    saveChange();
    if (selected.kind === 'node') {
      const id = selected.id;
      graph.nodes = graph.nodes.filter(n => n.id !== id);
      graph.bonds = graph.bonds.filter(e => e.a !== id && e.b !== id);
      announce('Η ομάδα αφαιρέθηκε. Είναι ξανά διαθέσιμη στα κομμάτια.');
    } else { graph.bonds.splice(selected.index, 1); announce('Ο δεσμός αφαιρέθηκε.'); }
    selected = null; bondStart = null; render();
  }
  function moveSelected(direction) {
    if (solved || busy || !selected || selected.kind !== 'node') return;
    const n = graph.nodes.find(n => n.id === selected.id), r = board.getBoundingClientRect();
    const delta = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[direction];
    const p = fitPoint({ x: n.x + delta[0] * 18 * W / r.width, y: n.y + delta[1] * 18 * H / r.height });
    const b = bounds();
    if (graph.nodes.some(o => o.id !== n.id && Math.abs(o.x - p.x) < b.halfWidth * 2 + 5 && Math.abs(o.y - p.y) < b.halfHeight * 2 + 5)) {
      announce('Υπάρχει άλλη ομάδα σε αυτή τη θέση.'); return;
    }
    if (p.x === n.x && p.y === n.y) return;
    saveChange(); Object.assign(n, p); render(n.id);
  }
  $('piece-bank').addEventListener('click', event => {
    if (performance.now() < ignoreClickUntil) return;
    const b = event.target.closest('[data-hydrogens]');
    if (b) addGroup(Number(b.dataset.hydrogens));
  });
  nodesLayer.addEventListener('click', event => {
    if (performance.now() < ignoreClickUntil) return;
    const b = event.target.closest('[data-node-id]');
    if (b) chooseNode(b.dataset.nodeId);
  });
  svg.addEventListener('click', event => {
    const edge = event.target.closest('[data-bond-index]');
    if (!edge || solved || busy) return;
    selected = { kind: 'bond', index: Number(edge.dataset.bondIndex) };
    bondStart = null; render(); announce('Επιλέχθηκε ο δεσμός. Μπορείς να τον αφαιρέσεις.');
    svg.querySelector('.puzzle-bond:not(.puzzle-bond-hit)[data-bond-index="' + selected.index + '"]').focus({ preventScroll: true });
  });
  svg.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('[data-bond-index]')) {
      event.preventDefault(); event.target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
  });
  board.addEventListener('keydown', event => {
    const arrows = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down' };
    if (event.target.dataset.nodeId && arrows[event.key]) {
      event.preventDefault(); selected = { kind: 'node', id: event.target.dataset.nodeId }; moveSelected(arrows[event.key]);
    } else if (event.key === 'Delete' || event.key === 'Backspace') {
      if (event.target.dataset.bondIndex) selected = { kind: 'bond', index: Number(event.target.dataset.bondIndex) };
      else if (event.target.dataset.nodeId) selected = { kind: 'node', id: event.target.dataset.nodeId };
      event.preventDefault(); removeSelected();
    } else if (event.key === 'Escape') { bonding = false; bondStart = null; render(); }
  });
  $('bond-tool').addEventListener('click', () => {
    bonding = !bonding; bondStart = null;
    announce(bonding ? 'Διάλεξε δύο ομάδες διαδοχικά, για να τις συνδέσεις.' : 'Επέστρεψες στη μετακίνηση ομάδων.'); render();
  });
  $('remove-selection').addEventListener('click', removeSelected);
  document.querySelectorAll('[data-move]').forEach(b => b.addEventListener('click', () => moveSelected(b.dataset.move)));
  $('undo-action').addEventListener('click', () => {
    if (busy || solved || !undo.length) return;
    graph = undo.pop(); selected = null; bondStart = null; clearFeedback(); render(); announce('Η τελευταία αλλαγή αναιρέθηκε.');
  });
  if ($('fit-board')) $('fit-board').addEventListener('click', () => {
    if (graph.nodes.length < 2) return;
    const before = clone(graph), b = bounds();
    const xs = graph.nodes.map(n => n.x), ys = graph.nodes.map(n => n.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const scale = Math.min((W - 2 * b.x) / Math.max(1, maxX - minX), (H - 2 * b.y) / Math.max(1, maxY - minY), 1.5);
    graph.nodes.forEach(n => { n.x = W / 2 + (n.x - (maxX + minX) / 2) * scale; n.y = H / 2 + (n.y - (maxY + minY) / 2) * scale; });
    if (!solved) saveChange(before); render();
  });
  $('check-answer').addEventListener('click', () => {
    if (busy || solved || !current || !graph.nodes.length) return;
    const result = E.grade(graph, current.target);
    $('feedback').hidden = false; $('feedback').textContent = result.message;
    $('feedback').classList.toggle('success', result.correct);
    if (result.correct) {
      solved = true; bonding = false; bondStart = null;
      $('game-status').textContent = 'Σωστά! Η δομή σου αντιστοιχεί στο όνομα ' + current.name + '.';
    }
    render(); reveal($('feedback'));
  });

  // Pointer capture stays on a stable container: rendering node buttons never loses a drag.
  document.addEventListener('pointerdown', event => {
    if (busy || solved || event.button !== 0 || drag) return;
    const item = event.target.closest('[data-node-id], [data-hydrogens]');
    if (!item || item.disabled) return;
    cancelReveal();
    drag = { pointerId: event.pointerId, item, capture: item.dataset.nodeId ? board : $('piece-bank'),
      id: item.dataset.nodeId || null, hydrogens: Number(item.dataset.hydrogens),
      x: event.clientX, y: event.clientY, active: false, before: clone(graph), ghost: null };
    drag.capture.setPointerCapture(event.pointerId);
  });
  document.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    if (!drag.active && Math.hypot(event.clientX - drag.x, event.clientY - drag.y) < 7) return;
    if (!drag.active) {
      drag.active = true;
      drag.ghost = drag.item.cloneNode(true);
      drag.ghost.removeAttribute('id'); drag.ghost.removeAttribute('data-node-id'); drag.ghost.removeAttribute('data-hydrogens');
      drag.ghost.className = 'puzzle-drag-ghost'; drag.ghost.setAttribute('aria-hidden', 'true');
      drag.ghost.setAttribute('tabindex', '-1');
      document.body.append(drag.ghost);
      if (drag.id) drag.item.classList.add('is-dragging');
    }
    event.preventDefault();
    drag.ghost.style.left = event.clientX + 'px'; drag.ghost.style.top = event.clientY + 'px';
    if (drag.id && insideBoard(event.clientX, event.clientY)) {
      const n = graph.nodes.find(n => n.id === drag.id), p = fitPoint(localPoint(event.clientX, event.clientY));
      Object.assign(n, p);
      drag.item.style.left = n.x / W * 100 + '%'; drag.item.style.top = n.y / H * 100 + '%'; renderBonds();
    }
  }, { passive: false });
  function finishDrag(event, cancel) {
    if (!drag || event && event.pointerId !== drag.pointerId) return;
    const d = drag; drag = null;
    if (d.ghost) d.ghost.remove(); d.item.classList.remove('is-dragging');
    if (d.capture.hasPointerCapture(d.pointerId)) d.capture.releasePointerCapture(d.pointerId);
    if (!d.active) {
      if (!cancel && event) {
        ignoreClickUntil = performance.now() + 350;
        if (d.id) chooseNode(d.id); else addGroup(d.hydrogens);
      }
      return;
    }
    ignoreClickUntil = performance.now() + 350;
    graph = d.before;
    const inPage = event && event.clientX >= 0 && event.clientY >= 0 && event.clientX <= innerWidth && event.clientY <= innerHeight;
    if (cancel || !inPage) { render(); return; }
    if (insideBoard(event.clientX, event.clientY)) {
      if (d.id) {
        const p = freePoint(localPoint(event.clientX, event.clientY), d.id);
        if (p) { saveChange(); Object.assign(graph.nodes.find(n => n.id === d.id), p); selected = { kind: 'node', id: d.id }; }
        render();
      } else addGroup(d.hydrogens, localPoint(event.clientX, event.clientY));
    } else if (d.id) { selected = { kind: 'node', id: d.id }; removeSelected(); }
    else render();
  }
  document.addEventListener('pointerup', event => finishDrag(event, false));
  document.addEventListener('pointercancel', event => finishDrag(event, true));
  document.addEventListener('lostpointercapture', event => { if (drag && event.pointerId === drag.pointerId) finishDrag(event, true); });
  addEventListener('blur', () => finishDrag(null, true));
  document.addEventListener('dragstart', event => { if (event.target.closest('[data-node-id],[data-hydrogens]')) event.preventDefault(); });

  function startRound(index) {
    finishDrag(null, true); cancelReveal();
    current = catalog[index]; if (!current) return;
    graph = { nodes: [], bonds: [] }; undo = []; selected = null; bondStart = null; bonding = false; solved = false;
    $('target-name').textContent = current.name;
    $('round-select').value = String(index);
    $('game-status').textContent = 'Διάβασε το όνομα και φτιάξε τον συνεπτυγμένο τύπο του μορίου.';
    clearFeedback(); announce('Νέο μόριο. Το πλαίσιο είναι κενό.'); render();
    reveal($('piece-bank'));
  }
  $('next-molecule').addEventListener('click', () => {
    startRound((catalog.indexOf(current) + 1) % catalog.length);
    reveal($('target-name'));
  });
  $('round-select').addEventListener('change', event => startRound(Number(event.target.value)));
  $('retry-load').addEventListener('click', load);
  const media = matchMedia('(max-width:600px)');
  function instructionsMode() { $('instructions').open = !media.matches; }
  media.addEventListener('change', instructionsMode); instructionsMode();
  async function digest(text) {
    const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, '0')).join('');
  }
  async function load() {
    const request = ++loadingSerial;
    if (loadController) loadController.abort();
    const controller = new AbortController();
    loadController = controller;
    const signal = controller.signal, timer = setTimeout(() => controller.abort(), 45000);
    busy = true; controls(); $('retry-load').hidden = true; $('game-status').classList.remove('error');
    $('game-status').textContent = 'Ετοιμάζουμε τα ονόματα και τα κομμάτια του παζλ.';
    try {
      const response = await fetch(new URL('data/alkane-structures.json', location.href), { signal });
      if (!response.ok) throw new Error('Δεν φορτώθηκαν τα δεδομένα των μορίων.');
      const data = await response.json();
      if (data.schemaVersion !== 1 || !Array.isArray(data.molecules) || data.molecules.length !== 8) throw new Error('Τα δεδομένα του παιχνιδιού δεν είναι συμβατά.');
      const ready = [];
      for (const m of data.molecules) {
        if (signal.aborted) throw new Error('Η φόρτωση ακυρώθηκε.');
        if (typeof m.mol !== 'string' || await digest(m.mol) !== m.sourceSHA256) throw new Error('Ο έλεγχος της πηγής ενός μορίου απέτυχε.');
        const target = E.parseMol(m.mol);
        const analysis = await window.NameleculeChemistryClient.analyze({ id: m.id, mol: m.mol }, { engineSHA256: data.engineSHA256, signal });
        if (typeof analysis.name !== 'string' || !analysis.name.trim()) throw new Error('Δεν προσδιορίστηκε το όνομα ενός μορίου.');
        ready.push({ id: m.id, name: analysis.name, target });
      }
      if (request !== loadingSerial) return;
      catalog = ready;
      $('round-select').replaceChildren(...catalog.map((m, i) => {
        const option = document.createElement('option'); option.value = i; option.textContent = m.name; return option;
      }));
      busy = false; startRound(0);
    } catch (error) {
      if (request !== loadingSerial) return;
      $('game-status').classList.add('error');
      $('game-status').textContent = 'Το παιχνίδι δεν ετοιμάστηκε. ' + (error.name === 'AbortError' ? 'Η φόρτωση άργησε ή ακυρώθηκε.' : error.message);
      $('retry-load').hidden = false;
    } finally { clearTimeout(timer); if (request === loadingSerial) { controls(); postSize(); } }
  }
  let resizePending = 0;
  new ResizeObserver(() => {
    cancelAnimationFrame(resizePending);
    resizePending = requestAnimationFrame(() => {
      if (drag) finishDrag(null, true);
      // render() frames the entire candidate, including solved/undo states.
      render();
    });
  }).observe(board);
  new ResizeObserver(postSize).observe(document.body);
  addEventListener('pagehide', () => { if (loadController) loadController.abort(); finishDrag(null, true); cancelReveal(); });
  load();
}());
