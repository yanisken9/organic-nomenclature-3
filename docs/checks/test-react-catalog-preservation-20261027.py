"""Read-only preservation check against the start of the approved React task."""
import hashlib
import json
import subprocess
from pathlib import Path

baseline = json.loads(Path('docs/checks/react-catalog-before-20261027.json').read_text())
protected = {p: h for p, h in baseline['files'].items()
             if not p.startswith('react-preview/')
             and p not in ('docs/SESSION-NOTES.md', 'docs/YANNIS-CONTRIBUTIONS.md')}
changed = [p for p, h in protected.items()
           if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest() != h]
assert not changed, changed
current = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode().split('\0')
unexpected = [p for p in current if p and p not in baseline['files']
              and not p.startswith(('react-preview/', 'docs/'))]
assert not unexpected, unexpected
print(json.dumps({'passed': True, 'protectedFilesUnchanged': len(protected),
                  'coreChanged': False, 'mainRuntimeChanged': False,
                  'moleculeAssetsChanged': False, 'scenarioJSONChanged': False}, indent=2))
