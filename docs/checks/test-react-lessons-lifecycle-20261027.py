"""Real cross-lesson/session/rules/Auto/3D-failure checks, Firefox9238. Only /tmp writes."""
from pathlib import Path
exec(compile(Path('docs/checks/test-react-lesson-lifecycle-20261027.py').read_text().split('\ntry:\n',1)[0], 'reviewed-lifecycle-harness', 'exec'))
folder=Path('/tmp/namelecule-react-lessons-20261027')
content=json.loads(Path('react-preview/src/content.json').read_text())
entries=[s for c in content['library']['categories'] for s in c['lessons']]
by_id={s['id']:s for s in entries}
result={'completed':False,'checks':[],'crossLesson':[],'manualRules':[]}
def go(ident,n):
    target='#/lesson/'+ident+'/step/'+str(n)
    ev('location.hash='+json.dumps(target))
    wait("location.hash==="+json.dumps(target)+" && !!document.querySelector('.lesson-stage iframe:not([hidden])') && new URL(document.querySelector('iframe').src).searchParams.get('lesson')==="+json.dumps(ident)+" && document.getElementById('lesson-position').textContent==="+json.dumps(str(n)+'/'+str(by_id[ident]['steps'])))
    attach();assert ce('fScenarioPresent().index')==n-1
