"""Actual wrong-model timeout/retry, pending route and teardown checks, Firefox9238."""
from pathlib import Path
helper = Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\nimport hashlib', 1)[0].replace('9237', '9238')
exec(compile(helper, 'existing-bidi-lifecycle', 'exec'))
folder = Path('/tmp/namelecule-react-lesson-20261027')
result = {'completed': False, 'checks': []}
child = None

def ce(expr):
    r=call('script.evaluate',{'expression':expr,'target':{'context':child},'awaitPromise':True})
    if r.get('type')=='exception': raise RuntimeError(r.get('exceptionDetails'))
    return r['result'].get('value')

def wait(expr, seconds=95):
    for _ in range(seconds*10):
        if ev(expr): return
        time.sleep(.1)
    raise AssertionError(expr)

def attach():
    global child
    child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context']

try:
    navigate('react-preview/dist/?v=lesson-lifecycle-'+str(time.time_ns())+'#/lesson/alkanes/step/20')
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')"); attach()
    # Real adapter deadline, not a substituted timer. Fault only the actual
    # Jmol model-file report; keep native load/atoms/bonds behavior running.
    ce("window.__modelProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...args){let v=__modelProperty.call(this,a,p,...args);return p==='modelInfo'?{...v,models:(v.models||[]).map(m=>({...m,file:'wrong-model.sdf'}))}:v}")
    started=time.monotonic();ev("document.getElementById('lesson-next').click()")
    wait("!!document.querySelector('.lesson-status[role=alert]')",22)
    result['wrongModelTimeoutSeconds']=round(time.monotonic()-started,2)
    assert 14.5 <= result['wrongModelTimeoutSeconds'] <= 17.5
    assert ev("document.querySelector('.lesson-stage iframe').hidden && document.getElementById('lesson-next').disabled")
    ev("document.querySelector('.lesson-status button').click()")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')");attach()
    assert ce("fScenarioPresent().index===20 && (Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models||[])[0].file.endsWith('/ethyl_3_dimethyl_2_5_hexane_3D.sdf')")
    result['checks'].append('Actual15s host deadline rejects wrong3D model; no false ready; retry reloads correct model at requested step21')
    # Trigger a native delayed3D transition, unmount immediately, then remount
    # at1. Old callbacks must neither restore the previous route nor ACK it.
    ev("location.hash='#/lesson/alkanes/step/20'")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])') && document.getElementById('lesson-position').textContent==='20/21'")
    ev("location.hash='#/lesson/alkanes/step/21';setTimeout(()=>{location.hash='#/library'},0)")
    wait("location.hash==='#/library' && !document.querySelector('iframe')")
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')");attach()
    time.sleep(2.5)
    assert ev("location.hash==='#/lesson/alkanes/step/1' && !document.querySelector('.lesson-status[role=alert]')")
    assert ce('fScenarioPresent().index===0 && selectedMol===\'ethane\'')
    ev("document.querySelector('.lesson-navigation a').click()")
    wait("location.hash==='#/library' && !document.querySelector('iframe')")
    # The library retains its React filter state across the pilot route.
    ev("document.getElementById('lesson-category').value='alkanes';document.getElementById('lesson-category').dispatchEvent(new Event('change',{bubbles:true}))")
    wait("document.querySelectorAll('article.lesson').length===1")
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')")
    ev("document.querySelector('.lesson-navigation a').click()")
    wait("location.hash==='#/library'")
    assert ev("document.getElementById('lesson-category').value==='alkanes' && document.querySelectorAll('article.lesson').length===1")
    result['checks'].append('Exit during pending3D, clean remount at1 after native delayed callbacks; explicit Exit returns React library and retains category filter')
    result['completed']=True
finally:
    result['javascriptErrors']=js_errors
    (folder/'lifecycle.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    call('session.end',{});s.close()
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
assert result['completed'] and not js_errors
