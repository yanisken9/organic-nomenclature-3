import { normalizeGreek } from './library-search.js';

export function filterMolecules(molecules, query, series) {
  const normalize = value => normalizeGreek(value.normalize('NFKD'));
  const terms = normalize(query).split(/\s+/).filter(Boolean);
  return molecules.filter(molecule => (!series || molecule.series === series) &&
    terms.every(term => normalize([molecule.title, molecule.commonName,
      molecule.formula, molecule.structuralFormula, molecule.seriesLabel].join(' ')).includes(term)));
}
