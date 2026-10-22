import socket,base64,os,struct,json,time
from pathlib import Path
s=socket.create_connection(('127.0.0.1',9225),timeout=30)
s.settimeout(60)
key=base64.b64encode(os.urandom(16)).decode()
s.sendall(f'GET /session HTTP/1.1\r\nHost: 127.0.0.1:9225\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
b=b''
while b'\r\n\r\n' not in b:b+=s.recv(1)
assert b'101' in b,b
seq=0;js_errors=[]
def exact(n):
 b=b''
 while len(b)<n:
  part=s.recv(n-len(b))
  if not part:raise RuntimeError('WebSocket closed')
  b+=part
 return b
def call(method,params):
 global seq
 seq+=1;payload=json.dumps({'id':seq,'method':method,'params':params}).encode();mask=os.urandom(4);n=len(payload)
 header=bytes([129,128|n]) if n<126 else (bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n))
 s.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(payload)))
 while True:
  h=exact(2);n=h[1]&127
  if n==126:n=struct.unpack('!H',exact(2))[0]
  elif n==127:n=struct.unpack('!Q',exact(8))[0]
  msg=json.loads(exact(n))
  if msg.get('method')=='log.entryAdded':
   item=msg.get('params',{})
   if item.get('level')=='error' and item.get('type')=='javascript':js_errors.append(item)
  if msg.get('id')==seq:
   if msg.get('type')=='error':raise RuntimeError(msg)
   return msg['result']
call('session.new',{'capabilities':{}})
ctx=call('browsingContext.create',{'type':'tab'})['context']
call('session.subscribe',{'events':['log.entryAdded'],'contexts':[ctx]})
call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
def ev(expr):
 result=call('script.evaluate',{'expression':expr,'target':{'context':ctx},'awaitPromise':True})
 if result.get('type')=='exception':raise RuntimeError(result.get('exceptionDetails'))
 return result['result'].get('value')
def navigate(path):
 call('browsingContext.navigate',{'context':ctx,'url':os.environ.get('NAMELECULE_TEST_BASE_URL','http://127.0.0.1:8013/')+path,'wait':'complete'})
def until(expr,seconds=90):
 for _ in range(seconds*2):
  if ev(expr):return
  time.sleep(.5)
 raise AssertionError('Timed out: '+expr)
def app_ready():
 until("typeof jsmeNomeclatureApplet!=='undefined' && !!jsmeNomeclatureApplet && !!nameExamples.methyl_3_butene_1.classification")
def screenshot(path):
 result=call('browsingContext.captureScreenshot',{'context':ctx,'origin':'document'});Path(path).write_bytes(base64.b64decode(result['data']))
def check_methyl(expanded):
 r=json.loads(ev("JSON.stringify({name:nameComponentsList.filter(Boolean).join(''),g:fGetHydrocarbonBranchGroup(1),h:fGetHydrocarbonBranchHighlight(1),h3:fGetHydrocarbonBranchHighlight3D(1),types:allAtomsTypeList,selection:JmolSelection,chain:mainChainAtomsList})"))
 assert r['name']=='3-μεθυλο-1-πεντίνιο',r
 assert len([a for a in r['h']['atoms'] if r['types'][a-1]=='C'])==1,r
 if expanded:assert len([a for a in r['h']['atoms'] if r['types'][a-1]=='H'])==3,r
 assert r['h3']['atoms']==[3],r
 assert [a for a in r['h']['atoms'] if r['types'][a-1]=='C']==[6],r
 assert len(r['h3']['atoms'])==1 and [x['locant'] for x in r['g']['members']]==[3],r
 assert not any(a in r['chain'] for a in r['h']['atoms'] if r['types'][a-1]=='C'),r
 assert ev("!!document.querySelector('.ruleAlkyl [data-row=\"alkyl-μεθυλο\"].selected')")
 import re
 assert set(map(int,re.findall(r'atomno=(\d+)',r['selection'])))==set(r['h3']['atoms']),r
