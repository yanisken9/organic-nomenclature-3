"""Shared actual-UI helpers for the bounded ether verification."""
from pathlib import Path
import os,json,gzip,traceback
ROOT=Path.cwd();HERE=ROOT/'docs/checks/ether-uniform-20261031'
os.environ.setdefault('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8052/namelecule/')
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'bidi','exec'))
KEYS=json.loads((HERE/'baseline.json').read_text())['keys']
def select_ui(key,mode='expanded'):
    index=['condensed','expanded','skeletal'].index(mode)
    ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
    until('selectedMol==='+json.dumps(key)+'&&mode2D==='+json.dumps(mode))
    ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
    assert ev('[...document.querySelectorAll("#radio2DMode .mode2DOption")].findIndex(e=>e.classList.contains("selectedRadio"))')==index
def audit(width,phase):
    row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'))
    row.update(width=width,phase=phase)
    assert not row['clipped'] and not row['raster']['inkWithinHalfCssPixelOfBond'] and not row['raster']['fullyHiddenLineCount'],(row['key'],phase)
    return row
def start(path):
    navigate(path);app_ready();until('window.JSmolReadyFlag===true')
    ev('document.fonts.ready.then(()=>true)');ev((ROOT/'tools/2d-label-probe.js').read_text())
def save_result(out,name):
    out['javascriptErrors']=js_errors
    (HERE/name).write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0))
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':out['completed'],'cases':len(out.get('cases',[])),'jsErrors':len(js_errors)}),flush=True)
