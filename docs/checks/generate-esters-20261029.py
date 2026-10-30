"""Five approved saturated monoesters; preserve heavy-atom IDs across 2D forms.

Explicit-H PubChem 3D is used only after graph/formula/stereo validation.
The documented RDKit fallback is an illustrative conformer, not an R/S claim.
Writes only new files in --output, refusing to overwrite existing assets.
"""
from pathlib import Path
import argparse, hashlib, io, json, math
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, rdDepictor, rdMolDescriptors
from rdkit.Geometry import Point2D

SPECS = json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())


def graph(s):
    rw = Chem.RWMol()
    for symbol in ['C'] * s['carbons'] + ['O', 'O']:
        rw.AddAtom(Chem.Atom(symbol))
    for a, b, order in s['edges']:
        rw.AddBond(a-1, b-1, Chem.BondType.DOUBLE if order == 2 else Chem.BondType.SINGLE)
    m = rw.GetMol()
    Chem.SanitizeMol(m)
    assert Chem.MolToSmiles(m) == Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']))
    assert rdMolDescriptors.CalcMolFormula(m) == s['formula']
    return m


def forms(s):
    # Drawing proportions measured from the four pre-existing ChemDraw esters.
    # Expanded school diagrams use orthogonal bonds and enough C-C spacing
    # for cardinal H arms. These are diagram units, not physical lengths.
    m = graph(s)
    xy = [list(p) for p in s['xy']]
    # Adjacent methyl branches must face opposite sides: at the old ester
    # proportions, inward-facing H atoms on parallel branches would cross.
    if s['key'] == 'isopropyl_2_3_dimethylbutanoate':
        xy[5][1] *= -1
    c = Chem.Conformer(m.GetNumAtoms())
    c.Set3D(False)
    for i, (x, y) in enumerate(xy):
        c.SetAtomPosition(i, (-.825*x, .825*y/(1.5 if abs(y) == 1.5 else 1), 0))
    m.AddConformer(c)
    expanded = Chem.Mol(m)
    c = expanded.GetConformer()
    # The heavy graph is a tree. Rebuild orthogonal coordinates from its
    # authored directions, spacing C-C arms instead of tilting methyl H.
    positions = {0: (0., 0.)}
    todo = [0]
    while todo:
        parent = todo.pop()
        for neighbor in expanded.GetAtomWithIdx(parent).GetNeighbors():
            i = neighbor.GetIdx()
            if i in positions:
                continue
            dx, dy = xy[i][0]-xy[parent][0], xy[i][1]-xy[parent][1]
            assert (dx == 0) != (dy == 0), (s['key'], parent, i)
            bond = expanded.GetBondBetweenAtoms(parent, i)
            length = 1.10 if bond.GetBondTypeAsDouble() == 2 else (
                1.80 if neighbor.GetSymbol() == expanded.GetAtomWithIdx(parent).GetSymbol() == 'C' else 1.21)
            x, y = positions[parent]
            positions[i] = (x-length*(int(dx > 0)-int(dx < 0)),
                            y+length*(int(dy > 0)-int(dy < 0)))
            todo.append(i)
    for i, (x, y) in positions.items():
        c.SetAtomPosition(i, (x, y, 0))
    expanded = Chem.AddHs(expanded, addCoords=True)
    c = expanded.GetConformer()
    c.Set3D(False)
    for atom in expanded.GetAtoms():
        if atom.GetSymbol() == 'H':
            continue
        p = c.GetAtomPosition(atom.GetIdx())
        occupied = set()
        for n in atom.GetNeighbors():
            if n.GetSymbol() == 'H':
                continue
            q = c.GetAtomPosition(n.GetIdx())
            occupied.add((int(q.x > p.x)-int(q.x < p.x), int(q.y > p.y)-int(q.y < p.y)))
        free = [d for d in [(0, -1), (0, 1), (-1, 0), (1, 0)] if d not in occupied]
        hs = [n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol() == 'H']
        assert len(hs) <= len(free)
        if atom.GetIdx() == 0 and s['key'] == 'tert_butyl_methanoate':
            # Author the requested horizontal formyl H in the saved MOL too.
            free.sort(key=lambda d: d != (-1, 0))
        for h, (dx, dy) in zip(hs, free):
            c.SetAtomPosition(h, (p.x+.825*dx, p.y+.825*dy, 0))
    skeletal = Chem.Mol(m)
    step = .825*math.sqrt(3)/2
    parent = {i: Point2D(-step*i, -.4125*(i % 2)) for i in range(s['parent'])}
    # Fix the ester motif as well as the parent: acid left, alcohol right,
    # carbonyl upwards and 120-degree carbonyl geometry. RDKit lays out branches.
    parent.update({s['carbons']: Point2D(0, .825),
                   s['carbons']+1: Point2D(step, -.4125),
                   s['alcoholAttach']-1: Point2D(2*step, 0)})
    rdDepictor.Compute2DCoords(skeletal, bondLength=.825, coordMap=parent, canonOrient=False)
    return {'Condensed': m, 'Expanded': expanded, 'Skeletal': skeletal}


