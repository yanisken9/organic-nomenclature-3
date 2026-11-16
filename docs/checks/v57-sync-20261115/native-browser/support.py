"""Owned real Firefox Developer evidence, no personal browser interaction."""
from pathlib import Path
import os,json,time,traceback,base64,hashlib
HERE=Path(__file__).resolve().parent
OUT=HERE/os.environ['NAMELECULE_NATIVE_RUN_LABEL'];OUT.mkdir(exist_ok=True)
ROOT=Path.cwd();proc=json.loads((HERE/'process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=proc['base_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned57-bidi','exec'))
out={'completed':False,'checks':[],'role':'Developer actual isolated Firefox; not independent browser review','limits':['HeadlessFirefox/viewportemulation, not physicalmobile/Safari/conference/offline guarantee','Remoteunpinnedj2s/fonts/externalservices remain dependencies','Only task-owned headlessprofile, no personalFirefox operation']}
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr,seconds=40):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if ev(expr):return
        time.sleep(.1)
    raise AssertionError('Timeout '+expr)
def check(value,label,detail=None):
    assert value,(label,detail)
    out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def pause(ms=150):ev('new Promise(r=>setTimeout(()=>r(true),'+str(ms)+'))')
def pointer_at(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'native57-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def click(selector):
    ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(80)
    p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()')
    assert p['hit'] and not p['disabled'],(selector,p);pointer_at(p)
def key(value):call('input.performActions',{'context':ctx,'actions':[{'type':'key','id':'native57-key','actions':[{'type':'keyDown','value':value},{'type':'keyUp','value':value}]}]})
def shot(name):
    item=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(OUT/(name+'.png')).write_bytes(base64.b64decode(item['data']))
def finish(name):
    out['javascriptErrors']=js_errors
    out['diagnostics']=[e['params'] for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')in['error','warn']]
    try:call('browsingContext.close',{'context':ctx})
    finally:call('session.end',{})
    (OUT/(name+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'JSexceptions':len(js_errors),'failure':out.get('failure')}),flush=True)

out["inputSurfaceAtStart"]=read("({innerWidth,innerHeight,outerWidth,outerHeight,screenWidth:screen.width,screenHeight:screen.height})")
assert out["inputSurfaceAtStart"]["outerWidth"]>=out["inputSurfaceAtStart"]["innerWidth"] and out["inputSurfaceAtStart"]["outerHeight"]>=out["inputSurfaceAtStart"]["innerHeight"], "Headlessnativeinputsurface smallerthanoverriddenCSSviewport"
