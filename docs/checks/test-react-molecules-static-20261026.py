"""Read-only C/H/O graph checks for the nine source MOLs captured by Firefox.

This checks neutral acyclic examples only; it is not a general MOL validator.
Supply the actual browser evidence JSON as argv[1]. No files are generated.
"""
import collections
import hashlib
import itertools
import json
import sys
from pathlib import Path

expected = {
    'ethanol': {'C': 2, 'H': 6, 'O': 1},
    'dimethyl_2_3_butane': {'C': 6, 'H': 14},
    'propanone': {'C': 3, 'H': 6, 'O': 1},
}

def parse_mol(source):
    lines = source.splitlines()
    counts = next(i for i, line in enumerate(lines) if 'V2000' in line)
    n, m = int(lines[counts][:3]), int(lines[counts][3:6])
    atoms = [line[31:34].strip() for line in lines[counts + 1:counts + 1 + n]]
    assert len(atoms) == n and set(atoms) <= {'C', 'H', 'O'}
    valence = [0] * n
    bonds = {}
    for line in lines[counts + 1 + n:counts + 1 + n + m]:
        a, b, order = int(line[:3]) - 1, int(line[3:6]) - 1, int(line[6:9])
        assert 0 <= a < n and 0 <= b < n and a != b and order in (1, 2, 3)
        edge = tuple(sorted((a, b)))
        assert edge not in bonds
        bonds[edge] = order
        valence[a] += order
        valence[b] += order
    assert len(bonds) == m
    formula = collections.Counter(atoms)
    for atom, v in zip(atoms, valence):
        assert v <= {'C': 4, 'O': 2, 'H': 1}[atom]
        if atom == 'H':
            assert v == 1
        else:
            formula['H'] += {'C': 4, 'O': 2}[atom] - v
    heavy = [i for i, a in enumerate(atoms) if a != 'H']
    heavy_bonds = {(heavy.index(a), heavy.index(b)): order for (a, b), order in bonds.items()
                   if a in heavy and b in heavy}
    return {'atoms': len(atoms), 'bonds': len(bonds), 'explicitH': atoms.count('H'),
            'formula': dict(formula), 'elements': [atoms[i] for i in heavy], 'edges': heavy_bonds}

def isomorphic(a, b):
    if collections.Counter(a['elements']) != collections.Counter(b['elements']):
        return False
    for perm in itertools.permutations(range(len(b['elements']))):
        if any(x != b['elements'][perm[i]] for i, x in enumerate(a['elements'])):
            continue
        mapped = {tuple(sorted((perm[i], perm[j]))): o for (i, j), o in a['edges'].items()}
        if mapped == b['edges']:
            return True
    return False

if __name__ == '__main__':
    evidence = json.loads(Path(sys.argv[1]).read_text())
    assert evidence['completed'] and all(all(m.values()) for m in evidence['exactSVGParity'].values())
    catalog = json.loads(Path('react-preview/src/molecules.json').read_text())
    assert set(expected) == {m['id'] for m in catalog} == set(evidence['sourceMOLs'])
    result = {}
    for key, forms in evidence['sourceMOLs'].items():
        assert set(forms) == {'Condensed', 'Expanded', 'Skeletal'}
        parsed = {mode: parse_mol(mol) for mode, mol in forms.items()}
        assert all(p['formula'] == expected[key] for p in parsed.values()), (key, parsed)
        assert all(isomorphic(parsed['Condensed'], p) for p in parsed.values()), key
        result[key] = {mode: {k: v for k, v in p.items() if k not in ('elements', 'edges')}
                       for mode, p in parsed.items()}
        result[key]['sourceSHA256'] = {mode: hashlib.sha256(mol.encode()).hexdigest() for mode, mol in forms.items()}
    print(json.dumps({'passed': True, 'molecules': result}, ensure_ascii=False, indent=2))
