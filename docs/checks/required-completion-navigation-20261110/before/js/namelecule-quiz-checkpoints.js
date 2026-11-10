/* Namelecule lesson checkpoints. Authored questions are separate from tab progress. */
(function (global) {
  "use strict";
  const types = Object.create(null);
  const records = new Map();
  let preview = null; // Editor rehearsal only; never a stored learner receipt.
  const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  const clone = value => JSON.parse(JSON.stringify(value));
  const storagePrefix = "namelecule:lesson-checkpoints:v1:";
  let active = null;
  let dialog = null;
  let mountHost = null;
  let retryButton = null;
  let progressCounter = null;
  let mounted = null;
  let mountToken = 0;
  let responseRevealer = null;
  let practiceContinue = null;
  let practiceNotice = null;

  function supportsPractice(adapter) {
    return ["createPractice", "restorePractice", "mountPractice"].every(key => typeof adapter[key] === "function");
  }

  function registerType(name, adapter) {
    if (!/^[a-z][a-z0-9-]{0,48}$/.test(name) || own(types, name) || !adapter ||
        ["validate", "restore", "mount"].some(key => typeof adapter[key] !== "function")) {
      throw new Error("Invalid checkpoint type registration");
    }
    types[name] = adapter;
  }

  registerType("name-repair", {
    validate(round) {
      const engine = global.NameleculeRepairEngine;
      if (!engine || typeof engine.validateRoundData !== "function") throw new Error("Repair engine unavailable");
      return engine.validateRoundData(round);
    },
    restore(round, state) {
      const engine = global.NameleculeRepairEngine;
      if (!engine || typeof engine.restoreRoundState !== "function") throw new Error("Repair restoration unavailable");
      return engine.restoreRoundState(round, state);
    },
    mount(host, options) {
      if (!global.NameleculeRepairGame || typeof global.NameleculeRepairGame.mountRound !== "function") {
        throw new Error("Repair interface unavailable");
      }
      return global.NameleculeRepairGame.mountRound(host, options);
    }
  });

  function validateCheckpoint(spec) {
    if (!spec || typeof spec !== "object" || Array.isArray(spec) || spec.version !== 1 ||
        typeof spec.id !== "string" || !/^[a-z][a-z0-9-]{0,80}$/.test(spec.id) ||
        typeof spec.type !== "string" || !own(types, spec.type)) {
      throw new Error("Unknown or invalid required checkpoint");
    }
    const value = clone(spec);
    if (own(value, "openLabel")) {
      const label = typeof value.openLabel === "string" ? value.openLabel.trim() : "";
      if (label && label.length <= 100) value.openLabel = label;
      else delete value.openLabel;
    }
    types[value.type].validate(value.round);
    return value;
  }

  function hasCheckpoints(scenario) {
    return !!(scenario && Array.isArray(scenario.steps) && scenario.steps.some(step => step && own(step, "checkpoint")));
  }

  function signature(scenario) {
    // No runtime card ID, current index or auto-generated creation timestamp:
    // reloading an identical authored lesson keeps the same tab progress.
    return JSON.stringify({ version: 1, title: String(scenario.title || ""),
      author: String(scenario.author || "Unknown"), steps: scenario.steps });
  }

  function hash(text) {
    let value = 2166136261;
    for (let index = 0; index < text.length; index++) value = Math.imul(value ^ text.charCodeAt(index), 16777619);
    return (value >>> 0).toString(16);
  }

  function recordFor(scenario) {
    const content = signature(scenario);
    if (isPreview(scenario)) return preview.record;
    if (records.has(content)) return records.get(content);
    const key = storagePrefix + hash(content);
    let states = Object.create(null);
    let practices = Object.create(null);
    let storageAvailable = true;
    try {
      const saved = JSON.parse(global.sessionStorage.getItem(key) || "null");
      // Compare the whole content as well as its short storage key. A hash
      // collision or edited/reordered question cannot reuse another receipt.
      if (saved && saved.version === 1 && saved.content === content && saved.states && typeof saved.states === "object") {
        for (let index = 0; index < scenario.steps.length; index++) {
          const step = scenario.steps[index];
          if (step && own(step, "checkpoint") && own(saved.states, index)) {
            try {
              const spec = validateCheckpoint(step.checkpoint);
              states[index] = types[spec.type].restore(spec.round, saved.states[index]);
              if (supportsPractice(types[spec.type]) && saved.practices && own(saved.practices, index)) {
                try { practices[index] = types[spec.type].restorePractice(spec.round, saved.practices[index]); }
                catch (_) { /* Optional progress cannot invalidate an earned required receipt. */ }
              }
            } catch (_) { /* Invalid stored progress never unlocks a checkpoint. */ }
          }
        }
      }
    } catch (_) { storageAvailable = false; }
    const result = { key, content, states, practices, storageAvailable };
    records.set(content, result);
    return result;
  }

  function persist(record) {
    if (record.temporary) return;
    try {
      global.sessionStorage.setItem(record.key, JSON.stringify({ version: 1, content: record.content, states: record.states, practices: record.practices }));
      record.storageAvailable = true;
    } catch (_) { record.storageAvailable = false; }
  }

  function isComplete(scenario, index) {
    const step = scenario && scenario.steps && scenario.steps[index];
    if (!step || !own(step, "checkpoint")) return true;
    try {
      const spec = validateCheckpoint(step.checkpoint);
      const state = types[spec.type].restore(spec.round, recordFor(scenario).states[index]);
      return state.solved === true;
    } catch (_) { return false; }
  }

  function resolveTarget(scenario, requested) {
    if (!scenario || !Array.isArray(scenario.steps) || !scenario.steps.length) return 0;
    const number = Number(requested);
    const target = Math.max(0, Math.min(scenario.steps.length - 1, Number.isFinite(number) ? Math.floor(number) : 0));
    for (let index = 0; index < target; index++) {
      if (own(scenario.steps[index] || {}, "checkpoint") && !isComplete(scenario, index)) return index;
    }
    return target;
  }

  // Existing authored checkpoints remain synchronous. An adapter may need the
  // engine to reconstruct a saved generated set before navigation can trust it.
  function prepareTarget(scenario, requested, options) {
    if (!scenario || !Array.isArray(scenario.steps)) return null;
    const number = Number(requested);
    const target = Math.max(0, Math.min(scenario.steps.length - 1, Number.isFinite(number) ? Math.floor(number) : 0));
    const record = recordFor(scenario);
    const content = record.content;
    const signal = options && options.signal;
    function checkCurrent() {
      if ((signal && signal.aborted) || signature(scenario) !== content) {
        const error = new Error("Checkpoint preparation cancelled");
        error.name = "AbortError";
        throw error;
      }
    }
    function scan(start) {
      checkCurrent();
      for (let index = start; index < target; index++) {
        const step = scenario.steps[index];
        if (!step || !own(step, "checkpoint")) continue;
        const spec = validateCheckpoint(step.checkpoint);
        const adapter = types[spec.type];
        const saved = record.states[index];
        if (saved && typeof adapter.prepare === "function") {
          const savedContent = JSON.stringify(saved);
          const pending = adapter.prepare(spec.round, saved, { signal });
          if (pending && typeof pending.then === "function") {
            return Promise.resolve(pending).then(state => {
              checkCurrent();
              if (JSON.stringify(record.states[index]) !== savedContent) {
                const error = new Error("Checkpoint progress changed during preparation");
                error.name = "AbortError";
                throw error;
              }
              record.states[index] = adapter.restore(spec.round, state);
              persist(record);
              return isComplete(scenario, index) ? scan(index + 1) : null;
            });
          }
        }
        if (!isComplete(scenario, index)) return null;
      }
      return null;
    }
    return scan(0);
  }

  const words = {
    gr: { label: "Μικρή στάση για επισκευή", counter: "Κουίζ", instruction: "Επισκεύασε το όνομα για να συνεχίσεις τη θεωρία.",
      open: "Στο Συνεργείο ονομάτων", done: "Η επισκευή ολοκληρώθηκε. Μπορείς να συνεχίσεις.", revisit: "Δες ξανά την επισκευή",
      back: "Επιστροφή στη θεωρία", retry: "Φόρτωσε ξανά την αποστολή", error: "Η αποστολή δεν φορτώθηκε. Δοκίμασε ξανά ή επέστρεψε στη θεωρία.",
      storage: "Η πρόοδος κρατιέται μόνο όσο μένει ανοιχτή αυτή η σελίδα· η αποθήκευση της καρτέλας δεν είναι διαθέσιμη.",
      reset: "Νέα προσπάθεια", resetLabel: "Ξεκίνα την επισκευή από την αρχή" },
    en: { label: "A short repair stop", counter: "Quiz", instruction: "Repair the name to continue the lesson.",
      open: "Open the name workshop", done: "Repair completed. You can continue.", revisit: "Review the repair",
      back: "Return to the lesson", retry: "Reload the mission", error: "The mission could not load. Retry or return to the lesson.",
      storage: "Progress is kept only while this page remains open; tab storage is unavailable.",
      reset: "New attempt", resetLabel: "Start this repair again" }
  };
  Object.assign(words.gr, {
    practice: "Άλλη τριάδα για εξάσκηση", resumePractice: "Συνέχισε την εξάσκηση",
    practiceTitle: "Προαιρετική εξάσκηση", continueLesson: "Συνεχίζω τη θεωρία",
    practiceNote: "Η αρχική τριάδα ολοκληρώθηκε. Μπορείς να συνεχίσεις τη θεωρία οποιαδήποτε στιγμή.",
    preparing: "Επαληθεύεται η αποθηκευμένη πρόοδός σου…"
  });
  Object.assign(words.en, {
    practice: "Another three for practice", resumePractice: "Resume practice",
    practiceTitle: "Optional practice", continueLesson: "Continue the lesson",
    practiceNote: "The required set is complete. You can continue the lesson at any time.",
    preparing: "Checking your saved progress…"
  });
  function text(key) {
    let lang = "gr";
    try { if (typeof global.fMulerLang === "function" && global.fMulerLang() === "en") lang = "en"; } catch (_) {}
    return words[lang][key];
  }
  function node(tag, className, value) {
    const element = global.document.createElement(tag);
    if (className) element.className = className;
    if (value) element.textContent = value;
    return element;
  }
  function button(label, className, action) {
    const element = node("button", className, label);
    element.type = "button";
    element.addEventListener("click", action);
    return element;
  }

  function validProgress(value) {
    return !!(value && Number.isSafeInteger(value.current) && Number.isSafeInteger(value.total) &&
      value.current >= 1 && value.current <= value.total);
  }
  function showProgress(value) {
    if (!progressCounter) return;
    const valid = validProgress(value);
    progressCounter.hidden = !valid;
    progressCounter.textContent = valid ? text("counter") + " " + value.current + "/" + value.total : "";
  }
  function stopResponseScroll() {
    if (responseRevealer) responseRevealer.stop();
  }
  function revealResponse(request) {
    if (responseRevealer) responseRevealer.reveal(request);
  }
  function destroyMount() {
    stopResponseScroll();
    mountToken++;
    showProgress(null);
    const previous = mounted;
    mounted = null;
    if (previous && typeof previous.destroy === "function") previous.destroy();
    if (mountHost) mountHost.replaceChildren();
  }
  function closeDialog() {
    destroyMount();
    if (dialog && dialog.open) dialog.close();
    if (active && active.openButton && active.openButton.isConnected) active.openButton.focus({ preventScroll: true });
  }
  function ensureDialog() {
    if (dialog) return;
    dialog = node("dialog", "nl-quiz-dialog");
    dialog.id = "nlQuizDialog";
    dialog.setAttribute("aria-labelledby", "nlQuizDialogTitle");
    const header = node("div", "nl-quiz-dialog-header");
    const title = node("h2", "nl-quiz-dialog-title");
    title.id = "nlQuizDialogTitle";
    const back = button("", "nl-quiz-button nl-quiz-back", closeDialog);
    back.id = "nlQuizBack";
    practiceContinue = button("", "nl-quiz-button nl-quiz-practice-continue", () => { if (active) continueLesson(active); });
    practiceContinue.id = "nlQuizPracticeContinue";
    practiceContinue.hidden = true;
    practiceNotice = node("p", "nl-quiz-practice-notice");
    practiceNotice.id = "nlQuizPracticeNotice";
    practiceNotice.hidden = true;
    const copy = node("div", "nl-quiz-dialog-copy");
    copy.append(title, practiceNotice);
    const actions = node("div", "nl-quiz-dialog-actions");
    progressCounter = node("span", "nl-quiz-round-progress");
    progressCounter.id = "nlQuizProgress";
    progressCounter.hidden = true;
    progressCounter.setAttribute("role", "status");
    progressCounter.setAttribute("aria-live", "polite");
    progressCounter.setAttribute("aria-atomic", "true");
    actions.append(progressCounter, practiceContinue, back);
    header.append(copy, actions);
    mountHost = node("div", "nl-quiz-host");
    mountHost.id = "nlQuizHost";
    retryButton = button("", "nl-quiz-button nl-quiz-retry", () => { if (active) mountQuestion(active); });
    retryButton.id = "nlQuizRetry";
    retryButton.hidden = true;
    mountHost.addEventListener("error", event => {
      if (dialog.open && event.target && event.target.tagName === "IMG") retryButton.hidden = false;
    }, true);
    dialog.append(header, mountHost, retryButton);
    responseRevealer = global.NameleculeRepairGame.createResponseRevealer({
      host: mountHost,
      active: () => !!(dialog && dialog.open),
      viewport() {
        const box = dialog.getBoundingClientRect();
        return { top: Math.max(box.top + dialog.clientTop, header.getBoundingClientRect().bottom) + 12,
          bottom: box.top + dialog.clientTop + dialog.clientHeight - 12 };
      },
      scrollTop: () => dialog.scrollTop,
      maxScroll: () => dialog.scrollHeight - dialog.clientHeight,
      scrollTo(top, behavior) {
        if (typeof dialog.scrollTo === "function") dialog.scrollTo({ top: top, behavior: behavior });
        else dialog.scrollTop = top;
      }
    });
    dialog.addEventListener("cancel", event => { event.preventDefault(); closeDialog(); });
    // Let the round handle its own keys first, then stop lesson arrows/Escape.
    dialog.addEventListener("keydown", event => { stopResponseScroll(); event.stopPropagation(); });
    dialog.addEventListener("wheel", stopResponseScroll, { passive: true });
    dialog.addEventListener("touchstart", stopResponseScroll, { passive: true });
    dialog.addEventListener("pointerdown", stopResponseScroll, { passive: true });
    dialog.addEventListener("close", () => { if (!dialog.open) destroyMount(); });
    global.document.body.append(dialog);
  }

  function currentContext(context) {
    if (active !== context) return false;
    try {
      const state = global.MuLERMoCScenario;
      return !!(state && state.present && typeof global.fScenarioPresent === "function" &&
        global.fScenarioPresent() === context.scenario && context.scenario.index === context.index &&
        signature(context.scenario) === context.record.content);
    } catch (_) { return false; }
  }
  function refreshCard(context) {
    if (active !== context) return;
    const done = isComplete(context.scenario, context.index);
    context.status.textContent = text(context.preparing ? "preparing" : done ? "done" : "instruction");
    context.openButton.disabled = !!context.preparing;
    context.openButton.textContent = done ? text("revisit") : (context.spec.openLabel || text("open"));
    context.section.classList.toggle("nl-quiz-complete", done);
    context.practiceButton.hidden = !done || !supportsPractice(types[context.spec.type]);
    context.practiceButton.textContent = text(context.record.practices[context.index] ? "resumePractice" : "practice");
    context.storageNote.textContent = context.record.storageAvailable ? "" : text("storage");
    context.storageNote.hidden = context.record.storageAvailable;
  }
  function updateNavigation(context) {
    refreshCard(context);
    if (typeof global.fScenarioPlayUi === "function") global.fScenarioPlayUi();
  }
  function continueLesson(context) {
    if (!currentContext(context) || !isComplete(context.scenario, context.index)) return;
    const destination = context.index + 1;
    closeDialog();
    if (typeof global.fScenarioGo === "function") global.fScenarioGo(destination);
  }
  function updateDialog(context) {
    dialog.querySelector("#nlQuizDialogTitle").textContent = text(context.practice ? "practiceTitle" : "label");
    dialog.querySelector("#nlQuizBack").hidden = context.practice;
    practiceNotice.textContent = text("practiceNote");
    practiceNotice.hidden = !context.practice;
    practiceContinue.textContent = text("continueLesson");
    practiceContinue.hidden = !context.practice;
  }
  function newPractice(context) {
    const adapter = types[context.spec.type];
    if (!currentContext(context) || !supportsPractice(adapter) || !isComplete(context.scenario, context.index)) return;
    context.record.practices[context.index] = adapter.createPractice(context.spec.round,
      context.record.practices[context.index] || context.record.states[context.index]);
    persist(context.record);
    refreshCard(context);
    openDialog(context, true);
  }
  function prepareRequired(context) {
    const adapter = types[context.spec.type], saved = context.record.states[context.index];
    if (!supportsPractice(adapter) || !saved || typeof adapter.prepare !== "function") return;
    const abort = new AbortController();
    context.preparationAbort = abort;
    const original = JSON.stringify(saved);
    try {
      const pending = adapter.prepare(context.spec.round, clone(saved), { signal: abort.signal });
      if (!pending || typeof pending.then !== "function") return;
      context.preparing = true;
      Promise.resolve(pending).then(state => {
        if (abort.signal.aborted || !currentContext(context) || JSON.stringify(context.record.states[context.index]) !== original) return;
        context.record.states[context.index] = adapter.restore(context.spec.round, state);
        persist(context.record);
      }).catch(() => { /* Open the original repair to retry; optional state never grants access. */ }).finally(() => {
        if (!abort.signal.aborted && currentContext(context)) { context.preparing = false; updateNavigation(context); }
      });
    } catch (_) { /* The ordinary required mount retains its retry UI. */ }
  }
  function mountQuestion(context) {
    if (!currentContext(context)) return;
    destroyMount();
    const token = mountToken;
    let visibleRound = null;
    retryButton.hidden = true;
    try {
      const spec = validateCheckpoint(context.spec);
      const adapter = types[spec.type];
      const optional = context.practice && supportsPractice(adapter) && isComplete(context.scenario, context.index);
      context.practice = !!optional;
      updateDialog(context);
      const states = optional ? context.record.practices : context.record.states;
      const restore = optional ? adapter.restorePractice : adapter.restore;
      const mount = optional ? adapter.mountPractice : adapter.mount;
      mounted = mount(mountHost, {
        round: clone(spec.round), assetBase: "games/",
        initialState: states[context.index] ? clone(states[context.index]) : null,
        newPracticeLabel: text("practice"),
        onNewPractice: supportsPractice(adapter) ? () => { if (token === mountToken) newPractice(context); } : undefined,
        onProgress(value) {
          if (token !== mountToken || !currentContext(context)) return;
          showProgress(value);
          const nextRound = validProgress(value) ? value.current + "/" + value.total : null;
          // A new question starts above the fold; same-round updates keep the learner's scroll.
          if (nextRound !== visibleRound) {
            stopResponseScroll();
            if (nextRound && dialog && dialog.open) dialog.scrollTop = 0;
          }
          visibleRound = nextRound;
        },
        onReveal(request) {
          if (token !== mountToken || !currentContext(context)) return;
          revealResponse(request);
        },
        onStateChange(state) {
          if (token !== mountToken || !currentContext(context)) return;
          const wasComplete = isComplete(context.scenario, context.index);
          states[context.index] = restore(spec.round, state);
          persist(context.record);
          refreshCard(context);
          if (wasComplete !== isComplete(context.scenario, context.index)) updateNavigation(context);
        },
        onSolved(result, state) {
          if (token !== mountToken || !currentContext(context) || !result || result.kind !== "correct") return;
          const normalized = restore(spec.round, state);
          if (!normalized.solved) return;
          states[context.index] = normalized;
          persist(context.record);
          updateNavigation(context);
        },
        onContinue() {
          if (token !== mountToken || !currentContext(context) || !isComplete(context.scenario, context.index)) return;
          continueLesson(context);
        }
      });
    } catch (_) {
      showProgress(null);
      mountHost.replaceChildren(node("p", "nl-quiz-error", text("error")));
      retryButton.hidden = false;
    }
  }
  function openDialog(context, optional) {
    if (!currentContext(context) || context.preparing) return;
    context.practice = optional === true && supportsPractice(types[context.spec.type]) && isComplete(context.scenario, context.index);
    ensureDialog();
    updateDialog(context);
    dialog.querySelector("#nlQuizBack").textContent = text("back");
    retryButton.textContent = text("retry");
    if (typeof dialog.showModal !== "function") {
      context.status.textContent = text("error");
      return;
    }
    if (!dialog.open) dialog.showModal();
    mountQuestion(context);
  }

  function onExit() {
    closeDialog();
    if (active && active.preparationAbort) active.preparationAbort.abort();
    if (active && active.section) active.section.remove();
    active = null;
  }
  function isPreview(scenario) {
    return !!(preview && preview.scenario === scenario && preview.record.content === signature(scenario));
  }
  function endPreview() {
    if (!preview) return;
    preview = null;
    onExit();
  }
  function beginPreview(scenario) {
    endPreview();
    onExit();
    preview = { scenario, record: { key: null, content: signature(scenario),
      states: Object.create(null), practices: Object.create(null), storageAvailable: true, temporary: true } };
  }
  function onStep(scenario, index) {
    const step = scenario && scenario.steps && scenario.steps[index];
    if (!step || !own(step, "checkpoint")) { onExit(); return; }
    const content = signature(scenario);
    if (active && active.scenario === scenario && active.index === index && active.record.content === content &&
        active.section.isConnected) { refreshCard(active); return; }
    onExit();
    const spec = validateCheckpoint(step.checkpoint);
    const section = node("section", "nl-quiz-checkpoint");
    section.id = "nlQuizCheckpoint";
    section.setAttribute("aria-labelledby", "nlQuizCheckpointHeading");
    const copy = node("div", "nl-quiz-checkpoint-copy");
    const heading = node("h2", "nl-quiz-checkpoint-heading", text("label"));
    heading.id = "nlQuizCheckpointHeading";
    const status = node("p", "nl-quiz-checkpoint-status");
    status.id = "nlQuizCheckpointStatus";
    status.setAttribute("aria-live", "polite");
    const storageNote = node("p", "nl-quiz-storage-note");
    storageNote.hidden = true;
    copy.append(heading, status, storageNote);
    const context = { scenario, index, spec, section, status, storageNote, record: recordFor(scenario) };
    context.openButton = button("", "nl-quiz-button nl-quiz-open", () => openDialog(context));
    context.openButton.id = "nlQuizOpen";
    context.practiceButton = button("", "nl-quiz-button nl-quiz-practice-open", () => {
      if (context.record.practices[context.index]) openDialog(context, true);
      else newPractice(context);
    });
    context.practiceButton.id = "nlQuizPracticeOpen";
    context.practiceButton.hidden = true;
    const actions = node("div", "nl-quiz-checkpoint-actions");
    actions.append(context.openButton, context.practiceButton);
    section.append(copy, actions);
    const note = global.document.getElementById("scStepText");
    const title = global.document.getElementById("pageTitle");
    if (note && note.parentNode) note.insertAdjacentElement("afterend", section);
    else if (title && title.parentNode) title.insertAdjacentElement("afterend", section);
    else global.document.body.append(section);
    active = context;
    prepareRequired(context);
    refreshCard(context);
  }

  function reset(scenario) {
    const record = recordFor(scenario);
    record.states = Object.create(null);
    record.practices = Object.create(null);
    persist(record);
    if (active && active.scenario === scenario) { closeDialog(); updateNavigation(active); }
  }

  global.NameleculeQuizCheckpoints = { registerType, validateCheckpoint, hasCheckpoints,
    resolveTarget, prepareTarget, isComplete, onStep, onExit, reset,
    beginPreview, endPreview, isPreview };
})(typeof window !== "undefined" ? window : globalThis);
