"""Actual core functions: equal-top-terminal priority before/raw57/composed57.

The tiny acyclic input parser creates graphs, never chemical answers. Expectations
specify direction-free symmetry, known locant tiers and acid priority explicitly.
No browser/JSME execution or atom-reordering coercion is claimed.
"""
from pathlib import Path
import argparse, ast, datetime, hashlib, json, re, subprocess

P=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate')
J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'

def graph(s):
    atoms=[]; edges=[]; stack=[]; prev=None; order=1; i=0
    while i<len(s):
        ch=s[i]
        if ch=='(': stack.append(prev); i+=1; continue
        if ch==')': prev=stack.pop(); i+=1; continue
        if ch in '=#': order={'=':2,'#':3}[ch]; i+=1; continue
        m=re.match(r'Cl|Br|[A-Z]',s[i:]); assert m,s[i:]
        atoms.append({'el':m[0],'x':len(atoms)*1.25,'y':0})
        if prev is not None: edges.append([prev,len(atoms),order])
        prev=len(atoms); order=1; i+=len(m[0])
    return {'atoms':atoms,'edges':edges}

fixtures=[
 {'id':'chlorobutanedioic','smiles':'O=C(O)CC(Cl)C(=O)O','chain':[2,4,5,7],
  'expected':[7,5,4,2],'namePrefix':'2-χλωρο'},
 {'id':'malonic-symmetric','smiles':'O=C(O)CC(=O)O','chain':[2,4,5], 'free':True},
 {'id':'tartaric-symmetric','smiles':'O=C(O)C(O)C(O)C(=O)O','chain':[2,4,6,8], 'free':True},
 {'id':'dialdehyde-symmetric','smiles':'O=CCCC=O','chain':[2,3,4,5], 'free':True},
 {'id':'dinitrile-symmetric','smiles':'N#CCCC#N','chain':[2,3,4,5], 'free':True},
 {'id':'oxoacid-acid-C1','smiles':'O=CCCC(=O)O','chain':[2,3,4,5], 'expected':[5,4,3,2]},
 {'id':'diacid-enyne-double-low-tie','smiles':'O=C(O)C=CC#CC(=O)O',
  'chain':[2,4,5,6,7,8], 'expected':[2,4,5,6,7,8]},
 {'id':'enyne-double-low-tie','smiles':'C=CC#C','chain':[1,2,3,4], 'expected':[1,2,3,4]},
 {'id':'ene-before-halogen','smiles':'C=CCCl','chain':[1,2,3], 'expected':[1,2,3]},
]
for f in fixtures: f['graph']=graph(f['smiles'])

z=ast.parse((P/'docs/checks/v54-sync-20261104/core/test-core54.py').read_text())
shared={n.targets[0].id:ast.literal_eval(n.value) for n in z.body
        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)
        and n.targets[0].id in ['PREFIX','TAIL']}
tail=shared['TAIL'].split('selectedMol=key; mode2D=mode;mainChainMode=cm;')[0]+r'''
selectedMol='ethane';mode2D='condensed';mainChainMode='algorithmic';nameExamples.ethane={};
const source=fWriteMolV2000([],extra.graph.atoms,extra.graph.edges);
load(source);fInitNamingProps();fCalcMainChain();
const input=extra.chain.map(x=>x-1),reverse=input.slice().reverse();
const path2={forward:fOrientChainPath(input).map(x=>x+1),reverse:fOrientChainPath(reverse).map(x=>x+1)};
const originalInputUnchanged=input.every((x,i)=>x===extra.chain[i]-1);
const terminal2=Object.assign({},terminalFgCarbons);
fGuessName();const name=currentMolName,chain2=mainChainAtomsList.slice();
fParseSDF3D(source);fDetectMolType3D();fCalcMainChain3D();
const chain3BeforeMatch=mainChainAtoms3D.slice(),terminal3=Object.assign({},terminalFgCarbons3D);
const path3={forward:fOrientChainPath3D(input).map(x=>x+1),reverse:fOrientChainPath3D(reverse).map(x=>x+1)};
fMatchNumberedMainChain3D();
return {name,chain2,chain3BeforeMatch,chain3AfterMatch:mainChainAtoms3D.slice(),path2,path3,terminal2,terminal3,
 originalInputUnchanged,groups2:Object.keys(functionalGroupObj),groups3:Object.keys(functionalGroupObj3D)};
'''
sources={'before':D/'before-core57.js',
         'raw57':D.parent/'upstream/target/js/mulermoc-nom-core-57.js',
         'candidate':C/'js/mulermoc-nom-core-57.js'}
data=(P/'js/jsme-nick-nomeclature-moc2-data_56.js').read_text()
src=''.join('var '+k+'=new Function("extra",'+json.dumps(shared['PREFIX']+data+'\n'+v.read_text()+'\n'+tail)+');'
            for k,v in sources.items())
src+='const fixtures='+json.dumps(fixtures)+';'
src+='const versions={};for(const [v,fn]of '+\
     '[["before",before],["raw57",raw57],["candidate",candidate]])'+\
     '{versions[v]=fixtures.map(f=>({id:f.id,...fn(f)}))}print(JSON.stringify({versions}));'

parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['before','after'],required=True)
args=parser.parse_args()
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',capture_output=True,text=True)
assert r.returncode==0,(r.stdout[-3000:],r.stderr[-1000:])
out=json.loads(r.stdout); assertions=0
for fixture, row in zip(fixtures,out['versions']['candidate']):
    assert row['originalInputUnchanged']; assertions+=1
    if args.phase=='after':
        for dimension in ['path2','path3']:
            expected=fixture.get('expected',fixture['chain'])
            assert row[dimension]['forward']==expected,(fixture['id'],dimension,row)
            assert row[dimension]['reverse']==(fixture['chain'][::-1] if fixture.get('free') else expected),(fixture['id'],dimension,row)
            assertions+=2
        assert row['path2']==row['path3'],(fixture['id'],row); assertions+=1
        assert row['chain2']==row['chain3BeforeMatch'],(fixture['id'],row); assertions+=1
        if fixture.get('namePrefix'):
            assert row['name'].startswith(fixture['namePrefix']),row; assertions+=1
    else:
        assert row==out['versions']['before'][fixtures.index(fixture)]; assertions+=1
before=out['versions']['before']; raw=out['versions']['raw57']
assert before[0]['name'].startswith('3-χλωρο'); assertions+=1
assert raw[0]['name'].startswith('2-χλωρο'); assertions+=1
assert before[1]['path2']['reverse']==fixtures[1]['chain']; assertions+=1
assert raw[1]['path2']['reverse']==fixtures[1]['chain'][::-1]; assertions+=1
assert raw[1]['path3']['reverse']==fixtures[1]['chain']; assertions+=1
out.update({'phase':args.phase,'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'fixtures':fixtures,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources.values()},
            'summary':{'fixtures':len(fixtures),'versions':list(sources),'assertions':assertions,
                       'actualRuntime':'macOS JavaScriptCore; actual project functions; no browser/JSME',
                       'beforeName':before[0]['name'], 'candidateName':out['versions']['candidate'][0]['name'],
                       'raw57Direct3DMalonicRemainsForced':raw[1]['path3']['reverse']==fixtures[1]['chain']}})
(D/f'terminal-priority-{args.phase}-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out['summary'],ensure_ascii=False))
