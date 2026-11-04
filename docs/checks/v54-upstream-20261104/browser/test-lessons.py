"""Developer regression: original14 Main54 lessons/337steps after checkpoint pilot.
Only evidence under legacy; isolated Firefox9245.
"""
from pathlib import Path
import os,json,time,traceback,hashlib,re
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-upstream-20261104/browser'
os.environ['NAMELECULE_BIDI_PORT']='9244'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
def hashes():
 paths=[ROOT/'mulermoc-nom-54.html']+sorted((ROOT/'js').glob('*54.js'))+sorted((ROOT/'css').glob('*54.css'))+[ROOT/'spt/init-54.spt',ROOT/'js/namelecule-quiz-checkpoints.js',ROOT/'css/namelecule-quiz-checkpoints.css',ROOT/'js/namelecule-game-repair.js',ROOT/'css/namelecule-games.css']+[ROOT/p for p in re.findall(r'scenario=([^&]+)',(ROOT/'design/theory-library.html').read_text())]
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':0,'failures':[],'steps':[],'lessons':[],'sourceHashesStart':hashes(),'loadedRuntime':[],'limits':['Developer browser execution; not independent review.','Replays original337 authored steps at1500x1000; not a mobile/viewer geometry certification or an offline/conference release test.']}
def check(ok,label,detail=None):
 out['checks']+=1
 if not ok:
  out['failures'].append({'label':label,'detail':detail})
  raise AssertionError(label+': '+str(detail))
def jscheck(expr,label):check(ev(expr),label)
def loaded_sources():
 return json.loads(ev("""(async()=>{let result=[];for(let x of [...document.scripts].filter(x=>x.src&&!x.src.startsWith('https:'))){let r=await fetch(x.src,{cache:'force-cache'}),b=await r.arrayBuffer(),h=await crypto.subtle.digest('SHA-256',b);result.push({url:x.src,sha256:[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('')});}return JSON.stringify(result);})()"""))

