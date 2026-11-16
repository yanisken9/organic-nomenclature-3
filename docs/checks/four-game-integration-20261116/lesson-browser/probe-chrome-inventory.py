"""Root-authorized short inventory measurement; no application source edits.

Reads the actual parent/native states first. Only afterward, invokes the native
supported fInitProps and fClassifyAllMolecules hooks as explicitly authorized
controlled diagnostics. These calls are not application fixes or solve inputs.
"""
from pathlib import Path

def inventory_probe():
 lesson()
 for index in range(1,4): pause(.9);click('#scNext');wait('fScenarioPresent().index==='+str(index))
 open_gate();wait('document.querySelectorAll(".nl-game-choice-card").length===4');click('.nl-game-choice-card:nth-child(4)')
 wait('!!document.querySelector(".nl-detective-frame")?.contentWindow?.NameleculeMolecularDetective&&!!document.querySelector(".nl-detective-frame").contentDocument.getElementById("molecule-viewer")?.contentWindow?.NameleculeMolecularDetectiveHost?.snapshot().started',90)
 pause(.5)
 expression=r'''(()=>{
 const summary=()=>({
   entryIds:Object.keys(nameExamples),
   expandedIds:Object.keys(nameExamples).filter(id=>!!nameExamples[id].structure2D_Expanded),
   mol2DIds:Object.keys(window.MOL2D||{}),customIds:Object.keys(window.nameExamplesCustom||{}),
   customRecords:Object.fromEntries(Object.keys(window.nameExamplesCustom||{}).map(id=>[id,{
     inExamples:!!nameExamples[id],sameReference:nameExamples[id]===window.nameExamplesCustom[id],
     registryHas:!!window.MOL2D?.[id],entryExpanded:!!nameExamples[id]?.structure2D_Expanded,
     entryCondensed:!!nameExamples[id]?.structure2D_Condensed,entrySkeletal:!!nameExamples[id]?.structure2D_Skeletal,
     customExpanded:!!window.nameExamplesCustom[id].structure2D_Expanded,
     customCondensed:!!window.nameExamplesCustom[id].structure2D_Condensed,
     customSkeletal:!!window.nameExamplesCustom[id].structure2D_Skeletal,
     file3D:nameExamples[id]?.file3D,classification:nameExamples[id]?.classification??null
   }])),
   customType:typeof nameExamplesCustom,extensible:Object.isExtensible(nameExamples),
   fInitProps:String(fInitProps),fInitData:String(fInitData),fClassifyAllMolecules:String(fClassifyAllMolecules).slice(0,1800),
   scriptOrder:[...document.scripts].map(s=>s.src).filter(Boolean),
   resources:performance.getEntriesByType('resource').filter(r=>r.initiatorType==='script').map(r=>({url:r.name,start:r.startTime,duration:r.duration}))
 });
 const c=document.querySelector('.nl-detective-frame').contentWindow,w=c.document.getElementById('molecule-viewer').contentWindow;
 return {parent:summary(),native:w.eval('('+summary.toString()+')()'),child:c.NameleculeMolecularDetective.snapshot(),
   nativeHost:w.NameleculeMolecularDetectiveHost.snapshot(),childBody:c.document.body.innerText};
 })()'''
 OUT['inventoryBeforeControlledCalls']=read(expression)
 shot('chrome-inventory-before-controlled')
 native='document.querySelector(".nl-detective-frame").contentDocument.getElementById("molecule-viewer").contentWindow'
 OUT['controlledDiagnosticCalls']=['Native fInitProps() only after full before-state capture; explicit root authorization.','Native fClassifyAllMolecules() only after fInitProps outcome capture; explicit root authorization.']
 ev(native+'.eval("fInitProps();true")')
 OUT['inventoryAfterInitProps']=read(expression)
 try:
  ev(native+'.eval("fClassifyAllMolecules();true")')
  OUT['inventoryAfterClassify']=read(expression)
 except Exception as problem: OUT['controlledClassifyError']=repr(problem)
 # Bounded isolated VM-like source reproduction uses a new plain object and
 # the exact actual fInitData body; it never edits the app's nameExamples.
 OUT['isolatedHydrationReproduction']=read(r'''(()=>{const frame=document.querySelector('.nl-detective-frame').contentDocument.getElementById('molecule-viewer').contentWindow;
 const source=frame.eval('String(fInitData)');const record={structure2D_Condensed:'verified condensed',structure2D_Expanded:'verified expanded',structure2D_Skeletal:'verified skeletal',file3D:'verified custom sdf'};
 const customs={example:record},examples={example:record},registry={};
 const before=JSON.parse(JSON.stringify({examples,customs}));
 const run=new Function('nameExamples','window',source+';fInitData();');run(examples,{MOL2D:registry});
 return {actualFunctionSource:source,before,after:{examples,customs},sameAlias:examples.example===customs.example};})()''')
 OUT['completedDiagnosticOnly']=True
 check(True,'short Chrome inventory states and explicitly controlled lifecycle outcomes captured')

driver=Path(__file__).with_name('replay-chrome.py').read_text()
stage=" if MODE.startswith('detective'): detective_replay(MODE=='detective-required')\n else: legacy_replay()"
assert driver.count(stage)==1,'Expected frozen diagnostic-stage seam'
exec(compile(driver.replace(stage,' inventory_probe()'),'owned-chrome-short-inventory-driver','exec'))
