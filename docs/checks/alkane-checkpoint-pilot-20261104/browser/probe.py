from pathlib import Path
import os,json
os.environ['NAMELECULE_BIDI_PORT']='9244'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-name-repair-pilot.scenario.json&present=1#step=21')
app_ready();until('MuLERMoCScenario.present && fScenarioPresent().steps.length===21');until('!!document.querySelector("#nlQuizOpen")')
print(ev('JSON.stringify({index:fScenarioPresent().index,hash:location.hash,next:document.querySelector("#scNext").disabled,controls:[...document.querySelectorAll("[id^=sc]")].filter(n=>["BUTTON","SELECT"].includes(n.tagName)).map(n=>({id:n.id,text:n.textContent.slice(0,80)})),note:document.querySelector("#scStepText").textContent})'))
screenshot('docs/checks/alkane-checkpoint-pilot-20261104/browser/pilot-gate-desktop.png')
ev('document.querySelector("#nlQuizOpen").click();true');until('!!document.querySelector(".diagram-image.is-ready")')
print(ev('JSON.stringify({dialog:document.querySelector("#nlQuizDialog").open,parts:[...document.querySelectorAll(".part-button")].map(n=>({id:n.id,text:n.textContent})),choices:[...document.querySelectorAll(".choice-button")].map(n=>({id:n.id,text:n.textContent})),text:document.querySelector("#nlQuizDialog").innerText,scenario:fScenarioPresent().index})'))
screenshot('docs/checks/alkane-checkpoint-pilot-20261104/browser/pilot-mission-desktop.png')
call('browsingContext.close',{'context':ctx});call('session.end',{})
