"""Bounded Main54 core sync checks; Python stdlib + macOS JavaScriptCore.

Run from repository root. Original52 is the preserved comparison target.
No dependencies installed; writes only the explicitly selected evidence file.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import random

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
ROOT = Path(__file__).resolve().parents[4]
PREFIX = '''var window={},console={log(){},warn(){},error(){}};
var selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet;
'''
TAIL = r'''
function assert(v,label){if(!v)throw Error(label)}
function load(text){
 const lines=text.split(/\r?\n/), n=+lines[3].slice(0,3), b=+lines[3].slice(3,6);
 const aa=lines.slice(4,4+n).map(l=>({label:l.slice(31,34).trim()}));
 const bb=lines.slice(4+n,4+n+b).map(l=>({atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}));
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>n,totalNumberOfBonds:()=>b,
  getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>text};
 fAnalyseStructure();fDetectMolType();
}
function state(){return {name:currentMolName,common:currentMolCommonName,
 parts:nameComponentsList,series:fGetMoleculeClassification().seriesKey,
 chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),
 branches:fGetHydrocarbonSubstituentInfo()}}
selectedMol=key; mode2D=mode;mainChainMode=cm;
if(task==='inventory')return Object.keys(window.MOL2D).map(k=>({key:k,file3D:nameExamples[k].file3D||('mols/nomeclature-moc2/'+k+'_3D.sdf'),
 modes:Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m])}));
if(task==='invalid')return [fParseMolV2000(null),fParseMolV2000('bad'),
 fStripHydrogensMol('bad'),fGenExpandedMol('bad'),fLinearizeMol('bad',[]),fZigzagMol('bad',[])];
if(task==='guard'){
 const {kind,types,edges}=extra,conn=types.map(()=>[]);
 edges.forEach(([a,b])=>{conn[a-1].push(b-1);conn[b-1].push(a-1)});
 return ({acid:fIsAcyclicSaturatedMonoacidGraph,unsaturated:fIsAcyclicUnsaturatedAcidGraph,
  ester:fIsAcyclicSaturatedMonoesterGraph})[kind](conn,types,edges);
}
if(task==='mapProbe'){
 allAtomsTypeList=extra.types2;bondList=extra.bonds2;
 allAtomsTypeList3D=extra.types3;bondList3D=extra.bonds3;
 const exact=fBuildHeavyMap2D3D(false),relaxed=fBuildHeavyMap2D3D(true);
 return {exact:!!exact,relaxed:!!relaxed};
}
if(task==='spProbe'){
 const source=fWriteMolV2000([],extra.atoms,extra.bonds);
 const result=fParseMolV2000(fLinearizeMol(source,extra.chain));
 const c=result.atoms[extra.center-1];
 const ns=result.bonds.filter(b=>b[0]===extra.center||b[1]===extra.center)
  .map(b=>result.atoms[(b[0]===extra.center?b[1]:b[0])-1]);
 const [a,b]=ns,ux=a.x-c.x,uy=a.y-c.y,vx=b.x-c.x,vy=b.y-c.y;
 const cosine=(ux*vx+uy*vy)/(Math.hypot(ux,uy)*Math.hypot(vx,vy));
 assert(Math.abs(cosine+1)<0.0001,'terminal sp axis:'+JSON.stringify(extra));
 assert(JSON.stringify(result.bonds)===JSON.stringify(extra.bonds),'terminal sp topology');
 return {chain:extra.chain,cosine,atoms:result.atoms};
}
let source=window.MOL2D[key][mode];
if(task==='probe'){
 source=fWriteMolV2000([],extra.types.map((el,i)=>({el,x:i,y:0})),extra.edges);
 nameExamples[key]={};
}
load(source);
if(task!=='cold')fInitNamingProps();
fGuessName();
const answer=state();
if(task==='name'||task==='cold'||task==='probe')return answer;
if(task==='map'){
 fParseSDF3D(extra);fDetectMolType3D();fCalcMainChain3D();fMatchNumberedMainChain3D();
 const map=fBuildHeavyMap2D3D(false),translated=fTranslateChain2D3D(mainChainAtomsList);
 const heavy=allAtomsTypeList.map((t,i)=>t!=='H'?i:-1).filter(i=>i>=0);
 let exact=!!map;
 if(map){
  assert(new Set(heavy.map(i=>map.arr[i])).size===heavy.length,'map bijection:'+key);
  for(const i of heavy)assert(allAtomsTypeList[i]===allAtomsTypeList3D[map.arr[i]],'map element:'+key);
  const B=fHeavyAdj2D3D(allAtomsTypeList3D,bondList3D);
  for(const [a,b,o] of bondList){if(allAtomsTypeList[a-1]==='H'||allAtomsTypeList[b-1]==='H')continue;
   assert((B.adj[map.arr[a-1]]||[]).includes(map.arr[b-1]),'map edge:'+key);
   assert(fOrderOf2D3D(B.ord,map.arr[a-1],map.arr[b-1])===o,'map order:'+key);
  }
 }
 const signature3=fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D);
 const mappedPool=mainChainPool.map(p=>fTranslateChain2D3D(p.chain));
 if(map){
  assert(mappedPool.every(p=>p),'every pool chain maps:'+key);
  assert(new Set(mappedPool.map(p=>JSON.stringify(p))).size===
   new Set(mainChainPool.map(p=>JSON.stringify(p.chain))).size,'distinct chains remain distinct:'+key);
 }
 return {key,mode,cm,exact,translated,chain3:mainChainAtoms3D,
  signatureMatches:answer.signature===signature3,pool:mainChainPool.map(p=>p.chain),
  mappedPool};
}
if(task==='generate'){
 const parsed=fParseMolV2000(source),stripped=fStripHydrogensMol(source);
 if(!stripped){
  assert(fGenExpandedMol(source)===null&&fLinearizeMol(source,mainChainAtomsList)===null&&
   fZigzagMol(source,mainChainAtomsList)===null,'unsupported input fails closed:'+key);
  return {key,mode,unsupported:true,results:[]};
 }
 const heavy=fParseMolV2000(stripped);
 const ids={};let next=0;
 parsed.atoms.forEach((a,i)=>{if(a.el!=='H')ids[i+1]=++next});
 const heavyChain=mainChainAtomsList.map(i=>ids[i]);
 function graph(m){return JSON.stringify([m.atoms.filter(a=>a.el!=='H').map(a=>a.el),
  m.bonds.filter(b=>m.atoms[b[0]-1].el!=='H'&&m.atoms[b[1]-1].el!=='H')])}
 const graphKey=graph(heavy),variants={
  linear:fLinearizeMol(stripped,heavyChain),zigzag:fZigzagMol(stripped,heavyChain),
  expanded:fGenExpandedMol(stripped)};
 function findBentSp(m){
  const bent=[];
  m.atoms.forEach((a,i)=>{
   if(a.el!=='C')return;
   const bs=m.bonds.filter(b=>b[0]===i+1||b[1]===i+1);
   if(bs.length!==2||!bs.some(b=>b[2]===3))return;
   const ends=bs.map(b=>m.atoms[(b[0]===i+1?b[1]:b[0])-1]);
   const [p,q]=ends,ux=p.x-a.x,uy=p.y-a.y,vx=q.x-a.x,vy=q.y-a.y;
   const cosine=(ux*vx+uy*vy)/(Math.hypot(ux,uy)*Math.hypot(vx,vy));
   if(Math.abs(cosine+1)>0.0001)bent.push({atom:i+1,cosine});
  });
  return bent;
 }
 const inputBentSp=findBentSp(heavy);
 const results=[];
 for(const [kind,text] of Object.entries(variants)){
  assert(text,'generator null:'+key+':'+kind);
  const m=fParseMolV2000(text);
  assert(m.atoms.every(a=>Number.isFinite(a.x)&&Number.isFinite(a.y)),'coordinates:'+key);
  const strippedVariant=fStripHydrogensMol(text);
  assert(graph(fParseMolV2000(strippedVariant))===graphKey,'heavy graph:'+key+':'+kind);
  if(kind==='expanded')assert(JSON.stringify(fParseMolV2000(fGenExpandedMol(text)))===JSON.stringify(m),
    'expanded graph/coordinate idempotence:'+key);
  if(kind==='linear'){
   assert(fLinearizeMol(stripped,heavyChain)===text,'linear determinism:'+key);
   assert(heavyChain.every(i=>m.atoms[i-1].y===0),'linear chain:'+key);
  }
  if(kind==='zigzag')assert(fZigzagMol(stripped,heavyChain)===text,'zigzag determinism:'+key);
  const bentSp=findBentSp(m);
  const newBentSp=bentSp.filter(b=>!inputBentSp.some(a=>a.atom===b.atom&&Math.abs(a.cosine-b.cosine)<0.0001));
  load(text);mainChainMode='algorithmic';fGuessName();
  results.push({kind,name:currentMolName,heavyAtoms:heavy.atoms.length,atoms:m.atoms.length,
   sameName:currentMolName===answer.name,bentSp,newBentSp,
   signatureMatches:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===answer.signature});
 }
 return {key,mode,inputBentSp,results};
}
if(task==='reorderedMap'){
 // Explicitly reorder the SDF atom positions; reverse atom order and bond order.
 const m=fParseMolV2000(extra),n=m.atoms.length;
 const atoms=m.atoms.slice().reverse();
 const bonds=m.bonds.slice().reverse().map(([a,b,o])=>[n+1-b,n+1-a,o]);
 fParseSDF3D(fWriteMolV2000(m.head,atoms,bonds));
 const map=fBuildHeavyMap2D3D(false);
 if(!map)return {key,mode,exact:false};
 const B=fHeavyAdj2D3D(allAtomsTypeList3D,bondList3D);
 for(const [a,b,o] of bondList){if(allAtomsTypeList[a-1]==='H'||allAtomsTypeList[b-1]==='H')continue;
  assert((B.adj[map.arr[a-1]]||[]).includes(map.arr[b-1])&&
    fOrderOf2D3D(B.ord,map.arr[a-1],map.arr[b-1])===o,'reordered edge:'+key);
 }
 return {key,mode,exact:true,heavyAtoms:map.arr.filter(i=>i!=null).length};
}
throw Error('unknown task:'+task);
'''


def jsc(code):
    p = subprocess.run([JSC, '-e', 'eval(JSON.parse(readline()))'],
                       input=json.dumps(code)+'\n', text=True, capture_output=True)
    if p.returncode:
        raise AssertionError((p.returncode, p.stdout[-6000:], p.stderr[-2000:]))
    return json.loads(p.stdout)


def run(data54, output):
    data52 = ROOT/'js/jsme-nick-nomeclature-moc2-data_52.js'
    core52 = ROOT/'js/mulermoc-nom-core-52.js'
    core54 = ROOT/'js/mulermoc-nom-core-54.js'
    sources = {'before': PREFIX+data52.read_text()+'\n'+core52.read_text(),
               'after': PREFIX+data54.read_text()+'\n'+core54.read_text()}
    js = ''.join('var '+k+'=new Function("task","key","mode","cm","extra",'+
                 json.dumps(v+'\n'+TAIL)+');' for k, v in sources.items())
    js += '''var originalAfter=after;after=function(...args){try{return originalAfter(...args)}
      catch(e){throw Error(JSON.stringify(args.slice(0,4))+':'+e.message+' '+e.stack)}};'''
    inventory = jsc(js+'print(JSON.stringify(before("inventory")));')
    sdfs = {row['key']: (ROOT/row['file3D']).read_text() for row in inventory}
    # Existing approved local specifications are semantic oracles, not just
    # a comparison of two implementations that might share the same defect.
    specs = sum((json.loads((ROOT/'docs/checks'/f).read_text()) for f in [
        'acids-specs-20261028.json', 'other-acids-specs-20261028.json',
        'two-enynoic-acids-specs-20261028.json', 'esters-specs-20261029.json']), [])
    probes = []
    rng = random.Random(20261104)
    for spec in specs:
        types = ['C']*spec['carbons']+['O']*(len(spec['xy'])-spec['carbons'])
        for _ in range(16):
            order = list(range(len(types)))
            rng.shuffle(order)
            mapping = {old+1: new+1 for new, old in enumerate(order)}
            edges = [[mapping[a], mapping[b], o] for a, b, o in spec['edges']]
            rng.shuffle(edges)
            probes.append({'key': spec['key'], 'name': spec['name'], 'parent': spec['parent'],
                           'types': [types[i] for i in order], 'edges': edges})
    guards = [
        ['acid', 'methanoic acid', ['C','O','O'], [[1,2,2],[1,3,1]], True],
        ['acid', 'explicit hydroxyl', ['C','O','O','H'], [[1,2,2],[1,3,1],[3,4,1]], True],
        ['acid', 'ester excluded', ['C','O','O','C'], [[1,2,2],[1,3,1],[3,4,1]], False],
        ['acid', 'hydroxyacid excluded', ['C','C','O','O','O'], [[1,2,1],[1,3,2],[1,4,1],[2,5,1]], False],
        ['acid', 'nitrogen excluded', ['C','C','O','O','N'], [[1,2,1],[1,3,2],[1,4,1],[2,5,1]], False],
        ['unsaturated', 'monoacid', ['C','C','C','O','O'], [[1,2,1],[2,3,2],[1,4,2],[1,5,1]], True],
        ['unsaturated', 'saturated excluded', ['C','C','O','O'], [[1,2,1],[1,3,2],[1,4,1]], False],
        ['unsaturated', 'cyclic excluded', ['C','C','C','C','O','O'], [[1,2,1],[2,3,2],[3,4,1],[4,2,1],[1,5,2],[1,6,1]], False],
        ['unsaturated', 'hydroxyacid excluded', ['C','C','C','O','O','O'], [[1,2,1],[2,3,2],[1,4,2],[1,5,1],[3,6,1]], False],
        ['ester', 'methyl formate', ['C','O','O','C'], [[1,2,2],[1,3,1],[3,4,1]], True],
        ['ester', 'acid excluded', ['C','O','O'], [[1,2,2],[1,3,1]], False],
        ['ester', 'lactone excluded', ['C','C','C','O','O'], [[1,2,1],[2,3,1],[3,4,1],[4,1,1],[1,5,2]], False],
        ['ester', 'unsaturated excluded', ['C','C','C','O','O','C'], [[1,2,2],[2,3,1],[3,4,2],[3,5,1],[5,6,1]], False],
        ['ester', 'disconnected excluded', ['C','O','O','C','C'], [[1,2,2],[1,3,1],[3,4,1]], False],
        ['ester', 'overvalent excluded', ['C','O','O','C','C','C'], [[1,2,2],[1,3,1],[3,4,1],[1,5,1],[1,6,1]], False],
    ]
    map_probes = [
        {'label': 'element mismatch', 'types2': ['C','O'], 'bonds2': [[1,2,1]],
         'types3': ['C','N'], 'bonds3': [[1,2,1]], 'expected': {'exact': False, 'relaxed': False}},
        {'label': 'bond order mismatch', 'types2': ['C','O'], 'bonds2': [[1,2,1]],
         'types3': ['O','C'], 'bonds3': [[1,2,2]], 'expected': {'exact': False, 'relaxed': True}},
        {'label': 'degree mismatch', 'types2': ['C']*4, 'bonds2': [[1,2,1],[2,3,1],[3,4,1]],
         'types3': ['C']*4, 'bonds3': [[1,2,1],[1,3,1],[1,4,1]],
         'expected': {'exact': False, 'relaxed': False}},
        {'label': 'symmetric reorder', 'types2': ['C','O','C'], 'bonds2': [[1,2,1],[2,3,1]],
         'types3': ['C','C','O'], 'bonds3': [[3,1,1],[2,3,1]],
         'expected': {'exact': True, 'relaxed': True}},
    ]
    js += 'const sdfs='+json.dumps(sdfs)+';const inventory=before("inventory");'
    js += 'const probes='+json.dumps(probes)+';const guards='+json.dumps(guards)+';'
    js += 'const mapProbes='+json.dumps(map_probes)+';'
    sp_probes = []
    for atoms, bonds, center, chains in [
        (['C','C','N'], [[1,2,1],[2,3,3]], 2, [[1,2],[2,1]]),
        (['N','C','C'], [[1,2,3],[2,3,1]], 2, [[3,2],[2,3]]),
    ]:
        for chain in chains:
            sp_probes.append({'atoms': [{'el': el, 'x': i*1.17, 'y': 0} for i, el in enumerate(atoms)],
                              'bonds': bonds, 'center': center, 'chain': chain})
    js += 'const spProbes='+json.dumps(sp_probes)+';'
    js += r'''
const regression=[],maps=[],cold=[],generated=[],reordered=[],differences=[];
for(const row of inventory){
 for(const mode of row.modes){for(const cm of ['algorithmic','data']){
  const a=before('name',row.key,mode,cm),b=after('name',row.key,mode,cm);
  if(JSON.stringify(a)!==JSON.stringify(b))differences.push({key:row.key,mode,cm,before:a,after:b});
  regression.push({key:row.key,mode,cm,name:b.name,chain:b.chain,series:b.series});
  const c=after('cold',row.key,mode,cm);
  if(JSON.stringify(b)!==JSON.stringify(c))throw Error('cold naming mismatch:'+row.key+':'+mode+':'+cm);
  cold.push([row.key,mode,cm]);
  maps.push(after('map',row.key,mode,cm,sdfs[row.key]));
 }
 generated.push(after('generate',row.key,mode,'algorithmic'));
 reordered.push(after('reorderedMap',row.key,mode,'algorithmic',sdfs[row.key]));
 }
}
const probeResults=probes.map(p=>{
 const result=after('probe',p.key,'condensed','algorithmic',p);
 if(result.name!==p.name||result.chain.length!==p.parent)throw Error('permutation oracle:'+JSON.stringify([p,result]));
 return {key:p.key,name:result.name,parent:result.chain.length};
});
const guardResults=guards.map(([kind,label,types,edges,expected])=>{
 const result=after('guard','methane','condensed','algorithmic',{kind,types,edges});
 if(result!==expected)throw Error('guard:'+kind+':'+label);
 return {kind,label,expected,result};
});
const mapProbeResults=mapProbes.map(p=>{
 const result=after('mapProbe','probe','condensed','algorithmic',p);
 if(JSON.stringify(result)!==JSON.stringify(p.expected))throw Error('map probe:'+p.label);
 return {label:p.label,result};
});
const spProbeResults=spProbes.map(p=>after('spProbe','probe','condensed','algorithmic',p));
print(JSON.stringify({inventory,regression,differences,maps,cold,generated,reordered,probeResults,guardResults,mapProbeResults,spProbeResults,
 invalid:after('invalid','methane','condensed','algorithmic')}));
'''
    result = jsc(js)
    result['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [data52, data54, core52, core54]}
    summary = {
        'molecules': len(inventory),
        'namingParentRegressionCases': len(result['regression']),
        'namingParentDifferences': len(result['differences']),
        'coldInitCases': len(result['cold']),
        'exactMaps': sum(row['exact'] for row in result['maps']),
        'mapCases': len(result['maps']),
        'signatureMismatches': [row for row in result['maps'] if not row['signatureMatches']],
        'untranslatedMaps': [row for row in result['maps'] if row['translated'] is None],
        'generatorCases': sum(len(row['results']) for row in result['generated']),
        'generatorNamingDifferences': [row for row in result['generated']
                                       if any(not v['sameName'] for v in row['results'])],
        'reorderedGraphMaps': len(result['reordered']),
        'reorderedGraphMapFailures': [row for row in result['reordered'] if not row['exact']],
        'invalidInputChecks': len(result['invalid']),
        'chemicalOraclePermutationCases': len(result['probeResults']),
        'chemicalGuardCases': len(result['guardResults']),
        'mapBoundaryCases': len(result['mapProbeResults']),
        'generatorBentSp': [{**row, 'results': [v for v in row['results'] if v['bentSp']]}
                           for row in result['generated'] if any(v['bentSp'] for v in row['results'])],
        'generatorNewBentSp': [{**row, 'results': [v for v in row['results'] if v['newBentSp']]}
                              for row in result['generated'] if any(v['newBentSp'] for v in row['results'])],
        'terminalSpDirectionCases': len(result['spProbeResults']),
        'unsupportedGeneratorSources': [row for row in result['generated'] if row.get('unsupported')],
    }
    result['summary'] = summary
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    assert len(inventory) == 141
    expected_names = {'Oxopropanoic_acid': '2-οξοπροπανικό οξύ',
                      'oxobutanoic_acid': '4-οξοβουτανικό οξύ'}
    assert len(result['differences']) == 12
    for diff in result['differences']:
        assert diff['after']['name'] == expected_names[diff['key']]
        for field in ['chain', 'signature', 'branches', 'common']:
            assert diff['before'][field] == diff['after'][field], (diff['key'], field)
    # The one inherited literal [H] MOL label needs real-JSME confirmation.
    # Keep this raw-MOL limitation explicit; never silently coerce source labels.
    assert len(summary['untranslatedMaps']) == 2
    assert all(row['key']=='penten_3_yne_1' and row['mode']=='expanded'
               for row in summary['untranslatedMaps'])
    assert summary['exactMaps'] == summary['mapCases']-2
    assert summary['reorderedGraphMapFailures'] == [
        {'key': 'penten_3_yne_1', 'mode': 'expanded', 'exact': False}]
    assert not summary['signatureMismatches']
    assert not summary['generatorNamingDifferences']
    assert not summary['generatorNewBentSp']
    assert result['invalid'] == [None]*6


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data54', type=Path, default=ROOT/'js/jsme-nick-nomeclature-moc2-data_52.js')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('core54-results.json'))
    args = parser.parse_args()
    run(args.data54.resolve(), args.output)
