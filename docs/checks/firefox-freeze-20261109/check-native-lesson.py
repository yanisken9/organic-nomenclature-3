"""Before/current lesson native fullscreen matrix in uniquely owned GUI profile."""
from pathlib import Path
import os,json,time,traceback
HERE=Path('docs/checks/firefox-freeze-20261109')
proc=json.loads((HERE/'native-window-process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
result={'completed':False,'runs':[],'limitations':['Own fresh GUI Firefox profile; not personal493','Author screen preview to reach11, not normal learner quiz progression','Native fullscreen command bypasses green-button hover popup','Passing fresh-profile replay does not resolve or rule out original whole-browser freeze']}
def save(): (HERE/'native-window-lesson.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
try:
 helper=Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(20)')
 exec(compile(helper,'owned-gui-bidi','exec'));s.settimeout(20)
 windows=call('browser.getClientWindows',{})['clientWindows'];assert len(windows)==1
 window=windows[0]['clientWindow']
 sources=[('before','docs/checks/firefox-freeze-20261109/before/scenarios/alkanes-user-3.scenario.json'),('current','scenarios/alkanes-user-3.scenario.json')]
 for label,path in sources:
  print('LOAD '+label,flush=True)
  run={'label':label,'scenario_path':path,'checks':[]};result['runs'].append(run);save()
  navigate('mulermoc-nom-54.html?scenario='+path+'&v=native-window-20261109')
  app_ready();until('!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',seconds=45)
  ev('fScenarioSetAuthoring(true);document.querySelector(".scenarioPanel.active .scList").click();document.querySelector(\'.scenarioPanel.active .srow[data-idx="10"] .scPresentStep\').click();true')
  until('MuLERMoCScenario.present&&fScenarioPresent().index===10',seconds=20)
  run['source_sha256']=ev('(async()=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",await (await fetch('+json.dumps(path)+',{cache:"no-store"})).arrayBuffer()))).map(x=>x.toString(16).padStart(2,"0")).join(""))()')
  run['loaded_scripts']=json.loads(ev('JSON.stringify([...document.scripts].map(s=>s.src).filter(Boolean))'))
  for cycle in range(3):
   for state in ['fullscreen','normal']:
    start=time.monotonic();call('browsingContext.activate',{'context':ctx})
    call('browser.setClientWindowState',{'clientWindow':window,'state':state})
    current=call('browser.getClientWindows',{})['clientWindows'];assert any(w['clientWindow']==window and w['state']==state for w in current)
    assert ev('fScenarioPresent().index')==10
    frame=ev('Promise.race([new Promise(r=>requestAnimationFrame(()=>r("frame"))),new Promise(r=>setTimeout(()=>r("timer-only"),3000))])')
    assert frame=='frame',frame
    run['checks'].append({'cycle':cycle+1,'state':state,'roundtrip_and_animation_frame':True,'elapsed_seconds':round(time.monotonic()-start,3),'viewport':json.loads(ev('JSON.stringify({width:innerWidth,height:innerHeight,viewerDisplay:getComputedStyle(document.getElementById("viewerCol")).display})'))})
    print('PASS '+label+' '+str(cycle+1)+' '+state,flush=True);save()
  screenshot(HERE/('native-'+label+'-step11.png'))
  run['loaded_j2s_resources']=json.loads(ev('JSON.stringify(performance.getEntriesByType("resource").filter(e=>/j2s|jmol|jsmol/i.test(e.name)).map(e=>({url:e.name,duration:e.duration,transferSize:e.transferSize})))'))
  run['javascript_errors_so_far']=list(js_errors);save()
 result['completed']=True;result['javascript_errors']=js_errors;save();print('COMPLETE native lesson matrix',flush=True)
except Exception:
 result['exception']=traceback.format_exc();result['javascript_errors']=globals().get('js_errors',[]);save();print(result['exception'],flush=True);raise
