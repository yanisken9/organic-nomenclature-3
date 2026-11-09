from pathlib import Path
p=Path('js/namelecule-game-repair.js')
s=p.read_text()
# Separate one-round validation from the legacy five-round game contract.
a=s.index('  function validateGameData(data) {')
b=s.index('\n  const engine =',a)
old=s[a:b]
roundbody=old[old.index('      ["title"'):old.index('\n    });\n    return data;')]
roundbody='\n'.join(line[4:] if line.startswith('    ') else line for line in roundbody.splitlines())
validation='''  function assert(condition, message) { if (!condition) throw new Error(message); }
  function text(value) { return typeof value === "string" && value.trim().length > 0; }
  function localAsset(value) { return text(value) && /^assets\\/[a-zA-Z0-9_/-]+\\.svg$/.test(value) && !value.includes(".."); }

  function validateRoundData(round) {
    assert(round && text(round.id), "Invalid round id");
    assert(round.guided === undefined || typeof round.guided === "boolean", "Invalid guided flag");
'''+roundbody+'''
    return round;
  }

  function validateGameData(data) {
    assert(data && data.schemaVersion === 1 && text(data.title) && text(data.description), "Invalid game metadata");
    assert(Array.isArray(data.rounds) && data.rounds.length === 5, "Expected one example and four challenges");
    const roundIds = new Set();
    data.rounds.forEach(function (round, index) {
      validateRoundData(round);
      assert(!roundIds.has(round.id), "Invalid round id");
      roundIds.add(round.id);
      assert(round.guided === (index === 0), "The first round must be the only guided example");
    });
    return data;
  }

  // Persist only legal answer data. A completion flag alone cannot restore success.
  function restoreRoundState(round, previous) {
    const restored = createRoundState(round);
    if (!previous || typeof previous !== "object") return restored;
    function permutation(value, expected) {
      return Array.isArray(value) && value.length === expected.length && new Set(value).size === expected.length &&
        value.every(function (entry) { return expected.includes(entry); });
    }
    ["attempts", "selectionMisses"].forEach(function (key) {
      if (Number.isSafeInteger(previous[key]) && previous[key] >= 0) restored[key] = previous[key];
    });
    const selectableIds = round.kind === "order" ? round.movablePartIds : round.parts.map(function (part) { return part.id; });
    if (selectableIds.includes(previous.selectedPartId)) restored.selectedPartId = previous.selectedPartId;
    if (round.kind === "replace") {
      if (restored.selectedPartId === round.targetPartId && round.choices.some(function (choice) { return choice.value === previous.selectedValue; })) {
        restored.selectedValue = previous.selectedValue;
      }
      const indices = round.choices.map(function (_, index) { return index; });
      if (permutation(previous.choiceOrder, indices)) restored.choiceOrder = previous.choiceOrder.slice();
    } else if (permutation(previous.order, round.movablePartIds)) restored.order = previous.order.slice();
    restored.submitted = previous.submitted === true && restored.attempts > 0;
    restored.solved = previous.solved === true && restored.submitted && evaluateRepair(round, restored).kind === "correct";
    return restored;
  }
'''
s=s[:a]+validation+s[b:]
s=s.replace('      solved: false\n','      solved: false,\n      submitted: false\n',1)
s=s.replace('evaluateRepair: evaluateRepair, summarizeGame: summarizeGame, validateGameData: validateGameData };','evaluateRepair: evaluateRepair, summarizeGame: summarizeGame, validateGameData: validateGameData,\n    validateRoundData: validateRoundData, restoreRoundState: restoreRoundState };')
# Retain the existing round UI in a lifecycle-owned reusable instance.
start=s.index('  function renderRound() {')
end=s.index('  function requestRestart() {',start)
roundui=s[start:end]
zoomstart=s.index('  function showDiagramZoom() {')
zoomend=s.index('  function restartGame() {',zoomstart)
zoom=s[zoomstart:zoomend]
roundui=roundui.replace('    replaceRoot(screen);','    root.replaceChildren(screen);\n    root.setAttribute("aria-busy", "false");')
roundui=roundui.replace('    focusHeading();','    const title = heading.querySelector("h1");\n    title.tabIndex = -1;\n    title.focus({ preventScroll: true });\n    if (standalone) window.scrollTo({ top: 0, behavior: "instant" });\n    if (state().solved) showSuccess(evaluateRepair(data, state()), false);')
roundui=roundui.replace('progressList()','options.progressList()')
roundui=roundui.replace('workshopLogo("workshop-logo-small")','workshopLogo("workshop-logo-small", assetBase)')
roundui=roundui.replace('node("div", { class: "round-topbar" }, [node("p", { class: "eyebrow round-game-brand" }, [workshopLogo("workshop-logo-small", assetBase), node("span", { class: "round-game-label", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" })]), options.progressList()])','node("div", { class: "round-topbar" }, [node("p", { class: "eyebrow round-game-brand" }, [workshopLogo("workshop-logo-small", assetBase), node("span", { class: "round-game-label", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" })])].concat(standalone ? [options.progressList()] : []))')
roundui=roundui.replace('[refs.sessionStats, button("Νέο παιχνίδι", "quiet", requestRestart)]','[refs.sessionStats].concat(standalone ? [button("Νέο παιχνίδι", "quiet", options.requestRestart)] : [])')
# Unique ids in embedded rounds, with standalone ids preserved for compatibility.
for text in ['"diagram-heading"','"check-helper"','"check-button"','"move-left"','"move-right"']:
 roundui=roundui.replace(text,'controlId('+text+')')
