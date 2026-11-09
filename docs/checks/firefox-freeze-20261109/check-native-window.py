"""Owned GUI Firefox control; native fullscreen is not the green hover popup."""
from pathlib import Path
import os,json,time,traceback
HERE=Path('docs/checks/firefox-freeze-20261109')
proc=json.loads((HERE/'native-window-process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port'])
result={'completed':False,'checks':[],'commands':[],'scope':'Own GUI profile, about:blank native fullscreen only. Does not exercise native green-button hover menu. No personal browser, app sources or settings changed.'}
def save(): (HERE/'native-window-control.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
try:
 helper=Path('tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(20)')
 helper=helper.replace('global seq\n seq+=1;', 'global seq\n print("COMMAND "+method,flush=True)\n seq+=1;')
 exec(compile(helper,'owned-gui-bidi','exec'))
 s.settimeout(20)
 native_call=call
 def call(method,params):
  start=time.monotonic();out=native_call(method,params)
  result['commands'].append({'method':method,'params':params,'elapsed_seconds':round(time.monotonic()-start,3)})
  save();return out
 windows=call('browser.getClientWindows',{})['clientWindows']
 assert len(windows)==1, 'Refuse ambiguous own-window selection'
 window=windows[0]['clientWindow'];result['initial_windows']=windows
 call('browsingContext.activate',{'context':ctx})
 ev('document.title="Namelecule — δοκιμή μεγέθυνσης"; document.body.textContent="Δοκιμαστικό παράθυρο Namelecule. Κενή σελίδα ελέγχου."; true')
 for cycle in range(3):
  for state in ['fullscreen','normal']:
   call('browser.setClientWindowState',{'clientWindow':window,'state':state})
   current=call('browser.getClientWindows',{})['clientWindows']
   assert any(w['clientWindow']==window and w['state']==state for w in current), current
   assert ev('20+22')==42
   result['checks'].append({'cycle':cycle+1,'state':state,'window_state':current,'page_roundtrip':True})
   save()
 result['completed']=True;result['javascript_errors']=js_errors;save()
 print(json.dumps({'completed':True,'checks':len(result['checks'])}),flush=True)
except Exception:
 result['exception']=traceback.format_exc();save();print(result['exception'],flush=True);raise
