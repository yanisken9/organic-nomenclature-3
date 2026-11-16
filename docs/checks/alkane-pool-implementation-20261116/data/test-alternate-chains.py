"""Bounded actual native 1→2→1 chain-switch check; launch only with root's slot grant.

Three approved fixtures in three forms. No source/runtime writes. Uses the
existing owned run-browser.py wrapper and native pointer input. This is
Developer browser evidence, not independent review or a geometry optimizer.
"""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'browser-support.py').read_text(),'owned-alternate-chain-support','exec'))
MANIFEST=json.loads((ROOT/'data/namelecule-alkanes-v1/manifest.json').read_text())
MOLECULES={m['id']:m for m in MANIFEST['molecules']}
FIXTURES=[('methyl_2_butane',2),('dimethyl_2_2_butane',3),('dimethyl_2_2_propane',6)]
source_paths=['mulermoc-nom-57.html','js/mulermoc-nom-core-57.js','js/mulermoc-nom-molview-57.js','js/MULERMOC_namelecule_alkanes_v1_data.js','data/namelecule-alkanes-v1/manifest.json']
for key,_ in FIXTURES:
 source_paths.extend(MOLECULES[key]['files'].values());source_paths.append(MOLECULES[key]['provenance'])
out['sourceHashesAtStart']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in source_paths}
out['coverage']='3 fixtures ×3 forms; trusted chain controls1→2→1; actual alternate-carbon pick into loaded3D in Expanded only.'
out['cases']=[]

def snapshot():
 return read('''(()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),lines=[...svg.querySelectorAll('line')],inverse=svg.getCTM().inverse(),anchors=Array(allAtomsTypeList.length).fill(null);
 for(let i=0;i<bondList.length;i++){
   const[a,b,order]=bondList[i],line=lines[svgBondList[i]-1];if(order!==1||!line)throw Error('Unexpected alkane SVG bond');
   const matrix=inverse.multiply(line.getCTM());
   for(const[atom,end]of[[a,1],[b,2]]){const p=svg.createSVGPoint();p.x=Number(line.getAttribute('x'+end));p.y=Number(line.getAttribute('y'+end));const q=p.matrixTransform(matrix),point=[q.x,q.y];
     if(anchors[atom-1]&&Math.hypot(anchors[atom-1][0]-point[0],anchors[atom-1][1]-point[1])>1)throw Error('Inconsistent native atom anchor');anchors[atom-1]=point;}
 }
 if(anchors.some(p=>!p))throw Error('Missing native atom anchor');
 const heavy=allAtomsTypeList.map((el,i)=>el==='C'?i:-1).filter(i=>i>=0),first=bondList.find(([a,b])=>allAtomsTypeList[a-1]==='C'&&allAtomsTypeList[b-1]==='C'),unit=Math.hypot(anchors[first[0]-1][0]-anchors[first[1]-1][0],anchors[first[0]-1][1]-anchors[first[1]-1][1]);
 const distances=[];for(let i=0;i<heavy.length;i++)for(let j=0;j<i;j++){const a=anchors[heavy[i]],b=anchors[heavy[j]];distances.push(Math.hypot(a[0]-b[0],a[1]-b[1])/unit);}
 return {key:selectedMol,mode:mode2D,name:currentMolName,poolSize:mainChainPool.length,index:mainChainPoolIdx,counter:document.getElementById('chainStepLabel').textContent,chain:mainChainAtomsList.slice(),chain3D:mainChainAtoms3D.slice(),translated:fTranslateChain2D3D(mainChainAtomsList),modelReady:fMuler3DModelReady(),analysis:nameAnalysisMode,highlight:typeof highAtoms!=='undefined'&&Array.isArray(highAtoms)?highAtoms.slice():[],numbers:[...svg.querySelectorAll('text[id^=number]')].map(e=>({id:e.id,text:e.textContent.trim()})),symbols:allAtomsTypeList.slice(),bonds:bondList.map(b=>b.slice(0,3)),anchors,normalizedHeavyDistances:distances,viewBox:svg.getAttribute('viewBox'),source2D:nameExamples[selectedMol]['structure2D_'+({condensed:'Condensed',expanded:'Expanded',skeletal:'Skeletal'}[mode2D])]};
 })()''')

def settled(molecule):
 # Await the native animation once. Never call fShowNumbering manually while
 # its interval is active, and never click an already-selected component.
 wait('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length==='+str(molecule['parentC']),10)
 pause(160)

def inspect(state,molecule,pool,index,label):
 check(state['index']==index and state['poolSize']==pool and state['counter']==f'{index+1}/{pool}',label+' native chain index/counter',{'index':state['index'],'counter':state['counter']})
 check(state['name']==molecule['nameGR'] and len(state['chain'])==molecule['parentC'],label+' name and parent length preserved',{'name':state['name'],'chain':state['chain']})
 check(state['analysis']=='compCarbonsCount'and state['highlight']==state['chain'],label+' selected parent highlight tracks current chain',{'highlight':state['highlight'],'chain':state['chain']})
 check([x['text']for x in state['numbers']]==[str(i+1)for i in range(molecule['parentC'])],label+' native numbering is exactly1..parentC',state['numbers'])
 check(state['modelReady']and state['translated']==state['chain3D'],label+' current parent maps into actually loaded SDF',{'mapped':state['translated'],'chain3D':state['chain3D']})
 check(state['source2D']==(ROOT/molecule['files'][state['mode']]).read_text(),label+' saved input source remains byte-identical')
 check(framing()['inside'],label+' complete labels/bonds/numbers fit viewport',framing())

