"""Generate six approved preview candidates; never writes application sources."""
from pathlib import Path
import gzip,json,math,runpy
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
helpers=runpy.run_path(str(ROOT/'docs/checks/enyne-uniform-20261031/transform.py'))
parse=helpers['parse'];literal=helpers['literal']
KEYS=['ethyl_2_methyl_3_pentanal','ethyl_4_isopropyl_3_methyl_2_hexanal',
      'ethyl_4_penten_4_yn_2_al','isopropyl_2_buten_2_dial',
      'trimethyl_3_4_4_pentanone_2','diethyl_4_5_dimethyl_2_6_heptanone_3']
# Parent/first/terminal carbon IDs from the six reviewed molecular graphs.
# Only ethyl continuations turn; isopropyl arms remain distinct left/right.
VERTICAL_ETHYLS={KEYS[0]:[(2,6,7)],KEYS[1]:[(4,11,12)],
                 KEYS[2]:[(4,6,7)],KEYS[5]:[(4,9,10),(5,11,12)]}
def vertical_ethyls(xy,atoms,near,key):
    changes=[]
    for parent,first,last in VERTICAL_ETHYLS.get(key,[]):
        parent,first,last=parent-1,first-1,last-1
        assert atoms[parent][2]==atoms[first][2]==atoms[last][2]=='C'
        assert sum(atoms[n][2]=='H'for n,o in near[first])==2
        assert sum(atoms[n][2]=='H'for n,o in near[last])==3
        assert len(near[first])==len(near[last])==4
        p,f,t=xy[parent],xy[first],xy[last]
        stem=math.dist(p,f);length=math.dist(f,t)
        u=((t[0]-f[0])/length,(t[1]-f[1])/length)
        v=((f[0]-p[0])/stem,(f[1]-p[1])/stem)
        assert abs(v[0])<1e-9 and abs(u[1])<1e-9
        cosine=u[0]*v[0]+u[1]*v[1];sine=u[0]*v[1]-u[1]*v[0]
        # Rotate terminal CH3 rigidly about CH2: no reflection or length change.
        for i in [last]+[n for n,o in near[last]if atoms[n][2]=='H']:
            dx,dy=xy[i][0]-f[0],xy[i][1]-f[1]
            xy[i]=(f[0]+cosine*dx-sine*dy,f[1]+sine*dx+cosine*dy)
        # The CH2 hydrogen in the newly occupied direction takes the vacated slot.
        moved=[]
        for i,o in near[first]:
            if atoms[i][2]!='H':continue
            dx,dy=xy[i][0]-f[0],xy[i][1]-f[1];r=math.hypot(dx,dy)
            if (dx*v[0]+dy*v[1])/r>1-1e-9:
                xy[i]=(f[0]+u[0]*r,f[1]+u[1]*r);moved.append(i+1)
        assert len(moved)==1
        changes.append({'parent':parent+1,'first':first+1,'terminal':last+1,
                        'CH2HydrogenReoriented':moved[0],
                        'terminalRotationDegrees':round(math.degrees(math.atan2(sine,cosine))),
                        'heavyLength':round(length,4)})
    return changes
def requested_spacing(xy,atoms,near,key,stems):
    """Apply the approved 1 November experiment after vertical ethyl development."""
    changes=[]
    if key==KEYS[4]:return changes
    for edge in stems:
        a,b=[i-1 for i in edge['atoms']];old=math.dist(xy[a],xy[b])
        target=.588 if key!=KEYS[5]else round(.9282*.4,4)
        dx=(xy[b][0]-xy[a][0])*(target/old-1)
        dy=(xy[b][1]-xy[a][1])*(target/old-1)
        seen={a};pending=[b]
        while pending:
            i=pending.pop()
            if i in seen:continue
            seen.add(i);xy[i]=(xy[i][0]+dx,xy[i][1]+dy)
            pending.extend(n for n,o in near[i])
        edge['previousPreview']=edge['proposed'];edge['proposed']=target
    if key==KEYS[1]:
        # A narrow outward V separates both methyl groups from the parent H.
        # Explicit terminal H use the approved outward/up/down free directions.
        c=7;x,y=xy[c]
        for terminal,side in [(8,1),(9,-1)]:
            assert {n for n,o in near[terminal]if atoms[n][2]!='H'}=={c}
            xy[terminal]=(x+side*.6188/2,y+.6188*math.sqrt(3)/2)
            hs=[n for n,o in near[terminal]if atoms[n][2]=='H'];assert len(hs)==3
            for i,(dx,dy)in zip(hs,[(side*.3094,0),(0,.3094),(0,-.3094)]):
                xy[i]=(xy[terminal][0]+dx,xy[terminal][1]+dy)
        changes.append({'kind':'isopropylOutwardV','center':8,'terminalCarbons':[9,10],
                        'angleAboveHorizontalDegrees':60,'terminalH':'outward/up/down'})
    elif key==KEYS[3]:
        # Actual screen-left aldehyde is C4; the next parent carbon is C3.
        xy[11]=(xy[3][0]-.3094,xy[3][1])
        xy[10]=(xy[2][0],xy[2][1]+.3094)
        # Turn the left methyl (C7) down about C5; its three H move rigidly.
        c,last=4,6;x,y=xy[c]
        for i in [last]+[n for n,o in near[last]if atoms[n][2]=='H']:
            dx,dy=xy[i][0]-x,xy[i][1]-y
            xy[i]=(x-dy,y+dx)
        xy[12]=(x-.3094,y)
        changes.extend([{'kind':'screenLeftHydrogen','carbon':4,'hydrogen':12,'direction':'left'},
                        {'kind':'secondScreenLeftHydrogen','carbon':3,'hydrogen':11,'direction':'up'},
                        {'kind':'isopropylOneVerticalArm','center':5,'terminal':7,
                         'direction':'down','centralHydrogen':13,'centralHDirection':'left'}])
    return changes
