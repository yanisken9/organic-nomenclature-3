import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import content from './content.json';
import LibraryPage from './LibraryPage.jsx';
import MoleculePreview from './MoleculePreview.jsx';
import './preview.css';

// dist/ is served under the existing repository: both hosting subpaths and
// the current Python HTTP server resolve the same unchanged legacy files.
const projectRoot = new URL('../../', window.location.href);

function resolveUrl(value, page) {
  if (/^theory-library\.html(?:[?#]|$)/.test(value)) return '#/library';
  if (/^welcome-proposal\.html(?:[?#]|$)/.test(value)) return '#/';
  return new URL(value, new URL(page.source, projectRoot)).href;
}

function reactProps(attrs, page) {
  const props = {};
  for (const [name, value] of Object.entries(attrs)) {
    if (/^on/i.test(name)) continue;
    if (name === 'class') props.className = value;
    else if (name === 'style') {
      props.style = Object.fromEntries(value.split(';').filter(s => s.trim()).map(s => {
        const colon = s.indexOf(':');
        const key = s.slice(0, colon).trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase());
        return [key, s.slice(colon + 1).trim()];
      }));
    } else if (name === 'href' || name === 'src') props[name] = resolveUrl(value, page);
    else if (name === 'tabindex') props.tabIndex = value;
    else if (name === 'viewbox') props.viewBox = value;
    else if (name.startsWith('aria-') || name.startsWith('data-')) props[name] = value;
    else props[name.replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value ?? '';
  }
  return props;
}

function FeatureCard({ node, page, openPanel }) {
  return <article {...reactProps(node.attrs, page)}>
    {renderChildren(node, page, openPanel)}
  </article>;
}

function renderChildren(node, page, openPanel) {
  return node.children.map((child, index) => renderNode(child, index, page, openPanel));
}

function renderNode(node, key, page, openPanel) {
  if (typeof node === 'string') return node;
  if (node.tag === 'script') return null;
  const props = { ...reactProps(node.attrs, page), key };
  if (node.attrs['data-panel']) {
    props.onClick = event => openPanel(node.attrs['data-panel'], event.currentTarget);
  }
  if (node.tag === 'article') {
    return <FeatureCard key={key} node={node} page={page} openPanel={openPanel} />;
  }
  const children = renderChildren(node, page, openPanel);
  return React.createElement(node.tag, props, ...(children.length ? children : []));
}

function SiteHeader({ page, openPanel }) {
  return renderNode(page.header, 'header', page, openPanel);
}

function SiteFooter({ page, openPanel }) {
  return renderNode(page.footer, 'footer', page, openPanel);
}

function PanelDialog({ panel, onClose }) {
  const dialog = useRef(null);
  useEffect(() => {
    if (!panel) return;
    const element = dialog.current;
    if (!element.open) element.showModal();
    return () => { if (element.open) element.close(); };
  }, [panel]);
  if (!panel) return null;
  const [title, copy, linkLabel, linkUrl] = content.panels[panel.name];
  return <dialog ref={dialog} aria-labelledby="dialog-title" onClose={event => {
    if (!event.currentTarget.open) onClose();
  }}>
    <h2 id="dialog-title">{title}</h2>
    <p>{copy}</p>
    {linkLabel && <a href={resolveUrl(linkUrl, content.welcome)}>{linkLabel}</a>}
    <form method="dialog"><button>Κλείσιμο</button></form>
  </dialog>;
}

function App() {
  const [route, setRoute] = useState(() => window.location.hash);
  const [panel, setPanel] = useState(null);
  const [filters, setFilters] = useState({ query: '', categoryId: '' });
  const library = route === '#/library';
  const viewer = route === '#/viewer';
  const page = library || viewer ? content.library : content.welcome;
  useEffect(() => {
    const onHashChange = () => {
      setRoute(window.location.hash);
      setPanel(null);
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);
  useEffect(() => {
    document.title = (viewer ? 'Αιθανόλη' : page.title) + ' — Namelecule React';
  }, [page, viewer]);
  function openPanel(name, trigger) { setPanel({ name, trigger }); }
  function closePanel() {
    panel?.trigger?.focus();
    setPanel(null);
  }
  // Welcome contains its footer within main; the library puts it after main.
  const hasFooterInMain = !library && !viewer && page.main.children.some(node => typeof node !== 'string' && node.tag === 'footer');
  return <>
    <style>{page.styles}</style>
    <aside className="react-preview-banner" aria-label="Δοκιμαστική έκδοση">
      <span>Namelecule React — Δοκιμαστική έκδοση</span>
      <a href="#/viewer">2D δοκιμή · Αιθανόλη</a>
      <a href={new URL('design/welcome-proposal.html', projectRoot).href}>Κύρια έκδοση</a>
    </aside>
    <SiteHeader page={page} openPanel={openPanel} />
    {viewer ? <MoleculePreview mainUrl={new URL('design/welcome-proposal.html', projectRoot).href} />
      : library ? <LibraryPage catalog={content.library} filters={filters} setFilters={setFilters}
      resolveHref={href => resolveUrl(href, content.library)} />
      : renderNode(page.main, 'main', page, openPanel)}
    {!hasFooterInMain && <SiteFooter page={page} openPanel={openPanel} />}
    {!library && !viewer && <div className="preview-note">Η βιβλιοθήκη θεωρίας είναι διαθέσιμη. Η σύνδεση και τα παιχνίδια είναι υπό σχεδιασμό.</div>}
    <PanelDialog panel={panel} onClose={closePanel} />
  </>;
}

createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>);
