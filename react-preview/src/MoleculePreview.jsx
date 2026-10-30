import React, { useEffect, useRef, useState } from 'react';
import molecules from './molecules.json';
import NameAnalysis, { validAnalysis } from './NameAnalysis.jsx';
import { filterMolecules } from './molecule-search.js';

const channel = 'namelecule-viewer-v4';
const initialMolecule = 'ethanol';
const initial3D = { hydrogens: true, labels: true, rotating: false, style: 'ballnstick' };
const styles3D = [['ballnstick', 'Σφαίρες και ράβδοι'], ['spacefill', 'Χωροπληρωτικό'], ['sticks', 'Ράβδοι']];
const controls3DCommands = { hydrogens3d: 'hydrogens', labels3d: 'labels', rotation3d: 'rotating', style3d: 'style' };
const initialState = { status: 'loading', failure: null, view: '2d', molecule: initialMolecule, mode: 'condensed', symbols: false, symbolsBusy: false, exportStatus: null, naming: 'iupac', zoom: 2, pending: false, analysis: null, ruleRevision: 0, rulesPending: false, controls3D: initial3D };
const modes = [['condensed', 'Συνεπτυγμένος'], ['expanded', 'Ανεπτυγμένος'], ['skeletal', 'Σκελετικός']];

export default function MoleculePreview({ mainUrl }) {
  const frame = useRef(null);
  const connection = useRef(null);
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState(initialState);
  const [query, setQuery] = useState('');
  const [series, setSeries] = useState('');
  const search = useRef(null);
  useEffect(() => {
    const session = crypto.randomUUID();
    const current = { session, id: 0, ackId: 0, exportId: null, exportDeadline: 0, timer: null, ready: false, failed: false, molecule: initialMolecule, mode: 'condensed', symbols: false, view: '2d', naming: 'iupac', analysis: null, controls3D: { ...initial3D } };
    connection.current = current;
    const fail = reason => {
      if (connection.current !== current) return;
      current.ready = false;
      current.failed = true;
      clearTimeout(current.timer);
      setState(s => ({ ...s, status: 'failed', failure: reason === 'export' ? 'export' : null, pending: false, analysis: null, exportStatus: null }));
    };
    function receive(event) {
      const d = event.data;
      if (connection.current !== current || current.failed || event.origin !== location.origin ||
          event.source !== frame.current?.contentWindow || !d || d.channel !== channel || d.session !== session) return;
      if (d.type === 'failed') return fail(d.reason);
      if (!validAnalysis(d.analysis) || !['ready', 'state'].includes(d.type) || d.molecule !== current.molecule || d.mode !== current.mode || d.view !== current.view ||
          !d.controls3D || Object.keys(initial3D).some(key => d.controls3D[key] !== current.controls3D[key]) ||
          typeof d.symbols !== 'boolean' || d.symbols !== current.symbols || (d.symbols && d.mode !== 'skeletal') ||
          (current.exportId === d.id ? !['requested', 'failed'].includes(d.exportStatus) : d.exportStatus !== undefined) ||
          !['iupac', 'common'].includes(d.naming) || d.naming !== current.naming ||
          !d.model || d.model.file !== new URL('../../mols/nomeclature-moc2/' + current.molecule + '_3D.sdf', location.href).href ||
          !Number.isInteger(d.model.atoms) || d.model.atoms <= 0 || !Number.isInteger(d.model.bonds) || d.model.bonds <= 0 ||
          !modes.some(([mode]) => mode === d.mode) || !Number.isFinite(d.zoom) || d.zoom < .5 || d.zoom > 6 ||
          (d.type === 'state' && d.id !== current.id) ||
          (d.type === 'ready' && (current.id !== 0 || current.ready))) return;
      clearTimeout(current.timer);
      current.ready = true;
      current.analysis = d.analysis;
      current.ackId = current.id;
      current.exportDeadline = 0;
      setState(previous => ({ ...previous, status: 'ready', view: d.view, molecule: d.molecule, mode: d.mode, symbols: d.symbols, symbolsBusy: false, exportStatus: d.exportStatus || null, naming: d.naming, zoom: d.zoom, pending: false, analysis: d.analysis, rulesPending: false, controls3D: { ...current.controls3D } }));
    }
    window.addEventListener('message', receive);
    const element = frame.current;
    element.addEventListener('error', fail);
    setState(initialState);
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
    if (Object.hasOwn(controls3DCommands, command)) {
      const key = controls3DCommands[command];
      if (state.pending || current.ackId !== current.id || !current.analysis || current.view !== '3d' ||
          (key === 'style' ? !styles3D.some(([style]) => style === value) : typeof value !== 'boolean') ||
          value === current.controls3D[key]) return;
      current.controls3D = { ...current.controls3D, [key]: value };
      setState(s => ({ ...s, pending: true }));
    }
    if (command === 'molecule') {
      if (!molecules.some(m => m.id === value) || value === current.molecule) return;
      current.molecule = value;
      current.analysis = null;
      const next = molecules.find(m => m.id === value);
      if (!next.modes.includes(current.mode)) current.mode = next.modes[0];
      if (current.mode !== 'skeletal') current.symbols = false;
      setState(s => ({ ...s, molecule: value, mode: current.mode, symbols: current.symbols, zoom: 2, pending: true, analysis: null }));
    }
    if (command === 'view') {
      if (!['2d', '3d'].includes(value) || value === current.view) return;
      current.view = value;
      setState(s => ({ ...s, view: value, pending: true }));
    }
    if (command === 'component') {
      if (!current.analysis?.components.some(c => c.id === value)) return;
      setState(previous => ({ ...previous, ruleRevision: previous.ruleRevision + 1, rulesPending: true }));
    }
    if (command === 'naming') {
      if (state.pending || molecules.find(m => m.id === current.molecule).series !== 'ether' ||
          !['iupac', 'common'].includes(value) || value === current.naming) return;
      current.naming = value;
      current.analysis = null;
      setState(s => ({ ...s, naming: value, pending: true, analysis: null }));
    }
    if (command === 'mode') {
      if (!molecules.find(m => m.id === current.molecule).modes.includes(value)) return;
      current.mode = value;
      current.symbols = false;
    }
    if (command === 'symbols') {
      if (state.pending || current.ackId !== current.id || !current.analysis || current.view !== '2d' || current.mode !== 'skeletal' ||
          !molecules.find(m => m.id === current.molecule).modes.includes('skeletal') ||
          typeof value !== 'boolean' || value === current.symbols) return;
      current.symbols = value;
      setState(s => ({ ...s, symbols: value, pending: true }));
    }
    if (command === 'export' && (value !== 'png' || state.pending || current.ackId !== current.id ||
        !current.analysis || !['2d', '3d'].includes(current.view))) return;
    const id = ++current.id;
    current.exportId = command === 'export' ? id : null;
    if (command === 'export' && current.view === '3d') current.exportDeadline = Date.now() + 100000;
    // Wait for the latest ACK before annotating a possibly queued 2D mode.
    setState(s => ({ ...s, symbolsBusy: true, exportStatus: command === 'export' ? 'preparing' : null }));
    clearTimeout(current.timer);
    current.timer = setTimeout(() => {
      current.ready = false;
      current.failed = true;
      setState(s => ({ ...s, status: 'failed', failure: current.exportId === current.id ? 'export' : null, pending: false, analysis: null, exportStatus: null }));
    }, Math.max(10000, current.exportDeadline - Date.now()));
    if (command === 'mode') setState(s => ({ ...s, mode: value, symbols: false }));
    frame.current.contentWindow.postMessage({ channel, session: current.session, id, command, value, molecule: current.molecule,
      ...(command === 'export' ? { view: current.view, controls3D: { ...current.controls3D }, mode: current.mode, symbols: current.symbols, naming: current.naming,
        component: current.analysis.components.find(c => c.selected)?.id || null } : {}) }, location.origin);
  }
  const available = state.status === 'ready';
  const selected = molecules.find(m => m.id === state.molecule);
  const visible = available && !state.pending;
  const matches = filterMolecules(molecules, query, series);
  const seriesOptions = [...new Map(molecules.map(m => [m.series, m.seriesLabel]))];
  const selectionMatches = matches.some(m => m.id === state.molecule);
  return <main className="molecule-preview">
    <a href="#/library">← Βιβλιοθήκη θεωρίας</a>
    <h1>{selected.title} <span className="molecule-formula">{selected.formula}</span></h1>
    <p>Εξερεύνησε τα μόρια σε 2D και 3D και τα συνθετικά των ονομάτων τους.</p>
    <div className="molecule-filters">
      <label>Αναζήτηση μορίου
        <input ref={search} type="search" value={query} onChange={event => setQuery(event.target.value)}
          placeholder="Όνομα ή τύπος" aria-describedby="molecule-results" />
      </label>
      <label>Ομόλογη σειρά
        <select id="molecule-series" value={series} onChange={event => setSeries(event.target.value)}>
          <option value="">Όλες οι σειρές</option>
          {seriesOptions.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
        </select>
      </label>
      <button type="button" disabled={!query && !series} onClick={() => {
        setQuery(''); setSeries(''); search.current.focus();
      }}>Καθαρισμός</button>
    </div>
    <p id="molecule-results" role="status" aria-live="polite">{matches.length} από {molecules.length} μόρια
      {!matches.length && ' — Δεν βρέθηκαν μόρια.'}</p>
    <div className="molecule-picker">
      <label htmlFor="molecule-select">Μόριο</label>
      <select id="molecule-select" value={state.molecule} disabled={!available}
        onChange={event => command('molecule', event.target.value)}>
        {!selectionMatches && <optgroup label="Τρέχον μόριο — εκτός φίλτρου">
          <option value={selected.id}>{selected.title}</option>
        </optgroup>}
        {seriesOptions.map(([id, label]) => {
          const group = matches.filter(m => m.series === id);
          return group.length > 0 && <optgroup key={id} label={label}>
            {group.map(m => <option key={m.id} value={m.id}>{m.title}</option>)}
          </optgroup>;
        })}
      </select>
    </div>
    <div className="molecule-views" role="group" aria-label="Προβολή μορίου">
      {['2d', '3d'].map(view => <button key={view} type="button" data-view={view}
        aria-pressed={state.view === view} disabled={!available}
        onClick={() => command('view', view)}>{view.toUpperCase()}</button>)}
    </div>
    <div className="molecule-workspace">
    <section className="molecule-panel" aria-label={`Μοριακή απεικόνιση: ${selected.title}`}>
      <div className="molecule-stage" aria-busy={state.status === 'loading' || state.pending}>
        <iframe ref={frame} title={`${selected.title} — ${state.view.toUpperCase()} μοριακή δομή`} hidden={!visible} />
        {!visible && <div className="molecule-status" role={state.status === 'failed' ? 'alert' : 'status'}>
          {state.status === 'failed' ? <>
            <p>{state.failure === 'export' ? 'Η λήψη PNG δεν ξεκίνησε. Δοκίμασε ξανά.' : 'Η απεικόνιση δεν μπόρεσε να φορτωθεί.'}</p>
            <button onClick={() => setAttempt(n => n + 1)}>Δοκίμασε ξανά</button>
            <a href={mainUrl}>Άνοιξε την κύρια έκδοση</a>
          </> : <p>Φόρτωση μορίου…</p>}
        </div>}
      </div>
      <div className="molecule-controls">
        {state.view === '3d' && <fieldset className="molecule-controls-3d" disabled={!visible || state.symbolsBusy}>
          <legend>Μορφή 3D</legend>
          <label>Μοντέλο
            <select id="style-3d" value={state.controls3D.style} onChange={event => command('style3d', event.target.value)}>
              {styles3D.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <label><input id="hydrogens-3d" type="checkbox" checked={state.controls3D.hydrogens}
            onChange={event => command('hydrogens3d', event.target.checked)} />Υδρογόνα C–H</label>
          <label><input id="labels-3d" type="checkbox" checked={state.controls3D.labels}
            onChange={event => command('labels3d', event.target.checked)} />Σύμβολα ατόμων</label>
          <label><input id="rotation-3d" type="checkbox" checked={state.controls3D.rotating}
            onChange={event => command('rotation3d', event.target.checked)} />Περιστροφή</label>
        </fieldset>}
        <fieldset disabled={!available || state.view !== '2d'}>
          <legend>Μορφή 2D</legend>
          {modes.map(([value, label]) => <label key={value}>
            <input type="radio" name="mode" value={value} checked={state.mode === value} disabled={!selected.modes.includes(value)}
              onChange={() => command('mode', value)} />{label}
          </label>)}
          <label>
            <input type="checkbox" id="skeletal-symbols" checked={state.symbols}
              disabled={state.pending || state.symbolsBusy || state.mode !== 'skeletal' || !selected.modes.includes('skeletal')}
              onChange={event => command('symbols', event.target.checked)} /><span>Σύμβολα CH<sub>n</sub></span>
          </label>
        </fieldset>
        <div className="molecule-zoom" role="group" aria-label="Μεγέθυνση">
          <button disabled={!available || state.pending || (state.view === '2d' && state.zoom <= .5)} onClick={() => command('zoom', -1)} aria-label="Σμίκρυνση">−</button>
          <button disabled={!available || state.pending || (state.view === '2d' && state.zoom >= 6)} onClick={() => command('zoom', 1)} aria-label="Μεγέθυνση">+</button>
        </div>
        <button type="button" id={state.view === '3d' ? 'save-3d-png' : 'save-2d-png'} disabled={!visible || state.symbolsBusy}
          onClick={() => command('export', 'png')}>Αποθήκευση PNG ({state.view.toUpperCase()})</button>
      </div>
      {state.exportStatus && <p className="molecule-export-status" role="status" aria-live="polite" aria-atomic="true">
        {state.exportStatus === 'preparing' ? 'Προετοιμασία PNG…' : state.exportStatus === 'requested'
          ? 'Ζητήθηκε λήψη PNG.' : 'Η λήψη δεν ξεκίνησε. Δοκίμασε ξανά.'}
      </p>}
    </section>
    <NameAnalysis analysis={state.analysis} disabled={!visible} onSelect={id => command('component', id)}
      naming={state.naming} canSwitchNaming={selected.series === 'ether'} onNamingChange={value => command('naming', value)}
      ruleContext={`${state.molecule}:${state.naming}:${state.ruleRevision}`} rulesPending={state.rulesPending} />
    </div>
  </main>;
}
