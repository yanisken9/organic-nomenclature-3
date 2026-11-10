"""Actual JSME Submit/Accept,55 slot/fork/saveall and3Dtier/manual lifecycle.
Network lookups/tier outcomes are declared fixtures; real engine/JSME/SVG/JSmol remain.
"""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
def load(n):
 ev('jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Authoring input","",""],Array.from({length:'+str(n)+'},(_,i)=>({el:"C",x:i*1.17,y:i%2?.45:0})),Array.from({length:'+str(n-1)+'},(_,i)=>[i+1,i+2,1])));true');wait('fMolDraftReadDrawing().smiles==='+json.dumps('C'*n))
def submit():
 pointer('#molDraftSubmitBtn');wait('!!MulerDraft&&MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone',30)
 out.setdefault('submissions',[]).append(read('({smiles:MulerDraft.smiles,source:MulerDraft.sdf3DSource,status:MulerDraft.sdf3DStatus,provenance:MulerDraft.sdf3DProvenance,has3D:!!MulerDraft.sdf3D,name:MulerDraft.engineName,en:MulerDraft.engineEN})'))
def mode(m):
 if ev('mode2D')!=m:pointer('#radio2DMode .mode2DOption:nth-child('+str({'condensed':1,'expanded':2,'skeletal':3}[m])+')')
 wait('mode2D==='+json.dumps(m)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
def cancel():pointer('#molDraftCancelBtn');wait('!window.MulerDraft&&!window.MulerDraftAcquisition')
def accept():pointer('#molDraftAcceptBtn');wait('!window.MulerDraft',25)
def confirm():wait('!!document.querySelector("#scenarioConfirm.show .scConfirmYes")');pointer('#scenarioConfirm.show .scConfirmYes')
try:
 navigate('mulermoc-nom-55.html?lang=gr&v=author55-'+str(time.time_ns()));app_ready();wait('!!jsmeEditDraftApplet&&window.JSmolReadyFlag===true',60);call('browsingContext.activate',{'context':ctx})
 records={}
 for name,folder in [('undecane',Path('docs/checks/v54-upstream-20261104/browser')),('nonane',Path('docs/checks/v54-sync-20261104')),('octane',Path('docs/checks/v54-sync-20261104/drafts'))]:
  p=json.loads((folder/(name+'-pubchem.json')).read_text())['PropertyTable']['Properties'][0];records[p['ConnectivitySMILES']]={'hit':{'source':'recorded-pubchem-fixture','cid':p['CID'],'iupac':p['IUPACName'],'iupacPubchem':p['IUPACName'],'title':p.get('Title',name),'systematic':p['IUPACName'],'canonicalSmiles':p['ConnectivitySMILES'],'synonyms':[]},'sdf':(folder/(name+'-3d.sdf')).read_text()}
 out['fixturePolicy']='Stored actual PubChem name/SDF responses; lookup transports and selected3Dtier outcomes controlled for repeatable authoring; source graph validation, actual JSME, engine, renderer, registry and JSmol kept live. Controlled delayed localtier opens the standard production wait overlay; STOP is recorded without issuing an engine command for that simulated run. No assertion of externalnetwork availability.'
 ev('window.__fixtures='+json.dumps(records)+';window.__tier="pubchem";window.__calls=[];window.__downloads=[];window.__manualDelay=2300;window.__realStop=fMolDraftMinStopEngine;window.__realRemote=fMolDraftRemote3DFromJSmol;window.__realLocal=fMolDraftLocal3DFromMol;'+r'''
 fFetchIUPAC_EN=async function(s){__calls.push({kind:'name',s});return __fixtures[s]?.hit||{source:'none'}};
 fFetchIUPAC_OC=async function(s){__calls.push({kind:'oc',s});return{source:'fixture-openclatura',name:__fixtures[s]?.hit.iupac||'fixture',opsin:'matched'}};
 fFetchSDF3D_PubChem=async function(s){__calls.push({kind:'pubchem',s});return __tier==='pubchem'?__fixtures[s]?.sdf:null};
 fMolDraftRemote3DFromJSmol=function(s,n,current){__calls.push({kind:'remote',s});return __tier==='remote'&&(!current||typeof current!=='function'||current())?__fixtures[s]?.sdf:null};
 fMolDraftLocal3DFromMol=async function(m,n,prepared,job,steps,further){__calls.push({kind:'local',n,steps,further,tier:__tier});let p=fParseMolV2000(m),c=p.atoms.filter(a=>a.el==='C').length;if(__tier==='realLocal')return __realLocal.apply(this,arguments);if(__tier==='manual'||__tier==='further-miss'){job.minimizing=true;fMolDraftMinWaitShow(()=>fMolDraftMinWaitAbort(job),fMolDraftMinWaitSecs(n),job);await new Promise(r=>setTimeout(r,__manualDelay));job.minimizing=false;}return __tier==='local'||__tier==='manual'?{sdf:__fixtures['C'.repeat(c)]?.sdf,prepared:true}:null};
 fMolDraftMinStopEngine=function(){__calls.push({kind:'stop-request',tier:__tier});if(__tier==='realLocal')return __realStop.apply(this,arguments);return true};
 fScenarioSaveBlobDownload=function(filename,blob){window.__downloadPending=blob.text().then(text=>__downloads.push({filename,text}));return true};
 window.__originalKeys=Object.keys(nameExamples);window.__originalMOL=JSON.stringify(MOL2D);true''')
 pointer('#newMolBtn');wait('!!MulerDraft');load(11);submit();check(ev('MulerDraft.engineName==="ενδεκάνιο"&&MulerDraft.engineEN==="undecane"&&MulerDraft.sdf3DSource==="pubchem"'),'RealC11 GR/EN prediction and graph-matched PubChem fixture accepted for preview')
 wait('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===35',35);check(True,'Real JSmol submittedC11 fixture preview has35atoms');check(ev('document.querySelector("#molDraftBar").textContent.includes("OpenClatura")||document.body.textContent.includes("OpenClatura")'),'OpenClatura independent oracle row visible in draft')
 accept();ev('window.__key=selectedMol;window.__ref=nameExamples[selectedMol];true');check(ev('Object.keys(nameExamples).length===142&&__downloads.length===0'),'New Accept creates one sessionrecord without automaticdownload')
 check(ev('["structure2D_Condensed","structure2D_Expanded","structure2D_Skeletal"].every(k=>typeof nameExamples[__key][k]==="string"&&nameExamples[__key][k].includes("V2000"))'),'New Accept generatedall3representation slots')
 # Disable supported auto-layout to keep deliberate same-identity redraw geometry.
 pointer('#viewerSettingsBtn');pause(250)
 if ev('document.querySelector("#autoLinearizeCheck").classList.contains("selectedCheck")'):pointer('#autoLinearizeCheck')
 pointer('#viewerSettingsBtn')
 out['slotUpdates']=[]
 for m,field in [('condensed','structure2D_Condensed'),('expanded','structure2D_Expanded'),('skeletal','structure2D_Skeletal')]:
  mode(m);ev('window.__beforeSlots=Object.fromEntries(["structure2D_Condensed","structure2D_Expanded","structure2D_Skeletal"].map(k=>[k,nameExamples[__key][k]]));true');pointer('#editMolBtn');wait('!!MulerDraft');ev('(()=>{const p=fParseMolV2000(fMolDraftReadDrawing().molText);p.atoms[0].x+=.18;jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Same identity redraw","",""],p.atoms,p.bonds));return true})()');submit();check(ev('fMolDraftIsSameMolecule()'),'Sameidentity '+m+' recognized');accept()
  result=read('({key:selectedMol,sameRef:nameExamples[__key]===__ref,count:Object.keys(nameExamples).length,changed:Object.keys(__beforeSlots).filter(k=>nameExamples[__key][k]!==__beforeSlots[k])})');out['slotUpdates'].append({'mode':m,'field':field,**result});check(result['key']==ev('__key') and result['sameRef'] and result['count']==142 and result['changed']==[field],'Sameidentity '+m+' update preserves siblings byteexactly',result)
 pointer('#editMolBtn');wait('!!MulerDraft');load(9);submit();pointer('#molDraftAcceptBtn');wait('!!document.querySelector("#scenarioConfirm.show")');check(ev('!!MulerDraft&&Object.keys(nameExamples).length===142'),'Editdifferent fork requires visibleconfirmation');confirm();wait('!MulerDraft',25);check(ev('selectedMol!==__key&&Object.keys(nameExamples).length===143&&nameExamples[__key]===__ref'),'Confirmed fork createsnew andpreservesoriginal')
 # Source2/3 tier behavior through actual new+submit, no record writes yet.
 for tier in ['remote','local','none']:
  ev('window.__tier='+json.dumps(tier)+';true');pointer('#newMolBtn');wait('!!MulerDraft');load(8);submit()
  if tier=='none':check(ev('!MulerDraft.sdf3D&&MulerDraft.sdfDone&&!!document.querySelector(".draftMinBtn")'),'Alltier misses visibly offermanualMinimize');ev('void fMolDraftAccept();true');check(ev('!!MulerDraft&&Object.keys(nameExamples).length===143'),'Alltier miss authoritativeAcceptguard')
  else:check(ev('MulerDraft.sdf3DSource==='+json.dumps('remote'if tier=='remote'else'jsmol-min')+'&&!!MulerDraft.sdf3D'),'ActualSubmit resolves '+tier+' controlledtier')
  if tier=='local':
   pointer('#molDraftAcceptBtn');wait('!!document.querySelector("#scenarioConfirm.show")');check(ev('MulerDraft.sdf3DStatus==="provisional"&&Object.keys(nameExamples).length===143'),'Local provisionalAcceptrequires explicitconfirmation');key('\ue00c');wait('!document.querySelector("#scenarioConfirm.show")');check(ev('!!MulerDraft&&Object.keys(nameExamples).length===143'),'Escape provisionalAcceptkeepsdraftuncommitted')
  if tier!='none':cancel()
 # Manual wait/countdown/ESC/Cancel and+100 use controlled delayed outcome, realUI/jobguards.
 ev('window.__tier="manual";true');pointer('.draftMinBtn');wait('!!document.querySelector("#molDraftMinWait.show")',10);first=ev('document.querySelector("#molDraftMinWait .scConfirmMsg").textContent');pause(1100);second=ev('document.querySelector("#molDraftMinWait .scConfirmMsg").textContent');check(first!=second,'Manualwait countdownprogresseswithpageclock',{'before':first,'after':second});pointer_at({'x':4,'y':4});check(ev('!!document.querySelector("#molDraftMinWait.show")&&MulerDraft._minimizing'),'Waitbackdrop doesnotcancel');key('\ue004');check(ev('document.activeElement.closest("#molDraftMinWait")!==null'),'Waitdialog trapsTab');key('\ue00c');wait('!document.querySelector("#molDraftMinWait")');pause(1500);check(ev('!!MulerDraft&&!MulerDraft.sdf3D&&!MulerDraft._minimizing'),'Manualwait Escape blocksstalecompletion')
 pointer('.draftMinBtn');wait('!!document.querySelector("#molDraftMinWait.show")');pointer('#molDraftMinWait .scConfirmCancel');pause(2500);check(ev('!!MulerDraft&&!MulerDraft.sdf3D&&!MulerDraft._minimizing'),'Manualwait Cancel blocksstalecompletion')
 pointer('.draftMinBtn');wait('!!document.querySelector("#molDraftMinWait.show")');wait('!document.querySelector("#molDraftMinWait")&&!!MulerDraft.sdf3D',15);check(ev('MulerDraft.sdf3DStatus==="provisional"&&!!MulerDraft.sdf3DProvenance&&!!document.querySelector(".draftMinBtn")&&document.querySelector(".draftMinBtn").textContent.includes("+"+MOLMIN_FURTHER_STEPS)&&!document.querySelector("#molDraftMinOK")'),'Manualcompleted storesmarkedprovisional3D andoffers+100 withoutremovedOKdialog');ev('window.__previous3D=MulerDraft.sdf3D;true')
 pointer('.draftMinBtn');wait('!!document.querySelector("#molDraftMinWait.show")');wait('!document.querySelector("#molDraftMinWait")&&!MulerDraft._minimizing',15);check(ev('MulerDraft.sdf3D===__previous3D&&__calls.some(c=>c.kind==="local"&&c.steps===MOLMIN_FURTHER_STEPS&&c.further===true)'),'Furtherround usescurrentconfiguredstepbudget andpreservesgraphmatchedfixture')
 ev('window.__tier="further-miss";true');pointer('.draftMinBtn');wait('!!document.querySelector("#molDraftMinWait.show")');wait('!document.querySelector("#molDraftMinWait")&&!MulerDraft._minimizing',15);check(ev('MulerDraft.sdf3D===__previous3D'),'Furtherinvalidresult retainslast3Dconformation')
 pointer('#molDraftAcceptBtn');wait('!!document.querySelector("#scenarioConfirm.show")');check(ev('Object.keys(nameExamples).length===143'),'Manualprovisionalmodel requiresexplicitAcceptconfirmation');confirm();wait('!MulerDraft',25);check(ev('Object.keys(nameExamples).length===144&&nameExamples[selectedMol].sdf3DStatus==="provisional"&&!!nameExamples[selectedMol].sdf3DProvenance'),'Manualprovisionalprovenance persistsinrecord');pointer('#molInfoBtn');check(ev('!!document.querySelector("#moleculeInfo [data-3d-status=provisional]")'),'Savedprovisionalstatus remainsvisibleinmoleculeinfo')
 pointer('#saveMolBtn');wait('__downloads.length===1');bundle=read('__downloads[0]');out['saveAll']={'filename':bundle['filename'],'bytes':len(bundle['text']),'sha256':hashlib.sha256(bundle['text'].encode()).hexdigest()};check(all(k in bundle['text'] for k in ['structure2D_Skeletal','sdf3DStatus','sdf3DProvenance']),'SaveAll bundleincludes3slots andprovisionalprovenance')
 ev('window.__importKeys=Object.keys(nameExamples).filter(k=>!__originalKeys.includes(k));window.__savedCustom=Object.fromEntries(__importKeys.map(k=>[k,JSON.stringify(nameExamples[k])]));__importKeys.forEach(k=>{delete nameExamples[k];if(window.nameExamplesCustom)delete nameExamplesCustom[k]});const script=document.createElement("script");script.textContent=__downloads[0].text;document.head.appendChild(script);script.remove();true');check(ev('__importKeys.every(k=>JSON.stringify(nameExamplesCustom[k])===__savedCustom[k])'),'Actual bundle script import restores allsessionrecords byteexactly withprovenance');ev('fClassifyAllMolecules();true');check(ev('__importKeys.every(k=>!!nameExamples[k]&&!!nameExamples[k].structure2D_Skeletal&&!!nameExamples[k].sdf3DProvenance)'),'Normal classificationmerges importedcustoms intoactivecatalog')
 check(ev('Object.keys(JSON.parse(__originalMOL)).every(k=>JSON.stringify(MOL2D[k])===JSON.stringify(JSON.parse(__originalMOL)[k]))'),'All141originalMOL2D storedformbytes preserved')
 out['fixtureCalls']=read('__calls');shot('authoring-final-provisional');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('authoring-failure');out['failureState']=read('({draft:window.MulerDraft&&{mode:MulerDraft.mode,smiles:MulerDraft.smiles,submitted:MulerDraft.submitted,submitting:MulerDraft.submitting,sdfDone:MulerDraft.sdfDone,source:MulerDraft.sdf3DSource,status:MulerDraft.sdf3DStatus,stale:MulerDraft.stale},toast:document.querySelector("#scenarioToast")?.textContent})')
 except Exception:pass
finally:finish('authoring-browser')
if not out['completed']:raise SystemExit(1)
