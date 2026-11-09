"""Developer Firefox replay of actual14 lessons/337steps; isolated BiDi9245."""
from pathlib import Path
import os,json,time,traceback,hashlib,re
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/shell'
os.environ['NAMELECULE_BIDI_PORT']='9245'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
def hashes():
 paths=[ROOT/'mulermoc-nom-54.html']+sorted((ROOT/'js').glob('*54.js'))+sorted((ROOT/'css').glob('*54.css'))+[ROOT/'spt/init-54.spt']
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':0,'failures':[],'steps':[],'lessons':[],'sourceHashesStart':hashes(),'loadedRuntime':[],'limits':['Developer browser execution; not independent review.','Existing337 steps have no stored moveto/lang/nameExpanded fields; separate in-memory probes exercise those54 additions.']}
def check(ok,label,detail=None):
 out['checks']+=1
 if not ok:
  out['failures'].append({'label':label,'detail':detail})
  raise AssertionError(label+': '+str(detail))
def jscheck(expr,label):check(ev(expr),label)
def loaded_sources():
 return json.loads(ev("""(async()=>{let result=[];for(let x of [...document.scripts].filter(x=>x.src&&!x.src.startsWith('https:'))){let r=await fetch(x.src,{cache:'force-cache'}),b=await r.arrayBuffer(),h=await crypto.subtle.digest('SHA-256',b);result.push({url:x.src,sha256:[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('')});}return JSON.stringify(result);})()"""))

