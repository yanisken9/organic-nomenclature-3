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
 click('#molDraftSubmitBtn');until('!!window.MulerDraft&&MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone',seconds=40)
def load(n):
 ev('jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Authoring input","",""],Array.from({length:'+str(n)+'},(_,i)=>({el:"C",x:i*1.17,y:i%2?.45:0})),Array.from({length:'+str(n-1)+'},(_,i)=>[i+1,i+2,1])));true')
 until('fMolDraftReadDrawing().smiles==='+json.dumps('C'*n))
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=upstream54-drawing-'+str(time.time_ns()));app_ready();until('!!jsmeEditDraftApplet&&window.JSmolReadyFlag===true')
 call('browsingContext.activate',{'context':ctx})
 check(ev('document.querySelector("#originalJSMECheck").classList.contains("selectedCheck")') and visible('#newMolBtn') and visible('#editMolBtn'),'Teacher drawing default on exposes New/Edit')
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
 ev('window.__saveCalls=[];window.__saveSelectedOriginal=fMolDraftSaveSelected;fMolDraftSaveSelected=function(){__saveCalls.push({kind:"selected",selected:selectedMol,custom:!!nameExamplesCustom[selectedMol],draft:!!MulerDraft});return __saveSelectedOriginal.apply(this,arguments)};window.__singleOriginal=fMolDraftDownloadSingle;fMolDraftDownloadSingle=function(rec){__saveCalls.push({kind:"single",key:rec&&rec.key,hook:typeof fScenarioSaveBlobDownload});const result=__singleOriginal.apply(this,arguments);__saveCalls.push({kind:"singleResult",result});return result};true')
 click('#viewerSettingsBtn');until('document.querySelector("#viewerSettingsPanel").classList.contains("open")');ev('new Promise(r=>setTimeout(r,350))');ev('window.__saveEvents=[];["pointerdown","pointerup","click"].forEach(k=>document.addEventListener(k,e=>__saveEvents.push({type:k,id:e.target.id,tag:e.target.tagName,x:e.clientX,y:e.clientY}),true));true');out['saveButtonBefore']=read('({selected:selectedMol,customKeys:Object.keys(nameExamplesCustom),button:document.querySelector("#customMolSaveBtn").outerHTML})');click('#customMolSaveBtn')
 until('window.__downloads.length>=1',seconds=10)
 out['saveCalls']=read('__saveCalls');out['saveEvents']=read('__saveEvents')
 check(ev('__downloads[0].filename.startsWith("MULERMOC_")&&__downloads[0].text.includes("structure2D_Skeletal")'),'Manual Save delivers JS data payload')
 out['manualSave']=read('({filename:__downloads[0].filename,bytes:__downloads[0].text.length})')
 click('#viewerSettingsBtn')
 out['actualFixtureCalls']=read('__fixtureCalls');out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('manual-save-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 try:out['saveEvents']=read('window.__saveEvents||[]');out['saveCalls']=read('window.__saveCalls||[]');out['downloads']=read('({count:window.__downloads?.length,pending:typeof window.__downloadPending})')
 except Exception:pass
 out['diagnostics']=[e.get('params',{})for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in ['warn','error']]
 (HERE/'manual-save-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
