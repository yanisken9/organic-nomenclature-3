"""Focused Developer browser evidence; only the owned process.json Firefox profile.
No app state is fabricated. Bridge loads are observed to select genuine answer tiles;
trusted pointer actions complete both required triples through the production UI.
"""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
import hashlib
def lesson(index=3,version=55):
 open_page(f'mulermoc-nom-{version}.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&headerProbe=after-20261111-r1#step={index+1}');ready()
OUT.update({'layouts':[], 'heightSamples':[], 'limits':['Owned headless Firefox on macOS with localhost HTTP; no public deployment, personal Firefox, real touch screen, other browsers or conference/offline availability certification.','The focused representation smoke check covers two 2D modes and zoom; no broad chemistry or 3D retest is implied.']})
def visible_js():return '(e=>{let s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=="none"&&s.visibility!=="hidden"&&r.width>0&&r.height>0})'
def header(label,focused=False,screenshot=False):
 wait('!!document.querySelector(".nl-builder-logo")&&document.querySelector(".nl-builder-logo").complete&&document.querySelector(".nl-builder-logo").naturalWidth>0')
 data=read('''(()=>{let h=document.querySelector('.nl-builder-heading'),l=document.querySelector('.nl-builder-logo'),t=document.querySelector('.nl-builder-title'),host=document.querySelector('.nl-builder-host'),r=h.getBoundingClientRect(),lr=l.getBoundingClientRect(),hr=host.getBoundingClientRect(),s=getComputedStyle(h),d=document.getElementById('nlQuizDialog'),f=document.querySelector('.nl-builder-frame');return {label:'''+json.dumps(label)+''',viewport:{width:innerWidth,height:innerHeight},font:parseFloat(s.fontSize),align:s.textAlign,headingCount:[...document.querySelectorAll('.nl-builder-heading')].filter('''+visible_js()+''').length,logoCount:[...document.querySelectorAll('.nl-builder-logo')].filter('''+visible_js()+''').length,headingCenter:r.x+r.width/2,logoCenter:lr.x+lr.width/2,hostCenter:hr.x+hr.width/2,headingWidth:r.width,headingHeight:r.height,hostWidth:hr.width,logoWidth:lr.width,loaded:l.complete&&l.naturalWidth>0,logoSrc:l.currentSrc,decorative:l.alt===''&&l.getAttribute('aria-hidden')==='true',focusedHeading:document.activeElement===h,headingTabIndex:h.tabIndex,parentOverflow:document.documentElement.scrollWidth>innerWidth,dialogOverflow:d.scrollWidth>d.clientWidth,headerOverflow:t.scrollWidth>t.clientWidth,childOverflow:f.contentDocument.documentElement.scrollWidth>f.contentWindow.innerWidth,innerTitleVisible:[...f.contentDocument.querySelectorAll('.builder-title')].some('''+visible_js()+''')}})()''')
 OUT['layouts'].append(data)
 check(data['headingCount']==1 and data['logoCount']==1,label+' exactly one visible Builder title/logo',data)
 check(data['loaded'] and data['logoSrc'].endswith('/games/assets/name-builder/name-builder-logo-3d-blank-v1.png') and data['decorative'],label+' existing decorative asset loads',data['logoSrc'])
 check(data['font']>=28.7 and data['align']=='center' and abs(data['headingCenter']-data['hostCenter'])<1 and abs(data['logoCenter']-data['hostCenter'])<1,label+' large individually centered heading/logo',data)
 check(not any(data[k] for k in ['parentOverflow','dialogOverflow','headerOverflow','childOverflow']) and data['headingWidth']<=data['hostWidth'] and not data['innerTitleVisible'],label+' header/dialog/embedded page fit without duplicate title',data)
 if focused:check(data['focusedHeading'] and data['headingTabIndex']==-1,label+' retained same h2 focus target',data)
 if screenshot:
  ev('document.getElementById("nlQuizDialog").scrollTop=0;true');pause(.3);shot(label+'.png')
 return data

def stable_height(label):
 pause(.7);samples=[]
 for i in range(6):
  samples.append(read('({height:document.querySelector(".nl-builder-frame").getBoundingClientRect().height,body:document.querySelector(".nl-builder-frame").contentDocument.body.scrollHeight})'));pause(.2)
 OUT['heightSamples'].append({'label':label,'samples':samples})
 check(max(p['height'] for p in samples)-min(p['height'] for p in samples)<=1 and min(p['height'] for p in samples)>160,label+' iframe height settles',samples)

def feedback(label):
 pause(1)
 data=read('''(()=>{let f=document.querySelector('.nl-builder-frame'),n=f.contentDocument.getElementById('feedback'),r=n.getBoundingClientRect(),fr=f.getBoundingClientRect(),d=document.getElementById('nlQuizDialog'),dr=d.getBoundingClientRect(),hd=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect(),a=document.querySelector('.round-next').getBoundingClientRect();return{scrollTop:d.scrollTop,feedbackTop:fr.top+r.top,feedbackBottom:fr.top+r.bottom,dialogTop:dr.top,dialogBottom:dr.bottom,stickyBottom:hd.bottom,actionsTop:a.top,actionsBottom:a.bottom,success:n.classList.contains('success')}})()''')
 check(data['success'] and data['scrollTop']>0 and data['feedbackBottom']>max(data['dialogTop'],data['stickyBottom']) and data['feedbackTop']<data['dialogBottom'] and data['actionsTop']<data['dialogBottom'],label+' success feedback and next action revealed in dialog',data)
 shot(label+'-feedback.png')

