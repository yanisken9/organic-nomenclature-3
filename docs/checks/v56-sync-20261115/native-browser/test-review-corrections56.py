"""Actual DOM reproduction of independent rule/naming visibility and Greek feedback."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned56-review-support','exec'))
def apply_case(naming,rule,mode='none',alkoxy=False,viewer=False):
    ev('(()=>{const p=fScenarioPresent(),s=p.steps[0];p.title="Αλκάνια-Ονοματολογία και διακλαδώσεις";p.index=0;MuLERMoCScenario.index=0;s.nameAnalysisMode='+json.dumps(mode)+';s.show.naming='+json.dumps(naming)+';s.show.rule='+json.dumps(rule)+';s.show.alkoxyRule='+json.dumps(alkoxy)+';s.show.menu=false;s.show.viewers={"2D":'+json.dumps(viewer)+',"3D":false};return fScenarioApply(s)})()');pause(550)
    return read('({analysis:!!document.querySelector("#analysisCol")&&getComputedStyle(document.querySelector("#analysisCol")).display!=="none",name:!!document.querySelector("#nameAnalysisContainer")&&getComputedStyle(document.querySelector("#nameAnalysisContainer")).display!=="none",singleAnalysis:document.querySelector("#pageContainer").classList.contains("present-single-analysis"),singleViewer:document.querySelector("#pageContainer").classList.contains("present-single-viewer")})')
try:
    navigate('mulermoc-nom-56.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&v=review56-'+str(time.time_ns()))
    wait('!!fScenarioPresent()?.steps?.length&&MuLERMoCScenario.present&&!document.documentElement.classList.contains("lesson-loading")',100);call('browsingContext.activate',{'context':ctx})
    out['fixturePolicy']='Only transient copied/imported step settings in own headless session are varied. Stored scenario JSON and source molecule files are never written.'
    row=apply_case(False,True);check(row['analysis'] and not row['name'] and row['singleAnalysis'],'R1: explicit rule remains visible with naming hidden; single analysis column counted',row);shot('rule-only-column')
    row=apply_case(False,False);check(not row['analysis'] and not row['name'] and not row['singleAnalysis'],'R1: naming and rule both off hide analysis column',row)
    row=apply_case(True,False);check(row['analysis'] and row['name'] and row['singleAnalysis'],'R1: naming-on restores one analysis column',row)
    row=apply_case(False,False,'compCarbonsCount');check(row['analysis'] and not row['name'] and row['singleAnalysis'],'R1: component reference independently keeps its column',row)
    row=apply_case(False,False,'none',True);check(row['analysis'] and not row['name'] and row['singleAnalysis'],'R1: authored alkoxy reference independently keeps its column',row)
    row=apply_case(False,False,'none',False,True);check(not row['analysis'] and row['singleViewer'],'R1: viewer alone recenters when naming and references off',row)
    row=apply_case(False,True,'none',False,True);check(row['analysis'] and not row['singleAnalysis'] and not row['singleViewer'],'R1: viewer plus rule remain two columns',row)
    navigate('mulermoc-nom-56.html?lang=gr&mol=butane&v=wording56-'+str(time.time_ns()));app_ready();wait('window.JSmolReadyFlag===true',60);call('browsingContext.activate',{'context':ctx});pause(600)
    texts=read('Object.fromEntries(["quizMore","quizFewer","quizHetero"].map(k=>[k,fMulerT(k)]))');check(all('άτομα C'in x and 'άτομα άνθρακα'not in x for x in texts.values()),'R2: all three new GR feedback strings use approved wording',texts)
    pointer('#selectAtomsBtn');pause(250);pointer('#comp5');wait('MulerQuizTarget==="compCarbonsCount"')
    point=read('(()=>{const a=fMulerSelectAnchors().find(a=>a.atom===fMulerMainChainResolved()[0]-1),g=document.querySelector("#jsmeNomeclatureSVG svg g"),p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y}})()');pointer_at(point);pause(250)
    feedback=read('document.getElementById("mulerQuizVerdict").textContent');check('άτομα C'in feedback,'R2: actual partial native answer displays revised Greek feedback',feedback)
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:shot('review-corrections-failure')
    except Exception:pass
finally:finish('review-corrections56-browser')
if not out['completed']:raise SystemExit(1)
