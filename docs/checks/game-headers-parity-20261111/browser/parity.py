"""Bounded Developer evidence: actual lesson UI in the newly owned headless Firefox.
Bridge loads are observed; native pointer input submits genuine game answers.
No fake progress, DOM style patches, image edits, personal-browser control or app writes.
"""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
import hashlib
OUT.update({'styles':[], 'naturalEntries':[], 'matchedShots':{},'limits':['Owned headless Firefox/macOS and local HTTP only; no personal GUI, public deployment, other browser, real touch or conference/offline guarantee.','Six genuine completions exercise required gate4 Builder and gate11 Workshop; this CSS-only unit does not repeat broad chemistry or 3D regression checks.','Paired screenshots preserve the games normal independent random seeds; the molecule can differ between games.']})
def lesson(index=3,version=55):
 open_page(f'mulermoc-nom-{version}.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&headerParity=20261111-r1#step={index+1}');ready()
def measure(game,label,natural=False,shotname=None):
 title='.nl-builder-heading' if game=='builder' else '.nl-game-choice-repair .round-heading h1'
 logo='.nl-builder-logo' if game=='builder' else '.nl-game-choice-repair .workshop-logo-small'
 host='.nl-builder-host' if game=='builder' else '.nl-game-choice-repair'
 wait('!!document.querySelector('+json.dumps(logo)+')&&document.querySelector('+json.dumps(logo)+').complete&&document.querySelector('+json.dumps(logo)+').naturalWidth>0')
 d=read('''(()=>{let h=document.querySelector('''+json.dumps(title)+'''),l=document.querySelector('''+json.dumps(logo)+'''),host=document.querySelector('''+json.dumps(host)+'''),s=getComputedStyle(h),r=h.getBoundingClientRect(),lr=l.getBoundingClientRect(),hr=host.getBoundingClientRect(),d=document.getElementById('nlQuizDialog'),dr=d.getBoundingClientRect(),bar=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect(),f=document.querySelector('.nl-builder-frame');let visible=e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'};return{game:'''+json.dumps(game)+''',label:'''+json.dumps(label)+''',width:innerWidth,height:innerHeight,fontFamily:s.fontFamily,fontSize:s.fontSize,fontWeight:s.fontWeight,lineHeight:s.lineHeight,letterSpacing:s.letterSpacing,textAlign:s.textAlign,headingText:h.textContent,headingCount:[...document.querySelectorAll('''+json.dumps(title)+''')].filter(visible).length,logoCount:[...document.querySelectorAll('''+json.dumps(logo)+''')].filter(visible).length,logoSrc:l.currentSrc,logoLoaded:l.naturalWidth>0,decorative:l.alt===''&&l.getAttribute('aria-hidden')==='true',logoWidth:lr.width,logoHeight:lr.height,logoCenter:lr.x+lr.width/2,headingCenter:r.x+r.width/2,hostCenter:hr.x+hr.width/2,headingTop:r.top,headingBottom:r.bottom,logoTop:lr.top,logoBottom:lr.bottom,stickyBottom:bar.bottom,dialogBottom:dr.bottom,scrollTop:d.scrollTop,focused:document.activeElement===h,tabIndex:h.tabIndex,parentOverflow:document.documentElement.scrollWidth>innerWidth,dialogOverflow:d.scrollWidth>d.clientWidth,headingOverflow:h.scrollWidth>h.clientWidth,childOverflow:f?f.contentDocument.documentElement.scrollWidth>f.contentWindow.innerWidth:false,caption:document.querySelector('.nl-game-choice-repair .round-game-label')?.textContent||null}})()''')
 OUT['styles'].append(d)
 expect=40 if d['width']==1500 else (28.8 if d['width']>760 else 28)
 check(d['fontFamily'].replace(chr(34),'')=='Roboto Condensed, sans-serif' and abs(float(d['fontSize'][:-2])-expect)<.05 and d['fontWeight']=='700' and abs(float(d['lineHeight'][:-2])-expect*1.12)<.05,label+' expected common title typography',d)
 check(d['headingCount']==1 and d['logoCount']==1 and d['logoLoaded'] and d['decorative'],label+' one loaded decorative title/logo',d)
 check(abs(d['headingCenter']-d['hostCenter'])<1 and abs(d['logoCenter']-d['hostCenter'])<1 and d['textAlign']=='center' and d['logoWidth']==(64 if d['width']<=650 else 88) and d['logoHeight']==d['logoWidth'] and d['logoBottom']<=d['headingTop'],label+' centered logo above centered heading',d)
 check(not any(d[k] for k in ['parentOverflow','dialogOverflow','headingOverflow','childOverflow']),label+' parent/dialog/header/embedded page fit',d)
 if game=='repair':check(d['caption']=='ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ',label+' existing Workshop caption retained',d['caption'])
 if natural:
  OUT['naturalEntries'].append(d)
  check(d['focused'] and d['tabIndex']==-1 and d['logoTop']>=d['stickyBottom'] and d['headingTop']>=d['stickyBottom'] and d['headingBottom']<=d['dialogBottom'],label+' natural entry and existing heading focus',d)
 if shotname:
  ev('document.getElementById("nlQuizDialog").scrollTop=0;true');pause(.3);shot(shotname)
 return d

