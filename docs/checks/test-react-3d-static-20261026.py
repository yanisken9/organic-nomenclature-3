"""Read-only 3D runtime/source correspondence for the three unchanged pilot molecules.
Usage: python3 .../test-react-3d-static-20261026.py BROWSER_JSON REGRESSION_JSON
Not a general conformer-quality or IUPAC certification.
"""
import collections, hashlib, json, math, runpy, sys
from pathlib import Path
helpers=runpy.run_path(str(Path(__file__).with_name('test-react-molecules-static-20261026.py')))
parse_mol,isomorphic=helpers['parse_mol'],helpers['isomorphic']
browser=json.loads(Path(sys.argv[1]).read_text())
regression=json.loads(Path(sys.argv[2]).read_text())
assert browser['completed'] and regression['completed']
result={}
for key,formula in helpers['expected'].items():
 source=Path('mols/nomeclature-moc2')/(key+'_3D.sdf')
 raw=source.read_text(); graph=parse_mol(raw)
 assert graph['formula']==formula and graph['explicitH']==formula['H']
 for mode,mol in regression['sourceMOLs'][key].items():
  assert isomorphic(graph,parse_mol(mol)),(key,mode)
 lines=raw.splitlines(); start=next(i for i,l in enumerate(lines) if 'V2000' in l)
 n,m=graph['atoms'],graph['bonds']; atoms=lines[start+1:start+1+n]
 runtime=browser['models'][key]
 assert len(runtime['atoms'])==n and len(runtime['bonds'])==m
 valence=[0]*n
 max_delta=0
 for serial,(line,atom) in enumerate(zip(atoms,runtime['atoms']),1):
  assert atom['n']==serial and atom['s']==line[31:34].strip()
  coords=[float(line[i:i+10]) for i in (0,10,20)]
  delta=max(abs(a-atom[k]) for a,k in zip(coords,('x','y','z')))
  assert all(math.isfinite(a) for a in coords) and delta<1e-5
  max_delta=max(max_delta,delta)
 edges={}
 for line in lines[start+1+n:start+1+n+m]:
  a,b,order=int(line[:3]),int(line[3:6]),int(line[6:9])
  edges[tuple(sorted((a,b)))]=order
  valence[a-1]+=order;valence[b-1]+=order
 assert all(v=={'C':4,'H':1,'O':2}[a['s']] for v,a in zip(valence,runtime['atoms']))
 assert {tuple(sorted((b['a'],b['b']))):b['order'] for b in runtime['bonds']}==edges
 chain=runtime['chain']
 assert len(chain)==formula['C']-(2 if key=='dimethyl_2_3_butane' else 0)
 assert all(runtime['atoms'][serial-1]['s']=='C' for serial in chain)
 assert all(tuple(sorted(pair)) in edges for pair in zip(chain,chain[1:]))
 assert browser['highlights'][key]['exactLegacyParity']
 result[key]={'formula':formula,'atoms':n,'bonds':m,'explicitH':graph['explicitH'],
  'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'allThree2DHeavyGraphsMatch3D':True,'runtimeSerialElementsCoordinatesBondsMatchSource':True,
  'maxCoordinateDelta':max_delta,'mainChainSerials':chain,'valencesComplete':True}
print(json.dumps({'passed':True,'molecules':result},ensure_ascii=False,indent=2))
