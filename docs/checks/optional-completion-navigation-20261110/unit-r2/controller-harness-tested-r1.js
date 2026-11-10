const global=globalThis;global.window=global;
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

  function createRoundView(host, options, standalone) {
    assert(host && typeof host.replaceChildren === "function", "A round host is required");
    assert(options && typeof options === "object", "Round options are required");
    const data = validateRoundData(options.round);
    const emphasizeObjective = options.emphasizeObjective === true;
    const condensedDiagram = options.diagramRepresentation === "condensed";
    const compactDiagramZoom = options.compactDiagramZoom === true;
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
    let zoomPanel = null;
    let zoomImage = null;
    let listeners = [];
    const ownedClass = !host.classList.contains("nl-repair-round");
    if (ownedClass) host.classList.add("nl-repair-round");
    const pageScroller = function () { return global.document.scrollingElement || global.document.documentElement; };
    const pageReveal = standalone ? createResponseRevealer({
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
      if (destroyed) return;
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

    function renderRound() {
      const currentRender = ++renderId;
      mainImageStatus = "loading";
      const data = round();
      refs = {};
      const heading = node("div", { class: "round-heading" });
      if (data.guided) heading.append(node("span", { class: "guided-pill", text: "Πρώτα δοκιμάζουμε μαζί" }));
      if (standalone && options.setTitle) heading.append(node("p", { class: "round-set-name", text: "Αλκάνια · " + options.setTitle }));
      heading.append(node("h1", { text: data.title }), node("p", {
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
        node("div", { class: "broken-name", text: broken }),
        node("h2", { class: "step-heading", text: data.kind === "order" ? "1. Βάλε τους κλάδους στη σειρά" : "1. Ποιο κομμάτι θα αλλάξεις;" }),
        node("p", { class: "step-description", text: data.kind === "order" ? "Διάλεξε έναν κλάδο και μετακίνησέ τον με τα βέλη. Η κύρια αλυσίδα μένει στο τέλος." : "Πάτησε το κομμάτι που δεν ταιριάζει με τη δομή." }),
        refs.parts, refs.selectionStatus, refs.orderControls, refs.choiceFieldset, refs.candidate,
        node("div", { class: "repair-actions" }, [refs.checkButton]),
        refs.checkHelper, refs.feedback
      ]);
      refs.sessionStats = node("span");
      const screen = node("div", { class: "round-screen" }, [
        node("div", { class: "round-topbar" }, [node("p", { class: "eyebrow round-game-brand" }, [workshopLogo("workshop-logo-small", assetBase), node("span", { class: "round-game-label", text: "ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ" })])].concat(standalone ? [options.progressList()] : [])),
        heading, steps,
        node("div", { class: "bench" }, [node("div", { class: "visual-side" }, [diagram]), node("div", { class: "repair-side" }, [repair, refs.next])]),
        node("div", { class: "session-row" }, [refs.sessionStats].concat(standalone ? [button("Επιστροφή στα σετ", "quiet", options.requestRestart)] : []))
      ]);
      root.replaceChildren(screen);
      root.setAttribute("aria-busy", "false");
      loadDiagram(currentRender);
      updateControls();
      const title = heading.querySelector("h1");
      title.tabIndex = -1;
      title.focus({ preventScroll: true });
      if (standalone) window.scrollTo({ top: 0, behavior: "instant" });
      if (state().solved) showSuccess(evaluateRepair(data, state()), false);
      else if (state().submitted) {
        const result = evaluateRepair(data, state());
        if (result.message) replaceChildren(refs.feedback, node("p", { text: result.message }));
      }
      if (data.kind === "replace" && state().selectedPartId && state().selectedPartId !== data.targetPartId) {
        refs.selectionStatus.textContent = data.feedback.wrongPart;
      }
    }

    function loadDiagram(currentRender) {
      mainImageStatus = "loading";
      refs.image.classList.remove("is-ready");
      replaceChildren(refs.imageStatus, node("p", { text: "Η δομή φορτώνεται. Οι επιλογές θα ανοίξουν μόλις εμφανιστεί." }));
      const loadId = ++imageLoadId;
      refs.image.onload = function () {
        if (destroyed || currentRender !== renderId || loadId !== imageLoadId) return;
        if (!refs.image.naturalWidth) return diagramFailure(currentRender);
        mainImageStatus = "ready";
        refs.image.classList.add("is-ready");
        replaceChildren(refs.imageStatus);
        updateControls();
      };
      refs.image.onerror = function () {
        if (!destroyed && loadId === imageLoadId) diagramFailure(currentRender);
      };
      refs.image.src = assetBase + round().asset;
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
      if (restoreId) restoreFocus(restoreId);
      const successActionsReady = nextButtons.length > 0 && diagramsReady() && current.solved;
      if (!destroyed && successActionsReady !== lastSuccessActionsReady && typeof options.onSuccessActionsReady === "function") {
        lastSuccessActionsReady = successActionsReady;
        options.onSuccessActionsReady(successActionsReady);
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
      updateControls(controlId("part-" + id));
      emitState();
      if (round().kind === "order") revealResponse("order-controls", refs.selectionStatus, refs.orderControls);
      else if (id === round().targetPartId) revealResponse("replacement-options", refs.choiceFieldset);
      else revealResponse("selection-feedback", refs.selectionStatus);
    }

    function clearFeedback() {
      refs.feedback.classList.remove("is-success");
      replaceChildren(refs.feedback);
    }

    function showSuccess(result, fresh) {
      refs.feedback.classList.add("is-success");
      replaceChildren(refs.feedback,
        node("strong", { class: "success-title", text: "✓ Η επισκευή πέτυχε" }),
        node("span", { class: "success-name", text: round().correctName }),
        node("p", { class: "success-explanation", text: result.message })
      );
      const next = button(options.continueLabel || "Συνεχίζω τη θεωρία", "primary", function () {
        if (!diagramsReady() || !state().solved) return;
        if (typeof options.onContinue === "function") options.onContinue(getState());
      });
      replaceChildren(refs.next, next);
      if (typeof options.onNewPractice === "function") {
        refs.next.classList.add("has-practice-action");
        refs.next.append(button(options.newPracticeLabel || "Άλλη τριάδα για εξάσκηση", "secondary", function () {
          if (destroyed || !diagramsReady() || !state().solved) return;
          options.onNewPractice(getState());
        }));
      }
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
        revealResponse("success", refs.feedback, refs.next);
      } else {
        replaceChildren(refs.feedback, node("p", { text: result.message }));
        updateControls(controlId("check-button"));
        emitState();
        revealResponse("check-feedback", refs.feedback);
      }
    }

    function showDiagramZoom() {
      if (destroyed || mainImageStatus !== "ready" || zoomPanel) return;
      if (pageReveal) pageReveal.stop();
      const dialog = node(standalone ? "dialog" : "section", { class: "zoom-dialog", "aria-labelledby": controlId("zoom-title") });
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
      dialog.append(
        node("div", { class: "zoom-heading" }, [node("h2", { id: controlId("zoom-title"), text: "Η δομή σε αρχικό μέγεθος" }), close]),
        node("p", { text: "Αν η εικόνα δεν χωρά, μετακινήσου μέσα στο πλαίσιο με αφή ή τα πλήκτρα βέλους." }),
        viewport
      );
      if (standalone) {
        listen(dialog, "close", function () { finishZoom(dialog); });
        document.body.append(dialog);
        dialog.showModal();
      } else {
        dialog.setAttribute("role", "region");
        listen(dialog, "keydown", function (event) {
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
      refs.zoomButton.setAttribute("aria-expanded", "false");
      refs.zoomButton.disabled = mainImageStatus !== "ready";
      refs.zoomButton.focus({ preventScroll: true });
    }

    function closeZoom() {
      if (!zoomPanel) return;
      // Native close is queued; restore controls only when that panel finishes.
      if (standalone) zoomPanel.close();
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
  let renderId = 0;
  const enginePilot = new URLSearchParams(window.location.search).get("source") === "engine";
  const pilotStorageKey = "namelecule-repair-engine-pilot-v1";
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

  function readPilotProgress() {
    try { return JSON.parse(window.sessionStorage.getItem(pilotStorageKey)); }
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
    try { window.sessionStorage.setItem(pilotStorageKey, JSON.stringify(record)); }
    catch (_) { pilot.storageAvailable = false; }
  }

  function generatePilotGame(seed) {
    pilot.seed = global.NameleculeRepairGenerator.normalizeSeed(seed);
    game = validateGameData(global.NameleculeRepairGenerator.createGame(pilot.catalog, pilot.analyses, {
      seed: pilot.seed, difficulty: pilot.difficulty
    }));
  }

  function restorePilotProgress(record) {
    if (!record || record.version !== 1 || record.generatorVersion !== global.NameleculeRepairGenerator.version ||
        record.catalogRevision !== pilot.catalog.revision || record.engineSHA256 !== pilot.catalog.engineSHA256 ||
        !["basic", "challenge"].includes(record.difficulty) || typeof record.seed !== "string") return false;
    try { global.NameleculeRepairGenerator.normalizeSeed(record.seed); }
    catch (_) { return false; }
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
    const response = await fetch("./data/alkane-structures.json", { cache: "no-cache", signal: signal });
    if (!response.ok) throw new Error("Alkane structures HTTP " + response.status);
    const catalog = await response.json();
    assert(catalog && catalog.schemaVersion === 1 && Array.isArray(catalog.molecules) && catalog.molecules.length === 8, "Invalid alkane structure catalog");
    const analyses = [];
    // Bound parallel work; each analysis gets a fresh, short-lived core instance.
    for (let i = 0; i < catalog.molecules.length; i += 3) {
      const batch = await Promise.all(catalog.molecules.slice(i, i + 3).map(function (molecule) {
        return global.NameleculeChemistryClient.analyze(molecule, { signal: signal, engineSHA256: catalog.engineSHA256 });
      }));
      analyses.push.apply(analyses, batch);
    }
    if (signal.aborted) throw new DOMException("Cancelled", "AbortError");
    pilot = { catalog: catalog, analyses: analyses, seed: newSeed(), difficulty: "basic", storageAvailable: true };
    const restored = restorePilotProgress(readPilotProgress());
    if (!restored) {
      activeSet = null; states = []; roundIndex = 0; pilotPhase = "hub";
      pilot.difficulty = "basic";
      generatePilotGame(newSeed());
    }
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
      node("label", { for: "pilot-difficulty", text: "Δυσκολία" }), select,
      node("p", { text: "Στο Βασικό δίνεται μια αρχική κατεύθυνση. Στην Πρόκληση εντοπίζεις και τον κανόνα που χρειάζεται." }),
      node("p", { class: "muted", text: "Σε κάθε νέα προσπάθεια επιλέγονται τυχαία επισκευές από τα οκτώ διαθέσιμα αλκάνια." })
    ]);
  }

  function startSet(setId) {
    if (pilot) generatePilotGame(newSeed());
    activeSet = game.sets.find(function (entry) { return entry.id === setId; });
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
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function replaceRoot(content) {
    if (activeRound) { activeRound.destroy(); activeRound = null; }
    root.replaceChildren(content);
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
      if (pilot && pilotPhase === "round") renderRound();
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
        node("a", { class: "secondary", href: "name-repair.html", text: "Άνοιξε τα αρχικά σετ" })
      ]));
    }
  }

  function renderWelcome() {
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
      ["Δες τη δομή", "Σύνδεσε τους άνθρακες και τους κλάδους με το όνομα."],
      ["Βρες τι χρειάζεται αλλαγή", "Διάλεξε κομμάτι και αντικατάσταση ή άλλαξε τη σειρά."],
      ["Έλεγξε και ξαναδοκίμασε", "Μετά τη σωστή επισκευή, δες γιατί το όνομα ταιριάζει στη δομή."]
    ];
    const welcome = node("div", { class: "workshop-hub" }, [
      hero,
      node("p", { class: "pilot-entry" }, [node("a", {
        href: enginePilot ? "name-repair.html" : "name-repair.html?source=engine",
        text: enginePilot ? "Δοκιμή ερωτήσεων από τη μηχανή · Αρχικά σετ" : "Δοκίμασε νέες ερωτήσεις από τη μηχανή →"
      })]),
      sets,
      node("section", { class: "intro-how", "aria-label": "Πώς παίζεται" }, steps.map(function (step, index) {
        return node("div", { class: "how-item" }, [node("span", { class: "how-number", "aria-hidden": "true", text: String(index + 1) }), node("div", {}, [node("h2", { text: step[0] }), node("p", { text: step[1] })])]);
      }))
    ]);
    replaceRoot(welcome);
    savePilotProgress();
  }

  function renderSetPicker() {
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
    pilotPhase = "round";
    if (activeRound) activeRound.destroy();
    const index = roundIndex;
    const presentation = presentationForRound(round(), { difficulty: pilot ? pilot.difficulty : "basic" });
    activeRound = createRoundView(root, Object.assign({}, presentation, {
      initialState: state(), assetBase: "", progressList: progressList, setTitle: activeSet.title,
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
      node("p", { text: "Οι επισκευές και οι προσπάθειες αυτού του σετ θα μηδενιστούν." })
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
      node("div", { class: "results-actions" }, [button("Επιστροφή στα σετ", "primary", restartGame), node("a", { class: "secondary", href: "../design/welcome-proposal.html", text: "Επιστροφή στην αρχική" })])
    ]);
    replaceRoot(content);
    focusHeading();
    savePilotProgress();
  }

  loadGame();
})(typeof globalThis !== "undefined" ? globalThis : this);

class FakeNode{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.handlers={};this.parentNode=null;this.className='';this.open=false;this.hidden=false;this.focusCalls=0;this._text='';const names=new Set();this.classList={toggle:(name,on)=>on?names.add(name):names.delete(name),add:name=>names.add(name),remove:name=>names.delete(name),contains:name=>names.has(name)};}
 get isConnected(){return this===body||!!(this.parentNode&&this.parentNode.isConnected);}
 get textContent(){return this._text+this.children.map(child=>child.textContent).join('');}
 set textContent(value){this.replaceChildren();this._text=String(value);}
 append(...items){for(const item of items){if(item.parentNode)item.remove();item.parentNode=this;this.children.push(item);}}
 appendChild(item){this.append(item);return item;}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(item=>item!==this);this.parentNode=null;}}
 replaceChildren(...items){for(const item of this.children)item.parentNode=null;this.children=[];this._text='';this.append(...items);}
 setAttribute(key,value){this.attributes[key]=String(value);}
 removeAttribute(key){delete this.attributes[key];}
 addEventListener(name,handler){(this.handlers[name]||(this.handlers[name]=[])).push(handler);}
 fire(name,extra={}){for(const handler of this.handlers[name]||[])handler({target:this,preventDefault(){},stopPropagation(){},...extra});}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 querySelectorAll(selector){const match=node=>selector[0]==='#'?node.id===selector.slice(1):selector[0]==='.'?node.className.split(/\s+/).includes(selector.slice(1)):selector.split(',').some(tag=>node.tagName===tag.toUpperCase());const found=[];function walk(node){for(const child of node.children){if(match(child))found.push(child);walk(child);}}walk(this);return found;}
 find(id){return this.id===id?this:this.querySelector('#'+id);}
 showModal(){this.open=true;}
 close(){this.open=false;this.fire('close');}
 focus(){this.focusCalls++;}
}
let body;
const rounds=[];
let destroyCalls=0,storageReads=0,storageWrites=0;
let liveScenario=null,navigation=[];
const storage=new Map();
function resetEnvironment(){
 body=new FakeNode('body');rounds.length=0;destroyCalls=0;storageReads=0;storageWrites=0;storage.clear();liveScenario=null;navigation=[];
 global.document={body,baseURI:'http://memory.test/',readyState:'loading',createElement:tag=>new FakeNode(tag),getElementById:id=>body.find(id),querySelectorAll:selector=>body.querySelectorAll(selector)};
 global.sessionStorage={getItem(key){storageReads++;return storage.get(key)||null;},setItem(key,value){storageWrites++;storage.set(key,value);}};
 global.MuLERMoCScenario={present:true};global.fScenarioPresent=()=>liveScenario;
 global.fScenarioPlayUi=()=>{};global.fScenarioGo=index=>navigation.push(index);
 global.NameleculeRepairGame={mountRound(host,options){const handle={destroyed:false,destroy(){if(!this.destroyed){this.destroyed=true;destroyCalls++;}}};rounds.push({host,options,handle});return handle;}};
}