STATE="""JSON.stringify((()=>{let q=s=>document.querySelector(s),v=s=>{let x=q(s);return x?getComputedStyle(x).display!=='none':false};return {index:fScenarioPresent().index,molecule:selectedMol,pageTitle:document.getElementById('pageTitle').textContent,mode:mode2D,chainMode:mainChainMode,nameMode:nameAnalysisMode,name:currentMolName,maxH:viewerMaxH,bothH:viewerBothH,zoom:molZoom2D,hidden:window.nameHiddenComps||[],expanded:!!window.nameExpanded,stepLang:window.__mulerStepLang,lang:fMulerLang(),box:!!window.nameBoxFlag,cross:!!window.nameCrossFlag,color:!!svgAtomColors2DFlag,colorMode:atomColorMode2D,vis3D:vis3D,atomSymbols:!!atomSymbols3DFlag,hydrogens:!!hydrogens3DFlag,spin:!!rotateFlag,svg:!!q('#jsmeNomeclatureSVG svg'),labelError:q('#jsmeNomeclatureSVG')&&q('#jsmeNomeclatureSVG').getAttribute('data-label-error'),chain:mainChainAtomsList,selectedComponents:[...document.querySelectorAll('#nameAnalysis .nameCompBox.selected')].map(x=>x.id),hiddenComponents:[...document.querySelectorAll('#nameAnalysis .nameCompBox.comp-hidden')].map(x=>x.id),componentRule:fScenarioShowComponentRule(nameAnalysisMode),ruleVisible:v('#ruleContainer'),alkoxyVisible:v('#alkoxyRuleContainer'),pending3D:MuLERMoCScenario.pending3D&&{done:MuLERMoCScenario.pending3D.done},shown2D:v('#jsmeNomeclatureSVG')&&v('#jsmeNomeclatureDIV'),shown3D:v('#nomeclature3D')}})())"""
try:
 links=['../mulermoc-nom-54.html?scenario='+p+'&present=1&from=theory-library' for p in re.findall(r'scenario=([^&]+)',(ROOT/'design/theory-library.html').read_text())]
 check(len(links)==14,'Original14 theory lesson links',len(links))
 check(sum(len(json.loads((ROOT/re.search(r'scenario=([^&]+)',link).group(1)).read_text())['steps']) for link in links)==337,'Original lesson total337')
 for lesson_index,link in enumerate(links):
  print('Starting lesson',lesson_index+1,flush=True)
  path=link.removeprefix('../').replace('mulermoc-nom-52.html','mulermoc-nom-54.html')
  navigate(path+'&test='+str(time.time_ns()))
  until("typeof fScenarioPresent==='function' && MuLERMoCScenario.ready && !!fScenarioPresent() && fScenarioPresent().steps.length>0 && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();until('window.JSmolReadyFlag===true')
  jscheck("typeof MuSVG==='function' && typeof Snap==='undefined' && !!MuLERMoCNote.isAvailable()",'NativeSVG/richnote readiness lesson'+str(lesson_index+1))
  if lesson_index==0:out['loadedRuntime'].append({'lesson':1,'sources':loaded_sources()})
  source=json.loads(ev('JSON.stringify(fScenarioPresent().steps)'))
  check(not any('checkpoint' in step for step in source),'Original lesson has no required checkpoint metadata')
  title=ev('fScenarioPresent().title')
  shownumbers=ev('fScenarioPresent().showStepNumbers!==false')
  firsttitle=(('1. ' if shownumbers else '')+source[0]['title'])
  check(ev("document.getElementById('pageTitle').textContent")==firsttitle,'Cold initial authored presentation title '+title)
  lesson_start=len(out['steps'])
  ev('window.__validated=fScenarioValidate({scenarioVersion:1,steps:'+json.dumps(source,ensure_ascii=False)+'})')
  jscheck('window.__validated.ok && window.__validated.warnings.length===0','Scenario validates '+title)
  for i,step in enumerate(source):
   ev('fScenarioGo('+str(i)+')')
   wantedMode='condensedZigZag' if step['style2D']['zigzag'] else step['mode2D']
   until('fScenarioPresent().index==='+str(i)+' && selectedMol==='+json.dumps(step['selectedMol']))
   until('mode2D==='+json.dumps(wantedMode)+' && nameAnalysisMode==='+json.dumps(step['nameAnalysisMode']),seconds=20)
   if step['show']['viewers']['3D']:
    until('!MuLERMoCScenario.pending3D || MuLERMoCScenario.pending3D.done',seconds=25)
   state=json.loads(ev(STATE))
   for field,expected in [('index',i),('pageTitle',((str(i+1)+'. ' if shownumbers else '')+step['title'])),('molecule',step['selectedMol']),('mode',wantedMode),('chainMode',step['mainChainMode']),('nameMode',step['nameAnalysisMode']),('maxH',step['show']['viewerMaxHeight']),('bothH',step['show']['viewerBothHeight']),('zoom',step['style2D']['zoom']),('hidden',step['styleName']['hidden']),('expanded',bool(step['show'].get('nameExpanded',False) and step['show'].get('naming',True))),('stepLang',step.get('lang','gr')),('lang',step.get('lang','gr')),('box',step['styleName']['box']),('cross',step['styleName']['cross']),('color',step['style2D']['atomColors']),('colorMode',step['style2D']['colorMode']),('vis3D',step['view3D']['style']),('atomSymbols',step['view3D']['atomSymbols']),('hydrogens',step['view3D']['showH']),('spin',step['view3D']['spin']),('shown2D',step['show']['viewers']['2D']),('shown3D',step['show']['viewers']['3D'])]:
    check(state[field]==expected,title+' step'+str(i+1)+' '+field,{'expected':expected,'actual':state[field]})
   check(bool(state['name']) and bool(state['chain']),title+' step'+str(i+1)+' name andchain',state)
   if step['show']['viewers']['2D']:check(state['svg'] and not state['labelError'],title+' step'+str(i+1)+' actual2D drawing',state.get('labelError'))
   if state['componentRule']:check(not state['ruleVisible'],title+' step'+str(i+1)+' componentrule initiallycollapsed')
   if step['nameAnalysisMode']!='none':check(bool(state['selectedComponents']),title+' step'+str(i+1)+' selectedname component',state)
   jscheck("!document.querySelector('#nlQuizCheckpoint,#nlQuizDialog[open]')",title+' step'+str(i+1)+' no checkpoint UI')
   if i<len(source)-1:jscheck("!document.getElementById('scNext').disabled && document.getElementById('scNext').getAttribute('aria-disabled')==='false'",title+' step'+str(i+1)+' Next remains enabled')
   out['steps'].append({'lesson':title,'step':i+1,'state':state})
  actual3d=None
  if source[-1]['show']['viewers']['3D']:
   sdf=ev('nameExamples[selectedMol].file3D')
   sdfpath=(ROOT/sdf).resolve()
   check(sdfpath.is_relative_to(ROOT),'Final3D source in repo '+title)
   expected_atoms=int(sdfpath.read_text().splitlines()[3][:3])
   until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))==="+str(expected_atoms),seconds=30)
   actual3d=json.loads(ev("JSON.stringify({molecule:selectedMol,model:fJSmolGetPropertyAsArray(jmolAppletNomeclature,'modelInfo'),atoms:Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count')),live:fJSmolLive(),canvas:!!document.querySelector('#nomeclature3D canvas'),height:document.getElementById('nomeclature3D').clientHeight,width:document.getElementById('nomeclature3D').clientWidth})"))
   check(actual3d['live'] and actual3d['atoms']==expected_atoms and actual3d['canvas'] and actual3d['height']>0 and actual3d['width']>0,'Actual final3D rendered model '+title,actual3d)
   check(len(actual3d['model']['models'])==1 and actual3d['model']['models'][0]['file'].endswith('/'+sdf),'Actual final3D source matches selected molecule '+title,actual3d)
  # Invoke the real export assembly and intercept only browser delivery.
  ev("window.__saveOriginal=fScenarioSaveBlob;window.__exportBlob=null;fScenarioSaveBlob=(name,blob)=>(window.__exportBlob=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=window.__saveOriginal")
  exported=json.loads(ev('window.__exportBlob.text()'))
  check(exported['app']=='mulermoc-nom-54' and exported['scenarioVersion']==1,'Export54 marker/schema '+title)
  ev('window.__round=fScenarioValidate('+json.dumps(exported,ensure_ascii=False)+')')
  jscheck('window.__round.ok && !window.__round.warnings.length && JSON.stringify(window.__round.steps)===JSON.stringify(window.__validated.steps)','Export/validate roundtrip '+title)
  check(exported.get('showStepNumbers')==ev('fScenarioPresent().showStepNumbers!==false') and exported.get('reserveTitleSpace')==ev('fScenarioPresent().reserveTitleSpace===true'),'Export local preference metadata '+title)
  ev("document.getElementById('scPrev').click()")
  until('fScenarioPresent().index==='+str(len(source)-2))
  check(ev('fScenarioPresent().index')==len(source)-2,'Previous button '+title)
  ev("document.getElementById('scNext').click()")
  until('fScenarioPresent().index==='+str(len(source)-1))
  check(ev('fScenarioPresent().index')==len(source)-1,'Next button '+title)
  if lesson_index in [0,7,13]:screenshot(HERE/('lesson-'+str(lesson_index+1)+'-last.png'))
  out['lessons'].append({'title':title,'steps':len(out['steps'])-lesson_start,'actualFinal3D':actual3d,'sourceHashesAfter':hashes()})
  print('Lesson checked',lesson_index+1,len(source),title,flush=True)
  ev("document.getElementById('scExit').click()")
  until("location.pathname.endsWith('/design/theory-library.html')")
  check(True,'Exit returns tolibrary '+title)
  (HERE/'lessons-progress.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 check(len(out['steps'])==337,'All337 actual steps replayed',len(out['steps']))
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'lessons-failure.png')
 except Exception:pass
finally:
 out['sourceHashesEnd']=hashes();out['changedDuringRun']=[p for p,h in out['sourceHashesStart'].items() if out['sourceHashesEnd'].get(p)!=h]
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['error','warn']]
 out['externalCactusDiagnostics']=[e for e in out['diagnostics'] if 'cactus.nci.nih.gov' in json.dumps(e)]
 out['otherDiagnostics']=[e for e in out['diagnostics'] if 'cactus.nci.nih.gov' not in json.dumps(e)]
 (HERE/'lessons-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':out['checks'],'steps':len(out['steps']),'errors':len(js_errors),'failure':out.get('failure'),'changedDuringRun':out['changedDuringRun']}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
