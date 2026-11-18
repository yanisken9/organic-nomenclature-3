/* Optional presentation only. Game evidence, chemistry and grading stay owned
 * by the existing controllers. Older hosts need not load this module. */
(function (global) {
  "use strict";
  const doc = global.document, mounted = new WeakMap(), receivedCaps = new WeakMap(), dialogs = new WeakMap();
  let documentOwners = 0;
  function later(callback) { return global.requestAnimationFrame(callback); }
  function cancel(id) { if (id !== null) global.cancelAnimationFrame(id); }
  function observeResize(target, callback) {
    if (!global.ResizeObserver || !target) return null;
    const observer = new global.ResizeObserver(callback); observer.observe(target); return observer;
  }
  function pixels(value) { return parseFloat(value) || 0; }
  function inFlow(element) {
    if (!element || element.hidden) return false;
    const style = global.getComputedStyle(element);
    return style.display !== "none" && style.position !== "absolute" && style.position !== "fixed";
  }
  function outerHeight(element) {
    if (!inFlow(element)) return 0;
    const style = global.getComputedStyle(element);
    return element.getBoundingClientRect().height + pixels(style.marginTop) + pixels(style.marginBottom);
  }
  // Only independently sized chrome is measured. The allocated/stretched body
  // is replaced by its controller's usable region envelope, including results.
  function preferred(root, region, regionHeight, key, options) {
    if (!root || !region || !root.contains(region) || !Number.isFinite(regionHeight) || regionHeight < 0) return null;
    options = options || {};
    const excluded = new Set(options.exclude || []);
    let height = regionHeight, current = region;
    while (current && current !== root) {
      const parent = current.parentElement;
      if (!parent) return null;
      const style = global.getComputedStyle(parent);
      const siblings = Array.from(parent.children).filter(element => element !== current && !excluded.has(element) &&
        inFlow(element) && pixels(global.getComputedStyle(element).flexGrow) === 0);
      height += pixels(style.paddingTop) + pixels(style.paddingBottom) + pixels(style.borderTopWidth) + pixels(style.borderBottomWidth);
      height += siblings.reduce((sum, element) => sum + outerHeight(element), 0);
      if (style.display.includes("flex") || style.display.includes("grid")) height += pixels(style.rowGap) * siblings.length;
      current = parent;
    }
    if (current !== root) return null;
    return { key: String(key || "question").slice(0, 200), height: Math.ceil(height),
      width: Math.floor(root.getBoundingClientRect().width) };
  }
  function availableHeight(root, fallback) {
    const dialog = root.closest(".nl-vp-dialog"), owner = dialog && dialogs.get(dialog);
    if (owner) return owner.available(root);
    return receivedCaps.get(root) || fallback || pixels(root.style.getPropertyValue("--nl-vp-height")) || root.getBoundingClientRect().height ||
      Math.min(global.innerHeight, global.visualViewport ? global.visualViewport.height : global.innerHeight);
  }
  function acceptViewport(root, data) {
    if (!root || !data || !Number.isFinite(data.availableHeight) || data.availableHeight < 80 || data.availableHeight > 8000) return false;
    receivedCaps.set(root, data.availableHeight);
    const api = mounted.get(root); if (api) api.refresh();
    return true;
  }
  function validDemand(value) {
    return !!(value && value.layoutVersion === 1 && typeof value.key === "string" && value.key.length > 0 && value.key.length <= 200 &&
      Number.isFinite(value.height) && value.height >= 80 && value.height <= 8000 &&
      Number.isFinite(value.width) && value.width >= 80 && value.width <= 16000);
  }
  function mount(root, options) {
    options = options || {};
    if (!root || !doc) throw new Error("Missing game viewport root");
    if (mounted.has(root)) mounted.get(root).destroy();
    let dead = false, task = null, previous = "", demandKey = "", demandHeight = 0, lastDemand = "", fontEpoch = 0;
    const originalHeight = root.style.getPropertyValue("--nl-vp-height");
    const originalWidth = root.style.getPropertyValue("--nl-vp-width");
    const ownsDocument = options.document !== false && !root.closest(".nl-vp-dialog");
    root.classList.add("nl-game-viewport");
    if (options.kind) root.setAttribute("data-nl-vp-kind", options.kind);
    if (ownsDocument) { documentOwners++; doc.documentElement.classList.add("nl-vp-document"); doc.body.classList.add("nl-vp-document"); }
    function measure() {
      task = null; if (dead || !root.isConnected) return;
      // The measured node may itself be a slot with our previous explicit
      // height. Its external slot owns the available space on a later resize.
      const rect = root.getBoundingClientRect(), slot = root.parentElement ? root.parentElement.closest(".nl-vp-slot") : null;
      const viewportHeight = Math.min(global.innerHeight, global.visualViewport ? global.visualViewport.height : global.innerHeight);
      const bottom = slot ? Math.min(viewportHeight, slot.getBoundingClientRect().bottom) : viewportHeight - 8;
      const height = Math.max(80, Math.floor(bottom - Math.max(0, rect.top)));
      const width = Math.max(80, Math.floor(Math.min(global.innerWidth, rect.width || root.clientWidth || global.innerWidth)));
      const cap = Math.max(80, Math.floor(availableHeight(root, height))), key = width + ":" + height + ":" + cap;
      if (key !== previous) {
        previous = key;
        root.style.setProperty("--nl-vp-height", height + "px"); root.style.setProperty("--nl-vp-width", width + "px");
        root.classList.toggle("nl-vp-narrow", width < 760 || cap < 430);
        const detail = { height, width, availableHeight: cap, narrow: width < 760 || cap < 430 };
        if (typeof options.onResize === "function") options.onResize(detail);
        root.dispatchEvent(new global.CustomEvent("nl-viewport-change", { bubbles: true, detail }));
      }
      if (typeof options.preferred === "function") {
        const value = options.preferred({ height, width, availableHeight: cap });
        if (value && typeof value.key === "string" && Number.isFinite(value.height)) {
          const context = value.key + ":" + width + ":" + cap + ":" + fontEpoch;
          if (context !== demandKey) { demandKey = context; demandHeight = 0; }
          demandHeight = Math.max(demandHeight, Math.ceil(value.height));
          const detail = { layoutVersion: 1, key: value.key, height: demandHeight, width };
          const signature = JSON.stringify(detail);
          if (validDemand(detail) && signature !== lastDemand) {
            lastDemand = signature;
            root.dispatchEvent(new global.CustomEvent("nl-layout-demand", { bubbles: true, detail }));
            if (typeof options.onDemand === "function") options.onDemand(detail);
          }
        }
      }
    }
    function refresh() { if (!dead && task === null) task = later(measure); }
    const observer = observeResize(root.parentElement, refresh);
    global.addEventListener("resize", refresh);
    if (global.visualViewport) global.visualViewport.addEventListener("resize", refresh);
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(() => { if (!dead) { fontEpoch++; refresh(); } });
    const api = { refresh, destroy() {
      if (dead) return; dead = true; cancel(task); task = null;
      if (observer) observer.disconnect(); global.removeEventListener("resize", refresh);
      if (global.visualViewport) global.visualViewport.removeEventListener("resize", refresh);
      root.classList.remove("nl-game-viewport", "nl-vp-narrow"); root.removeAttribute("data-nl-vp-kind");
      if (originalHeight) root.style.setProperty("--nl-vp-height", originalHeight); else root.style.removeProperty("--nl-vp-height");
      if (originalWidth) root.style.setProperty("--nl-vp-width", originalWidth); else root.style.removeProperty("--nl-vp-width");
      if (ownsDocument && --documentOwners === 0) { doc.documentElement.classList.remove("nl-vp-document"); doc.body.classList.remove("nl-vp-document"); }
      if (mounted.get(root) === api) mounted.delete(root);
      receivedCaps.delete(root);
    } };
    mounted.set(root, api); refresh(); return api;
  }
  function pager(content, options) {
    options = options || {};
    if (!content || !content.parentNode || !doc) throw new Error("Missing paged content");
    const horizontal = options.axis === "x", wrapper = doc.createElement("div"), nav = doc.createElement("nav");
    wrapper.className = "nl-vp-pager nl-vp-pager-" + (horizontal ? "x" : "y");
    nav.className = "nl-vp-pager-nav"; nav.setAttribute("aria-label", options.label || "Σελίδες περιεχομένου");
    const previous = doc.createElement("button"), next = doc.createElement("button"), count = doc.createElement("span");
    previous.type = next.type = "button"; previous.textContent = "←"; next.textContent = "→";
    previous.setAttribute("aria-label", "Προηγούμενη σελίδα — " + (options.label || "περιεχόμενο"));
    next.setAttribute("aria-label", "Επόμενη σελίδα — " + (options.label || "περιεχόμενο"));
    count.setAttribute("aria-live", "polite"); count.setAttribute("aria-atomic", "true");
    nav.append(previous, count, next); content.before(wrapper); wrapper.append(content, nav);
    content.classList.add("nl-vp-page-content", "nl-vp-page-window");
    let dead = false, task = null;
    function metrics() {
      const size = horizontal ? content.clientWidth : content.clientHeight;
      const total = horizontal ? content.scrollWidth : content.scrollHeight;
      const position = horizontal ? content.scrollLeft : content.scrollTop;
      const line = parseFloat(global.getComputedStyle(content).lineHeight) || 24;
      const explicitOverlap = !horizontal && Number.isFinite(options.overlap) && options.overlap > 0;
      const overlap = explicitOverlap ? Math.min(Math.max(0, size - 24), options.overlap) : Math.min(size / 4, horizontal ? 24 : line);
      const step = Math.max(24, size - overlap);
      return { size, maximum: Math.max(0, total - size), position, step };
    }
    function refresh() {
      if (dead) return;
      const m = metrics(), overflow = m.size > 0 && m.maximum > 2;
      wrapper.classList.toggle("is-overflow", overflow); nav.hidden = !overflow;
      previous.disabled = m.position <= 1; next.disabled = m.position >= m.maximum - 1;
      const pages = Math.ceil(m.maximum / m.step) + 1;
      const current = m.position >= m.maximum - 1 ? pages : Math.min(pages, Math.floor((m.position + 1) / m.step) + 1);
      count.textContent = overflow ? "Σελίδα " + current + "/" + pages : "";
    }
    function schedule() { if (!dead && task === null) task = later(() => { task = null; refresh(); }); }
    function go(direction) {
      const m = metrics(), position = Math.max(0, Math.min(m.maximum, m.position + direction * m.step));
      if (horizontal) content.scrollLeft = position; else content.scrollTop = position;
      refresh();
    }
    previous.addEventListener("click", () => go(-1)); next.addEventListener("click", () => go(1));
    content.addEventListener("scroll", schedule, { passive: true }); global.addEventListener("resize", schedule);
    const observer = observeResize(content, schedule);
    const mutation = global.MutationObserver ? new global.MutationObserver(schedule) : null;
    if (mutation) mutation.observe(content, { subtree: true, childList: true, characterData: true });
    refresh();
    return { refresh, previous: () => go(-1), next: () => go(1), element: wrapper, destroy() {
      if (dead) return; dead = true; cancel(task); if (observer) observer.disconnect(); if (mutation) mutation.disconnect();
      content.removeEventListener("scroll", schedule); global.removeEventListener("resize", schedule);
      content.classList.remove("nl-vp-page-content", "nl-vp-page-window");
      if (wrapper.parentNode) { wrapper.before(content); wrapper.remove(); }
    } };
  }
  /* The parent owns iframe height. Natural child resize reports are ignored only
   * for opted-in hosts; this protocol never reads or changes answer evidence. */
  function fitFrame(frame, options) {
    options = options || {};
    const stage = options.stage || frame.parentElement;
    let dead = false, task = null, last = "";
    frame.classList.add("nl-vp-frame"); stage.classList.add("nl-vp-fit-stage");
    function measure(force) {
      task = null; if (dead || !frame.isConnected) return;
      const rect = stage.getBoundingClientRect();
      const width = Math.max(80, Math.floor(rect.width)), height = Math.max(80, Math.floor(rect.height));
      const identity = typeof options.identity === "function" ? options.identity() : options.identity;
      if (!identity) return;
      const cap = Math.max(80, Math.floor(availableHeight(stage, height)));
      const key = width + ":" + height + ":" + cap + ":" + identity.requestId;
      if (!force && key === last) return; last = key;
      frame.style.height = height + "px";
      if (frame.contentWindow && options.channel && options.session) frame.contentWindow.postMessage({
        channel: options.channel, session: options.session, ...identity,
        command: "viewport", viewportVersion: 1, width, height, availableHeight: cap
      }, global.location.origin);
    }
    function refresh() { if (!dead && task === null) task = later(() => measure(false)); }
    const observer = observeResize(stage, refresh);
    const onLoad = () => measure(true); frame.addEventListener("load", onLoad); global.addEventListener("resize", refresh);
    refresh();
    return { refresh, setDemand(value) {
      if (dead || !validDemand(value) || Math.abs(value.width - stage.getBoundingClientRect().width) > 2) return false;
      stage.dispatchEvent(new global.CustomEvent("nl-layout-demand", { bubbles: true, detail: { ...value } }));
      return true;
    }, destroy() { if (dead) return; dead = true; cancel(task); if (observer) observer.disconnect();
      frame.removeEventListener("load", onLoad); global.removeEventListener("resize", refresh);
      frame.classList.remove("nl-vp-frame"); stage.classList.remove("nl-vp-fit-stage"); } };
  }
  // One dialog writer. Demand is independent of allocated height; this avoids
  // resizing loops between the parent flex slot and the child compact mode.
  function adaptiveDialog(dialog, options) {
    options = options || {};
    const host = options.host;
    let dead = false, enabled = false, task = null, source = null, demand = null, last = "", sizingSource = null, sizingKey = "", desiredHeight = 0;
    function cap() {
      return Math.max(80, Math.floor(Math.min(global.innerHeight, global.visualViewport ? global.visualViewport.height : global.innerHeight) - (global.innerWidth <= 650 ? 12 : 24)));
    }
    function chrome(target) {
      const top = Math.max(0, target.getBoundingClientRect().top - dialog.getBoundingClientRect().top);
      let bottom = 0, consumedFooter = 0, current = target;
      while (current && current !== dialog) {
        const parent = current.parentElement; if (!parent) break;
        const style = global.getComputedStyle(parent);
        bottom += pixels(style.paddingBottom) + pixels(style.borderBottomWidth);
        let following = 0;
        for (let sibling = current.nextElementSibling; sibling; sibling = sibling.nextElementSibling) {
          if (!inFlow(sibling)) continue;
          const size = outerHeight(sibling); bottom += size; following++;
          if (sibling.matches(".round-next") || sibling.querySelector(".round-next")) consumedFooter += size;
        }
        if ((style.display.includes("flex") || style.display.includes("grid")) && following) {
          bottom += pixels(style.rowGap) * following;
          if (consumedFooter) consumedFooter += pixels(style.rowGap);
        }
        current = parent;
      }
      const reserve = typeof options.reserveActions === "function" ? options.reserveActions() : 0;
      return top + bottom + Math.max(0, reserve - consumedFooter);
    }
    function available(target) { return Math.max(80, Math.floor(cap() - chrome(target))); }
    function choosing() {
      return host.matches(".nl-vp-level-selection") || host.matches(".nl-vp-game-selection") ||
        !!host.querySelector(".nl-vp-level-selection") || !!host.querySelector(".nl-vp-game-selection");
    }
    function restoreVisual() {
      last = "";
      dialog.classList.remove("nl-vp-adaptive"); dialog.style.removeProperty("--nl-dialog-height");
    }
    function measure() {
      task = null;
      if (dead || !enabled || !dialog.open) return;
      if (!source || !host.contains(source)) { reset(); return; }
      // A chooser can retain a hidden game slot. Suspend its allocation without
      // throwing away the question demand needed when that same slot returns.
      if (choosing() || source.getBoundingClientRect().width < 80) { restoreVisual(); return; }
      if (!validDemand(demand)) return;
      // A message for an old width cannot size a newly resized frame.
      if (Math.abs(source.getBoundingClientRect().width - demand.width) > 2) return;
      const context = demand.key + ":" + demand.width + ":" + cap();
      if (sizingSource !== source || sizingKey !== context) { sizingSource = source; sizingKey = context; desiredHeight = 0; }
      // Parent header/footer changes must not make the current quiz bounce.
      desiredHeight = Math.max(desiredHeight, Math.ceil(chrome(source) + demand.height));
      const height = Math.min(cap(), Math.max(160, desiredHeight));
      const key = height + ":" + demand.width;
      if (key === last) return; last = key;
      dialog.style.setProperty("--nl-dialog-height", height + "px");
      dialog.classList.add("nl-vp-adaptive");
      host.querySelectorAll(".nl-game-viewport").forEach(root => mounted.get(root)?.refresh());
      dialog.dispatchEvent(new global.CustomEvent("nl-dialog-layout", { detail: { height, cap: cap(), preferredHeight: demand.height } }));
    }
    function refresh() { if (!dead && task === null) task = later(measure); }
    function receive(event) {
      if (!enabled || !dialog.open || !host.contains(event.target) || !validDemand(event.detail)) return;
      const width = event.target.getBoundingClientRect().width;
      if (width < 80 || Math.abs(width - event.detail.width) > 2) return;
      source = event.target; demand = { ...event.detail }; refresh();
    }
    function reset() {
      cancel(task); task = null; source = demand = sizingSource = null; sizingKey = ""; desiredHeight = 0;
      restoreVisual();
    }
    const observer = observeResize(dialog, refresh);
    const mutation = global.MutationObserver ? new global.MutationObserver(records => {
      const relevant = records.some(record => {
        const target = record.target && (record.target.nodeType === 1 ? record.target : record.target.parentElement);
        if (target && target.closest(".nl-adaptive-reserve")) return false;
        return record.type !== "childList" ||
          [...record.addedNodes, ...record.removedNodes].some(node => node.nodeType !== 1 || !node.classList.contains("nl-adaptive-reserve"));
      });
      if (relevant) refresh();
    }) : null;
    if (mutation) mutation.observe(host, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ["class", "hidden"] });
    host.addEventListener("nl-layout-demand", receive); global.addEventListener("resize", refresh);
    if (global.visualViewport) global.visualViewport.addEventListener("resize", refresh);
    const api = { available, refresh, reset, enable(value) { enabled = !!value; reset(); }, destroy() {
      if (dead) return; reset(); dead = true; observer?.disconnect(); mutation?.disconnect();
      host.removeEventListener("nl-layout-demand", receive); global.removeEventListener("resize", refresh);
      if (global.visualViewport) global.visualViewport.removeEventListener("resize", refresh);
      dialogs.delete(dialog);
    } };
    dialogs.set(dialog, api); return api;
  }
  global.NameleculeGameViewport = Object.freeze({ version: 1, mount, pager, fitFrame, preferred, availableHeight, acceptViewport, adaptiveDialog });
})(typeof window !== "undefined" ? window : globalThis);
