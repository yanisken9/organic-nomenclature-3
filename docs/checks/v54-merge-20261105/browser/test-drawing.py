"""Real JSME/renderer/JSmol/registry; declared recorded PubChem response fixtures."""
from pathlib import Path
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
out['fixturePolicy']='Actual PubChem REST responses stored locally; name/3D async transport replaced for repeatable authoring. Real JSME, engine, SVG, JSmol, registry and Blob payload.'
def read(s):return json.loads(ev('JSON.stringify('+s+')'))
def visible(s):return ev('(()=>{const n=document.querySelector('+json.dumps(s)+');return !!n&&getComputedStyle(n).display!=="none"&&!n.classList.contains("hide")})()')
def mode(m):
 i={'condensed':1,'expanded':2,'skeletal':3}[m]
 if ev('mode2D')!=m:click('.mode2DOption:nth-child('+str(i)+')')
 until('mode2D==='+json.dumps(m)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
def submit():
 click('#molDraftSubmitBtn')
 out.setdefault('submitSnapshots',[]).append(read('({draft:window.MulerDraft&&Object.fromEntries(Object.entries(MulerDraft).filter(([k,v])=>typeof v!=="object"&&typeof v!=="function"&&k!=="molText"&&k!=="sdf3D")),acquisition:!!window.MulerDraftAcquisition,toast:document.querySelector("#scenarioToast")?.textContent,drawing:fMolDraftReadDrawing().smiles})'))
 until('!!window.MulerDraft&&MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone',seconds=15)
def load(n):
 ev('jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Authoring input","",""],Array.from({length:'+str(n)+'},(_,i)=>({el:"C",x:i*1.17,y:i%2?.45:0})),Array.from({length:'+str(n-1)+'},(_,i)=>[i+1,i+2,1])));true')
 until('fMolDraftReadDrawing().smiles==='+json.dumps('C'*n))
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=upstream54-drawing-'+str(time.time_ns()));app_ready();until('!!jsmeEditDraftApplet&&window.JSmolReadyFlag===true')
 call('browsingContext.activate',{'context':ctx})
 check(ev('document.querySelector("#originalJSMECheck").classList.contains("selectedCheck")') and visible('#newMolBtn') and visible('#editMolBtn'),'Teacher drawing default on exposes New/Edit')
 check(ev('document.querySelector("#autoLinearizeCheck").classList.contains("selectedCheck")'),'Auto-linearize defaults ON')
 click('#viewerSettingsBtn');ev('new Promise(r=>setTimeout(r,350))');click('#autoLinearizeCheck');click('#viewerSettingsBtn')
 check(ev('document.querySelector("#autoLinearizeCheck").classList.contains("unselectedCheck")'),'Manual Linearize selectable with Auto OFF')
 records={}
 for name,folder in [('undecane',HERE),('nonane',Path('docs/checks/v54-sync-20261104')),('octane',Path('docs/checks/v54-sync-20261104/drafts'))]:
  p=json.loads((folder/(name+'-pubchem.json')).read_text())['PropertyTable']['Properties'][0]
  records[p['ConnectivitySMILES']]={'hit':{'source':'recorded-pubchem-fixture','cid':p['CID'],'iupac':p['IUPACName'],'iupacPubchem':p['IUPACName'],'title':p.get('Title',name),'systematic':p['IUPACName'],'canonicalSmiles':p['ConnectivitySMILES'],'synonyms':[]},'sdf':(folder/(name+'-3d.sdf')).read_text()}
 ev('window.__draftFixtures='+json.dumps(records)+';window.__no3D=false;window.__downloads=[];window.__fixtureCalls=[];'+r'''
 fFetchIUPAC_EN=async function(s){__fixtureCalls.push({kind:'name',s});await new Promise(r=>setTimeout(r,30));return JSON.parse(JSON.stringify(__draftFixtures[s]?.hit||{source:'none'}))};
 fFetchSDF3D_PubChem=async function(s){__fixtureCalls.push({kind:'3d',s});await new Promise(r=>setTimeout(r,30));return __no3D?null:(__draftFixtures[s]?.sdf||null)};
 fScenarioSaveBlobDownload=function(filename,blob){window.__downloadPending=blob.text().then(text=>__downloads.push({filename,text}));return true};
 window.__originalKeys=Object.keys(nameExamples);window.__originalRecords=JSON.stringify(Object.fromEntries(__originalKeys.map(k=>[k,nameExamples[k]])));window.__originalMOL2D=JSON.stringify(MOL2D);true''')
 click('#newMolBtn');until('!!window.MulerDraft');load(11)
 check(visible('#molDraftBeautifyBtn'),'Beautify available in editor')
 click('#molDraftBeautifyBtn')
 until('(()=>{const m=fParseMolV2000(fMolDraftReadDrawing().molText);return m&&m.atoms.length===11&&Math.max(...m.atoms.map(a=>a.y))-Math.min(...m.atoms.map(a=>a.y))<.001})()',seconds=10)
 row=read('(()=>{const m=fParseMolV2000(fMolDraftReadDrawing().molText);return {n:m.atoms.length,range:Math.max(...m.atoms.map(a=>a.y))-Math.min(...m.atoms.map(a=>a.y))}})()')
 check(row['n']==11 and row['range']<.001,'Real Beautify uses live11C horizontal chain',row)
 submit()
 check(not visible('#molDraftBeautifyBtn') and visible('#molDraftDrawBtn'),'Beautify hidden in submitted depict preview')
 check(ev('MulerDraft.engineName==="ενδεκάνιο"&&MulerDraft.engineEN==="undecane"'),'New C11 GR/EN actual prediction')
 until('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===35',seconds=35)
 check(True,'Real JSmol preview has C11H24 35atoms')
 click('#molDraftAcceptBtn');until('!window.MulerDraft&&selectedMol.startsWith("custom_")')
 ev('window.__customKey=selectedMol;window.__customRef=nameExamples[selectedMol];true')
 check(ev('Object.keys(nameExamples).length===142&&__downloads.length===0'),'Accept adds session molecule without automatic download')
 slots=read('(()=>{const r=nameExamples[__customKey],p=fParseMolV2000(r.structure2D_Skeletal);return {n:p.atoms.filter(a=>a.el==="C").length,range:Math.max(...p.atoms.map(a=>a.y))-Math.min(...p.atoms.map(a=>a.y)),bonds:p.bonds.length}})()')
 check(slots['n']==11 and slots['bonds']==10 and slots['range']>.1,'Accepted skeletal is generated zigzag',slots)
 for w,h in [(1500,1000),(844,390)]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':h},'devicePixelRatio':1})
  for m in ['condensed','expanded','skeletal']:
   mode(m);check(ev('currentMolName==="ενδεκάνιο"&&mainChainAtomsList.length===11&&!document.querySelector("#jsmeNomeclatureSVG").getAttribute("data-label-error")'),'Accepted '+m+' name/parent/drawing '+str(w))
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 mode('skeletal');click('#editMolBtn');until('!!window.MulerDraft');submit()
 check(not visible('#molDraftBeautifyBtn'),'Skeletal edit hides school-only Beautify')
 click('#molDraftAcceptBtn');until('!window.MulerDraft')
 check(ev('selectedMol===__customKey&&nameExamples[selectedMol]===__customRef&&Object.keys(nameExamples).length===142'),'Skeletal Update retains registry identity/key/count')
 check(ev('(()=>{const p=fParseMolV2000(nameExamples[__customKey].structure2D_Skeletal);return Math.max(...p.atoms.map(a=>a.y))-Math.min(...p.atoms.map(a=>a.y))>.1})()'),'Skeletal Update retains valid zigzag fixed point')
 click('#zoomInBtn');click('#zoomOutBtn');ev('document.querySelector("#nameAnalysis #comp5").click();true')
 until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===11')
 check(True,'Accepted skeletal zoom and11parentnumbers work');screenshot_here('accepted-undecane.png')
 # Different molecule from custom edit must fork; unavailable3D/stale states cannot accept.
 click('#editMolBtn');until('!!window.MulerDraft');load(9);ev('window.__no3D=true;true');submit()
 check(ev('!MulerDraft.sdf3D&&document.querySelector("#molDraftAcceptBtn").classList.contains("btnInactive")'),'No3D visibly prevents acceptance')
 ev('fMolDraftAccept();true');check(ev('!!MulerDraft&&Object.keys(nameExamples).length===142'),'No3D authoritative guard preserves draft and records')
 ev('window.__no3D=false;true');click('#molDraftDrawBtn');submit();click('#molDraftDrawBtn');load(8);ev('fMolDraftAccept();true')
 check(ev('!!MulerDraft&&MulerDraft.stale&&Object.keys(nameExamples).length===142'),'Stale accepted preview cannot create a record')
 submit();click('#molDraftAcceptBtn');until('!window.MulerDraft')
 check(ev('selectedMol!==__customKey&&Object.keys(nameExamples).length===143&&nameExamples[__customKey]===__customRef'),'Changed custom molecule forks and preserves prior record')
 out['originalRecordDifferences']=read('(()=>{const old=JSON.parse(__originalRecords),rows=[];for(const k of __originalKeys)for(const f of new Set([...Object.keys(old[k]),...Object.keys(nameExamples[k])]))if(JSON.stringify(old[k][f])!==JSON.stringify(nameExamples[k][f]))rows.push({molecule:k,field:f,before:old[k][f],after:nameExamples[k][f]});return rows})()')
 out['originalMOLDifferences']=read('(()=>{const old=JSON.parse(__originalMOL2D);return Object.keys(old).filter(k=>JSON.stringify(old[k])!==JSON.stringify(MOL2D[k]))})()')
 out['addedMOLKeys']=read('Object.keys(MOL2D).filter(k=>!Object.hasOwn(JSON.parse(__originalMOL2D),k))')
 check(not out['originalMOLDifferences'],'All original stored2D forms preserved')
 permitted={'systematicEN','iupacEN','iupacPubchem','titlePubchem','iupacFetchDone','iupacFetchError','engineEN','engineDelegated','needsHumanCheck','pubchemCID','iupacSource','canonicalSmiles'}
 check(all(r['field']in permitted and r['molecule']=='methane' and 'before'not in r for r in out['originalRecordDifferences']),'Original scientific records unchanged except named runtime lookup cache fields',out['originalRecordDifferences'])
 click('#viewerSettingsBtn');ev('new Promise(r=>setTimeout(r,350))');click('#customMolSaveBtn');until('window.__downloads.length===1')
 check(ev('__downloads[0].filename.startsWith("MULERMOC_")&&__downloads[0].text.includes("structure2D_Skeletal")'),'Manual Save delivers JS data payload')
 out['manualSave']=read('({filename:__downloads[0].filename,bytes:__downloads[0].text.length})')
 click('#viewerSettingsBtn')
 out['actualFixtureCalls']=read('__fixtureCalls');out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:
  out['failureState']=read('({draft:window.MulerDraft&&Object.fromEntries(Object.entries(MulerDraft).filter(([k,v])=>typeof v!=="object"&&typeof v!=="function"&&k!=="molText"&&k!=="sdf3D")),acquisition:!!window.MulerDraftAcquisition,toast:document.querySelector("#scenarioToast")?.textContent,drawing:fMolDraftReadDrawing().smiles})')
  print('FAILURE_STATE',json.dumps(out['failureState'],ensure_ascii=False),flush=True)
 except Exception:pass
 try:screenshot_here('drawing-failure.png')
 except Exception:pass
finally:
 out['consoleEntries']=[e.get('params',{}) for e in all_events if e.get('method')=='log.entryAdded']
 out['javascriptErrors']=js_errors
 (Path('docs/checks/v54-merge-20261105/browser')/'drawing-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