try:
 navigate('mulermoc-nom-49.html?v=methylpentyne-20261022');app_ready()
 until("window.JSmolReadyFlag===true")
 assert ev("Object.keys(nameExamples).length>=77 && !!nameExamples.methyl_3_pentyne_1.classification")
 ev("document.querySelector('[data-grouping-mode=series]').click()")
 assert ev("!!document.querySelector('[data-group-key=alkynes]').nextElementSibling.querySelector('#methyl_3_pentyne_1')")
 ev("document.querySelector('[data-group-key=alkynes]').click();document.getElementById('methyl_3_pentyne_1').click()")
 until("mainChainPool3DKey==='methyl_3_pentyne_1' && mainChainAtoms3D.length===5")
 until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))===16")
 ev("window.__bondPaint=[];window.__origBondPaint=jsmeNomeclatureApplet.setBondBackgroundColors.bind(jsmeNomeclatureApplet);jsmeNomeclatureApplet.setBondBackgroundColors=function(n,s){window.__bondPaint.push(s);return window.__origBondPaint(n,s);}")
 for chainMode in ['algorithmic','data']:
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   ev("mainChainMode='"+chainMode+"';mode2D='"+mode+"';fLoadMol2D();fShowNameAnalysis()")
   assert ev("nameComponentsList.filter(Boolean).join('')==='3-μεθυλο-1-πεντίνιο' && JSON.stringify(mainChainAtomsList).startsWith('[5,4,3,2,1')"),(chainMode,mode)
   for comp in ['comp4','comp6']:
    ev("window.__bondPaint=[];document.getElementById('"+comp+"').click()")
    assert ev("!!document.querySelector('[data-row=\"r2-triple\"].selected')"),(chainMode,mode,comp)
    assert ev("window.__bondPaint.some(s=>s==='4,9')"),(chainMode,mode,comp)
    assert ev("JmolSelection.includes('atomno=5') && JmolSelection.includes('atomno=6')"),(chainMode,mode,comp,ev('JmolSelection'))
   if mode=='skeletal':assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")
   for comp in ['comp0','comp1']:
    ev("document.getElementById('"+comp+"').click()");check_methyl(mode=='expanded')
 print('PASS alkynes menu,8form/chain modes,name/numbering/triple2D3D/rule/methyl atomsets+expandedH3,Jmol16atoms',flush=True)
 ev("mainChainMode='algorithmic';mode2D='condensed';fLoadMol2D();fShowNameAnalysis()")
 count=ev('mainChainPool.length')
 for _ in range(count):
  ev("nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('comp1').click()");check_methyl(False)
  ev('fStepMainChain(1)')
 print('PASS all',count,'equivalent parent chains and branch selections',flush=True)
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')["+str(i)+"].click()")
  assert ev('mode2D')==mode
  assert ev("nameComponentsList.filter(Boolean).join('')==='3-μεθυλο-1-πεντίνιο'")
  ev("nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('comp1').click()")
  time.sleep(.25)
  screenshot('/tmp/methylpentyne-'+mode+'.png')
 ev("document.getElementById('zigzagCheck').click()")
 assert ev("mode2D==='condensedZigZag' && nameComponentsList.filter(Boolean).join('')==='3-μεθυλο-1-πεντίνιο'")
 for key,name in [('methyl_3_butyne_1','3-μεθυλο-1-βουτίνιο'),('butyne_1','1-βουτίνιο'),('butyne_2','2-βουτίνιο'),('methyl_3_butene_1','3-μεθυλο-1-βουτένιο')]:
  ev("mode2D='condensed';selectedMol='"+key+"';fSelectMol()")
  assert ev("nameComponentsList.filter(Boolean).join('')=== '"+name+"'")
 assert not js_errors,js_errors
 print('PASS real form/CHn clicks and priorbutynes+branchedalkene; no JS errors',flush=True)
finally:
 call('session.end',{})
