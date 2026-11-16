"""Hermetic preparation checks: no browser, network, app code or app storage writes."""
from pathlib import Path
import ast, datetime, hashlib, json, os, runpy, subprocess, sys, time
HERE=Path(__file__).resolve().parent
scope=runpy.run_path(str(HERE/'replay-levels.py'),run_name='prepared_harness')['load_functions'].__globals__
records=[]
def check(label,ok):
 assert ok,label
 records.append({'label':label,'passed':True})
source=(HERE/'replay-levels.py').read_text();ast.parse(source)
check('Runner parses and importing definitions starts no browser/profile/server',not any(k in scope for k in ['browser','server','profile','DEST','OUT']))
# No saved app data mutators or synthetic bridge messages occur in the runner.
all_student_sources=source+(HERE/'legacy-api-helpers.py').read_text()
check('No student progress or synthetic bridge injection; explicit author API checks are separate',all(token not in all_student_sources for token in ['sessionStorage.setItem','localStorage.setItem','dispatchEvent(','.postMessage(','.click()','NameleculeGameChoiceCheckpoint.restore']))
checks=HERE.parent/'builder-puzzle/handoff.json';manifest=json.loads(checks.read_text())
check('All4 Builder/Puzzle runtime files still match frozen handoff',all(hashlib.sha256((scope['ROOT']/p).read_bytes()).hexdigest()==v['sha256'] for p,v in manifest['paths'].items()))
env=dict(os.environ);env.pop('NAMELECULE_LEVELS_BROWSER_GRANT',None);env.pop('NAMELECULE_LEVELS_FROZEN_MANIFEST',None)
result=subprocess.run([sys.executable,'-B',str(HERE/'replay-levels.py'),'--mode','standalone-puzzle'],env=env,text=True,capture_output=True,timeout=10)
check('Missing explicit root browser/freeze grant rejects before browser startup',result.returncode!=0 and 'Root frozen-target AND exclusive browser-slot grant required' in result.stderr)
# Actual imported CDP transport cannot be kept alive with endless notifications.
scope['PROTOCOL_TIMEOUT']=.025;scope['RUN_DEADLINE']=time.monotonic()+2;scope['all_events']=[];scope['js_errors']=[]
scope['load_functions'](scope['RECORDED']/'replay-chrome.py',{'configure_connection','connect_target','cdp','ev','wait_document','call'},include_classes={'CDP'})
cdp=scope['CDP'].__new__(scope['CDP']);cdp.seq=0;cdp.send=lambda *args:None
cdp.receive=lambda:(time.sleep(.001) or {'method':'Network.responseReceived','params':{}})
start=time.monotonic()
try:cdp.call('Runtime.evaluate',{})
except TimeoutError:check('Actual CDP command deadline holds despite endless notifications',time.monotonic()-start<.3)
else:raise AssertionError('CDP failed deadline')
# Actual instrumented Firefox/BiDi transport has the same deadline property.
bidi=ast.parse(scope['bounded_bidi_source']((scope['ROOT']/'tools/namelecule_bidi.py').read_text()))
selected=[n for n in bidi.body if isinstance(n,ast.FunctionDef) and n.name in ['exact','call']]
exec(compile(ast.Module(body=selected,type_ignores=[]),'prepared-bidi-deadlines','exec'),scope)
payload=json.dumps({'method':'network.responseCompleted','params':{}}).encode();frame=bytes([129,len(payload)])+payload
class EventSocket:
 def __init__(self):self.buffer=b''
 def settimeout(self,v):assert v>0
 def sendall(self,*args):pass
 def recv(self,size):
  if not self.buffer:self.buffer=frame;time.sleep(.001)
  part=self.buffer[:size];self.buffer=self.buffer[size:];return part
scope['s']=EventSocket();scope['seq']=0;scope['all_events']=[];scope['js_errors']=[]
start=time.monotonic()
try:scope['call']('script.evaluate',{})
except TimeoutError:check('Actual BiDi command deadline holds despite endless valid event frames',time.monotonic()-start<.3)
else:raise AssertionError('BiDi failed deadline')
scope['RUN_DEADLINE']=time.monotonic()-.001
try:scope['check_deadline']()
except TimeoutError:check('Absolute process deadline bounds otherwise responsive commands',True)
else:raise AssertionError('Run deadline failed')
result={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Developer no-browser/no-network preparation checks','completed':True,'checks':len(records),'records':records,'harnessSHA256':hashlib.sha256(source.encode()).hexdigest(),'browserLaunched':False,'runtimeEdited':False}
(HERE/'prepared-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
