/* Optional presentation only. Game evidence, chemistry and grading stay owned
 * by the existing controllers. Older hosts need not load this module. */
(function (global) {
  "use strict";
  const doc = global.document, mounted = new WeakMap();
  let documentOwners = 0;
  function later(callback) { return global.requestAnimationFrame(callback); }
  function cancel(id) { if (id !== null) global.cancelAnimationFrame(id); }
  function observeResize(target, callback) {
    if (!global.ResizeObserver || !target) return null;
    const observer = new global.ResizeObserver(callback); observer.observe(target); return observer;
  }
  function mount(root, options) {
    options = options || {};
    if (!root || !doc) throw new Error("Missing game viewport root");
    if (mounted.has(root)) mounted.get(root).destroy();
    let dead = false, task = null, previous = "";
    const originalHeight = root.style.getPropertyValue("--nl-vp-height");
    const originalWidth = root.style.getPropertyValue("--nl-vp-width");
    const ownsDocument = options.document !== false && !root.closest(".nl-vp-dialog");
    root.classList.add("nl-game-viewport");
    if (options.kind) root.setAttribute("data-nl-vp-kind", options.kind);
    if (ownsDocument) { documentOwners++; doc.documentElement.classList.add("nl-vp-document"); doc.body.classList.add("nl-vp-document"); }
    function measure() {
      task = null; if (dead || !root.isConnected) return;
      const rect = root.getBoundingClientRect(), slot = root.closest(".nl-vp-slot");
      const viewportHeight = Math.min(global.innerHeight, global.visualViewport ? global.visualViewport.height : global.innerHeight);
      const bottom = slot ? Math.min(viewportHeight, slot.getBoundingClientRect().bottom) : viewportHeight - 8;
      const height = Math.max(80, Math.floor(bottom - Math.max(0, rect.top)));
      const width = Math.max(80, Math.floor(Math.min(global.innerWidth, rect.width || root.clientWidth || global.innerWidth)));
      const key = width + ":" + height;
      if (key === previous) return; previous = key;
      root.style.setProperty("--nl-vp-height", height + "px"); root.style.setProperty("--nl-vp-width", width + "px");
      root.classList.toggle("nl-vp-narrow", width < 760 || height < 430);
      const detail = { height, width, narrow: width < 760 || height < 430 };
      if (typeof options.onResize === "function") options.onResize(detail);
      root.dispatchEvent(new global.CustomEvent("nl-viewport-change", { bubbles: true, detail }));
    }
    function refresh() { if (!dead && task === null) task = later(measure); }
    const observer = observeResize(root.parentElement, refresh);
    global.addEventListener("resize", refresh);
    if (global.visualViewport) global.visualViewport.addEventListener("resize", refresh);
    const api = { refresh, destroy() {
      if (dead) return; dead = true; cancel(task); task = null;
      if (observer) observer.disconnect(); global.removeEventListener("resize", refresh);
      if (global.visualViewport) global.visualViewport.removeEventListener("resize", refresh);
      root.classList.remove("nl-game-viewport", "nl-vp-narrow"); root.removeAttribute("data-nl-vp-kind");
      if (originalHeight) root.style.setProperty("--nl-vp-height", originalHeight); else root.style.removeProperty("--nl-vp-height");
      if (originalWidth) root.style.setProperty("--nl-vp-width", originalWidth); else root.style.removeProperty("--nl-vp-width");
      if (ownsDocument && --documentOwners === 0) { doc.documentElement.classList.remove("nl-vp-document"); doc.body.classList.remove("nl-vp-document"); }
      if (mounted.get(root) === api) mounted.delete(root);
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
      const key = width + ":" + height + ":" + identity.requestId;
      if (!force && key === last) return; last = key;
      frame.style.height = height + "px";
      if (frame.contentWindow && options.channel && options.session) frame.contentWindow.postMessage({
        channel: options.channel, session: options.session, ...identity,
        command: "viewport", viewportVersion: 1, width, height
      }, global.location.origin);
    }
    function refresh() { if (!dead && task === null) task = later(() => measure(false)); }
    const observer = observeResize(stage, refresh);
    const onLoad = () => measure(true); frame.addEventListener("load", onLoad); global.addEventListener("resize", refresh);
    refresh();
    return { refresh, destroy() { if (dead) return; dead = true; cancel(task); if (observer) observer.disconnect();
      frame.removeEventListener("load", onLoad); global.removeEventListener("resize", refresh);
      frame.classList.remove("nl-vp-frame"); stage.classList.remove("nl-vp-fit-stage"); } };
  }
  global.NameleculeGameViewport = Object.freeze({ version: 1, mount, pager, fitFrame });
})(typeof window !== "undefined" ? window : globalThis);
