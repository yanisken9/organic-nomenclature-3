"""Natural entry position, without a screenshot-preparation scroll."""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
try:
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&headerProbe=natural-entry-20261111-r1#step=4');ready();open_gate();choose('builder');pause(.8)
 wait('document.querySelector(".nl-builder-logo").complete&&document.querySelector(".nl-builder-logo").naturalWidth>0')
 data=read('''(()=>{let h=document.querySelector('.nl-builder-heading').getBoundingClientRect(),l=document.querySelector('.nl-builder-logo').getBoundingClientRect(),d=document.getElementById('nlQuizDialog'),dr=d.getBoundingClientRect(),bar=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();return{scrollTop:d.scrollTop,headingTop:h.top,headingBottom:h.bottom,logoTop:l.top,logoBottom:l.bottom,stickyBottom:bar.bottom,dialogTop:dr.top,dialogBottom:dr.bottom,focused:document.activeElement===document.querySelector('.nl-builder-heading'),noScreenshotPreparationScroll:true}})()''')
 data['passed']=data['headingTop']>=data['stickyBottom'] and data['headingBottom']<=data['dialogBottom'] and data['logoTop']>=data['stickyBottom'] and data['logoBottom']<=data['dialogBottom'] and data['focused']
 data['jsExceptions']=js_errors
 shot('step4-natural-entry-desktop.png')
 (HERE/'natural-entry-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(data,ensure_ascii=False),flush=True)
 assert data['passed'],data
finally:finish()
