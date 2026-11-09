// Build metadata with the unchanged main engine, never another naming algorithm.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const context = vm.createContext({ window: {}, console });
vm.runInContext(read('js/jsme-nick-nomeclature-moc2-data_52.js'), context);
vm.runInContext(read('js/mulermoc-nom-core-52.js'), context);
const teaching = read('js/mulermoc-nom-teaching-52.js');
const labels = teaching.match(/const homologousSeriesLabels = \{[\s\S]*?\n\};/);
assert(labels, 'Main series labels unavailable');
vm.runInContext(labels[0], context);

// Only the four JSME graph-access methods consumed by fAnalyseStructure.
// Names/classification/parent selection are calculated by the existing core.
function moleculeApi(mol) {
  const lines = mol.split(/\r?\n/);
  assert(lines[3].includes('V2000'));
  const n = +lines[3].slice(0, 3), m = +lines[3].slice(3, 6);
  const atoms = lines.slice(4, 4 + n).map(line => ({ label: line.slice(31, 34).trim() }));
  const bonds = lines.slice(4 + n, 4 + n + m).map(line => ({
    atoms: [+line.slice(0, 3), +line.slice(3, 6)], order: +line.slice(6, 9),
  }));
  assert(atoms.length === n && bonds.length === m);
  return { totalNumberOfAtoms: () => n, totalNumberOfBonds: () => m,
    getAtom: (_, i) => atoms[i - 1], getBond: (_, i) => bonds[i - 1] };
}
context.mode2D = 'condensed';
context.mainChainMode = 'algorithmic';
vm.runInContext('fInitNamingProps()', context);
const entries = vm.runInContext('Object.keys(nameExamples)', context);
const catalog = entries.map(id => {
  assert(/^[A-Za-z0-9_]+$/.test(id), id);
  const forms = context.window.MOL2D[id];
  assert(forms && typeof forms.condensed === 'string', id);
  const modes = ['condensed', 'expanded', 'skeletal'].filter(k => typeof forms[k] === 'string');
  context.jsmeNomeclatureApplet = moleculeApi(forms.condensed);
  context.selectedMol = id;
  const metadata = vm.runInContext(`(()=>{
    mainChainPoolIdx=0; carbonHydrogens=[];
    fAnalyseStructure(); fDetectMolType();
    const classification=fGetMoleculeClassification(); fGuessName();
    return {title:currentMolName, commonName:currentMolCommonName||'',
      structuralFormula:nameExamples[selectedMol].formula, series:classification.seriesKey,
      seriesLabel:homologousSeriesLabels[classification.seriesKey]||classification.taxonomy,
      carbonCount:classification.carbonCount};
  })()`, context);
  // Formula is a count of the existing explicit-H SDF, not inferred chemistry.
  const sdf = read(`mols/nomeclature-moc2/${id}_3D.sdf`).split(/\r?\n/);
  assert(!sdf[3].includes('V3000') && +sdf[3].slice(0, 3) > 0, id);
  const counts = {};
  for (const line of sdf.slice(4, 4 + +sdf[3].slice(0, 3))) {
    const symbol = line.slice(31, 34).trim();
    assert(/^[A-Z][a-z]?$/.test(symbol), id);
    counts[symbol] = (counts[symbol] || 0) + 1;
  }
  const subs = number => String(number).replace(/\d/g, digit => '₀₁₂₃₄₅₆₇₈₉'[+digit]);
  const formula = ['C', 'H', ...Object.keys(counts).filter(k => !['C', 'H'].includes(k)).sort()]
    .filter(k => counts[k]).map(k => k + (counts[k] > 1 ? subs(counts[k]) : '')).join('');
  assert(metadata.title && metadata.series && metadata.seriesLabel && counts.C === metadata.carbonCount, id);
  return { id, ...metadata, formula, modes };
});
// Preserve the main application's increasing-carbon order, including stable ties.
catalog.sort((a, b) => a.carbonCount - b.carbonCount);
const destination = path.join(root, 'react-preview/src/molecules.json');
const output = JSON.stringify(catalog, null, 2) + '\n';
if (process.argv.includes('--check')) assert.equal(fs.readFileSync(destination, 'utf8'), output, 'Rebuild molecule catalog');
else fs.writeFileSync(destination, output);
console.log(`Molecule catalog ${process.argv.includes('--check') ? 'matches main v52' : 'generated'}: ${catalog.length}`);
