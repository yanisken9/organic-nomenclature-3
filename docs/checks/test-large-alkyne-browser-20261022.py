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
def clean_skeletal():
 assert ev("![...document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])')].some(e=>e.textContent.trim()==='C') && !document.querySelector('#jsmeNomeclatureSVG rect[rx]')")
 assert ev("(()=>{let d=new DOMParser().parseFromString(jsmeNomeclatureApplet.getMolecularAreaGraphicsString(),'text/html');const lines=e=>[...e.querySelectorAll('line')].map(l=>['x1','y1','x2','y2'].map(a=>l.getAttribute(a)));return JSON.stringify(lines(d))===JSON.stringify(lines(document.querySelector('#jsmeNomeclatureSVG svg')));})()")
def check_branch(slot,expanded):
 r=json.loads(ev("JSON.stringify({name:nameComponentsList.filter(Boolean).join(''),g:fGetHydrocarbonBranchGroup(fHydrocarbonBranchSlot()),h:fGetHydrocarbonBranchHighlight(fHydrocarbonBranchSlot()),h3:fGetHydrocarbonBranchHighlight3D(fHydrocarbonBranchSlot()),types:allAtomsTypeList,selection:JmolSelection,chain:mainChainAtomsList,chain3D:mainChainAtoms3D})"))
 assert r['name']=='4-αιθυλο-3,5-διμεθυλο-1-επτίνιο',r
 expected=[9,10] if slot==1 else [8,11]
 assert sorted(a for a in r['h']['atoms'] if r['types'][a-1]=='C')==expected,r
 assert sorted(r['h3']['atoms'])==expected,r
 if expanded:assert len([a for a in r['h']['atoms'] if r['types'][a-1]=='H'])==(5 if slot==1 else 6),r
 assert sorted(x['locant'] for x in r['g']['members'])==([4] if slot==1 else [3,5]),r
 assert not set(expected).intersection(r['chain']) and not set(expected).intersection(r['chain3D']),r
 import re
 assert set(map(int,re.findall(r'atomno=([0-9]+)',r['selection'])))==set(r['h3']['atoms']),r
 row='alkyl-αιθυλο' if slot==1 else 'alkyl-μεθυλο'
 assert ev("!!document.querySelector('.ruleAlkyl [data-row=\""+row+"\"].selected')")
