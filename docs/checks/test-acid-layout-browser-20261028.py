"""Real Firefox: Expanded acid layout, label clearance, native lines, zoom/highlight.
Browser screenshots and intermediate artifacts only under /tmp.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
import runpy
ns=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py');probes=[]
for key,forms in ns['inventory']().items():
 if not forms.get('expanded'):continue
 ls,n,nb,aa,bb,tt,xyz,edges,groups=ns['parse'](forms['expanded'])
 if groups:probes.append(dict(key=key,groups=[dict(c=c,o=o,h=hs[0],od=next(b if a==c else a for a,b,q in edges if q==2 and ((a==c and tt[b]=='O')or(b==c and tt[a]=='O'))))for c,o,hs in groups]))
folder=Path('/tmp/namelecule-acid-layout-20261028');folder.mkdir(exist_ok=True);result={'completed':False,'cases':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def select(p):
 ev('selectedMol='+json.dumps(p['key'])+";mode2D='expanded';nameAnalysisMode='none';numberingFlag=false;fSelectMol();true")
 until('mainChainPool3DKey==='+json.dumps(p['key']))
 until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
 time.sleep(.12)
def inspect(p):
 return data("""(()=>{const groups="""+json.dumps(p['groups'])+""",map=fGetRenderedAtomTextMap(false,true),rects=fGetRenderedAtomRectMap(false,true),svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text:not([id^=number])')],boxes=labels.map(e=>e.getBoundingClientRect()),overlaps=[];for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){const a=boxes[i],b=boxes[j];if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([i+1,j+1,labels[i].textContent,labels[j].textContent])}return {key:selectedMol,zoom:molZoom2D,mode:nameAnalysisMode,overlaps,clipped:labels.filter((e,i)=>{const b=boxes[i];return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),groups:groups.map(g=>{const c=map[g.c].node.getBoundingClientRect(),o=map[g.od].node.getBoundingClientRect(),oh=map[g.o].node.getBoundingClientRect(),h=map[g.h].node.getBoundingClientRect(),bi=fFindBondIndexByAtoms(g.c,g.od),lines=molSvg.selectAll('line'),ls=[lines[svgBondList[bi]-1].node,lines[svgBondList[bi]].node];return {vertical:ls.every(l=>Math.abs(Number(l.getAttribute('x1'))-Number(l.getAttribute('x2')))<.01),carbonylLabelGap:Math.max(c.top-o.bottom,o.top-c.bottom),ohLabelGap:Math.max(h.left-oh.right,oh.left-h.right),maskClearances:[g.c,g.od].map(i=>{const b=map[i].node.getBoundingClientRect(),r=rects[i].node.getBoundingClientRect();return Math.min(b.left-r.left,r.right-b.right,b.top-r.top,r.bottom-b.bottom)})}})}})()""")
def check(row):
 assert not row['clipped']and not row['overlaps'],row
 for g in row['groups']:assert g['vertical']and g['carbonylLabelGap']>2 and g['ohLabelGap']>2 and min(g['maskClearances'])>.5,row
try:
 navigate('mulermoc-nom-52.html?v=acid-layout-check');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  if width==390:ev("document.getElementById('rotatePromptDismiss').click();true")
  for p in probes:
   select(p);row=inspect(p);row['width']=width;check(row);result['cases'].append(row)
   # Existing masks only: native JSME line geometry/count remains exactly intact.
   assert ev("(()=>{const raw=new DOMParser().parseFromString(jsmeNomeclatureApplet.getMolecularAreaGraphicsString(),'image/svg+xml'),a=[...raw.querySelectorAll('line')],b=[...document.querySelectorAll('#jsmeNomeclatureSVG line')];return a.length===b.length&&a.every((l,i)=>['x1','x2','y1','y2'].every(k=>l.getAttribute(k)===b[i].getAttribute(k)))})()")
   if width==1500 and p['key']in ['methanoicacid','propanedioic_acid','dihydroxybutanedioic_acid_2_3','ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid','dimethyl_2_2_propanoic_acid']:screenshot(str(folder/(p['key']+'-expanded.png')))
  print('PASS',width,'15 Expanded / 17 carboxyls / masks / all labels / native bond lines',flush=True)
  for key in ['methanoicacid','dimethyl_2_2_propanoic_acid','ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid']:
   p=next(p for p in probes if p['key']==key);select(p)
   # The root component selects the main chain, including carboxyl C.
   ev("document.getElementById('comp5').click();true");time.sleep(.15)
   for phase in ['selected','zoom-in','zoom-restored']:
    if phase=='zoom-in':ev("document.getElementById('zoomInBtn').click();true")
    if phase=='zoom-restored':ev("document.getElementById('zoomOutBtn').click();true")
    row=inspect(p);row.update(width=width,phase=phase);check(row);result['cases'].append(row)
   screenshot(str(folder/(key+'-selected-'+str(width)+'.png')))
 # Existing mode controls, colour toggles and PNG export still render the final masks.
 p=next(p for p in probes if p['key']=='methanoicacid');select(p)
 for i,mode in enumerate(['condensed','expanded','skeletal','expanded']):
  idx=['condensed','expanded','skeletal'].index(mode)
  ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(idx)+'].click();true')
  assert ev('mode2D')==mode
  if mode=='expanded':check(inspect(p))
 for _ in range(2):
  ev("document.getElementById('svgAtomColorCheck').click();true");check(inspect(p))
 ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
 until('!!window.__png && !!window.__exportSvg')
 assert ev("window.__png.size>1000 && !new DOMParser().parseFromString(window.__exportSvg,'image/svg+xml').querySelector('parsererror')")
 result['lifecycle']=['Actual mode radio handlers','Colour off/on','PNG blob and parseable exported SVG']
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['cases']),'errors':len(js_errors)}),flush=True)
