// Isolated prototype. State belongs to the applet object, not its DOM id.
a._nameleculeLifecycle = (function () {
  var states = new WeakMap();
  function state(applet) {
    var value = states.get(applet);
    if (!value) {
      value = { closed: false, frames: new Set(), resize: null };
      states.set(applet, value);
    }
    return value;
  }
  function live(applet, panel) {
    return !!applet && !state(applet).closed &&
      (!panel || applet._appletPanel === panel);
  }
  return {
    version: "20261031-v1",
    live: live,
    paint: function (applet, panel, deferred, draw) {
      if (!live(applet, panel)) return;
      var value = state(applet), handle = null;
      function run() {
        if (handle !== null) value.frames.delete(handle);
        if (live(applet, panel)) draw();
      }
      if (deferred) {
        handle = requestAnimationFrame(run);
        value.frames.add(handle);
      } else {
        run();
      }
    },
    resize: function (applet) {
      if (!live(applet)) return;
      var value = state(applet), key = "__resizeTimeout_" + applet._id;
      if (value.resize !== null) clearTimeout(value.resize);
      var handle = setTimeout(function () {
        if (value.resize !== handle) return;
        value.resize = null;
        if (a[key] === handle) a[key] = null;
        if (live(applet)) a.repaint(applet, true);
      }, 100);
      value.resize = handle;
      a[key] = handle;
    },
    dispose: function (applet) {
      if (!applet) return;
      var value = state(applet);
      // Close first: teardown can re-enter through native script/paint code.
      value.closed = true;
      value.frames.forEach(function (handle) { cancelAnimationFrame(handle); });
      value.frames.clear();
      if (value.resize !== null) {
        clearTimeout(value.resize);
        var key = "__resizeTimeout_" + applet._id;
        if (a[key] === value.resize) a[key] = null;
        value.resize = null;
      }
    }
  };
})();
