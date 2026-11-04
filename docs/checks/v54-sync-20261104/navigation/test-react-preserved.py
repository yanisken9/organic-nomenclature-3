"""Evidence-only preserved React smoke; no source changes or build."""
from pathlib import Path
import os
os.environ['NAMELECULE_BIDI_PORT']='9246'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
support=Path('docs/checks/game-repair-20261103/test-browser.py').read_text().split('\ntry:\n',1)[0]
support=support.replace('HERE = ROOT / "docs/checks/game-repair-20261103"',
                        'HERE = ROOT / "docs/checks/v54-sync-20261104/navigation"')
exec(compile(support,'existing-browser-input-support','exec'))
call('session.subscribe',{'events':['network.responseCompleted'],'contexts':[ctx]})
ready_react='!!document.querySelector(".molecule-stage iframe:not([hidden])")&&!document.getElementById("molecule-select").disabled&&document.querySelector(".molecule-stage").getAttribute("aria-busy")==="false"'

def inner(expr):
    return ev('document.querySelector("iframe").contentWindow.eval('+json.dumps(expr)+')')

def model(key,count):
    until(ready_react)
    until('document.querySelector("iframe").contentWindow.eval("selectedMol")==='+json.dumps(key))
    until('Number(document.querySelector("iframe").contentWindow.eval(\'Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count")\'))==='+str(count))
    check(inner('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")'),key+' actual 2D SVG')
    check(True,key+' actual JSmol atom count',atoms=count)

try:
    navigate('react-preview/dist/#/library')
    until("Array.from(document.querySelectorAll('.lessons a')).filter(a=>a.getAttribute('href').startsWith('#/lesson/')).length===12")
    check(True,'Preserved React library exposes twelve lessons')
    screenshot(HERE/'react-library.png')
    navigate('react-preview/dist/#/viewer');model('ethanol',9)
    check(ev('document.getElementById("molecule-results").textContent.includes("126")'),'Preserved React catalog reports 126')
    click('input[name=mode][value=expanded]');until(ready_react)
    check(inner('mode2D')=='expanded','React expanded-mode switch')
    until('!!document.querySelector(".react-name-components button:not(:disabled)")')
    component=ev('document.querySelector(".react-name-components button:not(:disabled)").dataset.component')
    activate('.react-name-components button[data-component='+component+']')
    until('document.querySelector("[data-component='+component+']").getAttribute("aria-pressed")==="true"')
    check(inner('document.querySelector("#'+component+'").classList.contains("selected")'),'React component selection reaches actual viewer',component=component)
    click('.molecule-views button:nth-child(2)');until(ready_react)
    check(ev('!!document.getElementById("style-3d")'),'React actual 3D view controls')
    check(inner('document.documentElement.dataset.view')=='3d','Iframe actual 3D mode')
    selected=inner('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{selected}.count"))')
    check(0<selected<=9,'Component highlights an actual JSmol atom selection',selectedAtoms=selected)
    screenshot(HERE/'react-3d.png')
    click('.molecule-views button:nth-child(1)');until(ready_react)
    ev('document.getElementById("molecule-select").value="methane";document.getElementById("molecule-select").dispatchEvent(new Event("change",{bubbles:true}));true')
    model('methane',5)
    scripts=json.loads(inner('JSON.stringify([...document.scripts].map(s=>s.src).filter(Boolean))'))
    pinned=[s for s in scripts if 'preserved-main-20261030/' in s]
    check(len(pinned)==2 and any('data_52.js' in s for s in pinned)and any('molview-52.js' in s for s in pinned),'Preserved data52 and viewer52 references',scripts=pinned)
    check(any('/js/mulermoc-nom-core-52.js' in s for s in scripts)and not any('core-54.js' in s for s in scripts),'React keeps original core52 reference')
    screenshot(HERE/'react-viewer.png')
    navigate('react-preview/dist/#/lesson/monoalcohols/step/1')
    until('!!document.querySelector(".lesson-stage iframe:not([hidden])")&&!document.getElementById("lesson-next").disabled')
    check(inner('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG[data-label-error]")'),'React lesson actual 2D SVG')
    screenshot(HERE/'react-lesson-step1.png')
    click('#lesson-next')
    until('location.hash.endsWith("/step/2")&&!document.getElementById("lesson-prev").disabled&&!document.querySelector(".lesson-stage iframe").hidden')
    check(True,'React lesson Next reaches step2')
    click('#lesson-prev')
    until('location.hash.endsWith("/step/1")&&!document.querySelector(".lesson-stage iframe").hidden')
    check(True,'React lesson Previous returns step1')
    click('.lesson-navigation a');until('location.hash==="#/library"')
    check(True,'React lesson Exit returns library')
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
    try:screenshot(HERE/'react-failure.png')
    except Exception:pass
finally:
    out['javascriptErrors']=js_errors
    out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
    out['failedResponses']=[{'url':e['params'].get('request',{}).get('url'),
       'status':e['params'].get('response',{}).get('status')}for e in all_events if e.get('method')=='network.responseCompleted'and e.get('params',{}).get('response',{}).get('status',0)>=400]
    (HERE/'react-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failedResponses':out['failedResponses']}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
