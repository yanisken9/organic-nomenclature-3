from pathlib import Path
exec(compile(Path(__file__).with_name('support.py').read_text(),'native57-support','exec'))
def model_state():
    return read('(()=>{const m=window.fMuler3DModel;return{m:m?{id:m.id,source:m.source,revision:m.revision,completed:m.completed,parsed:m.parsed,liveValidated:m.liveValidated,picking:m.picking,pickCallback:m.pickCallback,keys:Object.keys(m)}:null,parsed:window.fMuler3DParsed?Object.keys(window.fMuler3DParsed):null,ready:typeof fMuler3DModelReady==="function"?fMuler3DModelReady():null,sel:window.MulerUserSelection,model:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo"),callbacks:window.__native57RawCallbacks}})()')
def point3d(atom):
    ev('document.querySelector("#nomeclature3D canvas").scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
    return read('(()=>{const v=jmolAppletNomeclature._applet.viewer,a=v.ms.at['+str(atom-1)+'],c=document.querySelector("#nomeclature3D canvas"),r=c.getBoundingClientRect(),g=v.gdata;const width=g.width||r.width*2,height=g.height||r.height*2;return{x:r.x+a.sX*r.width/width,y:r.y+a.sY*r.height/height,sX:a.sX,sY:a.sY,bufferWidth:width,bufferHeight:height,gkeys:Object.keys(g).filter(k=>/width|height|alias/i.test(k)),rect:{x:r.x,y:r.y,width:r.width,height:r.height}}})()')
try:
    call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH=true; }','contexts':[ctx]})
    navigate('mulermoc-nom-57.html?libs=cdn')
    app_ready();wait('window.JSmolReadyFlag===true',65)
    ev('selectedMol="ethanol";mode2D="expanded";modeSuffix="_2D_Expanded";fSelectMol();true')
    wait('typeof fMuler3DModelReady==="function"&&fMuler3DModelReady()',35)
    check(True,'Native57 model load/parsed/live ownership gate becomes ready',model_state())
    click('#selectAtomsBtn')
    wait('fMulerSelectState().active&&fMuler3DModel.picking')
    ev('window.__native57RawCallbacks=[];{const n=fMuler3DModel.pickCallback,f=window[n];window[n]=function(...args){window.__native57RawCallbacks.push(args.slice(0,3));return f.apply(this,args)}};true')
    point=point3d(1);out['point']=point;pointer_at(point)
    wait('fMulerSelectState().atoms3D.includes(1)',8)
    check(ev('fMulerSelectState().atoms2D.includes(3)'),'Genuine 3D oxygen click selects actual 2D oxygen3',model_state())
    pointer_at(point3d(1));wait('fMulerSelectState().atoms3D.length===0',8)
    check(ev('fMulerSelectState().atoms2D.length===0'),'Genuine 3D re-click clears both selections')
    out['finalModel']=model_state();shot('native57-first')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc()
    try:out['modelAtFailure']=model_state();shot('first57-failure')
    except Exception as extra:out['failureDiagnostic']=str(extra)
finally:finish('first57')
if not out['completed']:raise SystemExit(1)
