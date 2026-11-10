"""Actual pointer-selected calibration supplement. Original16 API-render measurements stay preserved."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
def dismiss_rotate():
 if ev('!!document.getElementById("rotatePrompt")&&getComputedStyle(document.getElementById("rotatePrompt")).display!=="none"'):pointer('#rotatePromptDismiss')
def panelshot(name):
 ev('document.getElementById("viewerCol").scrollIntoView({block:"center",behavior:"instant"});true');pause(250);r=read('(()=>{let r=document.getElementById("viewerCol").getBoundingClientRect();return{x:Math.max(0,r.x),y:Math.max(0,r.y),width:Math.min(innerWidth,r.right)-Math.max(0,r.x),height:Math.min(innerHeight,r.bottom)-Math.max(0,r.y)}})()');result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport','clip':{'type':'box',**r}});(HERE/(name+'.png')).write_bytes(base64.b64decode(result['data']));return r
try:
 out['scope']='Supplemental actual pointer molecule/Expanded selections, rotate-dismissal, exact source3D readiness, then actual3D toggle off and2D-panel-only screenshots. Original calibration16 and562audit are direct renderer API sweeps.';out['cases']=[]
 for version in [54,55]:
  for mol,width in [('dimethyl_2_3_butane',1500),('isopropyl_4_dimethyl_3_5_heptanol_2',1500),('isopropyl_ethanoate',390)]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});navigate('mulermoc-nom-'+str(version)+'.html?v=pointer-calibration-'+str(time.time_ns()));app_ready();wait('window.JSmolReadyFlag===true&&MuLERMoCScenario.ready===true',60);pointer('#'+mol);wait('selectedMol==='+json.dumps(mol));pointer('#radio2DMode .mode2DOption:nth-child(2)');wait('mode2D==="expanded"&&document.querySelector("#radio2DMode .mode2DOption:nth-child(2)").classList.contains("selectedRadio")')
   file=ev('nameExamples[selectedMol].file3D');expected=int((CR/file).read_text().splitlines()[3][:3]);wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length==='+str(expected)+'}catch(e){return false}})()',35);model=read('({file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length})');check(True,'Actual molecule3D eventuallymatches exactsource '+str(version)+' '+mol)
   if ev('document.getElementById("view3DBtn").classList.contains("active")'):pointer('#view3DBtn')
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':760 if width==390 else 1000},'devicePixelRatio':1});dismiss_rotate();wait('!document.getElementById("view3DBtn").classList.contains("active")');filename='pointer-calibration-v'+str(version)+'-'+mol+'-'+str(width);clip=panelshot(filename);check(ev('mode2D==="expanded"&&document.querySelector("#radio2DMode .mode2DOption:nth-child(2)").classList.contains("selectedRadio")') and not visible('#rotatePrompt'),'Visible pointerExpanded2Dpanel synced '+str(version)+' '+mol+' '+str(width));out['cases'].append({'version':version,'key':mol,'width':width,'expectedSourceAtoms':expected,'actual3D':model,'screenshot':filename+'.png','clip':clip,'3DhiddenAfterVerifiedModel':True})
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('pointer-calibration-failure')
 except Exception:pass
finally:finish('calibration-pointer-browser')
if not out['completed']:raise SystemExit(1)
