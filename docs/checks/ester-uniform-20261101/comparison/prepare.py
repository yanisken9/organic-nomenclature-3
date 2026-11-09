"""Prepare isolated ester MOL proposals; never write application sources."""
from pathlib import Path
import gzip,json,math,runpy
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
helpers=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
parse=helpers['parse'];literal=helpers['literal']
KEYS=['methyl_methanoate','isopropyl_ethanoate']
CAPTURE_KEYS=KEYS+['tert_butyl_methanoate','isopropyl_2_3_dimethylbutanoate']
def proposal(mol,key):
    lines,atoms,bonds=parse(mol);near=[[]for _ in atoms]
    assert len(bonds)==len(atoms)-1
    for a,b,o in bonds:near[a].append(b);near[b].append(a)
    xy={0:(0.,0.)};pending=[0]
    while pending:
        a=pending.pop()
        for b in near[a]:
            if b in xy:continue
            dx,dy=atoms[b][0]-atoms[a][0],atoms[b][1]-atoms[a][1]
            assert math.hypot(dx,dy)>0
            if key in KEYS:
                # Explicit approved reconstruction of the two slightly slanted
                # Expanded originals only. The shared strict guard is untouched.
                assert math.degrees(math.atan2(min(abs(dx),abs(dy)),max(abs(dx),abs(dy))))<1.4
            else:assert min(abs(dx),abs(dy))<.00001
            ux,uy=((1 if dx>0 else -1),0)if abs(dx)>abs(dy)else(0,(1 if dy>0 else -1))
            length=.3094 if 'H'in[atoms[a][2],atoms[b][2]]else .6188
            xy[b]=(xy[a][0]+ux*length,xy[a][1]+uy*length);pending.append(b)
    assert len(xy)==len(atoms)
    xy={i:tuple(round(v,4)for v in p)for i,p in xy.items()}
    assert len(set(xy.values()))==len(atoms)
    for i in range(len(atoms)):
        x,y=xy[i];lines[4+i]='%10.4f%10.4f'%(x or 0.,y or 0.)+lines[4+i][20:]
    return ''.join(lines)
def calibration(code):
    a=code.index('function fPrepareFixedCCAlkanePrototype()');b=code.index('function fGetUniform2DLibraryFrame()',a)
    original=code[a:b].strip()
    # Reuse the existing C-O/native-anchor/font mechanism, transiently in the
    # disposable browser context. No production eligibility change here.
    preview=original.replace('const etherScale = [','const etherScale = ['+','.join(json.dumps(k)for k in CAPTURE_KEYS)+',',1)
    assert preview!=original
    return original+'\n',preview+'\n'
if __name__=='__main__':
    code=(ROOT/helpers['DATA']).read_text();source={k:literal(code,k)[1]for k in CAPTURE_KEYS}
    frozen=HERE/'originals.json.gz'
    if frozen.exists():assert json.load(gzip.open(frozen,'rt'))==source
    else:frozen.write_bytes(gzip.compress(json.dumps(source).encode(),mtime=0))
    rows=[]
    for key,mol in source.items():
        (HERE/(key+'-before.mol')).write_text(mol)
        (HERE/(key+'-proposed.mol')).write_text(proposal(mol,key))
        if key in KEYS:rows.append({'key':key,'stems':[],'verticalEthylTurns':[],'layoutAdjustments':[]})
    original,preview=calibration((ROOT/'js/mulermoc-nom-molview-52.js').read_text())
    (HERE/'original-calibration.js').write_text(original);(HERE/'preview-calibration.js').write_text(preview)
    (HERE/'geometry.json').write_text(json.dumps({'previewOnly':True,'normalHeavy':.6188,'CH':.3094,'molecules':rows,'calibrationCheckKeys':CAPTURE_KEYS[2:]},indent=2)+'\n')
    print('Prepared2 comparison pairs and2 calibration controls; Main unchanged.')
