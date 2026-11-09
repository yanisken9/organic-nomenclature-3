"""Actual Firefox 41-step natural playback, capture/export, desktop/mobile lesson checks."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
folder=Path('/tmp/namelecule-other-acids-lesson-20261028');folder.mkdir(exist_ok=True)
lesson=json.loads(Path('scenarios/other-carboxylic-acids-nomenclature.scenario.json').read_text());source=lesson['steps'];keys=source[0]['menuSubset']
result={'completed':False,'steps':[],'checks':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def settled(i):
 t=source[i];until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(t['selectedMol'])+' && nameAnalysisMode==='+json.dumps(t['nameAnalysisMode']),seconds=20)
 until('mainChainPool3DKey==='+json.dumps(t['selectedMol']),seconds=20)
def geometry():
 return data("(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),r=svg.getBoundingClientRect();return {clipped:[...svg.querySelectorAll('text')].filter(e=>{const b=e.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1}).map(e=>e.textContent),nameOverflow:document.querySelector('.nameCompContainer').getBoundingClientRect().width>document.querySelector('#nameAnalysis .nameContainer').getBoundingClientRect().width+1}})()")
try:
 navigate('design/theory-library.html?v=other-acids-lesson-test')
 assert ev("document.querySelectorAll('a[href*=scenario]').length===14")
 ev("document.querySelector('a[href*=other-carboxylic-acids]').click();true")
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();until('!!window.JSmolReadyFlag')
 ev('window.__validated=fScenarioValidate('+json.dumps(lesson,ensure_ascii=False)+');true');assert ev('__validated.ok&&!__validated.warnings.length')
 assert data('fScenarioPresent().steps')==data('__validated.steps')
 for i,t in enumerate(source):
  settled(i)
  assert data('window.nameHiddenComps')==t['styleName']['hidden']
  assert ev('viewerMaxH')==420
  assert ev("document.getElementById('scStepText').textContent").strip()
  if t['nameAnalysisMode']!='none':
   assert ev('fScenarioShowComponentRule(nameAnalysisMode)')
   assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   assert ev('fScenarioCompIdFor(nameAnalysisMode)!==null')
   for box in t['styleName']['hidden']:assert ev('fNameCompHidden('+json.dumps(box)+')')
   if i in [2,11,15,24,28,35,37]:
    ev("document.getElementById('ruleTitle').click();true");until("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'",seconds=10)
    assert len(ev("document.getElementById('ruleTheoryContainer').textContent"))>20
    ev("document.getElementById('ruleTitle').click();true")
  if ev('numberingFlag'):until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length",seconds=10)
  geo=geometry();assert not geo['clipped']and not geo['nameOverflow'],(i+1,geo)
  result['steps'].append({'step':i+1,'key':t['selectedMol'],'name':ev('currentMolName'),'mode':t['nameAnalysisMode'],'geometry':geo,'parent':data('mainChainAtomsList')})
  if i in [0,11,15,25,29,35,38,40]:screenshot(str(folder/('step-'+str(i+1)+'.png')))
  if i<40:ev("document.getElementById('scNext').click();true")
 print('PASS natural41step playback',flush=True)
 until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
 assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
 ev("window.__blob=null;window.__create=URL.createObjectURL;URL.createObjectURL=b=>(window.__blob=b,'blob:lesson-test');window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click;true")
 exported=json.loads(ev('__blob.text()'));ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+');true');assert ev('__round.ok&&!__round.warnings.length&&JSON.stringify(__round.steps)===JSON.stringify(__validated.steps)')
 result['checks'].append('Export validates and retains all41snapshots')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.5)
  if width==390:ev("document.getElementById('rotatePromptDismiss').click();true")
  for i in [11,15,24,28,35,37,38,39,40]:
   ev('fScenarioGo('+str(i)+');true');settled(i)
   for form,idx in [('condensed',0),('expanded',1),('skeletal',2)]if i==39 else [('condensed',0)]:
    if i==39:ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(idx)+'].click();true');until('mode2D==='+json.dumps(form))
    until("(()=>{const a=document.querySelector('.nameCompContainer'),b=document.querySelector('#nameAnalysis .nameContainer');return a.getBoundingClientRect().width<=b.getBoundingClientRect().width+1})()",seconds=10)
    geo=geometry();assert not geo['clipped']and not geo['nameOverflow'],(width,i+1,form,geo)
    ev('window.__capture=fScenarioCapture();fScenarioApply(__capture);true');until('nameAnalysisMode==='+json.dumps(source[i]['nameAnalysisMode']))
  screenshot(str(folder/('final-'+str(width)+'.png')))
 result['checks'].append('Desktop1500/mobile390, twooxo, triple/thirdprefix modes,3forms,capture/apply')
 ev("document.getElementById('scPrev').click();true");settled(39)
 before_count=ev('MuLERMoCScenario.scenarios.length')
 ev('fScenarioImportFile(new File(['+json.dumps(json.dumps(lesson,ensure_ascii=False))+'],"other-acids.scenario.json",{type:"application/json"}));true')
 until('MuLERMoCScenario.scenarios.length==='+str(before_count+1),seconds=15)
 assert data('fScenarioActive().steps')==data('__validated.steps')
 result['checks'].append('Actual FileReader JSON import retains41steps')
 ev("document.getElementById('scExit').click();true");until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev('document.documentElement.scrollWidth<=innerWidth')
 ev("document.getElementById('carboxylic-acids-card').scrollIntoView({block:'center'});true");time.sleep(.5);screenshot(str(folder/'library-mobile.png'))
 assert ev("document.getElementById('carboxylic-acids-card').textContent.includes('2 διαθέσιμα μαθήματα')")
 result['checks'].append('Prev/Exit return to library, mobile card fits')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'steps':len(result['steps']),'errors':len(js_errors)}),flush=True)
