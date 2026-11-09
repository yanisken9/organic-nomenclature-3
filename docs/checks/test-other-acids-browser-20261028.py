"""Real Firefox: acid registry, three 2D forms, 3D identity, highlights, numbering.
Artifacts stay in /tmp; uses existing localhost8013 and Firefox BiDi9237.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
specs=json.load(open('docs/checks/other-acids-specs-20261028.json'));folder=Path('/tmp/namelecule-other-acids-20261028');result={'completed':False,'forms':[],'molecules':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
# Native CH2 backgrounds cover the bonded C anchor; subscript extents may extend
# below that background without touching a bond. Check that anchor, plus all overlaps.
def geometry():
 return data("""(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),els=[...svg.querySelectorAll('text:not([id^=number])')].filter(e=>e.textContent.trim()),rect=e=>e.getBoundingClientRect(),overlaps=[];for(let i=0;i<els.length;i++)for(let j=0;j<i;j++){if(els[i].contains(els[j])||els[j].contains(els[i]))continue;const a=rect(els[i]),b=rect(els[j]);if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([els[i].textContent,els[j].textContent]);}return {key:selectedMol,mode:mode2D,name:currentMolName,texts:els.map(e=>e.textContent),overlaps,clipped:els.filter(e=>{const b=rect(e);return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),unmasked:els.filter(e=>{let b=rect(e);if(/^C(?:H[23]?)?$|^COOH$|^HOOC$/.test(e.textContent)){const a=e.getExtentOfChar(e.textContent==='HOOC'?3:0),m=e.getScreenCTM(),p=new DOMPoint(a.x,a.y).matrixTransform(m),q=new DOMPoint(a.x+a.width,a.y+a.height).matrixTransform(m);b={left:p.x,top:p.y,right:q.x,bottom:q.y}}return ![...svg.querySelectorAll('rect')].some(r=>{const c=rect(r);return getComputedStyle(r).fill==='rgb(255, 255, 255)'&&!!(r.compareDocumentPosition(e)&Node.DOCUMENT_POSITION_FOLLOWING)&&c.left<=b.left+.5&&c.right>=b.right-.5&&c.top<=b.top+.5&&c.bottom>=b.bottom-.5})}).map(e=>e.textContent),font:svg.dataset.uniformAtomFontPixels,chain:mainChainAtomsList,chain3D:mainChainAtoms3D}})()""")
try:
 navigate('mulermoc-nom-52.html?v=acids-browser-20261028');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)')
 assert ev('Object.keys(nameExamples).length')==134
 for spec in specs:
  k=spec['key'];ev('document.getElementById('+json.dumps(k)+').click();true')
  until('mainChainPool3DKey==='+json.dumps(k))
  until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
  model=data("({atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length,bonds:Jmol.getPropertyAsArray(jmolAppletNomeclature,'bondInfo').length,parsedAtoms:allAtomsTypeList3D.length,chain:mainChainAtoms3D})")
  assert model['atoms']==model['parsedAtoms'] and model['bonds']==model['atoms']-1,(k,model)
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.25)
   for i,mode in enumerate(['condensed','expanded','skeletal']):
    ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(i)+'].click();true');row=geometry()
    assert row['name']==spec['name'] and len(row['chain'])==spec['parent'],row
    assert not row['overlaps'] and not row['clipped'],(width,row)
    if mode=='expanded':assert row['texts'].count('H')==int(spec['formula'].split('H')[1].split('O')[0]),row
    if mode=='condensed':
     assert any('COOH' in t for t in row['texts']),row
     assert not row['unmasked'],row
    result['forms'].append(dict(width=width,**row))
    if width==1500:screenshot(str(folder/(k+'-'+mode+'.png')))
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});time.sleep(.8)
  ev("document.querySelectorAll('#radio2DMode .mode2DOption')[1].click();true")
  groups=[]
  for slot in ([1,2,3] if spec['parent']>=6 else [1,2]):
   group=data('fGetHydrocarbonBranchGroup('+str(slot)+')')
   if not group:continue
   comp='acidPrefixNumber3' if slot==3 else 'comp'+str(slot*2-1)
   ev('document.getElementById('+json.dumps(comp)+').click();true')
   high=data('({a:fGetHydrocarbonBranchHighlight('+str(slot)+'),b:fGetHydrocarbonBranchHighlight3D('+str(slot)+'),members:fGetHydrocarbonBranchGroup('+str(slot)+').members,selection:JmolSelection})')
   expected=sorted(a+1 for member in high['members'] for a in member['atoms'])
   actual=data('fGetHydrocarbonBranchHighlight('+str(slot)+').atoms.filter(a=>allAtomsTypeList[a-1]===\'C\').sort((a,b)=>a-b)')
   assert expected==actual and len(high['b']['atoms'])==len(expected),(k,slot,high)
   assert high['selection'].startswith('select atomno='),(k,slot,high)
   time.sleep(.15)
   selected3=data("Jmol.evaluateVar(jmolAppletNomeclature,'{selected}.atomno.all')")
   expected3=data('(()=>{const ids=fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms,expected=new Set(ids);for(const b of bondList3D){if(ids.includes(b[0])&&allAtomsTypeList3D[b[1]-1]==="H")expected.add(b[1]);if(ids.includes(b[1])&&allAtomsTypeList3D[b[0]-1]==="H")expected.add(b[0]);}return [...expected].sort((a,b)=>a-b)})()')
   assert sorted(selected3)==expected3,(k,slot,selected3,expected3)
   high.update(actualSelected3D=selected3,expectedSelected3D=expected3);groups.append(high)
  # Click actual parent-name component. Timer must append rather than replace numbers.
  ev("window.acidNumberHistory=[];window.acidNumberObserver=new MutationObserver(()=>{const a=[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>Number(e.textContent));acidNumberHistory.push({time:performance.now(),numbers:a})});acidNumberObserver.observe(document.getElementById('jsmeNomeclatureSVG'),{childList:true,subtree:true});document.getElementById('comp5').click();true")
  samples=[]
  for i in range(spec['parent']+2):
   samples.append(data("[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>Number(e.textContent))"));time.sleep(.22)
  until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length==='+str(spec['parent']))
  final=data("[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>Number(e.textContent))")
  history=data('acidNumberHistory');ev('acidNumberObserver.disconnect();true');assert final==list(range(1,spec['parent']+1)) and any(0<len(a['numbers'])<spec['parent'] for a in history),(k,samples,history,final)
  assert all(a==list(range(1,len(a)+1)) for a in samples),(k,samples)
  ev('fClearHighlights();true');result['molecules'].append(dict(key=k,model=model,groups=groups,numberingSamples=samples,numberingHistory=history,finalNumbers=final))
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 Path('/tmp/namelecule-other-acids-20261028/browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'forms':len(result['forms']),'3D':len(result['molecules']),'errors':len(js_errors)}),flush=True)