def mobile_layouts(label):
 for w in [390,320]:
  viewport(w,760);pause(.8);header(label+'-'+str(w),screenshot=True);stable_height(label+'-'+str(w))
 viewport(1500,1000);pause(.7)

try:
 lesson(10);check(ev('fScenarioPresent().index')==3,'Locked direct step11 still starts at required gate4')
 open_gate();choose('builder');pause(.5);header('step4-desktop',focused=True,screenshot=True);stable_height('step4-desktop')
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'header-tab','actions':[{'type':'keyDown','value':'\ue004'},{'type':'keyUp','value':'\ue004'}]}]})
 check(ev('document.getElementById("nlQuizDialog").contains(document.activeElement)&&document.activeElement!==document.querySelector(".nl-builder-heading")'),'Keyboard Tab leaves focused heading within lesson dialog',ev('document.activeElement.tagName'))
 mobile_layouts('step4')
 # Two existing 2D modes and zoom; no 3D switch added by this header change.
 for mode in ['expanded','condensed']:
  bc('[data-representation='+json.dumps(mode)+']');wait(bel('[data-representation='+json.dumps(mode)+']')+'.getAttribute("aria-pressed")==="true"');check(bread('document.querySelector("#bank-tiles button")!==null'),'step4 '+mode+' remains interactive')
 bc('#zoom-in');bc('#zoom-out');check(bread('document.querySelector("#bank-tiles button")!==null'),'step4 zoom controls remain interactive')
 for index in [3,10]:
  if index==10:
   ev('location.hash="step=11";true');wait('fScenarioPresent().index===10');open_gate();choose('builder');pause(.5);header('step11-desktop',focused=True,screenshot=True);mobile_layouts('step11')
  molecules=[]
  for i in range(3):
   molecules.append(bsolve('Required Builder step'+str(index+1)+' round'+str(i+1),partial_refresh=(index==3 and i==0)))
   if i==0:header('step'+str(index+1)+'-after-refresh' if index==3 else 'step11-after-first');feedback('step'+str(index+1)+'-round1');stable_height('step'+str(index+1)+'-round1-complete')
   footer('step'+str(index+1)+'-round'+str(i+1),i==2)
   if i<2:
    check(not rec()['states'][str(index)]['solved'],'step'+str(index+1)+' still locked after '+str(i+1)+' successes')
    click('.round-next button');builder_ready();header('step'+str(index+1)+'-next'+str(i+2),focused=True)
  state=rec()['states'][str(index)]
  check(len(set(molecules))==3 and state['solved'] and state['earned']['game']=='builder','step'+str(index+1)+' genuine distinct Builder triple earns access',{'molecules':molecules,'earned':state['earned']})
  shot('step'+str(index+1)+'-triple-earned.png')
  if index==3:
   # Optional state and Workshop switch use real parent controls, preserving earned progress.
   earned=state['earned'];click('.round-next button:nth-child(2)');builder_ready();header('step4-optional',screenshot=True)
   check('Προαιρετική' in ev('document.getElementById("nlQuizDialogTitle").textContent'),'Optional practice keeps its own lesson heading')
   check(not ev('!!document.querySelector(".round-next button")'),'Unsolved optional round has no duplicate continuation footer')
   choose('repair');check(not ev('!!document.querySelector(".nl-builder-title")') and ev('!!document.querySelector(".diagram-image.is-ready")'),'Workshop switch renders existing Workshop without Builder brand')
   shot('step4-optional-workshop.png');choose('builder');header('step4-switch-back',focused=True,screenshot=True)
   check(rec()['states']['3']['earned']==earned,'Switch Workshop/back preserves exact earned access')
   click('#nlQuizPracticeContinue');wait('!document.getElementById("nlQuizDialog").open')
 # Main54 retains its own existing progress namespace and uses the same parent header pipeline.
 viewport(1500,1000);lesson(3,54);check(ev('fScenarioPresent().index')==3,'Main54 compatible gate4 loaded');open_gate();choose('builder');header('main54-step4',screenshot=True)
 # Standalone modes and old single-Workshop scenario remain unaffected by scoped parent styling.
 open_page('games/name-builder.html?molecule=butane');wait('!!document.querySelector("#bank-tiles button")',60)
 check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"&&document.querySelectorAll(".builder-title").length===1&&!document.querySelector(".nl-builder-title")'),'Standalone Builder keeps its original brand/header/next/mode');shot('standalone-builder-desktop.png')
 open_page('games/name-repair.html');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-builder-title")'),'Standalone Workshop remains outside Builder header scope');shot('standalone-workshop.png')
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")',60)
 check(not ev('!!document.querySelector(".nl-game-choice-card")||!!document.querySelector(".nl-builder-title")'),'Legacy Workshop-only checkpoint remains unchanged');shot('legacy-workshop-checkpoint.png')
 OUT['passed']=True
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('after-failure.png');raise
finally:
 OUT['browserSource']=read('({url:location.href,scripts:[...document.scripts].map(s=>s.src).filter(s=>s.includes("game-choice")),logoHTML:document.querySelector(".nl-builder-logo")?.outerHTML})');OUT['jsExceptions']=js_errors
 OUT['consoleEntries']=[e.get('params') for e in all_events if e.get('method')=='log.entryAdded']
 OUT['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['js/namelecule-game-choice-checkpoint.js','css/namelecule-quiz-checkpoints.css','mulermoc-nom-54.html','mulermoc-nom-55.html']}
 (HERE/'after-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