const controllerSource="/* Namelecule lesson checkpoints. Authored questions are separate from tab progress. */\n(function (global) {\n  \"use strict\";\n  const types = Object.create(null);\n  const records = new Map();\n  let preview = null; // Editor rehearsal only; never a stored learner receipt.\n  const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);\n  const clone = value => JSON.parse(JSON.stringify(value));\n  const storagePrefix = \"namelecule:lesson-checkpoints:v1:\";\n  let active = null;\n  let dialog = null;\n  let mountHost = null;\n  let retryButton = null;\n  let progressCounter = null;\n  let mounted = null;\n  let mountToken = 0;\n  let responseRevealer = null;\n  let practiceContinue = null;\n  let practiceNotice = null;\n\n  function supportsPractice(adapter) {\n    return [\"createPractice\", \"restorePractice\", \"mountPractice\"].every(key => typeof adapter[key] === \"function\");\n  }\n\n  function registerType(name, adapter) {\n    if (!/^[a-z][a-z0-9-]{0,48}$/.test(name) || own(types, name) || !adapter ||\n        [\"validate\", \"restore\", \"mount\"].some(key => typeof adapter[key] !== \"function\")) {\n      throw new Error(\"Invalid checkpoint type registration\");\n    }\n    types[name] = adapter;\n  }\n\n  registerType(\"name-repair\", {\n    validate(round) {\n      const engine = global.NameleculeRepairEngine;\n      if (!engine || typeof engine.validateRoundData !== \"function\") throw new Error(\"Repair engine unavailable\");\n      return engine.validateRoundData(round);\n    },\n    restore(round, state) {\n      const engine = global.NameleculeRepairEngine;\n      if (!engine || typeof engine.restoreRoundState !== \"function\") throw new Error(\"Repair restoration unavailable\");\n      return engine.restoreRoundState(round, state);\n    },\n    mount(host, options) {\n      if (!global.NameleculeRepairGame || typeof global.NameleculeRepairGame.mountRound !== \"function\") {\n        throw new Error(\"Repair interface unavailable\");\n      }\n      return global.NameleculeRepairGame.mountRound(host, options);\n    }\n  });\n\n  function validateCheckpoint(spec) {\n    if (!spec || typeof spec !== \"object\" || Array.isArray(spec) || spec.version !== 1 ||\n        typeof spec.id !== \"string\" || !/^[a-z][a-z0-9-]{0,80}$/.test(spec.id) ||\n        typeof spec.type !== \"string\" || !own(types, spec.type)) {\n      throw new Error(\"Unknown or invalid required checkpoint\");\n    }\n    const value = clone(spec);\n    if (own(value, \"openLabel\")) {\n      const label = typeof value.openLabel === \"string\" ? value.openLabel.trim() : \"\";\n      if (label && label.length <= 100) value.openLabel = label;\n      else delete value.openLabel;\n    }\n    types[value.type].validate(value.round);\n    return value;\n  }\n\n  function hasCheckpoints(scenario) {\n    return !!(scenario && Array.isArray(scenario.steps) && scenario.steps.some(step => step && own(step, \"checkpoint\")));\n  }\n\n  function signature(scenario) {\n    // No runtime card ID, current index or auto-generated creation timestamp:\n    // reloading an identical authored lesson keeps the same tab progress.\n    return JSON.stringify({ version: 1, title: String(scenario.title || \"\"),\n      author: String(scenario.author || \"Unknown\"), steps: scenario.steps });\n  }\n\n  function hash(text) {\n    let value = 2166136261;\n    for (let index = 0; index < text.length; index++) value = Math.imul(value ^ text.charCodeAt(index), 16777619);\n    return (value >>> 0).toString(16);\n  }\n\n  function recordFor(scenario) {\n    const content = signature(scenario);\n    if (isPreview(scenario)) return preview.record;\n    if (records.has(content)) return records.get(content);\n    const key = storagePrefix + hash(content);\n    let states = Object.create(null);\n    let practices = Object.create(null);\n    let storageAvailable = true;\n    try {\n      const saved = JSON.parse(global.sessionStorage.getItem(key) || \"null\");\n      // Compare the whole content as well as its short storage key. A hash\n      // collision or edited/reordered question cannot reuse another receipt.\n      if (saved && saved.version === 1 && saved.content === content && saved.states && typeof saved.states === \"object\") {\n        for (let index = 0; index < scenario.steps.length; index++) {\n          const step = scenario.steps[index];\n          if (step && own(step, \"checkpoint\") && own(saved.states, index)) {\n            try {\n              const spec = validateCheckpoint(step.checkpoint);\n              states[index] = types[spec.type].restore(spec.round, saved.states[index]);\n              if (supportsPractice(types[spec.type]) && saved.practices && own(saved.practices, index)) {\n                try { practices[index] = types[spec.type].restorePractice(spec.round, saved.practices[index]); }\n                catch (_) { /* Optional progress cannot invalidate an earned required receipt. */ }\n              }\n            } catch (_) { /* Invalid stored progress never unlocks a checkpoint. */ }\n          }\n        }\n      }\n    } catch (_) { storageAvailable = false; }\n    const result = { key, content, states, practices, storageAvailable };\n    records.set(content, result);\n    return result;\n  }\n\n  function persist(record) {\n    if (record.temporary) return;\n    try {\n      global.sessionStorage.setItem(record.key, JSON.stringify({ version: 1, content: record.content, states: record.states, practices: record.practices }));\n      record.storageAvailable = true;\n    } catch (_) { record.storageAvailable = false; }\n  }\n\n  function isComplete(scenario, index) {\n    const step = scenario && scenario.steps && scenario.steps[index];\n    if (!step || !own(step, \"checkpoint\")) return true;\n    try {\n      const spec = validateCheckpoint(step.checkpoint);\n      const state = types[spec.type].restore(spec.round, recordFor(scenario).states[index]);\n      return state.solved === true;\n    } catch (_) { return false; }\n  }\n\n  function resolveTarget(scenario, requested) {\n    if (!scenario || !Array.isArray(scenario.steps) || !scenario.steps.length) return 0;\n    const number = Number(requested);\n    const target = Math.max(0, Math.min(scenario.steps.length - 1, Number.isFinite(number) ? Math.floor(number) : 0));\n    for (let index = 0; index < target; index++) {\n      if (own(scenario.steps[index] || {}, \"checkpoint\") && !isComplete(scenario, index)) return index;\n    }\n    return target;\n  }\n\n  // Existing authored checkpoints remain synchronous. An adapter may need the\n  // engine to reconstruct a saved generated set before navigation can trust it.\n  function prepareTarget(scenario, requested, options) {\n    if (!scenario || !Array.isArray(scenario.steps)) return null;\n    const number = Number(requested);\n    const target = Math.max(0, Math.min(scenario.steps.length - 1, Number.isFinite(number) ? Math.floor(number) : 0));\n    const record = recordFor(scenario);\n    const content = record.content;\n    const signal = options && options.signal;\n    function checkCurrent() {\n      if ((signal && signal.aborted) || signature(scenario) !== content) {\n        const error = new Error(\"Checkpoint preparation cancelled\");\n        error.name = \"AbortError\";\n        throw error;\n      }\n    }\n    function scan(start) {\n      checkCurrent();\n      for (let index = start; index < target; index++) {\n        const step = scenario.steps[index];\n        if (!step || !own(step, \"checkpoint\")) continue;\n        const spec = validateCheckpoint(step.checkpoint);\n        const adapter = types[spec.type];\n        const saved = record.states[index];\n        if (saved && typeof adapter.prepare === \"function\") {\n          const savedContent = JSON.stringify(saved);\n          const pending = adapter.prepare(spec.round, saved, { signal });\n          if (pending && typeof pending.then === \"function\") {\n            return Promise.resolve(pending).then(state => {\n              checkCurrent();\n              if (JSON.stringify(record.states[index]) !== savedContent) {\n                const error = new Error(\"Checkpoint progress changed during preparation\");\n                error.name = \"AbortError\";\n                throw error;\n              }\n              record.states[index] = adapter.restore(spec.round, state);\n              persist(record);\n              return isComplete(scenario, index) ? scan(index + 1) : null;\n            });\n          }\n        }\n        if (!isComplete(scenario, index)) return null;\n      }\n      return null;\n    }\n    return scan(0);\n  }\n\n  const words = {\n    gr: { label: \"\u039c\u03b9\u03ba\u03c1\u03ae \u03c3\u03c4\u03ac\u03c3\u03b7 \u03b3\u03b9\u03b1 \u03b5\u03c0\u03b9\u03c3\u03ba\u03b5\u03c5\u03ae\", counter: \"\u039a\u03bf\u03c5\u03af\u03b6\", instruction: \"\u0395\u03c0\u03b9\u03c3\u03ba\u03b5\u03cd\u03b1\u03c3\u03b5 \u03c4\u03bf \u03cc\u03bd\u03bf\u03bc\u03b1 \u03b3\u03b9\u03b1 \u03bd\u03b1 \u03c3\u03c5\u03bd\u03b5\u03c7\u03af\u03c3\u03b5\u03b9\u03c2 \u03c4\u03b7 \u03b8\u03b5\u03c9\u03c1\u03af\u03b1.\",\n      open: \"\u03a3\u03c4\u03bf \u03a3\u03c5\u03bd\u03b5\u03c1\u03b3\u03b5\u03af\u03bf \u03bf\u03bd\u03bf\u03bc\u03ac\u03c4\u03c9\u03bd\", done: \"\u0397 \u03b5\u03c0\u03b9\u03c3\u03ba\u03b5\u03c5\u03ae \u03bf\u03bb\u03bf\u03ba\u03bb\u03b7\u03c1\u03ce\u03b8\u03b7\u03ba\u03b5. \u039c\u03c0\u03bf\u03c1\u03b5\u03af\u03c2 \u03bd\u03b1 \u03c3\u03c5\u03bd\u03b5\u03c7\u03af\u03c3\u03b5\u03b9\u03c2.\", revisit: \"\u0394\u03b5\u03c2 \u03be\u03b1\u03bd\u03ac \u03c4\u03b7\u03bd \u03b5\u03c0\u03b9\u03c3\u03ba\u03b5\u03c5\u03ae\",\n      back: \"\u0395\u03c0\u03b9\u03c3\u03c4\u03c1\u03bf\u03c6\u03ae \u03c3\u03c4\u03b7 \u03b8\u03b5\u03c9\u03c1\u03af\u03b1\", retry: \"\u03a6\u03cc\u03c1\u03c4\u03c9\u03c3\u03b5 \u03be\u03b1\u03bd\u03ac \u03c4\u03b7\u03bd \u03b1\u03c0\u03bf\u03c3\u03c4\u03bf\u03bb\u03ae\", error: \"\u0397 \u03b1\u03c0\u03bf\u03c3\u03c4\u03bf\u03bb\u03ae \u03b4\u03b5\u03bd \u03c6\u03bf\u03c1\u03c4\u03ce\u03b8\u03b7\u03ba\u03b5. \u0394\u03bf\u03ba\u03af\u03bc\u03b1\u03c3\u03b5 \u03be\u03b1\u03bd\u03ac \u03ae \u03b5\u03c0\u03ad\u03c3\u03c4\u03c1\u03b5\u03c8\u03b5 \u03c3\u03c4\u03b7 \u03b8\u03b5\u03c9\u03c1\u03af\u03b1.\",\n      storage: \"\u0397 \u03c0\u03c1\u03cc\u03bf\u03b4\u03bf\u03c2 \u03ba\u03c1\u03b1\u03c4\u03b9\u03ad\u03c4\u03b1\u03b9 \u03bc\u03cc\u03bd\u03bf \u03cc\u03c3\u03bf \u03bc\u03ad\u03bd\u03b5\u03b9 \u03b1\u03bd\u03bf\u03b9\u03c7\u03c4\u03ae \u03b1\u03c5\u03c4\u03ae \u03b7 \u03c3\u03b5\u03bb\u03af\u03b4\u03b1\u00b7 \u03b7 \u03b1\u03c0\u03bf\u03b8\u03ae\u03ba\u03b5\u03c5\u03c3\u03b7 \u03c4\u03b7\u03c2 \u03ba\u03b1\u03c1\u03c4\u03ad\u03bb\u03b1\u03c2 \u03b4\u03b5\u03bd \u03b5\u03af\u03bd\u03b1\u03b9 \u03b4\u03b9\u03b1\u03b8\u03ad\u03c3\u03b9\u03bc\u03b7.\",\n      reset: \"\u039d\u03ad\u03b1 \u03c0\u03c1\u03bf\u03c3\u03c0\u03ac\u03b8\u03b5\u03b9\u03b1\", resetLabel: \"\u039e\u03b5\u03ba\u03af\u03bd\u03b1 \u03c4\u03b7\u03bd \u03b5\u03c0\u03b9\u03c3\u03ba\u03b5\u03c5\u03ae \u03b1\u03c0\u03cc \u03c4\u03b7\u03bd \u03b1\u03c1\u03c7\u03ae\" },\n    en: { label: \"A short repair stop\", counter: \"Quiz\", instruction: \"Repair the name to continue the lesson.\",\n      open: \"Open the name workshop\", done: \"Repair completed. You can continue.\", revisit: \"Review the repair\",\n      back: \"Return to the lesson\", retry: \"Reload the mission\", error: \"The mission could not load. Retry or return to the lesson.\",\n      storage: \"Progress is kept only while this page remains open; tab storage is unavailable.\",\n      reset: \"New attempt\", resetLabel: \"Start this repair again\" }\n  };\n  Object.assign(words.gr, {\n    practice: \"\u0386\u03bb\u03bb\u03b7 \u03c4\u03c1\u03b9\u03ac\u03b4\u03b1 \u03b3\u03b9\u03b1 \u03b5\u03be\u03ac\u03c3\u03ba\u03b7\u03c3\u03b7\", resumePractice: \"\u03a3\u03c5\u03bd\u03ad\u03c7\u03b9\u03c3\u03b5 \u03c4\u03b7\u03bd \u03b5\u03be\u03ac\u03c3\u03ba\u03b7\u03c3\u03b7\",\n    practiceTitle: \"\u03a0\u03c1\u03bf\u03b1\u03b9\u03c1\u03b5\u03c4\u03b9\u03ba\u03ae \u03b5\u03be\u03ac\u03c3\u03ba\u03b7\u03c3\u03b7\", continueLesson: \"\u03a3\u03c5\u03bd\u03b5\u03c7\u03af\u03b6\u03c9 \u03c4\u03b7 \u03b8\u03b5\u03c9\u03c1\u03af\u03b1\",\n    practiceNote: \"\u0397 \u03b1\u03c1\u03c7\u03b9\u03ba\u03ae \u03c4\u03c1\u03b9\u03ac\u03b4\u03b1 \u03bf\u03bb\u03bf\u03ba\u03bb\u03b7\u03c1\u03ce\u03b8\u03b7\u03ba\u03b5. \u039c\u03c0\u03bf\u03c1\u03b5\u03af\u03c2 \u03bd\u03b1 \u03c3\u03c5\u03bd\u03b5\u03c7\u03af\u03c3\u03b5\u03b9\u03c2 \u03c4\u03b7 \u03b8\u03b5\u03c9\u03c1\u03af\u03b1 \u03bf\u03c0\u03bf\u03b9\u03b1\u03b4\u03ae\u03c0\u03bf\u03c4\u03b5 \u03c3\u03c4\u03b9\u03b3\u03bc\u03ae.\",\n    preparing: \"\u0395\u03c0\u03b1\u03bb\u03b7\u03b8\u03b5\u03cd\u03b5\u03c4\u03b1\u03b9 \u03b7 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03c5\u03bc\u03ad\u03bd\u03b7 \u03c0\u03c1\u03cc\u03bf\u03b4\u03cc\u03c2 \u03c3\u03bf\u03c5\u2026\"\n  });\n  Object.assign(words.en, {\n    practice: \"Another three for practice\", resumePractice: \"Resume practice\",\n    practiceTitle: \"Optional practice\", continueLesson: \"Continue the lesson\",\n    practiceNote: \"The required set is complete. You can continue the lesson at any time.\",\n    preparing: \"Checking your saved progress\u2026\"\n  });\n  function text(key) {\n    let lang = \"gr\";\n    try { if (typeof global.fMulerLang === \"function\" && global.fMulerLang() === \"en\") lang = \"en\"; } catch (_) {}\n    return words[lang][key];\n  }\n  function node(tag, className, value) {\n    const element = global.document.createElement(tag);\n    if (className) element.className = className;\n    if (value) element.textContent = value;\n    return element;\n  }\n  function button(label, className, action) {\n    const element = node(\"button\", className, label);\n    element.type = \"button\";\n    element.addEventListener(\"click\", action);\n    return element;\n  }\n\n  function validProgress(value) {\n    return !!(value && Number.isSafeInteger(value.current) && Number.isSafeInteger(value.total) &&\n      value.current >= 1 && value.current <= value.total);\n  }\n  function showProgress(value) {\n    if (!progressCounter) return;\n    const valid = validProgress(value);\n    progressCounter.hidden = !valid;\n    progressCounter.textContent = valid ? text(\"counter\") + \" \" + value.current + \"/\" + value.total : \"\";\n  }\n  function stopResponseScroll() {\n    if (responseRevealer) responseRevealer.stop();\n  }\n  function revealResponse(request) {\n    if (responseRevealer) responseRevealer.reveal(request);\n  }\n  function destroyMount() {\n    stopResponseScroll();\n    mountToken++;\n    showProgress(null);\n    const previous = mounted;\n    mounted = null;\n    if (previous && typeof previous.destroy === \"function\") previous.destroy();\n    if (mountHost) mountHost.replaceChildren();\n  }\n  function closeDialog() {\n    destroyMount();\n    if (dialog && dialog.open) dialog.close();\n    if (active && active.openButton && active.openButton.isConnected) active.openButton.focus({ preventScroll: true });\n  }\n  function ensureDialog() {\n    if (dialog) return;\n    dialog = node(\"dialog\", \"nl-quiz-dialog\");\n    dialog.id = \"nlQuizDialog\";\n    dialog.setAttribute(\"aria-labelledby\", \"nlQuizDialogTitle\");\n    const header = node(\"div\", \"nl-quiz-dialog-header\");\n    const title = node(\"h2\", \"nl-quiz-dialog-title\");\n    title.id = \"nlQuizDialogTitle\";\n    const back = button(\"\", \"nl-quiz-button nl-quiz-back\", closeDialog);\n    back.id = \"nlQuizBack\";\n    practiceContinue = button(\"\", \"nl-quiz-button nl-quiz-practice-continue\", () => { if (active) continueLesson(active); });\n    practiceContinue.id = \"nlQuizPracticeContinue\";\n    practiceContinue.hidden = true;\n    practiceNotice = node(\"p\", \"nl-quiz-practice-notice\");\n    practiceNotice.id = \"nlQuizPracticeNotice\";\n    practiceNotice.hidden = true;\n    const copy = node(\"div\", \"nl-quiz-dialog-copy\");\n    copy.append(title, practiceNotice);\n    const actions = node(\"div\", \"nl-quiz-dialog-actions\");\n    progressCounter = node(\"span\", \"nl-quiz-round-progress\");\n    progressCounter.id = \"nlQuizProgress\";\n    progressCounter.hidden = true;\n    progressCounter.setAttribute(\"role\", \"status\");\n    progressCounter.setAttribute(\"aria-live\", \"polite\");\n    progressCounter.setAttribute(\"aria-atomic\", \"true\");\n    actions.append(progressCounter, practiceContinue, back);\n    header.append(copy, actions);\n    mountHost = node(\"div\", \"nl-quiz-host\");\n    mountHost.id = \"nlQuizHost\";\n    retryButton = button(\"\", \"nl-quiz-button nl-quiz-retry\", () => { if (active) mountQuestion(active); });\n    retryButton.id = \"nlQuizRetry\";\n    retryButton.hidden = true;\n    mountHost.addEventListener(\"error\", event => {\n      if (dialog.open && event.target && event.target.tagName === \"IMG\") retryButton.hidden = false;\n    }, true);\n    dialog.append(header, mountHost, retryButton);\n    responseRevealer = global.NameleculeRepairGame.createResponseRevealer({\n      host: mountHost,\n      active: () => !!(dialog && dialog.open),\n      viewport() {\n        const box = dialog.getBoundingClientRect();\n        return { top: Math.max(box.top + dialog.clientTop, header.getBoundingClientRect().bottom) + 12,\n          bottom: box.top + dialog.clientTop + dialog.clientHeight - 12 };\n      },\n      scrollTop: () => dialog.scrollTop,\n      maxScroll: () => dialog.scrollHeight - dialog.clientHeight,\n      scrollTo(top, behavior) {\n        if (typeof dialog.scrollTo === \"function\") dialog.scrollTo({ top: top, behavior: behavior });\n        else dialog.scrollTop = top;\n      }\n    });\n    dialog.addEventListener(\"cancel\", event => { event.preventDefault(); closeDialog(); });\n    // Let the round handle its own keys first, then stop lesson arrows/Escape.\n    dialog.addEventListener(\"keydown\", event => { stopResponseScroll(); event.stopPropagation(); });\n    dialog.addEventListener(\"wheel\", stopResponseScroll, { passive: true });\n    dialog.addEventListener(\"touchstart\", stopResponseScroll, { passive: true });\n    dialog.addEventListener(\"pointerdown\", stopResponseScroll, { passive: true });\n    dialog.addEventListener(\"close\", () => { if (!dialog.open) destroyMount(); });\n    global.document.body.append(dialog);\n  }\n\n  function currentContext(context) {\n    if (active !== context) return false;\n    try {\n      const state = global.MuLERMoCScenario;\n      return !!(state && state.present && typeof global.fScenarioPresent === \"function\" &&\n        global.fScenarioPresent() === context.scenario && context.scenario.index === context.index &&\n        signature(context.scenario) === context.record.content);\n    } catch (_) { return false; }\n  }\n  function refreshCard(context) {\n    if (active !== context) return;\n    const done = isComplete(context.scenario, context.index);\n    context.status.textContent = text(context.preparing ? \"preparing\" : done ? \"done\" : \"instruction\");\n    context.openButton.disabled = !!context.preparing;\n    context.openButton.textContent = done ? text(\"revisit\") : (context.spec.openLabel || text(\"open\"));\n    context.section.classList.toggle(\"nl-quiz-complete\", done);\n    context.practiceButton.hidden = !done || !supportsPractice(types[context.spec.type]);\n    context.practiceButton.textContent = text(context.record.practices[context.index] ? \"resumePractice\" : \"practice\");\n    context.storageNote.textContent = context.record.storageAvailable ? \"\" : text(\"storage\");\n    context.storageNote.hidden = context.record.storageAvailable;\n  }\n  function updateNavigation(context) {\n    refreshCard(context);\n    if (typeof global.fScenarioPlayUi === \"function\") global.fScenarioPlayUi();\n  }\n  function continueLesson(context) {\n    if (!currentContext(context) || !isComplete(context.scenario, context.index)) return;\n    const destination = context.index + 1;\n    closeDialog();\n    if (typeof global.fScenarioGo === \"function\") global.fScenarioGo(destination);\n  }\n  function updateDialog(context) {\n    const finalActions = context.finalRoundVisible === true && context.successActionsReady === true &&\n      supportsPractice(types[context.spec.type]) &&\n      isComplete(context.scenario, context.index);\n    let optionalFinalActions = false;\n    if (context.practice && finalActions) {\n      try {\n        optionalFinalActions = types[context.spec.type]\n          .restorePractice(context.spec.round, context.record.practices[context.index]).solved === true;\n      } catch (_) { /* Keep the independent exit when optional progress cannot be verified. */ }\n    }\n    dialog.querySelector(\"#nlQuizDialogTitle\").textContent = text(context.practice ? \"practiceTitle\" : \"label\");\n    dialog.querySelector(\"#nlQuizBack\").hidden = context.practice || finalActions;\n    practiceNotice.textContent = text(\"practiceNote\");\n    practiceNotice.hidden = !context.practice;\n    practiceContinue.textContent = text(\"continueLesson\");\n    practiceContinue.hidden = !context.practice || optionalFinalActions;\n  }\n  function newPractice(context) {\n    const adapter = types[context.spec.type];\n    if (!currentContext(context) || !supportsPractice(adapter) || !isComplete(context.scenario, context.index)) return;\n    context.record.practices[context.index] = adapter.createPractice(context.spec.round,\n      context.record.practices[context.index] || context.record.states[context.index]);\n    persist(context.record);\n    refreshCard(context);\n    openDialog(context, true);\n  }\n  function prepareRequired(context) {\n    const adapter = types[context.spec.type], saved = context.record.states[context.index];\n    if (!supportsPractice(adapter) || !saved || typeof adapter.prepare !== \"function\") return;\n    const abort = new AbortController();\n    context.preparationAbort = abort;\n    const original = JSON.stringify(saved);\n    try {\n      const pending = adapter.prepare(context.spec.round, clone(saved), { signal: abort.signal });\n      if (!pending || typeof pending.then !== \"function\") return;\n      context.preparing = true;\n      Promise.resolve(pending).then(state => {\n        if (abort.signal.aborted || !currentContext(context) || JSON.stringify(context.record.states[context.index]) !== original) return;\n        context.record.states[context.index] = adapter.restore(context.spec.round, state);\n        persist(context.record);\n      }).catch(() => { /* Open the original repair to retry; optional state never grants access. */ }).finally(() => {\n        if (!abort.signal.aborted && currentContext(context)) { context.preparing = false; updateNavigation(context); }\n      });\n    } catch (_) { /* The ordinary required mount retains its retry UI. */ }\n  }\n  function mountQuestion(context) {\n    if (!currentContext(context)) return;\n    destroyMount();\n    context.finalRoundVisible = false;\n    context.successActionsReady = false;\n    const token = mountToken;\n    let visibleRound = null;\n    retryButton.hidden = true;\n    try {\n      const spec = validateCheckpoint(context.spec);\n      const adapter = types[spec.type];\n      const optional = context.practice && supportsPractice(adapter) && isComplete(context.scenario, context.index);\n      context.practice = !!optional;\n      updateDialog(context);\n      const states = optional ? context.record.practices : context.record.states;\n      const restore = optional ? adapter.restorePractice : adapter.restore;\n      const mount = optional ? adapter.mountPractice : adapter.mount;\n      mounted = mount(mountHost, {\n        round: clone(spec.round), assetBase: \"games/\",\n        initialState: states[context.index] ? clone(states[context.index]) : null,\n        newPracticeLabel: text(\"practice\"),\n        onNewPractice: supportsPractice(adapter) ? () => { if (token === mountToken) newPractice(context); } : undefined,\n        onProgress(value) {\n          if (token !== mountToken || !currentContext(context)) return;\n          showProgress(value);\n          context.finalRoundVisible = validProgress(value) && value.current === value.total;\n          if (!context.finalRoundVisible) context.successActionsReady = false;\n          updateDialog(context);\n          const nextRound = validProgress(value) ? value.current + \"/\" + value.total : null;\n          // A new question starts above the fold; same-round updates keep the learner's scroll.\n          if (nextRound !== visibleRound) {\n            stopResponseScroll();\n            if (nextRound && dialog && dialog.open) dialog.scrollTop = 0;\n          }\n          visibleRound = nextRound;\n        },\n        onSuccessActionsReady(ready) {\n          if (token !== mountToken || !currentContext(context)) return;\n          context.successActionsReady = ready === true;\n          updateDialog(context);\n        },\n        onReveal(request) {\n          if (token !== mountToken || !currentContext(context)) return;\n          revealResponse(request);\n        },\n        onStateChange(state) {\n          if (token !== mountToken || !currentContext(context)) return;\n          const wasComplete = isComplete(context.scenario, context.index);\n          states[context.index] = restore(spec.round, state);\n          persist(context.record);\n          refreshCard(context);\n          if (wasComplete !== isComplete(context.scenario, context.index)) updateNavigation(context);\n        },\n        onSolved(result, state) {\n          if (token !== mountToken || !currentContext(context) || !result || result.kind !== \"correct\") return;\n          const normalized = restore(spec.round, state);\n          if (!normalized.solved) return;\n          states[context.index] = normalized;\n          persist(context.record);\n          updateNavigation(context);\n          updateDialog(context);\n        },\n        onContinue() {\n          if (token !== mountToken || !currentContext(context) || !isComplete(context.scenario, context.index)) return;\n          continueLesson(context);\n        }\n      });\n    } catch (_) {\n      context.finalRoundVisible = false;\n      context.successActionsReady = false;\n      updateDialog(context);\n      showProgress(null);\n      mountHost.replaceChildren(node(\"p\", \"nl-quiz-error\", text(\"error\")));\n      retryButton.hidden = false;\n    }\n  }\n  function openDialog(context, optional) {\n    if (!currentContext(context) || context.preparing) return;\n    context.practice = optional === true && supportsPractice(types[context.spec.type]) && isComplete(context.scenario, context.index);\n    ensureDialog();\n    updateDialog(context);\n    dialog.querySelector(\"#nlQuizBack\").textContent = text(\"back\");\n    retryButton.textContent = text(\"retry\");\n    if (typeof dialog.showModal !== \"function\") {\n      context.status.textContent = text(\"error\");\n      return;\n    }\n    if (!dialog.open) dialog.showModal();\n    mountQuestion(context);\n  }\n\n  function onExit() {\n    closeDialog();\n    if (active && active.preparationAbort) active.preparationAbort.abort();\n    if (active && active.section) active.section.remove();\n    active = null;\n  }\n  function isPreview(scenario) {\n    return !!(preview && preview.scenario === scenario && preview.record.content === signature(scenario));\n  }\n  function endPreview() {\n    if (!preview) return;\n    preview = null;\n    onExit();\n  }\n  function beginPreview(scenario) {\n    endPreview();\n    onExit();\n    preview = { scenario, record: { key: null, content: signature(scenario),\n      states: Object.create(null), practices: Object.create(null), storageAvailable: true, temporary: true } };\n  }\n  function onStep(scenario, index) {\n    const step = scenario && scenario.steps && scenario.steps[index];\n    if (!step || !own(step, \"checkpoint\")) { onExit(); return; }\n    const content = signature(scenario);\n    if (active && active.scenario === scenario && active.index === index && active.record.content === content &&\n        active.section.isConnected) { refreshCard(active); return; }\n    onExit();\n    const spec = validateCheckpoint(step.checkpoint);\n    const section = node(\"section\", \"nl-quiz-checkpoint\");\n    section.id = \"nlQuizCheckpoint\";\n    section.setAttribute(\"aria-labelledby\", \"nlQuizCheckpointHeading\");\n    const copy = node(\"div\", \"nl-quiz-checkpoint-copy\");\n    const heading = node(\"h2\", \"nl-quiz-checkpoint-heading\", text(\"label\"));\n    heading.id = \"nlQuizCheckpointHeading\";\n    const status = node(\"p\", \"nl-quiz-checkpoint-status\");\n    status.id = \"nlQuizCheckpointStatus\";\n    status.setAttribute(\"aria-live\", \"polite\");\n    const storageNote = node(\"p\", \"nl-quiz-storage-note\");\n    storageNote.hidden = true;\n    copy.append(heading, status, storageNote);\n    const context = { scenario, index, spec, section, status, storageNote, record: recordFor(scenario) };\n    context.openButton = button(\"\", \"nl-quiz-button nl-quiz-open\", () => openDialog(context));\n    context.openButton.id = \"nlQuizOpen\";\n    context.practiceButton = button(\"\", \"nl-quiz-button nl-quiz-practice-open\", () => {\n      if (context.record.practices[context.index]) openDialog(context, true);\n      else newPractice(context);\n    });\n    context.practiceButton.id = \"nlQuizPracticeOpen\";\n    context.practiceButton.hidden = true;\n    const actions = node(\"div\", \"nl-quiz-checkpoint-actions\");\n    actions.append(context.openButton, context.practiceButton);\n    section.append(copy, actions);\n    const note = global.document.getElementById(\"scStepText\");\n    const title = global.document.getElementById(\"pageTitle\");\n    if (note && note.parentNode) note.insertAdjacentElement(\"afterend\", section);\n    else if (title && title.parentNode) title.insertAdjacentElement(\"afterend\", section);\n    else global.document.body.append(section);\n    active = context;\n    prepareRequired(context);\n    refreshCard(context);\n  }\n\n  function reset(scenario) {\n    const record = recordFor(scenario);\n    record.states = Object.create(null);\n    record.practices = Object.create(null);\n    persist(record);\n    if (active && active.scenario === scenario) { closeDialog(); updateNavigation(active); }\n  }\n\n  global.NameleculeQuizCheckpoints = { registerType, validateCheckpoint, hasCheckpoints,\n    resolveTarget, prepareTarget, isComplete, onStep, onExit, reset,\n    beginPreview, endPreview, isPreview };\n})(typeof window !== \"undefined\" ? window : globalThis);\n";
// Developer controller evidence. Adapter, DOM, storage and abort are declared doubles.
let checks = 0;
const labels = [];
function check(ok, label) { if (!ok) throw Error(label); checks++; labels.push(label); }
function equal(actual, expected, label) { check(JSON.stringify(actual) === JSON.stringify(expected), label); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function deferred() { let resolve, reject; const promise = new Promise((a,b) => { resolve=a;reject=b; });return {promise,resolve,reject}; }
async function turns() { for (let index=0;index<20;index++) await Promise.resolve(); }
global.AbortController = class {
  constructor() { this.signal={aborted:false}; }
  abort() { this.signal.aborted=true; }
};
FakeNode.prototype.contains=function(node){return this===node||this.children.some(child=>child.contains(node));};
FakeNode.prototype.getBoundingClientRect=function(){return {top:0,bottom:0,height:0};};

function signature(scenario) { return JSON.stringify({version:1,title:String(scenario.title||''),author:String(scenario.author||'Unknown'),steps:scenario.steps}); }
function recordKey(scenario) { const content=signature(scenario);let hash=2166136261;for(let i=0;i<content.length;i++)hash=Math.imul(hash^content.charCodeAt(i),16777619);return 'namelecule:lesson-checkpoints:v1:'+(hash>>>0).toString(16); }
function scenario(type='practice-probe') { return {title:'Optional controller contract',author:'Declared Developer double',index:0,steps:[{checkpoint:{version:1,id:'required-three',type,round:{topic:'straight',roundCount:3}}},{text:'Theory after required gate'},{checkpoint:{version:1,id:'required-three-second',type,round:{topic:'branched',roundCount:3}}},{text:'Theory after second gate'}]}; }
function receipt(seed='required-1',answers=[true,true,true],currentRound=2) { return {version:1,seed,currentRound,answers:answers.slice(),solved:true}; }
function boot(options={}) {
  const copied=options.storage ? Array.from(options.storage) : [];
  resetEnvironment();for(const [key,value] of copied)storage.set(key,value);
  NameleculeRepairGame.createResponseRevealer=()=>({stop(){},reveal(){}});
  new Function(controllerSource)();
  const C=NameleculeQuizCheckpoints,mounts=[],preparations=[],created=[];
  const requiredTrusted=new Set(options.requiredTrusted||[]),optionalTrusted=new Set(options.optionalTrusted||[]);
  const controls={prepare:null,mountError:false,optionalMountError:false};
  let practiceNumber=0;
  function restore(value,previous,optional) {
    if(optional&&controls.optionalRestoreError)throw Error('declared optional verification unavailable');
    if(previous&&previous.malformed)throw Error('malformed '+(optional?'practice':'required'));
    const seed=previous&&typeof previous.seed==='string'?previous.seed:null;
    const answers=previous&&Array.isArray(previous.answers)&&previous.answers.length===3?previous.answers.map(v=>v===true):[false,false,false];
    const trusted=(optional?optionalTrusted:requiredTrusted).has(seed);
    return {version:1,seed,currentRound:previous&&Number.isInteger(previous.currentRound)?Math.max(0,Math.min(2,previous.currentRound)):0,answers,solved:!!seed&&trusted&&answers.every(v=>v)};
  }
  function mount(host,config,optional) {
    if(optional?controls.optionalMountError:controls.mountError)throw Error('declared mount failure');
    if(controls.reportFinalThenThrow){config.onProgress({current:3,total:3});if(typeof config.onSuccessActionsReady==='function')config.onSuccessActionsReady(true);throw Error('declared failure after final progress');}
    const seed=config.initialState&&config.initialState.seed||'required-'+(config.round.topic==='branched'?'2':'1');
    (optional?optionalTrusted:requiredTrusted).add(seed);
    const mounted={host,options:config,optional,seed,destroyed:false,destroyCalls:0};
    mounted.handle={destroy(){mounted.destroyed=true;mounted.destroyCalls++;}};
    mounts.push(mounted);return mounted.handle;
  }
  const adapter={validate(value){if(!value||value.roundCount!==3)throw Error('invalid probe');return value;},restore(value,state){return restore(value,state,false);},
    prepare(value,state,config){const call={round:clone(value),state:clone(state),signal:config.signal};preparations.push(call);return controls.prepare?controls.prepare(call):null;},
    mount(host,config){return mount(host,config,false);}};
  if(options.supportsPractice!==false)Object.assign(adapter,{
    createPractice(value,previous){const result={version:1,seed:'practice-'+(++practiceNumber),currentRound:0,answers:[false,false,false],solved:false};created.push({previous:clone(previous),result:clone(result)});return result;},
    restorePractice(value,state){return restore(value,state,true);},
    mountPractice(host,config){return mount(host,config,true);}
  });
  C.registerType('practice-probe',adapter);
  const s=options.scenario||scenario();liveScenario=s;
  function step(index=0){s.index=index;liveScenario=s;C.onStep(s,index);}
  function saved(){const value=storage.get(recordKey(s));return value?JSON.parse(value):null;}
  function seed(states,practices){storage.set(recordKey(s),JSON.stringify({version:1,content:signature(s),states, ...(practices===undefined?{}:{practices})}));}
  return {C,s,step,saved,seed,controls,mounts,preparations,created,requiredTrusted,optionalTrusted,latest:()=>mounts.at(-1)};
}
function click(id){const n=body.find(id);if(!n)throw Error('missing '+id);n.fire('click');return n;}
function open(env){click('nlQuizOpen');return env.latest();}
function complete(env,mount=env.latest()){const state=receipt(mount.seed);mount.options.onStateChange(state);mount.options.onSolved({kind:'correct'},state);if(typeof mount.options.onSuccessActionsReady==='function')mount.options.onSuccessActionsReady(true);return state;}

async function main(){
  let e=boot();e.step();
  check(!e.C.isComplete(e.s,0)&&e.C.resolveTarget(e.s,3)===0,'untouched required gate remains locked');
  check(body.find('nlQuizPracticeOpen').hidden,'no optional card before required mastery');
  click('nlQuizPracticeOpen');check(e.created.length===0&&e.mounts.length===0,'forced hidden practice card cannot bypass initial gate');
  let m=open(e);check(!body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'required header exposes Return only');click('nlQuizBack');check(!body.find('nlQuizDialog').open&&!e.C.isComplete(e.s,0),'visible required Return closes without unlocking');m=open(e);check(!m.optional&&typeof m.options.onNewPractice==='function','supported required mount receives opt-in action callback');
  m.options.onNewPractice();check(e.created.length===0,'onNewPractice independently verifies original mastery');
  m.options.onSolved({kind:'correct'},{...receipt(m.seed),answers:[true,true,false]});check(!e.C.isComplete(e.s,0),'claimed success without third repair is rejected');
  for(const answers of [[true,false,false],[true,true,false]]){
    m.options.onStateChange(receipt(m.seed,answers,answers[1]?1:0));
    check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'partial required answers do not expose optional card '+answers.filter(Boolean).length);
  }
  complete(e,m);check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'required three verified successes expose optional card');
  check(e.C.resolveTarget(e.s,3)===2,'first gate mastery does not bypass second gate');
  const required=clone(e.saved().states[0]);m.options.onNewPractice();m=e.latest();
  check(m.optional&&e.created.length===1,'success action starts optional mount');
  check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional header exposes Continue only');
  body.find('nlQuizDialog').fire('cancel');click('nlQuizOpen');check(!body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'reused dialog restores Return for required review');body.find('nlQuizDialog').fire('cancel');click('nlQuizPracticeOpen');m=e.latest();check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'reused dialog hides Return again for optional resume');
  equal(e.created[0].previous,required,'initial optional creation receives original required receipt');
  equal(e.saved().states[0],required,'starting optional practice preserves original required bytes');
  check(!body.find('nlQuizPracticeContinue').hidden&&!body.find('nlQuizPracticeNotice').hidden&&body.find('nlQuizDialogTitle').textContent==='Προαιρετική εξάσκηση','optional mode exposes continue and clear status');
  check(body.find('nlQuizPracticeNotice').textContent.includes('αρχική τριάδα ολοκληρώθηκε'),'optional status explicitly states required mastery');
  m.options.onProgress({current:1,total:3});check(body.find('nlQuizProgress').textContent==='Κουίζ 1/3','optional mount retains quiz position counter');
  const optionalWrong=receipt(m.seed,[true,false,false],1);m.options.onStateChange(optionalWrong);
  check(e.C.isComplete(e.s,0),'wrong or incomplete optional answers never relock required gate');
  equal(e.saved().states[0],required,'wrong optional answer leaves required receipt unchanged');
  check(e.saved().practices[0].seed===m.seed&&!e.saved().practices[0].solved,'optional answer persists in separate practices field');
  body.find('nlQuizDialog').fire('cancel');check(m.destroyed&&!body.find('nlQuizDialog').open,'Return destroys only current optional mount');
  check(body.find('nlQuizPracticeOpen').textContent==='Συνέχισε την εξάσκηση','card offers resume after partial optional exit');
  click('nlQuizPracticeOpen');let reopened=e.latest();
  check(reopened.optional&&reopened.seed===m.seed&&reopened.options.initialState.currentRound===1,'same-page reopen restores current optional attempt');
  equal(reopened.options.initialState.answers,[true,false,false],'same-page reopen retains optional answers');
  m.options.onStateChange(receipt(m.seed));equal(e.saved().practices[0].answers,[true,false,false],'closed optional callback cannot overwrite current attempt');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1&&!body.find('nlQuizDialog').open&&e.C.isComplete(e.s,0),'header Continue advances with optional set unfinished');
  e.step(0);click('nlQuizPracticeOpen');m=e.latest();
  for(let index=0;index<40;index++){
    const old=m;m.options.onNewPractice();m=e.latest();
    check(m.optional&&m.seed!==old.seed&&old.destroyed,'repeat replaces previous optional mount '+index);
    check(Object.keys(e.saved().practices).length===1&&Object.keys(e.saved().states).length===1,'repeat storage keeps one optional and original receipt '+index);
    equal(e.saved().states[0],required,'repeat preserves original required receipt '+index);
  }
  const latestBefore=clone(e.saved()),stale=reopened.options;
  stale.onNewPractice();stale.onSolved({kind:'correct'},receipt('bad'));stale.onContinue();
  equal(e.saved(),latestBefore,'stale callbacks after repeats cannot mutate storage or create attempts');
  check(e.C.isComplete(e.s,0),'mastery remains verified after more than 32 optional replacements');
  // Both gates have independent required and current practice fields.
  body.find('nlQuizDialog').fire('cancel');e.step(2);const second=open(e);complete(e,second);second.options.onNewPractice();
  check(e.saved().states[0].seed==='required-1'&&e.saved().states[2].seed==='required-2','both required gates retain separate mastery receipts');
  check(Object.keys(e.saved().practices).length===2&&e.C.resolveTarget(e.s,3)===3,'both gates may keep one optional attempt and theory remains unlocked');

  // Refresh must verify original required answers before accepting optional access.
  const storageSnapshot=Array.from(storage);e=boot({storage:storageSnapshot});
  const prep=deferred();e.controls.prepare=call=>prep.promise.then(()=>{e.requiredTrusted.add(call.state.seed);return call.state;});e.step(0);
  check(e.preparations.length===1&&e.preparations[0].state.seed==='required-1','refresh prepares original required receipt rather than optional seed');
  check(body.find('nlQuizOpen').disabled&&body.find('nlQuizPracticeOpen').hidden&&!e.C.isComplete(e.s,0),'cold saved practice stays unavailable while required validation is pending');
  click('nlQuizOpen');click('nlQuizPracticeOpen');check(e.mounts.length===0,'synthetic clicks cannot open while preparation is pending');
  prep.resolve();await turns();
  check(!body.find('nlQuizOpen').disabled&&e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'completed required verification restores practice card');
  click('nlQuizPracticeOpen');check(e.latest().optional&&e.latest().options.initialState.seed===latestBefore.practices[0].seed,'refresh restores same optional attempt');
  equal(e.saved().states[0],required,'refresh preparation preserves original verified required receipt');
  const furtherPreparation=e.C.prepareTarget(e.s,3,{});check(!!furtherPreparation&&typeof furtherPreparation.then==='function','forward navigation prepares still-cold second required gate');await furtherPreparation;
  check(e.preparations.at(-1).state.seed==='required-2'&&e.preparations.every(call=>call.state.seed.startsWith('required-')),'forward preparation reads required receipts and never current optional seeds');
  check(e.C.resolveTarget(e.s,3)===3&&e.C.isComplete(e.s,2),'forward preparation independently validates both required gates');
  check(Object.keys(e.saved().practices).length===2,'forward required verification preserves both saved optional attempts');

  // Stored optional data cannot stand in for missing or unproven required answers.
  e=boot();e.seed({0:receipt('untrusted-required',[false,false,false])},{0:receipt('trusted-optional')});e.optionalTrusted.add('trusted-optional');e.step();
  check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'solved optional receipt cannot unlock incomplete required gate');
  open(e).options.onNewPractice();check(e.created.length===0,'direct practice callback cannot promote optional completion to required mastery');
  e=boot();e.seed({}, {0:receipt('orphan-practice')});e.step();check(!e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'orphan practice without required receipt does not bypass gate');
  e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()},{0:{malformed:true}});e.step();
  check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'malformed optional receipt does not erase verified required mastery');
  click('nlQuizPracticeOpen');check(e.created.length===1&&e.latest().optional,'malformed optional receipt recovers as a fresh optional attempt');
  e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();
  check(e.C.isComplete(e.s,0)&&!body.find('nlQuizPracticeOpen').hidden,'old receipt without practices field retains mastery');

  // Unsupported adapters keep their existing required-only flow.
  e=boot({supportsPractice:false});e.step();m=open(e);
  check(m.options.onNewPractice===undefined&&body.find('nlQuizPracticeOpen').hidden,'unsupported type never receives opt-in renderer action');
  complete(e,m);check(e.C.isComplete(e.s,0)&&body.find('nlQuizPracticeOpen').hidden,'unsupported type completion remains ordinary required flow');
  m.options.onContinue();check(navigation.at(-1)===1,'unsupported required type still continues');

  // Active ownership also rejects callbacks from replaced scenarios and steps.
  for(const mode of ['different-object','different-step','edited-content']){
    e=boot();e.step();m=open(e);const writesBefore=storageWrites;
    if(mode==='different-object')liveScenario={...e.s};
    else if(mode==='different-step')e.s.index=1;
    else e.s.title+=' changed';
    m.options.onStateChange(receipt(m.seed));m.options.onSolved({kind:'correct'},receipt(m.seed));m.options.onNewPractice();m.options.onContinue();
    check(storageWrites===writesBefore&&e.created.length===0&&navigation.length===0,'current-context guard rejects stale '+mode+' callbacks');e.C.onExit();
  }

  // Optional loading/error/abort may not remove the independent Continue control.
  e=boot();e.step();m=open(e);complete(e,m);e.controls.optionalMountError=true;m.options.onNewPractice();
  check(!!body.find('nlQuizHost').querySelector('.nl-quiz-error')&&!body.find('nlQuizRetry').hidden,'optional thrown generation/mount error exposes retry');
  check(!body.find('nlQuizPracticeContinue').hidden&&e.C.isComplete(e.s,0),'optional error retains Continue and mastery');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1,'learner continues during optional error');
  e.step(0);e.controls.optionalMountError=false;click('nlQuizPracticeOpen');m=e.latest();m.options.onProgress(null);
  check(!body.find('nlQuizPracticeContinue').hidden&&body.find('nlQuizProgress').hidden,'loading optional progress retains independent Continue');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1&&m.destroyed,'learner continues during optional loading');
  const count=storageWrites;m.options.onStateChange(receipt(m.seed));m.options.onSolved({kind:'correct'},receipt(m.seed));m.options.onNewPractice();
  check(storageWrites===count,'late aborted optional callbacks do not persist or start more work');

  // Preparation failures, cancellation and reset cannot authorize stale state.
  for(const mode of ['reject','exit','reset','signature-change']){
    e=boot();e.seed({0:receipt()},{0:receipt('practice-saved',[true,false,false],1)});const work=deferred();
    e.controls.prepare=call=>work.promise.then(()=>{e.requiredTrusted.add(call.state.seed);return call.state;});e.step();const signal=e.preparations[0].signal;
    if(mode==='reject')work.reject(Error('declared preparation failure'));
    else if(mode==='exit'){e.C.onExit();work.resolve();}
    else if(mode==='reset'){e.C.reset(e.s);work.resolve();}
    else{e.s.title+=' edited';work.resolve();}
    await turns();
    if(mode==='exit')check(signal.aborted&&!body.find('nlQuizDialog')?.open,'exit aborts required preparation and ignores late completion');
    if(mode==='reset')check(!e.C.isComplete(e.s,0)&&Object.keys(e.saved().states).length===0&&Object.keys(e.saved().practices).length===0,'reset clears both fields and late required preparation cannot restore them');
    if(mode==='reject')check(!e.C.isComplete(e.s,0)&&!body.find('nlQuizOpen').disabled&&body.find('nlQuizPracticeOpen').hidden,'failed required preparation stays locked and original repair can retry');
    if(mode==='signature-change')check(!e.C.isComplete(e.s,0),'authored signature change rejects late preparation');
  }

  // Reset invalidates mounted callback ownership and both optional/required records.
  e=boot();e.step();m=open(e);complete(e,m);m.options.onNewPractice();m=e.latest();e.C.reset(e.s);
  check(!e.C.isComplete(e.s,0)&&Object.keys(e.saved().states).length===0&&Object.keys(e.saved().practices).length===0&&!body.find('nlQuizDialog').open,'active reset closes practice and clears both record fields');
  const resetWrites=storageWrites;m.options.onStateChange(receipt(m.seed));m.options.onNewPractice();check(storageWrites===resetWrites&&!e.C.isComplete(e.s,0),'late callback after reset cannot recreate either record');

  // A storage write failure retains in-memory required mastery and optional exit.
  e=boot();e.step();m=open(e);global.sessionStorage.setItem=()=>{throw Error('declared unavailable storage');};complete(e,m);m.options.onNewPractice();
  check(e.C.isComplete(e.s,0)&&e.latest().optional,'unavailable storage does not remove in-memory mastery or optional access');
  check(!body.find('nlQuizCheckpoint').querySelector('.nl-quiz-storage-note').hidden,'unavailable storage is disclosed on checkpoint card');
  click('nlQuizPracticeContinue');check(navigation.at(-1)===1,'optional Continue works when tab storage is unavailable');

  // Preview has separate mastery/practice and produces no stored learner writes.
  e=boot();e.step();m=open(e);complete(e,m);m.options.onNewPractice();const learnerStorage=Array.from(storage),learnerRequired=clone(e.saved().states);
  const previewScenario=clone(e.s);e.C.beginPreview(previewScenario);liveScenario=previewScenario;e.C.onStep(previewScenario,0);
  check(e.C.isPreview(previewScenario)&&!e.C.isComplete(previewScenario,0),'preview starts without adopting learner mastery');
  const writes=storageWrites;m=open(e);complete(e,m);m.options.onNewPractice();const previewMount=e.latest();previewMount.options.onStateChange(receipt(previewMount.seed,[true,false,false],1));
  check(storageWrites===writes,'preview required and optional work never persist to learner storage');
  equal(Array.from(storage),learnerStorage,'preview preserves exact learner stored records');e.C.endPreview();liveScenario=e.s;e.step();
  check(!e.C.isPreview(e.s)&&e.C.isComplete(e.s,0),'ending preview restores original learner mastery');equal(e.saved().states,learnerRequired,'preview leaves original required receipts unchanged');
  click('nlQuizPracticeOpen');check(e.latest().optional,'ending preview restores learner optional attempt');

  // Synthetic queued native-close event: reopening must retain the new mount.
  m=e.latest();const dialog=body.find('nlQuizDialog');dialog.close=function(){this.open=false;};body.find('nlQuizDialog').fire('cancel');click('nlQuizPracticeOpen');const newMount=e.latest();
  check(dialog.open&&newMount!==m&&!newMount.destroyed,'optional dialog reopens before queued close event');dialog.fire('close');
  check(!newMount.destroyed&&dialog.open,'queued close guard preserves reopened optional mount (synthetic event only)');
  print(JSON.stringify({completed:true,checks,labels,limits:['Actual current full controller runs in system JavaScriptCore. FakeNode DOM, storage, abort, adapter completion and preparation are explicit doubles.','No native browser layout/input, generated molecular answers, real transport, real timer or native close queue claim.','Probe trusted-required and trusted-optional sets model independent receipt validation; real engine/cache reconstruction is tested separately by adapter and integration owners.']}));
}


