from pathlib import Path
import json,time,traceback,os
os.environ['NAMELECULE_BIDI_PORT']='9246'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8055/'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
HERE=Path('docs/checks/alkanes-two-part-20261105/browser')
PILOT='mulermoc-nom-54.html?scenario=scenarios/alkanes-name-repair-pilot.scenario.json&present=1'
ROUND=json.loads(Path('scenarios/alkanes-name-repair-pilot.scenario.json').read_text())['steps'][9]['checkpoint']['round']
out={'completed':False,'checks':[]}
def check(ok,label,detail=None):
 assert ok,(label,detail)
 out['checks'].append({'label':label,'detail':detail});print('PASS',len(out['checks']),label,flush=True)
def click(selector,touch=False):
 for _ in range(12):
  ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});new Promise(r=>setTimeout(r,100))')
  p=json.loads(ev('JSON.stringify((()=>{let n=document.querySelector('+json.dumps(selector)+'),b=n.getBoundingClientRect(),h=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return{x:b.x+b.width/2,y:b.y+b.height/2,hit:n.contains(h),disabled:!!n.disabled,at:h&&h.outerHTML.slice(0,120)}})())'))
  if p['hit']:break
 assert p['hit'] and not p['disabled'],(selector,p)
 call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'touch'if touch else'mouse','parameters':{'pointerType':'touch'if touch else'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def key(value):
 call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'keyboard','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
def activate(selector):ev('document.querySelector('+json.dumps(selector)+').focus();true');key('\ue007')
def screenshot_here(name):screenshot(HERE/name)
def lesson_ready():
 app_ready();until('MuLERMoCScenario.present&&fScenarioPresent().steps.length===21');until('!document.documentElement.classList.contains("lesson-loading")');call('browsingContext.activate',{'context':ctx})
def open_quiz(touch=False):click('#nlQuizOpen',touch);until('!!document.querySelector("#nlQuizDialog[open] .diagram-image.is-ready")')
def part(id):return '[id$="-part-'+id+'"]'
def choice(i):return '[id$="-choice-'+str(i)+'"]'
def submit():return '[id$="-check-button"]'
def index():return ev('fScenarioPresent().index')
def state():return ev('JSON.stringify({mol:selectedMol,zoom:molZoom2D,numbering:numberingFlag,token:MuLERMoCScenario.applyToken,forms:document.querySelector("input[name=mol2d]:checked")?.id})')
def reload():call('browsingContext.reload',{'context':ctx,'wait':'complete'});lesson_ready()
