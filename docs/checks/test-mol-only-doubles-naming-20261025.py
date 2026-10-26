from pathlib import Path
import json,subprocess
p=Path('docs/checks/test-alcohols-naming-20261024.py');env={};exec(p.read_text().split("js='var run")[0],env)
body=env['body'];tail=body[body.index('var MOL2D=window.MOL2D;'):body.index('if(!probe){fParseSDF3D')]+"return {name:currentMolName,parts:nameComponentsList,chain:mainChainAtomsList};"
prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
base=Path('/tmp/mol-files-only-baseline');functions=[]
for variant in ['before','after']:
 sources=[]
 for name in ['js/jsme-nick-nomeclature-moc2-data_50.js','js/mulermoc-nom-core-50.js','js/mulermoc-nom-molview-50.js']:
  path=base/name if variant=='before' and (base/name).exists() else Path(name);sources.append(path.read_text())
 functions.append(prefix+'\n'.join(sources)+tail)
js='var before=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(functions[0])+'),after=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(functions[1])+');'
data=Path('js/jsme-nick-nomeclature-moc2-data_50.js').read_text()
js+='var inventory=(new Function("var window={};"+'+json.dumps(data)+'+";return Object.keys(window.MOL2D).flatMap(k=>Object.keys(window.MOL2D[k]).filter(m=>window.MOL2D[k][m]).map(m=>[k,m]));"))();var n=0;for(var pair of inventory){for(var chain of ["algorithmic","data"]){var args=[pair[0],pair[1],chain,"",null];var a=before.apply(null,args),b=after.apply(null,args);if(JSON.stringify(a)!==JSON.stringify(b))throw Error(JSON.stringify([args,a,b]));n++;}}print(JSON.stringify({cases:n,unchangedNamesPartsChains:true}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);print(r.stdout);assert r.returncode==0,(r.stdout,r.stderr)
Path('/tmp/mol-only-names-final.json').write_text(r.stdout)