function finalHeaderCases() {
 const startChecks=checks;
 let e=boot();e.step();let m=open(e);
 for(const n of [1,2]) {
  m.options.onProgress({current:n,total:3});
  m.options.onStateChange(receipt(m.seed,n===1?[true,false,false]:[true,true,false],n-1));
  check(!body.find('nlQuizBack').hidden,'required earlier rendered round retains Return '+n);
 }
 m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'unsolved third round retains Return');
 m.options.onSolved({kind:'correct'},receipt(m.seed,[true,true,false]));
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,0),'unverified claimed final success cannot hide Return or unlock');
 complete(e,m);
 check(body.find('nlQuizBack').hidden&&e.C.isComplete(e.s,0),'verified live third success hides Return');
 const required=clone(e.saved().states[0]);
 m.options.onProgress(null);
 check(!body.find('nlQuizBack').hidden,'required loading or error null progress restores Return after mastery');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'restored rendered final success hides Return');
 for(const value of [{current:0,total:3},{current:4,total:3},{current:3,total:0},{current:3.5,total:3.5},{}]) {
  m.options.onProgress(value);check(!body.find('nlQuizBack').hidden,'invalid progress cannot hide Return '+JSON.stringify(value));
 }
 m.options.onProgress({current:1,total:3});
 check(!body.find('nlQuizBack').hidden,'earned mastery alone does not hide Return on earlier rendered round');
 m.options.onProgress({current:3,total:3});
 body.find('nlQuizDialog').fire('cancel');m=open(e);
 check(!body.find('nlQuizBack').hidden,'reopen resets transient final visibility before rendered progress');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'reopen hides Return when restored final content is rendered');
 m.options.onNewPractice();m=e.latest();
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'new optional set retains existing Continue-only header');
 m.options.onProgress(null);
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional loading retains Continue-only header');
 equal(e.saved().states[0],required,'header changes preserve exact verified required receipt');
 body.find('nlQuizDialog').fire('cancel');e.step(2);m=open(e);m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,2),'next required gate does not inherit hidden Return or mastery');
 const old=m;body.find('nlQuizDialog').fire('cancel');e.step(0);m=open(e);m.options.onProgress({current:1,total:3});
 old.options.onProgress({current:3,total:3});old.options.onSolved({kind:'correct'},receipt(old.seed));
 check(!body.find('nlQuizBack').hidden,'stale previous gate callbacks cannot hide active Return');
 let storageCopy=Array.from(storage);e=boot({storage:storageCopy,requiredTrusted:['required-1']});e.step();m=open(e);
 check(!body.find('nlQuizBack').hidden,'refresh required preparation retains Return before final render');
 m.options.onProgress({current:3,total:3});
 if(typeof m.options.onSuccessActionsReady==='function')m.options.onSuccessActionsReady(true);
 check(body.find('nlQuizBack').hidden,'refresh validated final render hides Return');
 e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();e.controls.reportFinalThenThrow=true;m=open(e);
 check(!body.find('nlQuizBack').hidden&&!body.find('nlQuizRetry').hidden&&body.find('nlQuizProgress').hidden,'outer mount failure after final progress restores required Return and Retry');
 e=boot({supportsPractice:false});e.step();m=open(e);m.options.onProgress({current:3,total:3});complete(e,m);
 check(!body.find('nlQuizBack').hidden,'adapter without lower practice action retains ordinary required Return');
 print(JSON.stringify({completed:true,checks,additionalFinalHeaderChecks:checks-startChecks,labels,limits:['Actual controller and shared renderer source parsed by system JavaScriptCore; DOM, adapter, storage, trusted answers, abort and loading/error events are declared doubles.','Native rendering, real engine answers, keyboard, focus and browser recovery are supplied separately.']}));
}


