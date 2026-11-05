"""Real browser Auto/async transaction/negative submission and GR-EN settings flows."""
from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
def read(s):return json.loads(ev('JSON.stringify('+s+')'))
def load(n):
 ev('jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Live drawing","",""],Array.from({length:'+str(n)+'},(_,i)=>({el:"C",x:i*1.17,y:i%2?.45:0})),Array.from({length:'+str(n-1)+'},(_,i)=>[i+1,i+2,1])));true')
 until('fMolDraftReadDrawing().smiles==='+json.dumps('C'*n)+'&&(()=>{let p=fParseMolV2000(fMolDraftReadDrawing().molText);return p&&p.atoms.length==='+str(n)+'})()')
def submit():click('#molDraftSubmitBtn');until('MulerDraft&&MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone',seconds=15)
try:
 navigate('mulermoc-nom-54.html?v=transaction-'+str(time.time_ns()));app_ready();until('!!jsmeEditDraftApplet&&JSmolReadyFlag===true');call('browsingContext.activate',{'context':ctx})
 fixtures=Path('docs/checks/v54-upstream-20261104/browser');sdf=(fixtures/'undecane-3d.sdf').read_text()
 ev('window.__txSDF='+json.dumps(sdf)+';window.__txNo3D=false;window.__txCalls=0;fFetchIUPAC_EN=async s=>{__txCalls++;return {source:"recorded-fixture",systematic:s.length===11?"undecane":"nonane",canonicalSmiles:s}};fFetchSDF3D_PubChem=async()=>__txNo3D?null:__txSDF;window.__txOriginalCount=Object.keys(nameExamples).length;true')
 ev("window.__txTrace=[];document.addEventListener('click',e=>__txTrace.push({phase:'click',id:e.target.id,tag:e.target.tagName}),true);window.__realTxSubmit=fMolDraftSubmit;fMolDraftSubmit=function(){__txTrace.push({phase:'submit-enter',keys:Object.keys(MulerDraft||{}),present:fMolDraftPresenting(),acquisition:!!window.MulerDraftAcquisition});let p=__realTxSubmit.apply(this,arguments);__txTrace.push({phase:'submit-sync-return',submitted:MulerDraft&&MulerDraft.submitted,submitting:MulerDraft&&MulerDraft.submitting});return p};window.__realTxTidy=fMolDraftAutoTidy;fMolDraftAutoTidy=function(){let r=__realTxTidy.apply(this,arguments);__txTrace.push({phase:'tidy',ok:!!r,toast:document.querySelector('#scenarioToast')?.textContent});return r};window.__realTxSandbox=fMolDraftSandboxAnalyse;fMolDraftSandboxAnalyse=function(){let r=__realTxSandbox.apply(this,arguments);__txTrace.push({phase:'sandbox',result:r});return r};true")
 click('#newMolBtn');until('!!MulerDraft');load(11)
 check(ev('!document.querySelector("#molDraftBeautifyBtn")||getComputedStyle(document.querySelector("#molDraftBeautifyBtn")).display==="none"'),'Auto ON hides manual Linearize')
 submit()
 check(ev('(()=>{const p=fParseMolV2000(MulerDraft.molText);return p&&Math.max(...p.atoms.map(a=>a.y))-Math.min(...p.atoms.map(a=>a.y))<.001})()'),'Auto ON linearizes actual Submit input')
 ev(r"""window.__txApp=jsmeNomeclatureApplet;window.__txOriginalMol=__txApp.molFile;window.__txOriginalRead=__txApp.readMolFile;window.__txOriginalGeneric=__txApp.readGenericMolecularInput;window.__txTimer=window.setTimeout;window.__txDelayed=false;
 __txApp.readGenericMolecularInput=function(s){const r=__txOriginalGeneric.call(this,s);if(window.MulerDraftAcquisition)__txDelayed=true;return r};
 __txApp.readMolFile=function(s){__txDelayed=false;return __txOriginalRead.call(this,s)};
 __txApp.molFile=function(){return __txDelayed?'injected truncated depiction':__txOriginalMol.call(this)};
 window.setTimeout=function(fn,ms){return __txTimer(fn,ms===120?600:ms)};true""")
 click('#molDraftAcceptBtn')
 check(ev('!!window.MulerDraftAcquisition&&MulerDraft.accepting'),'Real Accept enters asynchronous acquisition')
 before=read('({n:Object.keys(nameExamples).length,c:__txCalls,smiles:MulerDraft.smiles})')
 check(ev('["molDraftAcceptBtn","molDraftSubmitBtn","molDraftDrawBtn","molDraftBeautifyBtn"].every(id=>document.getElementById(id).disabled)'),'Conflicting controls disabled during acquisition')
 ev('void fMolDraftAccept();void fMolDraftSubmit();fMolDraftBackToEdit();fMolDraftBeautify();true')
 check(read('({n:Object.keys(nameExamples).length,c:__txCalls,smiles:MulerDraft.smiles})')==before,'Authoritative duplicate/Submit/Draw/Linearize guards preserve transaction')
 click('#molDraftCancelBtn');until('!window.MulerDraft&&!window.MulerDraftAcquisition')
 check(ev('Object.keys(nameExamples).length===__txOriginalCount'),'Cancel during delayed output creates no record')
 ev('window.setTimeout=__txTimer;__txApp.molFile=__txOriginalMol;__txApp.readMolFile=__txOriginalRead;__txApp.readGenericMolecularInput=__txOriginalGeneric;true')
 check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Cancelled transaction returns usable original viewer')
 ev('window.__txEvents=[];document.addEventListener("click",e=>{if(e.target.closest("#molDraftSubmitBtn"))__txEvents.push("submit-pointer")},true);window.__txNo3D=true;true')
 click('#newMolBtn');until('!!MulerDraft')
 for n in [9,11,9]:
  load(n);submit()
  check(ev('MulerDraft.sdfDone&&!MulerDraft.sdf3D&&!MulerDraft.submitting'),'Repeated settled no3D Submit completes '+str(n))
  ev('void fMolDraftAccept();true')
  check(ev('!!MulerDraft&&Object.keys(nameExamples).length===__txOriginalCount'),'No3D remains authoritatively blocked '+str(n))
  click('#molDraftDrawBtn')
 check(ev('__txEvents.length===3'),'All three submission pointer events delivered')
 click('#molDraftCancelBtn');until('!MulerDraft')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:
  out['trace']=read('window.__txTrace');print('TRACE',json.dumps(out['trace'],ensure_ascii=False),flush=True)
  out['failureState']=read('({draft:window.MulerDraft&&{variant:MulerDraft.variant,submitted:MulerDraft.submitted,submitting:MulerDraft.submitting,accepting:MulerDraft.accepting,cancelRequested:MulerDraft.cancelRequested},acquisition:!!window.MulerDraftAcquisition,toast:document.querySelector("#scenarioToast")?.textContent})')
  screenshot_here('transaction-failure.png')
 except Exception:pass
finally:
 try:ev('if(window.__txTimer)window.setTimeout=__txTimer;if(window.__txApp){__txApp.molFile=__txOriginalMol;__txApp.readMolFile=__txOriginalRead;__txApp.readGenericMolecularInput=__txOriginalGeneric}true')
 except Exception:pass
 try:out['trace']=read('window.__txTrace')
 except Exception:pass
 out['javascriptErrors']=js_errors
 Path('docs/checks/v54-merge-20261105/browser/transactions-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
