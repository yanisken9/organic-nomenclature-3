"""Developer Firefox journeys for hub → four missions → hub; actual keyboard/pointer/touch."""
from pathlib import Path
import json,time,traceback
support=Path('docs/checks/alkane-checkpoint-pilot-20261104/browser/test-pilot.py').read_text().split('\ntry:\n',1)[0].replace('disabled:n.disabled','disabled:!!n.disabled')
exec(compile(support,'support','exec'))
HERE=Path('docs/checks/workshop-hub-20261104/browser')
out={'completed':False,'checks':[]}
game=json.loads(Path('games/data/name-repair-alkanes.json').read_text())
def hub_ready():
 until('!!document.querySelector("#set-alkanes-start")');until('document.querySelector(".workshop-logo").naturalWidth>0')
def round_ready():until('!!document.querySelector(".diagram-image.is-ready")')
def solve(r,touch=False):
 if r['kind']=='replace':
  (lambda s:click(s,True) if touch else activate(s))('#part-'+r['targetPartId']);i=next(i for i,c in enumerate(r['choices']) if c['value']==r['correctValue']);(lambda s:click(s,True) if touch else activate(s))('#choice-'+str(i))
 else:
  activate('#part-ethylGroup');activate('#move-left')
 (lambda s:click(s,True) if touch else activate(s))('#check-button');until('!!document.querySelector(".feedback.is-success")')
 check(ev('document.querySelector(".success-explanation").textContent')==r['successText'],'Exact existing explanation '+r['id'])
