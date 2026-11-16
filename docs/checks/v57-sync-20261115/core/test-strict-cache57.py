"""Exercise unchanged strict graph/source cache through existing public entry.

Single-heavy-atom translation intentionally primes the same whole-graph cache
used by chain translation. No new core mapping API is needed for the viewer.
"""
from pathlib import Path
import datetime, hashlib, json, subprocess
P=Path(__file__).resolve().parents[4]; D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate/js/mulermoc-nom-core-57.js')
J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
src='var window={},selectedMol="cache-fixture",mode2D="condensed",mainChainMode="algorithmic",jsmeNomeclatureApplet,console={log(){},warn(){},error(){}};\n'+C.read_text()+r'''
let checks=0;function check(v,m){checks++;if(!v)throw Error(m)}
allAtomsTypeList=['C','C','C','C'];allAtomsTypeList3D=allAtomsTypeList.slice();
bondList=[[1,2,2],[2,3,1],[3,4,1]];bondList3D=bondList.map(b=>b.slice());
const atoms=allAtomsTypeList.map((el,i)=>({el,x:i,y:0}));
let source2=fWriteMolV2000([],atoms,bondList),source3=source2;
jsmeNomeclatureApplet={molFile:()=>source2};fParseSDF3D(source3);
check(JSON.stringify(fTranslateChain2D3D([1]))==='[1]','single valid heavy atom primes full strict map');
const initial=molAtomMap2D3D,key0=molAtomMapKey;
check(initial&&initial.arr.filter(x=>x!=null).length===4,'primed map covers all heavy atoms');
check(fTranslateChain2D3D([1,2,3,4]).length===4,'full chain uses primed cache');
check(molAtomMap2D3D===initial&&molAtomMapKey===key0,'identical inputs reuse same map');
source2+='\n> <fixture>\nsource2-changed\n';
check(fTranslateChain2D3D([1])!==null,'source2 metadata remains mappable');
check(molAtomMapKey!==key0&&molAtomMap2D3D!==initial,'source2 change rebuilds same-size map');
const source2Cache=molAtomMap2D3D,key2=molAtomMapKey;
source3+='\n> <fixture>\nsource3-changed\n';fParseSDF3D(source3);
check(fTranslateChain2D3D([1])!==null,'source3 metadata remains mappable');
check(molAtomMapKey!==key2&&molAtomMap2D3D!==source2Cache,'source3 change rebuilds same-size map');
const source3Cache=molAtomMap2D3D;
bondList3D=[[1,2,1],[2,3,2],[3,4,1]];
check(fBuildHeavyMap2D3D(false)===null,'bond-order mismatch has no exact isomorphism');
check(fBuildHeavyMap2D3D(true)!==null,'negative control admits order-ignorant isomorphism');
check(fTranslateChain2D3D([1])===null,'primer never falls back to relaxed map');
check(molAtomMap2D3D===null,'invalidated graph cannot expose previous cached map');
bondList3D=bondList.map(b=>b.slice());
check(fTranslateChain2D3D([1])!==null,'restore valid graph after mismatch');
check(molAtomMap2D3D!==source3Cache,'restored graph rebuilt map');
check(fTranslateChain2D3D([99])===null,'invalid heavy atom rejected');
check(fTranslateChain2D3D([])===null,'empty primer rejected');
print(JSON.stringify({checks,singleHeavyPrimer:true,source2MutationRebuilt:true,
 source3MutationRebuilt:true,bondOrderMismatchRejected:true,restoredAfterMismatch:true}));
'''
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',capture_output=True,text=True)
assert r.returncode==0,(r.stdout[-3000:],r.stderr[-1000:])
out=json.loads(r.stdout);out['coreSHA256']=hashlib.sha256(C.read_bytes()).hexdigest()
out['timestampUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
out['actualRuntime']='macOS JavaScriptCore; actual core functions; no browser/JSME'
(D/'strict-cache-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
