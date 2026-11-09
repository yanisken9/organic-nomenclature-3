/* Native lesson playback, with a bounded same-origin React navigation adapter. */
(() => {
  'use strict';
  const lessons = __NAMELECULE_LESSONS__;
  const channel = 'namelecule-lesson-v1';
  const params = new URLSearchParams(location.search);
  const id = params.get('lesson');
  const spec = Object.hasOwn(lessons, id) ? lessons[id] : null;
  const session = params.get('session');
  let outerHeight = Number(params.get('viewportHeight'));
  const validHeight = value => Number.isInteger(value) && value >= 420 && value <= 12000;
  if (!spec || !session || !validHeight(outerHeight) || parent === window || params.get('scenario') !== spec.scenario || params.get('present') !== '1') return;
  let stopped = false;
  let ready = false;
  let lastId = 0;
  let revision = 0;
  let timer;
  let sizeFrame;
  let lastHeight = 0;
  const send = data => parent.postMessage({ channel, session, lesson: spec.id, ...data }, location.origin);
  function height() {
    // Measure native flow, not document scrollHeight (which cannot shrink
    // below an iframe's previous height). The page container owns the lesson.
    const page = document.getElementById('pageContainer');
    let required = page.getBoundingClientRect().bottom + scrollY + 24;
    // The native pixel setting is a ceiling constrained by its viewport
    // budget. Reserve that budget before shrinking this enclosing iframe;
    // otherwise a taller note can inadvertently shorten the next molecule.
    const step = fScenarioPresent().steps[fScenarioPresent().index];
    if (step) {
      const raw = fViewerHeights2D3D(true);
      const shares = [raw.h2, raw.h3].filter(h => h > 0);
      // Authored Auto uses an independent viewport, not a height derived
      // from its own auto-sized viewers (which would create a resize loop).
      // Native content scrolls normally within this viewport when necessary.
      const setting = shares.length === 2 ? viewerBothH : viewerMaxH;
      if (setting == null) return outerHeight;
      const cap = shares.length === 2 ? viewerBothH / 2 : viewerMaxH;
      if (Number.isFinite(cap) && cap > 0 && shares.length) {
        required = Math.max(required, innerHeight + (cap - Math.min(...shares)) * shares.length);
      }
    }
    return Math.max(420, Math.min(12000, Math.ceil(required)));
  }
  function resize() {
    sizeFrame = null;
    if (stopped || !ready) return;
    const value = height();
    if (value !== lastHeight) { lastHeight = value; send({ type: 'height', height: value }); }
  }
  function scheduleResize() { if (!sizeFrame) sizeFrame = requestAnimationFrame(resize); }
  function viewportResize() {
    if (stopped) return;
    // The current native release does not refit every height-only resize.
    // Reuse its fitter when React changes the enclosing iframe's height.
    fResizeViewers();
    scheduleResize();
  }
  const observer = new ResizeObserver(scheduleResize);
  observer.observe(document.getElementById('pageContainer'));
  const nativeApply = fScenarioApply;
  const nativeGo = fScenarioGo;
  const nativeExit = fScenarioExitPresent;
  const nativeLoadingDone = window.fLessonLoadingDone;
  function fail() {
    if (stopped) return;
    send({ type: 'failed' });
    stop();
  }
  function modelReady() {
    const models = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'modelInfo').models || [];
    if (models.length !== 1 || models[0].file !== new URL(nameExamples[selectedMol].file3D, document.baseURI).href) return false;
    const atoms = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'atomInfo', 'all');
    const bonds = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'bondInfo', 'all');
    if (!atoms.length || atoms.length !== allAtomsTypeList3D.length || bonds.length !== bondList3D.length ||
        atoms.some((a, i) => a.atomno !== i + 1 || a.sym !== allAtomsTypeList3D[i])) return false;
    const edge = (a, b, order) => [Math.min(a, b), Math.max(a, b), order].join(':');
    const parsed = new Set(bondList3D.map(b => edge(...b)));
    return bonds.every(b => parsed.has(edge(b.atom1.atomno, b.atom2.atomno, b.order)));
  }
  function synchronize() {
    clearTimeout(timer);
    ready = false;
    const ticket = ++revision;
    const token = MuLERMoCScenario.applyToken;
    const id = lastId;
    const ps = fScenarioPresent();
    const index = ps.index;
    const deadline = Date.now() + 15000;
    let marker = false;
    function check() {
      if (stopped || ticket !== revision) return;
      try {
        const step = ps.steps[index];
        if (ps !== fScenarioPresent() || ps.index !== index || MuLERMoCScenario.applyToken !== token) return;
        if (!step || ps.steps.length !== spec.total || step.title !== spec.titles[index]) return fail();
        let loaded = selectedMol === step.selectedMol && !!document.querySelector('#jsmeNomeclatureSVG svg') &&
          !!currentMolName && !document.documentElement.classList.contains('lesson-loading');
        if (step.show.viewers['3D']) {
          if (loaded && modelReady() && (!MuLERMoCScenario.pending3D || MuLERMoCScenario.pending3D.done)) {
            if (!marker) { marker = true; Jmol.script(jmolAppletNomeclature, 'reactLessonRevision = ' + ticket + ';'); }
            loaded = +Jmol.evaluateVar(jmolAppletNomeclature, 'reactLessonRevision') === ticket;
          } else loaded = false;
        }
        if (loaded) {
          ready = true;
          lastHeight = height();
          send({ type: 'state', id, step: index + 1, total: spec.total, title: step.title, height: lastHeight });
          scheduleResize();
          return;
        }
        if (Date.now() >= deadline) return fail();
        timer = setTimeout(check, 50);
      } catch (error) { fail(); }
    }
    check();
  }
  // Intercept only in this generated host. Native application files and the
  // original apply/go implementations remain unchanged.
  fScenarioApply = function (step) {
    if (stopped) return false;
    const ok = nativeApply(step);
    if (ok) { send({ type: 'busy', id: lastId, step: fScenarioPresent().index + 1 }); synchronize(); }
    else fail();
    return ok;
  };
  fScenarioExitPresent = () => { if (!stopped) send({ type: 'exit' }); };
  window.fLessonLoadingDone = function (failed) {
    nativeLoadingDone?.(failed);
    if (failed) fail();
  };
  function receive(event) {
    const d = event.data;
    if (stopped || event.origin !== location.origin || event.source !== parent || !d ||
        d.channel !== channel || d.session !== session || d.lesson !== spec.id) return;
    if (d.command === 'viewport') {
      if (validHeight(d.height)) { outerHeight = d.height; scheduleResize(); }
      return;
    }
    if (!ready || d.command !== 'step' || !Number.isSafeInteger(d.id) || d.id <= lastId ||
        !Number.isInteger(d.step) || d.step < 1 || d.step > spec.total) return;
    lastId = d.id;
    try { scrollTo(0, 0); nativeGo(d.step - 1); } catch (error) { fail(); }
  }
  function keydown(event) {
    if (event.ctrlKey || event.metaKey || event.altKey || event.target.closest?.('input,textarea,select,[contenteditable="true"]')) return;
    if (!['ArrowLeft', 'ArrowRight', 'Escape'].includes(event.key)) return;
    event.preventDefault(); event.stopImmediatePropagation();
    if (event.key === 'Escape') send({ type: 'exit' });
    else if (ready) send({ type: 'navigate', delta: event.key === 'ArrowLeft' ? -1 : 1 });
  }
  function stop() {
    if (stopped) return;
    stopped = true; ready = false; ++revision;
    clearTimeout(timer); cancelAnimationFrame(sizeFrame);
    observer.disconnect();
    window.removeEventListener('message', receive);
    window.removeEventListener('resize', viewportResize);
    document.removeEventListener('keydown', keydown, true);
    fScenarioApply = nativeApply; fScenarioExitPresent = nativeExit;
    window.fLessonLoadingDone = nativeLoadingDone;
    try { speechSynthesis.cancel(); Jmol.script(jmolAppletNomeclature, 'spin off;'); } catch (error) { /* unloading */ }
  }
  window.addEventListener('message', receive);
  window.addEventListener('resize', viewportResize);
  document.addEventListener('keydown', keydown, true);
  window.addEventListener('pagehide', stop, { once: true });
})();
