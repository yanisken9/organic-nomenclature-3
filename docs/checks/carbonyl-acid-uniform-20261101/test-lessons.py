"""Replay six existing Main lessons with actual next/back/replay/exit controls."""
from pathlib import Path
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
base=json.loads((HERE/'baseline.json').read_text())
out={'cases':[],'exits':[],'terminalModels':[],'completed':False,'scenarioModified':False}
def capture(width,index,phase,name,steps):
    step=steps[index]
    until('selectedMol==='+json.dumps(step['selectedMol'])+'&&mode2D==='+json.dumps(step['mode2D']))
    until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    assert ev('mainChainMode')==step['mainChainMode']
    assert ev('nameAnalysisMode')==step['nameAnalysisMode']
    assert abs(ev('molZoom2D')-step['style2D']['zoom'])<.001
    row=audit(width,phase);row.update(lesson=name,step=index+1)
    assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')==(step['mode2D']=='expanded')
    out['cases'].append(row)
try:
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        for name,count in base['lessons'].items():
            lesson='scenarios/'+name+'-nomenclature.scenario.json'
            steps=json.loads((ROOT/lesson).read_text())['steps'];assert len(steps)==count
            start('mulermoc-nom-52.html?scenario='+lesson+'&present=1&from=theory-library&audit=carbonyl-acid-lessons')
            until('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")')
            ev('document.getElementById("rotatePromptDismiss")?.click();true')
            for index in range(len(steps)):
                if index:
                    ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index))
                capture(width,index,'forward',name,steps)
                if index and(steps[index]['mode2D']=='expanded'or index==len(steps)-1):
                    ev('document.getElementById("scPrev").click();true');until('fScenarioPresent().index==='+str(index-1));capture(width,index-1,'backward',name,steps)
                    ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index));capture(width,index,'replay',name,steps)
            until('mainChainPool3DKey===selectedMol')
            until('(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()')
            out['terminalModels'].append({'lesson':name,'width':width,'key':ev('selectedMol'),'actualModelURLMatched':True})
            if width==1500:screenshot(HERE/(name+'-lesson-final.png'))
            ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("/design/theory-library.html")')
            out['exits'].append({'lesson':name,'width':width})
            print('lesson',width,name,count,'steps passed',flush=True)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'lessons.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
