"""No browser/network: actual transports must time out despite endless events."""
from pathlib import Path
import ast, datetime, json, os, socket, struct, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
common=(HERE/'replay-detective.py').read_text()
tree=ast.parse(common)
definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['check_deadline','bounded_bidi_source']]
PROTOCOL_TIMEOUT=.03
RUN_DEADLINE=time.monotonic()+2
exec(compile(ast.Module(body=definitions,type_ignores=[]),'actual-bounded-test-helpers','exec'))
records=[]
def expected_timeout(label,action):
 start=time.monotonic()
 try: action()
 except TimeoutError:
  elapsed=time.monotonic()-start
  assert elapsed<.3,(label,elapsed)
  records.append({'label':label,'passed':True,'elapsedSeconds':elapsed});return
 raise AssertionError(label+' did not stop')

# CDP notifications keep arriving without a response to the requested id.
chrome=ast.parse((HERE/'replay-chrome.py').read_text())
exec(compile(ast.Module(body=[n for n in chrome.body if isinstance(n,ast.ClassDef) and n.name=='CDP'],type_ignores=[]),'actual-cdp-class','exec'))
all_events=[];js_errors=[]
cdp=CDP.__new__(CDP);cdp.seq=0;cdp.send=lambda *args:None
def notification():
 time.sleep(.001);return {'method':'Network.responseReceived','params':{}}
cdp.receive=notification
expected_timeout('CDP absolute command timeout despite continuous notifications',lambda:cdp.call('Runtime.evaluate',{}))

# BiDi receives complete valid event frames, never the command response.
bidi=ast.parse(bounded_bidi_source((ROOT/'tools/namelecule_bidi.py').read_text()))
exec(compile(ast.Module(body=[n for n in bidi.body if isinstance(n,ast.FunctionDef) and n.name in ['exact','call']],type_ignores=[]),'actual-instrumented-bidi-functions','exec'))
payload=json.dumps({'method':'network.responseCompleted','params':{}}).encode()
frame=bytes([129,len(payload)])+payload
class EventSocket:
 def __init__(self): self.buffer=b''
 def settimeout(self,value): assert value>0
 def sendall(self,*args): pass
 def recv(self,size):
  if not self.buffer:self.buffer=frame;time.sleep(.001)
  data=self.buffer[:size];self.buffer=self.buffer[size:];return data
s=EventSocket();seq=0;all_events=[];js_errors=[]
expected_timeout('BiDi absolute command timeout despite continuous event frames',lambda:call('script.evaluate',{}))

# The process deadline takes precedence even for otherwise responsive commands.
RUN_DEADLINE=time.monotonic()-.001
expected_timeout('Process deadline bounds the whole replay',lambda:check_deadline())
result={'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Developer transport memory tests; no browser/network','completed':True,'checks':len(records),'records':records}
(HERE/'deadline-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
