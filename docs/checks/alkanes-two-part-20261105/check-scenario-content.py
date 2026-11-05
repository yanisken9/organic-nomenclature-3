"""Read-only curriculum/configuration and library preservation checks.

This does not replace the actual player/gate replay or chemistry validation.
Run from the repository root. Results are printed; the script writes no files.
"""
from pathlib import Path
import hashlib
import html
import json
import re
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCENARIO = "scenarios/alkanes-two-part-workshop.scenario.json"
IDS = ["methane", "ethane", "propane", "butane", "pentane",
       "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane"]
scenario = json.loads((ROOT / SCENARIO).read_text())
steps = scenario["steps"]
baseline = json.loads((HERE / "baseline.json").read_text())
catalog = json.loads((ROOT / "games/data/alkane-structures.json").read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert scenario["scenarioVersion"] == 2 and scenario["app"] == "mulermoc-nom-54"
assert scenario["title"] == scenario["scenario"] == "Αλκάνια · Δύο μέρη με Συνεργείο ονομάτων"
assert scenario["showStepNumbers"] is False and scenario["reserveTitleSpace"] is True
assert len(steps) == 12 and [s["n"] for s in steps] == list(range(1, 13))
assert [i for i, s in enumerate(steps) if "checkpoint" in s] == [3, 10]
assert [s["selectedMol"] for s in steps] == [
    "ethane", "ethane", "butane", "pentane", "methyl_2_pentane",
    "methyl_2_pentane", "dimethyl_2_3_butane", "ethyl_3_dimethyl_2_5_hexane",
    "ethyl_3_dimethyl_2_5_hexane", "ethyl_3_dimethyl_2_5_hexane",
    "ethyl_3_dimethyl_2_5_hexane", "ethyl_3_dimethyl_2_5_hexane"]

# The taught examples must remain visible, while the focused analysis component
# must not be hidden by a snapshot inherited from the longer lesson.
component = {"compCarbonsCount": "comp5", "compBondType": "comp6", "compSuffix": "comp9",
             "compNumber1": "comp0", "compSecondSub1": "comp1",
             "compNumber2": "comp2", "compSecondSub2": "comp3"}
for s in steps:
    assert s["selectedMol"] in IDS
    assert all(m in IDS for m in s["menuSubset"])
    assert s["mode2D"] == "condensed" and s["mainChainMode"] == "algorithmic"
    assert s["selectedRule"] is None and s["audio"]["narrate"] is False
    assert len(s["note"].split("\n\n")) == 2 and ":" not in s["note"]
    assert s["show"]["text"] and s["show"]["viewers"]["2D"]
    if s["nameAnalysisMode"] in component:
        assert component[s["nameAnalysisMode"]] not in s["styleName"]["hidden"]
assert [s["chainIdx"] for s in steps] == [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
assert [i for i, s in enumerate(steps) if s["show"]["rule"]] == [1, 5, 9]
assert steps[2]["menuSubset"] == IDS[:5] and steps[2]["show"]["controls"]["2D"]
for index in [1, 2, 5, 6, 9, 11]:
    assert not steps[index]["styleName"]["hidden"] and steps[index]["show"]["nameClick"]

for index, set_id in [(3, "alkanes-unbranched"), (10, "alkanes-branched")]:
    checkpoint = steps[index]["checkpoint"]
    assert checkpoint["id"] == set_id + "-workshop-v1"
    assert checkpoint["type"] == "generated-name-repair-set" and checkpoint["version"] == 1
    assert checkpoint["round"] == {
        "version": 1, "setId": set_id, "difficulty": "basic", "roundCount": 3,
        "generatorVersion": "1.0.0", "catalogRevision": catalog["revision"],
        "engineSHA256": sha(ROOT / "js/mulermoc-nom-core-54.js")}
    assert not any(key in checkpoint["round"] for key in ["correctName", "correctValue", "parts"])

final = steps[-1]
assert final["menuSubset"] == IDS
assert final["show"]["menu"] and final["show"]["nameSettings"] and final["show"]["nameClick"]
assert final["show"]["viewers"] == {"2D": True, "3D": True}
assert final["show"]["controls"] == {"2D": True, "3D": True}
assert "Το μεθάνιο" in final["note"] and "χωρίς σκελετικό" in final["note"]

# Historical lessons and molecular/runtime dependencies in the agreed baseline
# remain byte-identical; current player/controller edits are intentionally not
# part of this preservation list.
for path in baseline["preservedPaths"]:
    assert sha(ROOT / path) == baseline["SHA256"][path], ("changed protected file", path)

before = (HERE / "before/design/theory-library.html").read_text()
after = (ROOT / "design/theory-library.html").read_text()
start = '      <article class="lesson" aria-labelledby="alkanes-title">'
end = '      <article class="lesson" aria-labelledby="alkenes-title">'
a0, a1 = before.index(start), before.index(end)
b0, b1 = after.index(start), after.index(end)
assert before[:a0] == after[:b0] and before[a1:] == after[b1:]
card = after[b0:b1]
assert "12 βήματα · 8 μόρια" in card and "τρία κουίζ" in card
links = [html.unescape(link) for link in re.findall(r'href="([^"]*scenario=[^"]+)"', after)]
assert len(links) == 14
paths = [parse_qs(urlparse(link).query)["scenario"][0] for link in links]
assert paths[0] == SCENARIO
assert sum(len(json.loads((ROOT / path).read_text())["steps"]) for path in paths) == 328
assert all((ROOT / path).is_file() for path in paths)
assert sum(int(n) for n in re.findall(r'(\d+) βήματα', after)) == 328

print(json.dumps({"passed": True, "scenario": SCENARIO, "steps": 12,
    "gateIndices": [3, 10], "roundsPerGate": 3, "finalMolecules": IDS,
    "activeLessonCount": 14, "activeLessonSteps": 328,
    "preservedPaths": len(baseline["preservedPaths"]),
    "otherLibraryCardsByteIdentical": True,
    "scenarioSHA256": sha(ROOT / SCENARIO),
    "librarySHA256": sha(ROOT / "design/theory-library.html"),
    "limitations": ["No browser execution in this check", "Chemical graph checks run separately"]},
    ensure_ascii=False, indent=2))
