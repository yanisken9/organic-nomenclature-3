"""Actual v52 naming, graph-order independence, guard boundaries and old-library regression.

Use --baseline with the task-start source snapshot. Evidence is written under
--output only. Requires the macOS JavaScriptCore helper, not Node or RDKit.
"""
from pathlib import Path
import argparse, json, random, subprocess

FILES = ['js/jsme-nick-nomeclature-moc2-data_52.js', 'js/mulermoc-nom-core-52.js',
         'js/mulermoc-nom-molview-52.js']
PREFIX = 'var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
TAIL = r'''
selectedMol=key; mode2D=mode; mainChainMode=chainMode;
var text=window.MOL2D[key] && window.MOL2D[key][mode], aa,bb;
if(probe){
  aa=probe.types.map(label=>({label})); bb=probe.edges.map(b=>({atoms:b.slice(0,2),order:b[2]}));
  nameExamples[key]={};
}else{
  var ls=text.split('\n'),na=+ls[3].slice(0,3),nb=+ls[3].slice(3,6);
  aa=ls.slice(4,4+na).map(l=>({label:l.slice(31,34).trim()}));
  bb=ls.slice(4+na,4+na+nb).map(l=>({atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}));
}
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>aa.length,totalNumberOfBonds:()=>bb.length,
getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>probe?'':text};
fInitNamingProps(); fAnalyseStructure(); fDetectMolType(); fGuessName();
if(sdf){fParseSDF3D(sdf);fDetectMolType3D();fCalcMainChain3D();fMatchNumberedMainChain3D();}
return {name:currentMolName,common:currentMolCommonName,parts:nameComponentsList,
 saturatedEster:fIsAcyclicSaturatedMonoesterGraph(atomConnectivityList,allAtomsTypeList,bondList),
 series:fGetMoleculeClassification().seriesKey,chain:mainChainAtomsList,
 signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),
 signature3:sdf?fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D):null,
 acidCount:esterInfo?esterInfo.acidLen:null,acidParent:esterInfo?fGetEsterAcidParentChain():null,
 acidParent3:sdf&&esterInfo?fGetEsterAcidParentChain3D():null,
 alcohol:esterInfo?fGetEsterAlcoholChain():null,alcohol3:sdf&&esterInfo?fGetEsterAlcoholChain3D():null,
 branches:fGetHydrocarbonSubstituentInfo(),branchHighlight:fGetHydrocarbonBranchHighlight(1)};
'''


def jsc(code):
    p = subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                        '-e', 'eval(JSON.parse(readline()))'], input=json.dumps(code)+'\n',
                       text=True, capture_output=True)
    assert p.returncode == 0, (p.stdout, p.stderr)
    return json.loads(p.stdout)


