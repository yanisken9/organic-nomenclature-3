"""Existing 27-step ether lesson, actual next/previous/replay/exit, two widths."""
from pathlib import Path
exec(compile(Path('docs/checks/ether-uniform-20261031/browser_support.py').read_text(),'support','exec'))
lesson='scenarios/saturated-monoethers-nomenclature.scenario.json';steps=json.loads((ROOT/lesson).read_text())['steps']
out={'cases':[],'completed':False,'scenarioModified':False,'exits':[]}
def capture(width,index,phase):
    step=steps[index]
    until('selectedMol==='+json.dumps(step['selectedMol'])+'&&mode2D==='+json.dumps(step['mode2D']))
    until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
    assert ev('etherNamingMode')==step['etherNamingMode']
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    row=audit(width,phase);row['step']=index+1
    if step['mode2D']=='expanded':assert ev('!!molSvg.node.dataset.alkaneFixedCCScale')
    out['cases'].append(row)
try:
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        start('mulermoc-nom-52.html?scenario='+lesson+'&present=1&from=theory-library&audit=ether-lesson')
        until('typeof fScenarioPresent==="function"&&!!fScenarioPresent()&&!document.documentElement.classList.contains("lesson-loading")')
        for index in range(len(steps)):
            if index:
                ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index))
            capture(width,index,'forward')
            if index and(steps[index]['mode2D']=='expanded'or index==len(steps)-1):
                ev('document.getElementById("scPrev").click();true');until('fScenarioPresent().index==='+str(index-1));capture(width,index-1,'backward')
                ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(index));capture(width,index,'replay')
        until('mainChainPool3DKey===selectedMol');out.setdefault('terminal3DModels',[]).append({'width':width,'key':ev('selectedMol'),'atoms':ev('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))')})
        if width==1500:screenshot(HERE/'lesson-final.png')
        ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("/namelecule/design/theory-library.html")');out['exits'].append(width)
        print('lesson',width,'passed',flush=True)
    out['completed']=True
except Exception as e:out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'lesson.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