function readyHeaderCases(){
 const before=checks;
 let e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();let m=open(e);
 m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'R1 completed required retains Return while final image loading and lower actions unavailable');
 const notify=(mount,value)=>{if(typeof mount.options.onSuccessActionsReady==='function')mount.options.onSuccessActionsReady(value);};
 notify(m,false);check(!body.find('nlQuizBack').hidden,'explicit image loading retains required Return');
 notify(m,true);check(body.find('nlQuizBack').hidden,'actual ready final actions hide required Return');
 const required=clone(e.saved().states[0]);
 notify(m,false);check(!body.find('nlQuizBack').hidden,'image error restores required Return despite final progress and mastery');
 notify(m,false);check(!body.find('nlQuizBack').hidden,'image retry loading retains required Return');
 notify(m,true);check(body.find('nlQuizBack').hidden,'image retry success hides required Return again');
 for(const value of ['true',1,{},null]){notify(m,value);check(!body.find('nlQuizBack').hidden,'nonboolean readiness cannot hide Return '+JSON.stringify(value));}
 notify(m,true);m.options.onProgress(null);m.options.onProgress({current:3,total:3});
 check(!body.find('nlQuizBack').hidden,'null progress clears stale readiness before new final rendering');
 notify(m,true);check(body.find('nlQuizBack').hidden,'new explicit ready event restores completed header');
 const stale=m;body.find('nlQuizDialog').fire('cancel');m=open(e);m.options.onProgress({current:3,total:3});notify(m,true);notify(stale,false);
 check(body.find('nlQuizBack').hidden,'destroyed old readiness callback cannot reopen Return on current completed round');
 equal(e.saved().states[0],required,'readiness changes never mutate exact required receipt');
 m.options.onNewPractice();m=e.latest();notify(m,false);
 check(body.find('nlQuizBack').hidden&&!body.find('nlQuizPracticeContinue').hidden,'optional error retains independent Continue and hides Return');
 body.find('nlQuizDialog').fire('cancel');e.step(2);m=open(e);m.options.onProgress({current:3,total:3});notify(m,true);
 check(!body.find('nlQuizBack').hidden&&!e.C.isComplete(e.s,2),'ready actions cannot bypass missing required answers');
 e=boot({supportsPractice:false});e.step();m=open(e);m.options.onProgress({current:3,total:3});complete(e,m);notify(m,true);
 check(!body.find('nlQuizBack').hidden,'ready single-action adapter keeps ordinary Return');
 e=boot({requiredTrusted:['required-1']});e.seed({0:receipt()});e.step();e.controls.reportFinalThenThrow=true;open(e);
 check(!body.find('nlQuizBack').hidden&&!body.find('nlQuizRetry').hidden,'outer mount failure clears ready-final state and retains Return');
 print(JSON.stringify({completed:true,checks,newReadinessChecks:checks-before,labels,limits:['Actual controller source with explicit DOM/adapter/storage/trusted-answer/readiness doubles.','Real renderer and adapter readiness propagation checked separately; native delayed503/retry checks supplied separately.']}));
}


