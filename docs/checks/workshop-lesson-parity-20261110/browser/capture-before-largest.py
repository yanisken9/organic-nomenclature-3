from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
try:
 source_guard();viewport(390,760);direct(False,'alkanes-branched');rounds=json.loads((ROOT/'games/data/name-repair-alkanes.json').read_text())['sets'][1]['rounds'];OUT['scope'].append('Only first two authored branched repairs earned to reach baseline largest third-round capture; no old full-six replay.')
 for f in rounds[:2]:
  click('[id$="part-'+f['targetPartId']+'"]');good=next(i for i,c in enumerate(f['choices'])if c['value']==f['correctValue']);click('[id$="choice-'+str(good)+'"]');click('[id$="check-button"]');wait('!!document.querySelector(".feedback.is-success")');click('.round-next button');image_ready()
 for w,h in [(1280,800),(390,760),(320,700)]:viewport(w,h);top();geometry('authored-largest-entry',w)
 click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');shot('authored-largest-zoom');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
finally:finish()
if not OUT['completed']:raise SystemExit(1)
