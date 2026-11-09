"""Approved coordinate-only harmonization from an immutable session baseline.

The reference is the pre-existing methyl_2_pentane MOL, separately per form.
No graph fields, atom IDs, stereochemistry, 3D, core or viewer are regenerated.
"""
from pathlib import Path
import argparse
import base64
import gzip
import itertools
import json
import math
import re


KEYS = ("dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane")
FORMS = ("Condensed", "Expanded", "Skeletal")
DATA = "js/jsme-nick-nomeclature-moc2-data_52.js"
LITERAL = r'"(?:\\.|[^"\\])*"'


def parse(mol):
    lines = mol.splitlines(keepends=True)
    count, bonds = int(lines[3][:3]), int(lines[3][3:6])
    atoms = [(float(line[:10]), float(line[10:20]), line[31:34].strip())
             for line in lines[4:4 + count]]
    edges = [(int(line[:3]) - 1, int(line[3:6]) - 1)
             for line in lines[4 + count:4 + count + bonds]]
    return lines, atoms, edges


def literal_match(code, name):
    return re.search(r'\b(?:let|const|var)\s+' + re.escape(name) +
                     r'\s*=\s*((?:' + LITERAL + r'\s*\+\s*)*' + LITERAL + r')\s*;', code)


def reference_lengths(code):
    match = literal_match(code, "methyl_2_pentane_2D_Expanded")
    mol = ''.join(json.loads(value) for value in re.findall(LITERAL, match[1]))
    _, atoms, _ = parse(mol)
    # Exact coordinates of the existing reference's C1–C2, C1–H7 and C5–H18/20.
    return (math.dist(atoms[0][:2], atoms[1][:2]),
            math.dist(atoms[0][:2], atoms[6][:2]),
            math.dist(atoms[4][:2], atoms[17][:2]),
            math.dist(atoms[4][:2], atoms[19][:2]))


def coordinates(mol, key, form, path, lengths):
    lines, atoms, edges = parse(mol)
    cc, ch, side_h, outer_h = lengths
    neighbors = [[] for _ in atoms]
    for a, b in edges:
        neighbors[a].append(b)
        neighbors[b].append(a)
    carbon_count = sum(atom[2] == 'C' for atom in atoms)
    if form == "Skeletal":
        # Whole-molecule similarity transform; preserve all skeletal angles.
        # The source's nominal KingDraw bond unit is .7800.
        scale = cc / .78
        rotate = -1 if atoms[0][0] > atoms[3 if carbon_count == 6 else 5][0] else 1
        cx = sum(a[0] for a in atoms) / len(atoms)
        cy = sum(a[1] for a in atoms) / len(atoms)
        return [(rotate * (a[0] - cx) * scale, rotate * (a[1] - cy) * scale) for a in atoms]

    parent_count = 4 if carbon_count == 6 else 6
    # Preserve C1-to-right orientation of each active original via a proper
    # 180-degree rotation when required; this is never a reflection.
    rotate = -1 if carbon_count == 10 else 1
    parent = list(range(parent_count))
    if "source-2d" in str(path) and form == "Condensed":
        parent = [0, 1, 2, 5]  # Historical C4 is the branch on C3, not chain end.
    pos = {atom: ((i - (parent_count - 1) / 2) * cc, 0.0)
           for i, atom in enumerate(parent)}
    if carbon_count == 6:
        # Separate methyls to opposite sides, as in the active original.
        for parent_atom, sign in ((parent[1], -1), (parent[2], 1)):
            branch = next(i for i in neighbors[parent_atom]
                          if atoms[i][2] == 'C' and i not in parent)
            pos[branch] = (pos[parent_atom][0], sign * cc)
    else:
        for branch, parent_atom, y in ((6, 1, cc), (7, 2, -cc),
                                       (8, 2, -2 * cc), (9, 4, cc)):
            pos[branch] = (pos[parent_atom][0], y)

    axes = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for atom in range(carbon_count):
        hydrogens = [i for i in neighbors[atom] if atoms[i][2] == 'H']
        if not hydrogens:
            continue
        carbons = [i for i in neighbors[atom] if atoms[i][2] == 'C']
        occupied = set()
        for other in carbons:
            dx, dy = pos[other][0] - pos[atom][0], pos[other][1] - pos[atom][1]
            occupied.add((round(dx / cc), round(dy / cc)))
        free = [direction for direction in axes if direction not in occupied]
        assert len(free) == len(hydrogens), (path, atom, free, hydrogens)
        original = [(rotate * (atoms[h][0] - atoms[atom][0]),
                     rotate * (atoms[h][1] - atoms[atom][1])) for h in hydrogens]
        assignment = min(itertools.permutations(free),
                         key=lambda candidate: -sum(v[0] * d[0] + v[1] * d[1]
                                                    for v, d in zip(original, candidate)))
        vertical_branch = atom not in parent and all(pos[c][0] == pos[atom][0] for c in carbons)
        for hydrogen, (dx, dy) in zip(hydrogens, assignment):
            length = (side_h if dx else outer_h) if vertical_branch else ch
            pos[hydrogen] = (pos[atom][0] + dx * length, pos[atom][1] + dy * length)
    assert len(pos) == len(atoms)
    return [pos[i] for i in range(len(atoms))]


def replace_xy(mol, xy):
    lines, atoms, _ = parse(mol)
    for i, (x, y) in enumerate(xy):
        x = 0.0 if abs(x) < .00005 else x
        y = 0.0 if abs(y) < .00005 else y
        lines[4 + i] = "%10.4f%10.4f" % (x, y) + lines[4 + i][20:]
    return ''.join(lines)


def replace_embedded(code, name, mol):
    match = literal_match(code, name)
    assert match, name
    new_lines = iter(mol.splitlines(keepends=True))

    def substitute(literal):
        count = len(json.loads(literal[0]).splitlines(keepends=True))
        # Some original embedded records have one extra trailing blank line
        # relative to the source MOL. Keep the literal layout while making the
        # completed registry string byte-identical to the updated source.
        return json.dumps(''.join(next(new_lines, '') for _ in range(count)))

    expression = re.sub(LITERAL, substitute, match[1])
    assert next(new_lines, None) is None
    return code[:match.start(1)] + expression + code[match.end(1):]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True,
                        help="Immutable before-source.json.gz captured before intervention")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    snapshot = json.loads(gzip.decompress(args.before.read_bytes()))
    original = {p: base64.b64decode(value).decode() for p, value in
                snapshot.get('sources', snapshot).items()}
    lengths = reference_lengths(original[DATA])
    code = original[DATA]
    replacements = {}
    for path, mol in original.items():
        if not path.endswith('.mol'):
            continue
        key = next(key for key in KEYS if Path(path).name.startswith(key + '_2D_'))
        form = next(form for form in FORMS if path.endswith('_' + form + '.mol'))
        replacements[path] = replace_xy(mol, coordinates(mol, key, form, path, lengths))
        if "new_molecules" in path:
            code = replace_embedded(code, key + '_2D_' + form, replacements[path])
    if args.apply:
        for path, mol in replacements.items():
            Path(path).write_text(mol)
        Path(DATA).write_text(code)
    print(json.dumps({"applied": args.apply, "sourceMOLs": len(replacements),
                      "referenceLengths": dict(zip(("CC", "CH", "branchSideH", "branchOuterH"), lengths))}))


if __name__ == "__main__":
    main()