function optionalCompletedHeaderCases(){
 const start=checks;let e=boot();e.step();let m=open(e);complete(e,m);
 const required=clone(e.saved().states);
 m.options.onNewPractice();m=e.latest();
 check(m.optional&&!body.find('nlQuizPracticeContinue').hidden&&body.find('nlQuizBack').hidden,'optional new triple retains top Continue only');
 const ready=(mount,value)=>mount.options.onSuccessActionsReady(value);
 for(const [n,answers] of [[1,[true,false,false]],[2,[true,true,false]]]){
  m.options.onProgress({current:n,total:3});m.options.onStateChange(receipt(m.seed,answers,n-1));ready(m,false);
  check(!body.find('nlQuizPracticeContinue').hidden,'optional earlier round top Continue visible '+n);
 }
 m.options.onProgress({current:3,total:3});ready(m,false);
 check(!body.find('nlQuizPracticeContinue').hidden,'optional unanswered third retains top Continue');
 ready(m,true);
 check(!body.find('nlQuizPracticeContinue').hidden,'required mastery and claimed ready cannot hide Continue for incomplete optional receipt');
 m.options.onSolved({kind:'correct'},receipt(m.seed,[true,true,false]));
 check(!body.find('nlQuizPracticeContinue').hidden&&!e.saved().practices[0].solved,'claimed partial optional success cannot hide Continue');
 complete(e,m);
 check(body.find('nlQuizPracticeContinue').hidden&&e.saved().practices[0].solved,'verified ready optional third hides duplicate top Continue');
 equal(e.saved().states,required,'optional completion retains exact required receipt');
 ready(m,false);check(!body.find('nlQuizPracticeContinue').hidden,'optional image error restores independent top Continue');
 ready(m,false);check(!body.find('nlQuizPracticeContinue').hidden,'optional retry loading retains independent top Continue');
 ready(m,true);check(body.find('nlQuizPracticeContinue').hidden,'optional retry ready hides duplicate again');
 e.controls.optionalRestoreError=true;ready(m,true);
 check(!body.find('nlQuizPracticeContinue').hidden,'optional verification exception fails open to top Continue');
 e.controls.optionalRestoreError=false;ready(m,true);
 check(body.find('nlQuizPracticeContinue').hidden,'restored optional verification hides duplicate again');
 e.optionalTrusted.delete(m.seed);ready(m,true);
 check(!body.find('nlQuizPracticeContinue').hidden,'unavailable optional cache fails open despite original required mastery');
 e.optionalTrusted.add(m.seed);ready(m,true);
 check(body.find('nlQuizPracticeContinue').hidden,'trusted optional cache restores correct hidden header');
 const old=m;body.find('nlQuizDialog').fire('cancel');click('nlQuizPracticeOpen');m=e.latest();
 check(!body.find('nlQuizPracticeContinue').hidden,'completed optional reopen retains exit before rendered actions ready');
 m.options.onProgress({current:3,total:3});ready(m,true);
 check(body.find('nlQuizPracticeContinue').hidden,'completed optional reopen hides after verified ready actions');
 old.options.onSuccessActionsReady(false);
 check(body.find('nlQuizPracticeContinue').hidden,'closed stale callback cannot unhide active completed optional header');
 m.options.onNewPractice();m=e.latest();
 check(!body.find('nlQuizPracticeContinue').hidden&&m.options.initialState.currentRound===0,'another triple immediately restores top Continue');
 ready(old,true);m.options.onProgress({current:1,total:3});
 check(!body.find('nlQuizPracticeContinue').hidden,'old final readiness cannot hide new optional first-round Continue');
 m.options.onProgress({current:3,total:3});complete(e,m);
 check(body.find('nlQuizPracticeContinue').hidden,'second consecutive optional completion also hides duplicate');
 const snapshot=Array.from(storage),seed=m.seed;e=boot({storage:snapshot,requiredTrusted:['required-1'],optionalTrusted:[seed]});e.step();click('nlQuizPracticeOpen');m=e.latest();
 check(!body.find('nlQuizPracticeContinue').hidden,'refresh optional retains Continue while restoring');
 m.options.onProgress({current:3,total:3});ready(m,true);
 check(body.find('nlQuizPracticeContinue').hidden,'refresh completed optional hides after verified ready render');
 equal(e.saved().states,required,'refresh and repeat preserve exact required receipt');
 m.options.onNewPractice();m=e.latest();click('nlQuizPracticeContinue');
 check(navigation.at(-1)===1&&!body.find('nlQuizDialog').open,'available upper Continue still exits an unfinished optional triple');
 e.step(0);m=open(e);m.options.onProgress({current:3,total:3});ready(m,true);
 check(body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'required completed header behavior stays unchanged');
 body.find('nlQuizDialog').fire('cancel');e.step(2);m=open(e);m.options.onProgress({current:1,total:3});
 check(!body.find('nlQuizBack').hidden&&body.find('nlQuizPracticeContinue').hidden,'next unsolved required gate retains its Return');
 print(JSON.stringify({completed:true,checks,newOptionalHeaderChecks:checks-start,labels,limits:['Actual controller source; explicit DOM/adapter/trusted-answer/verification/readiness/storage doubles.','Native layout and generated answers tested separately; no full lesson or browser-freeze claim.']}));
}


