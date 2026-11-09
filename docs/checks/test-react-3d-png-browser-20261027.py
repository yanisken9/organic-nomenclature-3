"""Real native PNG downloads, UI prompt accept/rename/cancel and main52 parity."""
from pathlib import Path
helper=Path('docs/checks/test-react-ether-naming-browser-20261027.py').read_text().split('\ntry:\n',1)[0].replace('9237','9238')
helper=helper.replace("call('session.new',{'capabilities':{}})","call('session.new',{'capabilities':{'alwaysMatch':{'unhandledPromptBehavior':'ignore'}}})")
helper=helper.replace('seq=0;js_errors=[]','''seq=0;js_errors=[];promptRecords=[];promptReply={'accept':True}
def send_prompt_reply(params):
 reply={**promptReply}
 if reply.get('accept') and params.get('type')=='prompt':reply.setdefault('userText',params.get('defaultValue',''))
 payload=json.dumps({'id':1000000+len(promptRecords),'method':'browsingContext.handleUserPrompt','params':{'context':params['context'],**reply}}).encode();mask=os.urandom(4);n=len(payload)
 header=bytes([129,128|n]) if n<126 else bytes([129,254])+struct.pack('!H',n)
 s.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(payload)))''')
helper=helper.replace("  if msg.get('method')=='log.entryAdded':","  if msg.get('method')=='browsingContext.userPromptOpened':\n   promptRecords.append(msg['params']);send_prompt_reply(msg['params'])\n  if msg.get('method')=='log.entryAdded':")
helper=helper.replace("['log.entryAdded']","['log.entryAdded','browsingContext.userPromptOpened']")
exec(compile(helper,'existing-bidi-with-real-prompt-handler','exec'))
import zlib,unicodedata
folder=Path('/tmp/namelecule-react-png-20261027/downloads');folder.mkdir(exist_ok=True)
artifacts=Path('/tmp/namelecule-react-3d-png-20261027')
result={'completed':False,'checks':[],'cases':[],'parity':[]};capture=[]
runtime_paths=['react-preview/src/MoleculePreview.jsx','react-preview/public/viewer-host-bridge.js','react-preview/public/viewer-host.html']+[str(p) for p in Path('react-preview/dist').rglob('*') if p.is_file()]
fingerprint={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in runtime_paths}
legacy_drain=drain
def drain(evaluate):
 wait(evaluate,"nameAnalysisMode==='none' || !numberingFlag || document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.filter(Boolean).length",25);legacy_drain(evaluate)
def form(mode):
 if cev("mode2D==='condensedZigZag'?'skeletal':mode2D")!=mode:action("document.querySelector('input[name=mode][value="+mode+"]').click()")
def control(key,value):
 actual=json.loads(cev('JSON.stringify({style:vis3D,hydrogens:hydrogens3DFlag,labels:atomSymbols3DFlag,rotation:rotateFlag})'))[key]
 if actual==value:return
 if key=='style':action("(()=>{let s=document.getElementById('style-3d');s.value="+json.dumps(value)+";s.dispatchEvent(new Event('change',{bubbles:true}))})()")
 else:action("document.getElementById('"+key+"-3d').click()")
def observe_download(evaluate):evaluate("window.__pngIntents=[];document.addEventListener('click',e=>{let a=e.target;if(a instanceof HTMLAnchorElement && a.download)__pngIntents.push({name:a.download,href:a.href.slice(0,25)})},true)")
def png_info(data):
 assert data.startswith(b'\x89PNG\r\n\x1a\n');i=8;idat=[];header=None
 while i+12<=len(data):
  n=struct.unpack('!I',data[i:i+4])[0];kind=data[i+4:i+8];body=data[i+8:i+8+n]
  if i+12+n>len(data):return None
  assert zlib.crc32(kind+body)&0xffffffff==struct.unpack('!I',data[i+8+n:i+12+n])[0]
  if kind==b'IHDR':header=struct.unpack('!IIBBBBB',body)
  if kind==b'IDAT':idat.append(body)
  i+=12+n
  if kind==b'IEND':
   raw=zlib.decompress(b''.join(idat));assert len(raw)>header[0]*header[1]
   return {'width':header[0],'height':header[1],'format':list(header[2:]),'scanlinesSHA256':hashlib.sha256(raw).hexdigest(),'fileSHA256':hashlib.sha256(data).hexdigest(),'trailerBytes':len(data)-i}
 return None

