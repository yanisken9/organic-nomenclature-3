"""Manually select expanded mode in each lesson's optional final 2D/3D step."""
from pathlib import Path
exec(compile(Path('docs/checks/carbonyl-acid-uniform-20261101/browser_support.py').read_text(),'support','exec'))
base=json.loads((HERE/'baseline.json').read_text());out={'cases':[],'models':[],'completed':False}
try:
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
        for name,count in base['lessons'].items():
            lesson='scenarios/'+name+'-nomenclature.scenario.json'
            steps=json.loads((ROOT/lesson).read_text())['steps'];last=steps[-1]
            start('mulermoc-nom-52.html?scenario='+lesson+'&present=1&from=theory-library&audit=expanded-lesson#step='+str(count))
            until('!!fScenarioPresent()&&fScenarioPresent().index==='+str(count-1)+'&&!document.documentElement.classList.contains("lesson-loading")')
            until('selectedMol==='+json.dumps(last['selectedMol']))
            ev('document.getElementById("rotatePromptDismiss")?.click();true')
            ev('document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true');until('mode2D==="expanded"')
            until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",seconds=20)
            row=audit(width,'manual-expanded-in-lesson');row['lesson']=name
            assert ev('!!molSvg.node.dataset.alkaneFixedCCScale');out['cases'].append(row)
            until('mainChainPool3DKey===selectedMol')
            until('(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()')
            out['models'].append({'lesson':name,'width':width,'actualModelURLMatched':True})
            if width==1500 and name=='saturated-monocarboxylic-acids':screenshot(HERE/'expanded-acid-in-lesson.png')
            ev('document.getElementById("scPrev").click();true');until('fScenarioPresent().index==='+str(count-2))
            ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index==='+str(count-1)+'&&mode2D==='+json.dumps(last['mode2D']))
            row=audit(width,'authored-mode-restored');row['lesson']=name;out['cases'].append(row)
            print('expanded lesson',width,name,'passed',flush=True)
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
finally:save_result(out,'expanded-lessons.json.gz')
if not out['completed']or js_errors:raise SystemExit(1)
