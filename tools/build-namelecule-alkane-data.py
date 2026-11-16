#!/usr/bin/env python3
"""Build the six curated alkane records from fixed, hash-verified local sources.

No network, optimization, or source-geometry rewrite occurs here. --check also
validates source identity and the declared 2D/3D atom correspondence without
writing files. Original base-data files remain the native library's source.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/namelecule-alkanes-v1/manifest.json"
OUTPUT = ROOT / "js/MULERMOC_namelecule_alkanes_v1_data.js"
FORMS = {"condensed": "Condensed", "expanded": "Expanded", "skeletal": "Skeletal"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def local_source(path):
    source = ROOT / path
    if not source.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Source escapes the project: " + path)
    return source.read_bytes()


def parse_mol(text):
    lines = text.splitlines()
    if len(lines) < 5 or "V2000" not in lines[3]:
        raise ValueError("Expected a standard V2000 header")
    count, bond_count = int(lines[3][:3]), int(lines[3][3:6])
    atoms = []
    for line in lines[4:4 + count]:
        # This bounded pack contains neutral, isotope-free, achiral alkanes.
        if any(int(line[a:b].strip() or 0) for a, b in ((34, 36), (36, 39), (39, 42))):
            raise ValueError("Unexpected isotope, charge/radical or atom stereo")
        atoms.append({"element": line[31:34].strip(),
                      "xyz": [float(line[i:i + 10]) for i in (0, 10, 20)]})
    bonds = []
    for line in lines[4 + count:4 + count + bond_count]:
        a, b, order = (int(line[i:i + 3]) for i in (0, 3, 6))
        if not (1 <= a <= count and 1 <= b <= count and a != b and order == 1):
            raise ValueError("Invalid alkane bond")
        if int(line[9:12].strip() or 0):
            raise ValueError("Unexpected bond stereo")
        bonds.append([a, b, order])
    end = 4 + count + bond_count
    if len(atoms) != count or lines[end].strip() != "M  END":
        raise ValueError("Unsupported MOL properties or truncated source")
    adjacency = [[] for _ in atoms]
    for a, b, _ in bonds:
        adjacency[a - 1].append(b)
        adjacency[b - 1].append(a)
    if len({tuple(sorted(b[:2])) for b in bonds}) != len(bonds):
        raise ValueError("Duplicate bond")
    for i, atom in enumerate(atoms):
        if atom["element"] not in ("C", "H"):
            raise ValueError("Unexpected alkane element")
        degree = len(adjacency[i])
        if (atom["element"] == "C" and not 1 <= degree <= 4 or
                atom["element"] == "H" and degree != 1):
            raise ValueError("Invalid atom valence")
    reached, todo = set(), [1]
    while todo:
        atom = todo.pop()
        if atom in reached:
            continue
        reached.add(atom)
        todo.extend(adjacency[atom - 1])
    if len(reached) != count or len(bonds) != count - 1:
        raise ValueError("Expected one connected acyclic alkane")
    return atoms, bonds, adjacency


def validate_record(record, sources, provenance):
    n = record["carbonCount"]
    expected_edges = {tuple(sorted(edge)) for edge in record["carbonEdges"]}
    if record["formula"] != f"C{n}H{2 * n + 2}":
        raise ValueError("Formula mismatch")
    parsed = {key: parse_mol(text) for key, text in sources.items()}
    for form in FORMS:
        atoms, bonds, adjacency = parsed[form]
        if [atom["element"] for atom in atoms[:n]] != ["C"] * n:
            raise ValueError("2D carbon indices differ from the curated graph")
        edges = {tuple(sorted((a, b))) for a, b, _ in bonds if a <= n and b <= n}
        if edges != expected_edges:
            raise ValueError("2D carbon graph mismatch")
        if form == "expanded":
            if len(atoms) != 3 * n + 2 or any(len(ns) != 4 for ns in adjacency[:n]):
                raise ValueError("Expanded hydrogen/valence mismatch")
        elif len(atoms) != n:
            raise ValueError("Condensed/skeletal source must contain heavy atoms only")
    atoms3d, bonds3d, adjacency3d = parsed["sdf"]
    if (len(atoms3d) != 3 * n + 2 or
            sum(a["element"] == "C" for a in atoms3d) != n or
            any(len(adjacency3d[i]) != 4 for i, a in enumerate(atoms3d) if a["element"] == "C")):
        raise ValueError("3D formula/valence mismatch")
    cid_tag = "> <PUBCHEM_COMPOUND_CID>\n" + str(record["pubchemCID"]) + "\n"
    if cid_tag not in sources["sdf"]:
        raise ValueError("SDF compound CID mismatch")
    mapping = provenance["atomCorrespondence"]["expandedTo3D"]
    if len(mapping) != len(atoms3d) or set(mapping) != set(range(1, len(atoms3d) + 1)):
        raise ValueError("Incomplete atom correspondence")
    atoms2d, bonds2d, _ = parsed["expanded"]
    if any(a["element"] != atoms3d[mapping[i] - 1]["element"] for i, a in enumerate(atoms2d)):
        raise ValueError("Atom correspondence element mismatch")
    mapped_bonds = {tuple(sorted((mapping[a - 1], mapping[b - 1]))) for a, b, _ in bonds2d}
    if mapped_bonds != {tuple(sorted((a, b))) for a, b, _ in bonds3d}:
        raise ValueError("Atom correspondence bond mismatch")


def condensed_formula(molecule):
    """Use the existing library's CHn parent/branch menu notation."""
    n, parent = molecule["carbonCount"], molecule["parentC"]
    neighbors = [[] for _ in range(n)]
    for a, b in molecule["carbonEdges"]:
        neighbors[a - 1].append(b - 1)
        neighbors[b - 1].append(a - 1)

    def fragment(atom, previous, in_parent=False):
        hydrogens = 4 - len(neighbors[atom])
        label = "C" + ("H" + (str(hydrogens) if hydrogens > 1 else "") if hydrogens else "")
        branches = [other for other in neighbors[atom] if other != previous and other >= parent]
        if in_parent:
            return label + "".join("(" + fragment(other, atom) + ")" for other in branches)
        # Every curated off-parent component in this pack is a linear alkyl.
        continuations = [other for other in neighbors[atom] if other != previous]
        if len(continuations) > 1:
            raise ValueError("Unsupported branched formula fragment")
        return label + "".join(fragment(other, atom) for other in continuations)

    return "".join(fragment(atom, -1, True) for atom in range(parent))