def raster_bytes(path):
 data=Path(path).read_bytes();i=8;chunks=[]
 while i+12<=len(data):
  n=struct.unpack('!I',data[i:i+4])[0];kind=data[i+4:i+8];body=data[i+8:i+8+n];i+=12+n
  if kind==b'IDAT':chunks.append(body)
  if kind==b'IEND':break
 return zlib.decompress(b''.join(chunks))
def downloaded(before):
 for _ in range(160):
  paths=[p for p in folder.glob('*') if p.is_file() and not p.name.endswith('.part') and p.name not in before]
  if len(paths)==1:
   data=paths[0].read_bytes();info=png_info(data)
   if info:return paths[0],info
  time.sleep(.1)
 raise AssertionError('No single complete native PNG: '+str(paths))
def exported(evaluate,kind='3d',react=True,chosen=None):
 before={p.name for p in folder.glob('*')};n=evaluate('window.__pngIntents.length');prompts=len(promptRecords)
 if react:action("document.getElementById('save-"+kind+"-png').click()")
 else:
  evaluate('fSaveJmolPng()' if kind=='3d' else 'fSave2DPng()')
  # Drive the BiDi loop so the native Save Image prompt is actually accepted.
  wait(evaluate,'window.__pngIntents.length>'+str(n),25)
 path,info=downloaded(before)
 intent=json.loads(evaluate('JSON.stringify(window.__pngIntents.at(-1))'))
 expected=chosen or evaluate("(currentMolName||selectedMol||'molecule').replace(/\s+/g,'_')+'_"+kind.upper()+".png'")
 assert intent['name']==expected,(intent,expected)
 assert info['width']==1200 and (info['height']==1200 if kind=='3d' else info['height']>90)
 if kind=='3d':assert len(promptRecords)==prompts+1 and promptRecords[-1]['type']=='prompt'
 if react:assert ev("document.querySelector('.molecule-export-status').textContent==='Ζητήθηκε λήψη PNG.'")
 return {**info,'filename':intent['name'],'path':str(path)}

def model_state(evaluate):
 # Native export deliberately clears echoes, so compare the molecular scene
 # separately; its own footer/numbering policy is checked by PNG/native parity.
 value=json.loads(evaluate(scene));value.pop('echoes',None)
 return {'scene':value,'prefs':json.loads(evaluate('JSON.stringify({style:vis3D,hydrogens:hydrogens3DFlag,labels:atomSymbols3DFlag,rotation:rotateFlag})')),
 'labels':evaluate("JSON.stringify(Jmol.evaluateVar(jmolAppletNomeclature,'{all}.label'))"),'camera':json.loads(evaluate("JSON.stringify(Jmol.getPropertyAsArray(jmolAppletNomeclature,'orientationInfo').quaternion)"))}
def checkpoint():
 (artifacts/'capture.json').write_text(json.dumps({'sourceSHA256':fingerprint,'result':result,'capture':capture},ensure_ascii=False))