def run(baseline, output):
    specs = json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
    old = PREFIX+'\n'.join((baseline/p).read_text() for p in FILES)
    new = PREFIX+'\n'.join(Path(p).read_text() for p in FILES)
    # Old regression compares existing naming outputs/selected parents, not new
    # viewer helper functions. New molecules additionally exercise both graphs.
    old_tail = TAIL[:TAIL.index('return {name:')]+'''return {name:currentMolName,common:currentMolCommonName,
      parts:nameComponentsList,series:fGetMoleculeClassification().seriesKey,chain:mainChainAtomsList,
      signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)};'''
    js = 'var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(new+TAIL)+');'
    js += 'var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(old+old_tail)+');'
    js += 'var after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(new+old_tail)+');'
    js += 'var oldInventory=(new Function('+json.dumps(old+';return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));')+'))();'
    js += '''var regression=0;for(const [k,m] of oldInventory)for(const cm of ['algorithmic','data']){
      const a=before(k,m,cm,'',null),b=after(k,m,cm,'',null);
      if(JSON.stringify(a)!==JSON.stringify(b))throw Error('Old naming changed:'+JSON.stringify([k,m,cm,a,b]));regression++;
    } var rows=[];'''
    rng = random.Random(20261029)
    for s in specs:
        sdf = Path('mols/nomeclature-moc2', s['key']+'_3D.sdf').read_text()
        for mode in ['condensed', 'expanded', 'skeletal']:
            for cm in ['algorithmic', 'data']:
                args = [s['key'], mode, cm, sdf, None]
                js += 'rows.push({key:'+json.dumps(s['key'])+',mode:'+json.dumps(mode)+',chainMode:'+json.dumps(cm)+',value:run('+','.join(json.dumps(x) for x in args)+')});'
        for i in range(16):
            order = list(range(s['carbons']+2)); rng.shuffle(order)
            mapping = {old+1: new+1 for new, old in enumerate(order)}
            probe = {'types': [('C' if j < s['carbons'] else 'O') for j in order],
                     'edges': [[mapping[a], mapping[b], o] for a, b, o in s['edges']]}
            rng.shuffle(probe['edges'])
            js += 'rows.push({key:'+json.dumps(s['key'])+',mode:"permutation",value:run('+','.join(json.dumps(x) for x in [s['key'], 'condensed', 'algorithmic', '', probe])+')});'
    # Guard negatives use real graph motifs; malformed/overvalent cases are
    # intentionally passed directly rather than sanitized by a chemistry tool.
    cases = [
        ('acid', ['C','O','O'], [[1,2,2],[1,3,1]], False),
        ('lactone', ['C','C','C','O','O'], [[1,2,1],[2,3,1],[3,4,1],[4,1,1],[1,5,2]], False),
        ('cyclicAlcoholSide', ['C','O','O','C','C','C'], [[1,2,2],[1,3,1],[3,4,1],[4,5,1],[5,6,1],[6,4,1]], False),
        ('unsaturatedEster', ['C','C','C','O','O','C'], [[1,2,2],[2,3,1],[3,4,2],[3,5,1],[5,6,1]], False),
        ('hydroxyEster', ['C','O','O','C','O'], [[1,2,2],[1,3,1],[3,4,1],[4,5,1]], False),
        ('diester', ['C','O','O','C','O','O','C'], [[1,2,2],[1,3,1],[3,4,1],[4,5,2],[4,6,1],[6,7,1]], False),
        ('disconnected', ['C','O','O','C','C'], [[1,2,2],[1,3,1],[3,4,1]], False),
        ('overvalent', ['C','O','O','C','C','C'], [[1,2,2],[1,3,1],[3,4,1],[1,5,1],[1,6,1]], False),
        ('badOH', ['C','O','O','C','H'], [[1,2,2],[1,3,1],[3,4,1],[3,5,1]], False),
        ('methylFormate', ['C','O','O','C'], [[1,2,2],[1,3,1],[3,4,1]], True),
        ('explicitHMethylFormate', ['C','O','O','C','H','H','H','H'], [[1,2,2],[1,3,1],[3,4,1],[1,5,1],[4,6,1],[4,7,1],[4,8,1]], True),
    ]
    for s in specs:
        cases.append((s['key'], ['C']*s['carbons']+['O','O'], s['edges'], True))
    guard = new+''';const conn=types.map(()=>[]);for(const [a,b,o] of edges){conn[a-1].push(b-1);conn[b-1].push(a-1);}
       return fIsAcyclicSaturatedMonoesterGraph(conn,types,edges);'''
    js += 'var guard=new Function("types","edges",'+json.dumps(guard)+');var guards=[];'
    for label, types, edges, expected in cases:
        js += 'if(guard('+json.dumps(types)+','+json.dumps(edges)+')!=='+json.dumps(expected)+')throw Error('+json.dumps('Guard:'+label)+');guards.push('+json.dumps(label)+');'
    frame = ';return fGetUniform2DLibraryFrame();'
    js += 'print(JSON.stringify({rows,regression,oldMolecules:new Set(oldInventory.map(p=>p[0])).size,guards,frameBefore:(new Function('+json.dumps(old+frame)+'))(),frameAfter:(new Function('+json.dumps(new+frame)+'))()}));'
    result = jsc(js)
    by_key = {s['key']: s for s in specs}
    for row in result['rows']:
        s = by_key[row['key']]; v = row['value']
        assert v['name'] == s['name'] and v['series'] == 'ester', (row['key'], row['mode'], v)
        assert v['saturatedEster'], row
        assert len(v['chain']) == s['parent'] and v['acidCount'] == s['acidCarbons']
        assert v['acidParent'] == v['chain']
        assert len(v['alcohol']) == s['carbons']-s['acidCarbons']
        if row['mode'] != 'permutation':
            assert v['signature'] == v['signature3'], row
            assert len(v['acidParent3']) == s['parent']
            assert len(v['alcohol3']) == len(v['alcohol'])
            assert not set(v['acidParent3']) & set(v['alcohol3'])
        expected_locants = [] if s['acidCarbons'] == s['parent'] else ([2] if s['parent'] == 3 else [2,3])
        assert sorted(b['locant'] for b in v['branches']) == expected_locants, row
        if expected_locants:
            assert len(v['branchHighlight']['atoms']) == len(expected_locants)*(4 if row['mode'] == 'expanded' else 1), row
    assert result['oldMolecules'] == 136
    assert result['frameBefore'] == result['frameAfter'], (result['frameBefore'], result['frameAfter'])
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('PASS', len(result['rows']), 'new cases;', result['regression'], 'old cases;', len(result['guards']), 'guard cases')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.baseline, args.output)
