from pathlib import Path
import os,json,time,traceback,base64,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;OUT=HERE/os.environ['NAMELECULE_DATA_RUN'];proc=json.loads((HERE/'process.json').read_text())
os.environ['NAMELECULE_BIDI_PORT']=str(proc['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=proc['base_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text().replace('s.settimeout(60)','s.settimeout(30)'),'owned-alkane-data-bidi','exec'))
out={'completed':False,'checks':[],'role':'Developer actual isolated Firefox; not independent browser review','limits':['Native headless Firefox; viewport emulation, not physical mobile or conference/offline qualification','JSmol remote j2s/fonts/services dependencies remain','Personal Firefox and user preview server untouched']}
def read(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def wait(expr,seconds=50):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if ev(expr):return
  time.sleep(.1)
 raise AssertionError('Timeout '+expr)
def check(value,label,detail=None):
 assert value,(label,detail);out['checks'].append({'label':label,'detail':detail});print('PASS '+label,flush=True)
def pause(ms=150):ev('new Promise(r=>setTimeout(()=>r(true),'+str(ms)+'))')
def shot(name):
 item=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'viewport'});(OUT/(name+'.png')).write_bytes(base64.b64decode(item['data']))
def finish(name):
 out['javascriptErrors']=js_errors;out['diagnostics']=[e['params']for e in all_events if e.get('method')=='log.entryAdded'and e.get('params',{}).get('level')in['error','warn']]
 try:call('browsingContext.close',{'context':ctx})
 finally:call('session.end',{})
 (OUT/(name+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'JSexceptions':len(js_errors),'failure':out.get('failure')}),flush=True)
out['inputSurfaceAtStart']=read('({innerWidth,innerHeight,outerWidth,outerHeight,screenWidth:screen.width,screenHeight:screen.height})');assert out['inputSurfaceAtStart']['outerWidth']>=1500 and out['inputSurfaceAtStart']['outerHeight']>=1000
def pointer_at(p):call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'alkane-data-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':round(p['x']),'y':round(p['y']),'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
def click(selector):
 ev('document.querySelector('+json.dumps(selector)+').scrollIntoView({block:"center",behavior:"instant"});true');pause(80)
 p=read('(()=>{const e=document.querySelector('+json.dumps(selector)+'),r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,h=document.elementFromPoint(x,y);return{x,y,hit:e===h||e.contains(h),disabled:!!e.disabled}})()');assert p['hit']and not p['disabled'],(selector,p);pointer_at(p)
def framing():
 return read('''(()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),r=s.getBoundingClientRect();let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity,count=0;for(const e of s.querySelectorAll('line,text,path')){if(e.closest('defs')||e.hasAttribute('data-hidden-carbon-h')||e.hasAttribute('data-muler-hidden'))continue;const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden'||Number(c.opacity)===0)continue;const b=e.getBoundingClientRect();if(!b.width&&!b.height)continue;left=Math.min(left,b.left);top=Math.min(top,b.top);right=Math.max(right,b.right);bottom=Math.max(bottom,b.bottom);count++;}return{viewport:{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height},drawing:{left,top,right,bottom},margins:{left:left-r.left,top:top-r.top,right:r.right-right,bottom:r.bottom-bottom},count,inside:count>0&&left>=r.left-.5&&top>=r.top-.5&&right<=r.right+.5&&bottom<=r.bottom+.5,centeringError:{x:(left+right-r.left-r.right)/2,y:(top+bottom-r.top-r.bottom)/2}}})()''')
