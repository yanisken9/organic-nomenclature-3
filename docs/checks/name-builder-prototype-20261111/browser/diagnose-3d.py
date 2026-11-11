from pathlib import Path
exec((Path(__file__).parent/'driver.py').read_text(),globals())
out={'samples':[]}
try:
 open_page('games/name-builder.html');wait('document.querySelectorAll("#bank-tiles button").length>0')
 click('[data-representation="3d"]')
 for i in range(12):
  sample=read('(()=>{let w=document.querySelector("iframe").contentWindow;return w.eval(`(()=>{let live=fJSmolLive();return{host:NameleculeNameBuilderHost.snapshot(),live,modelInfo:live?Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo"):null,atoms:live?Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo","all"):null,bonds:live?Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all"):null,expectedAtoms:allAtomsTypeList3D,expectedBonds:bondList3D,file:nameExamples[selectedMol].file3D,base:document.baseURI,div3D:{style:document.getElementById("nomeclature3D").style.cssText,display:getComputedStyle(document.getElementById("nomeclature3D")).display,rect:document.getElementById("nomeclature3D").getBoundingClientRect().toJSON()},canvases:[...document.querySelectorAll("canvas")].map(c=>({w:c.width,h:c.height})),visibleText:document.body.innerText}})()`);})()')
  out['samples'].append(sample)
  print(json.dumps({'i':i,'live':sample['live'],'models':sample['modelInfo'],'expectedN':len(sample['expectedAtoms'] or []),'actualN':len(sample['atoms'] or []),'display':sample['div3D']['display'],'status':ev('document.querySelector("#game-status").textContent')},ensure_ascii=False)[:1800],flush=True)
  time.sleep(2)
 out['events']=read('__builderEvents.slice(-4)');shot('diagnose-3d.png')
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 out['javascriptErrors']=js_errors
 (HERE/'diagnose-3d.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');finish()
