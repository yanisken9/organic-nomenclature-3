"""Real Firefox: all available skeletal forms and targeted before/after interactions."""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
folder=Path('/tmp/namelecule-skeletal-layout-20261028');folder.mkdir(exist_ok=True)
result={'completed':False,'inventory':[],'comparisons':[],'otherModes':[],'interactions':[]}
target='ethyl_2_isopropyl_3_dimethyl_6_6_hepten_2_yn_4_dioic_acid'
representatives=['ethanol','butanenitrile','hydroxypropanoic_acid_2','ethyl_sec_butyl_ether','ethyl_3_dimethyl_4_5_hexadiene_1_4']+[x['key']for x in json.loads(Path('docs/checks/other-acids-specs-20261028.json').read_text())]
measure=r"""(()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),v=svg.getBoundingClientRect(),els=[...svg.querySelectorAll('line,path,text')].filter(e=>!e.closest('defs')&&!(e.id||'').startsWith('number')&&e.getClientRects().length),rects=els.map(e=>e.getBoundingClientRect());const l=Math.min(...rects.map(r=>r.left)),r=Math.max(...rects.map(r=>r.right)),t=Math.min(...rects.map(r=>r.top)),b=Math.max(...rects.map(r=>r.bottom));const labels=els.filter(e=>e.tagName==='text'&&e.textContent.trim()),overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([labels[i].id,labels[j].id]);}const ls=jsmeNomeclatureApplet.molFile().split('\n'),ps=mainChainAtomsList.map(n=>[Number(ls[n+3].slice(0,10)),Number(ls[n+3].slice(10,20))]);return {key:selectedMol,mode:mode2D,name:currentMolName,chain:mainChainAtomsList.slice(),bounds:[r-l,b-t],centerErrorPx:(l+r-v.left-v.right)/2,margins:[l-v.left,v.right-r,t-v.top,v.bottom-b],parentHeight:Math.max(...ps.map(p=>p[1]))-Math.min(...ps.map(p=>p[1])),leftToRight:ps.at(-1)[0]>=ps[0][0]-.001,overlaps,labels:labels.map(e=>e.textContent)}})()"""
def data(expr):return json.loads(ev('JSON.stringify('+expr+')'))
def load(k,mode='skeletal'):
 ev('selectedMol='+json.dumps(k)+';mode2D='+json.dumps(mode)+";nameAnalysisMode='none';numberingFlag=false;fInitNamingProps();fLoadMol2D();true")
try:
 navigate('mulermoc-nom-52.html?v=skeletal-layout-test');app_ready();until('!!window.JSmolReadyFlag');ev('document.fonts.ready.then(()=>true)');ev('window.skeletalLayoutReal=fApplySkeletalLayout;true')
 # Before/after use exactly the same original library entry and naming state.
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.6)
  for k in representatives:
   ev('fApplySkeletalLayout=()=>{};true');load(k);before=data(measure)
   if width==1500 and k in [target,'butanenitrile']:screenshot(str(folder/(k+'-before.png')))
   ev('fApplySkeletalLayout=skeletalLayoutReal;fUpdateSVG();true');after=data(measure)
   assert before['name']==after['name'] and before['chain']==after['chain'],(k,'name/chain')
   assert abs(after['centerErrorPx'])<1 and min(after['margins'])>=-1,(width,after)
   assert after['leftToRight'] or len(after['chain'])<2,(k,'direction',after)
   assert not (set(map(tuple,after['overlaps']))-set(map(tuple,before['overlaps']))),(k,'new overlaps',before,after)
   result['comparisons'].append(dict(width=width,before=before,after=after))
   if width==1500:screenshot(str(folder/(k+'-after.png')))
  # Every available skeletal form, including cyclic/multifunctional legacy entries.
  rows=data("""(()=>{const out=[];for(const key of Object.keys(window.MOL2D)){if(!window.MOL2D[key].skeletal)continue;selectedMol=key;mode2D='skeletal';nameAnalysisMode='none';numberingFlag=false;fInitNamingProps();fLoadMol2D();out.push(MEASURE)}return out})()""".replace('MEASURE',measure))
  assert len(rows)==133
  for row in rows:
   assert abs(row['centerErrorPx'])<1 and min(row['margins'])>=-1,(width,row)
  result['inventory'].extend(dict(width=width,**row)for row in rows)
 # Other modes: geometry output and name are identical with/without the hook.
 for k in [target,'butanenitrile','hydroxypropanoic_acid_2']:
  for mode in ['condensed','expanded','condensedZigZag']:
   ev('fApplySkeletalLayout=()=>{};true');load(k,mode);before=data('({mol:jsmeNomeclatureApplet.molFile(),name:currentMolName})')
   ev('fApplySkeletalLayout=skeletalLayoutReal;true');load(k,mode);after=data('({mol:jsmeNomeclatureApplet.molFile(),name:currentMolName})')
   assert before==after,(k,mode);result['otherModes'].append(dict(key=k,mode=mode,unchanged=True))
 # Real selection + 3D model, zoom, resize and numbering on the user's molecule.
 call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1})
 ev('document.getElementById('+json.dumps(target)+').click();true');until('mainChainPool3DKey==='+json.dumps(target))
 ev("document.querySelectorAll('#radio2DMode .mode2DOption')[2].click();true")
 baseline=data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})')
 ev("document.getElementById('comp5').click();true")
 until("document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===7")
 numbers=data("[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>Number(e.textContent))");assert numbers==list(range(1,8)),numbers
 for width in [390,1000,1500]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.6)
  current=data('({mol:myMol2D,name:currentMolName,chain:mainChainAtomsList,chain3:mainChainAtoms3D})');assert current==baseline
  assert data("[...document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]')].map(e=>Number(e.textContent))")==numbers
  result['interactions'].append(dict(width=width,stable=True))
 for comp in ['comp1','comp3','acidPrefixSub3']:
  ev('document.getElementById('+json.dumps(comp)+').click();true');time.sleep(.2)
  assert ev('!!JmolSelection'),comp
  assert ev('myMol2D')==baseline['mol'],comp
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 (folder/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'allLibraryViews':len(result['inventory']),'beforeAfter':len(result['comparisons']),'otherModes':len(result['otherModes']),'errors':len(js_errors)}),flush=True)
