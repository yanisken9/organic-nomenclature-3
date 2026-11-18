/* Namelecule · Συνεργείο ονομάτων. Shared round UI, buildless and local assets only. */
(function (global) {
  "use strict";

  function initialChoiceOrder(round) {
    if (round.kind !== "replace") return [];
    const order = round.choices.map(function (_, index) { return index; });
    if (!round.guided) {
      for (let index = order.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        const previous = order[index];
        order[index] = order[swapIndex];
        order[swapIndex] = previous;
      }
    }
    return order;
  }

  function createRoundState(round, previous) {
    return {
      selectedPartId: null,
      selectedValue: null,
      order: round.kind === "order" ? round.movablePartIds.slice() : [],
      choiceOrder: previous && previous.choiceOrder ? previous.choiceOrder.slice() : initialChoiceOrder(round),
      attempts: previous ? previous.attempts : 0,
      selectionMisses: previous ? previous.selectionMisses : 0,
      solved: false,
      submitted: false
    };
  }

  function candidateName(round, state) {
    if (round.kind === "order") {
      const textById = Object.fromEntries(round.parts.map(function (part) { return [part.id, part.text]; }));
      return state.order.map(function (id) { return textById[id]; }).join("-") + textById[round.suffixPartId];
    }
    return round.parts.map(function (part) {
      return part.id === round.targetPartId && state.selectedValue !== null ? state.selectedValue : part.text;
    }).join("");
  }

  function movePart(order, partId, direction) {
    const next = order.slice();
    const index = next.indexOf(partId);
    const destination = index + direction;
    if ((direction === -1 || direction === 1) && index >= 0 && destination >= 0 && destination < next.length) {
      next[index] = next[destination];
      next[destination] = partId;
    }
    return next;
  }

  function evaluateRepair(round, state) {
    const name = candidateName(round, state);
    if (round.kind === "replace") {
      if (!state.selectedPartId || state.selectedValue === null) return { kind: "incomplete", name: name };
      if (state.selectedPartId !== round.targetPartId) return { kind: "wrongPart", name: name, message: round.feedback.wrongPart };
      if (state.selectedValue === round.correctValue) return { kind: "correct", name: name, message: round.successText };
      const original = round.parts.find(function (part) { return part.id === round.targetPartId; }).text;
      if (state.selectedValue === original) return { kind: "unchanged", name: name, message: round.feedback.unchanged };
      const choice = round.choices.find(function (item) { return item.value === state.selectedValue; });
      return { kind: "incorrect", name: name, message: choice && choice.feedback ? choice.feedback : round.feedback.incorrect };
    }
    const correct = state.order.length === round.correctOrder.length && state.order.every(function (id, index) {
      return id === round.correctOrder[index];
    });
    if (correct) return { kind: "correct", name: name, message: round.successText };
    const unchanged = state.order.every(function (id, index) { return id === round.movablePartIds[index]; });
    return { kind: unchanged ? "unchanged" : "incorrect", name: name, message: unchanged ? round.feedback.unchanged : round.feedback.incorrect };
  }

  function summarizeGame(rounds, states) {
    const challenges = rounds.map(function (round, index) { return { round: round, state: states[index] }; })
      .filter(function (entry) { return !entry.round.guided; });
    return {
      total: challenges.length,
      completed: challenges.filter(function (entry) { return entry.state && entry.state.solved; }).length,
      attempts: challenges.reduce(function (sum, entry) { return sum + (entry.state ? entry.state.attempts : 0); }, 0)
    };
  }

  function assert(condition, message) { if (!condition) throw new Error(message); }
  function text(value) { return typeof value === "string" && value.trim().length > 0; }
  function localAsset(value) { return text(value) && /^assets\/[a-zA-Z0-9_/-]+\.svg$/.test(value) && !value.includes(".."); }

  function validateRoundData(round) {
    assert(round && text(round.id), "Invalid round id");
    assert(round.guided === undefined || typeof round.guided === "boolean", "Invalid guided flag");
    ["title", "objective", "moleculeId", "diagramAlt", "correctName", "successText"].forEach(function (key) {
      assert(text(round[key]), "Missing round field " + key);
    });
    assert(localAsset(round.asset), "Invalid local diagram path");
    assert(Array.isArray(round.parts) && round.parts.length > 0, "Missing name parts");
    const ids = new Set();
    round.parts.forEach(function (part) {
      assert(part && text(part.id) && text(part.text) && text(part.label) && !ids.has(part.id), "Invalid name part");
      ids.add(part.id);
    });
    assert(round.feedback && ["wrongPart", "unchanged", "incorrect"].every(function (key) {
      return text(round.feedback[key]);
    }), "Missing targeted feedback");
    const solution = createRoundState(round);
    if (round.kind === "replace") {
      assert(ids.has(round.targetPartId) && text(round.correctValue), "Invalid replacement target");
      assert(Array.isArray(round.choices) && round.choices.length >= 2, "Missing replacement choices");
      const choiceValues = new Set();
      round.choices.forEach(function (choice) {
        assert(choice && text(choice.value) && text(choice.label) && !choiceValues.has(choice.value), "Invalid replacement choice");
        choiceValues.add(choice.value);
      });
      assert(choiceValues.has(round.correctValue), "Missing correct replacement");
      solution.selectedPartId = round.targetPartId;
      solution.selectedValue = round.correctValue;
    } else {
      assert(round.kind === "order" && Array.isArray(round.movablePartIds) && round.movablePartIds.length === 2, "Invalid ordering round");
      assert(new Set(round.movablePartIds).size === 2 && round.movablePartIds.every(function (id) { return ids.has(id); }), "Invalid movable groups");
      assert(ids.has(round.suffixPartId) && !round.movablePartIds.includes(round.suffixPartId), "Invalid fixed parent");
      assert(Array.isArray(round.correctOrder) && round.correctOrder.length === 2 && new Set(round.correctOrder).size === 2 && round.correctOrder.every(function (id) {
        return round.movablePartIds.includes(id);
      }), "Invalid correct group order");
      solution.order = round.correctOrder.slice();
    }
    assert(candidateName(round, solution) === round.correctName, "Correct name does not match name parts");
    assert(candidateName(round, createRoundState(round)) !== round.correctName, "The repair must begin with a different name");
    return round;
  }

  function validateGameData(data) {
    assert(data && data.schemaVersion === 2 && text(data.title) && text(data.description), "Invalid game metadata");
    assert(!Object.prototype.hasOwnProperty.call(data, "rounds") && Array.isArray(data.sets) && data.sets.length === 2, "Expected two quiz sets");
    const setIds = new Set();
    const roundIds = new Set();
    data.sets.forEach(function (set) {
      assert(set && ["alkanes-unbranched", "alkanes-branched"].includes(set.id) && !setIds.has(set.id), "Invalid set id");
      setIds.add(set.id);
      assert(text(set.title) && text(set.description) && Array.isArray(set.topics) && set.topics.length > 0 && set.topics.every(text), "Invalid set metadata");
      assert(Array.isArray(set.rounds) && set.rounds.length === 3, "Expected three quizzes per set");
      set.rounds.forEach(function (round) {
        validateRoundData(round);
        assert(!roundIds.has(round.id), "Invalid round id");
        roundIds.add(round.id);
        assert(round.guided === false, "Standalone rounds must be challenges");
      });
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

  const engine = { createRoundState: createRoundState, candidateName: candidateName, movePart: movePart,
    evaluateRepair: evaluateRepair, summarizeGame: summarizeGame, validateGameData: validateGameData,
    validateRoundData: validateRoundData, restoreRoundState: restoreRoundState };
  if (typeof module !== "undefined" && module.exports) module.exports = engine;
  global.NameleculeRepairEngine = engine;
  function node(tag, attributes, children) {
    const result = document.createElement(tag);
    Object.entries(attributes || {}).forEach(function (entry) {
      if (entry[0] === "class") result.className = entry[1];
      else if (entry[0] === "text") result.textContent = entry[1];
      else result.setAttribute(entry[0], entry[1]);
    });
    (children || []).forEach(function (child) { result.append(typeof child === "string" ? document.createTextNode(child) : child); });
    return result;
  }

  function button(label, className, action, attributes) {
    const result = node("button", Object.assign({ type: "button", class: className, text: label }, attributes || {}));
    result.addEventListener("click", action);
    return result;
  }

  function workshopLogo(className, assetBase) {
    return node("img", {
      class: className,
      src: (assetBase || "") + "assets/name-repair/workshop-logo-3d-v1.png",
      width: "128",
      height: "128",
      alt: "",
      "aria-hidden": "true"
    });
  }

  function diagramZoomIcon() {
    const icon = node("span", { class: "diagram-zoom-icon", "aria-hidden": "true" });
    const sharedIcon = global.MuLERIcons && global.MuLERIcons.zoomIn;
    // Main supplies the shared icon; isolated embedded mounts need no icon dependency.
    icon.innerHTML = typeof sharedIcon === "string" && sharedIcon.trim() ? sharedIcon :
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="7"/><path d="M15 15l6 6M10 6v8M6 10h8"/></svg>';
    const svg = icon.querySelector("svg");
    if (svg) { svg.setAttribute("aria-hidden", "true"); svg.setAttribute("focusable", "false"); }
    return icon;
  }

  const MISSION_REMINDERS = Object.freeze({
    "parent-length": "Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.",
    "bond-type": "Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.",
    "branch-locants": "Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.",
    "branch-multiplier": "Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων."
  });
  // Explicit compatibility metadata for the original authored questions.
  // Generated questions carry their own semantic fault.kind; never infer it from a part label.
  const AUTHORED_MISSIONS = Object.freeze({
    "unbranched-parent-four": "parent-length",
    "unbranched-parent-five": "parent-length",
    "unbranched-single-bond": "bond-type",
    "number-from-nearest": "branch-locants",
    "two-methyl-groups": "branch-multiplier",
    "alphabetical-branches": "alphabetical-order"
  });
  const AUTHORED_OBJECTIVES = Object.freeze({
    "parent-length": "Έλεγξε το μήκος της κύριας αλυσίδας και το συνθετικό που το δηλώνει.",
    "bond-type": "Έλεγξε το είδος των δεσμών μεταξύ ατόμων C.",
    "branch-locants": "Έλεγξε τα σημεία σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.",
    "branch-multiplier": "Έλεγξε πόσες ίδιες διακλαδώσεις υπάρχουν και πώς δηλώνεται το πλήθος τους.",
    "alphabetical-order": "Έλεγξε την αλφαβητική σειρά των διαφορετικών διακλαδώσεων."
  });

  function presentationForRound(round, options) {
    const basic = !options || options.difficulty !== "challenge";
    const authored = Object.prototype.hasOwnProperty.call(AUTHORED_MISSIONS, round.id) ? AUTHORED_MISSIONS[round.id] : null;
    const family = round.fault && round.fault.kind || authored;
    const condensed = round.moleculeId === "ethyl_3_dimethyl_2_5_hexane";
    const display = Object.assign({}, round);
    if (condensed) {
      display.asset = "assets/name-repair/condensed/ethyl_3_dimethyl_2_5_hexane.svg";
      display.diagramAlt = "Συνεπτυγμένος συντακτικός τύπος αλκανίου. Φαίνονται οι δεσμοί μεταξύ ατόμων C και οι ομάδες CH₃, CH₂ και CH.";
    }
    if (basic && authored) display.objective = AUTHORED_OBJECTIVES[authored];
    if (basic && round.kind === "replace" && Object.prototype.hasOwnProperty.call(MISSION_REMINDERS, family) &&
        round.feedback && typeof round.feedback.wrongPart === "string") {
      const reminder = MISSION_REMINDERS[family];
      display.feedback = Object.assign({}, round.feedback, {
        wrongPart: round.feedback.wrongPart.endsWith(reminder) ? round.feedback.wrongPart : round.feedback.wrongPart + " " + reminder
      });
    }
    return { round: display, emphasizeObjective: true, compactDiagramZoom: true,
      diagramRepresentation: condensed ? "condensed" : "expanded" };
  }

  // The same response-range policy serves a page and the lesson dialog.
  // Each owner supplies its viewport and scroll geometry; no focus or answer state is changed.
  function createResponseRevealer(options) {
    let moving = false;
    let disposed = false;
    const interrupts = [];
    function stop() {
      if (disposed || !moving) return;
      moving = false;
      options.scrollTo(options.scrollTop(), "instant");
    }
    function reveal(request) {
      if (disposed || !request || options.active && !options.active()) return;
      const start = request.start, end = request.end || start;
      if (!start || !end || !start.isConnected || !end.isConnected ||
          !options.host.contains(start) || !options.host.contains(end) ||
          typeof start.getBoundingClientRect !== "function" || typeof end.getBoundingClientRect !== "function") return;
      stop();
      const first = start.getBoundingClientRect(), last = end.getBoundingClientRect();
      if (first.height <= 0 || last.height <= 0) return;
      const viewport = options.viewport();
      const top = viewport.top, bottom = viewport.bottom;
      const rangeTop = Math.min(first.top, last.top), rangeBottom = Math.max(first.bottom, last.bottom);
      if (![top, bottom, rangeTop, rangeBottom].every(Number.isFinite) || bottom <= top) return;
      if (rangeTop >= top && rangeBottom <= bottom) return;
      const delta = rangeBottom - rangeTop > bottom - top || rangeTop < top ? rangeTop - top : rangeBottom - bottom;
      const current = options.scrollTop();
      const destination = Math.max(0, Math.min(options.maxScroll(), current + delta));
      if (!Number.isFinite(destination) || Math.abs(destination - current) < 1) return;
      const reduced = typeof global.matchMedia === "function" && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
      moving = !reduced;
      options.scrollTo(destination, reduced ? "instant" : "smooth");
    }
    const target = options.interruptTarget;
    if (target && typeof target.addEventListener === "function") {
      ["wheel", "touchstart", "pointerdown", "keydown", "pagehide"].forEach(function (event) {
        const eventOptions = { passive: true };
        target.addEventListener(event, stop, eventOptions);
        interrupts.push([event, eventOptions]);
      });
    }
    return { reveal: reveal, stop: stop, destroy: function () {
      if (disposed) return;
      stop();
      disposed = true;
      interrupts.forEach(function (entry) { target.removeEventListener(entry[0], stop, entry[1]); });
      interrupts.length = 0;
    } };
  }

  let nextMountId = 0;
  const mountedHosts = new WeakMap();
  const diagramFontMetrics = new Map();
  function sourceDiagramMetrics(url) {
    if (diagramFontMetrics.has(url)) return diagramFontMetrics.get(url);
    const promise = global.fetch(url, { credentials: "same-origin" }).then(function (response) {
      if (!response.ok) throw new Error("Diagram metrics unavailable");
      return response.text();
    }).then(function (source) {
      const svg = new global.DOMParser().parseFromString(source, "image/svg+xml").documentElement;
      const width = parseFloat(svg.getAttribute("width")), height = parseFloat(svg.getAttribute("height"));
      const font = Number(svg.getAttribute("data-uniform-atom-font-pixels"));
      if (svg.localName !== "svg" || ![width, height, font].every(Number.isFinite) || !(width > 0 && height > 0 && font > 0)) throw new Error("Unknown diagram scale");
      return { width: width, height: height, font: font };
    }).catch(function () { diagramFontMetrics.delete(url); return null; });
    diagramFontMetrics.set(url, promise);
    return promise;
  }

  function createRoundView(host, options, standalone) {
    assert(host && typeof host.replaceChildren === "function", "A round host is required");
    assert(options && typeof options === "object", "Round options are required");
    const data = validateRoundData(options.round);
    const emphasizeObjective = options.emphasizeObjective === true;
    const condensedDiagram = options.diagramRepresentation === "condensed";
    const compactDiagramZoom = options.compactDiagramZoom === true;
    // New hosts explicitly opt in; older Main/native hosts retain their layout.
    const viewportEnabled = options.viewport === true && !!global.NameleculeGameViewport;
    const lessonPresentation = viewportEnabled && !standalone && typeof host.closest === "function" && !!host.closest(".nl-vp-choice");
    const existing = mountedHosts.get(host);
    if (existing) existing.destroy();
    const root = host;
    const prefix = standalone ? "" : "nl-repair-" + (++nextMountId) + "-";
    const assetBase = typeof options.assetBase === "string" && options.assetBase ? options.assetBase.replace(/\/?$/, "/") : "";
    let currentState = restoreRoundState(data, options.initialState);
    let destroyed = false;
    let refs = {};
    let mainImageStatus = "loading";
    let lastSuccessActionsReady = null;
    let renderId = 0;
    let imageLoadId = 0;
    let imageMetrics = null;
    let diagramObserver = null;
    let zoomPanel = null;
    let zoomImage = null;
    let listeners = [];
    let viewport = null;
    let demandTextContext = null;
    let pagers = [];
    let viewportStage = "edit";
    let viewportView = "answer";
    const ownedClass = !host.classList.contains("nl-repair-round");
    if (ownedClass) host.classList.add("nl-repair-round");
    const pageScroller = function () { return global.document.scrollingElement || global.document.documentElement; };
    const pageReveal = standalone && !viewportEnabled ? createResponseRevealer({
      host: root, interruptTarget: global,
      active: function () { return !destroyed && !zoomPanel && root.isConnected; },
      viewport: function () { return { top: 12, bottom: global.document.documentElement.clientHeight - 12 }; },
      scrollTop: function () { return pageScroller().scrollTop; },
      maxScroll: function () { return pageScroller().scrollHeight - global.document.documentElement.clientHeight; },
      scrollTo: function (top, behavior) {
        if (typeof global.scrollTo === "function") global.scrollTo({ top: top, behavior: behavior });
        else pageScroller().scrollTop = top;
      }
    }) : null;
    function controlId(id) { return prefix + id; }
    function round() { return data; }
    function state() { return currentState; }
    function diagramsReady() { return !destroyed && mainImageStatus === "ready"; }
    function getState() { return JSON.parse(JSON.stringify(currentState)); }
    function emitState() {
      if (!destroyed && typeof options.onStateChange === "function") options.onStateChange(getState());
    }
    function revealResponse(reason, start, end) {
      if (destroyed || viewportEnabled) return;
      const request = { reason: reason, start: start, end: end || start };
      if (pageReveal) pageReveal.reveal(request);
      else if (typeof options.onReveal === "function") options.onReveal(request);
    }
    function listen(element, event, handler) {
      const guarded = function (e) { if (!destroyed) handler(e); };
      element.addEventListener(event, guarded);
      listeners.push([element, event, guarded]);
    }
    function replaceChildren(element) {
      const children = Array.prototype.slice.call(arguments, 1);
      // Release replaced controls instead of retaining their nodes for the whole lesson.
      listeners = listeners.filter(function (entry) {
        if (!element.contains(entry[0])) return true;
        entry[0].removeEventListener(entry[1], entry[2]);
        return false;
      });
      element.replaceChildren.apply(element, children);
    }
    function button(label, className, action, attributes) {
      const result = node("button", Object.assign({ type: "button", class: className, text: label }, attributes || {}));
      listen(result, "click", action);
      return result;
    }
    function destroy() {
      if (destroyed) return;
      if (pageReveal) pageReveal.destroy();
      if (viewport) viewport.destroy();
      pagers.forEach(function (pager) { pager.destroy(); }); pagers = [];
      host.classList.remove("nl-repair-viewport", "nl-repair-sequential", "nl-lesson-game", "nl-inline-results", "repair-has-result", "repair-solved");
      if (diagramObserver) diagramObserver.disconnect();
      ["data-repair-stage", "data-repair-view", "data-repair-step"].forEach(function (name) { host.removeAttribute(name); });
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
    const api = { destroy: destroy, getState: getState, refresh: function () { if (viewport) viewport.refresh(); refreshPagers(); } };
    mountedHosts.set(host, api);

    function renderRound() {
      const currentRender = ++renderId;
      mainImageStatus = "loading";
      const data = round();
      refs = {};
      const heading = node("div", { class: "round-heading" });
      if (data.guided) heading.append(node("span", { class: "guided-pill", text: "Πρώτα δοκιμάζουμε μαζί" }));
      if (standalone && options.setTitle) heading.append(node("p", { class: "round-set-name", text: "Αλκάνια · " + options.setTitle }));
      heading.append(node(lessonPresentation ? "h2" : "h1", { class: lessonPresentation ? "nl-game-round-title" : "", text: data.title }), node("p", {
        class: emphasizeObjective ? "round-objective is-emphasized" : "round-objective", text: data.objective
      }));
      const steps = node("ol", { class: "compact-steps", "aria-label": "Βήματα αποστολής" }, ["Παρατήρησε τη δομή", "Επισκεύασε το όνομα", "Έλεγξε την επιλογή σου"].map(function (text, index) {
        return node("li", {}, [node("span", { "aria-hidden": "true", text: String(index + 1) }), text]);
      }));
      refs.image = node("img", { class: "diagram-image", alt: data.diagramAlt, draggable: "false" });
      refs.imageStatus = node("div", { class: "image-status", role: "status", "aria-live": "polite" });
      refs.zoomButton = button(compactDiagramZoom ? "" : "Μεγέθυνση σχεδίου",
        compactDiagramZoom ? "quiet diagram-zoom-button" : "quiet", showDiagramZoom);
      if (compactDiagramZoom) {
        refs.zoomButton.setAttribute("aria-label", "Μεγέθυνση σχεδίου");
        refs.zoomButton.setAttribute("title", "Μεγέθυνση σχεδίου");
        refs.zoomButton.setAttribute("aria-expanded", "false");
        refs.zoomButton.append(diagramZoomIcon());
      }
      const diagram = node("section", { class: "diagram-card", "aria-labelledby": controlId("diagram-heading") }, [
        node("div", { class: "card-heading" }, [node("h2", { id: controlId("diagram-heading"), text: "Η δομή στο επίκεντρο" }), node("div", { class: "diagram-tools" }, [node("span", { class: condensedDiagram ? "diagram-representation-label" : "", text: condensedDiagram ? "Συνεπτυγμένος συντακτικός τύπος" : "Ανεπτυγμένος τύπος" }), refs.zoomButton])]),
        node("figure", { class: "diagram-figure" }, [node("div", { class: "diagram-stage" }, [refs.image]), node("figcaption", { text: "Παρατήρησε την κύρια αλυσίδα και τους κλάδους." })]),
        refs.imageStatus
      ]);
      const broken = candidateName(data, createRoundState(data));
      refs.parts = node("div", { class: "name-parts", role: "group", "aria-label": "Κομμάτια του ονόματος" });
      refs.selectionStatus = node("p", { class: "part-selection-status", role: "status", "aria-live": "polite" });
      refs.choices = node("div", { class: "choices", role: "group", "aria-label": "Επιλογές αντικατάστασης" });
      refs.choiceFieldset = node("fieldset", { class: "choice-fieldset" }, [node("legend", { text: "2. Διάλεξε την αντικατάσταση" }), refs.choices]);
      refs.orderControls = node("div", { class: "order-controls" });
      refs.candidateName = node("strong", { class: "candidate-name" });
      refs.candidate = node("div", { class: "candidate", "aria-live": "polite", "aria-atomic": "true" }, [node("span", { class: "candidate-label", text: "Η πρότασή σου για έλεγχο" }), refs.candidateName]);
      refs.checkButton = button("Έλεγχος", "primary", submitRepair);
      refs.checkButton.id = controlId("check-button");
      refs.checkHelper = node("p", { class: "check-helper", id: controlId("check-helper") });
      refs.checkButton.setAttribute("aria-describedby", controlId("check-helper"));
      refs.feedback = node("div", { class: "feedback", role: "status", "aria-live": "polite", "aria-atomic": "true" });
      refs.next = node("div", { class: "round-next" });
      const repair = node("section", { class: "repair-card", "aria-label": "Επισκευή ονόματος" }, [
        node("span", { class: "section-label", text: "ΟΝΟΜΑ ΠΟΥ ΧΡΕΙΑΖΕΤΑΙ ΕΠΙΣΚΕΥΗ" }),
        node("div", { class: "broken-name" + (lessonPresentation ? " nl-game-stimulus-name" : ""), text: broken }),
        node("h2", { class: "step-heading", text: data.kind === "order" ? "1. Βάλε τους κλάδους στη σειρά" : "1. Ποιο κομμάτι θα αλλάξεις;" }),
        node("p", { class: "step-description", text: data.kind === "order" ? "Διάλεξε έναν κλάδο και μετακίνησέ τον με τα βέλη. Η κύρια αλυσίδα μένει στο τέλος." : "Πάτησε το κομμάτι που δεν ταιριάζει με τη δομή." }),
        refs.parts, refs.selectionStatus, refs.orderControls, refs.choiceFieldset, refs.candidate,
        node("div", { class: "repair-actions" }, [refs.checkButton]),
        refs.checkHelper, refs.feedback
      ]);
      refs.sessionStats = node("span");
      const brand = lessonPresentation ? node("div", { class: "round-game-brand nl-game-identity" }, [
        workshopLogo("workshop-logo-small nl-game-logo", assetBase), node("h1", { class: "nl-game-title", text: "Συνεργείο ονομάτων" })
      ]) : node("p", { class: "eyebrow round-game-brand" }, [workshopLogo("workshop-logo-small", assetBase), node("span", { class: "round-game-label", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" })]);
      const topbar = [brand];
      if (lessonPresentation) topbar.push(node("p", { class: "nl-game-mission", text: "Παρατήρησε τη δομή. Εντόπισε το λάθος και επισκεύασε το όνομα." }));
      if (standalone) topbar.push(options.progressList());
      const screen = node("div", { class: "round-screen" }, [
        node("div", { class: "round-topbar" }, topbar),
        heading, steps,
        node("div", { class: "bench" }, [node("div", { class: "visual-side" }, [diagram]), node("div", { class: "repair-side" }, [repair, refs.next])]),
        node("div", { class: "session-row" }, [refs.sessionStats].concat(standalone ? [button("Επιστροφή στα σετ", "quiet", options.requestRestart)] : []))
      ]);
      root.replaceChildren(screen);
      if (viewportEnabled) configureViewport(screen, heading, diagram, repair);
      root.setAttribute("aria-busy", "false");
      loadDiagram(currentRender);
      updateControls();
      const title = lessonPresentation ? root.querySelector(".nl-game-title") : heading.querySelector("h1");
      title.tabIndex = -1;
      title.focus({ preventScroll: true });
      if (standalone && !viewportEnabled) window.scrollTo({ top: 0, behavior: "instant" });
      if (state().solved) showSuccess(evaluateRepair(data, state()), false);
      else if (state().submitted) {
        const result = evaluateRepair(data, state());
        if (result.message) { replaceChildren(refs.feedback, node("p", { text: result.message })); if (viewportEnabled) showViewportFeedback(false); }
      }
      if (data.kind === "replace" && state().selectedPartId && state().selectedPartId !== data.targetPartId) {
        refs.selectionStatus.textContent = data.feedback.wrongPart;
      }
    }

    function refreshPagers() {
      if (destroyed) return;
      pagers.forEach(function (pager) { pager.refresh(); });
      refreshInlineEditorMinimum();
      // Re-evaluate a nav row that disappeared once a complete item fitted.
      if (lessonPresentation) {
        pagers.forEach(function (pager) { pager.refresh(); });
        refreshInlineEditorMinimum();
      }
    }
    function refreshInlineEditorMinimum() {
      if (!lessonPresentation || !refs.repairCard) return;
      const repair = refs.repairCard;
      const active = root.classList.contains("repair-has-result") && !root.classList.contains("repair-solved");
      if (!active) {
        repair.style.removeProperty("min-height");
        [refs.partPage, refs.choicePage, refs.parts, refs.choices].forEach(function (element) { element.style.removeProperty("min-height"); });
        [refs.parts, refs.choices].forEach(function (element) { element.parentElement.style.removeProperty("min-height"); });
        return;
      }
      function number(value) { return parseFloat(value) || 0; }
      function outerHeight(element) {
        const style = global.getComputedStyle(element);
        if (style.display === "none" || style.position === "absolute" || !element.getClientRects().length) return 0;
        return element.getBoundingClientRect().height + number(style.marginTop) + number(style.marginBottom);
      }
      [refs.parts, refs.choices].forEach(function (content) {
        if (!content.getClientRects().length) return;
        const boxes = Array.from(content.querySelectorAll("button,.fixed-suffix")).filter(function (item) { return item.getClientRects().length; }).map(function (item) { return item.getBoundingClientRect(); });
        const tallest = boxes.reduce(function (height, box) { return Math.max(height, box.height); }, 0);
        const style = global.getComputedStyle(content);
        const padding = number(style.paddingTop) + number(style.paddingBottom);
        const extent = boxes.length ? Math.max.apply(null, boxes.map(function (box) { return box.bottom; })) - Math.min.apply(null, boxes.map(function (box) { return box.top; })) + padding : 0;
        const singleRow = tallest + padding;
        // The shared pager advances by at least 24px. Preserve enough overlap
        // for a whole item when the content occupies more than a single row.
        const minimum = Math.ceil(Math.max(singleRow, extent > singleRow + 2 ? tallest + 24 : 0));
        content.style.minHeight = minimum + "px";
        const wrapper = content.parentElement, nav = wrapper.querySelector(".nl-vp-pager-nav");
        wrapper.style.minHeight = Math.ceil(minimum + (nav ? outerHeight(nav) : 0)) + "px";
      });
      const page = root.dataset.repairStep === "choices" ? refs.choicePage : refs.partPage;
      function minimumFor(container) {
        const style = global.getComputedStyle(container);
        const children = Array.from(container.children).filter(function (child) { return outerHeight(child) > 0; });
        return children.reduce(function (height, child) {
          if (child === refs.choiceFieldset) {
            const fieldStyle = global.getComputedStyle(child), legend = child.querySelector("legend");
            return height + (legend ? outerHeight(legend) : 0) + number(refs.choices.parentElement.style.minHeight) + number(fieldStyle.paddingTop) + number(fieldStyle.paddingBottom);
          }
          if (child === page || child === refs.parts.parentElement) return height + number(child.style.minHeight);
          return height + outerHeight(child);
        }, number(style.paddingTop) + number(style.paddingBottom) + number(style.borderTopWidth) + number(style.borderBottomWidth)) + Math.max(0, children.length - 1) * number(style.rowGap);
      }
      page.style.minHeight = Math.ceil(minimumFor(page)) + "px";
      repair.style.minHeight = Math.ceil(minimumFor(repair)) + "px";
    }
    function setViewportStage(stage, view) {
      viewportStage = stage;
      if (view) viewportView = view;
      root.setAttribute("data-repair-stage", stage);
      root.setAttribute("data-repair-view", viewportView);
      if (refs.stageTabs) refs.stageTabs.querySelectorAll("[data-repair-view-button]").forEach(function (control) {
        control.setAttribute("aria-pressed", String(stage === "edit" && control.dataset.repairViewButton === viewportView));
      });
      refreshPagers();
      if (viewport) viewport.refresh();
      publishSuccessActionsReady();
    }
    function showViewportFeedback(solved) {
      if (!viewportEnabled) return;
      refs.feedbackBack.hidden = lessonPresentation || solved;
      refs.feedbackInspect.hidden = lessonPresentation || !solved;
      refs.feedbackHeading.textContent = solved ? "Η επισκευή ολοκληρώθηκε" : "Παρατήρησε την εξήγηση";
      if (lessonPresentation) {
        // A restored result belongs to the same attempt and selected view too.
        refs.feedbackStage.hidden = false;
        root.classList.add("repair-has-result");
        root.classList.toggle("repair-solved", solved);
        refs.feedback.scrollTop = 0;
        refreshPagers();
        if (viewport) viewport.refresh();
        publishSuccessActionsReady();
        return;
      }
      setViewportStage("feedback");
      refs.feedbackHeading.focus({ preventScroll: true });
    }
    function configureViewport(screen, heading, diagram, repair) {
      root.classList.add("nl-repair-viewport");
      if (lessonPresentation) {
        root.classList.add("nl-lesson-game", "nl-inline-results");
        diagram.classList.add("nl-game-stimulus-formula");
        if (typeof global.ResizeObserver === "function") {
          if (diagramObserver) diagramObserver.disconnect();
          diagramObserver = new global.ResizeObserver(fitDiagramImage);
          diagramObserver.observe(diagram.querySelector(".diagram-stage"));
        }
      }
      const tabs = node("div", { class: "repair-stage-tabs", "aria-label": "Προβολή αποστολής" });
      [ ["structure", "Δομή"], ["answer", "Επισκευή"] ].forEach(function (entry) {
        const control = button(entry[1], "secondary repair-view-button", function () { setViewportStage("edit", entry[0]); });
        control.dataset.repairViewButton = entry[0]; tabs.append(control);
      });
      tabs.append(button("Οδηγίες", "quiet", function () { setViewportStage("instructions"); refs.instructionsHeading.focus({ preventScroll: true }); }));
      refs.stageTabs = tabs;
      heading.after(tabs);
      const partHeading = repair.querySelector(".step-heading"), partDescription = repair.querySelector(".step-description");
      refs.repairCard = repair;
      const partPage = refs.partPage = node("div", { class: "repair-part-page" }, [partHeading, refs.parts, refs.orderControls]);
      const partsBack = button(lessonPresentation ? "← Κομμάτια" : "← Κομμάτια ονόματος", "quiet repair-parts-back", function () { root.dataset.repairStep = "parts"; refreshPagers(); }, { "aria-label": "Επιστροφή στα κομμάτια του ονόματος" });
      const choicePage = refs.choicePage = node("div", { class: "repair-choice-page" }, lessonPresentation ? [refs.choiceFieldset] : [partsBack, refs.choiceFieldset]);
      if (lessonPresentation) tabs.append(partsBack);
      repair.querySelector(".broken-name").after(partPage, choicePage);
      partDescription.remove(); refs.selectionStatus.remove();
      const instructions = node("section", { class: "repair-instructions-stage" }, [
        node("div", { class: "repair-stage-heading" }, [refs.instructionsHeading = node("h2", { tabindex: "-1", text: "Πώς επισκευάζω το όνομα" }), button("Στην επισκευή", "secondary", function () { setViewportStage("edit", "answer"); })]),
        refs.instructionsContent = node("div", { class: "repair-instructions-content" }, [
          node("p", { text: round().objective }), screen.querySelector(".compact-steps"), partDescription,
          node("p", { text: "Διάλεξε κομμάτι και αντικατάσταση ή μετακίνησε έναν κλάδο με τα βέλη. Η μεγέθυνση ανοίγει ολόκληρη τη δομή σε χωριστή προβολή." }), refs.selectionStatus, refs.checkHelper
        ])
      ]);
      const feedbackStage = refs.feedbackStage = node("section", { class: "repair-feedback-stage" }, [
        node("div", { class: "repair-stage-heading" }, [refs.feedbackHeading = node("h2", { tabindex: "-1", text: "Παρατήρησε την εξήγηση" }),
          refs.feedbackBack = button("Επιστροφή στην προσπάθεια", "secondary", function () { setViewportStage("edit", "answer"); refs.checkButton.focus({ preventScroll: true }); }),
          refs.feedbackInspect = button("Δες τη δομή", "secondary", function () { setViewportStage("edit", "structure"); })]),
        refs.feedback, refs.next
      ]);
      screen.append(instructions);
      if (lessonPresentation) {
        feedbackStage.classList.add("nl-inline-result");
        feedbackStage.setAttribute("aria-label", "Αποτέλεσμα επισκευής");
        feedbackStage.hidden = true;
        screen.querySelector(".repair-side").append(feedbackStage);
        const submission = node("div", { class: "repair-submission" }, [refs.candidate, repair.querySelector(".repair-actions")]);
        repair.append(submission);
        refs.feedbackBack.hidden = refs.feedbackInspect.hidden = true;
      } else screen.append(feedbackStage);
      repair.querySelector(".repair-actions").append(button("Δες την εξήγηση", "quiet repair-feedback-open", function () { showViewportFeedback(state().solved); }));
      refs.feedbackOpen = repair.querySelector(".repair-feedback-open"); refs.feedbackOpen.hidden = true;
      // A solved structure remains inspectable, with a direct route back to its actions.
      tabs.append(refs.feedbackReturn = button("Στην εξήγηση", "secondary", function () { showViewportFeedback(state().solved); }));
      refs.feedbackReturn.hidden = true;
      root.dataset.repairStep = round().kind === "replace" && state().selectedPartId === round().targetPartId ? "choices" : "parts";
      setViewportStage("edit", "answer");
      [ [refs.parts, "y", "Κομμάτια ονόματος"], [refs.choices, "y", "Αντικαταστάσεις"],
        [repair.querySelector(".broken-name"), "x", "Όνομα για επισκευή"], [refs.candidateName, "x", "Η πρότασή σου"],
        [refs.instructionsContent, "y", "Οδηγίες"], [refs.feedback, "y", "Εξήγηση επισκευής"] ].forEach(function (entry) {
        pagers.push(global.NameleculeGameViewport.pager(entry[0], { axis: entry[1], label: entry[2], overlap: entry[0] === refs.parts || entry[0] === refs.choices ? 64 : undefined }));
      });
      viewport = global.NameleculeGameViewport.mount(root, { kind: "repair", document: standalone,
        preferred: lessonPresentation ? preferredViewport : null, onResize: function (size) {
        const responsiveHeight = lessonPresentation ? size.availableHeight : size.height;
        root.classList.toggle("nl-repair-sequential", size.width < 760 || responsiveHeight < 430); refreshPagers(); fitDiagramImage();
        // Responsive structure/answer visibility also changes which actions
        // are actually reachable, even when the solved state is unchanged.
        if (lessonPresentation) publishSuccessActionsReady();
      } });
    }

    function preferredViewport() {
      if (!lessonPresentation || destroyed || !diagramsReady() || !imageMetrics) return null;
      const shared = global.NameleculeGameViewport, number = function (value) { return parseFloat(value) || 0; };
      const width = root.getBoundingClientRect().width;
      if (!(width > 0)) return null;
      const sequential = width < 760 || shared.availableHeight(root) < 430;
      const css = function (element) { return global.getComputedStyle(element); };
      const vertical = function (style) { return number(style.paddingTop) + number(style.paddingBottom) + number(style.borderTopWidth) + number(style.borderBottomWidth); };
      const horizontal = function (style) { return number(style.paddingLeft) + number(style.paddingRight) + number(style.borderLeftWidth) + number(style.borderRightWidth); };
      const line = function (style) { return number(style.lineHeight) || number(style.fontSize) * 1.4; };
      if (!demandTextContext) demandTextContext = document.createElement("canvas").getContext("2d");
      function textWidth(value, style) {
        if (!demandTextContext) return String(value).length * number(style.fontSize) * .6;
        demandTextContext.font = style.fontStyle + " " + style.fontWeight + " " + style.fontSize + " " + style.fontFamily;
        return demandTextContext.measureText(value).width;
      }
      function textHeight(value, style, available) {
        const limit = Math.max(1, available - horizontal(style)), space = textWidth(" ", style);
        let rows = 1, used = 0;
        String(value).trim().split(/\s+/).forEach(function (word) {
          const extent = textWidth(word, style);
          if (used && used + space + extent > limit) { rows++; used = 0; }
          rows += Math.max(0, Math.ceil(extent / limit) - 1);
          used = (used ? used + space : 0) + Math.min(limit, extent);
        });
        return rows * line(style) + vertical(style);
      }
      function controlsHeight(container, available) {
        const style = css(container), inner = Math.max(1, available - horizontal(style));
        const items = Array.from(container.querySelectorAll("button,.fixed-suffix"));
        let rows = 1, used = 0, tallest = 0;
        items.forEach(function (item) {
          const itemStyle = css(item), naturalWidth = textWidth(item.textContent, itemStyle) + horizontal(itemStyle) + (item.classList.contains("choice-button") ? 22 : 0);
          const itemWidth = Math.min(inner, naturalWidth);
          if (used && used + number(style.columnGap) + itemWidth > inner) { rows++; used = 0; }
          used += (used ? number(style.columnGap) : 0) + itemWidth;
          tallest = Math.max(tallest, number(itemStyle.minHeight), textHeight(item.textContent, itemStyle, itemWidth));
        });
        // A complete longest item plus the existing pager's 24px minimum
        // advance keeps every row reachable without reserving all the choices.
        return Math.ceil(tallest + vertical(style) + (rows > 1 ? 24 + 40 : 0));
      }
      const bench = root.querySelector(".bench"), benchStyle = css(bench), gap = number(benchStyle.columnGap);
      const diagramWidth = sequential ? width : (width - gap) * .95 / 2.1;
      const sideWidth = sequential ? width : (width - gap) * 1.15 / 2.1;
      // Reserve the narrower editor used alongside a result from the outset.
      const editorWidth = sequential ? sideWidth : (sideWidth - 7) * 1.1 / 2;
      const repairStyle = css(refs.repairCard), editorInner = Math.max(1, editorWidth - Math.max(22, horizontal(repairStyle)));
      const broken = refs.repairCard.querySelector(".broken-name"), brokenStyle = css(broken);
      const brokenHeight = Math.max(52, line(brokenStyle) + vertical(brokenStyle)) + (textWidth(broken.textContent, brokenStyle) > editorInner - horizontal(brokenStyle) ? 40 : 0);
      const headingStyle = css(refs.partPage.querySelector(".step-heading"));
      const partHeight = textHeight(refs.partPage.querySelector(".step-heading").textContent, headingStyle, editorInner) + 5 + controlsHeight(refs.parts, editorInner);
      const legend = refs.choiceFieldset.querySelector("legend"), legendStyle = css(legend);
      const choiceHeight = round().kind === "replace" ? textHeight(legend.textContent, legendStyle, editorInner) + 5 + controlsHeight(refs.choices, editorInner) : 0;
      const orderStyle = css(refs.orderControls), orderButtons = Array.from(refs.orderControls.querySelectorAll("button"));
      const orderWidth = orderButtons.reduce(function (sum, item) { const style = css(item); return sum + textWidth(item.textContent, style) + horizontal(style); }, Math.max(0, orderButtons.length - 1) * number(orderStyle.columnGap));
      const orderHeight = round().kind === "order" ? Math.max.apply(null, orderButtons.map(function (item) { const style = css(item); return Math.max(number(style.minHeight), line(style) + vertical(style)); })) * (orderWidth > editorInner ? orderButtons.length : 1) + 5 : 0;
      const candidateStyle = css(refs.candidateName), candidateWidth = Math.max(1, editorInner - 97 - horizontal(css(refs.candidate)));
      const initialCandidate = { selectedValue: null, order: round().kind === "order" ? round().movablePartIds : [] };
      const candidateNames = [round().correctName, candidateName(round(), initialCandidate)].concat(round().kind === "replace" ? round().choices.map(function (choice) {
        return round().parts.map(function (part) { return part.id === round().targetPartId ? choice.value : part.text; }).join("");
      }) : []);
      const candidateHeight = 29 + 14 + vertical(css(refs.candidate)) + (candidateNames.some(function (name) { return textWidth(name, candidateStyle) > candidateWidth; }) ? (sequential ? 23 : 40) : 0);
      const editorHeight = Math.max(22, vertical(repairStyle)) + 14 + brokenHeight + Math.max(partHeight + orderHeight, choiceHeight) + Math.max(40, candidateHeight) + 4 * 6;
      const feedbackStyle = css(refs.feedback), nextStyle = css(refs.next);
      const actionLabels = [options.continueLabel || "Συνεχίζω τη θεωρία"];
      if (typeof options.onNewPractice === "function") actionLabels.push(options.newPracticeLabel || "Άλλη τριάδα για εξάσκηση");
      if (typeof options.onOtherGame === "function") actionLabels.push(options.otherGameLabel || "Άλλο παιχνίδι");
      const resultWidth = Math.max(1, sequential ? sideWidth : (sideWidth - 7) * .9 / 2);
      // Success can expose all continuation actions, even when the initial
      // editor has none. Reserve one readable feedback line and its local nav.
      const actionRows = actionLabels.reduce(function (height, label) {
        const buttonStyle = css(refs.checkButton), lines = Math.max(1, Math.ceil(textWidth(label, buttonStyle) / Math.max(1, resultWidth - 40)));
        return height + Math.max(39, lines * 18.2 + 16);
      }, 0) + Math.max(0, actionLabels.length - 1) * Math.max(7, number(nextStyle.rowGap));
      const resultHeight = Math.max(92, 16 + line(feedbackStyle) + vertical(feedbackStyle) + 40 + actionRows + 5);
      const diagram = root.querySelector(".diagram-card"), diagramStyle = css(diagram), figure = diagram.querySelector(".diagram-figure"), figureStyle = css(figure);
      const drawingWidth = Math.max(1, diagramWidth - horizontal(diagramStyle) - horizontal(figureStyle));
      const formulaPx = number(css(root).getPropertyValue("--nl-game-formula-px")) || 28;
      const drawingHeight = imageMetrics.height * Math.min(formulaPx / imageMetrics.font, drawingWidth / imageMetrics.width);
      const cardHeader = diagram.querySelector(".card-heading"), headerStyle = css(cardHeader), caption = figure.querySelector("figcaption"), captionStyle = css(caption);
      const diagramHeight = vertical(diagramStyle) + Math.max(50, vertical(headerStyle) + 36) + vertical(figureStyle) + drawingHeight + textHeight(caption.textContent, captionStyle, drawingWidth);
      const workspaceHeight = Math.max(diagramHeight, sequential ? editorHeight + resultHeight + 7 : Math.max(editorHeight, resultHeight));
      return shared.preferred(root, bench, workspaceHeight, "repair:" + prefix + round().id, { exclude: [root.querySelector(".repair-instructions-stage")] });
    }

    function fitDiagramImage() {
      if (!lessonPresentation || !imageMetrics || !refs.image || !refs.image.naturalWidth || destroyed) return;
      const stage = refs.image.parentElement;
      const width = stage.clientWidth, height = stage.clientHeight;
      const requested = Number(global.getComputedStyle(root).getPropertyValue("--nl-game-formula-px"));
      if (!(width > 0 && height > 0 && requested >= 20 && requested <= 36)) return;
      const preferredScale = requested / imageMetrics.font;
      const scale = Math.min(preferredScale, width / imageMetrics.width, height / imageMetrics.height);
      const targetWidth = imageMetrics.width * scale, targetHeight = imageMetrics.height * scale;
      if (Math.abs(parseFloat(refs.image.style.width) - targetWidth) > .05 || !refs.image.style.width) refs.image.style.width = targetWidth + "px";
      if (Math.abs(parseFloat(refs.image.style.height) - targetHeight) > .05 || !refs.image.style.height) refs.image.style.height = targetHeight + "px";
      refs.image.dataset.preferredAtomFontPixels = String(requested);
      refs.image.dataset.fittedAtomFontPixels = String(imageMetrics.font * scale);
    }

    function loadDiagram(currentRender) {
      mainImageStatus = "loading";
      imageMetrics = null;
      refs.image.classList.remove("is-ready");
      replaceChildren(refs.imageStatus, node("p", { text: "Η δομή φορτώνεται. Οι επιλογές θα ανοίξουν μόλις εμφανιστεί." }));
      const loadId = ++imageLoadId;
      refs.image.onload = function () {
        if (destroyed || currentRender !== renderId || loadId !== imageLoadId) return;
        if (!refs.image.naturalWidth) return diagramFailure(currentRender);
        mainImageStatus = "ready";
        refs.image.classList.add("is-ready");
        fitDiagramImage();
        replaceChildren(refs.imageStatus);
        updateControls();
      };
      refs.image.onerror = function () {
        if (!destroyed && loadId === imageLoadId) diagramFailure(currentRender);
      };
      refs.image.src = assetBase + round().asset;
      if (lessonPresentation) sourceDiagramMetrics(refs.image.src).then(function (metrics) {
        if (destroyed || currentRender !== renderId || loadId !== imageLoadId) return;
        imageMetrics = metrics;
        fitDiagramImage();
        if (viewport) viewport.refresh();
      });
      updateControls();
    }

    function diagramFailure(currentRender) {
      if (destroyed || currentRender !== renderId) return;
      mainImageStatus = "error";
      refs.image.classList.remove("is-ready");
      replaceChildren(refs.imageStatus,
        node("p", { text: "Η δομή δεν εμφανίστηκε. Για να επισκευάσεις το όνομα, χρειάζεται πρώτα να δεις το μόριο." }),
        button("Φόρτωσε ξανά τη δομή", "secondary", function () { loadDiagram(currentRender); })
      );
      updateControls();
    }

    function restoreFocus(id) {
      const control = Array.from(root.querySelectorAll("[id]")).find(function (entry) { return entry.id === id; });
      if (control && !control.disabled) control.focus({ preventScroll: true });
    }

    function updateControls(focusId) {
      const activeElement = document.activeElement;
      const restoreId = focusId || (root.contains(activeElement) ? activeElement.id : null);
      const data = round();
      const current = state();
      const enabled = diagramsReady() && !current.solved;
      const hasTarget = current.selectedPartId === data.targetPartId;
      replaceChildren(refs.parts);
      const partIds = data.kind === "order" ? current.order : data.parts.map(function (part) { return part.id; });
      partIds.forEach(function (id) {
        const part = data.parts.find(function (entry) { return entry.id === id; });
        const partButton = button(part.text, "part-button", function () { selectPart(id); }, {
          id: controlId("part-" + id), "aria-label": part.label + " — " + part.text,
          "aria-pressed": String(current.selectedPartId === id)
        });
        partButton.disabled = !enabled;
        if (data.kind === "replace" && current.selectedPartId === id && !hasTarget) partButton.classList.add("is-agreeing");
        refs.parts.append(partButton);
      });
      if (data.kind === "order") {
        const suffix = data.parts.find(function (part) { return part.id === data.suffixPartId; });
        refs.parts.append(node("span", { class: "fixed-suffix", "aria-label": "Η κύρια αλυσίδα μένει σταθερή", text: suffix.text }));
      }
      refs.choiceFieldset.hidden = data.kind !== "replace" || !hasTarget;
      replaceChildren(refs.choices);
      if (data.kind === "replace") {
        current.choiceOrder.forEach(function (index) {
          const choice = data.choices[index];
          const choiceButton = button(choice.label, "choice-button", function () {
            if (!diagramsReady() || current.solved) return;
            current.selectedValue = choice.value;
            current.submitted = false;
            clearFeedback();
            updateControls(controlId("choice-" + index));
            emitState();
            revealResponse("candidate", refs.candidate, refs.checkHelper);
          }, { id: controlId("choice-" + index), "aria-pressed": String(current.selectedValue === choice.value) });
          choiceButton.disabled = !enabled;
          refs.choices.append(choiceButton);
        });
      }
      replaceChildren(refs.orderControls);
      refs.orderControls.hidden = data.kind !== "order";
      if (data.kind === "order") {
        const selectedIndex = current.order.indexOf(current.selectedPartId);
        [-1, 1].forEach(function (direction) {
          const id = direction < 0 ? controlId("move-left") : controlId("move-right");
          const moveButton = button(direction < 0 ? "← Αριστερά" : "Δεξιά →", "secondary", function () {
            if (!diagramsReady() || current.solved) return;
            current.submitted = false;
            current.order = movePart(current.order, current.selectedPartId, direction);
            clearFeedback();
            updateControls(controlId("part-" + current.selectedPartId));
            refs.selectionStatus.textContent = "Ο κλάδος μετακινήθηκε. Δες την πρότασή σου και πάτησε Έλεγχος.";
            emitState();
            revealResponse("order-candidate", refs.orderControls, refs.checkHelper);
          }, { id: id, "aria-label": direction < 0 ? "Μετακίνησε τον επιλεγμένο κλάδο αριστερά" : "Μετακίνησε τον επιλεγμένο κλάδο δεξιά" });
          moveButton.disabled = !enabled || selectedIndex < 0 || selectedIndex + direction < 0 || selectedIndex + direction >= current.order.length;
          refs.orderControls.append(moveButton);
        });
      }
      refs.candidateName.textContent = candidateName(data, current);
      refs.candidate.hidden = data.kind === "replace" && current.selectedValue === null;
      const hasCandidate = data.kind === "order" || (hasTarget && current.selectedValue !== null);
      refs.checkButton.disabled = !enabled || !hasCandidate;
      refs.zoomButton.disabled = mainImageStatus !== "ready" || !!zoomPanel;
      const nextButtons = refs.next.querySelectorAll("button");
      nextButtons.forEach(function (nextButton) {
        nextButton.disabled = !diagramsReady() || !current.solved;
      });
      refs.checkHelper.textContent = current.solved ? "Η επισκευή ολοκληρώθηκε. Συνέχισε όταν είσαι έτοιμος ή έτοιμη." : !diagramsReady() ? "Περιμένουμε να εμφανιστούν οι δομές πριν από τον έλεγχο." : data.kind === "order" ? "Επιλέγεις κλάδο, πατάς ένα βέλος και ελέγχεις τη νέα σειρά." : hasCandidate ? "Ο έλεγχος μετρά ως μία προσπάθεια. Μπορείς να δοκιμάσεις ξανά." : "Διάλεξε πρώτα το κομμάτι και έπειτα μια αντικατάσταση.";
      refs.sessionStats.textContent = "Προσπάθειες σε αυτή την " + (data.guided ? "πρόβα " : "αποστολή ") + current.attempts;
      if (viewportEnabled) {
        refs.feedbackOpen.hidden = lessonPresentation || !current.submitted;
        refs.feedbackReturn.hidden = lessonPresentation || !current.submitted;
        refreshPagers();
      }
      if (restoreId) restoreFocus(restoreId);
      publishSuccessActionsReady();
    }

    function publishSuccessActionsReady() {
      const nextButtons = refs.next ? refs.next.querySelectorAll("button") : [];
      const actionsVisible = Array.from(nextButtons).some(function (control) { return !control.disabled && control.getClientRects().length > 0; });
      const stageVisible = !viewportEnabled || (lessonPresentation ? viewportStage === "edit" : viewportStage === "feedback") && actionsVisible;
      const ready = nextButtons.length > 0 && diagramsReady() && state().solved && stageVisible;
      if (!destroyed && ready !== lastSuccessActionsReady && typeof options.onSuccessActionsReady === "function") {
        lastSuccessActionsReady = ready;
        options.onSuccessActionsReady(ready);
      }
    }

    function selectPart(id) {
      if (!diagramsReady() || state().solved) return;
      const current = state();
      current.selectedPartId = id;
      current.submitted = false;
      clearFeedback();
      if (round().kind === "replace") {
        current.selectedValue = null;
        if (id !== round().targetPartId) {
          current.selectionMisses += 1;
          refs.selectionStatus.textContent = round().feedback.wrongPart;
        } else {
          refs.selectionStatus.textContent = "Αυτό το κομμάτι χρειάζεται επισκευή. Διάλεξε την αντικατάστασή του.";
        }
      } else {
        refs.selectionStatus.textContent = "Ο κλάδος επιλέχθηκε. Μετακίνησέ τον με τα κουμπιά Αριστερά και Δεξιά.";
      }
      if (viewportEnabled && round().kind === "replace") root.dataset.repairStep = id === round().targetPartId ? "choices" : "parts";
      updateControls(viewportEnabled && id === round().targetPartId ? controlId("choice-" + current.choiceOrder[0]) : controlId("part-" + id));
      emitState();
      if (viewportEnabled && round().kind === "replace" && id !== round().targetPartId) {
        replaceChildren(refs.feedback, node("p", { text: round().feedback.wrongPart })); showViewportFeedback(false);
      }
      if (round().kind === "order") revealResponse("order-controls", refs.selectionStatus, refs.orderControls);
      else if (id === round().targetPartId) revealResponse("replacement-options", refs.choiceFieldset);
      else revealResponse("selection-feedback", refs.selectionStatus);
    }

    function clearFeedback() {
      if (lessonPresentation) {
        refs.feedbackStage.hidden = true;
        root.classList.remove("repair-has-result", "repair-solved");
      } else if (viewportEnabled) setViewportStage("edit", "answer");
      refs.feedback.classList.remove("is-success");
      replaceChildren(refs.feedback);
      if (lessonPresentation) {
        refreshPagers();
        if (viewport) viewport.refresh();
        publishSuccessActionsReady();
      }
    }

    function showSuccess(result, fresh) {
      refs.feedback.classList.add("is-success");
      replaceChildren(refs.feedback,
        node("strong", { class: "success-title", text: "✓ Η επισκευή πέτυχε" }),
        node("span", { class: "success-name", text: round().correctName }),
        node("p", { class: "success-explanation", text: result.message })
      );
      if (viewportEnabled) pagers.push(global.NameleculeGameViewport.pager(refs.feedback.querySelector(".success-name"), { axis: "x", label: "Σωστό όνομα" }));
      const next = button(options.continueLabel || "Συνεχίζω τη θεωρία", "primary", function () {
        if (!diagramsReady() || !state().solved) return;
        if (typeof options.onContinue === "function") options.onContinue(getState());
      });
      next.setAttribute("data-checkpoint-continue", "");
      replaceChildren(refs.next, next);
      if (typeof options.onNewPractice === "function") {
        refs.next.classList.add("has-practice-action");
        refs.next.append(button(options.newPracticeLabel || "Άλλη τριάδα για εξάσκηση", "secondary", function () {
          if (destroyed || !diagramsReady() || !state().solved) return;
          options.onNewPractice(getState());
        }));
      }
      if (typeof options.onOtherGame === "function") {
        refs.next.classList.add("has-other-game-action");
        refs.next.append(button(options.otherGameLabel || "Άλλο παιχνίδι", "secondary", function () {
          if (destroyed || !diagramsReady() || !state().solved) return;
          options.onOtherGame(getState());
        }));
      }
      updateControls();
      if (viewportEnabled) showViewportFeedback(true);
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
        revealResponse("success", refs.feedback, refs.next);
      } else {
        replaceChildren(refs.feedback, node("p", { text: result.message }));
        updateControls(controlId("check-button"));
        emitState();
        if (viewportEnabled) showViewportFeedback(false);
        revealResponse("check-feedback", refs.feedback);
      }
    }

    function showDiagramZoom() {
      if (destroyed || mainImageStatus !== "ready" || zoomPanel) return;
      if (pageReveal) pageReveal.stop();
      const dialog = node(standalone && !viewportEnabled ? "dialog" : "section", { class: viewportEnabled ? "zoom-dialog repair-zoom-overlay" : "zoom-dialog", "aria-labelledby": controlId("zoom-title") });
      zoomPanel = dialog;
      const close = button("Κλείσιμο", "secondary", closeZoom);
      const image = node("img", { class: "zoom-image", alt: round().diagramAlt });
      const viewport = node("div", { class: "zoom-viewport", tabindex: "0", "aria-label": "Μεγεθυμένη δομή. Μετακινήσου μέσα στην εικόνα με αφή ή τα πλήκτρα βέλους." }, [image]);
      zoomImage = image;
      image.onerror = function () {
        if (destroyed || zoomPanel !== dialog) return;
        replaceChildren(viewport, node("p", { role: "status", text: "Η εικόνα δεν εμφανίστηκε. Κλείσε τη μεγέθυνση και δοκίμασε ξανά." }));
      };
      image.src = assetBase + round().asset;
      if (viewportEnabled) {
        let scale = 1;
        const zoomTools = node("div", { class: "repair-zoom-controls", role: "group", "aria-label": "Μέγεθος σχεδίου" });
        [-1, 1].forEach(function (direction) { zoomTools.append(button(direction < 0 ? "−" : "+", "secondary", function () {
          scale = Math.max(1, Math.min(4, scale + direction * .5)); image.style.width = (scale * 100) + "%"; image.style.height = (scale * 100) + "%"; image.style.maxWidth = "none";
        }, { "aria-label": direction < 0 ? "Σμίκρυνση σχεδίου" : "Μεγέθυνση σχεδίου" })); });
        refs.zoomTools = zoomTools;
      }
      dialog.append(
        node("div", { class: "zoom-heading" }, [node("h2", { id: controlId("zoom-title"), text: "Η δομή σε αρχικό μέγεθος" }), close]),
        node("p", { text: "Αν η εικόνα δεν χωρά, μετακινήσου μέσα στο πλαίσιο με αφή ή τα πλήκτρα βέλους." }),
        viewport
      );
      if (viewportEnabled) dialog.querySelector(".zoom-heading").insertBefore(refs.zoomTools, close);
      if (standalone && !viewportEnabled) {
        listen(dialog, "close", function () { finishZoom(dialog); });
        document.body.append(dialog);
        dialog.showModal();
      } else {
        dialog.setAttribute("role", viewportEnabled ? "dialog" : "region");
        if (viewportEnabled) { dialog.setAttribute("aria-modal", "true"); root.querySelector(".round-screen").inert = true; }
        listen(dialog, "keydown", function (event) {
          if (viewportEnabled && event.key === "Tab") {
            const targets = Array.from(dialog.querySelectorAll("button, [tabindex=\"0\"]"));
            const first = targets[0], last = targets[targets.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
          }
          if (event.key !== "Escape") return;
          event.preventDefault();
          event.stopPropagation();
          closeZoom();
        });
        root.append(dialog);
      }
      refs.zoomButton.setAttribute("aria-expanded", "true");
      refs.zoomButton.disabled = true;
      close.focus();
    }

    function finishZoom(panel) {
      if (destroyed || zoomPanel !== panel) return;
      if (zoomImage) zoomImage.onerror = null;
      zoomImage = null;
      replaceChildren(panel);
      panel.remove();
      zoomPanel = null;
      if (viewportEnabled) root.querySelector(".round-screen").inert = false;
      refs.zoomButton.setAttribute("aria-expanded", "false");
      refs.zoomButton.disabled = mainImageStatus !== "ready";
      refs.zoomButton.focus({ preventScroll: true });
    }

    function closeZoom() {
      if (!zoomPanel) return;
      // Native close is queued; restore controls only when that panel finishes.
      if (standalone && !viewportEnabled) zoomPanel.close();
      else finishZoom(zoomPanel);
    }

    renderRound();
    return api;
  }

  global.NameleculeRepairGame = {
    mountRound: function (host, options) { return createRoundView(host, options, false); },
    presentationForRound: presentationForRound,
    createResponseRevealer: createResponseRevealer
  };
  if (typeof document === "undefined") return;

  const root = document.getElementById("game-root");
  if (!root) return;
  let game = null;
  let activeSet = null;
  let roundIndex = 0;
  let states = [];
  let activeRound = null;
  let pageViewport = null;
  let pagePagers = [];
  let renderId = 0;
  const entryParams = new URLSearchParams(window.location.search);
  const enginePilot = entryParams.get("source") !== "authored";
  const legacyPilotStorageKey = "namelecule-repair-engine-pilot-v1";
  const enrichedPilotStorageKey = "namelecule-repair-engine-pool-v2";
  const levelPilotStoragePrefix = "namelecule-repair-levels-v1-";
  const levelPilotCurrentKey = levelPilotStoragePrefix + "current";
  let pilotStorageKey = enrichedPilotStorageKey;
  let levelControls = null;
  let pilot = null;
  let pilotPhase = "hub";
  let loadToken = 0;
  let loadAbort = null;

  function newSeed() {
    const values = new Uint32Array(1);
    window.crypto.getRandomValues(values);
    return String(values[0]);
  }

  function loadPilotScript(path) {
    return new Promise(function (resolve, reject) {
      const script = document.createElement("script");
      script.src = new URL(path, document.baseURI).href;
      script.onload = resolve;
      script.onerror = function () { script.remove(); reject(new Error("Pilot script could not load")); };
      document.head.append(script);
    });
  }

  function readPilotProgress(key = pilotStorageKey) {
    try { return JSON.parse(window.sessionStorage.getItem(key)); }
    catch (_) { return null; }
  }

  function savePilotProgress() {
    if (!pilot) return;
    const record = {
      version: 1, generatorVersion: global.NameleculeRepairGenerator.version,
      catalogRevision: pilot.catalog.revision, engineSHA256: pilot.catalog.engineSHA256,
      seed: pilot.seed, difficulty: pilot.difficulty, phase: pilotPhase,
      setId: activeSet && activeSet.id, roundIndex: roundIndex, states: states
    };
    if (pilot.levelMode) {
      if (!pilot.level) return;
      Object.assign(record, { version: 2, policyVersion: global.NameleculeGameLevels.policyVersion, level: pilot.level,
        sourceSHA256: pilot.view.sourceSHA256, viewRevision: pilot.view.viewRevision,
        context: global.NameleculeGameLevels.makeContext({ source: "enriched", level: pilot.level, seed: pilot.seed }) });
    }
    try {
      window.sessionStorage.setItem(pilotStorageKey, JSON.stringify(record));
      if (pilot.levelMode) window.sessionStorage.setItem(levelPilotCurrentKey, String(pilot.level));
    }
    catch (_) { pilot.storageAvailable = false; }
  }

  function generatePilotGame(seed) {
    pilot.seed = global.NameleculeRepairGenerator.normalizeSeed(seed);
    const input = pilot.levelMode ? global.NameleculeGameLevels.createGenerationInput({ catalog: pilot.catalog, analyses: pilot.analyses }, pilot.level) : pilot;
    pilot.view = pilot.levelMode ? input : null;
    game = validateGameData(global.NameleculeRepairGenerator.createGame(input.catalog, input.analyses, {
      seed: pilot.seed, difficulty: pilot.difficulty
    }));
    if (pilot.levelMode) {
      const setId = pilot.level === 1 ? "alkanes-unbranched" : "alkanes-branched";
      game.sets = game.sets.filter(function (set) { return set.id === setId; });
      const set = game.sets[0];
      assert(set && set.rounds.every(function (entry) { return global.NameleculeGameLevels.levelFor(entry.moleculeId) === pilot.level; }), "Incompatible level assignment");
      set.title = global.NameleculeGameLevels.label(pilot.level);
    }
  }

  function restorePilotProgress(record) {
    if (!record || record.version !== (pilot.levelMode ? 2 : 1) || record.generatorVersion !== global.NameleculeRepairGenerator.version ||
        record.catalogRevision !== pilot.catalog.revision || record.engineSHA256 !== pilot.catalog.engineSHA256 ||
        !["basic", "challenge"].includes(record.difficulty) || typeof record.seed !== "string") return false;
    if (!pilot.levelMode && Object.prototype.hasOwnProperty.call(record, "context")) return false;
    try { global.NameleculeRepairGenerator.normalizeSeed(record.seed); }
    catch (_) { return false; }
    if (pilot.levelMode) {
      if (record.policyVersion !== global.NameleculeGameLevels.policyVersion || ![1, 2, 3].includes(record.level) || record.difficulty !== "basic") return false;
      let context;
      try { context = global.NameleculeGameLevels.validateContext(record.context); } catch (_) { return false; }
      if (context.source !== "enriched" || context.level !== record.level || context.seed !== record.seed) return false;
      const view = global.NameleculeGameLevels.createGenerationInput({ catalog: pilot.catalog, analyses: pilot.analyses }, record.level);
      if (record.sourceSHA256 !== view.sourceSHA256 || record.viewRevision !== view.viewRevision) return false;
      pilot.level = record.level;
    }
    pilot.difficulty = record.difficulty;
    generatePilotGame(record.seed);
    if (["hub", "picker"].includes(record.phase)) { pilotPhase = record.phase; return true; }
    const set = game.sets.find(function (entry) { return entry.id === record.setId; });
    if (!set || !["round", "results"].includes(record.phase) || !Number.isInteger(record.roundIndex) ||
        record.roundIndex < 0 || record.roundIndex >= set.rounds.length ||
        !Array.isArray(record.states) || record.states.length !== set.rounds.length) return false;
    const restored = set.rounds.map(function (entry, i) { return restoreRoundState(entry, record.states[i]); });
    // Refresh cannot bypass an unsolved preceding round or manufacture results.
    if (restored.slice(0, record.roundIndex).some(function (entry) { return !entry.solved; }) ||
        (record.phase === "results" && restored.some(function (entry) { return !entry.solved; }))) return false;
    activeSet = set;
    states = restored;
    roundIndex = record.roundIndex;
    pilotPhase = record.phase;
    return true;
  }

  async function preparePilot(signal) {
    if (!global.NameleculeChemistryClient) await loadPilotScript("../js/namelecule-chemistry-client.js?v=verified-engines-20261105-r1");
    if (!global.NameleculeRepairGenerator) await loadPilotScript("../js/namelecule-repair-generator.js?v=engine-pilot-20261105-r2");
    if (!global.NameleculeGeneratedRepairCheckpoint) await loadPilotScript("../js/namelecule-generated-repair-checkpoint.js?v=game-viewport-20261116-r1");
    const provider = global.NameleculeGeneratedRepairCheckpoint;
    // v1 source identity belongs to the recorded standalone attempt (8 OR 14).
    // A normal new entry opens the structural level picker with full14 input.
    const requested = entryParams.get("catalog");
    const requestedDescriptor = requested ? provider.catalogDescriptor(requested) : null;
    const explicitOld = requestedDescriptor && ["legacy", "enriched"].includes(requestedDescriptor.id);
    const oldKey = explicitOld && requestedDescriptor.id === "legacy" ? legacyPilotStorageKey : enrichedPilotStorageKey;
    let descriptor = explicitOld ? requestedDescriptor : provider.catalogDescriptor("enriched");
    let input = await provider.loadCanonicalInput(signal, descriptor);
    if (signal.aborted) throw new DOMException("Cancelled", "AbortError");
    pilot = { catalog: input.catalog, analyses: input.analyses, seed: newSeed(), difficulty: "basic", storageAvailable: true, levelMode: !explicitOld, level: null };
    pilotStorageKey = oldKey;
    if (explicitOld && restorePilotProgress(readPilotProgress(oldKey)) && ["round", "results"].includes(pilotPhase)) {
      activeSet.title = "Προηγούμενη προσπάθεια · " + activeSet.title;
      return;
    }
    if (explicitOld) {
      descriptor = provider.catalogDescriptor("enriched");
      input = await provider.loadCanonicalInput(signal, descriptor);
      if (signal.aborted) throw new DOMException("Cancelled", "AbortError");
      pilot = { catalog: input.catalog, analyses: input.analyses, seed: newSeed(), difficulty: "basic", storageAvailable: true, levelMode: true, level: null };
    }
    if (!global.NameleculeGameLevels) throw new Error("Game levels module unavailable");
    let current = null;
    try { current = Number(window.sessionStorage.getItem(levelPilotCurrentKey)); } catch (_) { /* Storage is optional. */ }
    if ([1, 2, 3].includes(current)) {
      pilotStorageKey = levelPilotStoragePrefix + current;
      const previous = readPilotProgress();
      if (previous?.level === current && restorePilotProgress(previous) && ["round", "results"].includes(pilotPhase)) return;
    }
    activeSet = null; states = []; roundIndex = 0; pilotPhase = "hub"; pilot.level = null;
    game = null;
  }

  function startLevel(level) {
    if (!pilot?.levelMode || ![1, 2, 3].includes(level)) return;
    pilot.level = level; pilot.difficulty = "basic";
    pilotStorageKey = levelPilotStoragePrefix + level;
    activeSet = null; states = []; roundIndex = 0;
    const previous = readPilotProgress();
    if (previous?.level === level && restorePilotProgress(previous) && ["round", "results"].includes(pilotPhase)) {
      if (pilotPhase === "results") renderResults(); else renderRound();
      return;
    }
    startSet(level === 1 ? "alkanes-unbranched" : "alkanes-branched");
  }

  function renderLevelPicker() {
    pilotPhase = "picker"; renderId += 1;
    const host = node("div");
    const content = node("div", { class: "workshop-hub workshop-set-picker" }, [
      node("section", { class: "workshop-hero" }, [
        node("p", { class: "eyebrow", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" }),
        node("h1", { text: "Αλκάνια · Διάλεξε επίπεδο" }),
        node("p", { text: "Η εφαρμογή αναθέτει τρία διαφορετικά μόρια του επιπέδου. Κάθε όνομα έχει ένα λάθος· δίνεται αρχική καθοδήγηση." })
      ]), host
    ]);
    [ ["legacy", legacyPilotStorageKey], ["enriched", enrichedPilotStorageKey] ].forEach(function (entry) {
      const previous = readPilotProgress(entry[1]);
      const descriptor = global.NameleculeGeneratedRepairCheckpoint.catalogDescriptor(entry[0]);
      if (previous?.version === 1 && previous.generatorVersion === global.NameleculeRepairGenerator.version &&
          previous.catalogRevision === descriptor.revision && previous.engineSHA256 === descriptor.engineSHA256 && ["round", "results"].includes(previous.phase)) {
        content.append(node("p", { class: "pilot-entry" }, [node("a", { href: "name-repair.html?catalog=" + entry[0], text: "Προηγούμενη προσπάθεια (" + (entry[0] === "legacy" ? "8" : "14") + " μόρια)" })]));
      }
    });
    replaceRoot(content);
    levelControls = global.NameleculeGameLevels.mount(host, { availableIds: pilot.catalog.molecules.map(function (m) { return m.id; }),
      selectedLevel: null, allowedLevels: [1, 2, 3], onSelect: function (choice) { if (choice.level) startLevel(choice.level); } });
  }

  function pilotSettings() {
    const select = node("select", { id: "pilot-difficulty" }, [
      node("option", { value: "basic", text: "Βασικό" }), node("option", { value: "challenge", text: "Πρόκληση" })
    ]);
    select.value = pilot.difficulty;
    select.addEventListener("change", function () {
      pilot.difficulty = select.value;
      generatePilotGame(newSeed());
      renderSetPicker();
      document.getElementById("pilot-difficulty").focus();
    });
    return node("div", { class: "pilot-settings" }, [
      node("label", { for: "pilot-difficulty", text: "Καθοδήγηση" }), select,
      node("p", { text: "Στο Βασικό δίνεται μια αρχική κατεύθυνση. Στην Πρόκληση εντοπίζεις και τον κανόνα που χρειάζεται." }),
      node("p", { class: "muted", text: "Σε κάθε νέα προσπάθεια επιλέγονται τυχαία επισκευές από τα " + pilot.catalog.molecules.length + " διαθέσιμα αλκάνια." })
    ]);
  }

  function redirectLegacyAttempt() {
    if (!pilot || pilot.levelMode) return false;
    location.assign(new URL("name-repair.html?pickSet=1", location.href).href);
    return true;
  }

  function startSet(setId) {
    if (redirectLegacyAttempt(setId)) return;
    if (pilot) generatePilotGame(newSeed());
    activeSet = game.sets.find(function (entry) { return entry.id === setId; });
    assert(activeSet, "No compatible level set");
    roundIndex = 0;
    states = activeSet.rounds.map(function (entry) {
      const initial = createRoundState(entry);
      // The generator already shuffled choices using the recorded seed.
      if (pilot && entry.kind === "replace") initial.choiceOrder = entry.choices.map(function (_, i) { return i; });
      return initial;
    });
    renderRound();
  }

  window.addEventListener("pagehide", function () { if (loadAbort) loadAbort.abort(); });
  window.addEventListener("pageshow", function (event) {
    if (event.persisted && root.getAttribute("aria-busy") === "true") loadGame();
  });

  function focusHeading() {
    const heading = root.querySelector("h1");
    if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
    if (!global.NameleculeGameViewport) window.scrollTo({ top: 0, behavior: "instant" });
  }

  function clearPageViewport() {
    if (pageViewport) { pageViewport.destroy(); pageViewport = null; }
    pagePagers.forEach(function (pager) { pager.destroy(); }); pagePagers = [];
  }

  function replaceRoot(content) {
    clearPageViewport();
    if (activeRound) { activeRound.destroy(); activeRound = null; }
    if (levelControls) { levelControls.destroy(); levelControls = null; }
    root.replaceChildren(content);
    if (global.NameleculeGameViewport) {
      content.querySelectorAll(".result-name").forEach(function (name) { pagePagers.push(global.NameleculeGameViewport.pager(name, { axis: "x", label: "Ολοκληρωμένο όνομα" })); });
      pagePagers.push(global.NameleculeGameViewport.pager(content, { axis: "y", label: "Επιλογή και αποτελέσματα Συνεργείου" }));
      pageViewport = global.NameleculeGameViewport.mount(root, { kind: "repair-entry", onResize: function () { pagePagers.forEach(function (pager) { pager.refresh(); }); } });
    }
    root.setAttribute("aria-busy", "false");
  }

  async function loadGame() {
    const token = ++loadToken;
    if (loadAbort) loadAbort.abort();
    loadAbort = new AbortController();
    root.setAttribute("aria-busy", "true");
    const loading = node("section", { class: "loading-card" }, [
      node("span", { class: "loading-mark", "aria-hidden": "true", text: "C" }),
      node("p", { class: "eyebrow", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" }),
      node("h1", { text: "Ετοιμάζουμε τον πάγκο σου" }),
      node("p", { role: "status", text: "Οι δομές και οι αποστολές φορτώνονται." })
    ]);
    root.replaceChildren(loading);
    try {
      if (enginePilot) await preparePilot(loadAbort.signal);
      else {
        const response = await fetch("./data/name-repair-alkanes.json", { cache: "no-cache", signal: loadAbort.signal });
        if (!response.ok) throw new Error("Game data HTTP " + response.status);
        game = validateGameData(await response.json());
        states = []; activeSet = null;
      }
      if (token !== loadToken) return;
      root.setAttribute("aria-busy", "false");
      const requestedSet = entryParams.get("startSet");
      const hasStartCommand = entryParams.has("startSet"), hasPickerCommand = entryParams.has("pickSet");
      const pickerCommand = entryParams.get("pickSet");
      if (hasStartCommand || hasPickerCommand) {
        entryParams.delete("startSet"); entryParams.delete("pickSet");
        const url = new URL(location.href); url.searchParams.delete("startSet"); url.searchParams.delete("pickSet");
        history.replaceState(null, "", url.href);
      }
      if (pilot && hasPickerCommand && !hasStartCommand && pickerCommand === "1") {
        activeSet = null; states = []; roundIndex = 0;
        renderSetPicker(); focusHeading();
      } else if (pilot && !pilot.levelMode && hasStartCommand && !hasPickerCommand && ["alkanes-unbranched", "alkanes-branched"].includes(requestedSet)) {
        startSet(requestedSet);
      } else if (pilot && pilotPhase === "round") renderRound();
      else if (pilot && pilotPhase === "results") renderResults();
      else if (pilot && pilotPhase === "picker") renderSetPicker();
      else renderWelcome();
    } catch (error) {
      if (token !== loadToken || error.name === "AbortError") return;
      console.error("Namelecule game could not load", error);
      replaceRoot(node("section", { class: "loading-card" }, [
        node("span", { class: "loading-mark", "aria-hidden": "true", text: "?" }),
        node("p", { class: "eyebrow", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" }),
        node("h1", { text: "Ο πάγκος δεν άνοιξε ακόμη" }),
        node("p", { role: "status", text: "Δεν φορτώθηκαν οι αποστολές. Δοκίμασε ξανά ή επέστρεψε στην αρχική σελίδα από την Έξοδο." }),
        button("Δοκίμασε ξανά", "primary", loadGame),
        node("a", { class: "secondary", href: "name-repair.html?source=authored", text: "Άνοιξε τα αρχικά σετ" })
      ]));
    }
  }

  function renderWelcome() {
    if (pilot?.levelMode) return renderLevelPicker();
    pilotPhase = "hub";
    renderId += 1;
    const hero = node("section", { class: "workshop-hero", "aria-label": "Καλώς ήρθες στο Συνεργείο ονομάτων" }, [
      node("p", { class: "eyebrow", text: "ΠΑΙΧΝΙΔΙΑ ΟΝΟΜΑΤΟΛΟΓΙΑΣ" }),
      node("div", { class: "workshop-title" }, [workshopLogo("workshop-logo"), node("h1", {}, ["Συνεργείο", node("span", { text: "ονομάτων" })])]),
      node("p", { class: "workshop-description", text: "Διάλεξε μια κατηγορία και έπειτα ένα σύντομο σετ. Παρατήρησε κάθε δομή, επισκεύασε το όνομα και δες την εξήγηση μετά από κάθε σωστή απάντηση." })
    ]);
    const start = button("Δες τα σετ →", "primary workshop-set-start intro-start", function () {
      renderSetPicker();
      focusHeading();
    }, { id: "set-alkanes-start" });
    const card = node("article", { class: "workshop-set-card", "aria-labelledby": "set-alkanes-title" }, [
      node("span", { class: "workshop-set-kind", text: "ΣΕΤ ΑΠΟΣΤΟΛΩΝ" }),
      node("h3", { id: "set-alkanes-title", text: "Αλκάνια" }),
      node("p", { text: "Δύο σύντομα σετ για να συνδέσεις τη δομή των αλκανίων με τα κομμάτια του ονόματος." }),
      node("div", { class: "workshop-set-meta" }, [node("span", { text: "2 σετ" }), node("span", { text: "3 κουίζ ανά σετ" })]),
      node("ul", { class: "workshop-set-topics" }, ["Χωρίς διακλαδώσεις", "Με διακλαδώσεις"].map(function (text) { return node("li", { text: text }); })),
      start
    ]);
    const sets = node("section", { class: "workshop-sets", "aria-labelledby": "workshop-sets-title" }, [
      node("h2", { id: "workshop-sets-title", text: "Διάλεξε κατηγορία" }),
      node("div", { class: "workshop-set-grid" }, [card])
    ]);
    const steps = [
      ["Δες τη δομή", "Σύνδεσε τα άτομα C και τις αλκυλομάδες με το όνομα."],
      ["Βρες τι χρειάζεται αλλαγή", "Διάλεξε κομμάτι και αντικατάσταση ή άλλαξε τη σειρά."],
      ["Έλεγξε και ξαναδοκίμασε", "Μετά τη σωστή επισκευή, δες γιατί το όνομα ταιριάζει στη δομή."]
    ];
    const welcome = node("div", { class: "workshop-hub" }, [
      hero,
      node("p", { class: "pilot-entry" }, [node("a", {
        href: enginePilot ? "name-repair.html?source=authored" : "name-repair.html",
        text: enginePilot ? "Άνοιξε τα αρχικά επιμελημένα σετ" : "Νέες ερωτήσεις από τη μηχανή →"
      })]),
      sets,
      node("section", { class: "intro-how", "aria-label": "Πώς παίζεται" }, steps.map(function (step, index) {
        return node("div", { class: "how-item" }, [node("span", { class: "how-number", "aria-hidden": "true", text: String(index + 1) }), node("div", {}, [node("h2", { text: step[0] }), node("p", { text: step[1] })])]);
      }))
    ]);
    if (enginePilot && pilot.catalog.revision !== global.NameleculeGeneratedRepairCheckpoint.catalogDescriptor("legacy").revision) {
      const old = readPilotProgress(legacyPilotStorageKey);
      if (old && old.version === 1 && old.generatorVersion === global.NameleculeRepairGenerator.version &&
          old.engineSHA256 === global.NameleculeGeneratedRepairCheckpoint.catalogDescriptor("legacy").engineSHA256 &&
          old.catalogRevision === global.NameleculeGeneratedRepairCheckpoint.catalogDescriptor("legacy").revision &&
          ["round", "results"].includes(old.phase)) {
        welcome.append(node("p", { class: "pilot-entry" }, [node("a", { href: "name-repair.html?source=engine&catalog=legacy", text: "Συνέχισε την προηγούμενη εξάσκηση" })]));
      }
    }
    replaceRoot(welcome);
    savePilotProgress();
  }

  function renderSetPicker() {
    if (pilot?.levelMode) return renderLevelPicker();
    if (redirectLegacyAttempt()) return;
    pilotPhase = "picker";
    renderId += 1;
    const cards = game.sets.map(function (set) {
      const titleId = "set-" + set.id + "-title";
      return node("article", { class: "workshop-set-card", "aria-labelledby": titleId }, [
        node("span", { class: "workshop-set-kind", text: "ΣΕΤ ΑΠΟΣΤΟΛΩΝ" }),
        node("h3", { id: titleId, text: set.title }),
        node("p", { text: set.description }),
        node("div", { class: "workshop-set-meta" }, [node("span", { text: "3 κουίζ" }), node("span", { text: "Χωρίς χρονόμετρο" })]),
        node("ul", { class: "workshop-set-topics" }, set.topics.map(function (text) { return node("li", { text: text }); })),
        button("Ξεκίνα το σετ →", "primary workshop-set-start", function () {
          startSet(set.id);
        }, { id: "set-" + set.id + "-start" })
      ]);
    });
    replaceRoot(node("div", { class: "workshop-hub workshop-set-picker" }, [
      node("section", { class: "workshop-hero" }, [
        button("Όλα τα σετ", "secondary workshop-all-sets", function () { renderWelcome(); focusHeading(); }, { id: "workshop-all-sets" }),
        node("p", { class: "eyebrow workshop-brand" }, [
          workshopLogo("workshop-logo-small"),
          node("span", { class: "workshop-brand-label", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" })
        ]),
        node("h1", { text: "Αλκάνια" }),
        node("p", { class: "workshop-description", text: "Διάλεξε αλκάνια χωρίς ή με διακλαδώσεις. Κάθε σετ έχει τρία σύντομα κουίζ." })
      ]),
      ...(pilot ? [pilotSettings()] : []),
      node("section", { class: "workshop-sets", "aria-labelledby": "alkane-sets-title" }, [
        node("h2", { id: "alkane-sets-title", text: "Διάλεξε σετ" }),
        node("div", { class: "workshop-set-grid" }, cards)
      ])
    ]));
    savePilotProgress();
  }

  function progressList() {
    return node("p", { class: "progress round-progress-counter", role: "status", "aria-live": "polite",
      "aria-atomic": "true", "aria-label": "Κουίζ " + (roundIndex + 1) + " από " + activeSet.rounds.length,
      text: "Κουίζ " + (roundIndex + 1) + "/" + activeSet.rounds.length });
  }

  function round() { return activeSet.rounds[roundIndex]; }
  function state() { return states[roundIndex]; }
  function renderRound() {
    clearPageViewport();
    pilotPhase = "round";
    if (activeRound) activeRound.destroy();
    if (levelControls) { levelControls.destroy(); levelControls = null; }
    const index = roundIndex;
    const presentation = presentationForRound(round(), { difficulty: pilot ? pilot.difficulty : "basic" });
    activeRound = createRoundView(root, Object.assign({}, presentation, {
      initialState: state(), assetBase: "", progressList: progressList, setTitle: activeSet.title, viewport: !!global.NameleculeGameViewport,
      requestRestart: requestRestart,
      continueLabel: index === activeSet.rounds.length - 1 ? "Δες τις επισκευές σου  →" : "Επόμενο κουίζ  →",
      onStateChange: function (current) { states[index] = current; savePilotProgress(); },
      onContinue: function () {
        if (index === activeSet.rounds.length - 1) renderResults();
        else { roundIndex += 1; renderRound(); }
      }
    }), true);
    if (pilot && !pilot.storageAvailable) root.append(node("p", { role: "status", class: "pilot-entry", text: "Ο browser δεν επιτρέπει αποθήκευση της προσπάθειας. Κράτησε αυτή τη σελίδα ανοιχτή μέχρι να τελειώσεις." }));
    savePilotProgress();
  }

  function requestRestart() {
    const hasProgress = roundIndex > 0 || states.some(function (entry) { return entry.attempts > 0 || entry.selectionMisses > 0 || entry.selectedPartId; });
    if (!hasProgress) return restartGame();
    const dialog = node("dialog", { class: "confirm-dialog", "aria-labelledby": "restart-title" }, [
      node("h2", { id: "restart-title", text: "Επιστροφή στα σετ;" }),
      node("p", { text: pilot?.levelMode ? "Η πρόοδος σε αυτό το επίπεδο θα μείνει διαθέσιμη όταν το επιλέξεις ξανά." : "Οι επισκευές και οι προσπάθειες αυτού του σετ θα μηδενιστούν." })
    ]);
    const keep = button("Συνέχισε εδώ", "secondary", function () { dialog.close(); });
    const restart = button("Επιστροφή στα σετ", "primary", function () { dialog.close(); restartGame(); });
    dialog.append(node("div", { class: "confirm-actions" }, [keep, restart]));
    dialog.addEventListener("close", function () { dialog.remove(); });
    document.body.append(dialog);
    dialog.showModal();
    keep.focus();
  }

  function restartGame() {
    if (redirectLegacyAttempt()) return;
    if (pilot?.levelMode) { try { window.sessionStorage.removeItem(levelPilotCurrentKey); } catch (_) { pilot.storageAvailable = false; } }
    roundIndex = 0;
    states = [];
    activeSet = null;
    renderSetPicker();
    focusHeading();
  }

  function renderResults() {
    pilotPhase = "results";
    renderId += 1;
    const summary = summarizeGame(activeSet.rounds, states);
    const stats = [
      [summary.completed, "Κουίζ που ολοκληρώθηκαν"],
      [summary.attempts, "Προσπάθειες ελέγχου"]
    ];
    const challenges = activeSet.rounds.map(function (data, index) { return { data: data, state: states[index] }; }).filter(function (entry) { return !entry.data.guided; });
    const content = node("section", { class: "results" }, [
      node("div", { class: "results-hero" }, [
        node("span", { class: "results-seal", "aria-hidden": "true", text: "✓" }),
        node("p", { class: "eyebrow", text: "Ο ΠΑΓΚΟΣ ΤΑΚΤΟΠΟΙΗΘΗΚΕ" }),
        node("p", { class: "results-set-name", text: "Αλκάνια · " + activeSet.title }),
        node("h1", { text: summary.total + " ονόματα στη θέση τους" }),
        node("p", { role: "status", text: "Ολοκλήρωσες και τα " + summary.total + " κουίζ του σετ. Κράτησε τη σύνδεση ανάμεσα στη δομή και τα κομμάτια κάθε ονόματος." })
      ]),
      node("div", { class: "results-stats", "aria-label": "Οι επισκευές σου" }, stats.map(function (stat) {
        return node("div", { class: "stat-card" }, [node("span", { class: "stat-number", text: String(stat[0]) }), node("span", { class: "stat-label", text: stat[1] })]);
      })),
      node("section", { class: "results-detail", "aria-labelledby": "results-detail-title" }, [
        node("h2", { id: "results-detail-title", text: "Οι επισκευές του παιχνιδιού σου" }),
        node("ol", { class: "results-list" }, challenges.map(function (entry) {
          return node("li", { class: "result-item" }, [
            node("span", { class: "result-check", "aria-hidden": "true", text: "✓" }),
            node("div", {}, [node("strong", { class: "result-name", text: entry.data.correctName }), node("span", { class: "result-objective", text: entry.data.title })])
          ]);
        }))
      ]),
      node("p", { class: "results-note", text: "Οι προσπάθειες ελέγχου περιλαμβάνουν τις επαναλήψεις κάθε κουίζ." }),
      node("div", { class: "results-actions" }, [...(pilot?.levelMode ? [button("Νέα τριάδα στο ίδιο επίπεδο", "secondary", function () { startSet(pilot.level === 1 ? "alkanes-unbranched" : "alkanes-branched"); })] : []), button("Επιστροφή στα σετ", "primary", restartGame), node("a", { class: "secondary", href: "../design/welcome-proposal.html", text: "Επιστροφή στην αρχική" })])
    ]);
    replaceRoot(content);
    focusHeading();
    savePilotProgress();
  }

  loadGame();
})(typeof globalThis !== "undefined" ? globalThis : this);
