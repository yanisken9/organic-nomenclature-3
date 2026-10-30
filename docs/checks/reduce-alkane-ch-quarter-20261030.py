"""Approved expanded-alkane C-H additional 25% drawing experiment, from a fixed baseline."""
from pathlib import Path
import argparse
import base64
import gzip
import json
import re
import runpy


DATA = 'js/jsme-nick-nomeclature-moc2-data_52.js'
helpers = runpy.run_path('docs/checks/harmonize-two-alkanes-20261030.py')


def reduce_quarter(mol):
    lines, atoms, edges = helpers['parse'](mol)
    xy = [atom[:2] for atom in atoms]
    for h, atom in enumerate(atoms):
        if atom[2] != 'H':
            continue
        attached = [b if a == h else a for a,b in edges if h in (a,b)]
        assert len(attached) == 1 and atoms[attached[0]][2] == 'C'
        carbon = atoms[attached[0]]
        xy[h] = tuple(carbon[d] + .75*(atom[d]-carbon[d]) for d in (0,1))
    return helpers['replace_xy'](mol, xy)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snapshot = json.loads(gzip.decompress(args.before.read_bytes()))
    original = {p:base64.b64decode(v).decode() for p,v in snapshot['sources'].items()}
    code = original[DATA]
    for key in snapshot['keys']:
        name = key+'_2D_Expanded'
        match = helpers['literal_match'](original[DATA], name)
        assert match, key
        mol = ''.join(json.loads(v) for v in re.findall(helpers['LITERAL'], match[1]))
        code = helpers['replace_embedded'](code, name, reduce_quarter(mol))
    sources = {p:reduce_quarter(mol) for p,mol in original.items() if p.endswith('.mol')}
    if args.apply:
        for path,mol in sources.items():
            Path(path).write_text(mol)
        Path(DATA).write_text(code)
    print(json.dumps({'applied':args.apply,'expandedAlkanes':len(snapshot['keys']),
                      'sourceCopies':len(sources),'ratio':.75,'coordinatePrecision':'.0001 MOL units'}))


if __name__ == '__main__':
    main()
