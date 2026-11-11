from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={}
try:
 open_page('games/name-builder.html');wait('document.querySelectorAll("#bank-tiles button").length>0')
 ev('(()=>{let w=document.querySelector("iframe").contentWindow,original=w.Jmol.script;w.__scriptCalls=[];w.Jmol.script=function(a,c){let result=original(a,c);w.__scriptCalls.push({command:c,result:result??null});return result;};return true})()')
 click('[data-representation="3d"]');time.sleep(1)
 out['before']=read('(()=>{let w=document.querySelector("iframe").contentWindow;return w.eval(`({calls:__scriptCalls,selected:selectedMol,name:currentMolName,svg:!!document.querySelector("#jsmeNomeclatureSVG svg"),graph:NameleculeNameBuilderHost.modelReady(),host:NameleculeNameBuilderHost.snapshot(),camel:Jmol.evaluateVar(jmolAppletNomeclature,"nameBuilderRevision"),lower:Jmol.evaluateVar(jmolAppletNomeclature,"namebuilderrevision")})`)})()')
 out['asyncReturn']=ev('document.querySelector("iframe").contentWindow.eval(`Jmol.script(jmolAppletNomeclature,"namebuilderasync = 812;")`)')
 time.sleep(.6)
 out['afterAsync']=read('(()=>{let w=document.querySelector("iframe").contentWindow;return w.eval(`({value:Jmol.evaluateVar(jmolAppletNomeclature,"namebuilderasync"),calls:__scriptCalls,ready:jmolAppletNomeclature._ready})`)})()')
 out['camelWait']=read('(()=>{let w=document.querySelector("iframe").contentWindow;return w.eval(`({status:Jmol.scriptWait(jmolAppletNomeclature,"nameBuilderRevision = 99; print nameBuilderRevision;"),camel:Jmol.evaluateVar(jmolAppletNomeclature,"nameBuilderRevision"),lower:Jmol.evaluateVar(jmolAppletNomeclature,"namebuilderrevision")})`)})()')
 print(json.dumps(out,ensure_ascii=False),flush=True)
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 (HERE/'diagnose-queue.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
