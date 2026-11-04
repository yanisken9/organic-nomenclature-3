"""Chemical-property regression checks for the bounded Main54 MOL tools.

Run from the repository root; writes only --output. Uses Python stdlib/JSC.
"""
from pathlib import Path
import argparse
import hashlib
import json
import runpy

HERE = Path(__file__).resolve().parent
SHARED = runpy.run_path(str(HERE/'test-core54.py'))
ROOT, JSC = SHARED['ROOT'], SHARED['jsc']

BODY = r'''
function check(v,label){if(!v)throw Error(label)}
function profile(m){return {
 atoms:m.atoms.map(a=>[a.el,a.charge,a.isotope,a.massDifference,a.radical,a.parity,a.hydrogenCount,a.valence,a.z]),
 bonds:m.bonds.map(b=>[b[0],b[1],b[2],(b.tail||'').trim()])};}
function formula(m){
 const counts={},valences={C:4,N:3,O:2,F:1,Cl:1,Br:1,I:1};
 m.atoms.forEach((a,i)=>{
  const el=a.el==='[H]'?'H':a.el;counts[el]=(counts[el]||0)+1;
  if(el==='H')return;
  let v=valences[el];
  if(a.charge){const cv={C:{'-1':3,1:3},N:{'-1':2,1:4},O:{'-1':1,1:3},
   F:{'-1':0},Cl:{'-1':0},Br:{'-1':0},I:{'-1':0}};v=cv[el]&&cv[el][a.charge];}
  if(v==null)return;
  const used=m.bonds.filter(b=>b[0]===i+1||b[1]===i+1).reduce((n,b)=>n+b[2],0);
  counts.H=(counts.H||0)+Math.max(0,v-used);
 });
 return Object.keys(counts).sort().filter(k=>counts[k]).map(k=>k+(counts[k]===1?'':counts[k])).join('');
}
function charge(m){return m.atoms.reduce((sum,a)=>sum+a.charge,0)}
function groupProfile(m){
 const groups={};
 for(const line of m.properties){const f=line.trim().split(/\s+/);if(f[1]==='SAL'){
  const ids=f.slice(4).map(Number);check(ids.length===Number(f[3]),'Sgroup atom count');
  check(ids.every(i=>i>0&&i<=m.atoms.length),'Sgroup atom range');
  groups[f[2]]=(groups[f[2]]||[]).concat(ids);
 }}
 for(const line of m.properties){const f=line.trim().split(/\s+/);if(f[1]==='SBL'){
  for(const i of f.slice(4).map(Number)){
   check(i>0&&i<=m.bonds.length,'Sgroup bond range');const b=m.bonds[i-1];
   check(groups[f[2]].includes(b[0])!==groups[f[2]].includes(b[1]),'Sgroup crossing bond');
  }
 }}
 return {groups:Object.fromEntries(Object.entries(groups).map(([g,ids])=>[g,ids.map(i=>m.atoms[i-1])
   .filter(a=>a.el!=='H').map(a=>[a.el,a.charge,a.isotope,a.massDifference]).sort()])),
  labels:m.properties.filter(l=>l.startsWith('M  SMT'))};
}
function chainFor(key,mode,text){
 selectedMol=key;mode2D=mode;mainChainMode='algorithmic';
 const m=fParseMolV2000(text);
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>m.atoms.length,totalNumberOfBonds:()=>m.bonds.length,
  getAtom:(model,i)=>({label:m.atoms[i-1].el}),
  getBond:(model,i)=>({atoms:m.bonds[i-1].slice(0,2),order:m.bonds[i-1][2]}),molFile:()=>text};
 fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();return mainChainAtomsList;
}
function stripProfile(m){
 const ids={};let n=0;
 const atoms=m.atoms.filter((a,i)=>{if(a.el!=='H'){ids[i+1]=++n;return true}return false});
 return {atoms:atoms.map(a=>[a.el,a.charge,a.isotope,a.massDifference,a.radical]),
  bonds:m.bonds.filter(b=>ids[b[0]]&&ids[b[1]]).map(b=>[ids[b[0]],ids[b[1]],b[2]])};
}
function variants(text,chain){return {
 strip:fStripHydrogensMol(text),linear:fLinearizeMol(text,chain),
 zigzag:fZigzagMol(text,chain),expanded:fGenExpandedMol(text)};}
const roundtrips=[],generators=[],skips=[];
for(const [key,modes] of Object.entries(window.MOL2D))for(const [mode,text] of Object.entries(modes)){
 if(!text)continue;
 const m=fParseMolV2000(text);check(m,'parse:'+key+':'+mode);
 const written=fWriteMolV2000(m.head,m.atoms,m.bonds,m),back=fParseMolV2000(written);
 check(back,'roundtrip parse:'+key+':'+mode);
 check(JSON.stringify(profile(m))===JSON.stringify(profile(back)),'roundtrip metadata:'+key+':'+mode);
 check(formula(m)===formula(back)&&charge(m)===charge(back),'roundtrip formula/charge:'+key);
 roundtrips.push({key,mode,formula:formula(m),charge:charge(m),propertyRecords:m.properties.length});
 const chain=chainFor(key,mode,text);
 const output=variants(text,chain);
 if(!fMolCanTransform2D(m,true)){
  check(Object.values(output).every(v=>v===null),'unsupported generator rejection:'+key+':'+mode);
  skips.push({key,mode,reason:'unsupported literal element/query label'});continue;
 }
 for(const [kind,value] of Object.entries(output)){
  check(value,'generator:'+key+':'+mode+':'+kind);
  const generated=fParseMolV2000(value);
  check(JSON.stringify(stripProfile(m))===JSON.stringify(stripProfile(generated)),'generator heavy metadata:'+key+':'+mode+':'+kind);
  check(formula(m)===formula(generated)&&charge(m)===charge(generated),'generator formula/charge:'+key+':'+mode+':'+kind);
  check(JSON.stringify(groupProfile(m))===JSON.stringify(groupProfile(generated)),'generator Sgroups:'+key+':'+mode+':'+kind);
  generators.push({key,mode,kind,formula:formula(generated),charge:charge(generated)});
 }
}
function source(atoms,bonds,properties){
 atoms=atoms.map((a,i)=>Object.assign({x:i*1.17,y:0,el:'C'},a));
 const text=fWriteMolV2000([],atoms,bonds);
 return properties?text.replace('M  END',properties.join('\n')+'\nM  END'):text;
}
const fixtures=[];
function fixture(label,text,chain,expect){
 const result=variants(text,chain),parsed=fParseMolV2000(text);
 for(const [kind,value]of Object.entries(result)){
  const expected=expect[kind];check((value!==null)===expected,'fixture support:'+label+':'+kind);
  if(value){
   const m=fParseMolV2000(value);check(m,'fixture parse:'+label+':'+kind);
   check(formula(parsed)===formula(m)&&charge(parsed)===charge(m),'fixture formula:'+label+':'+kind);
   const tags=x=>x.atoms.filter(a=>a.charge||a.isotope||a.massDifference||a.radical)
    .map(a=>[a.el,a.charge,a.isotope,a.massDifference,a.radical]).sort();
   check(JSON.stringify(tags(parsed))===JSON.stringify(tags(m)),'fixture isotope/charge:'+label+':'+kind);
  }
 }
 fixtures.push({label,support:Object.fromEntries(Object.entries(result).map(([k,v])=>[k,v!==null]))});
 return result;
}
const all={strip:true,linear:true,zigzag:true,expanded:true},none={strip:false,linear:false,zigzag:false,expanded:false};
fixture('ammonium',source([{el:'N',charge:1}],[]),[1],all);
fixture('methoxide',source([{el:'C'},{el:'O',charge:-1}],[[1,2,1]]),[1],all);
fixture('13C methane',source([{el:'C',isotope:13}],[]),[1],all);
fixture('carbon mass difference',source([{el:'C',tail:' 1  0  0  0  0  0  0  0  0  0  0  0'}],[]),[1],all);
fixture('isotopic explicit H',source([{el:'C'},{el:'H',isotope:2}],[[1,2,1]]),[1],{...none,expanded:true});
fixture('mass-difference explicit H',source([{el:'C'},{el:'H',tail:' 1  0  0  0  0  0  0  0  0  0  0  0'}],[[1,2,1]]),[1],{...none,expanded:true});
fixture('atom parity',source([{el:'C',tail:' 0  0  1  0  0  0  0  0  0  0  0  0'}],[]),[1],none);
const wedge=[1,2,1];wedge.tail='  1  0  0';
fixture('bond wedge',source([{el:'C'},{el:'F'}],[wedge]),[1],none);
fixture('radical',source([{el:'C',radical:2}],[]),[1],none);
fixture('aromatic/query bond',source([{el:'C'},{el:'C'}],[[1,2,4]]),[1,2],none);
fixture('unknown property',source([{el:'C'}],[],['M  FOO  1   1   1']),[1],none);
fixture('polymer Sgroup',source([{el:'C'}],[],['M  STY  1   1 SRU','M  SAL   1  1   1']),[1],none);
const nitro=[];
for(const [key,h]of [['nitroethane',5],['nitropropane_2',7]])for(const mode of ['condensed','expanded','skeletal']){
 const text=window.MOL2D[key][mode],m=fParseMolV2000(text);
 const chain=nameExamples[key]['mainChain'+{condensed:'_Condensed',expanded:'_Expanded',skeletal:'_Skeletal'}[mode]];
 const out=variants(text,chain),derived=[out.expanded,
  fGenExpandedMol(out.strip),fGenExpandedMol(out.linear),fGenExpandedMol(out.zigzag)];
 for(const value of derived){const x=fParseMolV2000(value);
  check(x.atoms.filter(a=>a.el==='H').length===h,'nitro H count:'+key+':'+mode);
  check(x.atoms.filter(a=>a.charge===1&&a.el==='N').length===1&&
   x.atoms.filter(a=>a.charge===-1&&a.el==='O').length===1,'nitro charges:'+key+':'+mode);
  check(!x.bonds.some(([a,b])=>(x.atoms[a-1].el==='H'&&x.atoms[b-1].el==='O')||
   (x.atoms[b-1].el==='H'&&x.atoms[a-1].el==='O')),'nitro no hydroxyl:'+key);
 }
 nitro.push({key,mode,derived:derived.length,hydrogens:h});
}
// Atom and bond indices are permuted with explicit H interleaved. This forces
// CHG/ISO/SAL/SBL/SBV to follow retained graph identities rather than positions.
const original=fParseMolV2000(window.MOL2D.nitroethane.expanded),n=original.atoms.length;
const order=Array.from({length:n},(_,i)=>i).sort((a,b)=>a%2-b%2||b-a),map={};
order.forEach((old,i)=>map[old+1]=i+1);
const atoms=order.map(i=>fCopyMolAtom2D(original.atoms[i]));
const bonds=original.bonds.slice().reverse().map(b=>fCopyMolBond2D(b,map[b[0]],map[b[1]]));
const permuted=fWriteMolV2000(original.head,atoms,bonds,original);
fixture('permuted explicit-H nitro',permuted,[map[1],map[2]],all);
const reindexed=fParseMolV2000(fStripHydrogensMol(permuted));
check(reindexed.atoms.filter(a=>a.charge).length===2,'reindexed nitro charge count');
check(reindexed.atoms.some(a=>a.el==='N'&&a.charge===1)&&reindexed.atoms.some(a=>a.el==='O'&&a.charge===-1),'reindexed charge identities');
check(JSON.stringify(groupProfile(original))===JSON.stringify(groupProfile(reindexed)),'permuted Sgroup identities');
// Correct exact-map rejection when double-bond position changes.
selectedMol='negative-butene';allAtomsTypeList=allAtomsTypeList3D=['C','C','C','C'];
bondList=[[1,2,2],[2,3,1],[3,4,1]];bondList3D=[[1,2,1],[2,3,2],[3,4,1]];
check(fBuildHeavyMap2D3D(false)===null&&fTranslateChain2D3D([1,2,3,4])===null,'1/2-butene must not map');
print(JSON.stringify({roundtrips,generators,skips,fixtures,nitro,negativeButeneMap:true}));
'''


def run(output):
    files = [ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js', ROOT/'js/mulermoc-nom-core-54.js']
    result = JSC('var window={},selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet,console={log(){},warn(){},error(){}};'+''.join(p.read_text()+'\n' for p in files)+BODY)
    result['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result['summary'] = {'molecules': len({x['key'] for x in result['roundtrips']}),
                         'roundtripCases': len(result['roundtrips']),
                         'generatorGraphFormulaChargeCases': len(result['generators']),
                         'unsupportedSources': result['skips'], 'deliberateFixtures': len(result['fixtures']),
                         'namedNitroCases': sum(x['derived'] for x in result['nitro']),
                         'negativeButeneMap': result['negativeButeneMap']}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'mol-properties54-results.json')
    run(parser.parse_args().output)
