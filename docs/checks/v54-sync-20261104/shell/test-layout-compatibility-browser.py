"""Targeted developer regression checks for legacy/current authored box contracts."""
from pathlib import Path
import os,json,time,traceback,hashlib
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/shell';os.environ['NAMELECULE_BIDI_PORT']='9245'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
out={'completed':False,'checks':0,'states':{}}
def check(ok,label,detail=None):
 out['checks']+=1
 if not ok:raise AssertionError(label+': '+str(detail))
def jscheck(expr,label):check(ev(expr),label)
try:
 navigate('mulermoc-nom-54.html?scenario=scenarios/saturated-monoaldehydes-nomenclature.scenario.json&present=1&from=theory-library&v=legacy-layout-'+str(time.time_ns())+'#step=20')
 until("typeof fScenarioPresent==='function' && MuLERMoCScenario.ready && fScenarioPresent().steps.length===24 && !document.documentElement.classList.contains('lesson-loading')")
 app_ready()
 jscheck("fScenarioUseLegacyNameBoxes() && fScenarioPresent().steps[19].nameBoxLayout===1",'Existing missing-layout step uses legacy1')
 jscheck("document.getElementById('pageTitle').textContent===fScenarioPresent().steps[19].title",'Cold direct authored title preserved')
 jscheck("document.getElementById('comp3').classList.contains('comp-hidden') && !document.querySelector('#comp3loc,#comp3b')",'Step20 hides complete fused branch group')
 ev("window.__atomCalls=[];window.__setAtoms=jsmeNomeclatureApplet.setAtomBackgroundColors;jsmeNomeclatureApplet.setAtomBackgroundColors=function(n,args){window.__atomCalls.push(args);return window.__setAtoms.call(this,n,args)};fScenarioGo(20)")
 until("nameAnalysisMode==='compSecondSub2'")
 jscheck("document.querySelector('#comp3.selected').textContent==='ισοπροπυλο-2-μεθυλο' && !document.querySelector('#comp3loc,#comp3b')",'Original step21 fused selected component')
 state=json.loads(ev("JSON.stringify({mode:nameAnalysisMode,expected:fGetHydrocarbonBranchHighlight(2).atoms,calls:window.__atomCalls,explanation:document.querySelector('#nameAnalysisExplain').textContent})"));out['states']['legacyHighlight']=state
 wanted=sorted(state['expected']);calls=[sorted(int(x) for x in str(c).split(',')[::2] if x) for c in state['calls']]
 check(bool(wanted) and wanted in calls,'Step21 delegates whole-group actual atom highlight',state)
 check('μεθύλιο' in state['explanation'] and 'ισοπροπύλιο' in state['explanation'],'Step21 explanation retains both branch identities',state['explanation'])
 screenshot(HERE/'legacy-step21-fixed.png')
 # Authoring preview, capture/update and explicit free selection.
 navigate('mulermoc-nom-54.html?v=layout-author-'+str(time.time_ns()))
 app_ready();until('MuLERMoCScenario.ready')
 jscheck('!fScenarioUseLegacyNameBoxes() && MuLERMoCScenario.nameBoxLayoutContext===null','Default scenario preload does not leak legacycontext')
 ev("fScenarioSetAuthoring(true);window.__legacy=fScenarioNew('Legacy layout regression',true);window.__legacy.steps=[fScenarioDefaults({selectedMol:'ethyl_4_isopropyl_3_methyl_2_hexanal',nameAnalysisMode:'compSecondSub2',show:{nameSettings:true,viewers:{'2D':true,'3D':false}}},0)];fScenarioSetActive(window.__legacy.id);fScenarioGo(0)")
 jscheck("fScenarioUseLegacyNameBoxes() && fScenarioCapture().nameBoxLayout===1 && nameAnalysisMode==='compSecondSub2'",'Go preview and new capture preserve actual legacycontext')
 ev('fScenarioUpdateStep(window.__legacy.id,0)')
 jscheck('window.__legacy.steps[0].nameBoxLayout===1','Update preserves legacy layout1')
 ev("document.getElementById('ethyl_4_isopropyl_3_methyl_2_hexanal').click()")
 jscheck("!fScenarioUseLegacyNameBoxes() && !!document.getElementById('comp3loc') && !!document.getElementById('comp3b')",'Explicit free selection restores upstream54 split pieces')
 ev("document.getElementById('comp3b').click();window.__modern=fScenarioNew('Modern layout regression',true);window.__modern.steps=[fScenarioCapture()];fScenarioSetActive(window.__modern.id)")
 jscheck("window.__modern.steps[0].nameBoxLayout===2 && window.__modern.steps[0].nameAnalysisMode==='compBranchSub2'",'New split-piece capture records version2 and mode')
 ev("window.__saveOriginal=fScenarioSaveBlob;fScenarioSaveBlob=(name,blob)=>(window.__blob=blob,Promise.resolve(true));fScenarioExport();fScenarioSaveBlob=window.__saveOriginal")
 exported=ev('window.__blob.text()');ev('window.__importedText='+json.dumps(exported)+';window.__before=MuLERMoCScenario.scenarios.length;fScenarioImportFile(new File([window.__importedText],"modern.scenario.json",{type:"application/json"}))')
 until('MuLERMoCScenario.scenarios.length===window.__before+1')
 ev('fScenarioGo(0)')
 jscheck("fScenarioActive().steps[0].nameBoxLayout===2 && nameAnalysisMode==='compBranchSub2' && !!document.querySelector('#comp3b.selected')",'Real export/FileReader import replays modern split mode')
 # Present legacy from normal context, then Exit returns to that normal contract.
 ev("document.getElementById('ethyl_4_isopropyl_3_methyl_2_hexanal').click();fScenarioPresentBegin(window.__legacy.id)")
 jscheck('fScenarioUseLegacyNameBoxes() && MuLERMoCScenario.present','Legacy Present applies authored contract')
 ev('fScenarioExitPresent()')
 jscheck("!MuLERMoCScenario.present && !fScenarioUseLegacyNameBoxes() && !!document.getElementById('comp3b')",'Present Exit restores normal54 contract without leak')
 out['states']['afterExit']=json.loads(ev("JSON.stringify({mode:nameAnalysisMode,context:MuLERMoCScenario.nameBoxLayoutContext,capture:fScenarioCapture()})"))
 jscheck("nameAnalysisMode==='none' && !document.querySelector('#nameAnalysis .nameCompBox.selected') && fScenarioCapture().nameBoxLayout===2 && fScenarioCapture().nameAnalysisMode==='none'",'Exit invalidates old aggregate selection before modern capture')
 ev("window.__exitCopy=fScenarioNew('Exit capture replay',true);window.__exitCopy.steps=[fScenarioCapture()];fScenarioSetActive(window.__exitCopy.id);fScenarioGo(0)")
 jscheck("nameAnalysisMode==='none' && !fScenarioUseLegacyNameBoxes() && !!document.getElementById('comp3b')",'Exit capture replays modern layout without reinterpreted old selection')
 # Suffix splitting is versioned independently of scientific suffix naming.
 ev("window.__suffix=fScenarioNew('Suffix layout regression',true);window.__suffix.steps=[fScenarioDefaults({selectedMol:'ethyl_3_methyl_4_octen_3_yn_5_dione_2_7',nameBoxLayout:1,nameAnalysisMode:'compSuffix',show:{nameSettings:true,viewers:{'2D':true,'3D':false}}},0),fScenarioDefaults({selectedMol:'ethyl_3_methyl_4_octen_3_yn_5_dione_2_7',nameBoxLayout:2,nameAnalysisMode:'compSuffixLocants',show:{nameSettings:true,viewers:{'2D':true,'3D':false}}},1)];fScenarioSetActive(window.__suffix.id);fScenarioGo(0)")
 jscheck("nameAnalysisMode==='compSuffix' && !document.getElementById('comp9loc') && !!document.querySelector('#comp9.selected')",'Legacy suffix mode retains original combined control')
 ev('fScenarioGo(1)')
 jscheck("nameAnalysisMode==='compSuffixLocants' && !!document.querySelector('#comp9loc.selected')",'Modern suffix locant control remains available')
 ev("fScenarioPresentBegin(window.__suffix.id,0);fScenarioExitPresent()")
 jscheck("nameAnalysisMode==='none' && !document.querySelector('#nameAnalysis .nameCompBox.selected') && fScenarioCapture().nameBoxLayout===2",'Legacy fused suffix selection is invalidated on modern Exit')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'layout-compatibility-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;out['sourceHashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'js').glob('*54.js'))}
 (HERE/'layout-compatibility-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':out['checks'],'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
