"""Developer evidence: delayed default response, real browser authoring APIs."""
from pathlib import Path
import os,json,time,hashlib,traceback
ROOT=Path.cwd();HERE=ROOT/'docs/checks/v54-sync-20261104/drafts'
os.environ['NAMELECULE_BIDI_PORT']='9246';os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
paths=json.loads((HERE/'baseline.json').read_text())
def hashes():return{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in paths}
out={'checks':[],'cases':[],'sourceHashesAtStart':hashes(),'fixturePolicy':'Only default-scenario fetch held, then released with exact local stored JSON. Authoring/capture/delete APIs remain real. No source writes.'}
fixture_path=ROOT/'scenarios/Αλκάνια-Αιθάνιο-τεστ.scenario.json'
fixture=json.loads(fixture_path.read_text())
out['fixtureSHA256']=hashlib.sha256(fixture_path.read_bytes()).hexdigest()
def read(expr):return json.loads(ev('(async()=>JSON.stringify(await ('+expr+')))()'))
def check(value,label):
 out['checks'].append({'label':label,'passed':bool(value)})
 print(label,bool(value),flush=True)
def snapshot():return read('({scenarios:MuLERMoCScenario.scenarios,active:MuLERMoCScenario.activeId,authoring:MuLERMoCScenario.authoring,opened:MuLERMoCScenario.authoringOpened,selected:selectedMol,mode:mode2D,records:Object.keys(nameExamples).length})')
def fresh():
 global ctx
 ctx=call('browsingContext.create',{'type':'tab'})['context']
 call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
def close():call('browsingContext.close',{'context':ctx})
try:
 navigate('mulermoc-nom-54.html?lang=gr&v=normal-preload-final-'+str(time.time_ns()));app_ready()
 until('MuLERMoCScenario.scenarios.some(s=>s.title==="Αλκάνια-Αιθάνιο-τεστ"&&s.steps.length===7)')
 normal=snapshot();out['normalStartup']=normal
 check(len(normal['scenarios'])==2 and sorted(len(s['steps'])for s in normal['scenarios'])==[0,7],'Normal startup imports seven steps and one empty card');close()
 wrapper=r'''()=>{const nativeFetch=window.fetch.bind(window);window.fetch=function(input,init){let u=String(input&&input.url||input);try{u=decodeURIComponent(u)}catch(e){}if(u.includes("Αλκάνια-Αιθάνιο-τεστ.scenario.json")){window.__defaultHeld=true;return new Promise(resolve=>{window.__releaseDefault=()=>{window.__defaultReleased=true;resolve(new Response(JSON.stringify(FIXTURE),{status:200,headers:{"Content-Type":"application/json"}}))}})}return nativeFetch(input,init)}}'''.replace('FIXTURE',json.dumps(fixture))
 for kind in ['new-captured-user-card','edit-original-card','delete-original-card','author-bar-opened-and-closed']:
  print('Delayed case',kind,flush=True)
  fresh();preload=call('script.addPreloadScript',{'contexts':[ctx],'functionDeclaration':wrapper})['script']
  navigate('mulermoc-nom-54.html?lang=gr&v=delayed-'+kind+'-'+str(time.time_ns()));app_ready()
  until('window.__defaultHeld&&MuLERMoCScenario.ready&&!!window.__releaseDefault')
  until('!!(jQuery._data(document,"events")||{}).click?.some(h=>h.selector===".menuLi")')
  ev('document.getElementById("propene").click();true')
  until('selectedMol==="propene"&&allAtomsTypeList.filter(t=>t==="C").length===3')
  if kind=='new-captured-user-card':
   ev('fScenarioSetAuthoring(true);fScenarioNew("delayed-user-authored",true);(()=>{let s=fScenarioCapture();if(!s)throw Error("capture not ready");fScenarioActive().steps.push(s)})();fScenarioSyncLegacy();fScenarioBuildPanels();fScenarioSetAuthoring(false);true')
  elif kind=='edit-original-card':
   ev('fScenarioActive().title="edited-original-during-fetch";(()=>{let s=fScenarioCapture();if(!s)throw Error("capture not ready");fScenarioActive().steps.push(s)})();fScenarioSyncLegacy();fScenarioBuildPanels();true')
  elif kind=='delete-original-card':
   ev('window.__deletedBootCard=fScenarioActive().id;fScenarioDelete(window.__deletedBootCard);true')
  else:ev('fScenarioSetAuthoring(true);fScenarioSetAuthoring(false);true')
  before=snapshot()
  ev('window.__releaseDefault();new Promise(r=>setTimeout(r,700))')
  after=snapshot()
  check(before==after,'Delayed default preserves exact state: '+kind)
  check(after['records']==141,'All 141 templates retained: '+kind)
  row={'case':kind,'before':before,'after':after,'loadedGuard':ev('fScenarioBoot.toString().includes("defaultPreloadSnapshot")'),'scriptURLs':read('[...document.scripts].map(s=>s.src).filter(Boolean)')}
  if kind=='new-captured-user-card':
   ev('window.__cancelWarningCalls=[];window.confirm=m=>{window.__cancelWarningCalls.push(m);return false};fMulerToggleLang("en");true')
   check(ev('window.__cancelWarningCalls.length')==1 and snapshot()==after,'Final scenario retains language Cancel safeguard')
  out['cases'].append(row)
  screenshot(HERE/('delayed-'+kind+'.png'))
  call('script.removePreloadScript',{'script':preload});close()
 out['completed']=True
except Exception as error:
 out['error']=str(error);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
 try:out['failureState']=snapshot();screenshot(HERE/'delayed-preload-failure.png')
 except Exception:pass
 try:close()
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;out['sourceHashesAtEnd']=hashes()
 out['sourcesUnchanged']=out['sourceHashesAtStart']==out['sourceHashesAtEnd']
 (HERE/'delayed-preload-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('session.end',{})
 print(json.dumps({'completed':out.get('completed',False),'checks':len(out['checks']),'failures':[x for x in out['checks']if not x['passed']],'javascriptErrors':len(js_errors)}),flush=True)
if not out.get('completed')or any(not x['passed']for x in out['checks']):raise SystemExit(1)
