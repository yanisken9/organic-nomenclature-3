from pathlib import Path
exec(compile((Path(__file__).with_name('support.py')).read_text(), 'detective-support', 'exec'))
try:
    navigate('games/molecular-detective.html')
    wait('window.NameleculeMolecularDetective?.snapshot().phase==="active"')
    image=read('(()=>{const i=document.querySelector(".detective-logo"),r=i.getBoundingClientRect();return{src:i.currentSrc,loaded:i.complete,width:i.naturalWidth,height:i.naturalHeight,displayWidth:r.width,displayHeight:r.height}})()')
    check(image['loaded'] and image['width']==1254 and image['src'].endswith('molecular-detective-logo-molecule-v2.png'),'New molecule logo loaded in actual standalone game',image)
    check(image['displayWidth']==88 and image['displayHeight']==88,'Existing desktop logo size retained')
    shot('standalone-logo-v2')
    navigate('design/molecular-detective-preview.html')
    wait('document.querySelector(".preview-frame").contentWindow.NameleculeMolecularDetective?.snapshot().phase==="active"')
    check(ev('document.querySelector(".preview-frame").contentDocument.querySelector(".detective-logo").currentSrc.endsWith("molecular-detective-logo-molecule-v2.png")'),'Lesson-look preview uses same new logo')
    shot('lesson-look-logo-v2')
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(200)
    check(ev('document.documentElement.scrollWidth<=innerWidth+1&&document.querySelector(".preview-frame").contentDocument.documentElement.scrollWidth<=document.querySelector(".preview-frame").clientWidth+1'),'New logo mobile framing unchanged')
    check(not js_errors,'No captured JavaScript exceptions',js_errors)
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc()
finally:finish('logo')
if not out['completed']:raise SystemExit(1)
