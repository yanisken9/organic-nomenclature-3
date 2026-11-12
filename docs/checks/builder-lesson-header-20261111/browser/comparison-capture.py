"""Matched 1500×1000 actual page captures for the user's visual comparison."""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
RESULT={'captures':[], 'baselineOrigin':'http://127.0.0.1:57422/','currentOrigin':PROCESS['baseURL']}
try:
 viewport(1500,1000)
 call('browsingContext.navigate',{'context':ctx,'url':RESULT['baselineOrigin']+'mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&headerProbe=visual-before-20261111-r1#step=4','wait':'none'});ready();open_gate();choose('builder');pause(.7)
 before=read('({font:getComputedStyle(document.querySelector(".nl-builder-heading")).fontSize,textAlign:getComputedStyle(document.querySelector(".nl-builder-heading")).textAlign,logoCount:document.querySelectorAll(".nl-builder-logo").length})')
 check(before['font']=='24px' and before['logoCount']==0,'True frozen before header visible for comparison',before)
 ev('document.getElementById("nlQuizDialog").scrollTop=0;true');pause(.3);shot('before-top-desktop.png');RESULT['captures'].append({'file':'before-top-desktop.png','header':before,'viewport':[1500,1000],'dialogScrollTop':ev('document.getElementById("nlQuizDialog").scrollTop')})
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&headerProbe=visual-workshop-20261111-r1#step=4');ready();open_gate();choose('repair');pause(.7)
 ev('document.getElementById("nlQuizDialog").scrollTop=0;true');pause(.3);shot('workshop-desktop.png');RESULT['captures'].append({'file':'workshop-desktop.png','viewport':[1500,1000],'dialogScrollTop':ev('document.getElementById("nlQuizDialog").scrollTop'),'headings':read('[...document.querySelectorAll("#nlQuizDialog h1,#nlQuizDialog h2")].map(e=>({text:e.textContent,font:getComputedStyle(e).fontSize,textAlign:getComputedStyle(e).textAlign}))')})
 RESULT['passed']=True
except Exception as e:
 RESULT['passed']=False;RESULT['failure']=repr(e);RESULT['traceback']=traceback.format_exc();shot('comparison-failure.png');raise
finally:
 RESULT['jsExceptions']=js_errors;(HERE/'comparison-captures.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+'\n');finish()
