"""Bounded actual-UI checks for the approved decorative 3D logo."""
from pathlib import Path
import os
os.environ['NAMELECULE_BIDI_PORT'] = '9243'
os.environ['NAMELECULE_TEST_BASE_URL'] = 'http://127.0.0.1:8013/'
support = Path('docs/checks/game-repair-20261103/test-browser.py').read_text().split('\ntry:\n', 1)[0]
support = support.replace('HERE = ROOT / "docs/checks/game-repair-20261103"', 'HERE = ROOT / "docs/checks/game-workshop-logo-20261104"')
exec(compile(support, 'existing-browser-support', 'exec'))

def viewport(width):
    call('browsingContext.setViewport', {'context': ctx, 'viewport': {'width': width, 'height': 980}, 'devicePixelRatio': 1})

def logo_ok(selector, width):
    until('document.querySelector(' + json.dumps(selector) + ').naturalWidth>0')
    check(ev("(()=>{const n=document.querySelector(" + json.dumps(selector) + ");return n.complete&&n.alt===''&&n.getAttribute('aria-hidden')==='true'&&n.tabIndex<0&&n.currentSrc.endsWith('/workshop-logo-3d-v1.png')})()"), 'Accepted decorative logo decoded ' + str(width))

try:
    navigate('games/name-repair.html?v=logo-3d-20261104-r1')
    until('!!document.querySelector(".intro-start")')
    for width in [1500, 768, 550, 431, 390, 320]:
        viewport(width)
        logo_ok('.workshop-logo', width)
        no_overflow('Intro no overflow ' + str(width))
        check(ev("(()=>{const img=document.querySelector('.workshop-logo').getBoundingClientRect(),title=document.querySelector('.workshop-title h1').getBoundingClientRect();return img.right<=title.left&&title.right<=innerWidth})()"), 'Intro logo separate from title ' + str(width))
        if width in [1500, 390]:
            ev('scrollTo(0,0);true')
            screenshot(HERE / ('intro-3d-' + str(width) + '.png'))
    viewport(1500)
    activate('.intro-start')
    ready()
    for width in [1500, 768, 550, 431, 390, 320]:
        viewport(width)
        logo_ok('.workshop-logo-small', width)
        no_overflow('Mission no overflow ' + str(width))
        check(ev("(()=>{const brand=document.querySelector('.round-game-brand'),progress=document.querySelector('.progress'),a=brand.getBoundingClientRect(),b=progress.getBoundingClientRect();return a.right<=b.left&&brand.scrollWidth<=brand.clientWidth+1})()"), 'Mission logo/label separate from progress ' + str(width))
        if width in [1500, 390]:
            ev('scrollTo(0,0);true')
            screenshot(HERE / ('round-3d-' + str(width) + '.png'))
    viewport(1500)
    for r in GAME['rounds']:
        ready()
        logo_ok('.workshop-logo-small', 1500)
        solve(r, keyboard=True)
        check(ev("document.querySelector('.success-explanation').textContent") == r['successText'], 'Success explanation preserved ' + r['id'])
        activate('.round-next button')
    until('!!document.querySelector(".results")')
    check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))')) == [4, 4], 'Full journey counters preserved')
    activate('.results-actions button')
    until('!!document.querySelector(".intro-start")')
    logo_ok('.workshop-logo', 1500)
    viewport(390)
    click('.intro-start', touch=True)
    ready()
    logo_ok('.workshop-logo-small', 390)
    check(ev('document.querySelector(".session-row > span").textContent.trim().endsWith("0")'), 'Restart clears attempts')
    solve(GAME['rounds'][0], touch=True)
    click('.round-next button', touch=True)
    ready()
    logo_ok('.workshop-logo-small', 390)
    out['journeys'] = [{'width':1500,'input':'keyboard','rounds':5,'restart':True}, {'width':390,'input':'simulated touch','rounds':1,'next':True}]
    out['completed'] = True
except Exception as error:
    out.update(failure=str(error), traceback=traceback.format_exc())
    print(out['traceback'], flush=True)
    screenshot(HERE / 'integration-failure.png')
finally:
    out['javascriptErrors'] = js_errors
    out['diagnostics'] = [e for e in all_events if e.get('method') == 'log.entryAdded' and e.get('params', {}).get('level') in ['error','warn']]
    (HERE / 'integration-browser.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    call('browsingContext.close', {'context':ctx})
    call('session.end', {})
    print(json.dumps({'completed':out['completed'], 'checks':len(out['checks']), 'JavaScriptErrors':len(js_errors)}), flush=True)
if not out['completed'] or js_errors:
    raise SystemExit(1)