def build_bundle():
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["schemaVersion"] != 1 or manifest["id"] != "namelecule-alkanes-v1":
        raise ValueError("Unsupported alkane pack")
    records = {}
    for molecule in manifest["molecules"]:
        key = molecule["id"]
        if key in records:
            raise ValueError("Duplicate molecule ID")
        sources = {}
        for form in (*FORMS, "sdf"):
            raw = local_source(molecule["files"][form])
            if sha256(raw) != molecule["sha256"][form]:
                raise ValueError(f"Source hash mismatch: {key}/{form}")
            sources[form] = raw.decode("utf-8")
        provenance_raw = local_source(molecule["provenance"])
        if sha256(provenance_raw) != molecule["provenanceSHA256"]:
            raise ValueError("Provenance hash mismatch: " + key)
        provenance = json.loads(provenance_raw)
        validate_record(molecule, sources, provenance)
        record = {"key": key, "formula": condensed_formula(molecule),
                  "molecularFormula": molecule["formula"],
                  "grName": molecule["nameGR"], "pubchemCID": molecule["pubchemCID"],
                  "sourcePack": manifest["id"],
                  "displayPolicy": "namelecule-alkane-20261030",
                  "file3D": molecule["files"]["sdf"],
                  "sdf3DSource": "pubchem", "sdf3DStatus": "source-conformer",
                  "sdf3DProvenance": provenance["source3D"],
                  "mainChain3D": provenance["atomCorrespondence"]["parentTo3D"],
                  "status": "curated"}
        for form, suffix in FORMS.items():
            record["structure2D_" + suffix] = sources[form]
            record["mainChain_" + suffix] = list(range(1, molecule["parentC"] + 1))
        records[key] = record
    header = ("/* Generated by tools/build-namelecule-alkane-data.py; do not edit.\n"
              "   Fixed curated sources; no network or 3D optimization at build time.\n"
              f"   Manifest SHA-256: {sha256(manifest_bytes)} */\n")
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    # Custom files may coexist in any order. Existing accepted custom records
    # retain ownership of their keys, and base library records are never edited.
    return (header + "(function () {\n  var pack = " + payload + ";\n"
            "  var customs = window.nameExamplesCustom = window.nameExamplesCustom || {};\n"
            "  Object.keys(pack).forEach(function (key) {\n"
            "    if (!Object.prototype.hasOwnProperty.call(customs, key)) customs[key] = pack[key];\n"
            "  });\n})();\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    args = parser.parse_args()
    expected = build_bundle()
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Alkane bundle differs from curated sources; rebuild it")
        print("Verified six alkane source records, atom correspondence, hashes and bundle.")
    else:
        OUTPUT.write_text(expected, encoding="utf-8")
        print("Generated " + str(OUTPUT.relative_to(ROOT)))


if __name__ == "__main__":
    main()
