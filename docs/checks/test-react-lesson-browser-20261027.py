"""Actual Firefox alkane-pilot/native parity and lifecycle checks. Artifacts only /tmp.
Requires the repository on localhost8013 and the existing Firefox BiDi9237.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\nimport hashlib', 1)[0], 'existing-bidi-harness', 'exec'))
import hashlib, gzip, re
folder = Path('/tmp/namelecule-react-lesson-20261027')
folder.mkdir(exist_ok=True)
result = {'completed': False, 'checks': [], 'steps': [], 'parity': []}
source = json.loads(Path('scenarios/alkanes-nomenclature-branches.scenario.json').read_text())
child = None
captures = {}

def ce(expr):
    r = call('script.evaluate', {'expression': expr, 'target': {'context': child}, 'awaitPromise': True})
    if r.get('type') == 'exception': raise RuntimeError(r.get('exceptionDetails'))
    return r['result'].get('value')

def wait(evaluate, expr, seconds=22):
    for _ in range(int(seconds * 10)):
        if evaluate(expr): return
        time.sleep(.1)
    raise AssertionError('Timed out: ' + expr)

def ready(n=None):
    wait(ev, "!!document.querySelector('.lesson-stage iframe:not([hidden])') && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'", 95)
    if n is not None:
        attach()
        assert ev("document.getElementById('lesson-position').textContent") == str(n) + '/21'
        assert ce('fScenarioPresent().index') == n-1

def attach():
    global child
    child = call('browsingContext.getTree', {'root': ctx})['contexts'][0]['children'][0]['context']

def move(n):
    ev('location.hash=' + json.dumps('#/lesson/alkanes/step/' + str(n)))
    wait(ev, "document.getElementById('lesson-position')?.textContent===" + json.dumps(str(n) + '/21'))
    ready(n)

def drain(evaluate):
    wait(evaluate, "!numberingFlag || nameAnalysisMode==='none' || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length", 25)
    if evaluate("getComputedStyle(document.getElementById('nomeclature3D')).display!=='none'"):
        token = int(time.time_ns() % 1000000000)
        evaluate('Jmol.script(jmolAppletNomeclature,"lessonTestMarker = ' + str(token) + ';")')
        wait(evaluate, "+Jmol.evaluateVar(jmolAppletNomeclature,'lessonTestMarker')===" + str(token))
    # Let native ResizeObserver/iframe-height fitting settle before comparing
    # SVG coordinates, which depend on the actual applet viewport.
    time.sleep(.2)

signature = r"""JSON.stringify((()=>{
 const plain=e=>e?.textContent.replace(/\s+/g,' ').trim()||'';
 const svg=document.querySelector('#jsmeNomeclatureSVG svg');
 return {step:fScenarioPresent().index+1,title:document.getElementById('pageTitle').textContent,note:plain(document.getElementById('scStepText')),
 molecule:selectedMol,mode:mode2D,analysis:nameAnalysisMode,name:currentMolName,chain:mainChainAtomsList,hidden:nameHiddenComps,
 components:[...document.querySelectorAll('#nameAnalysis .nameCompBox')].map(e=>({id:e.id,label:e.textContent,selected:e.classList.contains('selected'),hidden:e.classList.contains('comp-hidden')})),
 explanation:plain(document.querySelector('#nameAnalysisExplain .explainText')),
 rules:[...document.querySelectorAll('#ruleTheoryContainer > .ruleTheory')].map(e=>({title:plain(e.querySelector('.ruleTile')),text:plain(e.querySelector('.ruleText')),table:plain(e.querySelector('.ruleTable'))})),
 show:Object.fromEntries(['menuCol','jsmeNomeclatureDIV','nomeclature3D','ruleContainer','radio2DMode','controls3D'].map(id=>[id,getComputedStyle(document.getElementById(id)).display!=='none'])),
 svg:svg?{viewBox:svg.getAttribute('viewBox'),nodes:[...svg.querySelectorAll('line,text,tspan,path,polygon,rect')].filter(e=>!e.closest('defs')).map(e=>({tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>!['id','class'].includes(a.name)).map(a=>[a.name,a.value])),text:['text','tspan'].includes(e.tagName)?e.textContent:null}))}:null};
})())"""

def scene(evaluate):
    return json.loads(evaluate("JSON.stringify({file:(Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models||[])[0]?.file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo','all').map(a=>({n:a.atomno,s:a.sym,x:a.x,y:a.y,z:a.z,color:a.color,visible:a.visible})),bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,'bondInfo','all').map(b=>({a:b.atom1.atomno,b:b.atom2.atomno,order:b.order,visible:b.visible})),chain:mainChainAtoms3D})"))

def key(value, context=None):
    call('input.performActions', {'context': context or ctx, 'actions': [{'type': 'key', 'id': 'keyboard', 'actions': [{'type': 'keyDown', 'value': value}, {'type': 'keyUp', 'value': value}]}]})

try:
    navigate('react-preview/dist/?v=lesson-test-' + str(time.time_ns()) + '#/library')
    assert ev("document.querySelectorAll('a[href=\"#/lesson/alkanes/step/1\"]').length===1")
    legacy = json.loads(ev("JSON.stringify([...document.querySelectorAll('a.action')].map(a=>a.getAttribute('href')).filter(h=>!h.startsWith('#')))"))
    assert len(legacy) == 11 and all('mulermoc-nom-52.html?scenario=' in href for href in legacy)
    ev("document.getElementById('lesson-search').value='αλκάνια';document.getElementById('lesson-search').dispatchEvent(new Event('input',{bubbles:true}))")
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    ready(1); attach()
    frame_size = json.loads(ev("JSON.stringify({width:Math.round(document.querySelector('iframe').clientWidth),height:Math.round(document.querySelector('iframe').clientHeight)})"))
    result['frameWidth'] = frame_size['width']
    for n, st in enumerate(source['steps'], 1):
        if n > 1:
            ev("document.getElementById('lesson-next').click()")
            wait(ev, "document.getElementById('lesson-position').textContent===" + json.dumps(str(n) + '/21'))
            ready(n)
        drain(ce)
        actual = json.loads(ce(signature)); captures[n] = actual
        assert actual['molecule'] == st['selectedMol'] and actual['analysis'] == st['nameAnalysisMode']
        assert ce('JSON.stringify(fScenarioPresent().steps[' + str(n-1) + '].note)') == json.dumps(st['note'], ensure_ascii=False, separators=(',', ':'))
        assert actual['hidden'] == st['styleName']['hidden']
        assert actual['show']['nomeclature3D'] == st['show']['viewers']['3D']
        if ce('fScenarioShowComponentRule(nameAnalysisMode)'):
            assert not actual['show']['ruleContainer'], 'Rule opened on entry'
        size = json.loads(ce("JSON.stringify({width:innerWidth,height:innerHeight,viewerHeight:document.getElementById('jsmeNomeclatureSVG').clientHeight})"))
        result['steps'].append({'step': n, 'title': st['title'], 'molecule': actual['molecule'], 'name': actual['name'], 'viewport': size})
        if n in [1, 12, 21]: screenshot(str(folder / ('desktop-step-' + str(n) + '.png')))
    result['scene3D'] = scene(ce)
    assert result['scene3D']['file'].endswith('/ethyl_3_dimethyl_2_5_hexane_3D.sdf')
    assert ev("document.getElementById('lesson-next').disabled")
    result['checks'].append('All21steps through real Next, source notes/hidden components/highlights/modes/rules/3D; terminal Next disabled')
    for n in range(20, 0, -1):
        ev("document.getElementById('lesson-prev').click()")
        wait(ev, "document.getElementById('lesson-position').textContent===" + json.dumps(str(n) + '/21'))
        ready(n)
    assert ev("document.getElementById('lesson-prev').disabled")
    result['checks'].append('All20reverse transitions and first Previous disabled')
    move(2)
    assert ce("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
    ce("document.querySelector('#ruleTheoryContainer .ruleTile').click()")
    wait(ce, "getComputedStyle(document.getElementById('ruleContainer')).display!=='none'")
    move(3)
    assert ce("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
    # Real keyboard input in each browsing context; native key handler must not
    # double-advance and iframe Escape must return to the React library.
    ev("document.getElementById('lesson-next').focus()")
    key('\ue007'); wait(ev, "location.hash.endsWith('/4')"); ready(4)
    ce('document.body.tabIndex=-1;document.body.focus()')
    key('\ue014', child); wait(ev, "location.hash.endsWith('/5')"); ready(5)
    ce("document.querySelectorAll('.mode2DOption')[1].click()")
    wait(ce, "mode2D==='expanded'")
    ce("document.querySelectorAll('.mode2DOption')[2].click()")
    wait(ce, "mode2D==='skeletal'")
    # Malformed route cannot start a player; restore a valid deep link.
    for route in ['#/lesson/alkanes/step/0', '#/lesson/alkanes/step/22', '#/lesson/alkanes/step/1x', '#/lesson/unknown/step/1']:
        ev('location.hash=' + json.dumps(route)); wait(ev, "!!document.querySelector('.lesson-preview [role=alert]')")
        assert ev("!document.querySelector('.lesson-stage iframe')")
    move(12); attach(); ready(12)
    call('browsingContext.reload', {'context': ctx, 'wait': 'complete'})
    ready(12); attach()
    move(13); move(14)
    ev('history.back()'); wait(ev, "location.hash.endsWith('/13')"); ready(13)
    ev('history.forward()'); wait(ev, "location.hash.endsWith('/14')"); ready(14)
    # Two route changes around an in-flight apply converge on the latest route.
    ev("location.hash='#/lesson/alkanes/step/15';setTimeout(()=>{location.hash='#/lesson/alkanes/step/17'},0)")
    wait(ev, "location.hash.endsWith('/17')"); ready(17)
    result['checks'].append('Optional rule opens manually/recloses on next; keyboard Enter/child ArrowRight; native form controls; invalid route rejection; reload/deep-link/history/rapid route convergence')
    # Invalid host command packets do not advance the step.
    session = ev("new URL(document.querySelector('iframe').src).searchParams.get('session')")
    for patch in [{'step': 0}, {'step': 22}, {'step': '1'}, {'id': -1}, {'session': 'stale'}, {'lesson': 'alkenes'}, {'command': 'export'}]:
        packet = {'channel': 'namelecule-lesson-v1', 'session': session, 'lesson': 'alkanes', 'command': 'step', 'step': 1, 'id': 100000, **patch}
        ev("document.querySelector('iframe').contentWindow.postMessage(" + json.dumps(packet) + ',location.origin)')
    time.sleep(.3); assert ce('fScenarioPresent().index') == 16
    # Spoofed parent packets, stale sessions and invalid heights leave UI intact.
    ev("window.dispatchEvent(new MessageEvent('message',{origin:location.origin,source:window,data:{channel:'namelecule-lesson-v1',session:" + json.dumps(session) + ",lesson:'alkanes',type:'failed'}}))")
    ce("parent.postMessage({channel:'namelecule-lesson-v1',session:'old',lesson:'alkanes',type:'failed'},location.origin)")
    ce("parent.postMessage({channel:'namelecule-lesson-v1',session:" + json.dumps(session) + ",lesson:'alkanes',type:'height',height:999999},location.origin)")
    time.sleep(.2); ready(17)
    # Native failure hook: no false-ready frame, retry reloads the same step.
    ce('window.fLessonLoadingDone(true)')
    wait(ev, "!!document.querySelector('.lesson-status[role=alert]')")
    assert ev("document.querySelector('.lesson-stage iframe').hidden && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'")
    ev("document.querySelector('.lesson-status button').click()")
    ready(17); attach()
    result['checks'].append('Invalid/stale/wrong-source host/parent packets rejected; native controlled failure hook hides content, aria-busy clears, retry retains step')
    # Mobile and final exploration menu, actual3D model, iframe Escape/remount.
    call('browsingContext.setViewport', {'context': ctx, 'viewport': {'width': 390, 'height': 844}, 'devicePixelRatio': 1})
    move(21); ready(21); drain(ce)
    time.sleep(.5)
    result['mobile'] = json.loads(ev("JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.querySelector('iframe').clientHeight})"))
    result['mobileChild'] = json.loads(ce("JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight})"))
    assert result['mobile']['scroll'] <= 390
    screenshot(str(folder / 'mobile-step-21.png'))
    ce("document.getElementById('butane').click()")
    wait(ce, "selectedMol==='butane' && (Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models||[])[0]?.file.endsWith('/butane_3D.sdf')", 25)
    assert ev("document.getElementById('lesson-position').textContent==='21/21'")
    ce('document.body.focus()')
    try:
        key('\ue00c', child)
    except RuntimeError as error:
        # Escape intentionally destroys its target frame on keyDown, before
        # BiDi can dispatch keyUp in that same discarded context.
        assert 'DiscardedBrowsingContextError' in str(error) and ev("location.hash==='#/library'")
    wait(ev, "location.hash==='#/library'")
    assert ev("!document.querySelector('iframe')")
    ev("document.querySelector('a[href=\"#/lesson/alkanes/step/1\"]').click()")
    ready(1); attach()
    # Unmount during a new apply must not corrupt the library or re-enter it.
    ev("document.getElementById('lesson-next').click();location.hash='#/library'")
    wait(ev, "location.hash==='#/library' && !document.querySelector('iframe')")
    time.sleep(.5)
    result['checks'].append('390px parent layout; final native menu selects butane with actual3D model; child Escape returns React library; clean remount; unmount while pending')
    # Native standalone parity: same viewport and only the host layout CSS.
    call('browsingContext.setViewport', {'context': ctx, 'viewport': {'width': frame_size['width'], 'height': 1000}, 'devicePixelRatio': 1})
    navigate('mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1#step=1')
    until("typeof fScenarioPresent==='function' && fScenarioPresent().steps.length===21 && !document.documentElement.classList.contains('lesson-loading')")
    css = re.search("css = '''(.*?)'''", Path('react-preview/tools/build-lesson-host.py').read_text(), re.S).group(1)
    ev("(()=>{let s=document.createElement('style');s.textContent=" + json.dumps(css) + ';document.head.appendChild(s)})()')
    for n in range(1, 22):
        size = result['steps'][n-1]['viewport']
        call('browsingContext.setViewport', {'context': ctx, 'viewport': {'width': size['width'], 'height': size['height']}, 'devicePixelRatio': 1})
        ev('fScenarioGo(' + str(n-1) + ');fResizeViewers()'); drain(ev)
        actual = json.loads(ev(signature))
        if actual != captures[n]:
            differences = [k for k in actual if actual[k] != captures[n][k]]
            (folder / 'parity-difference.json').write_text(json.dumps({'step': n, 'expected': captures[n], 'actual': actual}, ensure_ascii=False, indent=2))
            raise AssertionError(('Native parity', n, differences))
        result['parity'].append({'step': n, 'identical': True})
    assert scene(ev) == result['scene3D']
    result['checks'].append('21/21 native main state/text/rule/name/hidden/highlight/numbering/SVG parity at equal viewport and host layout CSS; final actual3D atoms/bonds/main chain identical')
    result['completed'] = True
finally:
    result['javascriptErrors'] = js_errors
    # Keep every raw event. Derive known signatures from the existing actual
    # v51/v52 control, rather than broadening a whitelist to fit this run.
    # The historical summary escaped apostrophes literally; normalize them.
    control = json.loads(Path('docs/checks/v52-jsmol-lifecycle-control-20261027.json').read_text())
    signatures = set(control['versions']['51']['signatures']) | set(control['fullLessonRun']['signatures'])
    signatures = {value.replace("\\'", "'") for value in signatures}
    def known_teardown(error):
        frames = error.get('stackTrace', {}).get('callFrames', [])
        return error.get('text') in signatures and bool(frames) and all(f.get('url', '').startswith('https://chemapps.stolaf.edu/jmol/jsmol/') for f in frames)
    result['knownJSmolTeardownErrors'] = [e for e in js_errors if known_teardown(e)]
    result['unexpectedJavascriptErrors'] = [e for e in js_errors if not known_teardown(e)]
    (folder / 'browser.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with gzip.open(folder / 'capture.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(captures, f, ensure_ascii=False)
    call('session.end', {}); s.close()
    print(json.dumps({'completed': result['completed'], 'steps': len(result['steps']), 'parity': len(result['parity']), 'javascriptErrors': len(js_errors), 'checks': result['checks']}, ensure_ascii=False, indent=2), flush=True)
assert result['completed'] and not result['unexpectedJavascriptErrors']
