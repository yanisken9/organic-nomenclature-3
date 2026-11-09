"""Real Firefox mouse/keyboard/touch journeys, render checks and fault recovery."""
from pathlib import Path
import json
import os
import traceback

ROOT = Path.cwd()
HERE = ROOT / "docs/checks/game-repair-20261103"
os.environ.setdefault("NAMELECULE_BIDI_PORT", "9241")
os.environ.setdefault("NAMELECULE_TEST_BASE_URL", "http://127.0.0.1:8053/")
exec(compile((ROOT / "tools/namelecule_bidi.py").read_text(), "bidi", "exec"))
GAME = json.loads((ROOT / "games/data/name-repair-alkanes.json").read_text())
out = {"completed": False, "checks": [], "journeys": [], "faults": []}


def check(condition, label, **details):
    assert condition, (label, details)
    out["checks"].append({"label": label, **details})


def click_expr(expr, touch=False):
    point = json.loads(ev("(()=>{const n=" + expr + ";if(!n||n.disabled)throw Error('Missing/disabled test control');n.scrollIntoView({block:'center'});const r=n.getBoundingClientRect();return JSON.stringify({x:r.x+r.width/2,y:r.y+r.height/2})})()"))
    call("input.performActions", {"context": ctx, "actions": [{"type": "pointer", "id": "finger" if touch else "mouse", "parameters": {"pointerType": "touch" if touch else "mouse"}, "actions": [{"type": "pointerMove", "x": round(point["x"]), "y": round(point["y"]), "duration": 0}, {"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]}]})


def click(selector, touch=False):
    click_expr("document.querySelector(" + json.dumps(selector) + ")", touch)


def text_button(text, touch=False):
    click_expr("[...document.querySelectorAll('button')].find(n=>n.textContent.trim().startsWith(" + json.dumps(text) + "))", touch)


def key(value):
    call("input.performActions", {"context": ctx, "actions": [{"type": "key", "id": "keyboard", "actions": [{"type": "keyDown", "value": value}, {"type": "keyUp", "value": value}]}]})


def activate(selector):
    ev("document.querySelector(" + json.dumps(selector) + ").focus();true")
    key("\ue007")  # actual Enter activation, not synthetic DOM click


def ready():
    until("!!document.querySelector('.diagram-image.is-ready')")


def stats():
    return ev("document.querySelector('.session-row').textContent")


def no_overflow(label):
    check(ev("document.documentElement.scrollWidth<=innerWidth"), label)


def solve(r, keyboard=False, touch=False):
    if r["kind"] == "replace":
        selector = "#part-" + r["targetPartId"]
        (activate if keyboard else lambda s: click(s, touch))(selector)
        choice = next(i for i, c in enumerate(r["choices"]) if c["value"] == r["correctValue"])
        (activate if keyboard else lambda s: click(s, touch))("#choice-" + str(choice))
    else:
        (activate if keyboard else lambda s: click(s, touch))("#part-ethylGroup")
        (activate if keyboard else lambda s: click(s, touch))("#move-left")
    check(ev("document.querySelector('.candidate-name').textContent") == r["correctName"], "Candidate exact " + r["id"])
    (activate if keyboard else lambda s: click(s, touch))("#check-button")
    until("!!document.querySelector('.feedback.is-success')")
    check(ev("document.querySelector('.success-name').textContent") == r["correctName"], "Accepted exact " + r["id"])
    check(ev("[...document.querySelectorAll('.part-button,.choice-button')].every(n=>n.disabled)"), "Solved round locked " + r["id"])


try:
    navigate("games/name-repair.html")
    until("!!document.querySelector('.intro-start')")
    screenshot(HERE / "intro-1500.png")
    no_overflow("Desktop intro no overflow")
    # Decode actual standalone SVG image resources, then measure their native
    # label sizes and full-label framing as embedded SVG documents.
    assets = [r["file"] for r in json.loads((ROOT / "games/assets/name-repair/provenance.json").read_text())["assets"]]
    audit = json.loads(ev("""(async()=>{const names=ASSET_NAMES,result=[];for(const name of names){
      const url='assets/name-repair/'+name,img=new Image();img.src=url;await img.decode();
      const xml=await(await fetch(url)).text(),doc=new DOMParser().parseFromString(xml,'image/svg+xml');
      if(doc.querySelector('parsererror'))throw Error('Invalid assetXML '+name);
      const host=document.createElement('div');host.style.cssText='position:fixed;left:-10000px;top:0;opacity:0';
      const svg=document.importNode(doc.documentElement,true);host.append(svg);document.body.append(host);
      await document.fonts.ready;const viewport=svg.getBoundingClientRect();
      const labels=[...svg.querySelectorAll('text[data-namelecule-role="label"]')];
      const fonts=labels.map(n=>{const m=n.getScreenCTM();return parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b)});
      const clipped=[...svg.querySelectorAll('text')].some(n=>{const b=n.getBoundingClientRect();return b.left<viewport.left||b.right>viewport.right||b.top<viewport.top||b.bottom>viewport.bottom});
      result.push({name,decoded:true,labels:labels.length,minFont:Math.min(...fonts),maxFont:Math.max(...fonts),clipped});host.remove();
    }return JSON.stringify(result)})()""".replace("ASSET_NAMES", json.dumps(assets))))
    for row in audit:
        check(row["decoded"] and not row["clipped"] and abs(row["minFont"] - 22) < .02 and abs(row["maxFont"] - 22) < .02, "Standalone SVG decode/font/frame " + row["name"], **row)
    out["assetAudit"] = audit
    activate(".intro-start")
    for index, r in enumerate(GAME["rounds"]):
        ready()
        no_overflow("Desktop round " + r["id"])
        if not r["guided"]:
            check(not ev("document.querySelector('.round-screen').innerText.includes(" + json.dumps(r["correctName"]) + ")"), "Answer not pre-displayed " + r["id"])
        if index == 1:
            screenshot(HERE / "round-1500.png")
        if index == 4:
            screenshot(HERE / "large-1500.png")
        solve(r, keyboard=True)
        check(ev("document.activeElement===document.querySelector('.round-next button')"), "Keyboard focus reaches next " + r["id"])
        activate(".round-next button")
    until("!!document.querySelector('.results')")
    summary = json.loads(ev("JSON.stringify([...document.querySelectorAll('.stat-number')].map(n=>Number(n.textContent)))"))
    check(summary == [4, 0, 4], "Unassisted keyboard journey counts", summary=summary)
    screenshot(HERE / "results-1500.png")
    out["journeys"].append({"input": "keyboard", "width": 1500, "summary": summary, "allFiveRounds": True})
    game_errors = list(js_errors)
    check(not game_errors, "No normal-game JavaScript errors", errors=game_errors)

    # A second real-input journey exercises wrong selection, wrong repair,
    # successive hints, retry accounting, diagram zoom and touch at 390px.
    call("browsingContext.setViewport", {"context": ctx, "viewport": {"width": 390, "height": 844}, "devicePixelRatio": 1})
    navigate("games/name-repair.html")
    until("!!document.querySelector('.intro-start')")
    no_overflow("Mobile intro no overflow")
    screenshot(HERE / "intro-390.png")
    click(".intro-start", touch=True)
    for index, r in enumerate(GAME["rounds"]):
        ready()
        no_overflow("Mobile round " + r["id"])
        if index in [0, 1]:
            text_button("Μια υπόδειξη", touch=True)
            text_button("Επόμενη ιδέα", touch=True)
            until("!!document.querySelector('.hint-image')&&document.querySelector('.hint-image').naturalWidth>0&&!document.querySelector('.hint-image').hidden")
            check(ev("document.querySelector('.hint-image').complete"), "Numbered hint visible " + r["id"])
        if index == 1:
            click("#part-ending", touch=True)
            check("συμφωνεί" in ev("document.querySelector('.part-selection-status').textContent"), "Wrong part gets specific feedback")
            click("#part-root", touch=True)
            old_order = ev("[...document.querySelectorAll('.choice-button')].map(n=>n.textContent).join('|')")
            wrong = next(i for i, c in enumerate(r["choices"]) if c["value"] != r["correctValue"])
            click("#choice-" + str(wrong), touch=True)
            click("#check-button", touch=True)
            check(ev("document.querySelector('.feedback').textContent") == r["choices"][wrong]["feedback"], "Choice-specific wrong repair feedback")
            check("1 · Υποδείξεις 2" in stats(), "Wrong attempt counted once")
            click(".repair-actions .quiet", touch=True)
            check("1 · Υποδείξεις 2" in stats(), "Retry preserves attempts and hints")
            click("#part-root", touch=True)
            check(ev("[...document.querySelectorAll('.choice-button')].map(n=>n.textContent).join('|')") == old_order, "Retry preserves shuffled choice order")
            screenshot(HERE / "hints-390.png")
        if index == 3:
            text_button("Μια υπόδειξη", touch=True)
        if index == 4:
            text_button("Μεγέθυνση σχεδίου", touch=True)
            until("!!document.querySelector('dialog[open] .zoom-image')&&document.querySelector('.zoom-image').naturalWidth>0")
            check(ev("document.querySelector('.zoom-viewport').scrollWidth>document.querySelector('.zoom-viewport').clientWidth"), "Large mobile diagram can scroll at native size")
            no_overflow("Mobile zoom no page overflow")
            key("\ue00c")
            until("!document.querySelector('dialog[open]')")
            screenshot(HERE / "large-390.png")
        solve(r, touch=True)
        click(".round-next button", touch=True)
    until("!!document.querySelector('.results')")
    summary = json.loads(ev("JSON.stringify([...document.querySelectorAll('.stat-number')].map(n=>Number(n.textContent)))"))
    check(summary == [2, 2, 5], "Mobile retry/hints summary excludes example", summary=summary)
    no_overflow("Mobile results no overflow")
    screenshot(HERE / "results-390.png")
    out["journeys"].append({"input": "touch+mouse", "width": 390, "summary": summary, "hintsAndRetry": True})
    click(".results-actions button")
    until("!!document.querySelector('.intro-start')")
    click(".intro-start")
    ready()
    click("#part-root")
    text_button("Νέο παιχνίδι")
    until("!!document.querySelector('dialog[open]')")
    text_button("Συνέχισε εδώ")
    check(ev("!!document.querySelector('#part-root[aria-pressed=true]')"), "Restart cancel preserves round")
    text_button("Νέο παιχνίδι")
    click_expr("document.querySelector('dialog[open] .primary')")
    until("!!document.querySelector('.intro-start')")
    click(".intro-start")
    ready()
    check("0 · Υποδείξεις 0" in stats(), "Full restart clears session")

    # Inject failures only in this isolated browser context. Missing SVG must
    # disable assessment and offer real recovery; fetch/schema errors must retry.
    preload = call("script.addPreloadScript", {"contexts": [ctx], "functionDeclaration": r"""()=>{
      window.__failData=false;window.__invalidData=false;window.__failMain=false;window.__failHint=false;
      const fetchOriginal=window.fetch;window.fetch=function(url,opts){
        if(String(url).includes('name-repair-alkanes.json')){
          if(window.__failData)return Promise.reject(Error('Deliberate test fetch failure'));
          if(window.__invalidData)return Promise.resolve(new Response('{"schemaVersion":0}',{status:200}));
        }return fetchOriginal.call(this,url,opts);
      };
      const src=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
      Object.defineProperty(HTMLImageElement.prototype,'src',{...src,set(value){
        if((window.__failMain&&String(value).endsWith('butane.svg'))||(window.__failHint&&String(value).endsWith('butane-chain.svg')))value='assets/name-repair/deliberate-missing.svg';
        src.set.call(this,value);
      }});
    }"""})["script"]
    navigate("games/name-repair.html")
    until("!!document.querySelector('.intro-start')")
    ev("window.__failMain=true;true")
    click(".intro-start")
    until("document.querySelector('.image-status').textContent.includes('δεν εμφανίστηκε')")
    check(ev("document.querySelector('#check-button').disabled&&[...document.querySelectorAll('.part-button')].every(n=>n.disabled)"), "Missing main SVG blocks answering")
    ev("window.__failMain=false;true")
    text_button("Φόρτωσε ξανά τη δομή")
    ready()
    check(ev("!document.querySelector('#part-root').disabled"), "Missing main SVG recovers")
    ev("window.__failHint=true;true")
    text_button("Μια υπόδειξη")
    text_button("Επόμενη ιδέα")
    until("document.querySelector('.hint-image-error').textContent.includes('δεν εμφανίστηκε')")
    check(ev("document.querySelector('#check-button').disabled"), "Missing opened hint blocks check")
    ev("window.__failHint=false;true")
    text_button("Φόρτωσε ξανά την υπόδειξη")
    until("!!document.querySelector('.hint-image')&&!document.querySelector('.hint-image').hidden")
    check(ev("!document.querySelector('#part-root').disabled"), "Missing hint SVG recovers")
    out["faults"].append({"missingMainAndHintSVG": "blocked and recovered"})
    for variable in ["__failData", "__invalidData"]:
        ev("window." + variable + "=true;true")
        text_button("Νέο παιχνίδι")
        click_expr("document.querySelector('dialog[open] .primary')")
        # Reload data through its public retry button in a deliberately failed
        # fresh document; preload sets booleans, add one-time task before load.
        bad = call("script.addPreloadScript", {"contexts": [ctx], "functionDeclaration": "()=>{window." + variable + "=true;}"})["script"]
        navigate("games/name-repair.html")
        until("document.querySelector('h1').textContent==='Ο πάγκος δεν άνοιξε ακόμη'")
        check(not ev("!!document.querySelector('.intro-start')"), "Invalid/unavailable data not playable " + variable)
        ev("window." + variable + "=false;true")
        text_button("Δοκίμασε ξανά")
        until("!!document.querySelector('.intro-start')")
        call("script.removePreloadScript", {"script": bad})
        out["faults"].append({"dataFailure": variable, "recovered": True})
        click(".intro-start")
        ready()
        click("#part-root")
    call("script.removePreloadScript", {"script": preload})
    # Navigating away and browser back is a fresh playable page; no progress
    # persistence is promised by this in-memory prototype.
    click(".exit-link")
    until("location.pathname.endsWith('/design/welcome-proposal.html')")
    check(ev("!!document.querySelector('a[href*=theory-library]')"), "Exit reaches existing welcome")
    out["completed"] = True
except Exception as error:
    out.update(failure=str(error), traceback=traceback.format_exc())
    print(out["traceback"], flush=True)
    try:
        out["failedPage"] = ev("document.body.innerText")
        screenshot(HERE / "browser-failure.png")
    except Exception:
        pass
finally:
    out["javascriptErrors"] = js_errors
    out["diagnostics"] = [e for e in all_events if e.get("method") == "log.entryAdded" and e.get("params", {}).get("level") in ["error", "warn"]]
    (HERE / "browser.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    call("browsingContext.close", {"context": ctx})
    call("session.end", {})
    print(json.dumps({"completed": out["completed"], "checks": len(out["checks"]), "journeys": len(out["journeys"]), "faults": len(out["faults"]), "rawJavaScriptErrors": len(js_errors)}), flush=True)
if not out["completed"]:
    raise SystemExit(1)
