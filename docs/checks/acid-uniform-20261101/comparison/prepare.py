"""Isolated acid preview, rebuilt from frozen original expanded MOLs only.

Writes this comparison directory, never application data or source MOLs.
All distances are schematic drawing units, not physical bond lengths.
"""
from pathlib import Path
import gzip,json,math,runpy
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
helpers=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
parse=helpers['parse'];literal=helpers['literal']
KEYS=['ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid',
      'ethyl_3_isopropyl_2_dimethyl_4_5_hexadien_2_4_dioic_acid']
CAPTURE_KEYS=KEYS+['methanoicacid','hydroxypropanoic_acid_2',
                   'aminobutanoic_acid_3','dihydroxybutanedioic_acid_2_3']
def proposal(mol,key):
    lines,atoms,bonds=parse(mol);near=[[]for _ in atoms]
    assert len(bonds)==len(atoms)-1
    for a,b,o in bonds:near[a].append((b,o));near[b].append((a,o))
    xy={0:(0.,0.)};pending=[0]
    while pending:
        a=pending.pop()
        for b,o in near[a]:
            if b in xy:continue
            dx,dy=atoms[b][0]-atoms[a][0],atoms[b][1]-atoms[a][1]
            r=math.hypot(dx,dy);assert r>0 and min(abs(dx),abs(dy))<r*.001
            length=.3094 if 'H'in[atoms[a][2],atoms[b][2]]else .6188
            xy[b]=(xy[a][0]+dx/r*length,xy[a][1]+dy/r*length);pending.append(b)
    assert len(xy)==len(atoms)
    layout=[]
    if key in KEYS:
        def rotate_terminal(center,terminal):
            center-=1;terminal-=1;x,y=xy[center]
            assert atoms[terminal][2]=='C'
            hydrogens=[n for n,o in near[terminal]if atoms[n][2]=='H']
            assert len(hydrogens)==3
            for i in [terminal]+hydrogens:
                dx,dy=xy[i][0]-x,xy[i][1]-y;xy[i]=(x-dy,y+dx)
        # Proper rotations, not reflections: isopropyl left arm becomes down;
        # ethyl right continuation becomes up. H occupy the vacated slots.
        rotate_terminal(7,9);rotate_terminal(10,11)
        central_h=23 if key==KEYS[0]else 18
        ethyl_h=30 if key==KEYS[0]else 25
        xy[central_h-1]=(xy[6][0]-.3094,xy[6][1])
        xy[ethyl_h-1]=(xy[9][0]+.3094,xy[9][1])
        layout=[{'kind':'isopropyl','center':7,'horizontalTerminal':8,
                 'horizontalDirection':'right','verticalTerminal':9,
                 'verticalDirection':'down','centralHydrogen':central_h,'HDirection':'left'},
                {'kind':'ethyl','center':10,'terminal':11,'direction':'up',
                 'hydrogenMovedRight':ethyl_h}]
    xy={i:tuple(round(v,4)for v in point)for i,point in xy.items()}
    assert len(set(xy.values()))==len(atoms),'Coincident atoms'
    assert all(xy[a][0]==xy[b][0]or xy[a][1]==xy[b][1]for a,b,o in bonds)
    for i in range(len(atoms)):
        x,y=xy[i];lines[4+i]='%10.4f%10.4f'%(x or 0.,y or 0.)+lines[4+i][20:]
    return ''.join(lines),layout
def calibration(code):
    start=code.index('function fPrepareFixedCCAlkanePrototype()')
    end=code.index('function fGetUniform2DLibraryFrame()',start)
    original=code[start:end].strip()
    preview=original.replace('const etherScale = [','const etherScale = ['+
                             ','.join(json.dumps(k)for k in CAPTURE_KEYS)+',',1)
    guard='if (!label || label.node.textContent.trim() !== allAtomsTypeList[atom]) return;'
    assert preview.count(guard)==1
    preview=preview.replace(guard,'''const symbol=allAtomsTypeList[atom];
    const raw=label?.node.textContent.replace(/\\s+/g, "");
    if (!label || !(raw===symbol || (symbol==="O" && ["OH","HO"].includes(raw)) ||
                   (symbol==="N" && raw==="NH2"))) return;''')
    old='changes.push([label, {x: anchor.x - cx, y: anchor.y + cy,'
    assert old in preview
    preview=preview.replace(old,'''const prefix=raw==="HO" ? context.measureText("H").width : 0;
    // Preserve compound labels/implicit H; defer every mutation until validated.
    const offsets=[];
    for (const tspan of label.node.querySelectorAll("tspan[dy]")) {
      const dy=tspan.getAttribute("dy");
      if (/^-?\\d+(?:\\.\\d+)?$/.test(dy))
        offsets.push([tspan,String(Number(dy)*font/originalFont)]);
    }
    changes.push([label, {x: anchor.x - cx - prefix, y: anchor.y + cy,''')
    assert preview.count('}, anchor]);')==1
    preview=preview.replace('}, anchor]);','}, anchor, offsets]);')
    preview=preview.replace('changes.forEach(([label, attributes, anchor]) => {',
                            'changes.forEach(([label, attributes, anchor, offsets]) => {')
    preview=preview.replace('label.attr(attributes);',
                            'label.attr(attributes);\n    offsets.forEach(([node,dy])=>node.setAttribute("dy",dy));')
    return original+'\n',preview+'\n'
if __name__=='__main__':
    code=(ROOT/helpers['DATA']).read_text()
    source={key:literal(code,key)[1]for key in CAPTURE_KEYS}
    frozen=HERE/'originals.json.gz'
    if frozen.exists():assert json.load(gzip.open(frozen,'rt'))==source,'Original baseline changed'
    else:frozen.write_bytes(gzip.compress(json.dumps(source).encode(),mtime=0))
    rows=[]
    for key,mol in source.items():
        proposed,layout=proposal(mol,key)
        (HERE/(key+'-before.mol')).write_text(mol)
        (HERE/(key+'-proposed.mol')).write_text(proposed)
        if key in KEYS:
            _,atoms,_=parse(mol)
            stems=[{'atoms':[a,b],'original':round(math.dist(atoms[a-1][:2],atoms[b-1][:2]),4),
                    'proposed':.6188}for a,b in [(2,7),(3,10),(4,12),(5,13)]]
            rows.append({'key':key,'stems':stems, 'verticalEthylTurns':[],
                         'layoutAdjustments':layout})
    original,preview=calibration((ROOT/'js/mulermoc-nom-molview-52.js').read_text())
    (HERE/'original-calibration.js').write_text(original)
    (HERE/'preview-calibration.js').write_text(preview)
    (HERE/'geometry.json').write_text(json.dumps({'previewOnly':True,'normalHeavy':.6188,
            'CHAndOH':.3094,'molecules':rows,'calibrationCheckKeys':CAPTURE_KEYS[2:]},indent=2)+'\n')
    print(json.dumps({'previewMolecules':len(rows),'additionalCalibrationMolecules':4,'MainWritten':False}))