def feedback(label,game):
 pause(.8)
 if game=='builder':expr='(()=>{let f=document.querySelector(".nl-builder-frame"),r=f.contentDocument.getElementById("feedback").getBoundingClientRect(),fr=f.getBoundingClientRect();return{top:r.top+fr.top,bottom:r.bottom+fr.top}})()'
 else:expr='(()=>{let r=document.querySelector(".feedback.is-success").getBoundingClientRect();return{top:r.top,bottom:r.bottom}})()'
 d=read('(()=>{let r='+expr+',d=document.getElementById("nlQuizDialog").getBoundingClientRect(),bar=document.querySelector(".nl-quiz-dialog-header").getBoundingClientRect(),a=document.querySelector(".round-next").getBoundingClientRect();return{top:r.top,bottom:r.bottom,stickyBottom:bar.bottom,dialogBottom:d.bottom,actionsTop:a.top,scrollTop:document.getElementById("nlQuizDialog").scrollTop}})()')
 check(d['bottom']>d['stickyBottom'] and d['top']<d['dialogBottom'] and d['actionsTop']<d['dialogBottom'],label+' success feedback and next action revealed',d)
 shot(label+'-feedback.png')
try:
 lesson();open_gate();choose('builder');pause(.6)
 measure('builder','Builder natural desktop',natural=True,shotname='builder-desktop.png');OUT['matchedShots']['builder']={'file':'builder-desktop.png','moleculeId':bread('__lessonLoad.moleculeId'),'viewport':[1500,1000]}
 for width in [768,760,650,390,320]:
  viewport(width,760 if width<768 else 1000);pause(.5);measure('builder','Builder '+str(width),shotname='builder-'+str(width)+'.png' if width in [390,320] else None)
 viewport(1500,1000);choose('repair');pause(.5);measure('repair','Workshop natural desktop',natural=True,shotname='workshop-desktop.png');OUT['matchedShots']['repair']={'file':'workshop-desktop.png','moleculeId':rround(3)['moleculeId'],'viewport':[1500,1000]}
 for width in [768,760,650,390,320]:
  viewport(width,760 if width<768 else 1000);pause(.5);measure('repair','Workshop '+str(width),shotname='workshop-'+str(width)+'.png' if width in [390,320] else None)
 for width in [1500,768,760,650,390,320]:
  pair=[d for d in OUT['styles'] if d['width']==width]
  keys=['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','textAlign']
  check(len(pair)==2 and all(pair[0][k]==pair[1][k] for k in keys),'Exact two-game computed typography parity at '+str(width),[{k:d[k] for k in keys} for d in pair])
 viewport(1500,1000);choose('builder');measure('builder','Builder return from Workshop',natural=True)
 ids=[]
 for i in range(3):
  ids.append(bsolve('Gate4 Builder '+str(i+1),partial_refresh=i==0));footer('Gate4 Builder '+str(i+1),i==2)
  if i==0:feedback('gate4-builder','builder');measure('builder','Builder after partial cold reload')
  if i<2:check(not rec()['states']['3']['solved'],'Gate4 remains locked after '+str(i+1)+' successes');click('.round-next button');builder_ready();measure('builder','Builder next '+str(i+2))
 earned=rec()['states']['3']['earned'];check(len(set(ids))==3 and earned['game']=='builder','Gate4 genuine Builder triple earns access',ids)
 click('.round-next button:nth-child(2)');builder_ready();measure('builder','Builder optional',shotname='builder-optional.png');check('Προαιρετική' in ev('document.getElementById("nlQuizDialogTitle").textContent'),'Optional practice heading retained')
 choose('repair');measure('repair','Workshop optional',shotname='workshop-optional.png');check(rec()['states']['3']['earned']==earned,'Optional switch preserves earned gate4');check(not ev('!!document.querySelector(".round-next button")'),'Unsolved optional has no duplicate footer')
 click('#nlQuizPracticeContinue');wait('!document.getElementById("nlQuizDialog").open');ev('location.hash="step=11";true');wait('fScenarioPresent().index===10');open_gate();choose('builder');measure('builder','Gate11 Builder',natural=True);choose('repair');measure('repair','Gate11 Workshop',natural=True,shotname='gate11-workshop-desktop.png')
 ids=[]
 for i in range(3):
  if i==1:
   saved=rec()['states']['10']['games']['repair'];call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');check(rec()['states']['10']['games']['repair']==saved,'Workshop partial progress survives cold reload');measure('repair','Workshop after cold reload')
  if i==2:viewport(390,760);measure('repair','Gate11 Workshop mobile390')
  ids.append(rsolve('Gate11 Workshop '+str(i+1),10)['moleculeId']);footer('Gate11 Workshop '+str(i+1),i==2)
  if i==2:feedback('gate11-workshop-mobile390','repair')
  if i<2:check(not rec()['states']['10']['solved'],'Gate11 remains locked after '+str(i+1)+' successes');click('.round-next button');wait('!!document.querySelector(".diagram-image.is-ready")')
 check(len(set(ids))==3 and rec()['states']['10']['earned']['game']=='repair','Gate11 genuine Workshop triple earns access',ids)
 viewport(1500,1000);lesson(3,54);check(ev('fScenarioPresent().index')==3,'Main54 own gate4 loaded');open_gate();choose('builder');measure('builder','Main54 Builder');choose('repair');measure('repair','Main54 Workshop')
 open_page('games/name-builder.html?molecule=butane&headerParity=20261111-r1');wait('!!document.querySelector("#bank-tiles button")',60);check(ev('!document.documentElement.classList.contains("lesson-mode")&&getComputedStyle(document.querySelector(".site-header")).display!=="none"&&!document.querySelector(".nl-game-choice-repair")&&getComputedStyle(document.getElementById("next-molecule")).display!=="none"'),'Standalone Builder original mode/header/next outside scoped styles')
 open_page('games/name-repair.html?headerParity=20261111-r1');wait('!!document.querySelector("#game-root")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Standalone Workshop outside scoped styles')
 open_page('mulermoc-nom-55.html?scenario=scenarios/alkanes-two-part-workshop.scenario.json&present=1&headerParity=20261111-r1#step=4');ready();open_gate();wait('!!document.querySelector(".diagram-image.is-ready")');check(not ev('!!document.querySelector(".nl-game-choice-repair")'),'Legacy Workshop checkpoint outside scoped parity styles');check(ev('getComputedStyle(document.querySelector(".workshop-logo-small")).width')=='36px','Legacy Workshop keeps prior 36px logo')
 OUT['passed']=True
except Exception as e:
 OUT['passed']=False;OUT['failure']=repr(e);OUT['traceback']=traceback.format_exc();shot('parity-failure.png');raise
finally:
 OUT['jsExceptions']=js_errors;OUT['consoleEntries']=[e.get('params') for e in all_events if e.get('method')=='log.entryAdded']
 OUT['sourceSHA256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['css/namelecule-quiz-checkpoints.css','mulermoc-nom-54.html','mulermoc-nom-55.html']}
 (HERE/'parity-results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n');finish()