def three(s, cache):
    metadata = cache/(s['key']+'.json')
    record = json.loads(metadata.read_text()) if metadata.exists() else {
        'source': 'RDKit', 'reason': 'No verified PubChem 3D source used for this compound.'}
    query = graph(s)
    if record.get('source') == 'PubChem' and record.get('downloaded'):
        raw = (cache/(s['key']+'.sdf')).read_bytes()
        m = next(Chem.ForwardSDMolSupplier(io.BytesIO(raw), removeHs=False))
        assert m is not None and m.GetConformer().Is3D()
        assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT') == '0'
        assert m.GetProp('PUBCHEM_BOND_DEF_STEREO_COUNT') == '0'
        provenance = record
    else:
        m = Chem.AddHs(query)
        params = AllChem.ETKDGv3()
        params.randomSeed = 20261029
        params.numThreads = 1
        ids = AllChem.EmbedMultipleConfs(m, numConfs=24, params=params)
        assert len(ids)
        scores = AllChem.MMFFOptimizeMoleculeConfs(m, numThreads=1, mmffVariant='MMFF94s', maxIters=1000)
        converged = [(energy, i) for i, (status, energy) in enumerate(scores) if status == 0]
        assert converged
        energy, best = min(converged)
        conf = Chem.Conformer(m.GetConformer(best))
        m.RemoveAllConformers()
        m.AddConformer(conf, assignId=True)
        Chem.RemoveStereochemistry(m)
        raw = (Chem.MolToMolBlock(m, includeStereo=False)+'\n$$$$\n').encode()
        provenance = {'source': 'RDKit', 'rdkitVersion': rdBase.rdkitVersion,
                      'method': 'ETKDGv3 / MMFF94s; lowest converged energy among 24 sampled conformers',
                      'seed': 20261029, 'sampledConformers': len(ids), 'convergedConformers': len(converged),
                      'energyKcalMol': energy, 'lookup': record}
    assert rdMolDescriptors.CalcMolFormula(m) == s['formula']
    assert Chem.MolToSmiles(Chem.RemoveHs(m), isomericSmiles=False) == Chem.MolToSmiles(query, isomericSmiles=False)
    assert m.GetNumAtoms() == 3*s['carbons']+2
    match = Chem.RemoveHs(m).GetSubstructMatch(query)
    assert len(match) == query.GetNumAtoms()
    mapping = {str(i+1): match[i]+1 for i in range(query.GetNumAtoms())}
    provenance.update(key=s['key'], name=s['name'], formula=s['formula'], retrievalDate='2026-10-29',
                      sha256=hashlib.sha256(raw).hexdigest(), atomMapping2Dto3D=mapping,
                      mainChain3D=[mapping[str(i)] for i in range(1, s['parent']+1)],
                      stereochemistry='Unspecified; illustrative 3D geometry does not assign R/S or mixture composition.')
    return raw, provenance


def generate(output, cache, only_2d=False):
    output.mkdir(parents=True, exist_ok=True)
    for s in SPECS:
        for form, m in forms(s).items():
            p = output/(s['key']+'_2D_'+form+'.mol')
            assert not p.exists(), p
            text = Chem.MolToMolBlock(m, includeStereo=False)
            p.write_text(p.stem+'\n'+text.split('\n', 1)[1])
        if only_2d:
            print('GENERATED 2D', s['key'], flush=True)
            continue
        raw, record = three(s, cache)
        p = output/(s['key']+'_3D.sdf')
        assert not p.exists(), p
        p.write_bytes(raw)
        (output/(s['key']+'_3D.provenance.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
        print('GENERATED', s['key'], s['formula'], record['source'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pubchem-cache', type=Path, required=True)
    parser.add_argument('--only-2d', action='store_true', help='Generate new 2D drafts without regenerating any 3D assets')
    args = parser.parse_args()
    generate(args.output, args.pubchem_cache, args.only_2d)
