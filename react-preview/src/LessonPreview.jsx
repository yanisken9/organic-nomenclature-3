import React, { useEffect, useRef, useState } from 'react';

const channel = 'namelecule-lesson-v1';
export const lessonRoute = (id, step) => `#/lesson/${id}/step/${step}`;

export function resolveLessonRoute(route, lessons) {
  const match = /^#\/lesson\/([a-z][a-z0-9-]*)\/step\/([1-9]\d*)$/.exec(route);
  const lesson = match && lessons.find(entry => entry.id === match[1]);
  const step = match ? Number(match[2]) : 0;
  return lesson && Number.isInteger(step) && step >= 1 && step <= lesson.steps ? { lesson, step } : null;
}

export default function LessonPreview({ step, lesson, mainUrl }) {
  const valid = !!lesson;
  const routeFor = next => lessonRoute(lesson.id, next);
  const frame = useRef(null);
  const connection = useRef(null);
  const desired = useRef(step);
  desired.current = step;
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ status: 'loading', step, title: '', height: 900 });

  useEffect(() => {
    if (!valid) return;
    const current = { session: crypto.randomUUID(), id: 0, expected: desired.current, ready: false, failed: false, timer: null };
    connection.current = current;
    setState({ status: 'loading', step: desired.current, title: '', height: 900 });
    function fail() {
      if (connection.current !== current || current.failed) return;
      current.failed = true; current.ready = false;
      clearTimeout(current.timer);
      setState(s => ({ ...s, status: 'failed' }));
    }
    function go(next) {
      if (!current.ready || current.failed || next === current.expected) return;
      current.ready = false; current.expected = next; ++current.id;
      setState(s => ({ ...s, status: 'loading' }));
      clearTimeout(current.timer);
      current.timer = setTimeout(fail, 18000);
      frame.current?.contentWindow.postMessage({ channel, session: current.session, lesson: lesson.id, command: 'step', id: current.id, step: next }, location.origin);
    }
    current.go = go;
    function navigate(delta) {
      if (!current.ready || current.failed) return;
      const next = desired.current + delta;
      if (next >= 1 && next <= lesson.steps) location.hash = routeFor(next);
    }
    function receive(event) {
      const d = event.data;
      if (connection.current !== current || current.failed || event.origin !== location.origin ||
          event.source !== frame.current?.contentWindow || !d || d.channel !== channel ||
          d.session !== current.session || d.lesson !== lesson.id) return;
      if (d.type === 'failed') return fail();
      if (d.type === 'exit') { location.hash = '#/library'; return; }
      if (d.type === 'navigate' && [-1, 1].includes(d.delta)) { navigate(d.delta); return; }
      if (d.type === 'busy') {
        if (d.id === current.id && d.step === current.expected) setState(s => ({ ...s, status: 'loading' }));
        return;
      }
      if (!Number.isInteger(d.height) || d.height < 420 || d.height > 12000) return;
      if (d.type === 'height') {
        if (current.ready) setState(s => ({ ...s, height: d.height }));
        return;
      }
      if (d.type !== 'state' || d.id !== current.id || d.step !== current.expected || d.total !== lesson.steps ||
          typeof d.title !== 'string' || !d.title || d.title.length > 200) return;
      clearTimeout(current.timer);
      current.ready = true;
      if (desired.current !== d.step) { go(desired.current); return; }
      setState({ status: 'ready', step: d.step, title: d.title, height: d.height });
    }
    function keydown(event) {
      if (event.ctrlKey || event.metaKey || event.altKey || event.target.closest?.('input,textarea,select,[contenteditable="true"],dialog')) return;
      if (event.key === 'Escape') { event.preventDefault(); location.hash = '#/library'; }
      else if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
        event.preventDefault(); navigate(event.key === 'ArrowLeft' ? -1 : 1);
      }
    }
    const viewportHeight = () => Math.max(420, Math.min(12000, Math.round(innerHeight)));
    function resize() {
      if (connection.current !== current || current.failed) return;
      frame.current?.contentWindow.postMessage({ channel, session: current.session, lesson: lesson.id,
        command: 'viewport', height: viewportHeight() }, location.origin);
    }
    const target = new URL('./lesson-host.html', location.href);
    target.search = new URLSearchParams({ session: current.session, lesson: lesson.id, scenario: lesson.scenario, present: '1', viewportHeight: String(viewportHeight()) });
    target.hash = `step=${current.expected}`;
    window.addEventListener('message', receive);
    window.addEventListener('keydown', keydown);
    window.addEventListener('resize', resize);
    const iframe = frame.current;
    iframe.addEventListener('error', fail);
    current.timer = setTimeout(fail, 90000);
    iframe.src = target.href;
    return () => {
      connection.current = null; clearTimeout(current.timer);
      window.removeEventListener('message', receive);
      window.removeEventListener('keydown', keydown);
      window.removeEventListener('resize', resize);
      iframe.removeEventListener('error', fail);
      iframe.removeAttribute('src');
    };
  }, [attempt, valid, lesson]);

  useEffect(() => { if (valid) connection.current?.go(step); }, [step, valid]);
  const ready = valid && state.status === 'ready' && state.step === step;
  return <main className="lesson-preview">
    <a href="#/library">← Βιβλιοθήκη θεωρίας</a>
    <h1>{lesson?.heading || 'Μάθημα θεωρίας'}</h1>
    {!valid ? <div role="alert"><p>Το μάθημα ή το βήμα δεν υπάρχει. Επίλεξε μάθημα από τη βιβλιοθήκη.</p></div> : <>
      <nav className="lesson-navigation" aria-label="Πλοήγηση μαθήματος">
        <button id="lesson-prev" type="button" disabled={!ready || step === 1} onClick={() => { location.hash = routeFor(step - 1); }}>← Προηγούμενο</button>
        <span id="lesson-position" role="status" aria-live="polite" aria-atomic="true">{step}/{lesson.steps}</span>
        <button id="lesson-next" type="button" disabled={!ready || step === lesson.steps} onClick={() => { location.hash = routeFor(step + 1); }}>Επόμενο →</button>
        <a href="#/library">Έξοδος</a>
      </nav>
      <p className="lesson-step-summary" aria-live="polite">{ready ? state.title : ''}</p>
      <section className="lesson-stage" aria-label="Περιεχόμενο μαθήματος" aria-busy={state.status === 'loading'}>
        <iframe ref={frame} title={`${lesson.heading} — θεωρία και μοριακές απεικονίσεις`} style={{ height: state.height }} hidden={!ready} />
        {!ready && <div className="lesson-status" role={state.status === 'failed' ? 'alert' : 'status'}>
          {state.status === 'failed' ? <>
            <p>Το μάθημα δεν μπόρεσε να φορτωθεί.</p>
            <button type="button" onClick={() => setAttempt(n => n + 1)}>Δοκίμασε ξανά</button>
            <a href={mainUrl}>Άνοιξε το μάθημα στην Κύρια έκδοση</a>
          </> : <p>Φόρτωση βήματος…</p>}
        </div>}
      </section>
    </>}
  </main>;
}
