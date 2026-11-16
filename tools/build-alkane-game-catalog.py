#!/usr/bin/env python3
"""Reproduce the versioned, structure-only alkane game catalogs.

Reads legacy data54 string literals and curated expanded MOL files; it never
evaluates JavaScript or stores names, selected chains or answers. Run --check to
verify the legacy catalog, or add --catalog-v2 for the curated 14-molecule pool.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
DATA = "js/jsme-nick-nomeclature-moc2-data_54.js"
ENGINE = "js/chemistry-engines/3f9382b45535ab101546fc70fe6c7264efcfe5ff4b6ea15deb9c4e80a38a5306.js"
OUTPUT = "games/data/alkane-structures.json"
OUTPUT_V2 = "games/data/alkane-structures-v2.json"
PACK = "data/namelecule-alkanes-v1/manifest.json"
LEGACY_SHA = "9778e30ea33f2f7cd4c8a472e46e90539856b861a54035a1d514c3246cccf724"
PACK_IDS = (
    "methyl_2_butane", "methyl_3_pentane", "ethyl_3_pentane",
    "dimethyl_2_2_propane", "dimethyl_2_2_butane", "ethyl_3_methyl_2_pentane",
)
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


def serialize_catalog(catalog):
    canonical = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    catalog["revision"] = sha256(canonical.encode("utf-8"))
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


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
    return serialize_catalog(catalog)


def build_catalog_v2():
    # Existing receipts identify the exact legacy bytes and engine. Import its
    # eight entries intact rather than regenerating them from a newer library.
    legacy_bytes = (ROOT / OUTPUT).read_bytes()
    if sha256(legacy_bytes) != LEGACY_SHA or legacy_bytes.decode("utf-8") != build_catalog():
        raise ValueError("The immutable legacy catalog no longer matches its pinned sources")
    legacy = json.loads(legacy_bytes)
    pack_bytes = (ROOT / PACK).read_bytes()
    pack = json.loads(pack_bytes)
    records = pack.get("molecules", [])
    if (pack.get("schemaVersion") != 1 or pack.get("id") != "namelecule-alkanes-v1"
            or not isinstance(records, list) or tuple(m.get("id") for m in records) != PACK_IDS):
        raise ValueError("Unexpected curated alkane pack identity or molecule order")
    molecules = legacy["molecules"].copy()
    for record in records:
        molecule_id = record["id"]
        relative = record.get("files", {}).get("expanded")
        expected_path = f"mols/namelecule-alkanes-v1/{molecule_id}_2D_Expanded.mol"
        if relative != expected_path:
            raise ValueError(f"Unexpected expanded MOL source for {molecule_id}")
        mol_bytes = (ROOT / relative).read_bytes()
        if sha256(mol_bytes) != record.get("sha256", {}).get("expanded"):
            raise ValueError(f"Expanded MOL source hash differs for {molecule_id}")
        mol = mol_bytes.decode("utf-8")
        lines = mol.splitlines()
        if len(lines) < 5 or "V2000" not in lines[3] or "M  END" not in lines:
            raise ValueError(f"Invalid expanded source MOL for {molecule_id}")
        molecules.append({
            "id": molecule_id,
            "mol": mol,
            "asset": f"assets/name-repair/expanded-v2/{molecule_id}.svg",
            "condensedAsset": f"assets/name-repair/condensed-v2/{molecule_id}.svg",
            "diagramAlt": "Ανεπτυγμένος μοριακός τύπος με σύμβολα άνθρακα και υδρογόνου και απλούς δεσμούς.",
            "sourceSHA256": sha256(mol_bytes),
        })
    return serialize_catalog({
        "schemaVersion": 1,
        "catalogVersion": 2,
        "engineSHA256": legacy["engineSHA256"],
        "source": {
            "legacy": {"file": OUTPUT, "sha256": sha256(legacy_bytes), "revision": legacy["revision"]},
            "pack": {"file": PACK, "sha256": sha256(pack_bytes), "id": pack["id"]},
        },
        "molecules": molecules,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare without writing")
    parser.add_argument("--catalog-v2", action="store_true", help="Build/check the curated 14-molecule catalog")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / (OUTPUT_V2 if args.catalog_v2 else OUTPUT)
    expected = build_catalog_v2() if args.catalog_v2 else build_catalog()
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Catalog differs from current sources: {output}")
        print("Catalog matches pinned sources; " + ("14" if args.catalog_v2 else "eight") + " structure-only entries.")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(expected, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