# molecule, representation, C–H, atomlabels, naming, component
cases=[('ethanol',style,h,l,'iupac','base') for style,h,l in [('ballnstick',True,True),('ballnstick',False,False),('spacefill',True,False),('spacefill',False,True),('sticks',True,True),('sticks',False,False)]]
cases += [('dimethyl_2_3_butane','ballnstick',True,True,'iupac','comp5'),('dimethyl_2_3_butane','sticks',False,False,'iupac','comp0'),('ethyl_isopropyl_ether','ballnstick',True,True,'iupac','base'),('ethyl_isopropyl_ether','spacefill',False,False,'common','comp10'),('isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5','ballnstick',True,True,'iupac','comp5'),('isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5','sticks',False,True,'iupac','comp0')]
try:
 navigate('react-preview/dist/?v=3d-png-'+str(time.time_ns())+'#/viewer');visible()
 child=call('browsingContext.getTree',{'root':ctx})['contexts'][0]['children'][0]['context'];observe();observe_download(cev);view('3d')
 result['iframeSize']=json.loads(ev("JSON.stringify((()=>{let r=document.querySelector('iframe').getBoundingClientRect();return {width:r.width,height:r.height}})())"))
 for key,style,h,l,name,ident in cases:
  pick(key);control('style',style);control('hydrogens',h);control('labels',l)
  if next(m for m in catalog if m['id']==key)['series']=='ether':naming(name)
  if ident!='base':component(ident)
  drain(cev);before=model_state(cev);value=exported(cev);after=model_state(cev)
  assert before==after,'Export changed model/labels/preferences/camera'
  capture.append({'kind':'3d','case':[key,style,h,l,name,ident],'image':value,'state':after})
  result['cases'].append({'kind':'3d','case':[key,style,h,l,name,ident],**value})
  if ident!='base':component(ident)
  checkpoint();print('React nativePNG3D',key,style,name,ident,flush=True)
 # Actual native prompt rename and cancellation, not a replaced prompt function.
 pick('ethanol');promptReply={'accept':True,'userText':'Namelecule δοκιμή_3D.png'}
 value=exported(cev,chosen='Namelecule δοκιμή_3D.png');result['renamedFile']=value
 promptReply={'accept':True,'userText':'Namelecule_no_extension'}
 result['extensionlessFile']=exported(cev,chosen='Namelecule_no_extension')
 promptReply={'accept':False};before={p.name for p in folder.glob('*')};action("document.getElementById('save-3d-png').click()")
 assert ev("document.querySelector('.molecule-export-status').textContent.includes('δεν ξεκίνησε') && !document.querySelector('iframe').hidden")
 assert before=={p.name for p in folder.glob('*')}
 promptReply={'accept':True};assert cev('window.prompt.toString().includes("[native code]")')
 # Controlled synchronous native failure, then recovery without remount.
 cev("window.__nativeSave=fSaveJmolPng;fSaveJmolPng=()=>{throw new Error('controlled native failure')}")
 action("document.getElementById('save-3d-png').click()")
 assert ev("document.querySelector('.molecule-export-status').textContent.includes('δεν ξεκίνησε') && !document.querySelector('iframe').hidden")
 cev('fSaveJmolPng=__nativeSave')
 # Actual PNG while native rotation is active; pose changes but graph stays.
 control('rotation',True);value=exported(cev);assert cev('rotateFlag');control('rotation',False);result['rotatingExport']=value
 result['checks'].append('12real1200square PNGs across3styles/H/labels/branch+chainhighlights/both ether names; actual native rename/cancel; syncfailure/recovery; rotation export; graph/preferences/labels/camera unchanged')
 # 2D regression all forms and CHn, after using the new3D export path.
 pick('ethanol');view('2d')
 for mode,sym in [('condensed',False),('expanded',False),('skeletal',False),('skeletal',True)]:
  form(mode)
  if sym:action("document.getElementById('skeletal-symbols').click()")
  value=exported(cev,'2d');capture.append({'kind':'2d','case':['ethanol',mode,sym,'iupac','base'],'image':value});result['cases'].append({'kind':'2d','mode':mode,'symbols':sym,**value})
 result['checks'].append('Native2D PNG still downloads in condensed/expanded/skeletal/CHn after3Dexport')
 # Native standalone output at exactly the captured viewport; current2D mode
 # is condensed in all3D captures. Restore the native camera with molecule load.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':int(result['iframeSize']['width']),'height':int(result['iframeSize']['height'])},'devicePixelRatio':1})
 navigate('mulermoc-nom-52.html?v=3d-png-main-'+str(time.time_ns()));app_ready();wait(ev,'!!window.JSmolReadyFlag')
 css=Path('react-preview/public/viewer-host.html').read_text().split('<style>\n')[-1].split('</style>')[0]
 ev("(()=>{let s=document.createElement('style');s.textContent="+json.dumps(css)+";document.head.append(s);document.documentElement.dataset.view='3d';document.getElementById('nomeclature3D').style.display='block';fResizeViewers()})()")
 observe_download(ev)
 for row in capture:
  key=row['case'][0];ev('selectedMol='+json.dumps(key)+';fSelectMol();fResizeViewers()')
  wait(ev,"Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models?.[0]?.file?.endsWith('/"+key+"_3D.sdf') && allAtomsTypeList3D.length>0");drain(ev)
  if row['kind']=='3d':
   _,style,h,l,name,ident=row['case']
   ev("if(vis3D!=="+json.dumps(style)+")$('#dropLi"+str(['ballnstick','spacefill','sticks'].index(style))+"').trigger('click')")
   ev("if(hydrogens3DFlag!=="+json.dumps(h)+")$('#hydrogensCheck').trigger('click');if(atomSymbols3DFlag!=="+json.dumps(l)+")$('#atomSymbolsCheck').trigger('click')")
   if next(m for m in catalog if m['id']==key)['series']=='ether':ev("$('#radioEtherNaming .etherNamingRadio[data-naming-mode="+name+"]').trigger('click')")
   if ident!='base':ev("$('#"+ident+"').trigger('click')")
   drain(ev);value=exported(ev,'3d',False)
   assert model_state(ev)==row['state'],('postexportstate',row['case'])
  else:
   _,mode,sym,name,ident=row['case']
   ev("document.documentElement.dataset.view='2d';document.getElementById('nomeclature3D').style.display='none';fResizeViewers();$('#radio2DMode .mode2DOption').eq("+str(['condensed','expanded','skeletal'].index(mode))+").trigger('click')")
   if sym:ev("$('#zigzagCheck').trigger('click')")
   drain(ev);value=exported(ev,'2d',False)
  expected=row['image'];assert {k:value[k] for k in ['width','height','format','filename']}=={k:expected[k] for k in ['width','height','format','filename']}
  if row['kind']=='2d':
   assert value['scanlinesSHA256']==expected['scanlinesSHA256'],('2DPNG raster differs',row['case']);comparison={'scanlinesExact':True}
  else:
   a,b=raster_bytes(value['path']),raster_bytes(expected['path']);assert len(a)==len(b)==4321200
   assert set(a[::3601])==set(b[::3601])=={0},'Unexpected3DPNG filtering'
   diffs=[abs(x-y) for x,y in zip(a,b) if x!=y];maximum=max(diffs,default=0)
   mean=sum(diffs)/len(a);comparison={'scanlinesExact':not diffs,'maxChannelDifference':maximum,'meanChannelDifference':mean,'differingBytes':len(diffs)}
   assert maximum<=40 and mean<=1,('Native3DPNG difference exceeds shading tolerance',row['case'],comparison)
  result['parity'].append({'kind':row['kind'],'case':row['case'],**comparison})
  print('Native PNG parity',row['kind'],row['case'],flush=True)
 result['checks'].append('16native PNGs:4exact2D raster comparisons and12bounded3D RGB comparisons(max40/255 and mean1/255 native shading tolerance), dimensions/formats/filenames equal, post3Dscene/state exact. Metadata/trailing embedded Jmol state excluded')
 result['knownJSmolErrors']=[e for e in js_errors if e.get('text')=="TypeError: can't access property \"setDisplay\", this.viewer is null" and any(f.get('url')=='https://chemapps.stolaf.edu/jmol/jsmol/j2s/core/corejmol.z.js' for f in e.get('stackTrace',{}).get('callFrames',[]))]
 result['unexpectedJavaScriptErrors']=[e for e in js_errors if e not in result['knownJSmolErrors']];assert not result['unexpectedJavaScriptErrors'],result['unexpectedJavaScriptErrors']
 assert len(result['parity'])==16;result['completed']=True
finally:
 result['javascriptErrors']=js_errors;result['nativePrompts']=[{k:p.get(k) for k in ['type','message','defaultValue']} for p in promptRecords];checkpoint()
 (artifacts/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'images':len(result['cases']),'parity':len(result['parity']),'errors':len(js_errors)}),flush=True)
