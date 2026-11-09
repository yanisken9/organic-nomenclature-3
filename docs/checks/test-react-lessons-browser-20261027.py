"""All12React/native lessons,283steps. Reuses the reviewed BiDi/snapshot helpers.
--resume reuses only completed lesson checks with identical runtime fingerprints.
Writes actual browser evidence only under /tmp/namelecule-react-lessons-20261027.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-react-lesson-browser-20261027.py').read_text().split('\ntry:\n',1)[0], 'reviewed-lesson-harness', 'exec'))
folder = Path('/tmp/namelecule-react-lessons-20261027')
folder.mkdir(exist_ok=True)
catalog = json.loads(Path('react-preview/src/content.json').read_text())
entries = [{**s, 'heading': c['title'] + ' — ' + s['title']} for c in catalog['library']['categories'] for s in c['lessons']]
current = None
result = {'completed': False, 'lessons': [], 'cases': {}, 'parity': {}, 'scenes': {}, 'mobile': {}, 'checks': []}
captures = {}
# Ether steps can offer only the supplemental alkoxy container; the generic
# ruleContainer then does not exist. Keep the reviewed snapshot shape while
# treating absent optional DOM as hidden, not as a browser failure.
signature=signature.replace("getComputedStyle(document.getElementById(id)).display!=='none'",
    "((e)=>!!e && getComputedStyle(e).display!=='none')(document.getElementById(id))")
paths = ['react-preview/src/main.jsx','react-preview/src/LessonPreview.jsx','react-preview/src/content.json',
         'react-preview/src/preview.css','react-preview/public/lesson-host-bridge.js','react-preview/public/lesson-host.html',
         'mulermoc-nom-52.html','js/mulermoc-nom-core-52.js','js/mulermoc-nom-molview-52.js',
         'js/mulermoc-nom-scenario-52.js','js/mulermoc-nom-teaching-52.js','js/mulermoc-nom-note-52.js']
paths += [s['scenario'] for s in entries] + [str(p) for p in Path('react-preview/dist').rglob('*') if p.is_file()]
fingerprint = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
if '--resume' in sys.argv:
    saved = json.loads(gzip.decompress((folder/'capture.json.gz').read_bytes()))
    assert saved['runtimeSHA256'] == fingerprint, 'Runtime changed; full rerun required'
    captures = saved['captures']; result = saved['result']; js_errors[:] = result.get('javascriptErrors', [])
    result['resumed'] = True

def checkpoint():
    result['javascriptErrors'] = js_errors[:]
    with gzip.open(folder/'capture.json.gz','wt',encoding='utf-8') as f:
        json.dump({'runtimeSHA256': fingerprint, 'captures': captures, 'result': result}, f, ensure_ascii=False)
    (folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))

def ready(n):
    wait(ev,"!!document.querySelector('.lesson-stage iframe:not([hidden])') && document.querySelector('.lesson-stage').getAttribute('aria-busy')==='false'",95)
    attach()
    assert ev("document.getElementById('lesson-position').textContent") == str(n)+'/'+str(current['steps'])
    assert ce('fScenarioPresent().index') == n-1

def move(n):
    ev('location.hash='+json.dumps('#/lesson/'+current['id']+'/step/'+str(n)))
    wait(ev,"document.getElementById('lesson-position')?.textContent==="+json.dumps(str(n)+'/'+str(current['steps'])))
    ready(n)

def snap(evaluate):
    value=json.loads(evaluate(signature))
    value['naming']=evaluate('etherNamingMode')
    return value

try:
    assert len(entries)==12 and sum(s['steps'] for s in entries)==283
    for current in entries:
        ident=current['id']
        if ident in result['lessons']: continue
        source=json.loads(Path(current['scenario']).read_text())
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
        navigate('react-preview/dist/?v=lessons-'+str(time.time_ns())+'#/library')
        routes=json.loads(ev("JSON.stringify([...document.querySelectorAll('a.action')].map(a=>a.getAttribute('href')))"))
        assert routes==['#/lesson/'+entry['id']+'/step/1' for entry in entries]
        ev('document.querySelector(\'a[href="'+routes[entries.index(current)]+'"]\').click()')
        ready(1)
        normalized_steps=json.loads(ce('JSON.stringify(fScenarioPresent().steps)'))
        assert ev("document.querySelector('.lesson-preview h1').textContent")==current['heading']
        assert current['heading'] in ev('document.title') and current['heading'] in ev("document.querySelector('iframe').title")
        for n,st in enumerate(source['steps'],1):
            if n>1:
                ev("document.getElementById('lesson-next').click()")
                wait(ev,"document.getElementById('lesson-position').textContent==="+json.dumps(str(n)+'/'+str(current['steps'])))
                ready(n)
            drain(ce); value=snap(ce); token=ident+'/'+str(n); captures[token]=value
            assert value['molecule']==st['selectedMol'] and value['mode']==st['mode2D']
            assert value['analysis']==st['nameAnalysisMode'] and value['naming']==st['etherNamingMode']
            assert value['hidden']==st['styleName']['hidden']
            assert json.loads(ce('JSON.stringify(fScenarioPresent().steps['+str(n-1)+'].note)'))==st['note']
            assert value['show']['nomeclature3D']==st['show']['viewers']['3D']
            # Native52derives menu visibility from the validated subset and
            # intentionally ignores the legacy stored show.menu boolean.
            assert value['show']['menuCol']==normalized_steps[n-1]['show']['menu']
            assert not value['show']['ruleContainer'], 'Source optional rule unexpectedly open'
            assert ce("[...document.querySelectorAll('#ruleContainer,#alkoxyRuleContainer')].every(e=>getComputedStyle(e).display==='none')")
            size=json.loads(ce("JSON.stringify({width:innerWidth,height:innerHeight,viewerHeight:document.getElementById('jsmeNomeclatureSVG').clientHeight})"))
            result['cases'][token]={'molecule':value['molecule'],'mode':value['mode'],'naming':value['naming'],'viewport':size}
        result['scenes'][ident]=scene(ce)
        assert ev("document.getElementById('lesson-next').disabled")
        move(current['steps']-1);move(current['steps'])
        if ident in ['other-alcohols','monoethers','other-aldehydes','other-ketones']:
            screenshot(str(folder/(ident+'-desktop.png')))
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
        time.sleep(.6)
        p=json.loads(ev("JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth})"))
        c=json.loads(ce("JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight})"))
        assert p['scroll']<=p['width'] and c['scroll']<=c['width'], (ident,p,c)
        result['mobile'][ident]={'parent':p,'child':c}
        if ident in ['monoethers','other-ketones']:screenshot(str(folder/(ident+'-mobile.png')))
        # Controlled standalone layout parity, preserving all original code.
        navigate('mulermoc-nom-52.html?scenario='+current['scenario']+'&present=1#step=1')
        until("typeof fScenarioPresent==='function' && fScenarioPresent().steps.length==="+str(current['steps'])+" && !document.documentElement.classList.contains('lesson-loading')")
        css=re.search("css = '''(.*?)'''",Path('react-preview/tools/build-lesson-host.py').read_text(),re.S).group(1)
        ev("(()=>{let s=document.createElement('style');s.textContent="+json.dumps(css)+';document.head.appendChild(s)})()')
        for n in range(1,current['steps']+1):
            token=ident+'/'+str(n);size=result['cases'][token]['viewport']
            call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':size['width'],'height':size['height']},'devicePixelRatio':1})
            ev('fScenarioGo('+str(n-1)+');fResizeViewers()');drain(ev)
            actual=snap(ev)
            if actual!=captures[token]:
                diff=[k for k in actual if actual[k]!=captures[token][k]]
                (folder/'parity-difference.json').write_text(json.dumps({'case':token,'keys':diff,'expected':captures[token],'actual':actual},ensure_ascii=False,indent=2))
                raise AssertionError(('Native parity',token,diff))
            result['parity'][token]=True
        assert scene(ev)==result['scenes'][ident], ('Actual3D parity',ident)
        result['lessons'].append(ident);checkpoint()
        print('Lesson verified',ident,current['steps'],'steps; total',len(result['parity']),flush=True)
    assert len(result['cases'])==len(result['parity'])==283
    result['checks'].append('12actual React library actions;283forward steps/native state+text+name+visibility+rules+highlight+numbering+SVG parity at matched viewport;12actual3D scenes;reverse boundaries;12mobile layouts')
    result['completed']=True
finally:
    control=json.loads(Path('docs/checks/v52-jsmol-lifecycle-control-20261027.json').read_text())
    known={v.replace("\\'", "'") for v in set(control['versions']['51']['signatures'])|set(control['fullLessonRun']['signatures'])}
    def known_teardown(error):
        frames=error.get('stackTrace',{}).get('callFrames',[])
        return error.get('text') in known and bool(frames) and all(f.get('url','').startswith('https://chemapps.stolaf.edu/jmol/jsmol/') for f in frames)
    result['knownJSmolTeardownErrors']=[e for e in js_errors if known_teardown(e)]
    result['unexpectedJavascriptErrors']=[e for e in js_errors if not known_teardown(e)]
    checkpoint()
    call('session.end',{});s.close()
    print(json.dumps({'completed':result['completed'],'lessons':len(result['lessons']),'steps':len(result['cases']),'parity':len(result['parity']),'knownJSmolTeardownErrors':len(result['knownJSmolTeardownErrors']),'unexpectedJavascriptErrors':result['unexpectedJavascriptErrors']},ensure_ascii=False,indent=2),flush=True)
assert result['completed'] and not result['unexpectedJavascriptErrors']
