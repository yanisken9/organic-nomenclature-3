// Inserted inside the existing bounded DOM observer, before observer-installed.
// Only controlled test runtime changes; production source stays byte-identical.
  const wrapperProof = [];
  function safeStageReport(reason, extra = {}) { try { report(reason, extra); } catch (_) {} }
  function setupRead(label, read) {
    safeStageReport(label + '-setup-read-before');
    try {
      const value = read();
      safeStageReport(label + '-setup-read-after', {valueType: typeof value});
      return value;
    } catch (_) { safeStageReport(label + '-setup-read-throw'); return undefined; }
  }
  function installStageWrapper(owner, key, label, wanted, describe) {
    try {
      const original = setupRead(label + '-original', () => owner?.[key]);
      if (typeof original !== 'function') { safeStageReport('wrapper-missing', {label}); return; }
      const descriptor = setupRead(label + '-descriptor', () => Object.getOwnPropertyDescriptor(owner, key));
      const wrapped = function (...args) {
        let observe = true, details = {};
        // Telemetry failures never skip, repeat or replace the original call.
        try { observe = !wanted || wanted(this, args); } catch (_) { observe = false; }
        if (!observe) return Reflect.apply(original, this, args);
        try { details = describe ? describe(this, args) : {}; } catch (_) {}
        safeStageReport(label + '-before', details);
        try {
          const result = Reflect.apply(original, this, args);
          safeStageReport(label + '-after', details);
          return result;
        } catch (failure) {
          safeStageReport(label + '-throw', {...details, exceptionType: typeof failure});
          throw failure;
        }
      };
      safeStageReport(label + '-setup-write-before');
      owner[key] = wrapped;
      safeStageReport(label + '-setup-write-after');
      const installed = setupRead(label + '-verification', () => owner[key]) === wrapped;
      wrapperProof.push({label, installed, ownOriginal: !!descriptor, originalName: original.name,
        originalLength: original.length, originalWritable: descriptor?.writable ?? null,
        originalConfigurable: descriptor?.configurable ?? null});
      if (!installed) safeStageReport('wrapper-install-failed', {label});
      return installed;
    } catch (_) { safeStageReport('wrapper-install-failed', {label}); }
  }
  installStageWrapper(setupRead('main-Element-prototype', () => Element.prototype), 'remove', 'main-iframe-remove',
    element => element?.tagName === 'IFRAME',
    element => ({frameId: element.id || null, frameClass: element.className || null,
      source: String(element.getAttribute('src') || '').slice(0, 180), connected: !!element.isConnected}));
  installStageWrapper(window, 'fScenarioGo', 'main-fScenarioGo', null,
    (_, args) => ({destination: typeof args[0] === 'number' ? args[0] : typeof args[0], argumentCount: args.length}));
  const outerUI = setupRead('outerUI-window', () => document.querySelector('.nl-detective-frame')?.contentWindow);
  const nativeUI = setupRead('native-window', () => outerUI?.document.getElementById('molecule-viewer')?.contentWindow);
  for (const [label, realm] of [['outerUI', outerUI], ['native', nativeUI]]) {
    if (!realm) { safeStageReport('pagehide-observer-missing', {realm: label}); continue; }
    try {
      realm.addEventListener('pagehide', event => {
        safeStageReport(label + '-pagehide-capture', {persisted: event.persisted, eventPhase: event.eventPhase});
        try { queueMicrotask(() => safeStageReport(label + '-pagehide-microtask')); } catch (_) {}
      }, {capture: true, passive: true});
      wrapperProof.push({label: label + '-pagehide-capture', installed: true});
    } catch (_) { safeStageReport('pagehide-observer-install-failed', {realm: label}); }
  }
  // Inspect property descriptors only: setup must not invoke this service getter.
  // The original getter runs exactly once for each subsequent application read.
  const speechHookLabel = 'native-speech-get';
  try {
    let descriptorOwner = nativeUI, descriptor, depth = 0;
    while (descriptorOwner && depth < 12) {
      descriptor = setupRead('native-speech-descriptor-' + depth, () => Object.getOwnPropertyDescriptor(descriptorOwner, 'speechSynthesis'));
      if (descriptor) break;
      descriptorOwner = setupRead('native-speech-prototype-' + depth, () => Object.getPrototypeOf(descriptorOwner));
      ++depth;
    }
    safeStageReport('native-speech-descriptor-result', {found: !!descriptor, depth,
      accessor: typeof descriptor?.get === 'function', configurable: descriptor?.configurable ?? null});
    if (!descriptor || descriptor.configurable !== true || typeof descriptor.get !== 'function') {
      wrapperProof.push({label: speechHookLabel, installed: false, unsupportedDescriptor: true});
      safeStageReport('native-speech-get-hook-unsupported');
    } else {
      const originalGet = descriptor.get, wrappedServices = new WeakSet();
      const observedGet = function () {
        safeStageReport('native-speech-get-before');
        let service;
        try {
          service = Reflect.apply(originalGet, this, []);
          safeStageReport('native-speech-get-after', {valueType: typeof service});
        } catch (failure) {
          safeStageReport('native-speech-get-throw', {exceptionType: typeof failure});
          throw failure;
        }
        try {
          if (service && (typeof service === 'object' || typeof service === 'function') && !wrappedServices.has(service)) {
            if (installStageWrapper(service, 'cancel', 'native-speech-cancel', null,
              (_, args) => ({argumentCount: args.length}))) wrappedServices.add(service);
          }
        } catch (_) { safeStageReport('native-speech-lazy-cancel-hook-failed'); }
        return service;
      };
      safeStageReport('native-speech-get-setup-write-before');
      Object.defineProperty(descriptorOwner, 'speechSynthesis', {...descriptor, get: observedGet});
      safeStageReport('native-speech-get-setup-write-after');
      const installed = setupRead('native-speech-hook-descriptor', () => Object.getOwnPropertyDescriptor(descriptorOwner, 'speechSynthesis'))?.get === observedGet;
      wrapperProof.push({label: speechHookLabel, installed, descriptorDepth: depth, originalConfigurable: descriptor.configurable,
        originalEnumerable: descriptor.enumerable, originalSetterPreserved: true, serviceGetterReadDuringSetup: false});
    }
  } catch (_) {
    wrapperProof.push({label: speechHookLabel, installed: false});
    safeStageReport('native-speech-get-hook-failed');
  }
  installStageWrapper(setupRead('native-Jmol-object', () => nativeUI?.Jmol), 'script', 'native-Jmol-script', null,
    (_, args) => ({argumentCount: args.length, command: typeof args[1] === 'string' ? args[1].slice(0, 120) : typeof args[1]}));
  safeStageReport('stage-wrappers-installed', {wrappers: wrapperProof});
