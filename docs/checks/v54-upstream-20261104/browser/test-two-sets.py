from pathlib import Path
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
GAME=json.loads(Path('games/data/name-repair-alkanes.json').read_text())
def picker():until('!!document.querySelector("#set-alkanes-unbranched-start")&&!!document.querySelector("#set-alkanes-branched-start")')
def ready():until('!!document.querySelector(".diagram-image.is-ready")')
def solve(r,touch=False):
 act=(lambda s:click(s,True))if touch else activate
 if r['kind']=='replace':
  act('#part-'+r['targetPartId']);i=next(i for i,c in enumerate(r['choices'])if c['value']==r['correctValue']);act('#choice-'+str(i))
 else:act('#part-ethylGroup');act('#move-left')
 check(ev('document.querySelector(".candidate-name").textContent')==r['correctName'],'Exact candidate '+r['id'])
 act('#check-button');until('!!document.querySelector(".feedback.is-success")')
 check(ev('document.querySelector(".success-explanation").textContent')==r['successText'],'Success explanation '+r['id'])
try:
 navigate('design/welcome-proposal.html?v=two-sets-test');call('browsingContext.activate',{'context':ctx});click('.card.two a.action');until('!!document.querySelector("#set-alkanes-start")');until('document.querySelector(".workshop-logo").naturalWidth>0')
 check(ev('document.querySelectorAll(".workshop-set-card").length===1'),'Workshop hub keeps one Alkanes family card')
 check(ev('document.querySelector(".workshop-set-meta").textContent.includes("2 σετ")&&document.querySelector(".workshop-set-meta").textContent.includes("3 κουίζ")'),'Family card states2sets and3quizzes each')
 check(ev('document.querySelector(".header-label").textContent')=='ΜΙΚΡΕΣ ΑΠΟΣΤΟΛΕΣ ΟΝΟΜΑΤΟΛΟΓΙΑΣ','Nomenclature header preserved')
 click('#set-alkanes-start');picker();check(ev('document.querySelectorAll(".workshop-set-card").length===2'),'Alkanes opens exactly two set cards')
 for w in [1500,768,550,390,320]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':w,'height':980},'devicePixelRatio':1})
  check(ev('document.documentElement.scrollWidth<=innerWidth'),'Two-set picker fits '+str(w))
  if w in [1500,390]:ev('scrollTo(0,0);true');screenshot_here('sets-'+str(w)+'.png')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 for si,setdata in enumerate(GAME['sets']):
  picker();activate('#set-'+setdata['id']+'-start');ready()
  check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".progress-dot")].map(n=>n.textContent))'))==['1','2','3'],'Exactly3progress dots '+setdata['id'])
  check(ev('document.querySelector(".round-set-name").textContent').find(setdata['title'])>=0,'Visible correct set identity '+setdata['id'])
  for ri,r in enumerate(setdata['rounds']):
   ready();check(ev('document.querySelector(".round-heading h1").textContent')==r['title'],'Correct question order '+r['id'])
   check(not ev('!!document.querySelector(".guided-pill")'),'No rehearsal '+r['id'])
   if ri==0:
    agree=next(p['id']for p in r['parts']if p['id']!=r.get('targetPartId'))
    activate('#part-'+agree);check(ev('document.querySelector(".part-selection-status").textContent')=='Αυτό το συνθετικό συμφωνεί με τη δομή.','Exact minimal feedback '+setdata['id'])
    activate('#part-'+r['targetPartId']);wrong=next(i for i,c in enumerate(r['choices'])if c['value']!=r['correctValue']);activate('#choice-'+str(wrong));activate('#check-button')
    check(not ev('!!document.querySelector(".feedback.is-success")'),'Wrong repair cannot pass '+setdata['id']);activate('.repair-actions .quiet')
   solve(r);check(ev('document.activeElement===document.querySelector(".round-next button")'),'Keyboard continuation focus '+r['id']);activate('.round-next button')
  until('!!document.querySelector(".results")')
  check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))'))==[3,4],'Independent3completed/4attempts summary '+setdata['id'])
  check(ev('document.querySelectorAll(".result-item").length===3&&!document.querySelector(".results").textContent.includes("Τέσσερα")'),'Exactly3results '+setdata['id'])
  screenshot_here('results-'+setdata['id']+'.png');activate('.results-actions .primary');picker()
 # New selection resets each set, never restores another set's completion.
 activate('#set-alkanes-unbranched-start');ready();check(ev('document.querySelector(".session-row").textContent').startswith('Προσπάθειες σε αυτή την αποστολή 0'),'Fresh linear set has zero effort')
 activate('#part-root');activate('.session-row button');until('!!document.querySelector(".confirm-dialog[open]")');activate('.confirm-dialog .secondary');until('!document.querySelector(".confirm-dialog")');check(ev('document.querySelector("#part-root").getAttribute("aria-pressed")==="true"'),'Return cancel preserves answer')
 activate('.session-row button');until('!!document.querySelector(".confirm-dialog[open]")');activate('.confirm-dialog .primary');picker()
 click('#workshop-all-sets');until('!!document.querySelector("#set-alkanes-start")');check(ev('document.querySelectorAll(".workshop-set-card").length===1'),'All sets returns generic hub')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});click('#set-alkanes-start',True);picker();click('#set-alkanes-unbranched-start',True);ready();solve(GAME['sets'][0]['rounds'][0],True);click('.round-next button',True);ready();check(ev('document.querySelector(".round-heading h1").textContent')==GAME['sets'][0]['rounds'][1]['title'],'Mobile set Continue reaches bond-typequiz')
 check(ev('document.documentElement.scrollWidth<=innerWidth'),'Mobile activequiz fits');screenshot_here('linear-bond-mobile.png');click('.session-row button',True);until('!!document.querySelector(".confirm-dialog[open]")');click('.confirm-dialog .primary',True);picker()
 # Decode standalone SVGs and independently measure final exported labels/frame.
 audit=json.loads(ev("""(async()=>{let rows=[];for(let name of ['ethane.svg','pentane.svg']){let im=new Image();im.src='assets/name-repair/'+name;await im.decode();let doc=new DOMParser().parseFromString(await(await fetch(im.src)).text(),'image/svg+xml');if(doc.querySelector('parsererror'))throw Error('badxml');let host=document.createElement('div');host.style.cssText='position:fixed;left:-10000px';let svg=document.importNode(doc.documentElement,true);host.append(svg);document.body.append(host);await document.fonts.ready;let frame=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text[data-namelecule-role="label"]')],fonts=labels.map(n=>{let m=n.getScreenCTM();return parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b)});let clipped=labels.some(n=>{let b=n.getBoundingClientRect();return b.left<frame.left||b.right>frame.right||b.top<frame.top||b.bottom>frame.bottom});rows.push({name,labels:labels.length,minFont:Math.min(...fonts),maxFont:Math.max(...fonts),clipped});host.remove()}return JSON.stringify(rows)})()"""))
 for row in audit:check(not row['clipped'] and abs(row['minFont']-22)<.02 and abs(row['maxFont']-22)<.02,'Actual newSVG decode/font/frame '+row['name'],row)
 out['assetAudit']=audit;out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('sets-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 (HERE/'two-sets-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