roundui=roundui.replace('"part-" + id','controlId("part-" + id)')
roundui=roundui.replace('"choice-" + index','controlId("choice-" + index)')
roundui=roundui.replace('"part-" + current.selectedPartId','controlId("part-" + current.selectedPartId)')
roundui=roundui.replace('const control = document.getElementById(id);','const control = Array.from(root.querySelectorAll("[id]")).find(function (entry) { return entry.id === id; });')
roundui=roundui.replace('    refs.image.onload = function () {\n      if (currentRender !== renderId) return;','    const loadId = ++imageLoadId;\n    refs.image.onload = function () {\n      if (destroyed || currentRender !== renderId || loadId !== imageLoadId) return;')
roundui=roundui.replace('    refs.image.onerror = function () { diagramFailure(currentRender); };','    refs.image.onerror = function () {\n      if (!destroyed && loadId === imageLoadId) diagramFailure(currentRender);\n    };')
roundui=roundui.replace('    refs.image.src = round().asset;','    refs.image.src = assetBase + round().asset;')
roundui=roundui.replace('    if (currentRender !== renderId) return;','    if (destroyed || currentRender !== renderId) return;')
roundui=roundui.replace('    refs.retryButton.disabled = !enabled;','    refs.retryButton.disabled = !enabled;\n    const continueButton = refs.next.querySelector("button");\n    if (continueButton) continueButton.disabled = !diagramsReady() || !current.solved;')
roundui=roundui.replace('        const choiceButton = button(choice.label, "choice-button", function () {\n          current.selectedValue', '        const choiceButton = button(choice.label, "choice-button", function () {\n          if (!diagramsReady() || current.solved) return;\n          current.selectedValue')
roundui=roundui.replace('          current.selectedValue = choice.value;\n          clearFeedback();','          current.selectedValue = choice.value;\n          current.submitted = false;\n          clearFeedback();')
roundui=roundui.replace('          updateControls(controlId("choice-" + index));','          updateControls(controlId("choice-" + index));\n          emitState();')
roundui=roundui.replace('          current.order = movePart', '          if (!diagramsReady() || current.solved) return;\n          current.submitted = false;\n          current.order = movePart')
roundui=roundui.replace('          refs.selectionStatus.textContent = "Ο κλάδος μετακινήθηκε. Δες την πρότασή σου και πάτησε Έλεγχος.";','          refs.selectionStatus.textContent = "Ο κλάδος μετακινήθηκε. Δες την πρότασή σου και πάτησε Έλεγχος.";\n          emitState();')
roundui=roundui.replace('    current.selectedPartId = id;','    current.selectedPartId = id;\n    current.submitted = false;')
roundui=roundui.replace('    updateControls(controlId("part-" + id));\n  }','    updateControls(controlId("part-" + id));\n    emitState();\n  }')
# Shared success/next rendering with a dedicated embedded Continue action.
ss=roundui.index('  function submitRepair() {')
se=roundui.index('  function retryRound() {',ss)
roundui=roundui[:ss]+'''  function showSuccess(result, fresh) {
    refs.feedback.classList.add("is-success");
    refs.feedback.replaceChildren(
      node("strong", { class: "success-title", text: "✓ Η επισκευή πέτυχε" }),
      node("span", { class: "success-name", text: round().correctName }),
      node("p", { class: "success-explanation", text: result.message })
    );
    const next = button(standalone ? options.continueLabel : "Συνεχίζω τη θεωρία", "primary", function () {
      if (!diagramsReady() || !state().solved) return;
      if (typeof options.onContinue === "function") options.onContinue(getState());
    });
    refs.next.replaceChildren(next);
    updateControls();
    if (fresh) {
      next.focus({ preventScroll: true });
      if (standalone) root.querySelector(".progress").replaceWith(options.progressList());
    }
  }

  function submitRepair() {
    if (!diagramsReady() || state().solved) return;
    const result = evaluateRepair(round(), state());
    if (result.kind === "incomplete" || result.kind === "wrongPart") return;
    state().attempts += 1;
    state().submitted = true;
    if (result.kind === "correct") {
      state().solved = true;
      // Publish the state before invoking the completion callback.
      emitState();
      if (destroyed) return;
      showSuccess(result, true);
      if (!destroyed && typeof options.onSolved === "function") options.onSolved(Object.assign({}, result), getState());
    } else {
      refs.feedback.replaceChildren(node("p", { text: result.message }));
      updateControls(controlId("check-button"));
      emitState();
    }
  }

'''+roundui[se:]
roundui=roundui.replace('    states[roundIndex] = createRoundState(round(), state());','    currentState = createRoundState(round(), state());')
roundui=roundui.replace('    if (first && !first.disabled) first.focus({ preventScroll: true });\n  }','    if (first && !first.disabled) first.focus({ preventScroll: true });\n    emitState();\n  }')
# Embedded zoom stays inside the host, without nesting a modal dialog.
zoom=zoom.replace('    const dialog = node("dialog", { class: "zoom-dialog", "aria-labelledby": "zoom-title" });','    const dialog = node(standalone ? "dialog" : "section", { class: "zoom-dialog", "aria-labelledby": controlId("zoom-title") });\n    zoomPanel = dialog;')
zoom=zoom.replace('    const close = button("Κλείσιμο", "secondary", function () { dialog.close(); });','    const close = button("Κλείσιμο", "secondary", closeZoom);')
zoom=zoom.replace('id: "zoom-title"','id: controlId("zoom-title")')
zoom=zoom.replace('    image.onerror = function () {','    zoomImage = image;\n    image.onerror = function () {\n      if (destroyed || zoomPanel !== dialog) return;')
zoom=zoom.replace('    image.src = round().asset;','    image.src = assetBase + round().asset;')
zoom=zoom.replace('    dialog.addEventListener("close", function () { dialog.remove(); });\n    document.body.append(dialog);\n    dialog.showModal();','    if (standalone) {\n      listen(dialog, "close", function () { dialog.remove(); zoomPanel = null; });\n      document.body.append(dialog);\n      dialog.showModal();\n    } else {\n      dialog.setAttribute("role", "region");\n      refs.zoomButton.setAttribute("aria-expanded", "true");\n      refs.zoomButton.disabled = true;\n      root.append(dialog);\n    }')
zoom=zoom.replace('    if (mainImageStatus !== "ready") return;','    if (destroyed || mainImageStatus !== "ready" || zoomPanel) return;')
zoom+='''  function closeZoom() {
    if (!zoomPanel) return;
    if (zoomImage) zoomImage.onerror = null;
    if (standalone) zoomPanel.close();
    else { zoomPanel.remove(); zoomPanel = null; }
    refs.zoomButton.setAttribute("aria-expanded", "false");
    refs.zoomButton.disabled = mainImageStatus !== "ready";
    refs.zoomButton.focus({ preventScroll: true });
  }

'''
# API and lifecycle declarations. All owned listeners are removable on destroy.
component='''  let nextMountId = 0;
  const mountedHosts = new WeakMap();

  function createRoundView(host, options, standalone) {
    assert(host && typeof host.replaceChildren === "function", "A round host is required");
    assert(options && typeof options === "object", "Round options are required");
    const data = validateRoundData(options.round);
    const existing = mountedHosts.get(host);
    if (existing) existing.destroy();
    const root = host;
    const prefix = standalone ? "" : "nl-repair-" + (++nextMountId) + "-";
    const assetBase = typeof options.assetBase === "string" && options.assetBase ? options.assetBase.replace(/\\/?$/, "/") : "";
    let currentState = restoreRoundState(data, options.initialState);
    let destroyed = false;
    let refs = {};
    let mainImageStatus = "loading";
    let renderId = 0;
    let imageLoadId = 0;
    let zoomPanel = null;
    let zoomImage = null;
    const listeners = [];
    const ownedClass = !standalone && !host.classList.contains("nl-repair-round");
    if (ownedClass) host.classList.add("nl-repair-round");
    function controlId(id) { return prefix + id; }
    function round() { return data; }
    function state() { return currentState; }
    function diagramsReady() { return !destroyed && mainImageStatus === "ready"; }
    function getState() { return JSON.parse(JSON.stringify(currentState)); }
    function emitState() {
      if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(getState());
    }
    function listen(element, event, handler) {
      const guarded = function (e) { if (!destroyed) handler(e); };
      element.addEventListener(event, guarded);
      listeners.push([element, event, guarded]);
    }
    function button(label, className, action, attributes) {
      const result = node("button", Object.assign({ type: "button", class: className, text: label }, attributes || {}));
      listen(result, "click", action);
      return result;
    }
    function destroy() {
      if (destroyed) return;
      destroyed = true;
      renderId += 1;
      imageLoadId += 1;
      listeners.forEach(function (entry) { entry[0].removeEventListener(entry[1], entry[2]); });
      listeners.length = 0;
      if (refs.image) { refs.image.onload = null; refs.image.onerror = null; }
      if (zoomImage) zoomImage.onerror = null;
      if (zoomPanel) {
        if (standalone && zoomPanel.open) zoomPanel.close();
        zoomPanel.remove();
        zoomPanel = null;
      }
      if (mountedHosts.get(host) === api) {
        host.replaceChildren();
        if (ownedClass) host.classList.remove("nl-repair-round");
        mountedHosts.delete(host);
      }
    }
    const api = { destroy: destroy, getState: getState };
    mountedHosts.set(host, api);

'''+''.join('  '+line+'\n' if line else '\n' for line in (roundui+zoom).splitlines())+'''    renderRound();
    return api;
  }

  global.NameleculeRepairGame = {
    mountRound: function (host, options) { return createRoundView(host, options, false); }
  };
'''
# Assemble shared helpers/API before the standalone root check.
engend=s.index('  if (typeof document === "undefined") return;')
nodepos=s.index('  function node(tag, attributes, children) {')
nodeend=s.index('  function focusHeading() {',nodepos)
helpers=s[nodepos:nodeend]
logopos=s.index('  function workshopLogo(className) {')
logoend=s.index('  function renderWelcome() {',logopos)
logo=s[logopos:logoend].replace('function workshopLogo(className)','function workshopLogo(className, assetBase)').replace('src: "assets/','src: (assetBase || "") + "assets/')
# Remove moved definitions while preserving the standalone shell.
shell=s[engend:]
for section in [s[nodepos:nodeend],s[logopos:logoend],s[start:end],s[zoomstart:zoomend]]:
 shell=shell.replace(section,'')
