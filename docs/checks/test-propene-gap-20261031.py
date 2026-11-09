"""Propene-only clearance: real Firefox guards, raster gaps and presentation flow.
Reuses existing BiDi and detached-glyph raster probes; requires isolated9237.
"""
from pathlib import Path
import argparse,ast,base64,gzip,json,os,traceback
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8023/')
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
# Read the existing independent glyph-raster probe without executing its tests.
tree=ast.parse(Path('docs/checks/test-alkane-clearance-v2-20261030.py').read_text())
install=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='install'for t in n.targets)))
# A double bond emits two SVG lines: resolve single-bond line indices from the
# core's actual mapping, rather than incorrectly assuming one line per bond.
install=install.replace('const bonds=bondList.map(b=>b.slice());','const singles=bondList.map((b,i)=>({b,i})).filter(v=>v.b[2]===1); const bonds=singles.map(v=>v.b.slice()); const lineIndices=singles.map(v=>svgBondList[v.i]-1);')
install=install.replace('line=edges[n];','line=edges[lineIndices[n]];')
snap=json.loads(gzip.decompress(Path('docs/checks/propene-gap-before-20261031.json.gz').read_bytes()))
old=base64.b64decode(snap['sources']['js/mulermoc-nom-molview-52.js']).decode();old=old[old.index('function fPadExpandedAlkaneLabels()'):old.index('// ── fMolHasSpCarbon')]
result={'completed':False,'guards':[],'cases':[],'interactions':[],'lesson':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def measure():return json.loads(ev('__endpointCheck().then(r=>JSON.stringify(r))'))
def validate(row):
 assert row['atomCount']==9 and not row['clipped']and not row['overlaps'],row
 assert len(row['checks'])==7,row
 for b in row['checks']:
  assert b['visibleLength']>1,b
  assert all(e['gap']>.2 and e['rasterClear']for e in b['endpoints']),b
try:
 navigate('mulermoc-nom-52.html?test=propene-gap');app_ready();ev('document.fonts.ready.then(()=>true)');until('window.JSmolReadyFlag===true')
 ev(install);ev('window.__padBefore=('+old+');true')
 keys=data('Object.keys(MOL2D)')
 for start in range(0,len(keys),20):
  rows=data('(()=>{const rows=[];for(const key of '+json.dumps(keys[start:start+20])+'){for(const mode of ["condensed","expanded","skeletal"]){if(!MOL2D[key][mode])continue;selectedMol=key;mode2D=mode;const a=__render(__padBefore),b=__render(__padAfter);rows.push({key,mode,sameSVG:a.svg===b.svg,sameLines:JSON.stringify(a.lines)===JSON.stringify(b.lines),sameText:JSON.stringify(a.texts)===JSON.stringify(b.texts),sameViewBox:a.viewBox===b.viewBox})}}return rows})()')
  for r in rows:
   assert r['sameLines']and r['sameText']and r['sameViewBox'],r
   assert r['sameSVG']==(r['key']!='propene'or r['mode']!='expanded'),r
  result['guards']+=rows
 print('Library guards',len(result['guards']),'PASS',flush=True)
 ev('fPadExpandedAlkaneLabels=__padAfter;true')
 for width,dpr in [(1500,1),(390,1),(1500,2)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':dpr})
  for zoom in [.5,2,4,6]:
   for phase in ['before','after']:
    ev('selectedMol="propene";mode2D="expanded";fInitProps();fLoadMol2D();fShowNameAnalysis();fPadExpandedAlkaneLabels=__pad'+phase.capitalize()+';molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
    row=measure();row.update(width=width,dpr=dpr,zoom=zoom,phase=phase);result['cases'].append(row)
    if phase=='after':validate(row)
    if width==1500 and dpr==1 and zoom==2:screenshot(str(args.output/('propene-'+phase+'.png')))
   print('Gaps',width,dpr,zoom,'PASS',flush=True)
  # Use the actual component buttons and zoom controls; check repeated rebuild.
  ev('document.getElementById("propene").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();fShowNameAnalysis();true')
  for comp in ['comp1','comp5','comp6']:
   if not ev('!!document.getElementById('+json.dumps(comp)+')'):continue
   ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(comp)+').click();true')
   until("!numberingFlag||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=15)
   row=measure();row.update(width=width,dpr=dpr,component=comp,analysisMode=ev('nameAnalysisMode'));validate(row);result['interactions'].append(row)
   if ev('numberingFlag'):assert ev('numbersSVGElements.length===3')
  ev('document.getElementById("zoomInBtn").click();document.getElementById("zoomOutBtn").click();true');validate(measure())
  assert ev('(()=>{fPadExpandedAlkaneLabels();const a=molSvg.node.outerHTML;fPadExpandedAlkaneLabels();return a===molSvg.node.outerHTML})()')
  # Switch away/back via real menu/radio events, preventing cached-mask leakage.
  ev('document.getElementById("methane").click();document.getElementById("propene").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true');validate(measure())
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png&&!!window.__exportSvg');assert ev("__png.size>1000&&!new DOMParser().parseFromString(__exportSvg,'image/svg+xml').querySelector('parsererror')");result['export']='PNG blob and parseable SVG'
 # Existing lesson has no propene Expanded preset. Check unchanged step replay
 # and use its existing allowed-molecule menu to exercise propene in presentation.
 navigate('mulermoc-nom-52.html?scenario=scenarios/alkenes-nomenclature-branches.scenario.json&present=1&from=theory-library&v=propene-gap-test')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();ev('document.fonts.ready.then(()=>true)');until('window.JSmolReadyFlag===true');ev(install)
 lesson=json.loads(Path('scenarios/alkenes-nomenclature-branches.scenario.json').read_text())
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for i in [0,4,18,20,19,20]:
   ev('fScenarioGo('+str(i)+');true');expected=lesson['steps'][i]
   until('selectedMol==='+json.dumps(expected['selectedMol'])+'&&mode2D==='+json.dumps(expected['mode2D']))
   result['lesson'].append({'width':width,'step':i+1,'molecule':expected['selectedMol'],'mode':expected['mode2D'],'presenting':ev('!!fScenarioPresent()')})
  assert ev('!!document.getElementById("propene")')
  ev('document.getElementById("propene").click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true');until('selectedMol==="propene"&&mode2D==="expanded"');validate(measure())
  if width==1500:screenshot(str(args.output/'propene-presentation.png'))
  ev('fScenarioGo(19);fScenarioGo(20);true');until('selectedMol==="ethyl_3_dimethyl_2_5_hexene_2"&&mode2D==="condensed"')
 result['completed']=True
except Exception as e:
 result['failure']=str(e);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
 result['javascriptErrors']=js_errors;(args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'guards':len(result['guards']),'cases':len(result['cases']),'interactions':len(result['interactions']),'lesson':len(result['lesson']),'diagnostics':len(js_errors)}),flush=True)
if not result['completed']:raise SystemExit(1)
