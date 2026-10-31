from pathlib import Path
import os,json,ast,traceback
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8023/'
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
root=Path('/tmp/namelecule-propene-fix-20261031');r={'navigation':[],'alkenes':[]}
try:
 navigate('mulermoc-nom-52.html?scenario=scenarios/alkenes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=propene-nav-test')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();ev('document.fonts.ready.then(()=>true)');until('window.JSmolReadyFlag===true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  ev('fScenarioGo(19);true');until('fScenarioPresent().index===19')
  for button,index in [('scNext',20),('scPrev',19),('scNext',20)]:
   ev('document.getElementById('+json.dumps(button)+').click();true');until('fScenarioPresent().index==='+str(index)+'&&selectedMol==="ethyl_3_dimethyl_2_5_hexene_2"&&mode2D==="condensed"')
   r['navigation'].append({'width':width,'button':button,'step':index+1,'passed':True})
 ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("design/theory-library.html")&&document.querySelectorAll("a[href*=\\"scenario=\\"]").length===14')
 r['exitToLibrary']=True
 navigate('mulermoc-nom-52.html?test=all-alkenes-read-only-audit');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)')
 tree=ast.parse(Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text());install=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='install'for t in n.targets)))
 install=install.replace('const bonds=bondList.map(b=>b.slice());','const primitives=bondList.flatMap((b,i)=>Array.from({length:b[2]},(_,offset)=>({b,line:svgBondList[i]-1+offset}))); const bonds=primitives.map(v=>v.b.slice()); const lineIndices=primitives.map(v=>v.line);')
 install=install.replace('line=edges[n];','line=edges[lineIndices[n]];').replace('if(!line||order!==1)','if(!line||![1,2].includes(order))')
 ev(install)
 keys=json.loads(ev('JSON.stringify(Object.keys(nameExamples).filter(k=>nameExamples[k]?.classification?.seriesKey==="alkenes"))'));r['alkeneKeys']=keys
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for key in keys:
   ev('selectedMol='+json.dumps(key)+';mode2D="expanded";fInitProps();fLoadMol2D();true')
   v=json.loads(ev('__endpointCheck().then(r=>JSON.stringify(r))'));v.update(key=key,width=width,mode=ev('mode2D'),name=ev('currentMolName'));r['alkenes'].append(v)
   singleFailures=[(b['a'],b['b'],e['atom'],e['gap'])for b in v['checks']for e in b['endpoints']if e['gap']<=.2 or not e['rasterClear']]
   print(key,width,v['name'],'min gap',round(min(e['gap']for b in v['checks']for e in b['endpoints']),3),'flagged endpoints',len(singleFailures),flush=True)
 r['completed']=True
except Exception as e:r['failure']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
finally:
 r['javascriptErrors']=js_errors;(root/'navigation-and-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{});print('Completed',r.get('completed',False),'navigation',len(r['navigation']),'alkene cases',len(r['alkenes']),'errors',len(js_errors)),
if not r.get('completed'):raise SystemExit(1)
