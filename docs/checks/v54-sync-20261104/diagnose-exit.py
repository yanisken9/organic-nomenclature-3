from pathlib import Path
import json
exec(compile(Path('docs/checks/v54-sync-20261104/test-features.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library')
until('typeof fScenarioPresent==="function"&&MuLERMoCScenario.ready&&!!fScenarioPresent()&&fScenarioPresent().steps.length>0&&!document.documentElement.classList.contains("lesson-loading")')
p=json.loads(ev('JSON.stringify((()=>{let a=document.querySelector("#scExit"),b=a.getBoundingClientRect(),s=getComputedStyle(a);return {ready:MuLERMoCScenario.ready,disabled:a.disabled,outer:a.outerHTML,css:{pointer:s.pointerEvents,vis:s.visibility,display:s.display,z:s.zIndex},rect:{x:b.x,y:b.y,w:b.width,h:b.height},hit:document.elementFromPoint(b.x+b.width/2,b.y+b.height/2).outerHTML.slice(0,500),parent:a.parentNode.outerHTML.slice(-1000)}})())'))
print(json.dumps(p,ensure_ascii=False));(HERE/'exit-diagnostic.json').write_text(json.dumps(p,ensure_ascii=False,indent=2))
call('browsingContext.close',{'context':ctx});call('session.end',{})
