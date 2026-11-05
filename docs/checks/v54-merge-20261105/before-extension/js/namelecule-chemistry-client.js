/* Public browser API for the opt-in Workshop. Each analysis has its own Worker. */
(function (global) {
  'use strict';
  var script = document.currentScript;
  var clientURL = new URL(script && script.src || document.baseURI);
  var baseURL = new URL('.', clientURL);
  var workerURL = new URL('namelecule-chemistry-worker.js', baseURL);
  var adapterVersion = clientURL.searchParams.get('v');
  if (adapterVersion) workerURL.searchParams.set('v', adapterVersion);
  var engineURL = new URL('mulermoc-nom-core-54.js', baseURL);
  var verifiedEngines = new Map();
  var nextRequest = 0;

  function failure(code, message) {
    var error = new Error(message);
    error.code = code;
    if (code === 'ABORTED') error.name = 'AbortError';
    return error;
  }

  function requireHash(hash) {
    if (typeof hash !== 'string' || !/^[a-f0-9]{64}$/.test(hash)) {
      throw failure('INVALID_ENGINE_VERSION', 'Απαιτείται έγκυρη έκδοση της χημικής μηχανής.');
    }
  }

  function verifyEngine(expectedHash, options) {
    options = options || {};
    return Promise.resolve().then(function () {
      requireHash(expectedHash);
      if (options.signal && options.signal.aborted) throw failure('ABORTED', 'Η ανάλυση ακυρώθηκε.');
      if (!global.crypto || !global.crypto.subtle || typeof global.fetch !== 'function' ||
          typeof global.Blob !== 'function' || !global.URL || typeof global.URL.createObjectURL !== 'function' ||
          typeof global.URL.revokeObjectURL !== 'function') {
        throw failure('ENGINE_UNAVAILABLE', 'Δεν είναι διαθέσιμος ο ασφαλής έλεγχος της χημικής μηχανής.');
      }
      if (verifiedEngines.has(expectedHash)) return expectedHash;
      var url = new URL(engineURL.href);
      url.searchParams.set('sha256', expectedHash);
      return global.fetch(url.href, { cache: 'reload', signal: options.signal }).then(function (response) {
        if (!response.ok) throw failure('ENGINE_LOAD_FAILED', 'Η χημική μηχανή δεν φορτώθηκε.');
        return response.arrayBuffer();
      }).then(function (bytes) {
        return global.crypto.subtle.digest('SHA-256', bytes).then(function (digest) {
          if (options.signal && options.signal.aborted) throw failure('ABORTED', 'Η ανάλυση ακυρώθηκε.');
          var actualHash = Array.from(new Uint8Array(digest), function (byte) { return byte.toString(16).padStart(2, '0'); }).join('');
          if (actualHash !== expectedHash) {
            throw failure('ENGINE_VERSION_MISMATCH', 'Η χημική μηχανή άλλαξε. Ανανέωσε τα δεδομένα του παιχνιδιού.');
          }
          // Blob snapshots these exact verified bytes. Subsequent analyses import
          // this immutable source, even if the network file changes while open.
          verifiedEngines.set(expectedHash, new global.Blob([bytes], { type: 'application/javascript' }));
          return actualHash;
        });
      });
    });
  }

  function analyze(molecule, options) {
    options = options || {};
    return new Promise(function (resolve, reject) {
      var worker = null, sourceURL = null, settled = false;
      var signal = options.signal;
      var timeoutMs = options.timeoutMs == null ? 12000 : options.timeoutMs;
      if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
        reject(failure('INVALID_TIMEOUT', 'Το χρονικό όριο ανάλυσης δεν είναι έγκυρο.'));
        return;
      }
      var controller = new AbortController();
      var requestId = 'nl-chemistry-' + (++nextRequest);
      var timer = global.setTimeout(function () {
        finish(failure('ENGINE_TIMEOUT', 'Η χημική ανάλυση άργησε. Δοκίμασε ξανά.'));
      }, timeoutMs);

      function finish(error, result) {
        if (settled) return;
        settled = true;
        global.clearTimeout(timer);
        if (signal) signal.removeEventListener('abort', onAbort);
        controller.abort();
        if (worker) {
          worker.onmessage = worker.onerror = worker.onmessageerror = null;
          worker.terminate();
        }
        if (sourceURL) {
          global.URL.revokeObjectURL(sourceURL);
          sourceURL = null;
        }
        if (error) reject(error); else resolve(result);
      }
      function onAbort() { finish(failure('ABORTED', 'Η ανάλυση ακυρώθηκε.')); }
      if (signal) {
        if (signal.aborted) { onAbort(); return; }
        signal.addEventListener('abort', onAbort, { once: true });
      }
      if (!molecule || typeof molecule.id !== 'string' || !molecule.id || typeof molecule.mol !== 'string') {
        finish(failure('INVALID_MOLECULE', 'Δεν δόθηκε έγκυρος μοριακός τύπος.'));
        return;
      }
      // Keep the request and its reply checks tied to the same input snapshot.
      // Caller mutation during asynchronous version verification cannot retarget it.
      var input = { id: molecule.id, mol: molecule.mol };
      if (typeof global.Worker !== 'function') {
        finish(failure('ENGINE_UNAVAILABLE', 'Ο περιηγητής δεν υποστηρίζει απομονωμένη χημική ανάλυση.'));
        return;
      }
      verifyEngine(options.engineSHA256, { signal: controller.signal }).then(function (actualHash) {
        if (settled) return;
        try {
          sourceURL = global.URL.createObjectURL(verifiedEngines.get(actualHash));
          worker = new global.Worker(workerURL.href);
          worker.onmessage = function (event) {
            if (settled || !event.data || event.data.requestId !== requestId) return;
            if (event.data.type === 'error') {
              var details = event.data.error || {};
              finish(failure(details.code || 'ENGINE_FAILED', details.message || 'Η χημική ανάλυση απέτυχε.'));
            } else if (event.data.type === 'result') {
              var result = event.data.result;
              if (!result || result.moleculeId !== input.id || result.engineSHA256 !== actualHash) {
                finish(failure('INVALID_ENGINE_RESULT', 'Η απόκριση της χημικής μηχανής δεν αντιστοιχεί στην αίτηση.'));
              } else finish(null, result);
            }
          };
          worker.onerror = function (event) {
            if (event.preventDefault) event.preventDefault();
            finish(failure('ENGINE_FAILED', 'Η χημική μηχανή δεν μπόρεσε να ολοκληρώσει την ανάλυση.'));
          };
          worker.onmessageerror = function () {
            finish(failure('INVALID_ENGINE_RESULT', 'Η απόκριση της χημικής μηχανής δεν μπορεί να διαβαστεί.'));
          };
          worker.postMessage({ type: 'analyze', requestId: requestId,
            molecule: input, engineSHA256: actualHash, engineURL: sourceURL });
        } catch (error) { finish(error); }
      }).catch(function (error) { finish(error); });
    });
  }

  global.NameleculeChemistryClient = Object.freeze({ analyze: analyze, verifyEngine: verifyEngine });
}(window));
