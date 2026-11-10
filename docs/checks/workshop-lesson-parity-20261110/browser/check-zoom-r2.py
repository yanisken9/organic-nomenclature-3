from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
def button_state():return read('(()=>{let b=document.querySelector(".diagram-tools button");return{disabled:b.disabled,expanded:b.getAttribute("aria-expanded"),focus:document.activeElement===b,modal:!!document.querySelector(".zoom-dialog"),image:document.querySelector(".zoom-image")?.currentSrc}})()')
def cycle(label,escape=False):
 b=button_state();check(not b['disabled']and b['expanded']=='false'and not b['modal'],label+' closed opener enabled/collapsed',b);click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');b=button_state();check(b['expanded']=='true'and b['modal'],label+' open aria-expanded true',b);check(ev('document.querySelector(".diagram-image").currentSrc===document.querySelector(".zoom-image").currentSrc'),label+' asset preserved')
 if escape:key('\ue00c')
 else:click('.zoom-heading button')
 pause(750);b=button_state();check(not b['modal']and not b['disabled']and b['expanded']=='false'and b['focus'],label+' native close settles enabled/collapsed/focused',b)
try:
 source_guard();viewport(390,760);direct();original=read('({candidate:document.querySelector(".candidate-name").textContent,parts:[...document.querySelectorAll(".part-button")].map(b=>b.getAttribute("aria-pressed")),counter:document.querySelector(".round-progress-counter").textContent,storage:Object.fromEntries(Object.entries(sessionStorage))})');cycle('Standalone Close');cycle('Standalone same-round reopen then Escape',True);cycle('Standalone same-round reopen again Close');after=read('({candidate:document.querySelector(".candidate-name").textContent,parts:[...document.querySelectorAll(".part-button")].map(b=>b.getAttribute("aria-pressed")),counter:document.querySelector(".round-progress-counter").textContent,storage:Object.fromEntries(Object.entries(sessionStorage))})');check(original==after,'Standalone repeated zoom leaves answer/progress unchanged',{'before':original,'after':after});shot('standalone-closed')
 # Controlled same-task lifecycle fixture, not a human timing claim: queued native close then destroy old round and mount next.
 click('.diagram-tools button');wait('!!document.querySelector("dialog.zoom-dialog[open]")');ev('(()=>{document.querySelector("dialog.zoom-dialog").close();document.querySelector(".session-row button").click();document.getElementById("set-alkanes-unbranched-start").click();return true})()');image_ready();pause(750);stale=button_state();check(not stale['modal']and not stale['disabled']and stale['expanded']=='false'and ev('document.getElementById("game-root").contains(document.activeElement)'),'Queued old close cannot disable or steal focus from replacement round',stale);cycle('Standalone replacement round after queued close');OUT['staleCloseFixture']='Programmatic same-task native dialog close → actual Return-to-sets handler → actual new-set handler; no synthetic solved progress or user-timing claim.'
 viewport(1280,800);navigate('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1');app_ready();wait('!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',55)
 for n in (1,2,3):click('#scNext');wait('fScenarioPresent().index==='+str(n)+'&&!MuLERMoCScenario.checkpointPreparation')
 click('#nlQuizOpen');image_ready();original=read('Object.fromEntries(Object.entries(sessionStorage))');cycle('Embedded Close');cycle('Embedded same-round reopen then Escape',True);cycle('Embedded same-round reopen again Close');check(original==read('Object.fromEntries(Object.entries(sessionStorage))'),'Embedded repeated zoom preserves exact canonical session receipts');check(ev('document.getElementById("scNext").disabled'),'Embedded unsolved gate remains locked');shot('embedded-closed');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
