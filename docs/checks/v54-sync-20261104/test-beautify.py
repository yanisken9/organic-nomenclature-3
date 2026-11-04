from pathlib import Path
import json,time,traceback
exec(compile(Path('docs/checks/v54-sync-20261104/test-final-interactions.py').read_text().split('\ntry:\n',1)[0],'support','exec'))
out={'completed':False,'checks':[]}
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=beautify-'+str(time.time_ns()));app_ready();until('window.JSmolReadyFlag===true&&!!jsmeEditDraftApplet')
 if ev('document.getElementById("newMolBtn").classList.contains("hide")'):
  click('#viewerSettingsBtn');click('#originalJSMECheck');click('#viewerSettingsBtn')
 click('#newMolBtn');until('!!window.MulerDraft')
 click('#molDraftBeautifyBtn');check(ev('!!window.MulerDraft&&!window.MulerDraft.submitted'),'Beautify empty drawing keeps editable draft')
 ev('window.__beautifyInput=fWriteMolV2000(["Beautify probe","",""],Array.from({length:9},(_,i)=>({el:"C",x:i*1.17,y:i%2?0.45:0})),Array.from({length:8},(_,i)=>[i+1,i+2,1]));jsmeEditDraftApplet.readMolFile(window.__beautifyInput);true')
 until('fMolDraftReadDrawing().smiles==="CCCCCCCCC"')
 click('#molDraftBeautifyBtn')
 row=json.loads(ev('JSON.stringify((()=>{let d=fMolDraftReadDrawing(),p=fParseMolV2000(d.molText);return {smiles:d.smiles,atoms:p.atoms.length,bonds:p.bonds.length,carbonYs:p.atoms.filter(a=>a.el==="C").map(a=>a.y),chain:mainChainAtomsList,submitted:MulerDraft.submitted}})())'))
 check(row['smiles']=='CCCCCCCCC'and row['atoms']==9 and row['bonds']==8,'Real Beautify preserves nonane graph before firstSubmit',row)
 check(len(row['chain'])==9 and max(row['carbonYs'])-min(row['carbonYs'])<0.001,'Beautify builds live9C horizontal parent instead of template chain')
 click('#molDraftCancelBtn');until('!window.MulerDraft')
 check(ev('selectedMol==="methane"&&currentMolName==="μεθάνιο"&&Object.keys(nameExamples).length===141'),'Cancel restores original methane/library')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot(HERE/'beautify-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'beautify-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'errors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
