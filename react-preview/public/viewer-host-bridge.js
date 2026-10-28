/* Classic script: access existing lexical app state without changing its engine. */
(() => {
  'use strict';
  const channel = 'namelecule-viewer-v4';
  // Injected from the same catalog imported by React, at host generation.
  const moleculeIds = __NAMELECULE_MOLECULE_IDS__;
  const ruleSchema = __NAMELECULE_RULE_SCHEMA__;
  const session = new URLSearchParams(location.search).get('session');
  if (!session || parent === window) return;
  let ready = false;
  let lastId = 0;
  let stopped = false;
  let view = '2d';
  let modelReady = false;
  let revision = 0;
  let waitTimer = null;
  let resizeFrame = 0;
  let commandRunning = false;
  let activeExport = null;
  let restoreExportPrompt = () => {};
  const commands = [];
  const styles3D = ['ballnstick', 'spacefill', 'sticks'];
  const toggles3D = { hydrogens3d: '#hydrogensCheck', labels3d: '#atomSymbolsCheck', rotation3d: '#rotateCheck' };
  function controls3D() {
    return { hydrogens: hydrogens3DFlag, labels: atomSymbols3DFlag, rotating: rotateFlag, style: vis3D };
  }
  function canChange3D(d) {
    return modelReady && view === '3d' && d.molecule === selectedMol &&
      (d.command === 'style3d' ? styles3D.includes(d.value) :
        Object.hasOwn(toggles3D, d.command) && typeof d.value === 'boolean');
  }
  function resize3D() {
    resizeFrame = 0;
    if (stopped || view !== '3d') return;
    const host = document.getElementById('nomeclature3D');
    const canvas = document.getElementById('jmolAppletNomeclature_canvas2d');
    if (host && canvas && (canvas.clientWidth !== host.clientWidth || canvas.clientHeight !== host.clientHeight)) {
      Jmol.resizeApplet(jmolAppletNomeclature, { width: host.clientWidth, height: host.clientHeight });
    }
  }
  function scheduleResize() {
    if (!resizeFrame) resizeFrame = requestAnimationFrame(resize3D);
  }
  const resizeObserver = new ResizeObserver(scheduleResize);
  window.addEventListener('resize', scheduleResize);
  function applyView() {
    document.documentElement.dataset.view = view;
    document.getElementById('nomeclature3D').style.display = view === '3d' ? 'block' : 'none';
    fResizeViewers();
    resize3D();
    if (view === '3d') Jmol.script(jmolAppletNomeclature, 'refresh;');
  }
  function currentModel() {
    const models = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'modelInfo').models || [];
    const file = new URL(nameExamples[selectedMol].file3D, document.baseURI).href;
    if (models.length !== 1 || models[0].file !== file) return null;
    const atoms = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'atomInfo', 'all');
    const bonds = Jmol.getPropertyAsArray(jmolAppletNomeclature, 'bondInfo', 'all');
    if (atoms.length !== allAtomsTypeList3D.length || !atoms.length || bonds.length !== bondList3D.length ||
        atoms.some((a, i) => a.atomno !== i + 1 || a.sym !== allAtomsTypeList3D[i])) return null;
    const edge = (a, b, order) => [Math.min(a, b), Math.max(a, b), order].join(':');
    const parsed = new Set(bondList3D.map(b => edge(...b)));
    if (bonds.some(b => !parsed.has(edge(b.atom1.atomno, b.atom2.atomno, b.order)))) return null;
    return { file, atoms: atoms.length, bonds: bonds.length };
  }
  function synchronize(type, id, complete = () => {}, extra = {}) {
    clearTimeout(waitTimer);
    const ticket = ++revision;
    const deadline = Date.now() + (type === 'ready' ? 80000 : 9000);
    // Ordered after the legacy load/style scripts, not merely applet-ready.
    Jmol.script(jmolAppletNomeclature, 'reactPreviewRevision = ' + ticket + ';');
    function check() {
      if (stopped || ticket !== revision) return;
      try {
        const model = currentModel();
        if (model && +Jmol.evaluateVar(jmolAppletNomeclature, 'reactPreviewRevision') === ticket) {
          modelReady = true;
          ready = true;
          send({ type, ...(id === undefined ? {} : { id }), ...state(), model, ...extra });
          complete();
          return;
        }
        if (Date.now() >= deadline) return fail();
        waitTimer = setTimeout(check, 50);
      } catch (error) {
        console.error('Molecule preview 3D readiness failed', error);
        fail();
      }
    }
    check();
  }
  const send = data => parent.postMessage({ channel, session, ...data }, location.origin);
  function componentElement(id) {
    if (typeof id !== 'string' || !/^comp(?:[0-9]|1[0-2])$/.test(id)) return null;
    const element = document.getElementById(id);
    return element?.matches('#nameAnalysis .nameCompBox:not(.comp-hidden)') ? element : null;
  }
  function state() {
    const components = [...document.querySelectorAll('#nameAnalysis .nameCompBox:not(.comp-hidden)')]
      .map(element => ({ id: element.id, label: element.textContent, selected: element.classList.contains('selected') }));
    return { mode: mode2D === 'condensedZigZag' ? 'skeletal' : mode2D, symbols: mode2D === 'condensedZigZag',
      zoom: molZoom2D, molecule: selectedMol, view, naming: etherNamingMode, controls3D: controls3D(),
      analysis: { components, explanation: document.querySelector('#nameAnalysisExplain .explainText')?.textContent || '', rules: readRules() } };
  }
  function readRules() {
    let count = 0, textLength = 0;
    function children(parent, depth = 0) {
      if (depth > ruleSchema.maxDepth) throw new Error('Rule markup too deep');
      return [...parent.childNodes].flatMap(node => {
        if (node.nodeType !== 1 && node.nodeType !== 3) return [];
        if (++count > ruleSchema.maxNodes) throw new Error('Rule markup too large');
        if (node.nodeType === 3) {
          textLength += node.textContent.length;
          if (textLength > ruleSchema.maxText) throw new Error('Rule text too large');
          return [node.textContent];
        }
        const tag = node.tagName.toLowerCase();
        if (!ruleSchema.tags.includes(tag)) throw new Error('Unsupported rule element');
        return [{ tag, classes: [...node.classList].filter(name => ruleSchema.classes.includes(name)),
          row: node.getAttribute('data-row'), children: children(node, depth + 1) }];
      });
    }
    return [...document.querySelectorAll('#ruleTheoryContainer > .ruleTheory')].flatMap(panel => {
      const title = panel.querySelector('.ruleTile');
      if (!title?.textContent.trim()) return [];
      count = 0; textLength = 0;
      const text = panel.querySelector('.ruleText'), table = panel.querySelector('.ruleTable');
      return [{ id: title.id === 'alkoxyRuleTitle' ? 'alkoxy' : 'component', title: title.textContent.trim(),
        text: text ? children(text) : [], textClasses: text ? [...text.classList].filter(name => ruleSchema.classes.includes(name)) : [],
        table: table ? children(table) : [] }];
    });
  }
  function fail(reason) {
    stopped = true;
    restoreExportPrompt();
    commands.length = 0;
    clearInterval(poll);
    clearTimeout(waitTimer);
    send({ type: 'failed', ...(reason === 'export' ? { reason } : {}) });
  }
  function canChangeSymbols(d) {
    return modelReady && view === '2d' && d.molecule === selectedMol &&
      typeof d.value === 'boolean' && ['skeletal', 'condensedZigZag'].includes(mode2D) &&
      !!nameExamples[selectedMol]?.structure2D_Skeletal &&
      !!document.querySelector('#zigzagCheck:not(.disabledCheck)');
  }
  function exportTarget(d) {
    return d.value === 'png' && modelReady && d.view === view && ['2d', '3d'].includes(view) && d.molecule === selectedMol &&
      d.mode === (mode2D === 'condensedZigZag' ? 'skeletal' : mode2D) &&
      d.symbols === (mode2D === 'condensedZigZag') && d.naming === etherNamingMode &&
      (view === '2d' || (d.controls3D && Object.keys(controls3D()).every(key => d.controls3D[key] === controls3D()[key]))) &&
      d.component === (document.querySelector('#nameAnalysis .nameCompBox.selected:not(.comp-hidden)')?.id || null);
  }
  function onPNGDownload(event) {
    const anchor = event.target;
    if (!activeExport || !(anchor instanceof HTMLAnchorElement) ||
        anchor.download !== activeExport.filename || !(activeExport.view === '3d'
          // JSmol derives the MIME label from the chosen extension; observe
          // the actual PNG signature even when the user omits an extension.
          ? /^data:[^,]*;base64,iVBORw0KGgo/.test(anchor.href) : anchor.href.startsWith('blob:'))) return;
    // On timeout the viewer stays failed until retry unloads this document;
    // prevent a delayed native callback from starting an obsolete download.
    if (stopped) return event.preventDefault();
    if (activeExport.view === '3d') {
      activeExport.requested = true;
      // The native function queues a delayed echo cleanup. Finish after it,
      // before allowing the next model/name/highlight command to run.
      activeExport.settleAt = Date.now() + 550;
      return;
    }
    clearTimeout(waitTimer);
    const pending = activeExport;
    activeExport = null;
    synchronize('state', pending.id, pending.complete, { exportStatus: 'requested' });
  }
  function export2D(d, complete) {
    const deadline = Date.now() + 8000;
    function check() {
      if (stopped) return;
      // Cancel a newer-action superseded request before it takes a snapshot.
      if (d.id !== lastId) return complete();
      try {
        const numbered = nameAnalysisMode === 'none' || !numberingFlag ||
          document.querySelectorAll('#jsmeNomeclatureSVG text[id^="number"]').length === numbersSVGElements.filter(Boolean).length;
        if (exportTarget(d) && currentModel() && numbered && document.querySelector('#jsmeNomeclatureSVG svg')) {
          activeExport = { id: d.id, complete,
            filename: (currentMolName || selectedMol || 'molecule').replace(/\s+/g, '_') + '_2D.png' };
          // Hold the command queue through the native async PNG callback: its
          // filename still reads legacy globals. An anchor click requests a
          // browser download; it does not prove the file was saved on disk.
          waitTimer = setTimeout(() => fail('export'), Math.max(0, deadline - Date.now()));
          try { window.fSave2DPng(); } catch {
            clearTimeout(waitTimer);
            activeExport = null;
            synchronize('state', d.id, complete, { exportStatus: 'failed' });
          }
          return;
        }
        if (Date.now() >= deadline) return synchronize('state', d.id, complete, { exportStatus: 'failed' });
        waitTimer = setTimeout(check, 50);
      } catch (error) {
        console.error('PNG export readiness failed', error);
        fail();
      }
    }
    check();
  }
  function export3D(d, complete) {
    if (d.id !== lastId) return complete();
    if (!exportTarget(d) || !currentModel()) return synchronize('state', d.id, complete, { exportStatus: 'failed' });
    const pending = { id: d.id, view: '3d', filename: null, requested: false, cancelled: false, settleAt: Infinity };
    activeExport = pending;
    const nativePrompt = window.prompt;
    function exportPrompt(...args) {
      const answer = nativePrompt.apply(window, args);
      if (answer === null && activeExport === pending) {
        pending.cancelled = true;
        pending.settleAt = Date.now() + 550;
      }
      return answer;
    }
    window.prompt = exportPrompt;
    restoreExportPrompt = () => {
      if (window.prompt === exportPrompt) window.prompt = nativePrompt;
      restoreExportPrompt = () => {};
    };
    const deadline = Date.now() + 90000;
    const marker = ++revision;
    function finish(status) {
      restoreExportPrompt();
      activeExport = null;
      synchronize('state', d.id, complete, { exportStatus: status });
    }
    function check() {
      if (stopped) return;
      try {
        // A cancelled native write may discard its queued marker. After the
        // native cleanup delay, synchronize with a fresh marker instead.
        if (Date.now() >= pending.settleAt && (pending.cancelled ||
            +Jmol.evaluateVar(jmolAppletNomeclature, 'reactPreviewExportRevision') === marker)) {
          return finish(pending.requested ? 'requested' : 'failed');
        }
        if (Date.now() >= deadline) return fail('export');
        waitTimer = setTimeout(check, 50);
      } catch (error) {
        console.error('3D PNG readiness failed', error);
        fail('export');
      }
    }
    try {
      // Keep the original prompt, filename, image bytes, footer and 1200px
      // renderer. The queue stays held until a real native download request.
      window.fSaveJmolPng();
      Jmol.script(jmolAppletNomeclature, 'reactPreviewExportRevision = ' + marker + ';');
      check();
    } catch {
      finish('failed');
    }
  }
  function onMessage(event) {
    const d = event.data;
    if (!ready || stopped || event.origin !== location.origin || event.source !== parent ||
        !d || d.channel !== channel || d.session !== session ||
        !Number.isSafeInteger(d.id) || d.id <= lastId) return;
    if (!(d.command === 'mode' && ['condensed', 'expanded', 'skeletal'].includes(d.value)) &&
        !canChange3D(d) &&
        !(d.command === 'symbols' && canChangeSymbols(d)) &&
        !(d.command === 'export' && exportTarget(d)) &&
        !(d.command === 'zoom' && (d.value === 1 || d.value === -1) && (view === '2d' || modelReady)) &&
        !(d.command === 'molecule' && moleculeIds.includes(d.value)) &&
        !(d.command === 'naming' && modelReady && d.molecule === selectedMol &&
          nameExamples[selectedMol]?.classification?.chemicalClass === 'ethers' && ['iupac', 'common'].includes(d.value)) &&
        !(d.command === 'component' && modelReady && d.molecule === selectedMol && componentElement(d.value)) &&
        !(d.command === 'view' && ['2d', '3d'].includes(d.value))) return;
    lastId = d.id;
    commands.push(d);
    runNext();
  }
  function runNext() {
    if (stopped || commandRunning || !commands.length) return;
    commandRunning = true;
    const d = commands.shift();
    try {
      if (d.command === 'export') return (d.view === '3d' ? export3D : export2D)(d, () => {
        commandRunning = false;
        runNext();
      });
      if (d.command === 'mode') {
        const index = ['condensed', 'expanded', 'skeletal'].indexOf(d.value);
        $('#radio2DMode .mode2DOption').eq(index).trigger('click');
      } else if (d.command === 'molecule') {
        modelReady = false;
        selectedMol = d.value;
        fSelectMol();
        applyView();
      } else if (d.command === 'view') {
        view = d.value;
        applyView();
      } else if (d.command === 'style3d' || Object.hasOwn(toggles3D, d.command)) {
        // Recheck queued targets, and use the original UI handlers. Neither
        // molecular coordinates nor a second Jmol styling algorithm live here.
        if (canChange3D(d)) {
          if (d.command === 'style3d') {
            if (vis3D !== d.value) $('#dropLi' + styles3D.indexOf(d.value)).trigger('click');
          } else {
            const key = { hydrogens3d: 'hydrogens', labels3d: 'labels', rotation3d: 'rotating' }[d.command];
            if (controls3D()[key] !== d.value) $(toggles3D[d.command]).trigger('click');
          }
        }
      } else if (d.command === 'component') {
        $(componentElement(d.value)).trigger('click');
      } else if (d.command === 'symbols') {
        // A queued model/view/mode change may have invalidated this target.
        // The native handler owns both the depiction and its checkbox state.
        if (canChangeSymbols(d) && d.value !== (mode2D === 'condensedZigZag')) {
          $('#zigzagCheck').trigger('click');
        }
      } else if (d.command === 'naming') {
        // Recheck the target after queued model/view changes; never mutate the
        // naming preference from a stale command belonging to another molecule.
        if (d.molecule === selectedMol && nameExamples[selectedMol]?.classification?.chemicalClass === 'ethers') {
          $('#radioEtherNaming .etherNamingRadio[data-naming-mode="' + d.value + '"]').trigger('click');
        }
      } else if (view === '3d') fZoom3D(d.value);
      else fZoom2D(d.value);
      synchronize('state', d.id, () => {
        commandRunning = false;
        runNext();
      });
    } catch (error) {
      console.error('Molecule preview command failed', error);
      fail();
    }
  }
  document.addEventListener('click', onPNGDownload, true);
  window.addEventListener('message', onMessage);
  const started = Date.now();
  const poll = setInterval(() => {
    if (Date.now() - started > 85000) return fail();
    if (typeof jsmeNomeclatureApplet === 'undefined' || !jsmeNomeclatureApplet ||
        typeof nameExamples === 'undefined' || !moleculeIds.every(id => nameExamples[id]?.classification) ||
        !window.JSmolReadyFlag || typeof selectedMol === 'undefined' || !selectedMol) return;
    clearInterval(poll);
    try {
      const nativeLocalSave = Jmol._localFileSaveFunction;
      Jmol._localFileSaveFunction = function (filename, data) {
        // Native JSmol calls this after its Save Image prompt, before making
        // the download anchor. Returning false leaves its encoding/save path
        // intact, including a user-chosen filename. Block obsolete callbacks.
        if (stopped) return true;
        if (activeExport?.view === '3d') {
          if (activeExport.cancelled) return true;
          if (typeof filename === 'string') activeExport.filename = filename.substring(filename.lastIndexOf('/') + 1);
        }
        return typeof nativeLocalSave === 'function' ? nativeLocalSave.apply(this, arguments) : false;
      };
      selectedMol = 'ethanol';
      fSelectMol();
      applyView();
      resizeObserver.observe(document.getElementById('nomeclature3D'));
      const canvas = document.getElementById('jmolAppletNomeclature_canvas2d');
      if (canvas) resizeObserver.observe(canvas);
      if (!document.querySelector('#jsmeNomeclatureSVG svg text')) return fail();
      synchronize('ready');
    } catch (error) {
      console.error('Molecule preview initialization failed', error);
      fail();
    }
  }, 100);
  window.addEventListener('pagehide', () => {
    stopped = true;
    restoreExportPrompt();
    commands.length = 0;
    clearInterval(poll);
    clearTimeout(waitTimer);
    cancelAnimationFrame(resizeFrame);
    resizeObserver.disconnect();
    window.removeEventListener('resize', scheduleResize);
    window.removeEventListener('message', onMessage);
    document.removeEventListener('click', onPNGDownload, true);
  }, { once: true });
})();
