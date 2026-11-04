from pathlib import Path
import os,json,traceback,time
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104'
os.environ['NAMELECULE_BIDI_PORT']='9244'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':[]}
try:
 navigate('mulermoc-nom-54.html?v=integration-'+str(time.time_ns()))
 app_ready()
 until('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!!document.querySelector("#nameAnalysis .nameCompBox")',seconds=20)
 out['checks'].append({'boot':True,'records':ev('Object.keys(nameExamples).length'),'name':ev('currentMolName'),'metrics':ev('!!window.NameleculeLabelMetrics')})
 for key in ['propene','penten_3_yne_1','penten_2_yn_4_oic_acid','ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid','isopropyl_2_3_dimethylbutanoate']:
  for mode in ['condensed','expanded','skeletal']:
   state=json.loads(ev('JSON.stringify((()=>{selectedMol='+json.dumps(key)+';fInitProps();mode2D='+json.dumps(mode)+';mainChainMode="algorithmic";fLoadMol2D();fShowNameAnalysis();return {key:selectedMol,mode:mode2D,name:currentMolName,chain:mainChainAtomsList,labels:[...document.querySelectorAll("#jsmeNomeclatureSVG text[data-namelecule-role=label]")].map(n=>n.textContent),labelError:document.getElementById("jsmeNomeclatureSVG").getAttribute("data-label-error"),svg:!!document.querySelector("#jsmeNomeclatureSVG svg")}})())'))
   assert state['svg']and state['name']and not state['labelError'],state
   out['checks'].append(state)
   if key=='penten_3_yne_1'and mode=='expanded':
    out['legacyHydrogen']=ev('jsmeNomeclatureApplet.getAtom(0,6).label')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  ev('fResizeViewers();true');until('!!document.querySelector("#jsmeNomeclatureSVG svg")')
  out['checks'].append({'width':width,'scrollWidth':ev('document.documentElement.scrollWidth'),'innerWidth':width})
  screenshot(HERE/('basic-'+str(width)+'.png'))
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'basic-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['error','warn']]
 (HERE/'basic-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
