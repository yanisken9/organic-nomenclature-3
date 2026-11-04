"""Targeted post-review verification; no production files changed."""
from pathlib import Path
import os
import json
import traceback
os.environ.setdefault('NAMELECULE_BIDI_PORT','9241')
os.environ.setdefault('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8053/')
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
HERE=Path('docs/checks/game-repair-20261103')
data=json.loads(Path('games/data/name-repair-alkanes.json').read_text())
out={'completed':False,'rounds':[],'tabPresses':0}
def key(value):
    call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
def tab_to(selector):
    for _ in range(45):
        if ev('document.activeElement.matches('+json.dumps(selector)+')'):return
        key('\ue004');out['tabPresses']+=1
    raise AssertionError('Tab cannot reach '+selector)
def enter(selector):
    tab_to(selector);key('\ue007')
try:
    navigate('games/name-repair.html');until('!!document.querySelector(".intro-start")')
    enter('.intro-start')
    for r in data['rounds']:
        until('!!document.querySelector(".diagram-image.is-ready")')
        if r['kind']=='replace':
            enter('#part-'+r['targetPartId'])
            option=next(i for i,c in enumerate(r['choices'])if c['value']==r['correctValue'])
            enter('#choice-'+str(option))
        else:
            enter('#part-ethylGroup');enter('#move-left')
        enter('#check-button');until('!!document.querySelector(".feedback.is-success")')
        out['rounds'].append(r['id']);enter('.round-next button')
    until('!!document.querySelector(".results")')
    assert ev('[...document.querySelectorAll(".stat-number")].map(n=>n.textContent).join()')=='4,0,4'
    out['fullTabEnterJourney']=True
    out['externalGameResources']=json.loads(ev('JSON.stringify(performance.getEntriesByType("resource").filter(e=>new URL(e.name).origin!==location.origin).map(e=>e.name))'))
    assert not out['externalGameResources']
    enter('.exit-link');until('location.pathname.endsWith("/design/welcome-proposal.html")')
    call('browsingContext.traverseHistory',{'context':ctx,'delta':-1})
    until('location.pathname.endsWith("/games/name-repair.html")&&!!document.querySelector(".results,.intro-start")')
    out['backRestored']=ev('document.querySelector(".results")?"results":"intro"')
    assert ev('!!document.querySelector(".exit-link")')
    out['completed']=True
except Exception as e:
    out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:
    out['javascriptErrors']=js_errors
    (HERE/'tab-and-back.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps(out,ensure_ascii=False),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
