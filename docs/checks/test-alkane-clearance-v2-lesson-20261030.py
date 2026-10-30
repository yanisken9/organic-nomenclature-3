"""Exercise the existing alkane lesson's only expanded step, without editing JSON."""
from pathlib import Path
source=Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text()
exec(compile(source.split('\ntry:\n navigate')[0],'clearance-test-setup','exec'))
result={'completed':False,'steps':[]}
try:
 navigate('mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=clearance-v2')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')")
 app_ready();ev('document.fonts.ready.then(()=>true)');ev(install)
 lesson=json.loads(Path('scenarios/alkanes-nomenclature-branches.scenario.json').read_text())
 indices=[i for i,s in enumerate(lesson['steps'])if s.get('mode2D')=='expanded']
 assert indices==[17]
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for i in indices:
   ev('fScenarioGo('+str(i)+');true')
   until("selectedMol==='ethyl_3_dimethyl_2_5_hexane'&&mode2D==='expanded'&&nameAnalysisMode==='compSecondSub2'")
   ev('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true))))')
   row=json.loads(ev('__endpointCheck().then(r=>JSON.stringify(r))'));row.update(step=i+1,width=width)
   assert not row['clipped']and not row['overlaps'],row
   assert row['atomCount']==32,row
   for bond in row['checks']:
    assert bond['visibleLength']>1 and all(e['gap']>.2 and e['rasterClear']for e in bond['endpoints']),(width,bond)
   result['steps'].append(row)
   if width==1500:screenshot(str(args.output/'lesson-step-18.png'))
 assert not js_errors,js_errors
 result['completed']=True
except Exception as error:
 result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors
 (args.output/'lesson.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'steps':len(result['steps'])}),flush=True)
if not result['completed']:raise SystemExit(1)
