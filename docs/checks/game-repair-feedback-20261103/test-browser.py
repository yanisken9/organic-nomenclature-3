"""Targeted feedback/hint-removal checks; reuses prior real-input helpers."""
from pathlib import Path
import os
os.environ['NAMELECULE_BIDI_PORT'] = '9242'
os.environ['NAMELECULE_TEST_BASE_URL'] = 'http://127.0.0.1:8013/'
support = Path('docs/checks/game-repair-20261103/test-browser.py').read_text().split('\ntry:\n', 1)[0]
support = support.replace('HERE = ROOT / "docs/checks/game-repair-20261103"', 'HERE = ROOT / "docs/checks/game-repair-feedback-20261103"')
exec(compile(support, 'existing-game-browser-support', 'exec'))

MINIMAL = 'Αυτό το συνθετικό συμφωνεί με τη δομή.'
try:
    for width, touch in [(1500, False), (390, True)]:
        call('browsingContext.setViewport', {'context': ctx, 'viewport': {'width': width, 'height': 950}, 'devicePixelRatio': 1})
        navigate('games/name-repair.html?v=feedback-20261103-r2')
        until('!!document.querySelector(".intro-start")')
        check(not ev('document.body.innerText.includes("υποδείξ")||document.body.innerText.includes("Βοήθεια όποτε")'), 'Intro makes no removed-feature promises ' + str(width))
        click('.intro-start', touch)
        for r in GAME['rounds']:
            ready()
            no_overflow(str(width) + ' round ' + r['id'])
            check(not ev('!!document.querySelector(".hint-card,.hint-list,.hint-image")'), 'No optional hints in DOM ' + r['id'])
            check(not ev('!!document.querySelector(".success-explanation")'), 'No success explanation before correct repair ' + r['id'])
            if r['kind'] == 'replace':
                for part in r['parts']:
                    if part['id'] == r['targetPartId']:
                        continue
                    (lambda s: click(s, touch))('#part-' + part['id'])
                    check(ev('document.querySelector(".part-selection-status").textContent') == MINIMAL, 'Exact minimal feedback ' + r['id'] + '/' + part['id'])
                    check(ev('document.querySelector(".choice-fieldset").hidden'), 'Wrong part does not expose replacement choices')
                check(ev('document.querySelector(".session-row > span").textContent.trim().endsWith("0")'), 'Part selection does not submit repair ' + r['id'])
            if r['id'] == 'parent-not-total':
                click('#part-root', touch)
                wrong = next(i for i, c in enumerate(r['choices']) if c['value'] != r['correctValue'])
                click('#choice-' + str(wrong), touch)
                click('#check-button', touch)
                check(ev('document.querySelector(".feedback").textContent') == r['choices'][wrong]['feedback'], 'Separate wrong-replacement explanation retained')
                check(not ev('!!document.querySelector(".success-explanation")'), 'Wrong replacement never gets success explanation')
                click('.repair-actions .quiet', touch)
                check(ev('document.querySelector(".session-row > span").textContent.trim().endsWith("1")'), 'Retry preserves attempts')
                screenshot(HERE / ('minimal-feedback-' + str(width) + '.png'))
            solve(r, keyboard=not touch, touch=touch)
            check(ev('document.querySelector(".success-explanation").textContent') == r['successText'], 'Exact explanatory success text ' + r['id'])
            check(not ev('document.querySelector(".session-row").textContent.includes("Υποδείξ")'), 'No hint counter ' + r['id'])
            if r['id'] == 'parent-not-total':
                screenshot(HERE / ('success-' + str(width) + '.png'))
            click('.round-next button', touch)
        until('!!document.querySelector(".results")')
        summary = json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))'))
        check(summary == [4, 5], 'Completed/attempts summary excludes guided ' + str(width), summary=summary)
        check(not ev('document.querySelector(".results").innerText.includes("υπόδειξ")||!!document.querySelector(".result-assistance")'), 'No removed hint classifications in summary ' + str(width))
        no_overflow(str(width) + ' summary no overflow')
        screenshot(HERE / ('results-' + str(width) + '.png'))
        out['journeys'].append({'width': width, 'touch': touch, 'summary': summary, 'rounds': 5})
        click('.results-actions button', touch)
        until('!!document.querySelector(".intro-start")')
        click('.intro-start', touch)
        ready()
        check(ev('document.querySelector(".session-row > span").textContent.trim().endsWith("0")'), 'Full restart clears attempts ' + str(width))
    # Missing base drawing must still block assessment after hint readiness was
    # removed from the state machine. Restore the source via the public retry.
    preload = call('script.addPreloadScript', {'contexts': [ctx], 'functionDeclaration': r'''()=>{
      window.__failImage=true;const src=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
      Object.defineProperty(HTMLImageElement.prototype,'src',{...src,set(value){
        src.set.call(this,window.__failImage&&String(value).endsWith('butane.svg')?'assets/name-repair/deliberate-missing.svg':value);
      }});
    }'''})['script']
    navigate('games/name-repair.html?v=feedback-20261103-r2')
    until('!!document.querySelector(".intro-start")')
    click('.intro-start')
    until('document.querySelector(".image-status").textContent.includes("δεν εμφανίστηκε")')
    check(ev('document.querySelector("#check-button").disabled&&[...document.querySelectorAll(".part-button")].every(n=>n.disabled)'), 'Missing SVG still gates answers')
    ev('window.__failImage=false;true')
    text_button('Φόρτωσε ξανά τη δομή')
    ready()
    check(ev('!document.querySelector("#part-root").disabled'), 'Base SVG recovery still works')
    call('script.removePreloadScript', {'script': preload})
    out['completed'] = True
except Exception as error:
    out.update(failure=str(error), traceback=traceback.format_exc())
    print(out['traceback'], flush=True)
    try:
        screenshot(HERE / 'failure.png')
    except Exception:
        pass
finally:
    out['javascriptErrors'] = js_errors
    out['diagnostics'] = [e for e in all_events if e.get('method') == 'log.entryAdded' and e.get('params', {}).get('level') in ['error', 'warn']]
    (HERE / 'browser.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    call('browsingContext.close', {'context': ctx})
    call('session.end', {})
    print(json.dumps({'completed': out['completed'], 'checks': len(out['checks']), 'journeys': len(out['journeys']), 'JavaScriptErrors': len(js_errors)}), flush=True)
if not out['completed'] or js_errors:
    raise SystemExit(1)