def numeric_delta(a,b):
 if isinstance(a,list)and isinstance(b,list):
  assert len(a)==len(b),(len(a),len(b));return max([numeric_delta(x,y)for x,y in zip(a,b)]or[0.])
 return abs(float(a)-float(b))

try:
 call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
 navigate('mulermoc-nom-57.html?audit=alkane-alternate-chains');app_ready();wait('window.JSmolReadyFlag===true',70);call('browsingContext.activate',{'context':ctx});ev('document.fonts.ready.then(()=>true)')
 for key,pool in FIXTURES:
  molecule=MOLECULES[key]
  ev('selectedMol='+json.dumps(key)+';mode2D="condensed";mainChainMode="algorithmic";fSelectMol();true');wait('fMuler3DModelReady()',50);pause(200)
  for number,mode in [(1,'condensed'),(2,'expanded'),(3,'skeletal')]:
   click('#radio2DMode .mode2DOption:nth-child('+str(number)+')');wait('mode2D==='+json.dumps(mode));wait('fMuler3DModelReady()',40);pause(200)
   check(read('mainChainPool.length')==pool,key+' '+mode+' expected pool size',read('mainChainPool.length'))
   # Mode-specific orientation can select a different equivalent pool entry.
   # Reach the first entry using the same trusted Previous control as the user.
   while read('mainChainPoolIdx')>0:
    previous=read('mainChainPoolIdx');click('#chainPrevBtn');wait('mainChainPoolIdx==='+str(previous-1));pause(120)
   if read('nameAnalysisMode')!='compCarbonsCount':click('#comp5')
   settled(molecule);baseline=snapshot();inspect(baseline,molecule,pool,0,key+' '+mode+' chain1')
   click('#chainNextBtn');wait('mainChainPoolIdx===1');settled(molecule);alternate=snapshot();inspect(alternate,molecule,pool,1,key+' '+mode+' chain2')
   check(set(alternate['chain'])!=set(baseline['chain']),key+' '+mode+' next control selects a distinct eligible parent set',{'first':baseline['chain'],'second':alternate['chain']})
   check(alternate['symbols']==baseline['symbols']and alternate['bonds']==baseline['bonds'],key+' '+mode+' topology remains identical after switch')
   delta=numeric_delta(baseline['normalizedHeavyDistances'],alternate['normalizedHeavyDistances']);check(delta<.005,key+' '+mode+' switch preserves whole-molecule geometry up to rigid display transform',delta)
   case={'key':key,'mode':mode,'expectedPool':pool,'first':baseline,'second':alternate,'geometryNormalizedMaximumDelta':delta,'secondFrame':framing()}
   if mode=='expanded':
    # Pick a carbon which belongs specifically to the alternate parent. The
    # free-selection entry intentionally clears component paint; restore it
    # through its normal button afterward, retaining the chosen parent index.
    atom=next(a for a in alternate['chain']if a not in baseline['chain'])
    click('#selectAtomsBtn');wait('fMulerSelectState().active&&fMuler3DModel.picking')
    ev('document.querySelector("#jsmeNomeclatureSVG").scrollIntoView({block:"center",behavior:"instant"});true');pause(100)
    point=read('(()=>{const a=fMulerSelectAnchors().find(p=>p.atom==='+str(atom-1)+'),g=document.querySelector("#jsmeNomeclatureSVG svg g");if(!a)throw Error("No alternate-carbon pick anchor");const p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y}})()');pointer_at(point);pause(250)
    selection=read('({atoms2D:fMulerSelectState().atoms2D,atoms3D:fMulerSelectState().atoms3D,mapped:fTranslateChain2D3D(['+str(atom)+']),index:mainChainPoolIdx,ready:fMuler3DModelReady()})');case['alternatePick']={'atom2D':atom,'state':selection}
    check(selection['ready']and selection['index']==1 and selection['atoms2D']==[atom]and selection['atoms3D']==selection['mapped'],key+' Expanded genuine alternate-parent carbon pick maps into current3D',selection)
    click('#selectAtomsBtn');pause(120)
    if read('nameAnalysisMode')!='compCarbonsCount':click('#comp5')
    settled(molecule)
   click('#chainPrevBtn');wait('mainChainPoolIdx===0');settled(molecule);returned=snapshot();inspect(returned,molecule,pool,0,key+' '+mode+' returned chain1')
   check(returned['chain']==baseline['chain']and returned['chain3D']==baseline['chain3D'],key+' '+mode+' 1→2→1 restores exact2D/3D parent ordering')
   delta=numeric_delta(baseline['anchors'],returned['anchors']);check(delta<=1,key+' '+mode+' 1→2→1 restores drawing geometry without accumulated transforms',delta)
   check(numeric_delta(baseline['normalizedHeavyDistances'],returned['normalizedHeavyDistances'])<.005,key+' '+mode+' returned whole-molecule distances preserved')
   case['returned']=returned;case['returnedGeometryMaximumDeltaSVGUnits']=delta;case['returnedFrame']=framing()
   for state in [case['first'],case['second'],case['returned']]:del state['source2D']
   out['cases'].append(case);shot(key+'-'+mode+'-returned')
 check(all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in out['sourceHashesAtStart'].items()),'Frozen runtime and molecular source hashes unchanged throughout alternate-chain checks')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:out['stateAtFailure']=snapshot();out['frameAtFailure']=framing();shot('failure')
 except Exception as extra:out['diagnosticFailure']=str(extra)
finally:finish('alternate-chains')
if not out['completed']or js_errors:raise SystemExit(1)
