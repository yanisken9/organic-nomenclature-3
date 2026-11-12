from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
import hashlib
try:
 lesson();open_gate();choose('builder');pause(1)
 ev('document.querySelector(".nl-builder-heading").scrollIntoView({block:"start",behavior:"instant"});true');pause(.3)
 data=read('(()=>{let h=document.querySelector(".nl-builder-heading"),r=h.getBoundingClientRect(),s=getComputedStyle(h),f=document.querySelector(".nl-builder-frame");return {heading:h.textContent,headingFont:s.fontSize,textAlign:s.textAlign,headingRect:{x:r.x,y:r.y,width:r.width,height:r.height},logoCount:document.querySelectorAll(".nl-builder-logo").length,focusedHeading:document.activeElement===h,frameHeight:f.getBoundingClientRect().height,viewport:{width:innerWidth,height:innerHeight},step:fScenarioPresent().index+1}})()')
 data['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-game-choice-checkpoint.js','css/namelecule-quiz-checkpoints.css','mulermoc-nom-54.html','mulermoc-nom-55.html']}
 data['jsExceptions']=js_errors
 shot('before-step4-desktop.png')
 (HERE/'before-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(data,ensure_ascii=False),flush=True)
finally:finish()
