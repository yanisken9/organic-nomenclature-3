from pathlib import Path
import os,json,traceback,subprocess,signal,time
HERE=Path('docs/checks/quiz-header-progress-preflight-20261108');process=json.loads((HERE/'test-process.json').read_text());os.environ['NAMELECULE_BIDI_PORT']=str(process['bidi_port'])
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'observations':[]}
def observe(label):
 d=json.loads(ev('JSON.stringify((()=>{const p=document.querySelector(".nl-quiz-set-progress"),d=document.getElementById("nlQuizDialog"),h=d.querySelector(".nl-quiz-dialog-header"),r=p.getBoundingClientRect(),b=h.getBoundingClientRect();return {text:p.textContent,parent:p.parentElement.id,scrollTop:d.scrollTop,progress:{top:r.top,bottom:r.bottom,left:r.left,right:r.right},stickyHeader:{top:b.top,bottom:b.bottom},visibleBelowHeader:r.bottom>b.bottom&&r.top<innerHeight}})())'));d['label']=label;out['observations'].append(d);print(json.dumps(d,ensure_ascii=False),flush=True)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=counter-preflight-20261108#step=4');app_ready();until('fScenarioPresent().index===3&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
 ev('document.getElementById("nlQuizOpen").click();true');until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")',seconds=45)
 ev('document.getElementById("nlQuizDialog").scrollTop=0;true');observe('Initial counter in content below sticky header');screenshot(HERE/'counter-current-top.png')
 ev('const d=document.getElementById("nlQuizDialog");d.scrollTop=d.scrollHeight;true');observe('Counter after dialog scroll');screenshot(HERE/'counter-current-scrolled.png')
 out['completed']=True
except Exception as e:
 out['failure']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['javascriptErrors']=js_errors;(HERE/'observations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 p=subprocess.run(['ps','-p',str(process['pid']),'-o','command='],capture_output=True,text=True)
 if p.returncode==0 and process['profile'] in p.stdout and '--headless' in p.stdout:
  os.kill(process['pid'],signal.SIGTERM)
  for _ in range(30):
   if subprocess.run(['ps','-p',str(process['pid']),'-o','command='],capture_output=True).returncode!=0:break
   time.sleep(.2)
  (HERE/'cleanup.json').write_text(json.dumps({'ownedPID':process['pid'],'profileVerified':True,'ownedFirefoxStopped':True,'userProfilesUntouched':True},indent=2)+'\n')
 print(json.dumps({'completed':out['completed'],'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']:raise SystemExit(1)
