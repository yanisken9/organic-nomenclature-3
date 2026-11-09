from pathlib import Path
import json,hashlib,copy,traceback
HERE=Path('docs/checks/alkane-step11-stop-20261109')
exec(compile((HERE/'browser-helpers.py').read_text(),'helpers','exec'))
out={'completed':False,'checks':[],'rounds':[],'bounds':[],'fixturePolicy':'Seed4 for unbranched/seed1 branched unsolved starts only; six repairs solved by actual UI, no fabricated solved receipts','limitations':['Developer evidence in owned headless Firefox; not independent Reviewer and not personal Firefox freeze diagnosis','Viewport emulation1500/390/320, not physical mobile/Safari/screen reader','Step12 shown/restored but no broad3D or conference demonstration audit','Content-keyed receipt changes with edited lesson content; no migration tested or introduced']}
def visible(id):return ev('(()=>{const e=document.getElementById('+json.dumps(id)+');if(!e)return false;const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=="hidden"})()')
def snap():return json.loads(ev('JSON.stringify({index:fScenarioPresent().index,preview:NameleculeQuizCheckpoints.isPreview(fScenarioPresent()),className:document.getElementById("pageContainer").className,titleHTML:document.getElementById("pageTitle").innerHTML,noteHTML:document.getElementById("scStepText").innerHTML,nextDisabled:document.getElementById("scNext").disabled,recipe:fScenarioPresent().steps[fScenarioPresent().index].checkpoint||null})'))
def content_only(name):
 check(ev('document.getElementById("pageContainer").classList.contains("scContentOnly")') and all(not visible(x) for x in ['viewerCol','analysisCol','menuCol','jsmeNomeclatureSVG','nomeclature3D','nameAnalysisContainer']),name+' hides molecule/name/menu and their frames')
 check(visible('nlQuizCheckpoint') and visible('scStepText') and visible('pageTitle'),name+' retains lesson instructions and actual workshop card')
def gate_notice(width,name):
 ev('fScenarioGo(11);true');until('!!document.getElementById("scCheckpointNotice")&&!document.getElementById("scCheckpointNotice").hidden',6)
 data=json.loads(ev('JSON.stringify((()=>{const e=document.getElementById("scCheckpointNotice"),r=e.getBoundingClientRect(),host=e.parentElement.getBoundingClientRect();return{width:innerWidth,left:r.left,right:r.right,top:r.top,bottom:r.bottom,centerDelta:(r.left+r.right-host.left-host.right)/2,role:e.getAttribute("role"),live:e.getAttribute("aria-live"),text:e.textContent,toast:document.getElementById("scenarioToast").classList.contains("show")}})())'))
 out['bounds'].append({'check':name,**data})
 check(ev('fScenarioPresent().index===10&&document.getElementById("scNext").disabled') and abs(data['centerDelta'])<2 and data['left']>=0 and data['right']<=width and not data['toast'] and data['role']=='status' and data['live']=='polite',name+' normal gate blocks12 and centers in-flow accessible notice')
 screenshot(HERE/('after-step11-blocked-'+str(width)+'.png'))
 until('document.getElementById("scCheckpointNotice").hidden',6)
 check(ev('document.getElementById("scCheckpointNotice").textContent===""'),name+' blocked notice expires without leftover text')
def plain_note(s):
 import re,html
 return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
