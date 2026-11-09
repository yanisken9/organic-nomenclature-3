"""Replay existing fixed game/checkpoint tests, changing only support location."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("target", choices=["two-sets", "pilot"])
args = parser.parse_args()
original = Path("docs/checks/v54-upstream-20261104/browser") / ("test-" + args.target + ".py")
source = original.read_text().replace(
    "docs/checks/v54-upstream-20261104/browser/support.py",
    "docs/checks/alkanes-two-part-20261105/browser/support.py",
)
exec(compile(source, str(original), "exec"))