def proposal(mol,key):
    lines,atoms,bonds=parse(mol);near=[[]for _ in atoms];heavy=[i for i,a in enumerate(atoms)if a[2]!='H']
    assert len(bonds)==len(atoms)-1
    for a,b,o in bonds:near[a].append((b,o));near[b].append((a,o))
    root=heavy[0];xy={root:(atoms[root][0]*.6188/1.17,atoms[root][1]*.6188/1.17)};pending=[root];stems=[]
    def add(a,b,length):
        dx,dy=atoms[b][0]-atoms[a][0],atoms[b][1]-atoms[a][1];r=math.hypot(dx,dy);assert r>0
        xy[b]=(xy[a][0]+dx/r*length,xy[a][1]+dy/r*length)
    while pending:
        a=pending.pop()
        for b,o in near[a]:
            if atoms[b][2]=='H'or b in xy:continue
            old_length=math.dist(atoms[a][:2],atoms[b][:2]);units=old_length/1.17;target=.6188
            if key==KEYS[4]:
                if set([a+1,b+1])=={4,8}:target=.98
            elif key==KEYS[5]:
                if units>1.5:target=.6188*(units+1)/2
            elif units>1.5:target=.98
            if target!=.6188:stems.append({'atoms':[a+1,b+1],'original':old_length,'proposed':round(target,4)})
            add(a,b,target);pending.append(b)
    assert all(i in xy for i in heavy)
    for i,a in enumerate(atoms):
        if a[2]=='H':assert len(near[i])==1;add(near[i][0][0],i,.3094)
    assert len(xy)==len(atoms)
    turns=vertical_ethyls(xy,atoms,near,key)
    layout=requested_spacing(xy,atoms,near,key,stems)
    points={i:tuple(round(v,4)for v in p)for i,p in xy.items()};assert len(set(points.values()))==len(atoms)
    for i in range(len(atoms)):
        x,y=points[i];lines[4+i]='%10.4f%10.4f'%(x or 0.,y or 0.)+lines[4+i][20:]
    return ''.join(lines),stems,turns,layout
if __name__=='__main__':
    data=(ROOT/'js/jsme-nick-nomeclature-moc2-data_52.js').read_text();rows=[];originals={}
    for key in KEYS:
        mol=literal(data,key)[1];new,stems,turns,layout=proposal(mol,key)
        (HERE/(key+'-before.mol')).write_text(mol);(HERE/(key+'-proposed.mol')).write_text(new)
        originals[key]=mol;rows.append({'key':key,'stems':stems,'verticalEthylTurns':turns,
                                      'layoutAdjustments':layout})
    (HERE/'originals.json.gz').write_bytes(gzip.compress(json.dumps(originals).encode(),mtime=0))
    code=(ROOT/'js/mulermoc-nom-molview-52.js').read_text();start=code.index('function fPrepareFixedCCAlkanePrototype()');end=code.index('function fGetUniform2DLibraryFrame()',start)
    original=code[start:end].strip();assert original.count('const etherScale = [')==1
    preview=original.replace('const etherScale = [','const etherScale = ['+','.join(json.dumps(k)for k in KEYS)+',',1)
    (HERE/'original-calibration.js').write_text(original+'\n');(HERE/'preview-calibration.js').write_text(preview+'\n')
    (HERE/'geometry.json').write_text(json.dumps({'previewOnly':True,'normalHeavy':.6188,'CH':.3094,'molecules':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'previewMolecules':len(rows),'mainSourcesWritten':False}))
