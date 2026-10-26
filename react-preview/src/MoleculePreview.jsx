import React, { useEffect, useRef, useState } from 'react';

const channel = 'namelecule-ethanol-v1';
const modes = [['condensed', 'Συνεπτυγμένος'], ['expanded', 'Ανεπτυγμένος'], ['skeletal', 'Σκελετικός']];

export default function MoleculePreview({ mainUrl }) {
  const frame = useRef(null);
  const connection = useRef(null);
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ status: 'loading', mode: 'condensed', zoom: 2 });
  useEffect(() => {
    const session = crypto.randomUUID();
    const current = { session, id: 0, timer: null, ready: false, failed: false };
    connection.current = current;
    const fail = () => {
      if (connection.current !== current) return;
      current.ready = false;
      current.failed = true;
      clearTimeout(current.timer);
      setState(s => ({ ...s, status: 'failed' }));
    };
    function receive(event) {
      const d = event.data;
      if (connection.current !== current || current.failed || event.origin !== location.origin ||
          event.source !== frame.current?.contentWindow || !d || d.channel !== channel || d.session !== session) return;
      if (d.type === 'failed') return fail();
      if (!['ready', 'state'].includes(d.type) || d.molecule !== 'ethanol' ||
          !modes.some(([mode]) => mode === d.mode) || !Number.isFinite(d.zoom) || d.zoom < .5 || d.zoom > 6 ||
          (d.type === 'state' && d.id !== current.id) ||
          (d.type === 'ready' && (current.id !== 0 || current.ready))) return;
      clearTimeout(current.timer);
      current.ready = true;
      setState({ status: 'ready', mode: d.mode, zoom: d.zoom });
    }
    window.addEventListener('message', receive);
    const element = frame.current;
    element.addEventListener('error', fail);
    setState({ status: 'loading', mode: 'condensed', zoom: 2 });
    current.timer = setTimeout(fail, 90000);
    const url = new URL('viewer-host.html', location.href);
    url.hash = '';
    url.search = new URLSearchParams({ session }).toString();
    element.src = url.href;
    return () => {
      connection.current = null;
      clearTimeout(current.timer);
      window.removeEventListener('message', receive);
      element.removeEventListener('error', fail);
      element.src = 'about:blank';
    };
  }, [attempt]);

  function command(command, value) {
    const current = connection.current;
    if (!current?.ready) return;
    const id = ++current.id;
    clearTimeout(current.timer);
    current.timer = setTimeout(() => {
      current.ready = false;
      current.failed = true;
      setState(s => ({ ...s, status: 'failed' }));
    }, 10000);
    if (command === 'mode') setState(s => ({ ...s, mode: value }));
    frame.current.contentWindow.postMessage({ channel, session: current.session, id, command, value }, location.origin);
  }
  const available = state.status === 'ready';
  return <main className="molecule-preview">
    <a href="#/library">← Βιβλιοθήκη θεωρίας</a>
    <h1>Αιθανόλη <span className="molecule-formula">C₂H₆O</span></h1>
    <p>Δοκιμή της 2D προβολής στη React έκδοση.</p>
    <section className="molecule-panel" aria-label="Δισδιάστατη απεικόνιση αιθανόλης">
      <div className="molecule-stage" aria-busy={state.status === 'loading'}>
        <iframe ref={frame} title="Αιθανόλη — 2D μοριακή δομή" hidden={!available} />
        {!available && <div className="molecule-status" role={state.status === 'failed' ? 'alert' : 'status'}>
          {state.status === 'failed' ? <>
            <p>Η απεικόνιση δεν μπόρεσε να φορτωθεί.</p>
            <button onClick={() => setAttempt(n => n + 1)}>Δοκίμασε ξανά</button>
            <a href={mainUrl}>Άνοιξε την κύρια έκδοση</a>
          </> : <p>Φόρτωση αιθανόλης…</p>}
        </div>}
      </div>
      <div className="molecule-controls">
        <fieldset disabled={!available}>
          <legend>Μορφή 2D</legend>
          {modes.map(([value, label]) => <label key={value}>
            <input type="radio" name="mode" value={value} checked={state.mode === value}
              onChange={() => command('mode', value)} />{label}
          </label>)}
        </fieldset>
        <div className="molecule-zoom" role="group" aria-label="Μεγέθυνση">
          <button disabled={!available || state.zoom <= .5} onClick={() => command('zoom', -1)} aria-label="Σμίκρυνση">−</button>
          <button disabled={!available || state.zoom >= 6} onClick={() => command('zoom', 1)} aria-label="Μεγέθυνση">+</button>
        </div>
      </div>
    </section>
  </main>;
}
