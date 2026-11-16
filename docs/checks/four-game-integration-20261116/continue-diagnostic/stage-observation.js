(()=>{
  const run=RUN_ID, endpoint='/__trace__', deadline=performance.now()+50000;
  let seq=0, ticks=0, mutationTimer=0, stopped=false;
  const listeners=[];
  function text(selector,n=120){const e=document.querySelector(selector);return e?String(e.innerText||e.textContent||'').replace(/\s+/g,' ').trim().slice(0,n):null;}
  function target(e){const t=e?.target;return t?{tag:t.tagName||null,id:t.id||null,text:String(t.innerText||t.textContent||'').trim().slice(0,80),connected:!!t.isConnected}:null;}
  function report(reason,extra={}){try{
    if(stopped)return;
    const d=document.querySelector('#nlQuizDialog'), active=document.activeElement;
    const value={run,seq:++seq,reason,utc:new Date().toISOString(),performance:performance.now(),
      counter:text('#scPos'),pageTitle:text('#pageTitle',180),documentTitle:document.title,
      dialogOpen:!!d?.open,dialogConnected:!!d?.isConnected,iframeCount:document.querySelectorAll('iframe').length,
      lessonText:text('#scStepText'),quizProgress:text('#nlQuizProgress'),
      active:{tag:active?.tagName||null,id:active?.id||null,text:String(active?.innerText||'').slice(0,80)},
      nextDisabled:document.querySelector('#scNext')?.disabled??null,visibility:document.visibilityState,...extra};
    const body=JSON.stringify(value);
    if(!navigator.sendBeacon(endpoint,new Blob([body],{type:'application/json'})))fetch(endpoint,{method:'POST',body,headers:{'Content-Type':'application/json'},keepalive:true}).catch(()=>{});
  }catch(_){}}
  for(const type of ['keydown','keyup','pointerdown','pointerup','click']){
    for(const capture of [true,false]){
      const handler=e=>{const extra={eventType:type,eventKey:e.key||null,eventButton:e.button??null,trusted:e.isTrusted,defaultPrevented:e.defaultPrevented,target:target(e),capture};
        report(capture?'event-before':'event-after',extra);
        queueMicrotask(()=>report(capture?'before-microtask':'after-microtask',extra));
        requestAnimationFrame(()=>report(capture?'before-rAF':'after-rAF',extra));};
      window.addEventListener(type,handler,{capture,passive:true});listeners.push([type,handler,capture]);
    }
  }
  const observer=new MutationObserver(records=>{
    if(stopped||mutationTimer)return;
    const count=records.length;
    mutationTimer=setTimeout(()=>{mutationTimer=0;report('mutation',{mutationCount:count});},35);
  });
  observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['open','disabled','hidden','class']});
  const interval=setInterval(()=>{
    report('interval',{tick:++ticks});
    if(ticks>=250||performance.now()>=deadline){report('observer-ended');stopped=true;clearInterval(interval);clearTimeout(mutationTimer);observer.disconnect();listeners.forEach(([type,fn,capture])=>window.removeEventListener(type,fn,capture));}
  },200);
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

  report('observer-installed');return true;
})()
