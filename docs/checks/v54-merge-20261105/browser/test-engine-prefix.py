"""Actual Firefox Workers and complete generated-quiz flows; no mock chemistry."""
from pathlib import Path
import json
import os
import time
import traceback

os.environ["NAMELECULE_BIDI_PORT"] = "9247"
os.environ["NAMELECULE_TEST_BASE_URL"] = "http://127.0.0.1:8056/"
exec(compile(Path("tools/namelecule_bidi.py").read_text().replace("{'type':'tab'}","{'type':'window'}"), "bidi", "exec"))
HERE = Path("docs/checks/v54-merge-20261105/browser")
out = {"completed": False, "checks": []}


def check(value, label, detail=None):
    assert value, (label, detail)
    out["checks"].append({"label": label, "detail": detail})
    print("PASS", len(out["checks"]), label, flush=True)


def click(selector):
    ev("document.querySelector(" + json.dumps(selector) + ").scrollIntoView({block:'center',behavior:'instant'});new Promise(r=>setTimeout(r,80))")
    box = json.loads(ev("JSON.stringify((()=>{const n=document.querySelector(" + json.dumps(selector) + "),b=n.getBoundingClientRect();return{x:b.x+b.width/2,y:b.y+b.height/2,enabled:!n.disabled,hit:n.contains(document.elementFromPoint(b.x+b.width/2,b.y+b.height/2))}})())"))
    assert box["hit"] and box["enabled"], (selector, box)
    call("input.performActions", {"context": ctx, "actions": [{"type": "pointer", "id": "mouse", "parameters": {"pointerType": "mouse"}, "actions": [
        {"type": "pointerMove", "x": round(box["x"]), "y": round(box["y"]), "duration": 0}, {"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]}]})


def key(value):
    call("input.performActions", {"context": ctx, "actions": [{"type": "key", "id": "keyboard", "actions": [{"type": "keyDown", "value": value}, {"type": "keyUp", "value": value}]}]})


def activate(selector):
    ev("document.querySelector(" + json.dumps(selector) + ").focus();true")
    key("\ue007")


def ready():
    until("!!document.querySelector('.diagram-image.is-ready')", seconds=35)


def recipe():
    return json.loads(ev("sessionStorage.getItem('namelecule-repair-engine-pilot-v1')"))


def cache_real_analyses():
    return json.loads(ev("""(async()=>{
      window.testCatalog=await(await fetch('./data/alkane-structures.json',{cache:'reload'})).json();
      window.testAnalyses=[];
      for(const m of testCatalog.molecules)testAnalyses.push(await NameleculeChemistryClient.analyze(m,{engineSHA256:testCatalog.engineSHA256}));
      return JSON.stringify(testAnalyses.map(a=>({id:a.moleculeId,name:a.name,parent:a.chain.length,carbons:a.carbonCount})));
    })()"""))


def current_round():
    return json.loads(ev("""JSON.stringify((()=>{
      const r=JSON.parse(sessionStorage.getItem('namelecule-repair-engine-pilot-v1'));
      const g=NameleculeRepairGenerator.createGame(testCatalog,testAnalyses,r);
      return g.sets.find(s=>s.id===r.setId).rounds[r.roundIndex];
    })())"""))


def correct_candidate(data):
    if data["kind"] == "replace":
        activate("#part-" + data["targetPartId"])
        choice = next(i for i, item in enumerate(data["choices"]) if item["value"] == data["correctValue"])
        activate("#choice-" + str(choice))
    else:
        activate("#part-" + data["correctOrder"][0])
        activate("#move-left")
    check(ev("document.querySelector('.candidate-name').textContent") == data["correctName"], "Exact graph-derived candidate " + data["moleculeId"])


try:
    navigate("organic-nomenclature-3/games/name-repair.html?source=engine")
    until("!!document.querySelector('#set-alkanes-start')",seconds=40)
    check(ev("typeof NameleculeChemistryClient==='object'"),"Actual client loads under Pages-shaped subdirectory")
    rows=cache_real_analyses()
    check(len(rows)==8,"Eight actual Workers succeed under subdirectory")
    failures=json.loads(ev("""(async()=>{const out=[],m=testCatalog.molecules[0],h=testCatalog.engineSHA256;try{await NameleculeChemistryClient.analyze({...m,mol:'bad'},{engineSHA256:h})}catch(e){out.push(e.code)}const c=new AbortController();c.abort();try{await NameleculeChemistryClient.analyze(m,{signal:c.signal,engineSHA256:h})}catch(e){out.push(e.name)}try{await NameleculeChemistryClient.verifyEngine('0'.repeat(64))}catch(e){out.push(e.code)}return JSON.stringify(out)})()"""))
    check(failures==['INVALID_MOLECULE','AbortError','ENGINE_VERSION_MISMATCH'],"Actual invalid input/abort/integrity rejection under prefix",failures)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
    out['javascriptErrors']=js_errors
    (HERE/'engine-prefix-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
