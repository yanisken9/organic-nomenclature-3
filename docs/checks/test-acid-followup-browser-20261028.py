"""Firefox follow-up checks. Writes only /tmp artifacts; real controls/labels/JSmol selections."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
import runpy
ns=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py');probes=[]
for key,forms in ns['inventory']().items():
 if forms.get('expanded'):
  groups=ns['parse'](forms['expanded'])[-1]
  if groups:probes.append(dict(key=key,groups=[dict(o=o,h=hs[0],c=c)for c,o,hs in groups]))
folder=Path('/tmp/namelecule-acid-followup-20261028');result={'completed':False,'expanded':[],'prefix':[],'checks':[]}
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def select(key,mode='expanded'):
 ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fSelectMol();true')
 until('mainChainPool3DKey==='+json.dumps(key))
 until("(()=>{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href})()")
try:
 navigate('mulermoc-nom-52.html?v=acid-followup-check');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7)
  for p in probes:
   select(p['key']);time.sleep(.12)
   row=data("""(()=>{const groups="""+json.dumps(p['groups'])+""",map=fGetRenderedAtomTextMap(false,true),svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text:not([id^=number])')];return {key:selectedMol,name:currentMolName,groups:groups.map(g=>{const o=map[g.o].node,h=map[g.h].node,a=o.getBoundingClientRect(),b=h.getBoundingClientRect(),bond=fFindBondIndexByAtoms(g.o,g.h),line=molSvg.selectAll('line')[svgBondList[bond]-1].node;return {oxygen:o.textContent,hydrogen:h.textContent,dy:Number(line.getAttribute('y2'))-Number(line.getAttribute('y1')),gap:Math.max(b.left-a.right,a.left-b.right),overlaps:labels.filter(t=>t!==h).filter(t=>{const c=t.getBoundingClientRect();return Math.min(c.right,b.right)-Math.max(c.left,b.left)>1&&Math.min(c.bottom,b.bottom)-Math.max(c.top,b.top)>1}).map(t=>t.textContent),clipped:b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}})}})()""")
   for g in row['groups']:assert g['oxygen']=='O'and g['hydrogen']=='H'and abs(g['dy'])<.01 and g['gap']>2 and not g['overlaps']and not g['clipped'],(width,row)
   result['expanded'].append(dict(width=width,**row))
   if width==1500 and p['key']in ['propanedioic_acid','methanoicacid','ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid']:screenshot(str(folder/(p['key']+'-expanded.png')))
  print('PASS',width,'15 expanded / 17 visible horizontal OH',flush=True)
 key='ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid'
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.7);select(key)
  labels=data("[...document.querySelectorAll('.nameCompContainer .nameCompBox')].map(e=>e.textContent.trim())")
  assert labels==['3-','αιθυλο','-2-','ισοπροπυλο','-4,5-','διμεθυλο','εξ','αν','ικό οξύ'],labels
  assert ev("(()=>{const r=document.querySelector('.nameCompContainer').getBoundingClientRect(),h=document.querySelector('#nameAnalysis .nameContainer').getBoundingClientRect();return r.left>=h.left-1&&r.right<=h.right+1})()")
  for mode in ['condensed','expanded','skeletal']:
   idx=['condensed','expanded','skeletal'].index(mode);ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(idx)+'].click();true');time.sleep(.5)
   for box,slot,locants in [('comp1',1,False),('comp3',2,False),('acidPrefixNumber3',3,True),('acidPrefixSub3',3,False)]:
    ev('document.getElementById('+json.dumps(box)+').click();true');time.sleep(.15)
    group=data('fGetHydrocarbonBranchGroup('+str(slot)+')');assert len(group['names'])==1
    high=data('({a:fGetHydrocarbonBranchHighlight('+str(slot)+'),b:fGetHydrocarbonBranchHighlight3D('+str(slot)+'),selected:Jmol.evaluateVar(jmolAppletNomeclature,"{selected}.atomno.all"),explanation:document.getElementById("nameAnalysisExplain").textContent,rule:document.getElementById("ruleTheoryContainer").textContent,ruleOpen:document.getElementById("ruleContainer").getBoundingClientRect().height>0,numbering:numberingFlag})')
    actual2=data('fGetHydrocarbonBranchHighlight('+str(slot)+').atoms.filter(a=>allAtomsTypeList[a-1]==="C").sort((a,b)=>a-b)')
    expected2=sorted(a+1 for member in group['members']for a in member['atoms']);assert actual2==expected2,(box,group,high)
    expect3=data('(()=>{const ids=fGetHydrocarbonBranchHighlight3D('+str(slot)+').atoms,expected=new Set(ids);for(const b of bondList3D){if(ids.includes(b[0])&&allAtomsTypeList3D[b[1]-1]==="H")expected.add(b[1]);if(ids.includes(b[1])&&allAtomsTypeList3D[b[0]-1]==="H")expected.add(b[0]);}return [...expected].sort((a,b)=>a-b)})()')
    assert sorted(high['selected'])==expect3 and high['numbering']==locants and not high['ruleOpen'],(box,high,expect3)
    if locants:
     until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===6')
     assert '4, 5' in high['explanation'],high
    result['prefix'].append(dict(width=width,mode=mode,box=box,names=group['names'],highlight=high))
  screenshot(str(folder/('prefix-'+str(width)+'.png')))
 # Restored selection and per-box eye controls must preserve new IDs/semantic modes.
 ev("if(nameAnalysisMode!=='compAcidSub3')document.getElementById('acidPrefixSub3').click();fShowNameAnalysis();true")
 assert ev("document.getElementById('acidPrefixSub3').classList.contains('selected')")
 ev("window.nameEyeEdit=true;fShowNameAnalysis();document.querySelector('.compEye[data-comp=acidPrefixSub3]').click();true")
 assert ev("fNameCompHidden('acidPrefixSub3')&&nameAnalysisMode==='none'")
 ev("document.querySelector('.compEye[data-comp=acidPrefixSub3]').click();window.nameEyeEdit=false;fShowNameAnalysis();true")
 # Saved embedded hosts opt out and retain the legacy fixed component rendering/grouping.
 ev("document.documentElement.removeAttribute('data-namelecule-acid-prefix-boxes');fShowNameAnalysis();true")
 assert ev("!document.getElementById('acidPrefixSub3')&&document.getElementById('comp3').textContent==='ισοπροπυλο-4,5-διμεθυλο'&&fGetHydrocarbonBranchGroup(2).names.length===2")
 result['checks']+=['Nine separate boxes, correct individual 2D/3D/H groups in all forms and two widths','Closed optional rules; locant numbering only','Selection restoration and eye hide/show','No-opt-in legacy name/group projection unchanged']
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;Path('/tmp/namelecule-acid-followup-20261028/browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'expanded':len(result['expanded']),'prefix':len(result['prefix']),'errors':len(js_errors)}),flush=True)