STATE="""JSON.stringify((()=>{let q=s=>document.querySelector(s),v=s=>{let x=q(s);return x?getComputedStyle(x).display!=='none':false};return {index:fScenarioPresent().index,molecule:selectedMol,mode:mode2D,chainMode:mainChainMode,nameMode:nameAnalysisMode,name:currentMolName,maxH:viewerMaxH,bothH:viewerBothH,zoom:molZoom2D,hidden:window.nameHiddenComps||[],expanded:!!window.nameExpanded,stepLang:window.__mulerStepLang,lang:fMulerLang(),box:!!window.nameBoxFlag,cross:!!window.nameCrossFlag,color:!!svgAtomColors2DFlag,colorMode:atomColorMode2D,vis3D:vis3D,atomSymbols:!!atomSymbols3DFlag,hydrogens:!!hydrogens3DFlag,spin:!!rotateFlag,svg:!!q('#jsmeNomeclatureSVG svg'),labelError:q('#jsmeNomeclatureSVG')&&q('#jsmeNomeclatureSVG').getAttribute('data-label-error'),chain:mainChainAtomsList,selectedComponents:[...document.querySelectorAll('#nameAnalysis .nameCompBox.selected')].map(x=>x.id),hiddenComponents:[...document.querySelectorAll('#nameAnalysis .nameCompBox.comp-hidden')].map(x=>x.id),componentRule:fScenarioShowComponentRule(nameAnalysisMode),ruleVisible:v('#ruleContainer'),alkoxyVisible:v('#alkoxyRuleContainer'),pending3D:MuLERMoCScenario.pending3D&&{done:MuLERMoCScenario.pending3D.done},shown2D:v('#jsmeNomeclatureSVG')&&v('#jsmeNomeclatureDIV'),shown3D:v('#nomeclature3D')}})())"""
try:
 # In-memory authoring probe exercises additive54 fields not present in existing lessonJSON.
 navigate('mulermoc-nom-54.html?probe='+str(time.time_ns()))
 app_ready();until('MuLERMoCScenario.ready && window.JSmolReadyFlag===true')
 out['loadedRuntime'].append({'lesson':'author-probe','sources':loaded_sources()})
 ev("fScenarioSetAuthoring(true);window.__probeSc=fScenarioNew('Browser54 fields',true);window.__probeSc.author='Browser author';window.__probeSc.created='2026-11-04T12:00:00.000Z';window.__probeSc.showStepNumbers=false;window.__probeSc.reserveTitleSpace=true;selectedMol='methane';fSelectMol();window.__probeStep=fScenarioCapture();window.__probeStep.title='Browser54 step';window.__probeStep.note='<p>Κανόνας <b>OH</b></p>';window.__probeStep.noteFormat='html';window.__probeStep.lang='en';window.__probeStep.show.naming=true;window.__probeStep.show.nameExpanded=true;window.__probeStep.show.viewerMaxHeight='full';window.__probeStep.show.viewerBothHeight='full';window.__probeStep.view3D.moveto='moveto 0.0 { 0 0 1 35} 85;';window.__probeSc.steps=[window.__probeStep];fScenarioSetActive(window.__probeSc.id);fScenarioPresentBegin(window.__probeSc.id)")
 until("MuLERMoCScenario.present && window.nameExpanded===true && fMulerLang()==='en' && viewerMaxH==='full' && viewerBothH==='full'")
 time.sleep(.8)
 jscheck("!!document.querySelector('#scStepText b') && document.querySelector('#scStepText b').textContent==='OH'",'Real presentation rich HTML note')
 jscheck("viewerMaxH==='full' && viewerBothH==='full' && !!window.nameExpanded && window.__mulerStepLang==='en'",'Author fullheights/expandedname/EN applied')
 out['cameraProbe']={'stored':ev('window.__probeStep.view3D.moveto'),'actual':ev('fScenarioGetMoveto()')}
 check(bool(out['cameraProbe']['actual']),'Actual3D camera readable after authoredmoveto',out['cameraProbe'])
 ev("window.__saveOriginal=fScenarioSaveBlob;fScenarioSaveBlob=(name,blob)=>(window.__exportBlob=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=window.__saveOriginal")
 probeExport=ev('window.__exportBlob.text()');exp=json.loads(probeExport)
 check(exp['author']=='Browser author' and exp['created']=='2026-11-04T12:00:00.000Z' and exp['showStepNumbers']==False and exp['reserveTitleSpace']==True,'Export real author/date/localpreferences')
 ev('window.__importText='+json.dumps(probeExport,ensure_ascii=False)+';window.__beforeImportCount=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File([window.__importText],"browser54.scenario.json",{type:"application/json"}))')
 until('MuLERMoCScenario.scenarios.length===window.__beforeImportCount+1')
 jscheck("fScenarioActive().author==='Browser author' && fScenarioActive().created==='2026-11-04T12:00:00.000Z' && fScenarioActive().showStepNumbers===false && fScenarioActive().reserveTitleSpace===true && fScenarioActive().steps[0].show.nameExpanded===true && fScenarioActive().steps[0].lang==='en' && fScenarioActive().steps[0].noteFormat==='html'",'Real FileReader import preserves54/local metadata')
 ev("window.__noteProbe=document.createElement('div');window.__pwn=0;MuLERMoCNote.renderInto(window.__noteProbe,'<p onclick=\"window.__pwn=1\">Κανόνας <b>OH</b></p><script>window.__pwn=2<'+ '/script><a href=\"javascript:alert(1)\">link</a><table><tr><td>δοκιμή</td></tr></table>','html')")
 jscheck("!!window.__noteProbe.querySelector('b') && !!window.__noteProbe.querySelector('table') && !window.__noteProbe.querySelector('script,[onclick],a[href^=javascript]') && window.__pwn===0",'Rich note sanitization')
 ev("MuLERMoCNote.renderInto(window.__noteProbe,'<div data-note-include=\"rule-table:1\"></div>','html')")
 jscheck("!!window.__noteProbe.querySelector('.note-embed--rule [data-row=\"r1-c1\"]') && !window.__noteProbe.querySelector('.note-embed--missing')",'Rich note embedded rule table')
 ev('fScenarioExitPresent()')
 jscheck("!MuLERMoCScenario.present && window.__mulerStepLang===null",'Author presentation Exit restores sessionlanguage')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 navigate('design/theory-library.html?v=v54-lessons-mobile')
 jscheck('document.documentElement.scrollWidth<=innerWidth','Library390px has no horizontaloverflow')
 check(len(json.loads(ev("JSON.stringify([...document.querySelectorAll('a[href*=scenario]')])")))==14,'Library390px retains14lessons')
 screenshot(HERE/'library-390.png')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'author-probe-failure.png')
 except Exception:pass
finally:
 out['sourceHashesEnd']=hashes();out['changedDuringRun']=[p for p,h in out['sourceHashesStart'].items() if out['sourceHashesEnd'].get(p)!=h]
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level') in ['error','warn']]
 (HERE/'author-probe-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':out['checks'],'steps':len(out['steps']),'errors':len(js_errors),'failure':out.get('failure'),'changedDuringRun':out['changedDuringRun']}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
