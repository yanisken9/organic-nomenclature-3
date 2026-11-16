"""Bounded release-candidate/public browser acceptance; prepare is side-effect free.

Run only with the root's assembled frozen release target and exclusive slot.
No source edits, storage fixtures, app callbacks or manufactured game evidence.
"""
from pathlib import Path
import runpy,sys,json,hashlib
HERE=Path(__file__).resolve().parent
CODE_ROOT=HERE.parents[3]
REUSED=CODE_ROOT/'docs/checks/game-viewport-implementation-20261116/lesson-browser/replay-viewport.py'
outer=runpy.run_path(str(REUSED),run_name='prepared_release_helpers')
ns=outer['namespace']
ns.update(HERE=HERE,CODE_ROOT=CODE_ROOT,REUSED=REUSED,__file__=str(Path(__file__).resolve()))
exec(compile((HERE/'release-checks.py').read_text(),str(HERE/'release-checks.py'),'exec'),ns)
if __name__=='__main__':
 if '--prepare-check' in sys.argv:
  print(json.dumps({'prepared':True,'browserLaunched':False,'entrypoint':str(Path(__file__).resolve()),'helpers':str(REUSED),'harnessSHA256':hashlib.sha256((HERE/'release-checks.py').read_bytes()).hexdigest(),'prefix':'/organic-nomenclature-3/','phases':['candidate','public','report-final'],'grant':'NAMELECULE_RELEASE_BROWSER_GRANT=frozen, release manifest, assembled root and exclusive root grant'}))
 else:ns['release_main']()