function focusHeaderCases(){
 const start=checks;
 function setup(mode){
  const e=boot();e.step();let m=open(e);complete(e,m);m.options.onNewPractice();m=e.latest();m.options.onProgress({current:3,total:3});
  const upper=body.find('nlQuizPracticeContinue');let next=null;
  if(mode!=='missing'){
   const actions=new FakeNode('div');actions.className='round-next';next=new FakeNode('button');next.disabled=mode==='disabled';
   next.focus=function(){this.focusCalls++;if(mode!=='rejected')document.activeElement=this;};actions.append(next);m.host.append(actions);
  }
  document.activeElement=upper;return{e,m,upper,next};
 }
 let x=setup('ready');complete(x.e,x.m);
 check(x.next.focusCalls===1&&document.activeElement===x.next&&x.upper.hidden,'focused upper Continue transfers to enabled lower Continue before hiding');
 x.m.options.onSuccessActionsReady(true);
 check(x.next.focusCalls===1&&document.activeElement===x.next,'repeated readiness does not steal or repeat focus');
 for(const mode of ['missing','disabled','rejected']){
  x=setup(mode);complete(x.e,x.m);
  check(!x.upper.hidden&&document.activeElement===x.upper,'focus fallback retains upper Continue if lower transfer '+mode);
 }
 x=setup('ready');const natural=new FakeNode('h1');x.m.host.append(natural);document.activeElement=natural;complete(x.e,x.m);
 check(x.upper.hidden&&x.next.focusCalls===0&&document.activeElement===natural,'natural round heading focus preserved while duplicate hides');
 print(JSON.stringify({completed:true,checks,newFocusCases:checks-start,labels,limits:['Actual controller with declared DOM/adapter/state/cache/readiness doubles. Focus probe target simulates accepted/rejected HTMLElement.focus; native focus/scroll tested separately.','No renderer/adapter/core or native input assertion from these unit doubles.']}));
}
main().then(finalHeaderCases).then(readyHeaderCases).then(optionalCompletedHeaderCases).then(focusHeaderCases).catch(error=>{print('FAIL '+error.message+' '+error.stack);throw error;});