shell=shell.replace('  let refs = {};\n  let mainImageStatus = "loading";','  let activeRound = null;')
shell=shell.replace('  function replaceRoot(content) {\n','  function replaceRoot(content) {\n    if (activeRound) { activeRound.destroy(); activeRound = null; }\n')
shell=shell.replace('  function diagramsReady() {\n    return mainImageStatus === "ready";\n  }','''  function renderRound() {
    if (activeRound) activeRound.destroy();
    const index = roundIndex;
    activeRound = createRoundView(root, {
      round: round(), initialState: state(), assetBase: "", progressList: progressList,
      requestRestart: requestRestart,
      continueLabel: index === game.rounds.length - 1 ? "Δες τις επισκευές σου  →" : "Επόμενη αποστολή  →",
      onStateChange: function (current) { states[index] = current; },
      onContinue: function () {
        if (index === game.rounds.length - 1) renderResults();
        else { roundIndex += 1; renderRound(); }
      }
    }, true);
  }''')
s=s[:engend]+helpers+logo+component+shell
s=s.replace('/* Namelecule · Συνεργείο ονομάτων. Standalone, buildless and local assets only. */','/* Namelecule · Συνεργείο ονομάτων. Shared round UI, buildless and local assets only. */')
p.write_text(s)
p=Path('games/name-repair.html');s=p.read_text().replace('../js/namelecule-game-repair.js?v=logo-3d-20261104-r1','../js/namelecule-game-repair.js?v=checkpoint-pilot-20261104-r1');p.write_text(s)
