"""Before/after real naming regression for all130molecules, 3forms and 2chain modes."""
from pathlib import Path
import json,subprocess,gzip,base64,sys
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
t=ns['body'];tail=t[t.index('var MOL2D=window.MOL2D;'):t.index('return {name:currentMolName')]
ret='return {name:currentMolName,common:currentMolCommonName,series:fGetMoleculeClassification().seriesKey,parts:nameComponentsList,chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)};'
old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/acid-layout-before-source-20261028.json.gz').read_bytes())).items()}
files=['js/jsme-nick-nomeclature-moc2-data_52.js','js/mulermoc-nom-core-52.js','js/mulermoc-nom-molview-52.js'];prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
before=prefix+'\n'.join(old.get(p,Path(p).read_text())for p in files)+tail+ret
after=prefix+'\n'.join(Path(p).read_text()for p in files)+tail+ret
sdfs={p.stem[:-3]:p.read_text()for p in Path('mols/nomeclature-moc2').glob('*_3D.sdf')}
extract='var window={};'+old[files[0]]+';return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));'
js='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(before)+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(after)+');var inv=(new Function('+json.dumps(extract)+'))(),sdfs='+json.dumps(sdfs)+',n=0;for(var pair of inv)for(var chain of ["algorithmic","data"]){var args=[pair[0],pair[1],chain,sdfs[pair[0]],null],a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify({args:args.slice(0,3),before:a,after:b}));n++;}'
frame=';return fGetUniform2DLibraryFrame();';bframe=prefix+'\n'.join(old.get(p,Path(p).read_text())for p in files)+frame;aframe=prefix+'\n'.join(Path(p).read_text()for p in files)+frame
js+='var bf=(new Function('+json.dumps(bframe)+'))(),af=(new Function('+json.dumps(aframe)+'))();if(JSON.stringify(bf)!==JSON.stringify(af))throw Error("Legacy frame changed");print(JSON.stringify({passed:true,molecules:new Set(inv.map(p=>p[0])).size,cases:n,legacyFrame:af}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
result=json.loads(r.stdout);assert result['molecules']==130 and result['cases']==778
if '--read-only'not in sys.argv:Path('docs/checks/acid-layout-naming-20261028.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',result)
