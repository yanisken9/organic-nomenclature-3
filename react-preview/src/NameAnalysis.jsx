import React from 'react';
import RulePanels from './RulePanels.jsx';
import { validRules } from './rule-data.js';

// Validate the bounded data contract before using any message in React state.
export function validAnalysis(value) {
  return !!value && Array.isArray(value.components) && value.components.length > 0 &&
    value.components.length <= 13 && typeof value.explanation === 'string' && value.explanation.length <= 4000 &&
    value.components.every(c => c && typeof c.id === 'string' && /^comp(?:[0-9]|1[0-2])$/.test(c.id) &&
      typeof c.label === 'string' && c.label.trim().length > 0 && c.label.length <= 128 && typeof c.selected === 'boolean') &&
    new Set(value.components.map(c => c.id)).size === value.components.length &&
    value.components.filter(c => c.selected).length <= 1 && validRules(value.rules);
}

export default function NameAnalysis({ analysis, disabled, onSelect, naming, canSwitchNaming, onNamingChange, ruleContext, rulesPending }) {
  return <section className="react-name-analysis" aria-labelledby="name-analysis-title">
    <h2 id="name-analysis-title">Ονοματολογία</h2>
    {canSwitchNaming && <fieldset className="react-ether-naming" disabled={disabled}>
      <legend>Τρόπος ονομασίας</legend>
      {[['iupac', 'IUPAC'], ['common', 'Κοινή']].map(([value, label]) => <label key={value}>
        <input type="radio" name="ether-naming" value={value} checked={naming === value}
          onChange={() => onNamingChange(value)} />{label}
      </label>)}
    </fieldset>}
    {analysis ? <>
      <div className="react-name-components" role="group" aria-label="Συνθετικά του ονόματος">
        {analysis.components.map(component => <button key={component.id} type="button"
          data-component={component.id} aria-pressed={component.selected} disabled={disabled}
          onClick={() => onSelect(component.id)}>{component.label}</button>)}
      </div>
      <p className="react-name-explanation" role="status" aria-live="polite" aria-atomic="true">{analysis.explanation}</p>
      <RulePanels key={`${ruleContext}:${analysis.components.find(component => component.selected)?.id || 'none'}`}
        rules={analysis.rules} disabled={disabled || rulesPending} />
    </> : <p className="react-name-hint">Η ανάλυση θα εμφανιστεί μαζί με το μόριο.</p>}
  </section>;
}
