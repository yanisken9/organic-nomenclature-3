#!/usr/bin/env python3
"""Reproduce the opt-in Workshop's structure-only alkane catalog.

Reads only string literals from data54; it never evaluates JavaScript or stores
names, selected chains, components or correct answers. Run with --check to
verify that the checked-in JSON still matches its exact sources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DATA = "js/jsme-nick-nomeclature-moc2-data_54.js"
ENGINE = "js/mulermoc-nom-core-54.js"
OUTPUT = "games/data/alkane-structures.json"
MOLECULE_IDS = (
    "methane", "ethane", "propane", "butane", "pentane",
    "methyl_2_pentane", "dimethyl_2_3_butane",
    "ethyl_3_dimethyl_2_5_hexane",
)
STRING = r'"(?:[^"\\]|\\.)*"'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_mol(source, molecule_id):
    variable = re.escape(molecule_id + "_2D_Expanded")
    declarations = re.findall(
        r"\b(?:let|const|var)\s+" + variable + r"\s*=\s*([^;]*);", source
    )
    if len(declarations) != 1:
        raise ValueError(f"Expected exactly one expanded MOL for {molecule_id}")
    expression = declarations[0]
    if not re.fullmatch(r"\s*" + STRING + r"(?:\s*\+\s*" + STRING + r")*\s*", expression):
        raise ValueError(f"Non-literal expanded MOL for {molecule_id}")
    mol = "".join(json.loads(part) for part in re.findall(STRING, expression))
    lines = mol.splitlines()
    if len(lines) < 5 or "V2000" not in lines[3] or "M  END" not in lines:
        raise ValueError(f"Invalid source MOL for {molecule_id}")
    return mol


def build_catalog():
    source_bytes = (ROOT / DATA).read_bytes()
    source = source_bytes.decode("utf-8")
    molecules = []
    for molecule_id in MOLECULE_IDS:
        mol = source_mol(source, molecule_id)
        molecules.append({
            "id": molecule_id,
            "mol": mol,
            "asset": f"assets/name-repair/{molecule_id}.svg",
            "diagramAlt": "Ανεπτυγμένος μοριακός τύπος με σύμβολα άνθρακα και υδρογόνου και απλούς δεσμούς.",
            "sourceSHA256": sha256(mol.encode("utf-8")),
        })
    catalog = {
        "schemaVersion": 1,
        "engineSHA256": sha256((ROOT / ENGINE).read_bytes()),
        "source": {"file": DATA, "sha256": sha256(source_bytes)},
        "molecules": molecules,
    }
    canonical = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    catalog["revision"] = sha256(canonical.encode("utf-8"))
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare without writing")
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    args = parser.parse_args()
    expected = build_catalog()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Catalog differs from current sources: {args.output}")
        print("Catalog matches data54 and core54; eight structure-only entries.")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
