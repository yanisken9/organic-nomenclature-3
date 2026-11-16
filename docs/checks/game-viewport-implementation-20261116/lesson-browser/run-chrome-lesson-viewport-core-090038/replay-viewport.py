"""Bounded lesson viewport acceptance; browser launch requires root frozen grant.

Uses existing replay-levels transport/native/pure-engine oracles. Trusted pointer
input operates the real production UI; no answer/receipt or app-handler writes.
"""
from pathlib import Path
import argparse, hashlib, json, os

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[3]
PRIOR_HARNESS = ROOT / 'docs/checks/game-levels-alkanes-implementation-20261116/browser/replay-levels.py'
namespace = {'__file__': str(PRIOR_HARNESS), '__name__': 'prepared_level_helpers'}
exec(compile(PRIOR_HARNESS.read_text(), str(PRIOR_HARNESS), 'exec'), namespace)
namespace.update(HERE=OWN, __file__=str(Path(__file__).resolve()), OWNED_PREFIX='namelecule-viewport-lesson-')
SCENARIOS = OWN / 'lesson-checks.py'
exec(compile(SCENARIOS.read_text(), str(SCENARIOS), 'exec'), namespace)

if __name__ == '__main__':
    if '--prepare-check' in os.sys.argv:
        print(json.dumps({'prepared': True, 'entrypoint': str(Path(__file__).resolve()),
                          'helpers': str(PRIOR_HARNESS), 'helperSHA256': hashlib.sha256(PRIOR_HARNESS.read_bytes()).hexdigest(),
                          'scenariosSHA256': hashlib.sha256(SCENARIOS.read_bytes()).hexdigest(),
                          'browserLaunched': False, 'scope': ['parent v57 all four active first screens', 'genuine required gates', 'cold restoration', 'optional3 blocked', 'native55/56'],
                          'grant': 'NAMELECULE_LEVELS_BROWSER_GRANT=frozen plus manifest; exclusive root approval separately required'}))
    else:
        namespace['main']()
