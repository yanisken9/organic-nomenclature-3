"""Unfrozen diagnostic authorized by root: actual JSmol reload/readback timing, no production edits."""
from pathlib import Path
helper=(Path(__file__).resolve().parent/'support.py').read_text();helper=helper.replace("assert START_HASHES==FROZEN['files'],'Frozen17 source mismatch before runtime'",'None')
exec(compile(helper,'unfrozen-diagnostic-support','exec'))
out['scope']='Diagnostic only while unrelated Greek-name/IUPAC corrections land; no final frozen-target pass claimed. Name/3D PubChem fixtures supply graph-matched C8; actual reload/readback methods stay real.'
try:
 navigate('mulermoc-nom-55.html?lang=en&v=reload-readback-diagnostic-'+str(time.time_ns()));app_ready();wait('window.JSmolReadyFlag===true&&MuLERMoCScenario.ready===true&&!!jsmeEditDraftApplet',60);sdf=Path('docs/checks/v54-sync-20261104/drafts/octane-3d.sdf').read_text();ev('window.__sdf='+json.dumps(sdf)+';fFetchIUPAC_EN=async s=>({source:"fixture",iupac:"octane",systematic:"octane",canonicalSmiles:s});fFetchIUPAC_OC=async()=>({source:"fixture",name:"octane"});fFetchSDF3D_PubChem=async()=>__sdf;true');pointer('#newMolBtn');wait('!!MulerDraft');ev('jsmeEditDraftApplet.readMolFile(fWriteMolV2000(["Reload diagnosticC8","",""],Array.from({length:8},(_,i)=>({el:"C",x:i*1.17,y:i%2?.45:0})),Array.from({length:7},(_,i)=>[i+1,i+2,1])));true');wait('fMolDraftReadDrawing().smiles==="CCCCCCCC"');pointer('#molDraftSubmitBtn');wait('MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone&&!!MulerDraft.sdf3D',30);wait('Number(Jmol.evaluateVar(jmolAppletNomeclature,"{*}.count"))===26',30)
 ev(r'''window.__reloadTrace=[];window.__realEcho=fJSmolScriptEcho;window.__realValid=fMolDraftValidSDF3D;window.__realWill=fMolDraft3DWillScript;
 fJSmolScriptEcho=function(a,c){let r=__realEcho.apply(this,arguments);__reloadTrace.push({kind:'echo',command:c,time:Date.now(),text:r});return r};
 fMolDraftValidSDF3D=function(t,n,m){let r=__realValid.apply(this,arguments);__reloadTrace.push({kind:'valid',time:Date.now(),bytes:String(t||'').length,heavy:n,valid:r,input:!!m});return r};
 fMolDraft3DWillScript=function(a,c){let before=fMolDraft3DRevision,job=fMolDraft3DJob,own=fMolDraft3DWriter===job;let r=__realWill.apply(this,arguments);__reloadTrace.push({kind:'writer',time:Date.now(),command:String(c).slice(0,180),before,after:fMolDraft3DRevision,own,current:!!job&&fMolDraft3DCurrent(job)});return r};
 window.__initialEcho=fJSmolScriptEcho(jmolAppletNomeclature,'write MOL');window.__job=fMolDraft3DBegin();window.__immediateReload=fMolDraftLocal3DReloadMinimized(MulerDraft.sdf3D,MulerDraft.expectHeavy,__job);true''')
 out['immediateReload']=ev('__immediateReload');out['readbacks']=[]
 for ms in [0,100,400,1000]:
  if ms:pause(ms)
  row=read('(()=>{let text=fJSmolScriptEcho(jmolAppletNomeclature,"write MOL"),p=fParseMolV2000(text),ref=fParseMolV2000(MulerDraft.molText);return{time:Date.now(),current:fMolDraft3DCurrent(__job),revision:fMolDraft3DRevision,jobRevision:__job.revision,valid:fMolDraftValidSDF3D(text,MulerDraft.expectHeavy,MulerDraft.molText),parsed:!!p,atoms:p?.atoms?.length,heavy:p?.atoms?.filter(a=>a.el!=="H").length,graphMatched:!!p&&!!fMolDraftGraphMap(ref,p),text}})()');row['delayFromPreviousMs']=ms;out['readbacks'].append(row)
 out['trace']=read('__reloadTrace');out['submittedMol']=ev('MulerDraft.molText');out['initialEcho']=ev('__initialEcho');shot('reload-readback-diagnostic');out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['trace']=read('window.__reloadTrace||[]');shot('reload-readback-diagnostic-failure')
 except Exception:pass
finally:
 out['sourceHashesAtFinish']={p:hashlib.sha256((CR/p).read_bytes()).hexdigest()for p in SOURCE_PATHS};out['javascriptErrors']=js_errors;out['allConsoleEntries']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'];
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 (HERE/'reload-readback-diagnostic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':out['completed'],'immediateReload':out.get('immediateReload'),'readbacks':[{k:r.get(k)for k in ['delayFromPreviousMs','current','valid','parsed','atoms','heavy','graphMatched']}for r in out.get('readbacks',[])],'failure':out.get('failure')},ensure_ascii=False),flush=True)
