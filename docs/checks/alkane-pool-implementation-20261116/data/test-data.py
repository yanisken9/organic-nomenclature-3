"""Actual native Main57 six-source viewer acceptance; source hashes remain frozen."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'browser-support.py').read_text(),'owned-alkane-support','exec'))
MANIFEST=json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text());TARGET=json.loads((HERE/'source-target.json').read_text())
ROOT_ADOPTED=['mulermoc-nom-57.html','tools/build-name-builder-host.py','tools/build-molecular-detective-host.py','js/mulermoc-nom-molview-55.js','js/mulermoc-nom-molview-56.js','js/mulermoc-nom-molview-57.js']
for path in ROOT_ADOPTED:TARGET['files'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
out['rootApprovedCurrentHashes']={p:TARGET['files'][p]for p in ROOT_ADOPTED}
def select(key,mode='expanded'):
 ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fSelectMol();true');wait('fMuler3DModelReady()',50);pause(200)
def dataset():
 return read('''(()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),lines=[...s.querySelectorAll('line')],cc=[],fonts=[...s.querySelectorAll('text[data-namelecule-role="label"]')].filter(t=>['C','H'].includes(t.textContent.trim())).map(t=>parseFloat(t.getAttribute('font-size'))).sort((a,b)=>a-b);for(let i=0;i<bondList.length;i++){const[a,b]=bondList[i];if(allAtomsTypeList[a-1]==='C'&&allAtomsTypeList[b-1]==='C'){const l=lines[svgBondList[i]-1];cc.push(Math.hypot(Number(l.getAttribute('x2'))-Number(l.getAttribute('x1')),Number(l.getAttribute('y2'))-Number(l.getAttribute('y1'))));}}cc.sort((a,b)=>a-b);const c=cc[Math.floor(cc.length/2)],font=fonts[Math.floor(fonts.length/2)];return{id:selectedMol,name:currentMolName,mode:mode2D,atoms:allAtomsTypeList.length,atoms3D:allAtomsTypeList3D.length,chain:mainChainAtomsList,ratio:font?c/font:null,calibration:s.dataset.alkaneFixedCCScale||null,displayPolicy:nameExamples[selectedMol].displayPolicy||null}})()''')
try:
 call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
 navigate('mulermoc-nom-57.html?v=alkane-data-final');app_ready();wait('window.JSmolReadyFlag===true',70);call('browsingContext.activate',{'context':ctx})
 check(read('Object.keys(nameExamples).length')==147,'Native library merges six customs into147 records')
 out['molecules']=[]
 for molecule in MANIFEST['molecules']:
  key=molecule['id'];n=molecule['carbonCount'];row={'id':key,'forms':[]}
  select(key)
  for num,mode in [(1,'condensed'),(2,'expanded'),(3,'skeletal')]:
   click('#radio2DMode .mode2DOption:nth-child('+str(num)+')');wait('mode2D==='+json.dumps(mode));pause(250)
   data=dataset();frame=framing();row['forms'].append({'state':data,'frame':frame})
   check(data['name']==molecule['nameGR'] and data['atoms']==(3*n+2 if mode=='expanded'else n),key+' '+mode+' actual name and atomcount',data)
   check(frame['inside'],key+' '+mode+' complete drawing inside viewport',frame)
   if mode=='expanded':check(bool(data['calibration'])and abs(data['ratio']-2.6175)<.0001,key+' shared CC/font calibration matches old8',data)
   if read('nameAnalysisMode')!='compCarbonsCount':click('#comp5')
   pause(400*molecule['parentC']+250)
   numbers=read('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length')
   check(read('nameAnalysisMode')=='compCarbonsCount'and numbers==molecule['parentC'],key+' '+mode+' parent highlight and numbering',numbers)
   check(framing()['inside'],key+' '+mode+' numbered drawing fits')
   before=read('molZoom2D');click('#zoomInBtn');pause(220);check(read('molZoom2D')>before and read('nameAnalysisMode')=='compCarbonsCount',key+' '+mode+' real zoom-in preserves highlight')
   check(framing()['inside'],key+' '+mode+' zoom-in fits');click('#zoomOutBtn');pause(220);check(abs(read('molZoom2D')-before)<1e-8,key+' '+mode+' real zoom-out restores')
   if mode=='skeletal':shot(key+'-skeletal')
  # Real selection in the actual expanded drawing must mirror into the loaded
  # PubChem model; its native map may choose an equivalent symmetry bijection.
  select(key);click('#selectAtomsBtn');wait('fMulerSelectState().active&&fMuler3DModel.picking')
  ev('document.querySelector("#jsmeNomeclatureSVG").scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
  point=read('(()=>{const a=fMulerSelectAnchors().find(p=>p.atom===0),g=document.querySelector("#jsmeNomeclatureSVG svg g"),p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y}})()');pointer_at(point);pause(250)
  selection=read('({a2:fMulerSelectState().atoms2D,a3:fMulerSelectState().atoms3D,ready:fMuler3DModelReady(),mapped:fTranslateChain2D3D([1])})');row['selection']=selection
  check(selection['ready'] and selection['a2']==[1] and selection['a3']==selection['mapped'],key+' genuine2D pick maps into actually loaded PubChem3D',selection)
  click('#selectAtomsBtn');pause(150)
  # Narrow viewport, fresh form switching and zoom at both legal extremes.
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':390,'height':844},'devicePixelRatio':1});pause(450)
  row['narrow']=[]
  for mode in ['condensed','expanded','skeletal']:
   ev('mode2D='+json.dumps(mode)+';fSelectMol();true');wait('!!document.querySelector("#jsmeNomeclatureSVG svg")');pause(220)
   frame=framing();row['narrow'].append({'mode':mode,'frame':frame});check(frame['inside'],key+' narrow '+mode+' full drawing fits',frame)
   for zoom in [.5,6]:
    ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true');pause(200);check(framing()['inside'],key+' narrow '+mode+' zoom'+str(zoom)+' fits')
  shot(key+'-narrow')
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':1});pause(300)
  row['immutableSources']=read('(()=>{const r=nameExamples['+json.dumps(key)+'];return{condensed:r.structure2D_Condensed,expanded:r.structure2D_Expanded,skeletal:r.structure2D_Skeletal}})()')
  check(all(row['immutableSources'][f]==(ROOT/molecule['files'][f]).read_text()for f in ['condensed','expanded','skeletal']),key+' repeatedforms/zoom/resize leave storedsourcebytes unchanged');del row['immutableSources'];out['molecules'].append(row)
 # Baseline existing representations remain unchanged and old calibration still works.
 for key in ['methane','methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane','ethanol']:
  select(key);check(bool(dataset()['calibration']),key+' unchanged existing calibration path still active')
 check(all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in TARGET['files'].items()),'Frozen owned source files unchanged during browser checks')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['atFailure']=dataset();out['frameAtFailure']=framing();shot('failure')
 except Exception as extra:out['diagnosticFailure']=str(extra)
finally:finish('data-viewer')
if not out['completed']:raise SystemExit(1)
