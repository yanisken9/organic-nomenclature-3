/* Name -> carbon-group graph; standalone or controlled by a verified lesson parent. */
(function () {
  'use strict';
  const E = window.NameleculeMolecularPuzzleEngine;
  const Levels = window.NameleculeGameLevels;
  const $ = id => document.getElementById(id);
  const board = $('assembly-board'), nodesLayer = $('board-nodes'), svg = $('board-svg');
  const W = 720, H = 360, SVG_NS = 'http://www.w3.org/2000/svg';
  const embedded = new URL(location.href).searchParams.get('embedded') === '1';
  const lessonSession = new URL(location.href).searchParams.get('lessonSession');
  const CHANNEL = 'namelecule-puzzle-lesson-v1';
  const lesson = parent !== window && /^[A-Za-z0-9_-]{16,128}$/.test(lessonSession || '')
    ? { current: null, lastRequest: 0, lastSnapshot: null, lastHeight: null, sizeFrame: null } : null;
  const Viewport = window.NameleculeGameViewport;
  const viewportEnabled = !!Viewport && (!lesson || new URL(location.href).searchParams.get('viewport') === '1');
  let viewportUI = null;
  const LEGACY_IDS = Object.freeze(['methane', 'ethane', 'propane', 'butane', 'pentane',
    'methyl_2_pentane', 'dimethyl_2_3_butane', 'ethyl_3_dimethyl_2_5_hexane']);
  const ENGINE_SHA = '3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306';
  const LEGACY_CATALOG = Object.freeze({ version: 1, file: 'data/alkane-structures.json',
    sha256: '9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724',
    revision: '275d537b19f3ef0791c97d8d78c127f541a0579038ef1e8d65dadde611845690', ids: LEGACY_IDS });
  const CURRENT_CATALOG = Object.freeze({ version: 2, file: 'data/alkane-structures-v2.json',
    sha256: '2c4d9a95a77291f13c4a422644aefdae7f23448c2eed7b9d2ef4913da6de92b2',
    revision: 'bb48fe6cbb689c2bad82cc15d47f53e49f4f021894183c6b228f97bf6902292f',
    ids: Object.freeze([...LEGACY_IDS, 'methyl_2_butane', 'methyl_3_pentane', 'ethyl_3_pentane',
      'dimethyl_2_2_propane', 'dimethyl_2_2_butane', 'ethyl_3_methyl_2_pentane']) });
  // Standalone state lives only in this page. The parent owns saved attempts;
  // old loads pin legacy8, while explicit validated contexts may select full14.
  let catalogDescriptor = lesson ? LEGACY_CATALOG : CURRENT_CATALOG;
  const verifiedCatalogs = new Map();
  const practice = { level: null, slots: new Map(), controls: null };
  document.body.classList.toggle('puzzle-embedded', embedded);
  document.body.classList.toggle('puzzle-controlled', !!lesson);
  $('game-levels').hidden = !!lesson;
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
  let attempts = 0, submitted = false, stopped = false;
  const clone = value => JSON.parse(JSON.stringify(value));
  const label = n => n === 0 ? 'C' : 'CH' + (n === 1 ? '' : ['₀', '₁', '₂', '₃', '₄'][n]);
  function snapshot() { return { graph: clone(graph), attempts, submitted }; }
  function postLesson(type, data) {
    if (!lesson || stopped || (type !== 'ready' && !lesson.current)) return;
    const c = type === 'ready' ? null : lesson.current;
    parent.postMessage({ channel: CHANNEL, session: lessonSession, type,
      ...(c ? { requestId: c.requestId, attemptId: c.attemptId, moleculeId: c.moleculeId,
        ...(c.context ? { context: c.context } : {}) } : {}), ...data }, location.origin);
  }
  function publish() {
    if (!lesson || !lesson.current || !lesson.current.loaded || busy || stopped || drag) return;
    const value = snapshot(), signature = JSON.stringify(value);
    if (signature !== lesson.lastSnapshot) { lesson.lastSnapshot = signature; postLesson('state', { state: value }); }
  }

  function validViewportMessage(data) {
    const controlled = lesson?.current;
    if (!controlled || data.channel !== CHANNEL || data.session !== lessonSession ||
        data.requestId !== controlled.requestId || data.attemptId !== controlled.attemptId || data.moleculeId !== controlled.moleculeId ||
        !Number.isFinite(data.height) || data.height <= 0 || !Number.isFinite(data.width) || data.width <= 0) return false;
    try {
      const context = validateLessonContext(data);
      return controlled.context ? !!context && Levels.contextKey(context) === Levels.contextKey(controlled.context) : context === null;
    } catch (_) { return false; }
  }
  function createViewportUI() {
    const root = $('game'), panel = root.querySelector('.puzzle-assembly-panel');
    const content = root.querySelector('.puzzle-assembly-content'), buttons = new Map(), pagers = [];
    let mounted = null;
    const nav = document.createElement('nav'); nav.className = 'puzzle-view-nav'; nav.setAttribute('aria-label', 'Προβολές άσκησης');
    [['editing', 'Σχέδιο'], ['pieces', 'Κομμάτια'], ['tools', 'Εργαλεία'], ['name', 'Όνομα'], ['help', 'Οδηγίες'], ['feedback', 'Σχόλιο']].forEach(([key, label]) => {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
      button.dataset.view = key; button.addEventListener('click', () => stage(key)); buttons.set(key, button); nav.append(button);
    });
    panel.before(nav);
    const port = document.createElement('div'); port.className = 'puzzle-board-port'; board.before(port); port.append(board);
    const side = document.createElement('div'); side.className = 'puzzle-side'; content.append(side);
    ['.puzzle-bank', '.puzzle-tools', '.puzzle-selection-controls', '.puzzle-interaction-status', '.check-row'].forEach(selector => side.append(content.querySelector(selector)));
    const help = document.createElement('section'); help.className = 'puzzle-help-stage'; help.setAttribute('aria-label', 'Οδηγίες χειρισμού'); help.append($('instructions')); root.append(help);
    const feedback = document.createElement('section'); feedback.className = 'puzzle-feedback-stage'; feedback.setAttribute('aria-label', 'Ανατροφοδότηση'); feedback.append($('feedback')); root.append(feedback);
    const actions = document.createElement('div'); actions.className = 'puzzle-feedback-actions'; feedback.append(actions);
    const back = document.createElement('button'); back.className = 'secondary'; back.type = 'button'; back.textContent = 'Επιστροφή στο σχέδιο';
    back.addEventListener('click', () => stage('editing')); actions.append(back);
    const nextHome = $('next-molecule').parentNode;
    pagers.push(Viewport.pager(port, { axis: 'y', overlap: 64, label: 'Πλαίσιο σύνθεσης — όλα τα κομμάτια' }));
    pagers.push(Viewport.pager($('target-name'), { axis: 'x', label: 'Πλήρες όνομα' }));
    pagers.push(Viewport.pager($('instructions').querySelector('.helper-methods'), { axis: 'y', label: 'Οδηγίες' }));
    pagers.push(Viewport.pager($('feedback'), { axis: 'y', label: 'Ανατροφοδότηση' }));
    function refresh() { pagers.forEach(pager => pager.refresh()); mounted?.refresh(); }
    function stage(key) {
      if (key === 'feedback' && $('feedback').hidden) key = 'editing';
      root.dataset.puzzleView = key;
      buttons.forEach((button, view) => { button.setAttribute('aria-pressed', String(view === key)); button.hidden = view === 'feedback' && $('feedback').hidden; });
      if (key === 'feedback') actions.append($('next-molecule')); else nextHome.append($('next-molecule'));
      refresh();
    }
    root.addEventListener('nl-level-stage', event => { root.classList.toggle('puzzle-choosing', !!event.detail.expanded); refresh(); });
    mounted = Viewport.mount(root, { kind: 'puzzle', onResize({ width, height }) {
      root.classList.toggle('puzzle-compact', width < 900 || height < 570);
      pagers.forEach(pager => pager.refresh());
    } });
    stage('editing');
    return { refresh, stage, feedback(correct) { back.textContent = correct ? 'Επιθεώρηση σχεδίου' : 'Επιστροφή στο σχέδιο'; stage('feedback'); },
      destroy() { pagers.forEach(pager => pager.destroy()); mounted?.destroy(); } };
  }
  function announce(text) { $('interaction-status').textContent = text; }
  function clearFeedback() {
    $('feedback').hidden = true;
    $('feedback').textContent = '';
    $('feedback').classList.remove('success');
  }
  function saveChange(before) {
    undo.push(before || clone(graph));
    if (undo.length > 50) undo.shift();
    submitted = false;
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
    $('next-molecule').disabled = busy || !current || (!lesson && practice.level === null);
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
    publish();
  }
  function postSize() {
    if (viewportEnabled) { viewportUI?.refresh(); return; }
    if (lesson) {
      if (lesson.sizeFrame !== null || stopped) return;
      lesson.sizeFrame = requestAnimationFrame(() => {
        lesson.sizeFrame = null;
        if (!lesson.current || !lesson.current.loaded || stopped) return;
        const height = Math.ceil(document.body.getBoundingClientRect().height);
        if (Number.isFinite(height) && height !== lesson.lastHeight) { lesson.lastHeight = height; postLesson('resize', { height }); }
      });
    } else if (embedded && parent !== window) parent.postMessage({ type: 'namelecule-puzzle-size', height: document.documentElement.scrollHeight }, location.origin);
  }
  function cancelReveal() { clearTimeout(revealTimer); }
  function reveal(el) {
    if (viewportEnabled) { viewportUI?.refresh(); return; }
    cancelReveal();
    revealTimer = setTimeout(() => {
      const r = el.getBoundingClientRect();
      if (lesson) {
        if (lesson.current && lesson.current.loaded) postLesson('reveal', { startY: r.top + scrollY,
          endY: r.bottom + scrollY, purpose: el === $('feedback') ? 'feedback' : el === $('piece-bank') ? 'entry' : 'construction' });
        return;
      }
      if (r.bottom > innerHeight - 14 || r.top < 10) {
        el.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth' });
      }
    }, 180);
  }
  ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(type => addEventListener(type, () => {
    if (viewportEnabled) return;
    cancelReveal(); if (lesson && lesson.current && lesson.current.loaded) postLesson('scroll-interrupt', {});
  }, { passive: true }));

  function addGroup(hydrogens, point) {
    if (busy || solved || graph.nodes.length >= E.MAX_NODES) return;
    const wanted = point || { x: W / 2, y: H / 2 };
    const p = freePoint(wanted) || fitPoint(wanted);
    saveChange();
    let id; do { id = 'piece-' + (++serial); } while (graph.nodes.some(n => n.id === id));
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
    graph = undo.pop(); submitted = false; selected = null; bondStart = null; clearFeedback(); render(); announce('Η τελευταία αλλαγή αναιρέθηκε.');
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
    attempts++; submitted = true;
    $('feedback').hidden = false; $('feedback').textContent = result.message;
    $('feedback').classList.toggle('success', result.correct);
    if (result.correct && lesson && lesson.current.explanation) {
      const explanation = document.createElement('p'); explanation.textContent = lesson.current.explanation; $('feedback').append(explanation);
    }
    if (result.correct) {
      solved = true; bonding = false; bondStart = null;
      $('game-status').textContent = 'Σωστά! Η δομή σου αντιστοιχεί στο όνομα ' + current.name + '.';
    }
    render(); viewportUI?.feedback(result.correct); reveal($('feedback'));
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
    attempts = 0; submitted = false;
    $('target-name').textContent = current.name;

    $('game-status').textContent = 'Διάβασε το όνομα και φτιάξε τον συνεπτυγμένο τύπο του μορίου.';
    clearFeedback(); viewportUI?.stage('editing'); announce('Νέο μόριο. Το πλαίσιο είναι κενό.'); render();
    reveal($('piece-bank'));
  }
  function freshSeed() { return Array.from(crypto.getRandomValues(new Uint32Array(4)), n => n.toString(16).padStart(8, '0')).join(''); }
  function savePractice() {
    const slot = practice.slots.get(practice.level);
    if (slot && current) slot.saved = { moleculeId: current.id, state: snapshot(), undo: clone(undo),
      selected: clone(selected), bonding, bondStart, serial };
  }
  function nextPractice() {
    const slot = practice.slots.get(practice.level);
    if (!slot) return;
    const id = slot.deck.next();
    busy = false; startRound(catalog.findIndex(m => m.id === id));
    slot.saved = null;
  }
  function selectPractice(selection) {
    if (lesson || stopped || selection.category !== 'alkanes' || selection.level === practice.level) return;
    // Complete/cancel interaction against its original graph before switching.
    finishDrag(null, true); cancelReveal(); savePractice();
    practice.level = selection.level;
    practice.controls.set({ selectedLevel: practice.level });
    if (!practice.slots.has(practice.level)) practice.slots.set(practice.level, {
      deck: Levels.createDeck(Levels.poolFor(practice.level, catalog.map(m => m.id)), { seed: freshSeed(), avoid: current?.id }), saved: null });
    const saved = practice.slots.get(practice.level).saved;
    if (!saved) { nextPractice(); return; }
    busy = false; startRound(catalog.findIndex(m => m.id === saved.moleculeId));
    graph = clone(saved.state.graph); attempts = saved.state.attempts; submitted = saved.state.submitted;
    undo = clone(saved.undo); selected = clone(saved.selected); bonding = saved.bonding; bondStart = saved.bondStart; serial = saved.serial;
    if (submitted) {
      const result = E.grade(graph, current.target); solved = result.correct;
      $('feedback').hidden = false; $('feedback').textContent = result.message; $('feedback').classList.toggle('success', solved);
    }
    render(); if (submitted) viewportUI?.feedback(solved); announce('Η προηγούμενη προσπάθειά σου σε αυτό το επίπεδο διατηρήθηκε.');
  }
  function preparePractice() {
    if (!Levels) throw new Error('Δεν φορτώθηκαν τα επίπεδα του παιχνιδιού. Ανανέωσε τη σελίδα.');
    const ids = catalog.map(m => m.id);
    if ([1, 2, 3].some(level => Levels.poolFor(level, ids).length !== [5, 4, 5][level - 1])) throw new Error('Η βιβλιοθήκη των 14 αλκανίων δεν είναι πλήρης.');
    if (!practice.controls) practice.controls = Levels.mount($('game-levels'), { compact: viewportEnabled, availableIds: ids,
      allowedLevels: [1, 2, 3], selectedLevel: null, category: 'alkanes', onSelect: selectPractice });
    busy = true; current = null;
    $('target-name').textContent = 'Διάλεξε επίπεδο για να εμφανιστεί το όνομα.';
    $('game-status').textContent = 'Διάλεξε επίπεδο για αυτόματη ανάθεση μορίου.';
  }
  $('next-molecule').addEventListener('click', () => {
    if (lesson || busy || practice.level === null) return;
    nextPractice(); reveal($('target-name'));
  });
  function restoreGraph(raw) {
    const blank = { nodes: [], bonds: [] };
    if (!raw || !Array.isArray(raw.nodes) || !Array.isArray(raw.bonds) || raw.nodes.length > 32 || raw.bonds.length > 64) return blank;
    const ids = new Set();
    for (const n of raw.nodes) {
      if (!n || typeof n.id !== 'string' || !n.id || n.id.length > 128 || ids.has(n.id) ||
          !Number.isInteger(n.hydrogens) || n.hydrogens < 0 || n.hydrogens > 4 ||
          !Number.isFinite(n.x) || n.x < 0 || n.x > W || !Number.isFinite(n.y) || n.y < 0 || n.y > H) return blank;
      ids.add(n.id);
    }
    if (raw.bonds.some(b => !b || !ids.has(b.a) || !ids.has(b.b) || b.order !== 1)) return blank;
    return { nodes: raw.nodes.map(n => ({ id: n.id, hydrogens: n.hydrogens, x: n.x, y: n.y })),
      bonds: raw.bonds.map(b => ({ a: b.a, b: b.b, order: b.order })) };
  }
  function validateLessonContext(data) {
    if (!Object.prototype.hasOwnProperty.call(data, 'context')) return null;
    if (!Levels) throw new Error('Δεν φορτώθηκε η πολιτική των επιπέδων.');
    const context = Levels.validateContext(data.context);
    if (context.seed === null || !Levels.contextIds(context).includes(data.moleculeId)) throw new Error('Το μόριο δεν ανήκει στην προσπάθεια αυτού του επιπέδου.');
    return context;
  }
  addEventListener('message', async event => {
    if (!lesson || stopped || event.origin !== location.origin || event.source !== parent) return;
    const d = event.data;
    if (d?.command === 'viewport') {
      if (viewportEnabled && validViewportMessage(d)) viewportUI?.refresh();
      return;
    }
    if (!d || d.channel !== CHANNEL || d.session !== lessonSession || d.command !== 'load' ||
        !Number.isSafeInteger(d.requestId) || d.requestId <= lesson.lastRequest ||
        typeof d.attemptId !== 'string' || !d.attemptId || d.attemptId.length > 160) return;
    lesson.lastRequest = d.requestId;
    let context;
    try {
      context = validateLessonContext(d);
      if (!(context ? Levels.contextIds(context) : LEGACY_IDS).includes(d.moleculeId)) throw new Error('Το μόριο δεν ανήκει σε αυτή την άσκηση.');
    } catch (error) {
      parent.postMessage({ channel: CHANNEL, session: lessonSession, type: 'error', requestId: d.requestId,
        attemptId: d.attemptId, moleculeId: d.moleculeId, message: error.message }, location.origin); return;
    }
    const controlled = { requestId: d.requestId, attemptId: d.attemptId, moleculeId: d.moleculeId,
      ...(context ? { context } : {}), explanation: typeof d.explanation === 'string' ? d.explanation.slice(0, 4000) : '', loaded: false };
    // load() increments the source request serial and aborts old analysis before
    // clearing; switching contexts never lets a late catalog/round replace it.
    lesson.current = controlled; finishDrag(null, true); cancelReveal();
    const loading = load(context?.source === 'enriched' ? CURRENT_CATALOG : LEGACY_CATALOG, false);
    current = null; graph = { nodes: [], bonds: [] }; undo = []; selected = null; bondStart = null; bonding = false;
    $('target-name').textContent = 'Περιμένουμε το μόριο του μαθήματος…'; clearFeedback(); render();
    if (!await loading || stopped || controlled !== lesson.current) return;
    const index = catalog.findIndex(m => m.id === d.moleculeId);
    if (index < 0 || d.correctName !== catalog[index].name) { postLesson('error', {}); return; }
    busy = false; startRound(index);
    const raw = d.initialState || {};
    graph = restoreGraph(raw.graph);
    serial = graph.nodes.reduce((value, n) => Math.max(value, /^piece-\d{1,9}$/.test(n.id) ? Number(n.id.slice(6)) : 0), 0);
    attempts = Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0;
    submitted = raw.submitted === true && attempts > 0 && graph.nodes.length > 0;
    const result = submitted ? E.grade(graph, current.target) : null;
    solved = !!(result && result.correct);
    if (result) {
      $('feedback').hidden = false; $('feedback').textContent = result.message; $('feedback').classList.toggle('success', solved);
      if (solved && controlled.explanation) { const p = document.createElement('p'); p.textContent = controlled.explanation; $('feedback').append(p); }
    }
    render(); if (submitted) viewportUI?.feedback(solved);
    lesson.lastSnapshot = JSON.stringify(snapshot()); controlled.loaded = true; lesson.lastHeight = null;
    postLesson('loaded', { state: snapshot() }); postSize(); reveal($('piece-bank'));
  });
  addEventListener('keydown', event => { if (lesson && event.key === 'Escape') { event.preventDefault(); postLesson('exit', {}); } });
  $('retry-load').addEventListener('click', () => load(lesson
    ? (lesson.current?.context?.source === 'enriched' ? CURRENT_CATALOG : LEGACY_CATALOG) : catalogDescriptor));
  const media = matchMedia('(max-width:600px)');
  function instructionsMode() { $('instructions').open = viewportEnabled || !media.matches; }
  media.addEventListener('change', instructionsMode); instructionsMode();
  async function digest(value) {
    const bytes = await crypto.subtle.digest('SHA-256', typeof value === 'string' ? new TextEncoder().encode(value) : value);
    return Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, '0')).join('');
  }
  async function load(descriptor = catalogDescriptor, announceReady = true) {
    const request = ++loadingSerial;
    if (loadController) loadController.abort();
    const controller = new AbortController();
    loadController = controller;
    const signal = controller.signal, timer = setTimeout(() => controller.abort(), 45000);
    busy = true; controls(); $('retry-load').hidden = true; $('game-status').classList.remove('error');
    $('game-status').textContent = 'Ετοιμάζουμε τα ονόματα και τα κομμάτια του παζλ.';
    try {
      let ready = verifiedCatalogs.get(descriptor.sha256);
      if (!ready) {
        const response = await fetch(new URL(descriptor.file, location.href), { cache: 'no-cache', signal });
        if (!response.ok) throw new Error('Δεν φορτώθηκαν τα δεδομένα των μορίων.');
        const bytes = await response.arrayBuffer();
        if (await digest(bytes) !== descriptor.sha256) throw new Error('Ο έλεγχος της έκδοσης των μορίων απέτυχε.');
        const data = JSON.parse(new TextDecoder().decode(bytes));
        if (data.schemaVersion !== 1 || (data.catalogVersion || 1) !== descriptor.version ||
            data.revision !== descriptor.revision || data.engineSHA256 !== ENGINE_SHA ||
            !Array.isArray(data.molecules) || data.molecules.length !== descriptor.ids.length ||
            data.molecules.some((m, index) => !m || m.id !== descriptor.ids[index])) {
          throw new Error('Τα δεδομένα του παιχνιδιού δεν είναι συμβατά.');
        }
        ready = [];
        for (const m of data.molecules) {
          if (signal.aborted) throw new Error('Η φόρτωση ακυρώθηκε.');
          if (typeof m.mol !== 'string' || await digest(m.mol) !== m.sourceSHA256) throw new Error('Ο έλεγχος της πηγής ενός μορίου απέτυχε.');
          const target = E.parseMol(m.mol);
          const analysis = await window.NameleculeChemistryClient.analyze({ id: m.id, mol: m.mol }, { engineSHA256: data.engineSHA256, signal });
          if (typeof analysis.name !== 'string' || !analysis.name.trim()) throw new Error('Δεν προσδιορίστηκε το όνομα ενός μορίου.');
          ready.push({ id: m.id, name: analysis.name, target });
      }
      if (signal.aborted || request !== loadingSerial) return false;
      verifiedCatalogs.set(descriptor.sha256, ready);
      }
      if (signal.aborted || request !== loadingSerial) return false;
      catalogDescriptor = descriptor; catalog = ready;

      if (lesson) {
        busy = true; $('target-name').textContent = 'Περιμένουμε το μόριο του μαθήματος…'; if (announceReady) postLesson('ready', {});
      } else preparePractice();
      return true;
    } catch (error) {
      if (request !== loadingSerial) return false;
      $('game-status').classList.add('error');
      $('game-status').textContent = 'Το παιχνίδι δεν ετοιμάστηκε. ' + (error.name === 'AbortError' ? 'Η φόρτωση άργησε ή ακυρώθηκε.' : error.message);
      $('retry-load').hidden = false;
      postLesson('error', {}); return false;
    } finally { clearTimeout(timer); if (request === loadingSerial) { controls(); postSize(); } }
  }
  let resizePending = 0;
  const boardObserver = new ResizeObserver(() => {
    cancelAnimationFrame(resizePending);
    resizePending = requestAnimationFrame(() => {
      if (drag) finishDrag(null, true);
      // render() frames the entire candidate, including solved/undo states.
      render();
    });
  });
  boardObserver.observe(board);
  const bodyObserver = viewportEnabled ? null : new ResizeObserver(postSize);
  bodyObserver?.observe(document.body);
  addEventListener('pagehide', () => { if (loadController) loadController.abort(); finishDrag(null, true); cancelReveal(); stopped = true; viewportUI?.destroy(); boardObserver.disconnect(); bodyObserver?.disconnect(); media.removeEventListener('change', instructionsMode); cancelAnimationFrame(resizePending); practice.controls?.destroy(); if (lesson && lesson.sizeFrame !== null) cancelAnimationFrame(lesson.sizeFrame); });
  if (viewportEnabled) viewportUI = createViewportUI();
  load();
}());
