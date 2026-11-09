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
    # Storage and all engine globals are confined to the pilot, never Main.
    navigate("games/name-repair.html")
    until("!!document.querySelector('#set-alkanes-start')")
    call("browsingContext.activate", {"context": ctx})
    check(ev("typeof NameleculeChemistryClient==='undefined'&&typeof NameleculeRepairGenerator==='undefined'"), "Default game does not load chemistry adapter/generator")
    ev("sessionStorage.removeItem('namelecule-repair-engine-pilot-v1');true")
    click(".pilot-entry a")
    until("location.search.includes('source=engine')", seconds=15)
    until("!!document.querySelector('#set-alkanes-start')", seconds=40)
    check(ev("location.search.includes('source=engine')"), "Visible entry opens opt-in pilot")
    check(ev("typeof jsmeNomeclatureApplet==='undefined'&&typeof Jmol==='undefined'&&typeof nameExamples==='undefined'"), "No live viewer, JSmol or main data globals in game")
    rows = cache_real_analyses()
    oracle = {"methane": ("μεθάνιο", 1, 1), "ethane": ("αιθάνιο", 2, 2), "propane": ("προπάνιο", 3, 3), "butane": ("βουτάνιο", 4, 4), "pentane": ("πεντάνιο", 5, 5),
              "methyl_2_pentane": ("2-μεθυλοπεντάνιο", 5, 6), "dimethyl_2_3_butane": ("2,3-διμεθυλοβουτάνιο", 4, 6), "ethyl_3_dimethyl_2_5_hexane": ("3-αιθυλο-2,5-διμεθυλοεξάνιο", 6, 10)}
    for row in rows:
        check((row["name"], row["parent"], row["carbons"]) == oracle[row["id"]], "Actual Worker agrees with independent oracle " + row["id"])
    click("#set-alkanes-start")
    until("!!document.querySelector('#pilot-difficulty')")
    for width in [1500, 768, 390, 320]:
        call("browsingContext.setViewport", {"context": ctx, "viewport": {"width": width, "height": 980}, "devicePixelRatio": 1})
        check(ev("document.documentElement.scrollWidth<=innerWidth"), "Difficulty/set picker fits " + str(width))
    call("browsingContext.setViewport", {"context": ctx, "viewport": {"width": 1500, "height": 1000}, "devicePixelRatio": 1})
    screenshot(HERE / "engine-set-picker.png")
    for set_id, difficulty in [("alkanes-unbranched", "basic"), ("alkanes-branched", "challenge")]:
        ev("document.querySelector('#pilot-difficulty').value=" + json.dumps(difficulty) + ";document.querySelector('#pilot-difficulty').dispatchEvent(new Event('change'));true")
        click("#set-" + set_id + "-start")
        ready()
        generated_ids = []
        for index in range(3):
            data = current_round()
            generated_ids.append(data["moleculeId"])
            check(len(json.loads(ev("JSON.stringify([...document.querySelectorAll('.progress-dot')].map(n=>n.textContent))"))) == 3, "Exactly three generated rounds")
            if index == 0:
                if data["kind"] == "replace":
                    agreed = next(p["id"] for p in data["parts"] if p["id"] != data["targetPartId"])
                    activate("#part-" + agreed)
                    check(ev("document.querySelector('.part-selection-status').textContent") == "Αυτό το συνθετικό συμφωνεί με τη δομή.", "Minimal correct-part acknowledgement preserved")
                    activate("#part-" + data["targetPartId"])
                    wrong = next(i for i, item in enumerate(data["choices"]) if item["value"] != data["correctValue"])
                    activate("#choice-" + str(wrong))
                    activate("#check-button")
                    check(not ev("!!document.querySelector('.feedback.is-success')"), "Wrong generated repair stays unsolved")
                    frozen = recipe()
                    activate(".repair-actions .quiet")
                    after = recipe()
                    check(after["seed"] == frozen["seed"] and after["states"][0]["choiceOrder"] == frozen["states"][0]["choiceOrder"] and after["states"][0]["attempts"] == 1, "Retry freezes question, choices and attempts")
                correct_candidate(data)
                before = recipe()
                activate(".session-row button")
                until("!!document.querySelector('.confirm-dialog[open]')")
                activate(".confirm-dialog .secondary")
                check(recipe() == before, "Cancel return preserves exact attempt")
                screenshot(HERE / (set_id + "-candidate.png"))
                # A refresh must compute the same questions and restore only legal state.
                call("browsingContext.reload", {"context": ctx, "wait": "complete"})
                ready()
                cache_real_analyses()
                check(recipe() == before, "Refresh restores exact active attempt and order")
                check(current_round() == data, "Refresh regenerates same graph-derived question")
                check(ev("document.querySelector('.candidate-name').textContent") == data["correctName"], "Refresh restores selected repair")
            else:
                correct_candidate(data)
            activate("#check-button")
            until("!!document.querySelector('.feedback.is-success')")
            check(ev("document.querySelector('.success-explanation').textContent") == data["successText"], "Specific graph-derived success explanation")
            check(ev("document.activeElement===document.querySelector('.round-next button')"), "Keyboard focus reaches continuation")
            if index == 1:
                click(".diagram-tools .quiet")
                until("!!document.querySelector('.zoom-dialog[open]')")
                key("\ue00c")
                until("!document.querySelector('.zoom-dialog')")
                check(ev("document.activeElement===document.querySelector('.diagram-tools .quiet')"), "Zoom Escape restores focus")
            if index == 2:
                solved = recipe()
                call("browsingContext.reload", {"context": ctx, "wait": "complete"})
                ready()
                cache_real_analyses()
                check(recipe() == solved and ev("!!document.querySelector('.feedback.is-success')"), "Solved repair survives refresh with explanation")
            activate(".round-next button")
            if index < 2:
                ready()
        until("!!document.querySelector('.results')")
        check(len(set(generated_ids)) == 3, "Three distinct structures in " + set_id)
        check(ev("document.querySelectorAll('.result-item').length===3") and recipe()["phase"] == "results", "Three completed repairs reach results")
        results = recipe()
        call("browsingContext.reload", {"context": ctx, "wait": "complete"})
        until("!!document.querySelector('.results')")
        cache_real_analyses()
        check(recipe() == results, "Completed results survive refresh")
        screenshot(HERE / (set_id + "-results.png"))
        activate(".results-actions .primary")
        until("!!document.querySelector('#pilot-difficulty')")

    # Incompatible/corrupt progress cannot silently retain an old solved state.
    ev("(()=>{const r=JSON.parse(sessionStorage.getItem('namelecule-repair-engine-pilot-v1'));r.generatorVersion='obsolete';r.phase='results';r.states=[{solved:true}];sessionStorage.setItem('namelecule-repair-engine-pilot-v1',JSON.stringify(r));})();true")
    call("browsingContext.reload", {"context": ctx, "wait": "complete"})
    until("!!document.querySelector('#set-alkanes-start')")
    check(recipe()["phase"] == "hub" and recipe()["states"] == [], "Obsolete generation resets safely")
    ev("(()=>{const r=JSON.parse(sessionStorage.getItem('namelecule-repair-engine-pilot-v1'));r.seed='';sessionStorage.setItem('namelecule-repair-engine-pilot-v1',JSON.stringify(r));})();true")
    call("browsingContext.reload", {"context": ctx, "wait": "complete"})
    until("!!document.querySelector('#set-alkanes-start')")
    check(bool(recipe()["seed"]), "Malformed saved seed recovers without trapping loading")
    click("#set-alkanes-start")
    click("#set-alkanes-branched-start")
    ready()
    for width in [1500, 768, 390, 320]:
        call("browsingContext.setViewport", {"context": ctx, "viewport": {"width": width, "height": 980}, "devicePixelRatio": 1})
        check(ev("document.documentElement.scrollWidth<=innerWidth"), "Generated active round fits " + str(width))
    screenshot(HERE / "engine-round-320.png")
    call("browsingContext.setViewport", {"context": ctx, "viewport": {"width": 1500, "height": 1000}, "devicePixelRatio": 1})

    # Actual same-origin Worker URL resolution under a Pages-shaped prefix.
    navigate("organic-nomenclature-3/games/name-repair.html?source=engine")
    until("!!document.querySelector('.diagram-image.is-ready')||!!document.querySelector('#set-alkanes-start')", seconds=40)
    check(ev("typeof NameleculeChemistryClient==='object'"), "Actual Worker loads under repository subdirectory")
    prefixed = cache_real_analyses()
    check(len(prefixed) == 8, "All eight Workers succeed under subdirectory")
    # Genuine malformed-input rejection and abort are checked without the UI.
    failures = json.loads(ev("""(async()=>{
      const failures=[];const m=testCatalog.molecules[0],h=testCatalog.engineSHA256;
      try{await NameleculeChemistryClient.analyze({...m,mol:'bad'},{engineSHA256:h});}catch(e){failures.push(e.code)}
      const c=new AbortController();c.abort();
      try{await NameleculeChemistryClient.analyze(m,{signal:c.signal,engineSHA256:h});}catch(e){failures.push(e.name)}
      try{await NameleculeChemistryClient.verifyEngine('0'.repeat(64));}catch(e){failures.push(e.code)}
      return JSON.stringify(failures);
    })()"""))
    check(failures == ["INVALID_MOLECULE", "AbortError", "ENGINE_VERSION_MISMATCH"], "Actual invalid input, abort and changed-core rejection", failures)
    out["completed"] = True
except Exception as error:
    out.update(failure=str(error), traceback=traceback.format_exc())
    print(out["traceback"], flush=True)
    try:
        screenshot(HERE / "engine-failure.png")
    except Exception:
        pass
finally:
    out["javascriptErrors"] = js_errors
    import hashlib
    out["sourceSHA256"] = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in [
        "js/namelecule-game-repair.js", "js/namelecule-chemistry-client.js", "js/namelecule-chemistry-worker.js", "js/namelecule-repair-generator.js", "games/data/alkane-structures.json"]}
    (HERE / "engine-browser.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    call("browsingContext.close", {"context": ctx})
    call("session.end", {})
    print(json.dumps({"completed": out["completed"], "checks": len(out["checks"]), "javascriptErrors": len(js_errors), "failure": out.get("failure")}), flush=True)
if not out["completed"] or js_errors:
    raise SystemExit(1)