try:
 before=json.loads((HERE/'before.scenario.json').read_text());current=json.loads(Path('scenarios/alkanes-user-3.scenario.json').read_text())
 digest=hashlib.sha256(Path('scenarios/alkanes-user-3.scenario.json').read_bytes()).hexdigest();out['scenarioSHA256']=digest
 check(digest=='607a530a2d3ba151026517c61d6f7a31644e15abf82a687e778b7453d80089b7','Exact approved AFTER JSON bytes loaded for test')
 check(len(current['steps'])==12 and all(a==b for i,(a,b) in enumerate(zip(before['steps'],current['steps'])) if i!=10),'All other11steps unchanged')
 check(current['steps'][10]['checkpoint']==before['steps'][10]['checkpoint'] and plain_note(current['steps'][10]['note'])==plain_note(before['steps'][10]['note']),'Branched wording and exact checkpoint recipe unchanged')
 navigate('design/theory-library.html?v=step11-after-20261109');click('article[aria-labelledby=alkanes-title] a.action');ready()
 check(ev('fScenarioValidate('+json.dumps(current,ensure_ascii=False)+').ok&&fScenarioPresent().steps.length===12'),'Actual player validates updated12step lesson')
 out['progressKey']=json.loads(ev('JSON.stringify(testReceiptInfo())'))['key']
 ev('fScenarioGo(9);true');until('fScenarioPresent().index===3',12)
 check(ev('document.getElementById("scNext").disabled&&!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Real learner cannot bypass prior unsolved workshop4')
 content_only('Unchanged step4')
 seed(3,'4');open_quiz()
 for ri,d in enumerate(games['4']['alkanes-unbranched']['rounds']):
  check(mounted()['id']==d['id'] and ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3','Prior gate4 actual seeded round'+str(ri+1)+' and counter')
  solve(d);out['rounds'].append({'step':4,'index':ri+1,'id':d['id'],'actualSuccess':True});click('#nlQuizDialog .round-next button')
  if ri<2:until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']),15)
  else:until('fScenarioPresent().index===4',15)
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'),'Gate4 opens after3 actual repairs')
 ev('fScenarioGo(9);true');until('fScenarioPresent().index===9',12)
 check(visible('viewerCol') and visible('analysisCol') and not visible('nlQuizCheckpoint'),'Step10 shows original molecule/name with no leaked checkpoint frame')
 screenshot(HERE/'after-step10-desktop.png');click('#scNext');until('fScenarioPresent().index===10&&!!document.getElementById("nlQuizOpen")',12)
 check(ev('!NameleculeQuizCheckpoints.isPreview(fScenarioPresent())'),'Step10→11 uses normal learner flow')
 content_only('Updated step11')
 until('!!document.querySelector("#pageTitle img")&&document.querySelector("#pageTitle img").complete&&document.querySelector("#pageTitle img").naturalWidth>0',10)
 check(ev('!!document.querySelector("#pageTitle.scStepHeadingHasLogo img")&&document.getElementById("scStepText").classList.contains("note-html")&&document.getElementById("scStepText").querySelectorAll("b").length===3&&!document.getElementById("scStepText").textContent.includes("<b>")'),'Workshop logo loads and branched HTML instructions render correctly')
 out['step11']=snap();screenshot(HERE/'after-step11-desktop.png');gate_notice(1500,'Desktop1500')
 # Clean back/forward: an active notice is removed when leaving11.
 ev('fScenarioGo(11);true');until('!document.getElementById("scCheckpointNotice").hidden',6);click('#scPrev');until('fScenarioPresent().index===9',12)
 check(ev('document.getElementById("scCheckpointNotice").hidden') and visible('viewerCol') and visible('analysisCol'),'Step11→10 clears live blocked notice and restores molecule/name')
 click('#scNext');until('fScenarioPresent().index===10',12)
 for width,height in [(390,760),(320,700),(1500,1000)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1})
  if ev('getComputedStyle(document.getElementById("rotatePrompt")).display')!='none':click('#rotatePromptDismiss')
  content_only('Step11 at'+str(width))
  check(ev('document.documentElement.scrollWidth<=innerWidth&&document.querySelector("#pageTitle img").getBoundingClientRect().width>0'),'Step11 at'+str(width)+' has loaded logo/no horizontal overflow')
  if width!=1500:gate_notice(width,'Viewport'+str(width))
  screenshot(HERE/('after-step11-'+str(width)+'.png'))
 # Reload only unsolved seeded11 state; preserve the actual completed gate4 receipt.
 seed(10,'1');until('fScenarioPresent().index===10&&!!document.getElementById("nlQuizOpen")',15)
 check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)&&!NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)'),'Unsolved seed fixture preserves actual prior4 completion and keeps11 locked')
 open_quiz()
 for ri,d in enumerate(games['1']['alkanes-branched']['rounds']):
  check(mounted()['id']==d['id'],'Branched round'+str(ri+1)+' uses actual deterministic fixture')
  check(ev('document.getElementById("nlQuizProgress").textContent')=='Κουίζ '+str(ri+1)+'/3','Branched actual counter'+str(ri+1)+'/3')
  screenshot(HERE/('after-branched-round'+str(ri+1)+'.png'))
  solve(d);out['rounds'].append({'step':11,'index':ri+1,'id':d['id'],'actualSuccess':True})
  check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),10)')==(ri==2),'Branched completion only after actual repair'+str(ri+1))
  if ri<2:
   check(ev('document.getElementById("scNext").disabled'),'Learner Next still blocked after'+str(ri+1)+' successful branched repair(s)')
   click('#nlQuizDialog .round-next button');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")&&testMounted.id!=='+json.dumps(d['id']),15)
   click('#nlQuizBack');ev('fScenarioGo(11);true');until('!document.getElementById("scCheckpointNotice").hidden',6)
   check(ev('fScenarioPresent().index===10&&document.getElementById("scNext").disabled'),'Returning to theory after'+str(ri+1)+' repair(s) cannot bypass gate11')
   open_quiz()
  else:
   check(ev('!document.getElementById("scNext").disabled&&document.getElementById("scCheckpointNotice").hidden'),'Third actual repair unlocks Next and clears blocked notice')
   out['actualBranchedReceipt']=state(10);check(all(s and s['solved'] for s in out['actualBranchedReceipt']['states']),'All3 actual branched receipts persisted as solved')
   out['errorCountBefore12']=len(js_errors);click('#nlQuizDialog .round-next button');until('fScenarioPresent().index===11',20)
 check(visible('viewerCol') and visible('analysisCol') and not visible('nlQuizCheckpoint') and ev('!document.getElementById("pageContainer").classList.contains("scContentOnly")&&document.getElementById("scCheckpointNotice").hidden'),'Actual third Continue enters12 and restores exploration without empty workshop frames/notice')
 ev('new Promise(resolve=>setTimeout(()=>resolve(true),1400))');screenshot(HERE/'after-step12-desktop.png')
 check(ev('fScenarioPresent().steps[11].menuSubset.length===8&&fScenarioPresent().steps[11].show.viewers["2D"]&&fScenarioPresent().steps[11].show.viewers["3D"]') and visible('jsmeNomeclatureSVG') and visible('nomeclature3D'),'Step12 retains8alkane menu and authored2D+3D visibility')
 click('#scPrev');until('fScenarioPresent().index===10',12);content_only('Revisited completed11')
 check(ev('!document.getElementById("scNext").disabled&&document.getElementById("scCheckpointNotice").hidden'),'Revisited completed11 stays unlocked without stale warning')
 click('#scNext');until('fScenarioPresent().index===11',12)
 check(visible('viewerCol') and visible('analysisCol') and not visible('nlQuizCheckpoint'),'Completed11→12 replay cleanly restores molecular view')
 click('#scExit');until('location.pathname.endsWith("/design/theory-library.html")',15)
 check(True,'Normal Exit returns to theory library')
 out['completed']=True
except Exception as exc:
 out['failure']=str(exc);out['traceback']=traceback.format_exc()
 try:out['failureSnapshot']=snap();screenshot(HERE/'after-failure.png')
 except Exception as failure:out['failureCaptureError']=str(failure)
finally:
 out['javascriptErrors']=js_errors;(HERE/'browser-after.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')},ensure_ascii=False),flush=True)
if not out['completed']:raise SystemExit(1)
