const global = globalThis;
global.window = global;
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
      const continueButton = refs.next.querySelector("button");
      if (continueButton) continueButton.disabled = !diagramsReady() || !current.solved;
      refs.checkHelper.textContent = current.solved ? "Η επισκευή ολοκληρώθηκε. Συνέχισε όταν είσαι έτοιμος ή έτοιμη." : !diagramsReady() ? "Περιμένουμε να εμφανιστούν οι δομές πριν από τον έλεγχο." : data.kind === "order" ? "Επιλέγεις κλάδο, πατάς ένα βέλος και ελέγχεις τη νέα σειρά." : hasCandidate ? "Ο έλεγχος μετρά ως μία προσπάθεια. Μπορείς να δοκιμάσεις ξανά." : "Διάλεξε πρώτα το κομμάτι και έπειτα μια αντικατάσταση.";
      refs.sessionStats.textContent = "Προσπάθειες σε αυτή την " + (data.guided ? "πρόβα " : "αποστολή ") + current.attempts;
      if (restoreId) restoreFocus(restoreId);
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
        listen(dialog, "close", function () { dialog.remove(); zoomPanel = null; });
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
        refs.zoomButton.setAttribute("aria-expanded", "true");
        refs.zoomButton.disabled = true;
        root.append(dialog);
      }
      close.focus();
    }

    function closeZoom() {
      if (!zoomPanel) return;
      if (zoomImage) zoomImage.onerror = null;
      if (standalone) zoomPanel.close();
      else { replaceChildren(zoomPanel); zoomPanel.remove(); zoomPanel = null; }
      refs.zoomButton.setAttribute("aria-expanded", "false");
      refs.zoomButton.disabled = mainImageStatus !== "ready" || !!zoomPanel;
      refs.zoomButton.focus({ preventScroll: true });
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

const authoredData = {"schemaVersion": 2, "title": "Συνεργείο ονομάτων", "description": "Κάθε μόριο έφτασε με ένα λάθος στο όνομά του. Εντόπισε το μέρος που δεν συμφωνεί με τη δομή, επισκεύασέ το και κράτησε όσα είναι σωστά.", "sets": [{"id": "alkanes-unbranched", "title": "Χωρίς διακλαδώσεις", "description": "Σύνδεσε το μήκος της συνεχούς αλυσίδας και το είδος των δεσμών με τα συνθετικά του ονόματος.", "topics": ["Μήκος αλυσίδας", "Είδος δεσμών", "Σύνθεση ονόματος"], "rounds": [{"id": "unbranched-parent-four", "guided": false, "title": "Πόσο μήκος δείχνει η αλυσίδα;", "objective": "Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.", "moleculeId": "butane", "asset": "assets/name-repair/butane.svg", "diagramAlt": "Ανεπτυγμένος τύπος ευθείας αλυσίδας τεσσάρων ανθράκων με απλούς δεσμούς και χωρίς διακλαδώσεις.", "kind": "replace", "parts": [{"id": "root", "text": "προπ", "label": "Μήκος κύριας αλυσίδας"}, {"id": "saturation", "text": "άν", "label": "Είδος δεσμών"}, {"id": "ending", "text": "ιο", "label": "Χημική τάξη"}], "targetPartId": "root", "correctValue": "βουτ", "correctName": "βουτάνιο", "choices": [{"value": "αιθ", "label": "αιθ", "feedback": "Το «αιθ» δηλώνει δύο άνθρακες. Ακολούθησε όλη τη συνεχή αλυσίδα του σχεδίου."}, {"value": "βουτ", "label": "βουτ"}, {"value": "πεντ", "label": "πεντ", "feedback": "Το «πεντ» δηλώνει πέντε άνθρακες. Μέτρησε τους άνθρακες της αλυσίδας στο σχέδιο."}], "successText": "Η συνεχής ανθρακική αλυσίδα έχει τέσσερις άνθρακες, άρα το συνθετικό του μήκους της είναι «βουτ». Έτσι το σωστό όνομα είναι βουτάνιο.", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Διάλεξε αντικατάσταση για το λανθασμένο συνθετικό.", "incorrect": "Το συνθετικό δεν συμφωνεί με τη δομή. Παρατήρησε το μόριο και δοκίμασε ξανά."}}, {"id": "unbranched-single-bond", "guided": false, "title": "Τι δείχνει ο δεσμός;", "objective": "Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.", "moleculeId": "ethane", "asset": "assets/name-repair/ethane.svg", "diagramAlt": "Ανεπτυγμένος τύπος δύο ανθράκων που ενώνονται με έναν απλό δεσμό. Κάθε άνθρακας συνδέεται με τρία υδρογόνα.", "kind": "replace", "parts": [{"id": "root", "text": "αιθ", "label": "Μήκος κύριας αλυσίδας"}, {"id": "saturation", "text": "έν", "label": "Είδος δεσμών"}, {"id": "ending", "text": "ιο", "label": "Χημική τάξη"}], "targetPartId": "saturation", "correctValue": "άν", "correctName": "αιθάνιο", "choices": [{"value": "άν", "label": "άν"}, {"value": "έν", "label": "έν", "feedback": "Το «έν» δηλώνει διπλό δεσμό μεταξύ ανθράκων. Στο σχέδιο ο δεσμός μεταξύ των δύο ανθράκων είναι απλός."}, {"value": "ίν", "label": "ίν", "feedback": "Το «ίν» δηλώνει τριπλό δεσμό μεταξύ ανθράκων. Στο σχέδιο ο δεσμός μεταξύ των δύο ανθράκων είναι απλός."}], "successText": "Ο δεσμός ανάμεσα στους δύο άνθρακες είναι απλός, επομένως χρησιμοποιούμε το «άν». Με το «αιθ» για τους δύο άνθρακες, το όνομα είναι αιθάνιο.", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Διάλεξε αντικατάσταση για το λανθασμένο συνθετικό.", "incorrect": "Το συνθετικό δεν συμφωνεί με τη δομή. Παρατήρησε το μόριο και δοκίμασε ξανά."}}, {"id": "unbranched-parent-five", "guided": false, "title": "Μέτρησε τη συνεχή αλυσίδα", "objective": "Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.", "moleculeId": "pentane", "asset": "assets/name-repair/pentane.svg", "diagramAlt": "Ανεπτυγμένος τύπος ευθείας αλυσίδας πέντε ανθράκων με απλούς δεσμούς και χωρίς διακλαδώσεις.", "kind": "replace", "parts": [{"id": "root", "text": "εξ", "label": "Μήκος κύριας αλυσίδας"}, {"id": "saturation", "text": "άν", "label": "Είδος δεσμών"}, {"id": "ending", "text": "ιο", "label": "Χημική τάξη"}], "targetPartId": "root", "correctValue": "πεντ", "correctName": "πεντάνιο", "choices": [{"value": "προπ", "label": "προπ", "feedback": "Το «προπ» δηλώνει τρεις άνθρακες. Ακολούθησε όλη τη συνεχή αλυσίδα του σχεδίου."}, {"value": "βουτ", "label": "βουτ", "feedback": "Το «βουτ» δηλώνει τέσσερις άνθρακες. Μέτρησε και τους δύο ακραίους άνθρακες της αλυσίδας."}, {"value": "πεντ", "label": "πεντ"}], "successText": "Η συνεχής ανθρακική αλυσίδα έχει πέντε άνθρακες, άρα το συνθετικό του μήκους της είναι «πεντ». Έτσι το σωστό όνομα είναι πεντάνιο.", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Διάλεξε αντικατάσταση για το λανθασμένο συνθετικό.", "incorrect": "Το συνθετικό δεν συμφωνεί με τη δομή. Παρατήρησε το μόριο και δοκίμασε ξανά."}}]}, {"id": "alkanes-branched", "title": "Με διακλαδώσεις", "description": "Σύνδεσε τις θέσεις, το πλήθος και τη σειρά των διακλαδώσεων με τα κομμάτια του ονόματος.", "topics": ["Αρίθμηση", "Ίδιες διακλαδώσεις", "Αλφαβητική σειρά"], "rounds": [{"id": "number-from-nearest", "guided": false, "title": "Η αρίθμηση αλλάζει το όνομα", "objective": "Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.", "moleculeId": "methyl_2_pentane", "asset": "assets/name-repair/methyl_2_pentane.svg", "diagramAlt": "Αλυσίδα πέντε ανθράκων με μια μεθυλομάδα. Η θέση της μεθυλομάδας είναι 2 από το ένα άκρο και 4 από το άλλο.", "kind": "replace", "parts": [{"id": "locant", "text": "4-", "label": "Θέση διακλάδωσης"}, {"id": "branch", "text": "μεθυλο", "label": "Είδος διακλάδωσης"}, {"id": "root", "text": "πεντ", "label": "Μήκος κύριας αλυσίδας"}, {"id": "saturation", "text": "άν", "label": "Απλοί δεσμοί"}, {"id": "ending", "text": "ιο", "label": "Κατάληξη αλκανίου"}], "targetPartId": "locant", "correctValue": "2-", "correctName": "2-μεθυλοπεντάνιο", "choices": [{"value": "1-", "label": "1-", "feedback": "Στο άκρο της κύριας αλυσίδας δεν συνδέεται μεθυλομάδα. Η διακλάδωση συνδέεται στον επόμενο άνθρακα."}, {"value": "2-", "label": "2-"}, {"value": "3-", "label": "3-", "feedback": "Η μεθυλομάδα δεν συνδέεται στον μεσαίο άνθρακα. Ακολούθησε διαδοχικά την αλυσίδα από το πλησιέστερο άκρο."}], "successText": "Οι δύο φορές αρίθμησης δίνουν στη μεθυλομάδα τις θέσεις 2 και 4. Επιλέγουμε τη θέση 2, επειδή σε αυτό το αλκάνιο η μοναδική διακλάδωση πρέπει να πάρει τον μικρότερο αριθμό.", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Επίλεξε μια νέα θέση πριν ελέγξεις την επισκευή.", "incorrect": "Η θέση πρέπει να συμφωνεί με το σημείο σύνδεσης της διακλάδωσης και με τη σωστή φορά αρίθμησης."}}, {"id": "two-methyl-groups", "guided": false, "title": "Μία λέξη, δύο διακλαδώσεις", "objective": "Ένα συνθετικό δεν συμφωνεί με τη δομή. Επισκεύασέ το.", "moleculeId": "dimethyl_2_3_butane", "asset": "assets/name-repair/dimethyl_2_3_butane.svg", "diagramAlt": "Κύρια αλυσίδα τεσσάρων ανθράκων με δύο μεθυλομάδες, μία στον δεύτερο και μία στον τρίτο άνθρακα.", "kind": "replace", "parts": [{"id": "locants", "text": "2,3-", "label": "Θέσεις διακλαδώσεων"}, {"id": "branch", "text": "μεθυλο", "label": "Είδος και πλήθος διακλαδώσεων"}, {"id": "root", "text": "βουτ", "label": "Μήκος κύριας αλυσίδας"}, {"id": "saturation", "text": "άν", "label": "Απλοί δεσμοί"}, {"id": "ending", "text": "ιο", "label": "Κατάληξη αλκανίου"}], "targetPartId": "branch", "correctValue": "διμεθυλο", "correctName": "2,3-διμεθυλοβουτάνιο", "choices": [{"value": "αιθυλο", "label": "αιθυλο", "feedback": "Κάθε διακλάδωση εδώ έχει έναν άνθρακα. Μια αιθυλομάδα θα είχε δύο συνδεδεμένους άνθρακες στην ίδια διακλάδωση."}, {"value": "διμεθυλο", "label": "διμεθυλο"}, {"value": "τριμεθυλο", "label": "τριμεθυλο", "feedback": "Το «τρι-» δηλώνει τρεις ίδιες διακλαδώσεις. Στο σχέδιο υπάρχουν δύο μεθυλομάδες, στις θέσεις 2 και 3."}], "successText": "Στις θέσεις 2 και 3 υπάρχει από μία μεθυλομάδα. Επειδή οι διακλαδώσεις είναι δύο και ίδιες, χρησιμοποιούμε το «διμεθυλο». Η κύρια αλυσίδα έχει τέσσερις άνθρακες και δίνει το «βουτ».", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Διάλεξε συνθετικό που να περιγράφει και τις δύο διακλαδώσεις.", "incorrect": "Η επισκευή πρέπει να διατηρεί το είδος της διακλάδωσης και να δηλώνει το σωστό πλήθος της."}}, {"id": "alphabetical-branches", "guided": false, "title": "Τα σωστά κομμάτια, στη σωστή σειρά", "objective": "Οι ομάδες του ονόματος μπήκαν σε λάθος σειρά. Επίλεξε μια ομάδα και μετακίνησέ τη.", "moleculeId": "ethyl_3_dimethyl_2_5_hexane", "asset": "assets/name-repair/ethyl_3_dimethyl_2_5_hexane.svg", "diagramAlt": "Κύρια αλυσίδα έξι ανθράκων με μεθυλομάδες στις θέσεις δύο και πέντε και αιθυλομάδα στη θέση τρία. Η αιθυλομάδα έχει δύο συνδεδεμένους άνθρακες.", "kind": "order", "parts": [{"id": "methylGroup", "text": "2,5-διμεθυλο", "label": "Οι δύο μεθυλομάδες με τις θέσεις τους"}, {"id": "ethylGroup", "text": "3-αιθυλο", "label": "Η αιθυλομάδα με τη θέση της"}, {"id": "parent", "text": "εξάνιο", "label": "Η κύρια αλυσίδα"}], "movablePartIds": ["methylGroup", "ethylGroup"], "correctOrder": ["ethylGroup", "methylGroup"], "suffixPartId": "parent", "correctName": "3-αιθυλο-2,5-διμεθυλοεξάνιο", "successText": "Συγκρίνουμε αλφαβητικά τα «αιθυλο» και «μεθυλο», επομένως προηγείται το «αιθυλο». Το «δι-» και οι αριθμοί θέσης δεν καθορίζουν αυτή τη σειρά. Κάθε ομάδα κρατά τις δικές της θέσεις όταν μετακινείται.", "feedback": {"wrongPart": "Αυτό το συνθετικό συμφωνεί με τη δομή.", "unchanged": "Μετακίνησε μια ομάδα για να αλλάξει η σειρά των διακλαδώσεων.", "incorrect": "Σύγκρινε τις λέξεις «αιθυλο» και «μεθυλο». Ο αριθμός θέσης και το «δι-» δεν αποφασίζουν ποια προηγείται."}}]}]};

let checks = 0;
const labels = [];
function check(ok, label) { if (!ok) throw Error(label); checks++; labels.push(label); }
function equal(a, b, label) { check(JSON.stringify(a) === JSON.stringify(b), label); }
function clone(v) { return JSON.parse(JSON.stringify(v)); }
function freeze(v) { if (v && typeof v === 'object') { Object.values(v).forEach(freeze); Object.freeze(v); } return v; }
let focusCalls = 0, storageCalls = 0;
for (const key of ['localStorage', 'sessionStorage']) global[key] = {
  getItem() { storageCalls++; throw Error('unexpected storage read'); },
  setItem() { storageCalls++; throw Error('unexpected storage write'); },
  removeItem() { storageCalls++; throw Error('unexpected storage delete'); }
};
const E = NameleculeRepairEngine, G = NameleculeRepairGame;
check(typeof document === 'undefined' && typeof G.presentationForRound === 'function' && typeof G.createResponseRevealer === 'function',
  'actual exports load with document undefined');
const authored = freeze(authoredData.sets.flatMap(set => set.rounds));
const expectedMissions = {
  'unbranched-parent-four': 'parent-length', 'unbranched-parent-five': 'parent-length',
  'unbranched-single-bond': 'bond-type', 'number-from-nearest': 'branch-locants',
  'two-methyl-groups': 'branch-multiplier', 'alphabetical-branches': 'alphabetical-order'
};
const expectedObjectives = {
  'parent-length': 'Έλεγξε το μήκος της κύριας αλυσίδας και το συνθετικό που το δηλώνει.',
  'bond-type': 'Έλεγξε το είδος των δεσμών μεταξύ ατόμων C.',
  'branch-locants': 'Έλεγξε τα σημεία σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
  'branch-multiplier': 'Έλεγξε πόσες ίδιες διακλαδώσεις υπάρχουν και πώς δηλώνεται το πλήθος τους.',
  'alphabetical-order': 'Έλεγξε την αλφαβητική σειρά των διαφορετικών διακλαδώσεων.'
};
const expectedReminders = {
  'parent-length': 'Η αποστολή αφορά το πλήθος των ατόμων C της κύριας αλυσίδας.',
  'bond-type': 'Η αποστολή αφορά το είδος των δεσμών μεταξύ ατόμων C.',
  'branch-locants': 'Η αποστολή αφορά τις θέσεις σύνδεσης των διακλαδώσεων και τη φορά αρίθμησης.',
  'branch-multiplier': 'Η αποστολή αφορά το πλήθος των ίδιων διακλαδώσεων.'
};
function solution(round) {
  const state = E.createRoundState(round);
  if (round.kind === 'replace') { state.selectedPartId = round.targetPartId; state.selectedValue = round.correctValue; }
  else state.order = round.correctOrder.slice();
  return state;
}
for (const original of authored) {
  const prefix = original.id + ': ', snapshot = JSON.stringify(original);
  const preset = G.presentationForRound(original, {difficulty: 'basic'}), shown = preset.round;
  check(shown !== original && preset.emphasizeObjective && preset.compactDiagramZoom, prefix + 'shared prominent objective and compact zoom flags');
  check(shown.objective === expectedObjectives[expectedMissions[original.id]] && shown.objective !== original.objective,
    prefix + 'authored basic mission objective is explicit');
  const reminder = expectedReminders[expectedMissions[original.id]];
  check(shown.feedback.wrongPart === original.feedback.wrongPart + (original.kind === 'replace' && reminder ? ' ' + reminder : ''),
    prefix + 'wrong-part feedback adds only approved non-answer mission reminder');
  equal(E.evaluateRepair(original, solution(original)), E.evaluateRepair(shown, solution(shown)), prefix + 'exact correct evaluation and success text unchanged');
  check(E.evaluateRepair(shown, solution(shown)).kind === 'correct' && E.candidateName(shown, solution(shown)) === original.correctName,
    prefix + 'correct repair still assembles canonical correct name');
  equal(E.evaluateRepair(original, E.createRoundState(original)), E.evaluateRepair(shown, E.createRoundState(shown)),
    prefix + 'initial/incomplete evaluation unchanged');
  if (original.kind === 'replace') {
    const selections = original.choices.map(choice => {
      const s = E.createRoundState(original); s.selectedPartId = original.targetPartId; s.selectedValue = choice.value; return s;
    });
    equal(selections.map(s => E.evaluateRepair(original, s)), selections.map(s => E.evaluateRepair(shown, s)),
      prefix + 'every authored replacement choice evaluation unchanged');
  } else {
    const wrong = E.createRoundState(original); wrong.order.reverse();
    equal(E.evaluateRepair(original, wrong), E.evaluateRepair(shown, wrong), prefix + 'reordered evaluation unchanged');
  }
  const restored = clone(shown);
  restored.objective = original.objective; restored.asset = original.asset; restored.diagramAlt = original.diagramAlt;
  restored.feedback = clone(original.feedback);
  equal(restored, original, prefix + 'all canonical non-display fields unchanged');
  equal(G.presentationForRound(shown, {difficulty:'basic'}), preset, prefix + 'presentation and reminder are idempotent');
  const challenge = G.presentationForRound(original, {difficulty:'challenge'}).round;
  check(challenge.objective === original.objective && challenge.feedback === original.feedback,
    prefix + 'challenge preserves original objective and neutral wrong-part feedback');
  equal(original, JSON.parse(snapshot), prefix + 'frozen canonical input remains byte-equivalent');
}
check(authored.length === 6, 'all six canonical authored questions tested');
for (const [family, reminder] of Object.entries(expectedReminders)) {
  const generated = clone(authored[0]);
  generated.id = 'generated-variable-id-' + family; generated.fault = {kind:family};
  generated.objective = 'Βρες και διόρθωσε το μέρος που διαφωνεί με τη δομή.';
  const snapshot = JSON.stringify(generated); freeze(generated);
  const shown = G.presentationForRound(generated, {difficulty:'basic'}).round;
  check(shown.objective === generated.objective && shown.feedback.wrongPart === generated.feedback.wrongPart + ' ' + reminder,
    family + ': generated semantic fault metadata controls reminder independently of authored ID');
  equal(G.presentationForRound(generated).round, shown, family + ': omitted options use basic presentation');
  equal(G.presentationForRound(generated, {difficulty:'challenge'}).round, generated,
    family + ': generated challenge objective/feedback remain neutral');
  equal(G.presentationForRound(shown, {difficulty:'basic'}).round, shown, family + ': generated reminder idempotent');
  check(JSON.stringify(generated) === snapshot, family + ': generated canonical input unchanged');
}
for (const id of ['future-question', '__proto__', 'constructor', 'toString']) {
  const unknown = clone(authored[0]); unknown.id = id;
  equal(G.presentationForRound(freeze(unknown), {difficulty:'basic'}).round, unknown, id + ': unknown/prototype-like ID cannot invent a mission');
  for (const family of ['future-family', '__proto__', 'constructor']) {
    const unknownFamily = clone(unknown); unknownFamily.fault = {kind:family};
    equal(G.presentationForRound(freeze(unknownFamily), {difficulty:'basic'}).round, unknownFamily,
      id + '/' + family + ': unsupported metadata cannot invent a mission');
  }
}
const orderWithMetadata = clone(authored[5]); orderWithMetadata.id = 'generated-order'; orderWithMetadata.fault = {kind:'parent-length'};
equal(G.presentationForRound(freeze(orderWithMetadata)).round.feedback, orderWithMetadata.feedback, 'order presentation does not append replacement-only reminder');
const largest = G.presentationForRound(authored[5]);
check(largest.diagramRepresentation === 'condensed' && largest.round.asset === 'assets/name-repair/condensed/ethyl_3_dimethyl_2_5_hexane.svg',
  'exact existing largest-molecule condensed asset selected');
check(largest.round.diagramAlt === 'Συνεπτυγμένος συντακτικός τύπος αλκανίου. Φαίνονται οι δεσμοί μεταξύ ατόμων C και οι ομάδες CH₃, CH₂ και CH.',
  'condensed alt names representation without numerical/name solution');
for (const round of authored.slice(0, 5)) {
  const p = G.presentationForRound(round);
  check(p.diagramRepresentation === 'expanded' && p.round.asset === round.asset && p.round.diagramAlt === round.diagramAlt,
    round.id + ': ordinary molecule asset/alt/expanded representation preserved');
}
const arbitraryLarge = clone(authored[0]); arbitraryLarge.id = 'new-largest-round'; arbitraryLarge.moleculeId = authored[5].moleculeId;
check(G.presentationForRound(arbitraryLarge).diagramRepresentation === 'condensed', 'largest representation depends on molecule, not question ID/kind');

function fixture(config = {}) {
  let current = config.current || 0, maximum = config.maximum === undefined ? 2400 : config.maximum;
  let active = true, reduced = !!config.reduced;
  const calls = [], entries = [], removals = [], handlers = new Map(), nodes = new Set();
  const target = {
    addEventListener(type, handler, options) { entries.push({type,handler,options}); handlers.set(type,handler); },
    removeEventListener(type, handler, options) {
      removals.push({type,handler,options});
      if (handlers.get(type) === handler) handlers.delete(type);
    },
    emit(type) { const callback = handlers.get(type); if (callback) callback({type}); }
  };
  const host = { contains(node) { return nodes.has(node); } };
  const viewport = {top:12,bottom:588};
  global.matchMedia = query => ({matches: query === '(prefers-reduced-motion: reduce)' && reduced});
  const options = {
    host, active:() => active, interruptTarget:target,
    viewport:() => viewport, scrollTop:() => current, maxScroll:() => maximum,
    scrollTo(destination, behavior) { calls.push({destination,behavior}); current = destination; }
  };
  const api = G.createResponseRevealer(options);
  function node(y, height=50) {
    const result = {isConnected:true, focus() { focusCalls++; },
      getBoundingClientRect() { return {top:y-current,bottom:y+height-current,height}; }};
    nodes.add(result); return result;
  }
  return {api,calls,target,entries,removals,handlers,nodes,viewport,node,
    y:() => current, setY:y => {current=y;}, setMax:y => {maximum=y;},
    setActive:v => {active=v;}, setReduced:v => {reduced=v;}};
}
function request(f, start, end) { f.api.reveal({start,end:end || start,reason:'pure-page-response'}); }
{
  const f = fixture(), visible = f.node(200);
  request(f,visible); check(f.calls.length === 0 && f.y() === 0, 'page: already-visible response is a no-op');
  check(f.entries.map(e=>e.type).join(',') === 'wheel,touchstart,pointerdown,keydown,pagehide' && f.entries.every(e=>e.options.passive === true),
    'page: exactly five passive manual-interruption listeners installed');
  f.api.destroy();
}
{
  const f=fixture(), low=f.node(700); request(f,low);
  equal(f.calls,[{destination:162,behavior:'smooth'}], 'page: short below response moves only enough to show its bottom');
  check(low.getBoundingClientRect().top >= 12 && low.getBoundingClientRect().bottom === 588, 'page: short below range fully fits viewport');
  request(f,low); equal(f.calls.at(-1),{destination:162,behavior:'instant'}, 'page: next visible request cancels prior motion without new smooth jump');
  const n=f.calls.length;request(f,low);check(f.calls.length===n,'page: repeated visible request after cancellation writes nothing');f.api.destroy();
}
{
  const f=fixture({current:500}), high=f.node(200);request(f,high);
  check(f.y()===188 && high.getBoundingClientRect().top===12 && high.getBoundingClientRect().bottom<=588,
    'page: response above viewport aligns its start and fits');f.api.destroy();
}
{
  const f=fixture(), start=f.node(700,30), end=f.node(820,40);request(f,start,end);
  check(f.y()===272 && start.getBoundingClientRect().top>=12 && end.getBoundingClientRect().bottom===588,
    'page: short response through following action fits as one measured range');f.api.destroy();
}
{
  const f=fixture(), tall=f.node(800,1000);request(f,tall);
  check(f.y()===788 && tall.getBoundingClientRect().top===12, 'page: tall explanation reveals its start rather than skipping to end');f.api.destroy();
}
{
  const f=fixture({maximum:100});request(f,f.node(5000));check(f.y()===100,'page: destination clamps to measured lower scroll extent');f.api.destroy();
  const top=fixture({current:10});request(top,top.node(0));check(top.y()===0,'page: destination clamps to zero');top.api.destroy();
  const tiny=fixture({maximum:.5});request(tiny,tiny.node(800));check(tiny.calls.length===0,'page: subpixel-only destination does not write');tiny.api.destroy();
}
{
  const f=fixture({reduced:true});request(f,f.node(800));
  equal(f.calls,[{destination:262,behavior:'instant'}], 'page: reduced motion uses immediate measured destination');
  const n=f.calls.length;f.target.emit('pointerdown');f.api.stop();check(f.calls.length===n,'page: no pending animation to cancel after reduced-motion reveal');f.api.destroy();
}
for (const failure of ['inactive','missing','disconnected-start','disconnected-end','outside-start','outside-end','hidden-start','hidden-end','nonfinite-start','nonfinite-end','nonfinite-viewport','invalid-viewport','nonfinite-extent','nonfinite-current','missing-rect']) {
  const f=fixture(), start=f.node(800), end=f.node(950);
  if(failure==='inactive')f.setActive(false);
  if(failure==='disconnected-start')start.isConnected=false;
  if(failure==='disconnected-end')end.isConnected=false;
  if(failure==='outside-start')f.nodes.delete(start);
  if(failure==='outside-end')f.nodes.delete(end);
  if(failure==='hidden-start')start.getBoundingClientRect=()=>({top:800,bottom:800,height:0});
  if(failure==='hidden-end')end.getBoundingClientRect=()=>({top:950,bottom:950,height:0});
  if(failure==='nonfinite-start')start.getBoundingClientRect=()=>({top:NaN,bottom:NaN,height:NaN});
  if(failure==='nonfinite-end')end.getBoundingClientRect=()=>({top:Infinity,bottom:Infinity,height:NaN});
  if(failure==='nonfinite-viewport')f.viewport.top=NaN;
  if(failure==='invalid-viewport')f.viewport.bottom=f.viewport.top;
  if(failure==='nonfinite-extent')f.setMax(NaN);
  if(failure==='nonfinite-current')f.setY(NaN);
  if(failure==='missing-rect')start.getBoundingClientRect=undefined;
  if(failure==='missing'){f.api.reveal(null);f.api.reveal({});}else request(f,start,end);
  check(f.calls.length===0,'page: rejects '+failure+' request');f.api.destroy();
}
for (const event of ['wheel','touchstart','pointerdown','keydown','pagehide']) {
  const f=fixture();f.target.emit(event);check(f.calls.length===0,event+': idle interruption writes nothing');
  request(f,f.node(900));const y=f.y();f.target.emit(event);
  equal(f.calls,[{destination:362,behavior:'smooth'},{destination:y,behavior:'instant'}],event+': pending motion cancelled at current position');
  f.target.emit(event);check(f.calls.length===2,event+': repeated interruption does not cancel twice');f.api.destroy();
}
{
  const f=fixture(), low=f.node(1000);request(f,low);const y=f.y();f.api.destroy();
  equal(f.calls.at(-1),{destination:y,behavior:'instant'},'page: destroy cancels pending motion');
  check(f.removals.length===5&&f.handlers.size===0&&f.removals.every((entry,i)=>entry.type===f.entries[i].type&&entry.handler===f.entries[i].handler&&entry.options===f.entries[i].options),
    'page: destroy removes all five listeners with matching handler/options');
  const n=f.calls.length;f.api.reveal({start:f.node(2000)});f.api.stop();f.api.destroy();f.target.emit('pointerdown');
  check(f.calls.length===n&&f.removals.length===5,'page: destroyed helper ignores later reveal/stop/events and repeat destroy');
}
check(focusCalls===0&&storageCalls===0,'pure presentation/reveal helpers produce no focus or storage side effects');
print(JSON.stringify({completed:true,checks,authoredRounds:authored.length,labels,
  limits:['Actual frozen NameleculeRepairGame exports and canonical authored data execute in system JavaScriptCore with document undefined.',
    'Page viewport, element rectangles, connected/containment state, event target, matchMedia and scrollTo are declared doubles.',
    'Synthetic scrollTo applies destinations synchronously; no native animation, browser layout, rendering or interaction claim.']}));
