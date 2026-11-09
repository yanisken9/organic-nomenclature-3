"""Actual generated repair families, failure/retry and exported asset framing."""
from pathlib import Path
import ast
import hashlib
import json
import os
import traceback

os.environ["NAMELECULE_BIDI_PORT"] = "9245"
os.environ["NAMELECULE_TEST_BASE_URL"] = "http://127.0.0.1:8055/"
exec(compile(Path("tools/namelecule_bidi.py").read_text(), "bidi", "exec"))
HERE = Path("docs/checks/engine-workshop-20261105/browser")
out = {"completed": False, "checks": []}
tree = ast.parse((HERE / "test-engine.py").read_text())
for definition in tree.body:
    if isinstance(definition, ast.FunctionDef):
        exec(compile(ast.Module(body=[definition], type_ignores=[]), "shared-pilot-test-functions", "exec"))
preload = None
try:
    navigate("games/name-repair.html?source=engine")
    until("!!document.querySelector('#set-alkanes-start')||!!document.querySelector('.diagram-image.is-ready')")
    cache_real_analyses()
    selected = json.loads(ev("""JSON.stringify((()=>{
      const cases={};
      for(let seed=0;seed<300;seed++){
        const game=NameleculeRepairGenerator.createGame(testCatalog,testAnalyses,{seed,difficulty:'challenge'});
        for(const set of game.sets){const r=set.rounds[0];if(!cases[r.fault.kind])cases[r.fault.kind]={seed:String(seed),setId:set.id,round:r};}
      }
      return Object.values(cases);
    })())"""))
    check(len(selected) == 5, "Five fault families have valid deterministic entry cases")
    for case in selected:
        ev("""(()=>{
          const item=""" + json.dumps(case, ensure_ascii=False) + """;
          const g=NameleculeRepairGenerator.createGame(testCatalog,testAnalyses,{seed:item.seed,difficulty:'challenge'});
          const set=g.sets.find(s=>s.id===item.setId);
          const record={version:1,generatorVersion:NameleculeRepairGenerator.version,catalogRevision:testCatalog.revision,engineSHA256:testCatalog.engineSHA256,
            seed:item.seed,difficulty:'challenge',phase:'round',setId:set.id,roundIndex:0,states:set.rounds.map(r=>NameleculeRepairEngine.createRoundState(r))};
          sessionStorage.setItem('namelecule-repair-engine-pilot-v1',JSON.stringify(record));
        })();true""")
        call("browsingContext.reload", {"context": ctx, "wait": "complete"})
        ready()
        cache_real_analyses()
        data = current_round()
        check(data == case["round"], "Frozen recipe replays family " + data["fault"]["kind"])
        correct_candidate(data)
        activate("#check-button")
        until("!!document.querySelector('.feedback.is-success')")
        check(ev("document.querySelector('.success-explanation').textContent") == data["successText"], "Actual successful family " + data["fault"]["kind"])
        if data["kind"] == "order":
            screenshot(HERE / "generated-alphabetical-order-success.png")

    # Measure standalone SVG decode, glyph-size consistency and full-label fit.
    assets = json.loads(ev("""(async()=>{const rows=[];
      for(const id of ['methane','propane']){
        const response=await fetch('assets/name-repair/'+id+'.svg');const raw=await response.text();
        const image=new Image();image.src='assets/name-repair/'+id+'.svg';await image.decode();
        const doc=new DOMParser().parseFromString(raw,'image/svg+xml');if(doc.querySelector('parsererror'))throw Error('bad SVG');
        const host=document.createElement('div');host.style.cssText='position:fixed;left:-10000px';
        const svg=document.importNode(doc.documentElement,true);host.append(svg);document.body.append(host);await document.fonts.ready;
        const frame=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text[data-namelecule-role=label]')];
        const fonts=labels.map(n=>{const m=n.getScreenCTM();return parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b)});
        rows.push({id,labels:labels.length,minFont:Math.min(...fonts),maxFont:Math.max(...fonts),clipped:labels.some(n=>{const b=n.getBoundingClientRect();return b.left<frame.left||b.right>frame.right||b.top<frame.top||b.bottom>frame.bottom})});host.remove();
      }return JSON.stringify(rows);
    })()"""))
    for row in assets:
        check(row["labels"] == {"methane": 5, "propane": 11}[row["id"]] and not row["clipped"] and abs(row["minFont"] - 22) < .02 and abs(row["maxFont"] - 22) < .02,
              "Exported asset decodes with 22px glyphs and complete frame " + row["id"], row)
    out["assetAudit"] = assets

    # Simulate a browser lacking Worker. Expected failure is visible and retryable.
    preload = call("script.addPreloadScript", {"functionDeclaration": "()=>{window.__originalWorker=window.Worker;window.Worker=undefined;}", "contexts": [ctx]})["script"]
    navigate("games/name-repair.html?source=engine")
    until("document.querySelector('.loading-card h1')?.textContent==='Ο πάγκος δεν άνοιξε ακόμη'")
    check(ev("!!document.querySelector('.loading-card .secondary')&&!document.querySelector('.part-button')"), "Unavailable engine fails visibly without pretending to grade")
    call("script.removePreloadScript", {"script": preload})
    preload = None
    ev("window.Worker=window.__originalWorker;true")
    click(".loading-card .primary")
    until("!!document.querySelector('#set-alkanes-start')||!!document.querySelector('.diagram-image.is-ready')")
    check(True, "Retry recovers after engine becomes available")
    # A forged jump to the third question cannot skip earlier repairs.
    ev("(()=>{const r=JSON.parse(sessionStorage.getItem('namelecule-repair-engine-pilot-v1'));r.phase='round';r.roundIndex=2;r.states=r.states.map(s=>({...s,solved:false,submitted:false}));sessionStorage.setItem('namelecule-repair-engine-pilot-v1',JSON.stringify(r));})();true")
    call("browsingContext.reload", {"context": ctx, "wait": "complete"})
    until("!!document.querySelector('#set-alkanes-start')")
    check(recipe()["phase"] == "hub" and not recipe()["states"], "Saved progress cannot bypass earlier unsolved rounds")
    out["completed"] = True
except Exception as error:
    out.update(failure=str(error), traceback=traceback.format_exc())
    print(out["traceback"], flush=True)
    try:
        screenshot(HERE / "recovery-failure.png")
    except Exception:
        pass
finally:
    if preload:
        call("script.removePreloadScript", {"script": preload})
    out["javascriptErrors"] = js_errors
    out["diagnostics"] = [e for e in all_events if e.get("method") == "log.entryAdded" and e.get("params", {}).get("level") in ["error", "warn"]]
    out["sourceSHA256"] = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in [
        "js/namelecule-game-repair.js", "js/namelecule-chemistry-client.js", "js/namelecule-chemistry-worker.js", "js/namelecule-repair-generator.js", "games/data/alkane-structures.json"]}
    (HERE / "families-and-recovery.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    call("browsingContext.close", {"context": ctx})
    call("session.end", {})
    print(json.dumps({"completed": out["completed"], "checks": len(out["checks"]), "javascriptErrors": len(js_errors), "failure": out.get("failure")}), flush=True)
if not out["completed"] or js_errors:
    raise SystemExit(1)
