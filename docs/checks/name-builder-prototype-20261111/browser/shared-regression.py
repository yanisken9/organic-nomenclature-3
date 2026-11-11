from pathlib import Path
import hashlib,urllib.request
exec((Path(__file__).parent/'driver.py').read_text(),globals())
BASE=json.loads((HERE/'preview-server.json').read_text())['baseURL']
call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }'})
out={'completed':False,'checks':[],'role':'Developer real-browser bounded shared-script regression','baseURL':BASE}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def nav(path):call('browsingContext.navigate',{'context':ctx,'url':BASE+path,'wait':'none'})
def main_ready():wait('typeof fSelectMol==="function"&&typeof nameExamples!=="undefined"&&!!jsmeNomeclatureApplet&&typeof fJSmolLive==="function"&&fJSmolLive()',60)
def model():return read('(()=>{let mi=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo"),a=Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all"),b=Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all");return{molecule:selectedMol,name:currentMolName,model:mi.models,atoms:a.map(x=>({n:x.atomno,s:x.sym})),bonds:b.map(x=>[x.atom1.atomno,x.atom2.atomno,x.order]),expectedAtoms:allAtomsTypeList3D,expectedBonds:bondList3D,error:Jmol.evaluateVar(jmolAppletNomeclature,"_errormessage"),marker:Jmol.evaluateVar(jmolAppletNomeclature,"regressionMarker"),canvas:document.querySelector("#jmolAppletNomeclature_canvas2d")?.getBoundingClientRect().toJSON()}})()')
def expect_model(mid,tag):
 wait('(()=>{try{let mi=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo");return selectedMol==='+json.dumps(mid)+'&&mi.models?.length===1&&mi.models[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all").length===allAtomsTypeList3D.length}catch(e){return false}})()',40)
 marker=int(time.time()*1000)%100000000
 ev('Jmol.script(jmolAppletNomeclature,"regressionMarker = '+str(marker)+';");true')
 wait('+Jmol.evaluateVar(jmolAppletNomeclature,"regressionMarker")==='+str(marker),30)
 d=model();out.setdefault('models',[]).append(d)
 expected=[{'n':i+1,'s':s}for i,s in enumerate(d['expectedAtoms'])]
 edge=lambda b:(min(b[0],b[1]),max(b[0],b[1]),b[2])
 check(d['atoms']==expected and sorted(map(edge,d['bonds']))==sorted(map(edge,d['expectedBonds'])) and not d['error'],tag+' actual model graph and queued init completion without parse error',{'id':mid,'atoms':len(d['atoms']),'bonds':len(d['bonds']),'error':d['error']})
 return d
try:
 with urllib.request.urlopen(BASE+'spt/init-55.spt',timeout=10)as r:b=r.read()
 check(hashlib.sha256(b).hexdigest()==hashlib.sha256((ROOT/'spt/init-55.spt').read_bytes()).hexdigest(),'Fresh origin serves exact corrected shared init')
 nav('mulermoc-nom-55.html');main_ready();ev('selectedMol="ethane";fSelectMol();true');expect_model('ethane','Ordinary Main55 cold-origin')
 for i,form in enumerate(['condensed','expanded','skeletal']):
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click();true');wait('mode2D==='+json.dumps(form)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
  check(ev('currentMolName')=='αιθάνιο','Main55 '+form+' name preserved')
 ev('fToggleViewer3D();true');time.sleep(.5);ev('fToggleViewer3D();true');time.sleep(.5);ev('fZoom3D(1);true');time.sleep(.5);ev('fZoom3D(-1);true');time.sleep(.5);expect_model('ethane','Main55 paced visibility/zoom replay')
 shot('shared-main55.png')
 nav('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library');main_ready()
 wait('MuLERMoCScenario.ready&&!!fScenarioPresent()&&fScenarioPresent().steps.length===12&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',60)
 # Reuse only byte-exact genuinely earned receipts from the prior native-pointer replay.
 prior_path=ROOT/'docs/checks/alkane-quiz-presentation-20261110/browser/after-browser.json';prior=json.loads(prior_path.read_text());assert prior['completed']and len(prior['rounds'])==6
 receipt=prior['rounds'][-1]['receipt'];current_content=ev('(()=>{let s=fScenarioPresent();return JSON.stringify({version:1,title:String(s.title||""),author:String(s.author||"Unknown"),steps:s.steps})})()')
 assert all(r['content']==current_content and r['states']['3']['solved'] and r['states']['10']['solved'] for r in receipt.values()),'Prior receipts not byte-exact/current/earned'
 out['receiptProvenance']={'path':str(prior_path.relative_to(ROOT)),'sha256':hashlib.sha256(prior_path.read_bytes()).hexdigest(),'sourceCompleted':True,'nativeRepairsEarned':6,'currentContentExact':True,'purpose':'Reuse genuine completed gates only for bounded shared-script/lesson rendering regression; no fabricated completion'}
 ev('(()=>{for(let[k,v]of Object.entries('+json.dumps(receipt,ensure_ascii=False)+'))sessionStorage.setItem(k,JSON.stringify(v));return true})()')
 call('browsingContext.reload',{'context':ctx,'wait':'none'});main_ready();wait('MuLERMoCScenario.ready&&!!fScenarioPresent()&&!MuLERMoCScenario.checkpointPreparation&&!document.documentElement.classList.contains("lesson-loading")',60)
 for index in [2,3,4,9,10,11,10,11]:
  ev('fScenarioGo('+str(index)+');true');wait('fScenarioPresent().index==='+str(index)+'&&!MuLERMoCScenario.checkpointPreparation')
  content_only=ev('document.getElementById("pageContainer").classList.contains("scContentOnly")')
  check(content_only==(index in [3,10]),'Lesson step'+str(index+1)+' expected content-only/molecule layout')
  if index in [2,4,9,11]:wait('!!document.querySelector("#jsmeNomeclatureSVG svg")')
  if index==11:expect_model('ethyl_3_dimethyl_2_5_hexane','Lesson final step12')
 for width,height in [(390,844),(1280,900)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});time.sleep(.5)
  check(ev('fScenarioPresent().index===11&&currentMolName.length>0&&!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Lesson resize preserves final molecule '+str(width))
 shot('shared-lesson12.png');ev('document.getElementById("nomeclature3D").scrollIntoView({block:"center",behavior:"instant"});true');time.sleep(.3);shot('shared-lesson12-3d.png')
 # Existing Workshop remains reachable; no new game integration into it.
 nav('games/name-repair.html');wait('!!document.getElementById("set-alkanes-start")',45);click('#set-alkanes-start');click('#set-alkanes-unbranched-start');wait('!!document.querySelector(".diagram-image.is-ready")',45)
 check(ev('Array.from(document.querySelectorAll("button")).some(b=>b.id.endsWith("check-button"))'),'Existing Workshop first exercise available')
 shot('shared-workshop.png');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['failureModel']=model()
 except Exception:pass
 try:shot('shared-regression-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'shared-regression.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
if not out['completed']:raise SystemExit(1)
