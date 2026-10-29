"""Actual entry-history, parent keys and viewer roundtrip; Firefox9238."""
from pathlib import Path
exec(compile(Path('docs/checks/test-react-lesson-lifecycle-20261027.py').read_text().split('\ntry:\n',1)[0], 'existing-lesson-lifecycle-harness', 'exec'))
try:
    navigate('react-preview/dist/?v=lesson-routes-'+str(time.time_ns())+'#/library')
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')");attach()
    ev('history.back()')
    wait("location.hash==='#/library' && !document.querySelector('iframe')")
    ev('history.forward()')
    wait("location.hash==='#/lesson/alkanes/step/1' && !!document.querySelector('.lesson-stage iframe:not([hidden])')");attach()
    assert ce("fScenarioPresent().index===0 && selectedMol==='ethane'")
    # Parent-scope keyboard navigation, complementary to iframe keys.
    ev("document.getElementById('lesson-next').focus()")
    def key(value):
        call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
    key('\ue014')
    wait("location.hash.endsWith('/2') && !!document.querySelector('.lesson-stage iframe:not([hidden])')")
    key('\ue012')
    wait("location.hash.endsWith('/1') && !!document.querySelector('.lesson-stage iframe:not([hidden])')")
    key('\ue00c');wait("location.hash==='#/library' && !document.querySelector('iframe')")
    ev("location.hash='#/viewer'")
    wait("!!document.querySelector('.molecule-stage iframe:not([hidden])')");attach()
    assert ce("selectedMol==='ethanol' && document.documentElement.dataset.view==='2d'")
    ev("document.querySelector('.molecule-preview > a').click()")
    wait("location.hash==='#/library' && !document.querySelector('iframe')")
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    wait("!!document.querySelector('.lesson-stage iframe:not([hidden])')");attach()
    assert ce("fScenarioPresent().index===0 && selectedMol==='ethane'")
    result['checks'].append('Real entry Back returns React library, Forward remounts step1; parent ArrowRight/ArrowLeft/Escape; lesson→library→viewer→library→lesson isolates sessions')
    result['completed']=True
finally:
    result['javascriptErrors']=js_errors
    (folder/'routes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    call('session.end',{});s.close()
    print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['completed'] and not js_errors
