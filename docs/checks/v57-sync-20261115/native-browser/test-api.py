from pathlib import Path
exec(compile(Path(__file__).with_name('support.py').read_text(),'native57-support','exec'))
try:
    navigate('mulermoc-nom-56.html?libs=cdn')
    app_ready()
    wait('window.JSmolReadyFlag===true',65)
    ev('selectedMol="ethanol";mode2D="expanded";modeSuffix="_2D_Expanded";fSelectMol();true')
    wait('Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all").length===9',50)
    out['modelInfo']=read('Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo")')
    out['atomInfo']=read('Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all")')
    out['bondInfo']=read('Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all")')
    out['propertyList']=read('Object.keys(Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all")[0])')
    ev('window.__native57TailProbe=0; Jmol.script(jmolAppletNomeclature,\'javascript "window.__native57TailProbe=123";\');true')
    wait('window.__native57TailProbe===123',10)
    check(True,'Real JSmol javascript tail reaches owning page window')
    out['screenQuery']=read('(()=>{const q={};for(const expr of ["{atomno=1}.screenX","{atomno=1}.screenY","{atomno=1}.screenXYZ","{atomno=1}.xyz"]){try{q[expr]=Jmol.evaluateVar(jmolAppletNomeclature,expr)}catch(e){q[expr]=String(e)}}return q})()')
    out['internals']=read('(()=>{const a=jmolAppletNomeclature._applet,v=a?.vwr||a?.viewer;return{appletKeys:Object.keys(a||{}).slice(0,60),viewerKeys:Object.keys(v||{}).filter(k=>/^(ms|tm|sm|slm|am)$/.test(k)),atoms:v?.ms?.at?.slice(0,3).map(x=>({keys:Object.keys(x).filter(k=>/^(sX|sY|sZ|i|x|y|z|screen|atom)/.test(k)),sX:x.sX,sY:x.sY,sZ:x.sZ,i:x.i,x:x.x,y:x.y,z:x.z})),canvases:Array.from(document.querySelectorAll("#nomeclature3D canvas")).map(c=>({id:c.id,width:c.width,height:c.height,rect:(()=>{const r=c.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}})()}))}})()')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc()
finally:finish('api')
if not out['completed']:raise SystemExit(1)