try:
    navigate('react-preview/dist/?v=lessons-life-'+str(time.time_ns())+'#/library')
    previous=None
    for entry in entries:
        ident=entry['id'];go(ident,2)
        session=ev("new URL(document.querySelector('iframe').src).searchParams.get('session')")
        assert session!=previous
        # Reject old-session and wrong-course messages even from the current host.
        ce("parent.postMessage({channel:'namelecule-lesson-v1',session:"+json.dumps(previous)+",lesson:"+json.dumps(ident)+",type:'failed'},location.origin)")
        ce("parent.postMessage({channel:'namelecule-lesson-v1',session:"+json.dumps(session)+",lesson:'unknown',type:'failed'},location.origin)")
        ev("window.dispatchEvent(new MessageEvent('message',{origin:location.origin,source:window,data:{channel:'namelecule-lesson-v1',session:"+json.dumps(session)+",lesson:"+json.dumps(ident)+",type:'failed'}}))")
        time.sleep(.1);assert ev("!document.querySelector('.lesson-status[role=alert]') && !document.querySelector('iframe').hidden")
        # Exercise one real optional table for every lesson that offers one.
        if ce("fScenarioShowComponentRule(nameAnalysisMode)"):
            assert ce("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
            ce("[...document.querySelectorAll('#ruleTheoryContainer .ruleTile')].find(e=>e.textContent.trim()).click()")
            assert ce("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'")
            go(ident,3);assert ce("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
            result['manualRules'].append(ident)
        # Course-specific bounds, then the next course remounts independently.
        ev('location.hash='+json.dumps('#/lesson/'+ident+'/step/'+str(entry['steps']+1)))
        wait("!!document.querySelector('.lesson-preview [role=alert]') && !document.querySelector('iframe')")
        result['crossLesson'].append(ident);previous=session
    for route in ['#/lesson/constructor/step/1','#/lesson/__proto__/step/1','#/lesson/%61lkanes/step/1','#/lesson/alkanes/step/01','#/lesson/alkanes/step/1e1','#/lesson/alkanes/step/0','#/lesson/alkanes/step/-1','#/lesson/alkanes/step/1/extra']:
        ev('location.hash='+json.dumps(route));wait("!!document.querySelector('.lesson-preview [role=alert]') && !document.querySelector('iframe')")
    result['checks'].append('12cross-course sessions remount independently; stale/wrong-course/wrong-source messages rejected; all12upper bounds and malformed/prototype/encoded routes rejected; optional tables open manually and close on next')
    # Ether common/IUPAC state and authored alkoxy table, without a second naming engine.
    go('monoethers',2);assert ce("etherNamingMode==='common' && nameAnalysisMode==='commonAlkyl2'")
    go('monoethers',5)
    assert ce("etherNamingMode==='iupac' && fScenarioShowAlkoxyRule() && nameAnalysisMode==='compSecondSub1'")
    assert ce("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
    ce("[...document.querySelectorAll('#ruleTheoryContainer .ruleTile')].find(e=>e.textContent.toLowerCase().includes('αλκοξ')).click()")
    assert ce("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'")
    result['alkoxyTable']=ce("document.getElementById('ruleContainer').textContent")
    assert 'μεθοξ' in result['alkoxyTable'].lower() and 'αιθοξ' in result['alkoxyTable'].lower()
    go('monoethers',6);assert ce("[...document.querySelectorAll('#ruleContainer,#alkoxyRuleContainer')].every(e=>getComputedStyle(e).display==='none')")
    go('monoethers',7);assert ce("!fScenarioShowAlkoxyRule() && [...document.querySelectorAll('#ruleContainer,#alkoxyRuleContainer')].every(e=>getComputedStyle(e).display==='none')")
    # Direct course history/reload must retain the actual requested course and step.
    go('other-alcohols',4);go('other-ketones',5)
    ev('history.back()');wait("location.hash==='#/lesson/other-alcohols/step/4'");go('other-alcohols',4)
    ev('history.forward()');wait("location.hash==='#/lesson/other-ketones/step/5'");go('other-ketones',5)
    call('browsingContext.reload',{'context':ctx,'wait':'complete'});go('other-ketones',5)
    result['checks'].append('Ether common→IUPAC with manual authored alkoxy table; next closes table; cross-course Back/Forward/reload retain course/step')
    # Auto: viewport budget stays independent of native content and supports
    # height-only resizing, malformed viewport packets, and internal scroll reset.
    go('alkenes',21)
    heights=[]
    for height in [1000,700,1100]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':height},'devicePixelRatio':1})
        wait('document.querySelector("iframe").clientHeight==='+str(height));time.sleep(.25)
        heights.append(ce('innerHeight'))
    assert heights==[1000,700,1100]
    session=ev("new URL(document.querySelector('iframe').src).searchParams.get('session')")
    for value in [0,12001,'700',None]:
        packet={'channel':'namelecule-lesson-v1','session':session,'lesson':'alkenes','command':'viewport','height':value}
        ev("document.querySelector('iframe').contentWindow.postMessage("+json.dumps(packet)+',location.origin)')
    time.sleep(.15);assert ce('innerHeight')==1100
    ce('scrollTo(0,500)');go('alkenes',20);assert ce('scrollY')==0
    go('alkenes',22)
    assert ce('viewerMaxH===null && viewerBothH===null') and ce('innerHeight')==1100
    result['autoViewportHeights']=heights
    result['checks'].append('Authored Auto retained; height-only1000→700→1100resize without feedback; invalid viewport commands rejected; next step resets internal scroll')
    # Actual wrong3Dmodel deadline in an added lesson; then retry must remain
    # in that lesson, and an old pending session cannot corrupt a new lesson.
    go('other-ketones',27)
    ce("window.__nativeProperty=Jmol.getPropertyAsArray;Jmol.getPropertyAsArray=function(a,p,...args){let v=__nativeProperty.call(this,a,p,...args);return p==='modelInfo'?{...v,models:(v.models||[]).map(m=>({...m,file:'wrong-model.sdf'}))}:v}")
    started=time.monotonic();ev("document.getElementById('lesson-next').click()")
    wait("!!document.querySelector('.lesson-status[role=alert]')",22)
    result['wrongModelTimeoutSeconds']=round(time.monotonic()-started,2)
    assert 14.5<=result['wrongModelTimeoutSeconds']<=17.5
    assert ev("document.querySelector('iframe').hidden && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'")
    assert 'other-ketones-nomenclature.scenario.json' in ev("document.querySelector('.lesson-status a').href")
    ev("document.querySelector('.lesson-status button').click()");go('other-ketones',28)
    go('other-ketones',27)
    ev("location.hash='#/lesson/other-ketones/step/28';setTimeout(()=>{location.hash='#/lesson/monoethers/step/1'},0)")
    go('monoethers',1);time.sleep(2.2)
    assert ce("fScenarioPresent().index===0 && selectedMol==='dimethylether' && etherNamingMode==='common'")
    ev("document.querySelector('.lesson-navigation a').click()");wait("location.hash==='#/library' && !document.querySelector('iframe')")
    result['checks'].append('Actual15swrong-model gate in otherketones; retry retains course28; pending3D→differentlesson isolates late callbacks; Exit returns React library')
    result['completed']=True
finally:
    result['javascriptErrors']=js_errors
    control=json.loads(Path('docs/checks/v52-jsmol-lifecycle-control-20261027.json').read_text())
    known={v.replace("\\'", "'") for v in set(control['versions']['51']['signatures'])|set(control['fullLessonRun']['signatures'])}
    def known_teardown(error):
        frames=error.get('stackTrace',{}).get('callFrames',[])
        return error.get('text') in known and bool(frames) and all(f.get('url','').startswith('https://chemapps.stolaf.edu/jmol/jsmol/') for f in frames)
    result['knownJSmolTeardownErrors']=[e for e in js_errors if known_teardown(e)]
    result['unexpectedJavascriptErrors']=[e for e in js_errors if not known_teardown(e)]
    (folder/'lifecycle.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    call('session.end',{});s.close()
    print(json.dumps({'completed':result['completed'],'crossLesson':result['crossLesson'],'manualRules':result['manualRules'],'checks':result['checks'],'knownJSmolTeardownErrors':len(result['knownJSmolTeardownErrors']),'unexpectedJavascriptErrors':result['unexpectedJavascriptErrors']},ensure_ascii=False,indent=2),flush=True)
assert result['completed'] and not result['unexpectedJavascriptErrors']
