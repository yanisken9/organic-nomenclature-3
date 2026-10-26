/* Classic script: access existing lexical app state without changing its engine. */
(() => {
  'use strict';
  const channel = 'namelecule-ethanol-v1';
  const session = new URLSearchParams(location.search).get('session');
  if (!session || parent === window) return;
  let ready = false;
  let lastId = 0;
  let stopped = false;
  const send = data => parent.postMessage({ channel, session, ...data }, location.origin);
  function state() {
    return { mode: mode2D, zoom: molZoom2D, molecule: selectedMol };
  }
  function fail() {
    stopped = true;
    clearInterval(poll);
    send({ type: 'failed' });
  }
  function onMessage(event) {
    const d = event.data;
    if (!ready || stopped || event.origin !== location.origin || event.source !== parent ||
        !d || d.channel !== channel || d.session !== session ||
        !Number.isSafeInteger(d.id) || d.id <= lastId) return;
    if (!(d.command === 'mode' && ['condensed', 'expanded', 'skeletal'].includes(d.value)) &&
        !(d.command === 'zoom' && (d.value === 1 || d.value === -1))) return;
    lastId = d.id;
    try {
      if (d.command === 'mode') {
        const index = ['condensed', 'expanded', 'skeletal'].indexOf(d.value);
        $('#radio2DMode .mode2DOption').eq(index).trigger('click');
      } else fZoom2D(d.value);
      send({ type: 'state', id: d.id, ...state() });
    } catch (error) {
      console.error('Ethanol preview command failed', error);
      fail();
    }
  }
  window.addEventListener('message', onMessage);
  const started = Date.now();
  const poll = setInterval(() => {
    if (Date.now() - started > 85000) return fail();
    if (typeof jsmeNomeclatureApplet === 'undefined' || !jsmeNomeclatureApplet ||
        typeof nameExamples === 'undefined' || !nameExamples.ethanol?.classification ||
        !window.JSmolReadyFlag || typeof selectedMol === 'undefined' || !selectedMol) return;
    clearInterval(poll);
    try {
      selectedMol = 'ethanol';
      fSelectMol();
      document.getElementById('nomeclature3D').style.display = 'none';
      fResizeViewers();
      if (!document.querySelector('#jsmeNomeclatureSVG svg text')) return fail();
      ready = true;
      send({ type: 'ready', ...state() });
    } catch (error) {
      console.error('Ethanol preview initialization failed', error);
      fail();
    }
  }, 100);
  window.addEventListener('pagehide', () => {
    stopped = true;
    clearInterval(poll);
    window.removeEventListener('message', onMessage);
  }, { once: true });
})();
