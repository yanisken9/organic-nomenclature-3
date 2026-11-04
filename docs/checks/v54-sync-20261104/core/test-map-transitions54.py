"""Persistent-engine 2D-mode/3D-map transitions; Python stdlib + JSC."""
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
function load(t){
 const lines=t.split(/\r?\n/),n=+lines[3].slice(0,3),nb=+lines[3].slice(3,6);
 jsmeNomeclatureApplet={totalNumberOfAtoms:()=>n,totalNumberOfBonds:()=>nb,
  getAtom:(m,i)=>({label:lines[3+i].slice(31,34).trim()}),
  getBond:(m,i)=>{const l=lines[3+n+i];return{atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}},molFile:()=>t};
 fAnalyseStructure();fDetectMolType();fGuessName();
}
const rows=[],unsupported=[];
for(const key of Object.keys(window.MOL2D))for(const cm of ['algorithmic','data']){
 const available=['condensed','skeletal','expanded'].filter(mode=>window.MOL2D[key][mode]);
 selectedMol=key;mainChainMode=cm;mainChainPool=[];mainChainPoolIdx=0;
 mainChainPool3D=[];mainChainPool3DKey=null;molAtomMap2D3D=null;molAtomMapKey=null;
 fInitNamingProps();mode2D=available[0];load(window.MOL2D[key][mode2D]);
 fParseSDF3D(sdfs[key]);fDetectMolType3D();fCalcMainChain3D();fMatchNumberedMainChain3D();
 for(const mode of available.concat(available.slice().reverse())){
  mode2D=mode;load(window.MOL2D[key][mode]);
  const translated=fTranslateChain2D3D(mainChainAtomsList),fresh=fBuildHeavyMap2D3D(false),cached=molAtomMap2D3D;
  if(!fresh){check(translated===null,'non-isomorphic input must not map:'+key+':'+mode);
   unsupported.push({key,mode,cm});continue;}
  check(cached&&translated,'exact translation:'+key+':'+mode+':'+cm);
  const B=fHeavyAdj2D3D(allAtomsTypeList3D,bondList3D);
  for(let i=0;i<allAtomsTypeList.length;i++)if(allAtomsTypeList[i]!=='H')
   check(allAtomsTypeList[i]===allAtomsTypeList3D[cached.arr[i]],'cached element:'+key+':'+mode);
  for(const[a,b,o]of bondList)if(allAtomsTypeList[a-1]!=='H'&&allAtomsTypeList[b-1]!=='H'){
   check((B.adj[cached.arr[a-1]]||[]).includes(cached.arr[b-1]),'cached edge:'+key+':'+mode);
   check(fOrderOf2D3D(B.ord,cached.arr[a-1],cached.arr[b-1])===o,'cached bond order:'+key+':'+mode);
  }
  check(fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList)===
   fNumberedChainSignature(translated,allAtomsTypeList3D,bondList3D),'translated parent chemistry:'+key+':'+mode);
  rows.push({key,mode,cm,chain2:mainChainAtomsList,chain3:translated});
 }
}
// Reuse an existing cache across a same-size 3D graph mutation. A positive
// 1-butene map must be invalidated before the 2-butene negative control.
selectedMol='same-key-mutated';jsmeNomeclatureApplet={molFile:()=>''};
allAtomsTypeList=allAtomsTypeList3D=['C','C','C','C'];
bondList=[[1,2,2],[2,3,1],[3,4,1]];bondList3D=[[1,2,2],[2,3,1],[3,4,1]];
check(fTranslateChain2D3D([1,2,3,4])!==null,'positive same-key cache');
bondList3D=[[1,2,1],[2,3,2],[3,4,1]];
check(fTranslateChain2D3D([1,2,3,4])===null,'mutated bond-order graph must invalidate cache');
print(JSON.stringify({rows,unsupported,sameSizeMutationRejected:true}));
'''


def run(output):
    files = [ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js', ROOT/'js/mulermoc-nom-core-54.js']
    sdfs = {p.stem[:-3]: p.read_text() for p in (ROOT/'mols/nomeclature-moc2').glob('*_3D.sdf')}
    prefix = 'var window={},selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet,console={log(){},warn(){},error(){}};'
    result = JSC(prefix+''.join(p.read_text()+'\n' for p in files)+';const sdfs='+json.dumps(sdfs)+';'+BODY)
    result['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result['summary'] = {'molecules': len({x['key'] for x in result['rows']}),
                         'exactPersistentTransitions': len(result['rows']),
                         'unsupportedRawLabelCases': result['unsupported'],
                         'sameSizeMutationRejected': result['sameSizeMutationRejected']}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
    assert result['summary']['molecules'] == 141


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'map-transitions54-results.json')
    run(parser.parse_args().output)
