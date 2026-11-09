"""Chemical graph, hydrogen, coordinate and provenance checks for five new esters."""
from pathlib import Path
import argparse, hashlib, json, math
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors


def check(output):
    specs = json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
    rows = []
    for s in specs:
        row = {'key': s['key'], 'formula': s['formula'], 'forms': {}}
        expected = Chem.MolToSmiles(Chem.MolFromSmiles(s['smiles']), isomericSmiles=False)
        for form in ['Condensed', 'Expanded', 'Skeletal']:
            p = Path('mols/new_molecules')/(s['key']+'_2D_'+form+'.mol')
            m = Chem.MolFromMolFile(str(p), removeHs=False)
            assert m is not None and rdMolDescriptors.CalcMolFormula(m) == s['formula']
            assert Chem.MolToSmiles(Chem.RemoveHs(m), isomericSmiles=False) == expected
            assert not any(a.GetFormalCharge() or a.GetIsotope() for a in m.GetAtoms())
            assert not any(a.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED for a in m.GetAtoms())
            assert sum(a.GetSymbol() == 'H' for a in m.GetAtoms()) == (2*s['carbons'] if form == 'Expanded' else 0)
            assert [a.GetSymbol() for a in list(m.GetAtoms())[:s['carbons']+2]] == ['C']*s['carbons']+['O','O']
            pts = m.GetConformer().GetPositions()
            assert max(abs(float(p[2])) for p in pts) < 1e-7
            nearest = min(math.dist(pts[i], pts[j]) for i in range(len(pts)) for j in range(i)
                          if not m.GetBondBetweenAtoms(i, j))
            assert nearest > .3, (s['key'], form, nearest)
            # A visible atom must not sit on an unrelated bond segment.
            for bond in m.GetBonds():
                a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
                u = pts[b]-pts[a]; length2 = float(u@u)
                assert length2 > .2
                for i in range(len(pts)):
                    if i in [a,b]:
                        continue
                    t = float((pts[i]-pts[a])@u)/length2
                    if .02 < t < .98:
                        assert math.dist(pts[i], pts[a]+t*u) > .15, (s['key'], form, 'atom on bond', i, a, b)
            if form != 'Skeletal':
                assert max(pts[i][1] for i in range(s['parent']))-min(pts[i][1] for i in range(s['parent'])) < 1e-7
            row['forms'][form] = {'atoms': m.GetNumAtoms(), 'nearestNonbonded': nearest}
        source = Path('mols/new_molecules')/(s['key']+'_3D.sdf')
        runtime = Path('mols/nomeclature-moc2')/source.name
        assert source.read_bytes() == runtime.read_bytes()
        record = json.loads(source.with_suffix('.provenance.json').read_text())
        # Actual provenance path retains the _3D filename stem.
        assert record['sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
        m = next(Chem.SDMolSupplier(str(source), removeHs=False))
        assert m is not None and m.GetConformer().Is3D()
        assert rdMolDescriptors.CalcMolFormula(m) == s['formula'] and m.GetNumAtoms() == 3*s['carbons']+2
        assert Chem.MolToSmiles(Chem.RemoveHs(m), isomericSmiles=False) == expected
        mapping = {int(a)-1: b-1 for a,b in record['atomMapping2Dto3D'].items()}
        assert len(set(mapping.values())) == s['carbons']+2
        for a,b,order in s['edges']:
            bond = m.GetBondBetweenAtoms(mapping[a-1],mapping[b-1])
            assert bond is not None and bond.GetBondTypeAsDouble() == order
        xyz = m.GetConformer().GetPositions()
        lengths = []
        for bond in m.GetBonds():
            a,b = bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()
            length = math.dist(xyz[a],xyz[b]); lengths.append(length)
            assert .85 < length < 1.8, (s['key'], a, b, length)
        if record['source'] == 'PubChem':
            assert int(m.GetProp('PUBCHEM_COMPOUND_CID')) == record['cid']
            assert m.GetProp('PUBCHEM_ATOM_DEF_STEREO_COUNT') == '0'
        else:
            assert record['source'] == 'RDKit' and record['convergedConformers'] > 0
        row.update(source3D=record['source'], cid=record.get('cid'), atomMapping=record['atomMapping2Dto3D'],
                   bondLengthRange=[min(lengths),max(lengths)])
        rows.append(row)
    result = {'passed': True, 'molecules': len(rows), 'forms2D': 3*len(rows), 'rows': rows}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS',len(rows),'molecules /',3*len(rows),'2D forms and graph-matched explicit-H3D')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    check(parser.parse_args().output)
