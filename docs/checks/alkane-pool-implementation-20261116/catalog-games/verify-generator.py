"""Developer generator checks in an isolated temporary source tree."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[4]
namespace = {"__file__": str(ROOT / "tools/build-alkane-game-catalog.py"), "__name__": "catalog_test"}
exec(compile((ROOT / "tools/build-alkane-game-catalog.py").read_text(), namespace["__file__"], "exec"), namespace)
checks = []

def check(condition, label):
    assert condition, label
    checks.append({"label": label, "passed": True})

check(namespace["build_catalog"]() == (ROOT / namespace["OUTPUT"]).read_text(), "legacy generator reproduces exact bytes with pinned engine")
check(namespace["build_catalog_v2"]() == (ROOT / namespace["OUTPUT_V2"]).read_text(), "version2 generator reproduces exact bytes")
original = json.loads((ROOT / namespace["PACK"]).read_bytes())
with tempfile.TemporaryDirectory(prefix="namelecule-catalog-source-check-") as temp:
    isolated = Path(temp)
    files = [namespace["DATA"], namespace["ENGINE"], namespace["OUTPUT"], namespace["PACK"]]
    files.extend(record["files"]["expanded"] for record in original["molecules"])
    for file in files:
        destination = isolated / file
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / file, destination)
    namespace["ROOT"] = isolated
    check(namespace["build_catalog_v2"]() == (ROOT / namespace["OUTPUT_V2"]).read_text(), "isolated source tree reproduces version2")
    def reject(pack, label):
        (isolated / namespace["PACK"]).write_text(json.dumps(pack, ensure_ascii=False))
        try:
            namespace["build_catalog_v2"]()
        except ValueError:
            check(True, label)
        else:
            raise AssertionError(label)
    changed = copy.deepcopy(original)
    changed["molecules"][0]["id"] = "unknown"
    reject(changed, "unexpected molecule ID rejected")
    changed = copy.deepcopy(original)
    changed["molecules"][0]["files"]["expanded"] = "../../outside.mol"
    reject(changed, "noncanonical/path-traversal source rejected")
    changed = copy.deepcopy(original)
    changed["molecules"][0]["sha256"]["expanded"] = "0" * 64
    reject(changed, "incorrect expanded source SHA rejected")
    changed = copy.deepcopy(original)
    relative = changed["molecules"][0]["files"]["expanded"]
    invalid = b"untrusted source is data, never code\n"
    (isolated / relative).write_bytes(invalid)
    changed["molecules"][0]["sha256"]["expanded"] = hashlib.sha256(invalid).hexdigest()
    reject(changed, "invalid MOL rejected even with matching supplied source SHA")
    shutil.copyfile(ROOT / relative, isolated / relative)
    (isolated / namespace["PACK"]).write_bytes((ROOT / namespace["PACK"]).read_bytes())
    (isolated / namespace["ENGINE"]).write_text("// changed engine bytes\n")
    try:
        namespace["build_catalog_v2"]()
    except ValueError:
        check(True, "mutated pinned engine cannot silently regenerate legacy receipts")
    else:
        raise AssertionError("mutated pinned engine accepted")
report = {"kind": "Developer isolated generator verification", "passed": True, "checks": len(checks), "results": checks}
(Path(__file__).parent / "generator-results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"checks": len(checks), "passed": True}))
