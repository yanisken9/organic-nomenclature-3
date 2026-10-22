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
def check_branch(slot,expanded,expected_name):
 r=json.loads(ev("JSON.stringify({name:nameComponentsList.filter(Boolean).join(''),group:fGetHydrocarbonBranchGroup(fHydrocarbonBranchSlot()),h:fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot()),h3:fGetHydrocarbonBranchHighlight3D(fHydrocarbonBranchSlot()),types:allAtomsTypeList,selection:JmolSelection})"))
 assert r['name']==expected_name,r
 assert len([a for a in r['h']['atoms'] if r['types'][a-1]=='C'])==2,r
 assert len(r['h3']['atoms'])==2,r
 if expanded:assert len([a for a in r['h']['atoms'] if r['types'][a-1]=='H'])==(5 if slot==1 else 6),r
 assert sorted(x['locant'] for x in r['group']['members'])==([3] if slot==1 else [2,5]),r
 import re
 assert set(map(int,re.findall(r'atomno=(\d+)',r['selection'])))==set(r['h3']['atoms']),r
 row='alkyl-αιθυλο' if slot==1 else 'alkyl-μεθυλο'
 assert ev("getComputedStyle(document.getElementById('ruleTheoryContainer')).display!=='none' && !!document.querySelector('.ruleAlkyl [data-row=\""+row+"\"].selected')")
try:
 navigate('mulermoc-nom-49.html?v=features');app_ready()
 until("window.JSmolReadyFlag===true")
 assert ev("Object.keys(nameExamples).length===73 && typeof fFitNameToWidth==='function' && typeof fFitNameComponents==='undefined'")
 for key,expected in [('ethyl_3_dimethyl_2_5_hexane','3-αιθυλο-2,5-διμεθυλοεξάνιο'),('ethyl_3_dimethyl_2_5_hexene_2','3-αιθυλο-2,5-διμεθυλο-2-εξένιο')]:
  ev("mainChainMode='algorithmic';selectedMol='"+key+"';fSelectMol()")
  until("mainChainPool3DKey==='"+key+"' && mainChainPool3D.length===4")
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   ev("mode2D='"+mode+"';fLoadMol2D();fShowNameAnalysis()")
   for comp,slot in [('comp0',1),('comp1',1),('comp2',2),('comp3',2)]:
    ev("document.getElementById('"+comp+"').click()")
    check_branch(slot,mode=='expanded',expected)
  ev("mode2D='condensed';fLoadMol2D();fShowNameAnalysis()")
  assert ev('mainChainPool.length')==4
  for i in range(4):
   for comp,slot in [('comp0',1),('comp2',2)]:
    ev("document.getElementById('"+comp+"').click()");check_branch(slot,False,expected)
   ev('fStepMainChain(1)');time.sleep(.2)
  print('PASS',key,':4forms/4parents,2D/3Dgroups and new branch-locant reference rules',flush=True)
 for key in ['hexen_1_yne_4','hexen_2_yne_4']:
  ev("selectedMol='"+key+"';fSelectMol()")
  for comp in ['comp7','comp8']:
   ev("document.getElementById('"+comp+"').click()")
   assert ev("document.getElementById('ruleTitle').textContent.includes('τύπου δεσμών') && !!document.querySelector('[data-row=\"r2-triple\"].selected') && !document.getElementById('ruleTheoryContainer').textContent.includes('undefined')"),(key,comp)
 assert ev("JSON.stringify(fGetNameComponentLocants('-2,5--3,4-'))==='[2,5,3,4]' && fGetNameComponentLocants(null).length===0")
 ev("fShowRule('unknown-test-rule')")
 assert ev("!document.getElementById('ruleTheoryContainer').textContent.includes('undefined')")
 print('PASS enyne type/locant tables and comma/hyphen parsing',flush=True)
 ev("selectedMol='ethyl_3_dimethyl_2_5_hexane';fSelectMol()")
 for boxed in [True,False]:
  for plus in [True,False]:
   for eyes in [True,False]:
    ev('nameBoxFlag='+str(boxed).lower()+';nameCrossFlag='+str(plus).lower()+';nameEyeEdit='+str(eyes).lower()+';fShowNameAnalysis()')
    time.sleep(.2)
    assert ev("(()=>{let p=document.getElementById('nameAnalysisContainer').getBoundingClientRect(),bs=[...document.querySelectorAll('.nameCompBox')].map(x=>x.getBoundingClientRect());return Math.min(...bs.map(x=>x.left))>=p.left && Math.max(...bs.map(x=>x.right))<=p.right+1 && Math.max(...bs.map(x=>x.top))-Math.min(...bs.map(x=>x.top))<1})()")
 ev("nameBoxFlag=true;nameCrossFlag=false;nameEyeEdit=false;fShowNameAnalysis();document.getElementById('analysisCol').style.setProperty('width','300px','important')")
 time.sleep(.4)
 assert ev("document.querySelector('.nameCompContainer').getBoundingClientRect().width<=document.querySelector('.nameContainer').clientWidth")
 ev("document.getElementById('analysisCol').style.setProperty('width','700px','important')")
 time.sleep(.4)
 assert ev("Number(document.querySelector('.nameCompContainer').style.getPropertyValue('--nl-name-scale'))===1")
 ev("document.getElementById('analysisCol').style.removeProperty('width')")
 screenshot('/tmp/v49-new-alkane.png')
 assert not js_errors,js_errors
 print('PASS single local fitter:8styles and narrow/wide panels, no Javascript errors',flush=True)
finally:
 call('session.end',{})