try:
 navigate('design/welcome-proposal.html?v=workshop-hub-test');call('browsingContext.activate',{'context':ctx})
 check('Καθοδηγούμενο παράδειγμα' not in ev('document.querySelector(".card.two").textContent'),'Main welcome no longer advertises removed rehearsal')
 click('.card.two a.action');until('location.pathname.endsWith("/games/name-repair.html")');hub_ready()
 check(ev('document.querySelectorAll(".workshop-set-card").length===1&&document.querySelector("#set-alkanes-title").textContent==="Αλκάνια"'),'Main welcome opens hub with only first Alkanes card')
 check(ev('document.querySelector(".workshop-set-meta").textContent.includes("4 αποστολές")'),'Card states four missions')
 check(not ev('document.querySelector(".workshop-hub").textContent.includes("ΠΑΙΧΝΙΔΙ ΟΝΟΜΑΤΟΛΟΓΙΑΣ · ΑΛΚΑΝΙΑ")'),'Hub branding is general workshop')
 for width in [1500,768,550,390,320]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':980},'devicePixelRatio':1})
  check(ev('document.documentElement.scrollWidth<=innerWidth'),'Hub fits '+str(width))
  check(ev('(()=>{let l=document.querySelector(".workshop-logo").getBoundingClientRect(),t=document.querySelector(".workshop-title h1").getBoundingClientRect();return l.right<=t.left&&t.right<=innerWidth})()'),'Logo and title remain separate '+str(width))
  if width in [1500,390]:ev('scrollTo(0,0);true');screenshot_here('hub-'+str(width)+'.png')
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 activate('#set-alkanes-start');round_ready()
 check(ev('document.querySelector(".round-heading h1").textContent')==game['rounds'][0]['title'],'Card starts first actual challenge directly')
 check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".progress-dot")].map(n=>n.textContent))'))==['1','2','3','4'],'Four visible progress dots1–4 without rehearsal')
 check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".progress-label")].map(n=>n.textContent))'))==['Αποστολή 1 σε εξέλιξη','Αποστολή 2','Αποστολή 3','Αποστολή 4'],'Accessible progression labels1–4')
 check(not ev('!!document.querySelector(".guided-pill")'),'No guided round or label')
 # One incorrect attempt and retry prove effort accounting after round removal.
 activate('#part-ending');check(ev('document.querySelector(".part-selection-status").textContent')=='Αυτό το συνθετικό συμφωνεί με τη δομή.','Minimal agreeing-fragment feedback unchanged')
 activate('#part-root');activate('#choice-0');activate('#check-button')
 check(ev('document.querySelector(".feedback").textContent')==game['rounds'][0]['choices'][0]['feedback'],'Existing wrong-replacement feedback unchanged')
 activate('.repair-actions .quiet')
 for i,r in enumerate(game['rounds']):
  round_ready();check(ev('document.querySelector(".round-heading h1").textContent')==r['title'],'Correct round order '+str(i+1))
  solve(r)
  check(ev('document.querySelector(".success-name").textContent')==r['correctName'],'Exact repaired name '+r['id'])
  check(ev('document.activeElement===document.querySelector(".round-next button")'),'Keyboard focuses continuation '+r['id'])
  check(not ev('document.querySelector(".round-screen").textContent.includes("Χρειάζεσαι μια ιδέα;")'),'Hint card stays absent '+r['id'])
  activate('.round-next button')
 until('!!document.querySelector(".results")')
 check(json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))'))==[4,5],'All four missions count, one retry adds fifth submitted effort')
 check(ev('document.querySelectorAll(".results-list li").length===4'),'All four repairs appear in results')
 check(not ev('document.querySelector(".results").textContent.includes("καθοδηγούμενο")'),'Results omit obsolete rehearsal statement')
 screenshot_here('four-results-desktop.png')
 activate('.results-actions .primary');hub_ready();check(ev('document.activeElement===document.querySelector(".workshop-title h1")'),'Results return resets to hub and focuses heading')
 activate('#set-alkanes-start');round_ready();check(ev('document.querySelector(".session-row").textContent').strip().startswith('Προσπάθειες σε αυτή την αποστολή 0'),'New set starts with zero attempts')
 activate('#part-root');activate('.session-row button');until('!!document.querySelector(".confirm-dialog[open]")')
 activate('.confirm-dialog .secondary');until('!document.querySelector(".confirm-dialog")')
 check(ev('document.querySelector("#part-root").getAttribute("aria-pressed")==="true"'),'Cancelling hub return preserves answer selection')
 activate('.session-row button');until('!!document.querySelector(".confirm-dialog[open]")');activate('.confirm-dialog .primary');hub_ready()
 check(not ev('!!document.querySelector(".round-screen")||!!document.querySelector(".zoom-dialog")'),'Confirmed return clears active round and zoom UI')
 # Mobile mission and fresh retry, real simulated touch.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1})
 click('#set-alkanes-start',True);round_ready();check(ev('document.documentElement.scrollWidth<=innerWidth'),'Mobile first actual mission fits')
 solve(game['rounds'][0],True);screenshot_here('first-success-mobile.png');click('.round-next button',True);round_ready()
 check(ev('document.querySelector(".round-heading h1").textContent')==game['rounds'][1]['title'],'Mobile Continue reaches second mission')
 click('.session-row button',True);until('!!document.querySelector(".confirm-dialog[open]")');click('.confirm-dialog .primary',True);hub_ready()
 # SVG failure/recovery now targets the actual first (branched) molecule.
 ev('window.__failDiagram=true;const ds=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");Object.defineProperty(HTMLImageElement.prototype,"src",{...ds,set(value){ds.set.call(this,window.__failDiagram&&String(value).endsWith("methyl_2_pentane.svg")?"assets/name-repair/deliberate-missing.svg":value)}});true')
 click('#set-alkanes-start',True);until('document.querySelector(".image-status")?.textContent.includes("δεν εμφανίστηκε")')
 check(ev('document.querySelectorAll(".part-button:disabled").length===5&&document.querySelector("#check-button").disabled'),'Missing first SVG disables assessment')
 ev('window.__failDiagram=false;true');click('.image-status button',True);round_ready()
 check(ev('document.querySelectorAll(".part-button:disabled").length===0'),'Image retry recovers actual first molecule')
 click('.session-row button',True);hub_ready()
 # Header exits to main welcome, independent of hub reset.
 click('.exit-link',True);until('location.pathname.endsWith("/design/welcome-proposal.html")');check(True,'Header Exit returns to Namelecule welcome')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('hub-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors
 out['diagnostics']=[e for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in['warn','error']]
 (HERE/'hub-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
