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
  const inlineResults = !!lesson && viewportEnabled;
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
  let selected = null, solved = false, busy = true;
  let serial = 0, drag = null, ignoreClickUntil = 0, loadController = null;
  let revealTimer = 0, loadingSerial = 0;
  let attempts = 0, submitted = false, stopped = false;
  let constructionEnabled = !lesson, pendingBond = null, pickerOwner = null, snapPreview = null, panning = false;
  const constructionInstructionHTML = $('construction-instructions').innerHTML;
  function updateConstructionInstructions() {
    $('construction-instructions').innerHTML = constructionEnabled ? constructionInstructionHTML :
      constructionInstructionHTML.replace('απλό, διπλό ή τριπλό δεσμό', 'απλό δεσμό');
    $('construction-intro').textContent = constructionEnabled ?
      'Από το όνομα στη δομή, με ομάδες ατόμων και δεσμούς μεταξύ ατόμων C.' :
      'Από το όνομα στη δομή, με ομάδες ατόμων και απλούς δεσμούς.';
  }
  updateConstructionInstructions();
  const clone = value => JSON.parse(JSON.stringify(value));
  const label = n => n === 0 ? 'C' : 'CH' + (n === 1 ? '' : ['₀', '₁', '₂', '₃', '₄'][n]);
  const orderName = order => ['απλός', 'διπλός', 'τριπλός'][order - 1];
  function snapshot() { return { graph: clone(graph), attempts, submitted,
    ...(constructionEnabled && pendingBond ? { construction: { version: 1, pendingBond: clone(pendingBond) } } : {}) }; }
  function constructionState() { return { graph: clone(graph), pendingBond: clone(pendingBond) }; }
  function restoreConstruction(state) { graph = clone(state.graph); pendingBond = clone(state.pendingBond || null); }
  function remainingCapacity(node, candidate = graph) {
    return 4 - node.hydrogens - candidate.bonds.reduce((total, edge) => total + (edge.a === node.id || edge.b === node.id ? edge.order : 0), 0);
  }
  function canJoin(owner, target, order) {
    return !!owner && !!target && owner.id !== target.id && Number.isInteger(order) && order >= 1 && order <= (constructionEnabled ? 3 : 1) &&
      !graph.bonds.some(edge => edge.a === owner.id && edge.b === target.id || edge.a === target.id && edge.b === owner.id) &&
      remainingCapacity(owner) >= order && remainingCapacity(target) >= order;
  }
  function restorePending(raw) {
    const p = raw?.version === 1 && raw.pendingBond, owner = p && graph.nodes.find(n => n.id === p.owner);
    return constructionEnabled && owner && Number.isInteger(p.order) && p.order >= 1 && p.order <= 3 &&
      Number.isFinite(p.dx) && Number.isFinite(p.dy) && Math.abs(p.dx) <= 1 && Math.abs(p.dy) <= 1 &&
      Math.abs(Math.hypot(p.dx, p.dy) - 1) <= 1e-6 && remainingCapacity(owner) >= p.order
      ? { owner: p.owner, order: p.order, dx: p.dx, dy: p.dy } : null;
  }
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
  function puzzleRegionEnvelope(target, width, metrics) {
    // The verified target determines construction room. Candidate coordinates,
    // selections, pending bonds and Undo never participate in popup sizing.
    const branchRows = Math.min(2, target.nodes.reduce((total, node) => total + Math.max(0, 2 - node.hydrogens), 0));
    const construction = 260 + branchRows * 30;
    const toolbar = metrics.tool + 11, bank = metrics.piece + 12;
    const result = 118; // readable feedback window and its existing local pager
    const drawing = construction + toolbar + 4;
    const controls = bank + metrics.check + result + 16;
    // Wide views put construction and feedback beside each other. Narrow
    // views reserve both the initial stacked controls and inline-result view.
    const initial = width >= 900 ? Math.max(drawing, controls) : bank + drawing + 34 + metrics.check + 20;
    const feedback = width >= 900 ? Math.max(drawing, controls) : bank + construction + result + 12;
    return Math.ceil(52 + 16 + Math.max(initial, feedback, 220) + 2);
  }
  function createViewportUI() {
    const root = $('game'), panel = root.querySelector('.puzzle-assembly-panel');
    root.classList.toggle('nl-inline-results', inlineResults);
    const content = panel.querySelector('.puzzle-assembly-content');
    const toggle = $('help-toggle'), pagers = [];
    let mounted = null, view = 'editing', returnView = 'editing', lastFocus = board;
    const port = document.createElement('div'); port.className = 'puzzle-board-port'; board.before(port); port.append(board);
    const help = document.createElement('section'); help.id = 'puzzle-help-stage'; help.className = 'puzzle-help-stage';
    help.setAttribute('aria-label', 'Οδηγίες χειρισμού'); help.append($('instructions')); panel.append(help);
    const feedback = document.createElement('section'); feedback.className = 'puzzle-feedback-stage';
    feedback.setAttribute('aria-label', 'Ανατροφοδότηση'); feedback.append($('feedback')); panel.append(feedback);
    const actions = document.createElement('div'); actions.className = 'puzzle-feedback-actions'; feedback.append(actions);
    const back = document.createElement('button'); back.className = 'secondary'; back.type = 'button'; back.id = 'return-to-puzzle';
    back.textContent = 'Επιστροφή στο παζλ'; back.addEventListener('click', () => stage('editing', true)); actions.append(back);
    const nextHome = $('next-molecule').parentNode;
    if (viewportEnabled) {
      pagers.push(Viewport.pager(port, { axis: 'y', overlap: 64, label: 'Πλαίσιο σύνθεσης — όλα τα κομμάτια' }));
      pagers.push(Viewport.pager($('target-name'), { axis: 'x', label: 'Πλήρες όνομα' }));
      pagers.push(Viewport.pager($('instructions').querySelector('.helper-methods'), { axis: 'y', label: 'Οδηγίες' }));
      pagers.push(Viewport.pager($('feedback'), { axis: 'y', label: 'Ανατροφοδότηση' }));
    }
    function refresh() { pagers.forEach(pager => pager.refresh()); mounted?.refresh(); }
    function preferred() {
      const controlled = lesson?.current;
      if (!inlineResults || !controlled?.loaded || !current || busy || stopped) return null;
      const natural = (element, floor) => {
        const style = getComputedStyle(element), px = value => parseFloat(value) || 0;
        const line = px(style.lineHeight) || px(style.fontSize) * 1.25;
        return Math.max(floor, px(style.minHeight), line + px(style.paddingTop) + px(style.paddingBottom) + px(style.borderTopWidth) + px(style.borderBottomWidth));
      };
      const metrics = { tool: natural($('undo-action'), 44), piece: natural($('piece-bank').querySelector('.puzzle-piece'), 44),
        check: natural($('check-answer'), 44) };
      const height = puzzleRegionEnvelope(current.target, root.clientWidth, metrics);
      const key = ['puzzle', controlled.requestId, controlled.attemptId, controlled.moleculeId].join(':');
      return Viewport.preferred(root, panel, height, key);
    }
    function restoreFocus() {
      const focus = lastFocus?.isConnected && !lastFocus.disabled && lastFocus.getClientRects().length ? lastFocus : board;
      focus.focus({ preventScroll: true });
    }
    function stage(key, focus = false) {
      if (!['editing', 'help', 'feedback'].includes(key)) key = 'editing';
      if (key === 'feedback' && $('feedback').hidden) key = 'editing';
      const success = solved && !$('feedback').hidden && $('feedback').classList.contains('success');
      const inline = !$('feedback').hidden && (inlineResults || success);
      if (inline && key === 'feedback') key = 'editing';
      root.classList.toggle('puzzle-solved', success);
      root.classList.toggle('nl-has-inline-result', inlineResults && inline);
      feedback.classList.toggle('puzzle-inline-success', success);
      feedback.classList.toggle('nl-inline-result', inlineResults && inline);
      if (inline) content.append(feedback); else panel.append(feedback);
      back.hidden = inline;
      view = key; root.dataset.puzzleView = key;
      toggle.setAttribute('aria-expanded', String(key === 'help'));
      if (inline || key === 'feedback') actions.append($('next-molecule')); else nextHome.append($('next-molecule'));
      refresh();
      if (focus) {
        if (key === 'feedback') {
          const target = feedback.contains(lastFocus) && lastFocus.isConnected && !lastFocus.disabled ? lastFocus : back;
          target.focus({ preventScroll: true });
        } else restoreFocus();
      }
    }
    function closeHelp() {
      if (view !== 'help') return false;
      stage(returnView, true); return true;
    }
    panel.addEventListener('focusin', event => {
      if (view !== 'help' && event.target !== toggle) lastFocus = event.target;
    });
    toggle.addEventListener('click', () => {
      if (closeHelp()) return;
      if (drag) finishDrag(null, true);
      returnView = view; stage('help');
    });
    root.addEventListener('nl-level-stage', event => { root.classList.toggle('puzzle-choosing', !!event.detail.expanded); refresh(); });
    if (viewportEnabled) mounted = Viewport.mount(root, { kind: 'puzzle', preferred, onDemand(detail) { postLesson('layout-demand', detail); }, onResize({ width, height, availableHeight }) {
      root.classList.toggle('puzzle-compact', width < 900 || (inlineResults ? availableHeight : height) < 570);
      pagers.forEach(pager => pager.refresh());
    } });
    stage('editing');
    return { refresh, stage, closeHelp, resetName() { $('target-name').scrollLeft = 0; refresh(); },
      feedback(correct, focus = false) {
        if (inlineResults) $('feedback').scrollTop = 0;
        stage(correct ? 'editing' : 'feedback', !correct && focus);
        if (correct && focus) {
          // Check is disabled and hidden after success. Keep keyboard focus in
          // the visible workspace; a restored lesson never steals parent focus.
          const next = $('next-molecule');
          (next.getClientRects().length && !next.disabled ? next : $('assembly-title')).focus({ preventScroll: true });
        }
      },
      destroy() { pagers.forEach(pager => pager.destroy()); mounted?.destroy(); } };
  }
  function announce(text) { $('interaction-status').textContent = text; }
  function clearFeedback() {
    $('feedback').hidden = true;
    $('feedback').textContent = '';
    $('feedback').classList.remove('success');
    if (inlineResults) viewportUI?.stage('editing');
  }
  function saveChange(before) {
    undo.push(before || constructionState());
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
  function freePoint(wanted, except, candidateGraph = graph) {
    const b = bounds(), stepX = b.halfWidth * 2 + 18, stepY = b.halfHeight * 2 + 24;
    const free = point => !candidateGraph.nodes.some(n => n.id !== except &&
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
      // A shared translation can introduce subpixel roundoff in a subtraction;
      // it must not trigger a new packing of an already separated construction.
      fitted.every((other, j) => i === j || Math.abs(n.x - other.x) * r.width / W + 1e-6 >= width + 8 ||
        Math.abs(n.y - other.y) * r.height / H + 1e-6 >= 52));
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
  function pendingPoint(candidate = pendingBond, candidateGraph = graph) {
    if (!candidate) return null;
    const owner = candidateGraph.nodes.find(n => n.id === candidate.owner), r = board.getBoundingClientRect();
    if (!owner || r.width <= 0 || r.height <= 0) return null;
    const sx = r.width / W, sy = r.height / H;
    const length = Math.hypot(candidate.dx * sx, candidate.dy * sy);
    const ux = candidate.dx * sx / length, uy = candidate.dy * sy / length;
    const ox = owner.x * sx, oy = owner.y * sy, box = bounds(), marginX = box.x * sx, marginY = box.y * sy;
    const roomX = ux > 0 ? (r.width - marginX - ox) / ux : ux < 0 ? (marginX - ox) / ux : Infinity;
    const roomY = uy > 0 ? (r.height - marginY - oy) / uy : uy < 0 ? (marginY - oy) / uy : Infinity;
    const pixels = Math.max(0, Math.min(102, roomX, roomY));
    return { x: owner.x + ux * pixels / sx, y: owner.y + uy * pixels / sy };
  }
  function placementClear(point, except, candidateGraph = graph) {
    const r = board.getBoundingClientRect(), width = matchMedia('(max-width:650px)').matches ? 50 : 64;
    return candidateGraph.nodes.every(n => n.id === except || Math.abs(n.x - point.x) * r.width / W + 1e-6 >= width + 8 ||
      Math.abs(n.y - point.y) * r.height / H + 1e-6 >= 52);
  }
  function segmentHitsBox(start, end, center, halfWidth, halfHeight) {
    let near = 0, far = 1;
    for (const [axis, half] of [['x', halfWidth], ['y', halfHeight]]) {
      const delta = end[axis] - start[axis], low = center[axis] - half, high = center[axis] + half;
      if (Math.abs(delta) < 1e-9) {
        if (start[axis] < low || start[axis] > high) return false;
      } else {
        const a = (low - start[axis]) / delta, b = (high - start[axis]) / delta;
        near = Math.max(near, Math.min(a, b)); far = Math.min(far, Math.max(a, b));
        if (near > far) return false;
      }
    }
    return true;
  }
  function bondCorridorClear(a, b, order, candidateGraph) {
    const r = board.getBoundingClientRect(), box = bounds(), sx = r.width / W, sy = r.height / H;
    const screen = p => ({ x: p.x * sx, y: p.y * sy });
    const start = screen(bondEnd(a, b)), end = screen(bondEnd(b, a));
    const spread = (order === 3 ? 6 : order === 2 ? 3 : 0) + 3;
    return !candidateGraph.nodes.some(n => n.id !== a.id && n.id !== b.id &&
      segmentHitsBox(start, end, screen(n), box.halfWidth * sx + spread, box.halfHeight * sy + spread));
  }
  function incidentNeighbours(id, candidateGraph) {
    const neighbours = new Map();
    for (const edge of candidateGraph.bonds) {
      if (edge.a !== id && edge.b !== id) continue;
      const other = candidateGraph.nodes.find(n => n.id === (edge.a === id ? edge.b : edge.a));
      if (!other || other.id === id) return null;
      neighbours.set(other.id, other);
    }
    return [...neighbours.values()];
  }
  function nodePositionValid(id, point, candidateGraph = graph) {
    const node = candidateGraph.nodes.find(n => n.id === id), b = bounds(), r = b.r;
    if (!node || !Number.isFinite(point?.x) || !Number.isFinite(point?.y) || r.width <= 0 || r.height <= 0) return false;
    const sx = r.width / W, sy = r.height / H, eps = 1e-6;
    if ((point.x - b.x) * sx < -eps || (W - b.x - point.x) * sx < -eps ||
        (point.y - b.y) * sy < -eps || (H - b.y - point.y) * sy < -eps || !placementClear(point, id, candidateGraph)) return false;
    const moved = { ...node, ...point };
    const next = { nodes: candidateGraph.nodes.map(n => n.id === id ? moved : n), bonds: candidateGraph.bonds };
    for (const edge of next.bonds) {
      const a = next.nodes.find(n => n.id === edge.a), other = next.nodes.find(n => n.id === edge.b);
      if (!a || !other) return false;
      if (edge.a === id || edge.b === id) {
        const dx = (a.x - other.x) * sx, dy = (a.y - other.y) * sy;
        if (a.id === other.id || Math.abs(dx) > eps && Math.abs(dy) > eps || Math.hypot(dx, dy) < eps ||
            !bondCorridorClear(a, other, edge.order, next)) return false;
      } else {
        // A moved label cannot cover an unrelated existing bond either.
        const start = bondEnd(a, other), end = bondEnd(other, a);
        const spread = (edge.order === 3 ? 6 : edge.order === 2 ? 3 : 0) + 3;
        if (segmentHitsBox({ x: start.x * sx, y: start.y * sy }, { x: end.x * sx, y: end.y * sy },
          { x: point.x * sx, y: point.y * sy }, b.halfWidth * sx + spread, b.halfHeight * sy + spread)) return false;
      }
    }
    return true;
  }
  function projectNodePosition(id, wanted, candidateGraph = graph) {
    const node = candidateGraph.nodes.find(n => n.id === id), neighbours = incidentNeighbours(id, candidateGraph), b = bounds();
    if (!node || !neighbours || !Number.isFinite(wanted?.x) || !Number.isFinite(wanted?.y) || b.r.width <= 0 || b.r.height <= 0) return null;
    const valid = p => {
      if (!nodePositionValid(id, p, candidateGraph)) return false;
      if (pendingBond?.owner !== id) return true;
      return pendingDirectionClear(pendingBond, { nodes: candidateGraph.nodes.map(n => n.id === id ? { ...n, ...p } : n), bonds: candidateGraph.bonds });
    };
    if (!neighbours.length) {
      const fitted = fitPoint(wanted);
      if (valid(fitted)) return fitted;
      const free = freePoint(wanted, id, candidateGraph);
      return free && valid(free) ? free : null;
    }
    const sx = b.r.width / W, sy = b.r.height / H, width = matchMedia('(max-width:650px)').matches ? 50 : 64;
    const xs = [wanted.x, node.x, b.x, W - b.x], ys = [wanted.y, node.y, b.y, H - b.y];
    candidateGraph.nodes.forEach(n => {
      if (n.id === id) return;
      xs.push(n.x, n.x - (width + 8) / sx, n.x + (width + 8) / sx);
      ys.push(n.y, n.y - 52 / sy, n.y + 52 / sy);
    });
    const anchor = neighbours[0];
    function corridorCuts(axis, fixed) {
      const along = axis === 'x' ? sx : sy, across = axis === 'x' ? sy : sx;
      const cross = axis === 'x' ? 'y' : 'x', cuts = axis === 'x' ? xs : ys;
      const half = (axis === 'x' ? b.halfWidth : b.halfHeight) * along;
      const halfCross = (axis === 'x' ? b.halfHeight : b.halfWidth) * across;
      const add = value => { if (Number.isFinite(value)) cuts.push(value / along); };
      // A fixed segment expanded by the moving label is a convex corridor.
      // Intersect it with this H/V movement line, including slanted old bonds.
      candidateGraph.bonds.forEach(edge => {
        if (edge.a === id || edge.b === id) return;
        const a = candidateGraph.nodes.find(n => n.id === edge.a), c = candidateGraph.nodes.find(n => n.id === edge.b);
        if (!a || !c) return;
        const start = bondEnd(a, c), end = bondEnd(c, a), spread = (edge.order === 3 ? 6 : edge.order === 2 ? 3 : 0) + 3;
        const delta = (end[cross] - start[cross]) * across;
        let low = 0, high = 1;
        if (Math.abs(delta) < 1e-9) {
          if (Math.abs(start[cross] * across - fixed) > halfCross + spread) return;
        } else {
          const t1 = (fixed - halfCross - spread - start[cross] * across) / delta;
          const t2 = (fixed + halfCross + spread - start[cross] * across) / delta;
          low = Math.max(0, Math.min(t1, t2)); high = Math.min(1, Math.max(t1, t2));
          if (low > high) return;
        }
        const v1 = (start[axis] + (end[axis] - start[axis]) * low) * along;
        const v2 = (start[axis] + (end[axis] - start[axis]) * high) * along;
        add(Math.min(v1, v2) - half - spread); add(Math.max(v1, v2) + half + spread);
      });
      // An incident corridor has two clipped ends: constant label radius or
      // 45% of a short edge. Include both affine branches of their boundaries.
      neighbours.forEach(neighbour => {
        if (Math.abs(neighbour[cross] * across - fixed) > 1e-6) return;
        const edge = candidateGraph.bonds.find(e => e.a === id && e.b === neighbour.id || e.b === id && e.a === neighbour.id);
        const spread = (edge.order === 3 ? 6 : edge.order === 2 ? 3 : 0) + 3, origin = neighbour[axis] * along;
        add(origin - half / .45); add(origin + half / .45);
        candidateGraph.nodes.forEach(obstacle => {
          if (obstacle.id === id || obstacle.id === neighbour.id || Math.abs(obstacle[cross] * across - fixed) > halfCross + spread) return;
          for (const value of [obstacle[axis] * along - half - spread, obstacle[axis] * along + half + spread]) {
            add(value - half); add(value + half);
            add((value - .45 * origin) / .55); add((value - .55 * origin) / .45);
          }
        });
      });
      if (pendingBond?.owner === id) {
        const length = Math.hypot(pendingBond.dx * sx, pendingBond.dy * sy);
        const ux = pendingBond.dx * sx / length, uy = pendingBond.dy * sy / length;
        const spread = (pendingBond.order === 3 ? 6 : pendingBond.order === 2 ? 3 : 0) + 3;
        const min = (axis === 'x' ? b.x : b.y) * along, max = (axis === 'x' ? W - b.x : H - b.y) * along;
        // Clipping makes the endpoint piecewise affine in the moving coordinate,
        // including arbitrary unit directions accepted from older saved rounds.
        const ox = axis === 'x' ? [1, 0] : [0, fixed], oy = axis === 'y' ? [1, 0] : [0, fixed];
        const value = (line, z) => line[0] * z + line[1];
        const subtract = (a, c) => [a[0] - c[0], a[1] - c[1]];
        const offsetLine = (origin, direction, distance) => [origin[0] + direction * distance[0], origin[1] + direction * distance[1]];
        const rooms = [[0, 102]];
        if (Math.abs(ux) > 1e-12) rooms.push([-ox[0] / ux, ((ux > 0 ? W - b.x : b.x) * sx - ox[1]) / ux]);
        if (Math.abs(uy) > 1e-12) rooms.push([-oy[0] / uy, ((uy > 0 ? H - b.y : b.y) * sy - oy[1]) / uy]);
        const clip = Math.min(Math.abs(ux) > 1e-12 ? b.halfWidth * sx / Math.abs(ux) : Infinity,
          Math.abs(uy) > 1e-12 ? b.halfHeight * sy / Math.abs(uy) : Infinity);
        const splits = [min, max];
        function root(line, target, low, high, list) {
          if (Math.abs(line[0]) < 1e-12) return;
          const z = (target - line[1]) / line[0];
          if (z >= low - 1e-6 && z <= high + 1e-6) list.push(z);
        }
        rooms.forEach((room, i) => {
          rooms.slice(i + 1).forEach(other => root(subtract(room, other), 0, min, max, splits));
          root(room, clip / .45, min, max, splits);
        });
        const intervals = [...new Set(splits)].sort((a, c) => a - c);
        intervals.forEach(add);
        for (let i = 1; i < intervals.length; i++) {
          const low = intervals[i - 1], high = intervals[i], mid = (low + high) / 2, roots = [];
          const distance = rooms.reduce((best, room) => value(room, mid) < value(best, mid) ? room : best);
          const clipped = value(distance, mid) * .45 < clip ? distance.map(n => n * .45) : [0, clip];
          const ex = offsetLine(ox, ux, distance), ey = offsetLine(oy, uy, distance);
          const startX = offsetLine(ox, ux, clipped), startY = offsetLine(oy, uy, clipped);
          const cut = (line, boundary) => root(line, boundary, low, high, roots);
          // Endpoint clearance against its moving owner can be satisfied on
          // either axis, particularly when an old diagonal reaches an edge.
          for (const sign of [-1, 1]) {
            cut(subtract(ex, ox), sign * (width + 8)); cut(subtract(ey, oy), sign * 52);
          }
          candidateGraph.nodes.forEach(obstacle => {
            if (obstacle.id === id) return;
            const x = obstacle.x * sx, y = obstacle.y * sy;
            for (const sign of [-1, 1]) {
              cut(ex, x + sign * (width + 8)); cut(ey, y + sign * 52);
            }
            for (const bx of [x - b.halfWidth * sx - spread, x + b.halfWidth * sx + spread]) {
              cut(startX, bx); cut(ex, bx);
              for (const by of [y - b.halfHeight * sy - spread, y + b.halfHeight * sy + spread]) {
                cut(startY, by); cut(ey, by);
                // Contact of the constant-direction corridor with a box corner.
                cut([-ox[0] * uy + oy[0] * ux, (bx - ox[1]) * uy - (by - oy[1]) * ux], 0);
              }
            }
          });
          roots.forEach(add);
        }
      }
    }
    corridorCuts('x', anchor.y * sy); corridorCuts('y', anchor.x * sx);
    // Inclusive corridor contact needs a tiny outside sample as well as the
    // exact spacing boundary; use CSS units regardless of board aspect ratio.
    const samples = (values, scale) => [...new Set(values.flatMap(value => [value, value - .0001 / scale, value + .0001 / scale]))];
    // Every admissible point lies on the first neighbour's H/V cross. Critical
    // label/boundary coordinates also cover continuous valid line intervals.
    const candidates = samples(xs, sx).map(x => ({ x, y: anchor.y }))
      .concat(samples(ys, sy).map(y => ({ x: anchor.x, y })));
    candidates.sort((a, c) => Math.hypot((a.x - wanted.x) * sx, (a.y - wanted.y) * sy) -
      Math.hypot((c.x - wanted.x) * sx, (c.y - wanted.y) * sy) || a.x - c.x || a.y - c.y);
    return candidates.find(valid) || null;
  }
  function pendingDirectionClear(candidate, candidateGraph = graph) {
    const r = board.getBoundingClientRect();
    const owner = candidateGraph.nodes.find(n => n.id === candidate?.owner);
    if (!owner || r.width <= 0 || r.height <= 0) return false;
    const sx = r.width / W, sy = r.height / H, box = bounds();
    const screen = point => ({ x: point.x * sx, y: point.y * sy });
    // Reserve the incoming tile (including separation from the owner), as well
    // as the whole visible corridor of all parallel strokes, in CSS pixels.
    const spread = (candidate.order === 3 ? 6 : candidate.order === 2 ? 3 : 0) + 3;
    const end = pendingPoint(candidate, candidateGraph);
    if (!end || !placementClear(end, undefined, candidateGraph)) return false;
    const start = screen(bondEnd(owner, end)), finish = screen(end);
    return !candidateGraph.nodes.some(node => node.id !== owner.id &&
      segmentHitsBox(start, finish, screen(node), box.halfWidth * sx + spread, box.halfHeight * sy + spread));
  }
  function initialPendingBond(owner, order) {
    const preferred = owner.x <= W / 2 ? 1 : -1;
    for (const [dx, dy] of [[preferred, 0], [-preferred, 0], [0, -1], [0, 1]]) {
      const candidate = { owner: owner.id, order, dx, dy };
      if (pendingDirectionClear(candidate)) return candidate;
    }
    return null;
  }
  function turnPending(dx, dy, save = true) {
    if (busy || solved || !pendingBond ||
        !Number.isInteger(dx) || !Number.isInteger(dy) || Math.abs(dx) + Math.abs(dy) !== 1 ||
        pendingBond.dx === dx && pendingBond.dy === dy) return false;
    const candidate = { ...pendingBond, dx, dy };
    if (!pendingDirectionClear(candidate)) {
      const message = 'Η κατεύθυνση αυτή δεν έχει ελεύθερο χώρο.';
      if ($('interaction-status').textContent !== message) announce(message);
      return false;
    }
    if (save) saveChange();
    pendingBond = candidate;
    if (save) render(); else renderBonds();
    return true;
  }
  function translateConstruction(before, dx, dy) {
    const state = clone(before), nodes = state.graph.nodes, b = bounds();
    if (!nodes.length || b.r.width <= 0 || b.r.height <= 0 || !Number.isFinite(dx) || !Number.isFinite(dy)) return state;
    const end = pendingPoint(before.pendingBond, before.graph), points = end ? [...nodes, end] : nodes;
    const left = b.x - Math.min(...points.map(n => n.x)), right = W - b.x - Math.max(...points.map(n => n.x));
    const top = b.y - Math.min(...points.map(n => n.y)), bottom = H - b.y - Math.max(...points.map(n => n.y));
    if (left > right || top > bottom) return state;
    dx = Math.max(left, Math.min(right, dx)); dy = Math.max(top, Math.min(bottom, dy));
    nodes.forEach(n => { n.x += dx; n.y += dy; });
    return state;
  }
  function setPanMode(value) {
    if (value && (busy || solved || !graph.nodes.length)) return;
    if (drag) finishDrag(null, true);
    panning = value;
    pickerOwner = null; selected = null;
    render();
    announce(panning ? 'Το χεράκι είναι ενεργό. Σύρε όλη την κατασκευή ή χρησιμοποίησε τα βέλη μέσα στο σχέδιο.' : 'Επέστρεψες στη μετακίνηση κομματιών.');
  }
  function moveConstruction(direction) {
    if (!panning || busy || solved || drag) return;
    const r = board.getBoundingClientRect(), before = constructionState();
    const delta = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[direction];
    const next = translateConstruction(before, delta[0] * 18 * W / r.width, delta[1] * 18 * H / r.height);
    if (JSON.stringify(next) === JSON.stringify(before)) return;
    saveChange(before); restoreConstruction(next); render();
    // SVG bond targets are replaced during rendering. Keep subsequent Hand
    // arrow keys on the stable construction surface, including from a bond.
    board.focus({ preventScroll: true });
  }
  function cancelLocalInteraction() {
    if (viewportUI?.closeHelp()) return true;
    if (drag?.whole) { finishDrag(null, true); return true; }
    if (panning) { setPanMode(false); return true; }
    if (pendingBond || pickerOwner || drag) { finishDrag(null, true); cancelPending(); return true; }
    return false;
  }
  function snapCandidate(point, id, hydrogens) {
    if (id && id === pendingBond?.owner) return null;
    const end = pendingPoint();
    if (!end) return null;
    const r = board.getBoundingClientRect();
    if (Math.hypot((point.x - end.x) * r.width / W, (point.y - end.y) * r.height / H) > 32) return null;
    const owner = graph.nodes.find(n => n.id === pendingBond.owner);
    const target = id ? graph.nodes.find(n => n.id === id) : { id: null, hydrogens };
    const next = { nodes: id ? graph.nodes : [...graph.nodes, target],
      bonds: [...graph.bonds, { a: owner.id, b: target.id, order: pendingBond.order }] };
    return { point: end, valid: canJoin(owner, target, pendingBond.order) && nodePositionValid(target.id, end, next) };
  }
  function bondStrokes(start, end, order, className, edgeIndex) {
    const r = board.getBoundingClientRect(), sx = r.width / W, sy = r.height / H;
    const dx = (end.x - start.x) * sx, dy = (end.y - start.y) * sy, length = Math.hypot(dx, dy) || 1;
    const offsets = order === 3 ? [-6, 0, 6] : order === 2 ? [-3, 3] : [0];
    offsets.forEach(offset => {
      const line = document.createElementNS(SVG_NS, 'line');
      Object.entries({ x1: start.x - dy / length * offset / sx, y1: start.y + dx / length * offset / sy,
        x2: end.x - dy / length * offset / sx, y2: end.y + dx / length * offset / sy }).forEach(([k, v]) => line.setAttribute(k, v));
      line.classList.add(className); line.dataset.order = order;
      if (edgeIndex !== undefined) line.dataset.bondIndex = edgeIndex;
      line.setAttribute('aria-hidden', 'true'); svg.append(line);
    });
  }
  function renderPicker() {
    const owner = !solved && !busy && graph.nodes.find(n => n.id === pickerOwner);
    const picker = $('bond-picker'); picker.hidden = !owner;
    if (!owner) return;
    $('bond-picker-label').textContent = label(owner.hydrogens) + ' — διάλεξε δεσμό';
    picker.querySelectorAll('[data-bond-order]').forEach(button => {
      const order = Number(button.dataset.bondOrder);
      button.disabled = order > (constructionEnabled ? 3 : 1) || remainingCapacity(owner) < order;
    });
    const r = board.getBoundingClientRect(), width = Math.min(260, r.width - 12), height = picker.offsetHeight || 95;
    picker.style.width = width + 'px';
    picker.style.left = Math.max(6, Math.min(r.width - width - 6, owner.x * r.width / W - width / 2)) + 'px';
    const below = owner.y * r.height / H + 30;
    picker.style.top = Math.max(6, Math.min(r.height - height - 6, below + height <= r.height - 6 ? below : owner.y * r.height / H - height - 30)) + 'px';
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
      line.setAttribute('aria-label', orderName(edge.order) + ' δεσμός ' + (i + 1) + ', μεταξύ ομάδων ' +
        (graph.nodes.indexOf(a) + 1) + ' και ' + (graph.nodes.indexOf(b) + 1));
      line.setAttribute('aria-pressed', String(!!selected && selected.kind === 'bond' && selected.index === i));
      // SVG hit area is wide, while its visible stroke remains a chemical bond.
      const hit = line.cloneNode();
      hit.classList.add('puzzle-bond-hit');
      hit.removeAttribute('tabindex'); hit.removeAttribute('role'); hit.removeAttribute('aria-label');
      hit.setAttribute('aria-hidden', 'true');
      // One accessible hit target per real edge; visible parallel strokes use CSS-pixel offsets.
      line.classList.add('puzzle-bond-target');
      svg.append(hit, line);
      bondStrokes(start, end, edge.order, 'puzzle-bond-visible', i);
      if (selected && selected.kind === 'bond' && selected.index === i) {
        [...svg.querySelectorAll('.puzzle-bond-visible[data-bond-index="' + i + '"]')].forEach(el => el.classList.add('is-selected'));
      }
    });
    const end = pendingPoint(), endpoint = $('pending-bond-end');
    endpoint.hidden = !end || solved;
    if (end && !endpoint.hidden) {
      const owner = graph.nodes.find(n => n.id === pendingBond.owner);
      bondStrokes(bondEnd(owner, end), end, pendingBond.order, 'puzzle-pending-bond');
      endpoint.style.left = end.x / W * 100 + '%'; endpoint.style.top = end.y / H * 100 + '%';
      endpoint.setAttribute('aria-label', 'Ελεύθερο άκρο: ' + orderName(pendingBond.order) + ' δεσμός. Σύρε για κατεύθυνση ή χρησιμοποίησε τα βέλη.');
    }
    board.classList.toggle('is-snap-compatible', snapPreview?.valid === true);
    board.classList.toggle('is-snap-incompatible', snapPreview?.valid === false);
    if (snapPreview) {
      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.setAttribute('cx', snapPreview.point.x); circle.setAttribute('cy', snapPreview.point.y); circle.setAttribute('r', '15');
      circle.classList.add('puzzle-snap-preview'); circle.setAttribute('aria-hidden', 'true'); svg.append(circle);
    }
  }
  function controls() {
    $('check-answer').disabled = busy || solved || !graph.nodes.length;
    $('next-molecule').disabled = busy || !current || (!lesson && practice.level === null);
    $('undo-action').disabled = busy || solved || !undo.length;
    $('pan-tool').disabled = busy || solved || !graph.nodes.length;
    $('pan-tool').setAttribute('aria-pressed', String(panning));
    $('remove-selection').disabled = busy || solved || !selected;
    const node = selected && selected.kind === 'node' && graph.nodes.find(n => n.id === selected.id);
    $('selection-label').textContent = node ? label(node.hydrogens) :
      selected ? 'δεσμός' : 'κανένα';
    document.querySelectorAll('[data-hydrogens]').forEach(b => { b.disabled = busy || solved || graph.nodes.length >= E.MAX_NODES; });
    board.classList.toggle('is-panning', panning);
    board.classList.toggle('is-pan-dragging', !!drag?.whole && drag.active);
    board.setAttribute('aria-busy', String(busy));
    $('cancel-pending-bond').hidden = !pendingBond;
    renderPicker();
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

  function detachedPoint(wanted, hydrogens) {
    const b = bounds(), r = b.r;
    if (r.width <= 0 || r.height <= 0) return null;
    const valid = point => {
      const next = { nodes: [...graph.nodes, { id: null, hydrogens, ...point }], bonds: graph.bonds };
      // Reserve existing bond corridors as well as the empty end and its
      // incoming-tile footprint. Adding a piece must never look like a join.
      return nodePositionValid(null, point, next) && (!pendingBond || pendingDirectionClear(pendingBond, next));
    };
    const first = fitPoint(wanted);
    if (valid(first)) return first;
    const stepX = b.halfWidth * 2 + 18, stepY = b.halfHeight * 2 + 24, candidates = [];
    for (let y = b.y; y <= H - b.y; y += stepY) {
      for (let x = b.x; x <= W - b.x; x += stepX) candidates.push({ x, y });
    }
    candidates.sort((a, c) => Math.hypot((a.x - first.x) * r.width / W, (a.y - first.y) * r.height / H) -
      Math.hypot((c.x - first.x) * r.width / W, (c.y - first.y) * r.height / H));
    return candidates.find(valid) || null;
  }
  function addGroup(hydrogens, point) {
    if (busy || solved || graph.nodes.length >= E.MAX_NODES) return;
    const wanted = point || { x: W / 2, y: H / 2 };
    const p = detachedPoint(wanted, hydrogens);
    if (!p) { announce('Δεν υπάρχει ελεύθερη θέση για νέο κομμάτι. Μετακίνησε μια ομάδα και δοκίμασε ξανά.'); return; }
    saveChange();
    let id; do { id = 'piece-' + (++serial); } while (graph.nodes.some(n => n.id === id));
    graph.nodes.push({ id, hydrogens, x: p.x, y: p.y });
    selected = { kind: 'node', id };
    pickerOwner = null;
    announce('Προστέθηκε ' + label(hydrogens) + ' ασύνδετο.' + (pendingBond ? ' Σύρε το στο ελεύθερο άκρο για να το ενώσεις.' : '')); render(id);
    reveal($('check-answer'));
  }
  function chooseNode(id) {
    if (busy || solved || panning) return;
    const node = graph.nodes.find(n => n.id === id);
    if (!node) return;
    selected = { kind: 'node', id };
    pickerOwner = id;
    announce('Επιλέχθηκε ' + label(node.hydrogens) + '.');
    render(id);
  }
  function createPending(order) {
    const owner = graph.nodes.find(n => n.id === pickerOwner);
    if (busy || solved || !owner || !Number.isInteger(order) || order < 1 || order > (constructionEnabled ? 3 : 1) || remainingCapacity(owner) < order) return;
    const candidate = initialPendingBond(owner, order);
    if (!candidate) {
      announce('Δεν βρέθηκε ελεύθερος χώρος για τον δεσμό. Μετακίνησε μια ομάδα και δοκίμασε ξανά.');
      return;
    }
    saveChange();
    pendingBond = candidate;
    pickerOwner = null;
    announce('Έτοιμος ' + orderName(order) + ' δεσμός. Φέρε μια συμβατή ομάδα στο ελεύθερο άκρο.'); render();
    $('pending-bond-end').focus({ preventScroll: true });
  }
  function cancelPending() {
    if (pendingBond && !solved && !busy) { saveChange(); pendingBond = null; }
    pickerOwner = null; snapPreview = null; render();
  }
  function connectAtPending(id, hydrogens, candidate) {
    if (!pendingBond || !candidate?.valid || !id && graph.nodes.length >= E.MAX_NODES) return false;
    const owner = graph.nodes.find(n => n.id === pendingBond.owner);
    const target = id ? graph.nodes.find(n => n.id === id) : { id: null, hydrogens };
    const end = pendingPoint();
    if (!end || !candidate.point || Math.abs(end.x - candidate.point.x) > 1e-6 || Math.abs(end.y - candidate.point.y) > 1e-6 ||
        !canJoin(owner, target, pendingBond.order)) return false;
    const next = { nodes: id ? graph.nodes : [...graph.nodes, target],
      bonds: [...graph.bonds, { a: owner.id, b: target.id, order: pendingBond.order }] };
    if (!nodePositionValid(target.id, end, next)) return false;
    saveChange();
    if (!id) {
      do { id = 'piece-' + (++serial); } while (graph.nodes.some(n => n.id === id));
      graph.nodes.push({ id, hydrogens, ...candidate.point });
    } else Object.assign(target, candidate.point);
    graph.bonds.push({ a: owner.id, b: id, order: pendingBond.order });
    pendingBond = null; pickerOwner = null;
    selected = { kind: 'node', id };
    announce('Η ομάδα συνδέθηκε στο ελεύθερο άκρο.'); return true;
  }
  function removeSelected() {
    if (!selected || solved || busy) return;
    if (drag) finishDrag(null, true);
    saveChange();
    if (selected.kind === 'node') {
      const id = selected.id;
      graph.nodes = graph.nodes.filter(n => n.id !== id);
      graph.bonds = graph.bonds.filter(e => e.a !== id && e.b !== id);
      if (pendingBond?.owner === id) pendingBond = null;
      announce('Η ομάδα αφαιρέθηκε. Είναι ξανά διαθέσιμη στα κομμάτια.');
    } else { graph.bonds.splice(selected.index, 1); announce('Ο δεσμός αφαιρέθηκε.'); }
    selected = null; pickerOwner = null; render();
  }
  function moveSelected(direction) {
    if (solved || busy || !selected || selected.kind !== 'node') return;
    const n = graph.nodes.find(n => n.id === selected.id), r = board.getBoundingClientRect();
    const delta = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[direction];
    const p = projectNodePosition(n.id, { x: n.x + delta[0] * 18 * W / r.width, y: n.y + delta[1] * 18 * H / r.height });
    if (!p) { announce('Δεν υπάρχει ελεύθερη οριζόντια ή κατακόρυφη θέση για όλους τους δεσμούς.'); return; }
    if (Math.abs(p.x - n.x) < 1e-6 && Math.abs(p.y - n.y) < 1e-6) return;
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
    if (!edge || solved || busy || panning || performance.now() < ignoreClickUntil) return;
    selected = { kind: 'bond', index: Number(edge.dataset.bondIndex) };
    pickerOwner = null; render(); announce('Επιλέχθηκε ο δεσμός. Μπορείς να τον αφαιρέσεις.');
    svg.querySelector('.puzzle-bond:not(.puzzle-bond-hit)[data-bond-index="' + selected.index + '"]').focus({ preventScroll: true });
  });
  svg.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('[data-bond-index]')) {
      event.preventDefault(); event.target.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
  });
  board.addEventListener('keydown', event => {
    const arrows = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down' };
    const drawingTarget = event.target === board || event.target.dataset.nodeId || event.target.dataset.bondIndex !== undefined || event.target.hasAttribute('data-pending-end');
    if (panning && drawingTarget && arrows[event.key]) {
      event.preventDefault(); event.stopPropagation(); moveConstruction(arrows[event.key]);
    } else if (panning && (event.key === 'Delete' || event.key === 'Backspace')) {
      event.preventDefault();
    } else if (event.target.dataset.nodeId && (event.key === 'Enter' || event.key === ' ') && pendingBond && !busy && !solved && !panning && !drag) {
      const id = event.target.dataset.nodeId, node = graph.nodes.find(n => n.id === id);
      const candidate = node && snapCandidate(node, id);
      if (candidate) {
        event.preventDefault(); event.stopPropagation();
        if (!connectAtPending(id, node.hydrogens, candidate)) announce('Η ομάδα δεν μπορεί να συνδεθεί σε αυτό το άκρο. Η προηγούμενη δομή διατηρήθηκε.');
        render(id);
      }
    } else if (event.target.dataset.nodeId && arrows[event.key]) {
      event.preventDefault(); selected = { kind: 'node', id: event.target.dataset.nodeId }; moveSelected(arrows[event.key]);
    } else if (drawingTarget && (event.key === 'Delete' || event.key === 'Backspace')) {
      if (event.target.dataset.bondIndex) selected = { kind: 'bond', index: Number(event.target.dataset.bondIndex) };
      else if (event.target.dataset.nodeId) selected = { kind: 'node', id: event.target.dataset.nodeId };
      event.preventDefault(); removeSelected();
    } else if (event.key === 'Escape' && cancelLocalInteraction()) {
      event.preventDefault(); event.stopPropagation();
    }
  });
  $('bond-picker').addEventListener('click', event => {
    const button = event.target.closest('[data-bond-order]');
    if (button) createPending(Number(button.dataset.bondOrder));
  });
  $('close-bond-picker').addEventListener('click', () => { const id = pickerOwner; pickerOwner = null; render(id); });
  $('cancel-pending-bond').addEventListener('click', cancelPending);
  $('pending-bond-end').addEventListener('keydown', event => {
    if (panning) return;
    const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
    if (pendingBond && directions[event.key]) {
      event.preventDefault(); event.stopPropagation();
      turnPending(...directions[event.key]); $('pending-bond-end').focus({ preventScroll: true });
    } else if (event.key === 'Delete' || event.key === 'Backspace') {
      event.preventDefault(); event.stopPropagation(); cancelPending();
    }
  });
  $('pan-tool').addEventListener('click', () => setPanMode(!panning));
  $('remove-selection').addEventListener('click', removeSelected);
  $('undo-action').addEventListener('click', () => {
    if (busy || solved || !undo.length) return;
    if (drag) finishDrag(null, true);
    restoreConstruction(undo.pop()); submitted = false; selected = null; pickerOwner = null; snapPreview = null; clearFeedback(); render(); announce('Η τελευταία αλλαγή αναιρέθηκε.');
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
      solved = true; pendingBond = null; pickerOwner = null; panning = false;
      $('game-status').textContent = 'Σωστά! Η δομή σου αντιστοιχεί στο όνομα ' + current.name + '.';
    }
    render(); viewportUI?.feedback(result.correct, true); reveal($('feedback'));
  });

  // Pointer capture stays on a stable container: rendering node buttons never loses a drag.
  document.addEventListener('pointerdown', event => {
    if (busy || solved || event.button !== 0 || drag) return;
    if (panning && board.contains(event.target)) {
      cancelReveal();
      drag = { whole: true, pointerId: event.pointerId, item: board, capture: board,
        x: event.clientX, y: event.clientY, active: false, before: constructionState(), ghost: null };
      board.setPointerCapture(event.pointerId);
      event.preventDefault(); return;
    }
    const item = event.target.closest('[data-node-id], [data-hydrogens], [data-pending-end]');
    if (!item || item.disabled) return;
    cancelReveal();
    const endpoint = item.hasAttribute('data-pending-end');
    drag = { pointerId: event.pointerId, item, endpoint, capture: endpoint || item.dataset.nodeId ? board : $('piece-bank'),
      id: item.dataset.nodeId || null, hydrogens: Number(item.dataset.hydrogens),
      x: event.clientX, y: event.clientY, active: false, before: constructionState(), ghost: null };
    drag.capture.setPointerCapture(event.pointerId);
  });
  document.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    if (!drag.active && Math.hypot(event.clientX - drag.x, event.clientY - drag.y) < 7) return;
    if (!drag.active) {
      drag.active = true; pickerOwner = null; renderPicker();
      if (!drag.endpoint && !drag.whole) {
        drag.ghost = drag.item.cloneNode(true);
        drag.ghost.removeAttribute('id'); drag.ghost.removeAttribute('data-node-id'); drag.ghost.removeAttribute('data-hydrogens');
        drag.ghost.className = 'puzzle-drag-ghost'; drag.ghost.setAttribute('aria-hidden', 'true');
        drag.ghost.setAttribute('tabindex', '-1');
        document.body.append(drag.ghost);
      }
      if (drag.id) drag.item.classList.add('is-dragging');
    }
    event.preventDefault();
    if (drag.whole) {
      const r = board.getBoundingClientRect();
      restoreConstruction(translateConstruction(drag.before, (event.clientX - drag.x) * W / r.width, (event.clientY - drag.y) * H / r.height));
      render(); return;
    }
    if (drag.endpoint) {
      const owner = graph.nodes.find(n => n.id === pendingBond?.owner), p = localPoint(event.clientX, event.clientY);
      if (owner) {
        const r = board.getBoundingClientRect(), dx = (p.x - owner.x) * r.width / W, dy = (p.y - owner.y) * r.height / H;
        if (Math.hypot(dx, dy) > 1e-6) {
          if (Math.abs(dx) >= Math.abs(dy)) turnPending(Math.sign(dx), 0, false);
          else turnPending(0, Math.sign(dy), false);
        }
      }
      return;
    }
    drag.ghost.style.left = event.clientX + 'px'; drag.ghost.style.top = event.clientY + 'px';
    snapPreview = insideBoard(event.clientX, event.clientY) ? snapCandidate(localPoint(event.clientX, event.clientY), drag.id, drag.hydrogens) : null;
    if (drag.id && insideBoard(event.clientX, event.clientY)) {
      const n = graph.nodes.find(n => n.id === drag.id);
      const p = projectNodePosition(drag.id, localPoint(event.clientX, event.clientY), drag.before.graph);
      Object.assign(n, p || drag.before.graph.nodes.find(item => item.id === drag.id));
      drag.item.style.left = n.x / W * 100 + '%'; drag.item.style.top = n.y / H * 100 + '%';
    }
    renderBonds();
  }, { passive: false });
  function finishDrag(event, cancel) {
    if (!drag || event && event.pointerId !== drag.pointerId) return;
    const d = drag; drag = null;
    if (d.ghost) d.ghost.remove(); d.item.classList.remove('is-dragging');
    if (d.capture.hasPointerCapture(d.pointerId)) d.capture.releasePointerCapture(d.pointerId);
    if (!d.active) {
      if (!cancel && event) {
        ignoreClickUntil = performance.now() + 350;
        if (d.endpoint || d.whole) return;
        if (d.id) chooseNode(d.id); else addGroup(d.hydrogens);
      }
      return;
    }
    ignoreClickUntil = performance.now() + 350;
    const after = constructionState(), endPending = after.pendingBond;
    restoreConstruction(d.before); snapPreview = null;
    const inPage = event && event.clientX >= 0 && event.clientY >= 0 && event.clientX <= innerWidth && event.clientY <= innerHeight;
    if (cancel || !inPage) { render(); return; }
    if (d.whole) {
      if (JSON.stringify(after) !== JSON.stringify(d.before)) {
        saveChange(); restoreConstruction(after); announce('Μετακινήθηκε όλη η κατασκευή.');
      }
      render(); return;
    }
    if (d.endpoint) {
      if (insideBoard(event.clientX, event.clientY) && JSON.stringify(endPending) !== JSON.stringify(pendingBond) && pendingDirectionClear(endPending)) {
        saveChange(); pendingBond = endPending;
      }
      render(); return;
    }
    if (insideBoard(event.clientX, event.clientY)) {
      const candidate = snapCandidate(localPoint(event.clientX, event.clientY), d.id, d.hydrogens);
      if (candidate) {
        if (!connectAtPending(d.id, d.hydrogens, candidate)) announce('Η ομάδα δεν μπορεί να συνδεθεί σε αυτό το άκρο. Η προηγούμενη δομή διατηρήθηκε.');
        render(); return;
      }
      if (d.id) {
        const node = graph.nodes.find(n => n.id === d.id), p = projectNodePosition(d.id, localPoint(event.clientX, event.clientY));
        if (p && (Math.abs(p.x - node.x) > 1e-6 || Math.abs(p.y - node.y) > 1e-6)) {
          saveChange(); Object.assign(node, p); selected = { kind: 'node', id: d.id };
        } else if (!p) announce('Δεν υπάρχει ελεύθερη οριζόντια ή κατακόρυφη θέση για όλους τους δεσμούς. Η προηγούμενη δομή διατηρήθηκε.');
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
    graph = { nodes: [], bonds: [] }; undo = []; selected = null; solved = false;
    pendingBond = null; pickerOwner = null; snapPreview = null; panning = false;
    attempts = 0; submitted = false;
    $('target-name').textContent = current.name;
    viewportUI?.resetName();

    $('game-status').textContent = 'Διάβασε το όνομα και φτιάξε τον συνεπτυγμένο τύπο του μορίου.';
    clearFeedback(); viewportUI?.stage('editing'); announce('Νέο μόριο. Το πλαίσιο είναι κενό.'); render();
    reveal($('piece-bank'));
  }
  function freshSeed() { return Array.from(crypto.getRandomValues(new Uint32Array(4)), n => n.toString(16).padStart(8, '0')).join(''); }
  function savePractice() {
    const slot = practice.slots.get(practice.level);
    if (slot && current) slot.saved = { moleculeId: current.id, state: snapshot(), undo: clone(undo),
      selected: clone(selected), serial };
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
    pendingBond = restorePending(saved.state.construction);
    undo = clone(saved.undo); selected = clone(saved.selected); serial = saved.serial;
    if (submitted) {
      const result = E.grade(graph, current.target); solved = result.correct;
      if (solved) pendingBond = null;
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
    if (raw.bonds.some(b => !b || !ids.has(b.a) || !ids.has(b.b) || !Number.isInteger(b.order) || b.order < 1 || b.order > (constructionEnabled ? 3 : 1))) return blank;
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
      if (viewportEnabled && validViewportMessage(d)) {
        Viewport.acceptViewport($('game'), d); viewportUI?.refresh();
      }
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
    constructionEnabled = d.constructionVersion === 1; updateConstructionInstructions();
    const loading = load(context?.source === 'enriched' ? CURRENT_CATALOG : LEGACY_CATALOG, false);
    current = null; graph = { nodes: [], bonds: [] }; undo = []; selected = null; panning = false;
    $('target-name').textContent = 'Περιμένουμε το μόριο του μαθήματος…'; clearFeedback(); render();
    if (!await loading || stopped || controlled !== lesson.current) return;
    const index = catalog.findIndex(m => m.id === d.moleculeId);
    if (index < 0 || d.correctName !== catalog[index].name) { postLesson('error', {}); return; }
    busy = false; startRound(index);
    const raw = d.initialState || {};
    graph = restoreGraph(raw.graph);
    pendingBond = restorePending(raw.construction);
    serial = graph.nodes.reduce((value, n) => Math.max(value, /^piece-\d{1,9}$/.test(n.id) ? Number(n.id.slice(6)) : 0), 0);
    attempts = Number.isSafeInteger(raw.attempts) && raw.attempts >= 0 ? raw.attempts : 0;
    submitted = raw.submitted === true && attempts > 0 && graph.nodes.length > 0;
    const result = submitted ? E.grade(graph, current.target) : null;
    solved = !!(result && result.correct);
    if (solved) pendingBond = null;
    if (result) {
      $('feedback').hidden = false; $('feedback').textContent = result.message; $('feedback').classList.toggle('success', solved);
      if (solved && controlled.explanation) { const p = document.createElement('p'); p.textContent = controlled.explanation; $('feedback').append(p); }
    }
    render(); if (submitted) viewportUI?.feedback(solved);
    lesson.lastSnapshot = JSON.stringify(snapshot()); controlled.loaded = true; lesson.lastHeight = null;
    postLesson('loaded', { state: snapshot() }); postSize(); reveal($('piece-bank'));
  });
  addEventListener('keydown', event => {
    if (event.key !== 'Escape' || event.defaultPrevented) return;
    if (cancelLocalInteraction()) event.preventDefault();
    else if (lesson) { event.preventDefault(); postLesson('exit', {}); }
  });
  $('retry-load').addEventListener('click', () => load(lesson
    ? (lesson.current?.context?.source === 'enriched' ? CURRENT_CATALOG : LEGACY_CATALOG) : catalogDescriptor));
  const media = matchMedia('(max-width:600px)');
  function instructionsMode() { $('instructions').open = true; }
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
  viewportUI = createViewportUI();
  load();
}());
