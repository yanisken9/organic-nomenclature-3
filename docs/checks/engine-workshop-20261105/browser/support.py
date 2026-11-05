"""Reuse established interaction checks on our owned endpoint/artifact folder."""
from pathlib import Path
import os

os.environ["NAMELECULE_TEST_BASE_URL"] = "http://127.0.0.1:8055/"
source = Path("docs/checks/v54-upstream-20261104/browser/support.py").read_text()
source = source.replace("'9244'", "'9245'").replace(
    "HERE=Path('docs/checks/v54-upstream-20261104/browser')",
    "HERE=Path('docs/checks/engine-workshop-20261105/browser')",
)
exec(compile(source, "existing-interaction-support", "exec"))
