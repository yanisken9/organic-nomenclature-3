"""Actual upstream55/current54/candidate55 probes for CV55-01/02/03.
No browser. Historical test bodies reused without rewriting old output files.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,subprocess,datetime
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
C=Path(argparse.ArgumentParser().parse_known_args()[1][0]);J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def literal(path,name):
 tree=ast.parse(path.read_text())
 for n in tree.body:
  if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name:return ast.literal_eval(n.value)
def run(js):
 r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout[-3000:],r.stderr[-1000:]);return json.loads(r.stdout)
paths={'current54':P/'js/mulermoc-nom-core-54.js','upstream55':P/'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-core-55.js','candidate55':C/'js/mulermoc-nom-core-55.js'}
prefix='var window={},selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet,console={log(){},warn(){},error(){}};\n'
data=(P/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()
body=literal(P/'docs/checks/v54-sync-20261104/core/test-core54.py','TAIL')
src=''.join('var '+k+'=new Function("task","key","mode","cm","extra",'+json.dumps(prefix+data+'\n'+p.read_text()+'\n'+body)+');'for k,p in paths.items())
probes=r'''
function invoke(fn,x){try{return{status:'named',result:fn('probe','ethane','condensed','algorithmic',x)}}catch(e){return{status:'declined',error:String(e)}}}
function chain(){return{types:Array(7).fill('C'),edges:Array.from({length:6},(_,i)=>[i+1,i+2,1])}}
const fork=chain();fork.types.push('C','C','C','Cl');fork.edges.push([4,8,1],[8,9,1],[8,10,1],[8,11,1]);
const halo=chain();halo.types.push('C','Cl','Cl','Cl');halo.edges.push([4,8,1],[8,9,1],[2,10,1],[6,11,1]);
const nitro=chain();nitro.types.push('C');nitro.edges.push([4,8,1]);
for(const at of [8,2,6]){const n=nitro.types.length+1;nitro.types.push('N','O','O');nitro.edges.push([at,n,1],[n,n+1,2],[n,n+2,1])}
const supported=[];for(const len of [1,2,3]){const x=chain();for(let i=0;i<len;i++){x.types.push('C');x.edges.push([i?7+i:4,8+i,1])}x.types.push('Cl');x.edges.push([7+len,8+len,1]);supported.push(x)}
const output={};for(const [k,fn]of [['current54',current54],['upstream55',upstream55],['candidate55',candidate55]])output[k]={fork:invoke(fn,fork),halo:invoke(fn,halo),nitro:invoke(fn,nitro),supported:supported.map(x=>invoke(fn,x))};print(JSON.stringify(output));
'''
result=run(src+probes)
assert result['upstream55']['fork']['status']=='named' and 'αιθυλο' in result['upstream55']['fork']['result']['name']
assert result['candidate55']['fork']['status']=='declined' and 'off main chain' in result['candidate55']['fork']['error']
assert 'διδιχλωρο' in result['upstream55']['halo']['result']['name']
assert result['candidate55']['halo']['result']['name']=='2,6-διχλωρο-4-χλωρομεθυλοεπτάνιο'
assert 'διδινιτρο' in result['upstream55']['nitro']['result']['name']
assert result['candidate55']['nitro']['result']['name']=='2,6-δινιτρο-4-νιτρομεθυλοεπτάνιο'
assert all(x['status']=='named'for x in result['candidate55']['supported'])
# Entire historical counts/body fixture, with the current input bytes shared.
body=literal(P/'docs/checks/v54-merge-20261105/core/test-counts-metadata-terminal.py','BODY')
data+='\nconst actualLegacySDF='+json.dumps((P/'mols/nomeclature-moc2/pentyn_4_one_2_3D.sdf').read_text())+';\n'
src=''.join('var '+k+'=new Function('+json.dumps(prefix+data+'\n'+p.read_text()+'\n'+body)+');'for k,p in paths.items())
counts=run(src+'print(JSON.stringify({current54:current54(),upstream55:upstream55(),candidate55:candidate55()}));')
a=counts['candidate55'];assert a['standard']and a['short']and a['shortAtoms']==3
assert a['contiguous101100']['standard']==[101,100]and a['contiguous101100']['short']==[101,100]
assert a['legacy']['storedPentyn']==[12,11]and not a['legacy']['v3000']
assert all(not x['standard']and not x['short']for x in a['invalid'].values())
assert all(x['parsed']and x['roundtrip']for x in a['metadata'].values())
assert all(abs(x['angle']-180)<1e-4 and x['bondsPreserved']for x in a['nitriles'])
assert all(abs(x['etherAngle']-180)<1e-4 for x in a['terminal'][2:])
assert a['stereo']=={'parityParsed':True,'parityRejected':True,'wedgeParsed':True,'wedgeRejected':True}
def funcs(t):
 ms=list(re.finditer(r'^function ([\w$]+)\(',t,re.M));return{m.group(1):t[m.start():ms[i+1].start()if i+1<len(ms)else len(t)]for i,m in enumerate(ms)}
f0,f1=funcs(paths['current54'].read_text()),funcs(paths['candidate55'].read_text())
exact=['fMolCountsLine','fParseMolV2000','fWriteMolV2000','fRemapMolProperties2D','fMolCanTransform2D','fCopyMolAtom2D','fCopyMolBond2D','fAlkylGroupName','fTranslateChain2D3D','fBuildHeavyMap2D3D','fHeavyAdj2D3D','fParseSDF3D','fDetectMolType']
assert all(f0[k]==f1[k]for k in exact),[k for k in exact if f0[k]!=f1[k]]
result={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime':'macOS JavaScriptCore actual functions; no browser','naming':result,'countsMetadataTerminal':counts,'byteIdenticalLocalSafeguardFunctions':exact,'sourceSHA256':{k:hashlib.sha256(p.read_bytes()).hexdigest()for k,p in paths.items()},'passed':True}
(H/'causal-probes-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':True,'causalFindings':['CV55-01','CV55-02','CV55-03'],'exactGuardFunctions':exact},ensure_ascii=False))
