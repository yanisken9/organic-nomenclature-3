"""Bounded verification of the exact reviewed files after installation in primary workspace."""
from pathlib import Path
import urllib.request
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned57-primary-support','exec'))
FROZEN=json.loads((HERE.parent/"verification-target.json").read_text());CR=Path(proc["candidateRoot"])
def visible(s):return ev("(()=>{const e=document.querySelector("+json.dumps(s)+");if(!e)return false;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return r.width>0&&r.height>0&&c.display!==\"none\"&&c.visibility!==\"hidden\"})()")
try:
    out['httpHashes']=[]
    for path,digest in FROZEN['files'].items():
        with urllib.request.urlopen(proc['base_url']+path+'?verify=primary57',timeout=12)as response:
            data=response.read();actual=hashlib.sha256(data).hexdigest();assert response.status==200 and actual==digest,(path,actual,digest)
            out['httpHashes'].append({'path':path,'status':response.status,'sha256':actual})
    check(CR.resolve()==ROOT.resolve(),'HTTP server serves actual primary workspace, not candidate',str(CR))
    check(len(out['httpHashes'])==17,'all17 installed files return exact reviewed HTTP bytes')
    navigate('design/welcome-proposal.html?v=local-sync57');wait('!!document.querySelector(".card.one .action")');call('browsingContext.activate',{'context':ctx})
    check(ev('document.querySelector(".explore-entry a").href.includes("mulermoc-nom-57.html")'),'welcome exploration route points to57')
    click('.card.one .action');wait('location.pathname.endsWith("theory-library.html")')
    links=read('[...document.querySelectorAll("a.action")].filter(a=>a.href.includes("scenario=")).map(a=>a.href)')
    check(len(links)==14 and all('mulermoc-nom-57.html?'in x for x in links),'all14 primary lesson routes point to57')
    click('.lesson:first-child .action');wait('typeof fScenarioPresent==="function"&&!!fScenarioPresent()?.steps?.length&&MuLERMoCScenario.present&&!document.documentElement.classList.contains("lesson-loading")',100)
    check(read('fScenarioPresent().index')==0 and read('fScenarioPresent().steps.length')==12,'actual welcome/library clicks start12-step alkane lesson')
    for idx in [1,2,3]:pause(850);click('#scNext');wait('fScenarioPresent().index==='+str(idx))
    check(ev('document.getElementById("scNext").disabled'),'cold primary gate4 stays locked')
    check(not visible('#viewerCol') and not visible('#analysisCol'),'primary gate4 retains molecule-free/name-free stop')
    click('#nlQuizOpen');wait('document.querySelectorAll(".nl-game-choice-card").length===3')
    check(read('document.querySelectorAll(".nl-game-choice-card").length')==3,'primary stop exposes exactly3 existing game choices')
    click('.nl-game-choice-card:nth-child(3)');wait('document.querySelector(".nl-puzzle-frame")?.contentDocument?.querySelector("#assembly-board[aria-busy=false]")',85)
    check(read('document.getElementById("nlQuizProgress").textContent')=='Κουίζ 1/3','actual primary Puzzle loads first counted molecule');shot('primary57-embedded-puzzle')
    navigate('mulermoc-nom-57.html?lang=en&mol=methyl_2_pentane&v=primary-native57');app_ready();wait('window.JSmolReadyFlag===true',60);call('browsingContext.activate',{'context':ctx});pause(600)
    check(visible('#selectAtomsBtn'),'primary native selection entry loads')
    for num,mode in [(2,'expanded'),(3,'skeletal'),(1,'condensed')]:
        click('#radio2DMode .mode2DOption:nth-child('+str(num)+')');wait('mode2D==='+json.dumps(mode)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")');pause(250)
        check(ev('mode2D==='+json.dumps(mode)),'actual primary representation control '+mode)
    click('#comp5');check(ev('nameAnalysisMode==="compCarbonsCount"'),'primary normal name highlight remains available')
    before=read('molZoom2D');click('#zoomInBtn');pause(200);check(read('molZoom2D')>before and ev('nameAnalysisMode==="compCarbonsCount"'),'actual zoom-in preserves highlighted component')
    click('#zoomOutBtn');pause(200);check(abs(read('molZoom2D')-before)<1e-8,'actual zoom-out restores initial scale')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(450);check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&nameAnalysisMode==="compCarbonsCount"'),'primary resize retains drawing and requested highlight');shot('primary57-phone')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});pause(300)
    ev('selectedMol="ethanol";mode2D="expanded";fSelectMol();true');wait('fMuler3DModelReady()',45);click('#selectAtomsBtn');wait('fMuler3DModel.picking');ev('document.querySelector(\"#nomeclature3D canvas\").scrollIntoView({block:\"center\",behavior:\"instant\"});true');pause(150)
    p=read('(()=>{const v=jmolAppletNomeclature._applet.viewer,a=v.ms.at[0],r=document.querySelector(\"#nomeclature3D canvas\").getBoundingClientRect();return{x:r.x+a.sX*r.width/v.gdata.width,y:r.y+a.sY*r.height/v.gdata.height}})()');pointer_at(p);pause(350)
    check(ev('fMulerSelectState().atoms3D.includes(1)&&fMulerSelectState().atoms2D.length===1'),'Installed57 actual3D atom click mirrors into2D')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:shot('primary57-failure')
    except Exception:pass
finally:finish('primary57-browser')
if not out['completed']:raise SystemExit(1)
