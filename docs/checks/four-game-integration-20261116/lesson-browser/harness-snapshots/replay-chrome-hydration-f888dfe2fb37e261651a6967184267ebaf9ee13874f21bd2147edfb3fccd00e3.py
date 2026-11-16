"""Owned Chrome: actual147 hydration, six real representation/3D loads, gates.

Uses public Builder representation controls and read-only native/source oracles.
No naming/answer/catalog/mission state, bridge response or app callback injected.
"""
from pathlib import Path

def hydrate_summary(window_expression):
 ids=[m['id'] for m in HYDRATION_PACK['molecules']]
 expression='''(()=>{const ids=IDS;return{entries:Object.keys(nameExamples).length,expanded:Object.keys(nameExamples).filter(id=>!!nameExamples[id].structure2D_Expanded).length,records:Object.fromEntries(ids.map(id=>[id,{condensed:nameExamples[id]?.structure2D_Condensed??null,expanded:nameExamples[id]?.structure2D_Expanded??null,skeletal:nameExamples[id]?.structure2D_Skeletal??null,file3D:nameExamples[id]?.file3D??null,sameOwner:nameExamples[id]===window.nameExamplesCustom?.[id]}]))}})()'''.replace('IDS',json.dumps(ids))
 return read('('+window_expression+').eval('+json.dumps(expression)+')')
def verify_hydration(summary,label):
 check(summary['entries']==147 and summary['expanded']==147,label+' all147 entries and expanded forms')
 for item in HYDRATION_PACK['molecules']:
  record=summary['records'][item['id']]
  check(record['sameOwner'],label+' registered custom identity '+item['id'])
  for mode in ['condensed','expanded','skeletal']:
   check(record[mode]==(ROOT/item['files'][mode]).read_text(),label+' exact source '+item['id']+'/'+mode)
  check(record['file3D']==item['files']['sdf'],label+' exact curated SDF route '+item['id'])
def hydration_and_required_replay():
 page('mulermoc-nom-57.html')
 wait('typeof jsmeNomeclatureApplet!=="undefined"&&!!jsmeNomeclatureApplet&&typeof nameExamples!=="undefined"&&!!nameExamples.methane.classification',110)
 parent=hydrate_summary('window');verify_hydration(parent,'actual Main57');OUT['main57Hydration']=parent;shot('main57-hydration147')
 for item in HYDRATION_PACK['molecules']:
  mid=item['id'];page('games/name-builder.html?molecule='+mid)
  wait('!!document.querySelector("#bank-tiles button")&&document.getElementById("viewer-mask").hidden',110)
  native='document.getElementById("molecule-viewer").contentWindow'
  summary=hydrate_summary(native);verify_hydration(summary,'actual Builder55 '+mid)
  check(read(native+'.eval("selectedMol")')==mid,'Builder55 actual target '+mid)
  for mode in ['condensed','expanded','skeletal','3d']:
   selector='[data-representation='+json.dumps(mode)+']';click(selector)
   wait('document.querySelector('+json.dumps(selector)+').getAttribute("aria-pressed")==="true"&&document.getElementById("viewer-mask").hidden',90)
   check(read(native+'.eval("selectedMol")')==mid,'actual '+mode+' keeps intended molecule '+mid)
   if mode!='3d':
    check(read(native+'.eval('+json.dumps('!!document.querySelector("#jsmeNomeclatureSVG svg")')+')'),'actual '+mode+' SVG loaded '+mid)
   else:
    model=read(native+'.eval('+json.dumps('({models:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all").length,bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all").length,file3D:nameExamples[selectedMol].file3D})')+')')
    check(len(model['models'])==1 and model['atoms']>0 and model['bonds']==model['atoms']-1 and model['file3D']==item['files']['sdf'],'actual single 3D model and exact retained SDF route '+mid,model)
    OUT.setdefault('actual3DModels',[]).append({'moleculeId':mid,**model})
  verify_hydration(hydrate_summary(native),'post-mode-cycle Builder55 '+mid);shot('builder55-'+mid+'-3d')
 detective_replay(True)
 # The final lesson child/native56 must retain the same source catalog too.
 native='document.querySelector(".nl-detective-frame")?.contentDocument?.getElementById("molecule-viewer")?.contentWindow'
 # Continue destroys the final child by design, so its147 proof is collected
 # from recorded read-only native snapshots during required missions instead.

driver=Path(__file__).with_name('replay-chrome.py').read_text()
stage=" if MODE.startswith('detective'): detective_replay(MODE=='detective-required')\n else: legacy_replay()"
assert driver.count(stage)==1,'Expected bounded Chrome stage seam'
exec(compile(driver.replace(stage,' hydration_and_required_replay()'),'owned-chrome-hydration-and-required-driver','exec'))