try:
 navigate('mulermoc-nom-49.html?v=large-alkyne-20261022');app_ready()
 until("window.JSmolReadyFlag===true")
 assert ev("Object.keys(nameExamples).length>=79 && nameExamples.ethyl_4_dimethyl_3_5_heptyne_1.classification.seriesKey==='alkynes'")
 ev("document.querySelector('[data-grouping-mode=series]').click();document.querySelector('[data-group-key=alkynes]').click()")
 time.sleep(.45)
 ev("document.getElementById('ethyl_4_dimethyl_3_5_heptyne_1').scrollIntoView({block:'nearest'});document.getElementById('ethyl_4_dimethyl_3_5_heptyne_1').click()")
 until("mainChainPool3DKey==='ethyl_4_dimethyl_3_5_heptyne_1' && mainChainAtoms3D.length===7")
 until("Number(Jmol.evaluateVar(jmolAppletNomeclature,'{*}.count'))===31")
 ev("window.__bondPaint=[];window.__origBondPaint=jsmeNomeclatureApplet.setBondBackgroundColors.bind(jsmeNomeclatureApplet);jsmeNomeclatureApplet.setBondBackgroundColors=function(n,s){window.__bondPaint.push(s);return window.__origBondPaint(n,s);}")
 for chain_mode in ['algorithmic','data']:
  for mode in ['condensed','expanded','skeletal','condensedZigZag']:
   ev("mainChainMode='"+chain_mode+"';mode2D='"+mode+"';fLoadMol2D();fShowNameAnalysis()")
   assert ev("nameComponentsList.filter(Boolean).join('')==='4-αιθυλο-3,5-διμεθυλο-1-επτίνιο' && JSON.stringify(mainChainAtomsList)==='[1,2,3,4,5,6,7]' && JSON.stringify(mainChainAtoms3D)==='[1,2,3,4,5,6,7]'")
   for comp in ['comp4','comp6']:
    ev("nameAnalysisMode='none';fShowNameAnalysis();window.__bondPaint=[];document.getElementById('"+comp+"').click()")
    assert ev("!!document.querySelector('[data-row=\"r2-triple\"].selected') && window.__bondPaint.some(s=>s==='1,9') && JmolSelection.includes('atomno=1') && JmolSelection.includes('atomno=2')"),(mode,comp)
   for comp,slot in [('comp0',1),('comp1',1),('comp2',2),('comp3',2)]:
    ev("nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('"+comp+"').click()");check_branch(slot,mode=='expanded')
   if mode=='skeletal':clean_skeletal()
  print('PASS',chain_mode,':4forms,parent7,ethylat4/C2H5,methyls3,5/C2H6,tripleat1,2D3D exact sets',flush=True)
 ev("mainChainMode='algorithmic';mode2D='skeletal';fLoadMol2D();nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('comp5').click();clearInterval(myNumberingTimeout);document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').forEach(e=>e.remove());currNumberEl=0;fShowNumbering(0)")
 assert ev("mainChainPool.length===1 && mainChainPool3D.length===1 && document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===7")
 clean_skeletal()
 # Complete name fits the panel at the default, narrow and wide widths.
 for width in ['300px','700px','']:
  ev("document.getElementById('analysisCol').style.setProperty('width','"+width+"','important');fFitNameToWidth()") if width else ev("document.getElementById('analysisCol').style.removeProperty('width');fFitNameToWidth()")
  time.sleep(.2)
  assert ev("document.querySelector('.nameCompContainer').getBoundingClientRect().width<=document.querySelector('.nameContainer').clientWidth+1"),width
 # Actual UI clicks keep explicit C/H in expanded and CHn, then hide C again.
 for i,mode in enumerate(['condensed','expanded','skeletal']):
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')["+str(i)+"].click();nameAnalysisMode='none';fShowNameAnalysis();document.getElementById('comp1').click()")
  time.sleep(.25)
  assert ev('mode2D')==mode
  if mode=='skeletal':clean_skeletal()
  screenshot('/tmp/large-alkyne-'+mode+'.png')
 ev("document.getElementById('zigzagCheck').click()")
 assert ev("mode2D==='condensedZigZag' && document.querySelectorAll('#jsmeNomeclatureSVG text:not([id^=number])').length>=11")
 ev("document.getElementById('zigzagCheck').click()")
 clean_skeletal()
 ev("window.__exportSvg=null;window.__png=null;window.__download=null;window.__makeURL=URL.createObjectURL.bind(URL);URL.createObjectURL=function(blob){if(blob.type.startsWith('image/svg'))blob.text().then(s=>window.__exportSvg=s);if(blob.type==='image/png')window.__png=blob;return window.__makeURL(blob);};HTMLAnchorElement.prototype.click=function(){window.__download=this.download;};fSave2DPng()")
 until("!!window.__png && !!window.__exportSvg && !!window.__download",20)
 assert ev("window.__png.size>1000 && ![...new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelectorAll('text')].some(e=>e.textContent.trim()==='C')")
 print('PASS numbering7,namefit300/700/default,actual forms/CHn,skeletal noC,PNG export',flush=True)
 for key,name in [('methyl_4_pentyne_2','4-μεθυλο-2-πεντίνιο'),('methyl_3_pentyne_1','3-μεθυλο-1-πεντίνιο'),('ethyl_3_dimethyl_2_5_hexene_2','3-αιθυλο-2,5-διμεθυλο-2-εξένιο'),('ethyl_3_dimethyl_2_5_hexane','3-αιθυλο-2,5-διμεθυλοεξάνιο')]:
  ev("mode2D='condensed';selectedMol='"+key+"';fSelectMol()")
  assert ev("nameComponentsList.filter(Boolean).join('')==='"+name+"'")
 assert not js_errors,js_errors
 print('PASS previous complex molecules/alkynes; no JavaScript errors',flush=True)
finally:
 call('session.end',{})
