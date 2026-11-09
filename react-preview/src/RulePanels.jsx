import React, { useId, useState } from 'react';

function renderNodes(nodes) {
  return nodes.map((node, key) => typeof node === 'string' ? node :
    React.createElement(node.tag, { key, className: node.classes.join(' ') || undefined,
      'data-row': node.row ?? undefined }, ...renderNodes(node.children)));
}

export default function RulePanels({ rules, disabled }) {
  const id = useId();
  const [open, setOpen] = useState([]);
  return rules.map(rule => {
    const expanded = open.includes(rule.id);
    const bodyId = `${id}-${rule.id}`;
    return <section key={rule.id} className="react-rule-panel" data-rule={rule.id}>
      <button type="button" className="react-rule-toggle" disabled={disabled}
        aria-expanded={expanded} aria-controls={bodyId}
        onClick={() => setOpen(previous => expanded ? previous.filter(key => key !== rule.id) : [...previous, rule.id])}>
        <span aria-hidden="true">{expanded ? '−' : '+'}</span> {rule.title}
      </button>
      <div id={bodyId} className="react-rule-body" hidden={!expanded}>
        <div className={['ruleText', ...rule.textClasses].join(' ')}>{renderNodes(rule.text)}</div>
        <div className="ruleTable">{renderNodes(rule.table)}</div>
      </div>
    </section>;
  });
}
