"""Bounded author Exit input diagnostic after two missing-click observations.

Open step12 directly from author UI; capture input at window before application
listeners. Use only trusted pointer/Escape input, never invoke the handler.
"""
from pathlib import Path
import os,textwrap
os.environ.setdefault('NAMELECULE_V57_GAME','author')
os.environ.setdefault('NAMELECULE_V57_RUN','author-exit-run1')
driver=Path(__file__).with_name('replay.py').read_text()
prefix,start=driver.split('\ntry:\n server=',1)
exec(compile(prefix,'author-exit-frozen-replay-helpers','exec'))
OUT['scope']='Targeted input routing diagnostic: direct author step12, window-capture events, trusted Exit click and conditional trusted Escape, then normal learner Play/gating. Previous author runs already traversed5→12 and verified no earned receipt.'
def state():
 return read('({url:location.href,present:MuLERMoCScenario.present,preview:fScenarioIsAuthorPreview(fScenarioPresent()),authoring:MuLERMoCScenario.authoring,index:fScenarioPresent().index,focus:document.hasFocus(),visibility:document.visibilityState,active:document.activeElement?.id,rect:document.getElementById("scExit")?.getBoundingClientRect().toJSON(),inner:[innerWidth,innerHeight],outer:[outerWidth,outerHeight],screen:[screenX,screenY],events:window.__exitProbeEvents??[]})')
try:
 startup=' server='+start.split(" if GAME=='author':",1)[0]
 exec(compile(textwrap.dedent(startup),'author-exit-owned-startup','exec'))
 call('script.addPreloadScript',{'functionDeclaration':'''() => {window.__exitProbeEvents=[];for(const type of ['pointermove','pointerdown','pointerup','mousedown','mouseup','click','keydown'])window.addEventListener(type,e=>window.__exitProbeEvents.push({type,trusted:e.isTrusted,key:e.key??null,target:e.target?.id||e.target?.className,tag:e.target?.tagName,x:e.clientX,y:e.clientY,defaultPrevented:e.defaultPrevented,path:e.composedPath().slice(0,5).map(n=>n.id||n.tagName||n.nodeName||'window')}),true)}'''})
 page('mulermoc-nom-57.html?scenario=scenarios/alkanes-user-3.scenario.json#step=1');ready()
 wait('document.readyState==="complete"&&MuLERMoCScenario.ready===true');pause(1)
 call('browsingContext.activate',{'context':ctx});click('#scenarioAuthorTab');wait('MuLERMoCScenario.authoring',8)
 click('.scenarioPanel.active .scList');wait('!!document.querySelector(".scenarioPanel.active .scenarioDrawer.open")')
 click('.scenarioPanel.active .srow[data-idx="11"] .scPresentStep')
 wait('MuLERMoCScenario.present&&fScenarioPresent().index===11&&fScenarioIsAuthorPreview(fScenarioPresent())&&!MuLERMoCScenario.checkpointPreparation')
 check(True,'Direct author UI opens actual step12 rehearsal')
 check(rec() is None,'Targeted author rehearsal still creates no learner receipt')
 OUT['beforeExit']=state();ev('window.__exitProbeEvents=[];true')
 click('#scExit');pause(.5);OUT['afterExitClick']=state()
 OUT['exitClickVerified']=not OUT['afterExitClick']['present'] and not OUT['afterExitClick']['preview']
 print(json.dumps({'phase':'afterExitClick','exitClickVerified':OUT['exitClickVerified'],'state':OUT['afterExitClick']},ensure_ascii=False),flush=True)
 if not OUT['exitClickVerified']:
  call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'v57-author-exit-key','actions':[{'type':'keyDown','value':'\ue00c'},{'type':'keyUp','value':'\ue00c'}]}]})
  pause(.5);OUT['afterEscape']=state()
  print(json.dumps({'phase':'afterEscape','state':OUT['afterEscape']},ensure_ascii=False),flush=True)
 wait('!MuLERMoCScenario.present&&!fScenarioIsAuthorPreview(fScenarioPresent())',10)
 check(ev('MuLERMoCScenario.authoring'),'Trusted Exit input returns to authoring')
 OUT['exitMethod']='pointer' if OUT['exitClickVerified'] else 'Escape';shot('author-after-exit')
 click('.scenarioPanel.active .scPresent');wait('MuLERMoCScenario.present&&!MuLERMoCScenario.checkpointPreparation&&fScenarioPresent().index===0')
 check(not ev('fScenarioIsAuthorPreview(fScenarioPresent())'),'Normal card Play ends transient author bypass')
 ev('location.hash="step=5";true');wait('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation')
 check(ev('document.getElementById("scNext").disabled'),'Normal learner Play still requires unsolved gate4 after exit')
 r=rec();check(r is None or not r.get('states',{}).get('3',{}).get('solved',False),'Author preview and Exit never earn learner unlock')
 OUT['finalState']=state();shot('learner-gate-after-author-exit');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']=state();shot('failure')
 except Exception as error:OUT['failureCaptureError']=repr(error)
finally:
 cleanup=driver.rsplit("\nfinally:\n OUT['javascriptErrors']",1)[1].split("\nif not OUT.get('completed')",1)[0]
 exec(compile(textwrap.dedent(" OUT['javascriptErrors']"+cleanup),'author-exit-owned-cleanup','exec'))
if not OUT.get('completed'):raise SystemExit(1)
