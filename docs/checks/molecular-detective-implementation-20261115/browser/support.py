"""Owned-browser Developer evidence, separate from independent review."""
from pathlib import Path
import os, json, time, traceback, hashlib, base64
ROOT = Path.cwd()
OUT = Path(os.environ['DETECTIVE_TEST_OUT'])
exec(compile((ROOT / 'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)', 's.settimeout(30)'), 'owned-detective-bidi', 'exec'))
out = {'completed': False, 'checks': [], 'role': 'Developer actual headless Firefox, viewport emulation; not independent browser review', 'limits': ['No personal/GUI Firefox or physical device test', 'No offline/conference/uninterrupted-operation claim', 'External font/vendor dependencies retained']}
def read(expr): return json.loads(ev('JSON.stringify(' + expr + ')'))
def wait(expr, seconds=35):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if ev(expr): return
        time.sleep(.1)
    raise AssertionError('Timeout: ' + expr)
def check(value, label, detail=None):
    assert value, (label, detail)
    out['checks'].append({'label': label, 'detail': detail})
    print('PASS ' + label, flush=True)
def pause(ms=150): ev('new Promise(r=>setTimeout(()=>r(true),' + str(ms) + '))')
def pointer_at(x, y, touch=False):
    call('input.performActions', {'context': ctx, 'actions': [{'type': 'pointer', 'id': 'detective-touch' if touch else 'detective-pointer', 'parameters': {'pointerType': 'touch' if touch else 'mouse'}, 'actions': [{'type': 'pointerMove', 'x': round(x), 'y': round(y), 'duration': 0}, {'type': 'pointerDown', 'button': 0}, {'type': 'pointerUp', 'button': 0}]}]})
def click(selector):
    ev('document.querySelector(' + json.dumps(selector) + ').scrollIntoView({block:"center",behavior:"instant"});true')
    pause(70)
    p = read('(()=>{const e=document.querySelector(' + json.dumps(selector) + '),r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()')
    assert p['hit'] and not p['disabled'], (selector, p)
    pointer_at(p['x'], p['y'])
def key(value): call('input.performActions', {'context': ctx, 'actions': [{'type': 'key', 'id': 'detective-key', 'actions': [{'type': 'keyDown', 'value': value}, {'type': 'keyUp', 'value': value}]}]})
def shot(name):
    image = call('browsingContext.captureScreenshot', {'context': ctx, 'origin': 'viewport'})
    (OUT / (name + '.png')).write_bytes(base64.b64decode(image['data']))
def finish(name):
    out['javascriptErrors'] = js_errors
    out['diagnostics'] = [x['params'] for x in all_events if x.get('method') == 'log.entryAdded' and x.get('params', {}).get('level') in ['error', 'warn']]
    try: call('browsingContext.close', {'context': ctx})
    finally: call('session.end', {})
    (OUT / (name + '.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'completed': out['completed'], 'checks': len(out['checks']), 'JSerrors': len(js_errors), 'failure': out.get('failure')}), flush=True)
