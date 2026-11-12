from pathlib import Path
# Load definitions only; do not rerun the six already recorded actual Main55 completions.
exec(Path(__file__).with_name('after.py').read_text().split('\ntry:\n lesson(10);')[0])
try:
 viewport(1500,1000);lesson(3,54);check(ev('fScenarioPresent().index')==3,'Main54 compatible gate4 loaded');open_gate();choose('builder');header('main54-step4',focused=True,screenshot=True)
 open_page('games/name-builder.html?molecule=butane');wait('!!document.querySelector("#bank-tiles button")',60)
 check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"&&document.querySelectorAll(".builder-title").length===1&&!document.querySelector(".nl-builder-title")'),'Standalone Builder keeps its original brand/header/next/mode');shot('standalone-builder-desktop.png')
 open_page('games/name-repair.html');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-builder-title")'),'Standalone Workshop remains outside Builder header scope');shot('standalone-workshop.png')
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1&headerProbe=supplement-20261111-r1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")',60)
 check(not ev('!!document.querySelector(".nl-game-choice-card")||!!document.querySelector(".nl-builder-title")'),'Legacy Workshop-only checkpoint remains unchanged');shot('legacy-workshop-checkpoint.png')
 OUT['passed']=True
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('supplement-failure.png');raise
finally:
 OUT['jsExceptions']=js_errors;OUT['consoleEntries']=[e.get('params') for e in all_events if e.get('method')=='log.entryAdded']
 OUT['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-game-choice-checkpoint.js','css/namelecule-quiz-checkpoints.css','mulermoc-nom-54.html','mulermoc-nom-55.html']}
 (HERE/'supplement-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
