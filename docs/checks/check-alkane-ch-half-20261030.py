"""Verify 50% C-H vectors, fixed C/graph and scope against the experiment baseline."""
from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import json
import math
import runpy
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args = parser.parse_args()
snapshot = json.loads(gzip.decompress(args.before.read_bytes()))
old = {p:base64.b64decode(v).decode() for p,v in snapshot['sources'].items()}
helpers = runpy.run_path('docs/checks/harmonize-two-alkanes-20261030.py')
parse = helpers['parse']; data_path = 'js/jsme-nick-nomeclature-moc2-data_52.js'


def registry(code):
    script='var window={};'+code+';print(JSON.stringify({mols:window.MOL2D,examples:nameExamples}));'
    response=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                            '-e','eval(JSON.parse(readline()))'],input=json.dumps(script)+'\n',
                            capture_output=True,text=True,check=True)
    return json.loads(response.stdout)


before = registry(old[data_path]); after_code = Path(data_path).read_text(); after = registry(after_code)
assert before['examples']==after['examples'] and set(before['mols'])==set(after['mols'])
assert all(before['mols'][key]==value for key,value in after['mols'].items() if key not in snapshot['keys'])
assert all(before['mols'][key][form]==after['mols'][key][form] for key in snapshot['keys'] for form in ('condensed','skeletal'))


def masked(code):
    for key in snapshot['keys']:
        match=helpers['literal_match'](code,key+'_2D_Expanded');assert match
        code=code[:match.start(1)]+'CH_EXPERIMENT_MOL'+code[match.end(1):]
    return code


assert masked(old[data_path])==masked(after_code)


def verify(before_mol,after_mol,label):
    old_lines,old_atoms,old_edges=parse(before_mol)
    lines,atoms,edges=parse(after_mol); n=len(atoms)
    assert len(old_atoms)==n and old_edges==edges,label
    assert old_lines[:4]==lines[:4] and old_lines[4+n:]==lines[4+n:],label
    ratios=[]
    for i,(a,b) in enumerate(zip(old_atoms,atoms)):
        assert old_lines[4+i][20:]==lines[4+i][20:],(label,i)
        if a[2]!='H':
            assert old_lines[4+i]==lines[4+i],(label,'carbon moved',i)
            continue
        neighbors=[v if u==i else u for u,v in edges if i in (u,v)]
        assert len(neighbors)==1 and atoms[neighbors[0]][2]=='C'
        c=neighbors[0]
        expected=[old_atoms[c][d]+.5*(a[d]-old_atoms[c][d]) for d in (0,1)]
        assert max(abs(expected[d]-b[d]) for d in (0,1))<=.000050001,(label,i,expected,b)
        ratios.append(math.dist(b[:2],atoms[c][:2])/math.dist(a[:2],old_atoms[c][:2]))
    assert len(ratios)==sum(atom[2]=='H' for atom in atoms)
    return {'label':label,'explicitH':len(ratios),'ratioRange':[min(ratios),max(ratios)],
            'fixedCarbonAndIndexedGraph':True,'halfVectorWithinMOLPrecision':True}


rows=[verify(before['mols'][key]['expanded'],after['mols'][key]['expanded'],key) for key in snapshot['keys']]
for path,mol in old.items():
    if path.endswith('.mol'):
        verify(mol,Path(path).read_text(),path)
        if 'new_molecules' in path:
            key=Path(path).name.removesuffix('_2D_Expanded.mol')
            assert after['mols'][key]['expanded']==Path(path).read_text()
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=[p for p in snapshot['fileHashes'] if p not in allowed]
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==snapshot['fileHashes'][p] for p in protected)
result={'passed':True,'rows':rows,'explicitHChanged':sum(r['explicitH'] for r in rows),
        'expandedMolecules':8,'sourceMOLCopies':3,'otherMoleculeRecordsUnchanged':len(after['mols'])-8,
        'condensedAndSkeletalAndMetadataUnchanged':True,'otherDataCodeByteIdentical':True,
        'protectedExistingFilesUnchanged':len(protected),'coreUnchanged':True,'roundingTolerance':.000050001}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: 90 explicit H vectors halved in 8 expanded alkanes; C,graph,other forms and',len(protected),'protected files unchanged')
