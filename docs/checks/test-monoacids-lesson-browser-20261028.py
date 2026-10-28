"""Real Firefox lesson playback; artifacts only under /tmp. Localhost8013/BiDi9237."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
folder=Path('/tmp/namelecule-monoacids-lesson-20261028');folder.mkdir(exist_ok=True)
lesson=json.loads(Path('scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json').read_text());source=lesson['steps']
keys=source[0]['menuSubset'];names=dict(zip(keys,['μεθανικό οξύ','προπανικό οξύ','βουτανικό οξύ','2-μεθυλοπροπανικό οξύ','πεντανικό οξύ','2,2-διμεθυλοπροπανικό οξύ','2-αιθυλο-3-μεθυλοπεντανικό οξύ','3-αιθυλο-2-ισοπροπυλο-4,5-διμεθυλοεξανικό οξύ']))
result={'completed':False,'steps':[],'checks':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def settled(i,mode=None):
 t=source[i];until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(t['selectedMol']))
 until('nameAnalysisMode==='+json.dumps(t['nameAnalysisMode']if mode is None else mode),seconds=15)
 until('mainChainPool3DKey==='+json.dumps(t['selectedMol']),seconds=15)
def geometry():
 return data("(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),r=svg.getBoundingClientRect();return {clipped:[...svg.querySelectorAll('text')].filter(e=>{const b=e.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1}).map(e=>e.textContent),nameOverflow:document.querySelector('.nameCompContainer').getBoundingClientRect().width>document.querySelector('#nameAnalysis .nameContainer').getBoundingClientRect().width+1}})()")
try:
 navigate('design/welcome-proposal.html?v=monoacids-test');ev("document.querySelector('a[href*=theory-library]').click();true")
 until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev("document.querySelectorAll('article.lesson').length===10 && document.querySelectorAll('a[href*=scenario]').length===13")
 assert ev("!document.querySelector('[aria-labelledby=other-carboxylic-acids-title] a')")
 ev("document.querySelector('a[href*=saturated-monocarboxylic-acids]').click();true")
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')")
 app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)')
 ev('window.__validated=fScenarioValidate('+json.dumps(lesson,ensure_ascii=False)+');true');assert ev('window.__validated.ok&&!window.__validated.warnings.length')
 assert data('fScenarioPresent().steps')==data('__validated.steps')
 for i,t in enumerate(source):
  settled(i);assert ev('currentMolName')==names[t['selectedMol']]
  assert data('window.nameHiddenComps')==t['styleName']['hidden']
  assert ev('viewerMaxH')==420
  if t['nameAnalysisMode']!='none':
   assert ev('fScenarioShowComponentRule(nameAnalysisMode)')
   assert ev("getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
   for box in t['styleName']['hidden']:assert ev('fNameCompHidden('+json.dumps(box)+')')
   if i in [1,2,3,10,23,24]:
    ev("document.getElementById('ruleTitle').click();true");until("getComputedStyle(document.getElementById('ruleContainer')).display!=='none'",seconds=10)
    assert len(ev("document.getElementById('ruleTheoryContainer').textContent"))>20
    ev("document.getElementById('ruleTitle').click();true");until("getComputedStyle(document.getElementById('ruleContainer')).display==='none'",seconds=10)
  if ev('numberingFlag'):until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length",seconds=10)
  geo=geometry();assert not geo['clipped']and not geo['nameOverflow'],(i+1,geo)
  if i in [0,6,23,24,27]:screenshot(str(folder/('step-'+str(i+1)+'.png')))
  result['steps'].append({'step':i+1,'key':t['selectedMol'],'name':names[t['selectedMol']],'mode':t['nameAnalysisMode'],'hidden':t['styleName']['hidden'],'geometry':geo})
  if i<27:ev("document.getElementById('scNext').click();true")
 print('PASS natural28step playback, rules, reveal states, geometry',flush=True)
 until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
 assert ev("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))===41")
 assert ev('fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)')
 # Full third-prefix capture/apply round trip including its optional rule.
 for box,mode in [('acidPrefixNumber3','compAcidNumber3'),('acidPrefixSub3','compAcidSub3')]:
  ev('if(nameAnalysisMode!=='+json.dumps(mode)+')document.getElementById('+json.dumps(box)+').click();true')
  until('nameAnalysisMode==='+json.dumps(mode),seconds=10)
  expected=data('(()=>{const ids=fGetHydrocarbonBranchHighlight3D(3).atoms,s=new Set(ids);for(const b of bondList3D){if(ids.includes(b[0])&&allAtomsTypeList3D[b[1]-1]==="H")s.add(b[1]);if(ids.includes(b[1])&&allAtomsTypeList3D[b[0]-1]==="H")s.add(b[0]);}return [...s].sort((a,b)=>a-b)})()')
  until("JSON.stringify(Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno.all').sort((a,b)=>a-b))==="+json.dumps(json.dumps(expected,separators=(',',':'))),seconds=10)
  selected=data("Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno.all')");assert sorted(selected)==expected,(box,selected,expected)
  ev('window.__capture=fScenarioCapture();true');assert ev('__capture.nameAnalysisMode')==mode
  ev('nameAnalysisMode="none";fClearHighlights();fScenarioApply(__capture);true');until('nameAnalysisMode==='+json.dumps(mode),seconds=10)
  result['checks'].append({'captureMode':mode,'selected3D':selected})
 # Export/validate must retain all authored snapshots and new modes/hidden IDs.
 ev("window.__blob=null;window.__create=URL.createObjectURL;URL.createObjectURL=b=>(window.__blob=b,'blob:lesson-test');window.__click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};fScenarioExport();URL.createObjectURL=window.__create;HTMLAnchorElement.prototype.click=window.__click;true")
 exported=json.loads(ev('__blob.text()'));ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+');true')
 assert ev('__round.ok&&!__round.warnings.length&&JSON.stringify(__round.steps)===JSON.stringify(__validated.steps)')
 ev("document.getElementById('scPrev').click();true");settled(26)
 ev('fScenarioGo(23);true');settled(23)
 ev('fScenarioGo(24);true');settled(24)
 # Narrow lesson replay exercises both new modes and the long full name.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':1000},'devicePixelRatio':1});time.sleep(.7)
 ev("document.getElementById('rotatePromptDismiss').click();true")
 for i in [20,23,24,25,27]:
  ev('fScenarioGo('+str(i)+');true');settled(i)
  if ev('numberingFlag'):until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===mainChainAtomsList.length",seconds=10)
  geo=geometry();assert not geo['clipped']and not geo['nameOverflow'],(i,geo)
 screenshot(str(folder/'final-narrow.png'))
 ev("document.getElementById('scExit').click();true");until("location.pathname.endsWith('/design/theory-library.html')")
 assert ev('document.documentElement.scrollWidth<=innerWidth');screenshot(str(folder/'library-narrow.png'))
 # Existing12linked lessons validate; existing rule availability/mappings remain.
 links=data("[...document.querySelectorAll('a[href*=scenario]')].map(a=>a.href)")
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=monoacid-old-guard');app_ready()
 for url in links:
  path=url.split('scenario=')[1].split('&')[0];oldlesson=json.loads(Path(path).read_text());ev('window.__old=fScenarioValidate('+json.dumps(oldlesson,ensure_ascii=False)+');true');assert ev('__old.ok&&!__old.warnings.length'),path
 result['checks']+=['Export/schema round trip','Prev/jump/new modes at390px','Exit to13lesson library without overflow','All13linked lessons validate']
 navigate('mulermoc-nom-52.html?scenario=scenarios/saturated-monoketones-nomenclature.scenario.json&present=1&from=theory-library&v=monoacid-old-player-guard')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready()
 for i in [1,3,21]:
  ev('fScenarioGo('+str(i)+');true');oldmode=json.loads(Path('scenarios/saturated-monoketones-nomenclature.scenario.json').read_text())['steps'][i]['nameAnalysisMode'];until('nameAnalysisMode==='+json.dumps(oldmode),seconds=15)
  assert ev("fScenarioShowComponentRule(nameAnalysisMode)&&getComputedStyle(document.getElementById('ruleContainer')).display==='none'")
 result['checks'].append('Existing ketone lesson replays root/suffix/branch steps with closed rules')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'steps':len(result['steps']),'errors':len(js_errors)}),flush=True)
