"""Reject bond interruptions by non-endpoint atom backplates in native captures."""
from pathlib import Path
import gzip,json,math,sys,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;NS='{http://www.w3.org/2000/svg}'
def audit(row):
    root=E.fromstring(row['rawSVG']);lines=[];rects=[];transforms=set()
    def visit(node,chain):
        chain=chain+((node.get('transform'),)if node.get('transform')else())
        if node.tag==NS+'line':lines.append(node);transforms.add(chain)
        elif node.tag==NS+'rect'and node.get('data-namelecule-atom'):rects.append(node);transforms.add(chain)
        for child in node:visit(child,chain)
    visit(root,())
    # Captured Main bonds/backplates share one drawing coordinate space.
    assert len(transforms)==1
    issues=[];li=0;diagonals=[]
    for a,b,order in row['bondGraph']:
        for line in lines[li:li+order]:
            x,y,u,v=[float(line.get(k))for k in ['x1','y1','x2','y2']];dx,dy=u-x,v-y
            if abs(dx)>1e-7 and abs(dy)>1e-7:diagonals.append([a,b])
            # Include the stroke envelope; existing backplates have no stroke.
            margin=float(line.get('stroke-width'))/2
            for rect in rects:
                atom=int(rect.get('data-namelecule-atom'))
                if atom in [a,b]:continue
                left,top,width,height=[float(rect.get(k))for k in ['x','y','width','height']]
                lo,hi=0.,1.
                for pos,delta,low,high in [(x,dx,left-margin,left+width+margin),
                                           (y,dy,top-margin,top+height+margin)]:
                    if abs(delta)<1e-10:
                        if pos<low or pos>high:hi=-1;break
                    else:
                        t1,t2=sorted([(low-pos)/delta,(high-pos)/delta]);lo=max(lo,t1);hi=min(hi,t2)
                if hi-lo>1e-8:issues.append({'bond':[a,b],'nonEndpointAtom':atom,
                                            'intersectionNativeUnits':(hi-lo)*math.hypot(dx,dy)})
        li+=order
    assert li==len(lines)
    return {'key':row['key'],'variant':row['variant'],'width':row['width'],'occlusions':issues,
            'diagonalStrokes':diagonals,'allStrokesOrthogonal':not diagonals}
if __name__=='__main__':
    source=Path(sys.argv[1])if len(sys.argv)>1 else HERE/'browser.json.gz'
    output=Path(sys.argv[2])if len(sys.argv)>2 else HERE/'backplate-check.json'
    data=json.load(gzip.open(source,'rt'));rows=[audit(r)for r in data['cases']]
    out={'passed':not any(r['occlusions']or r['diagonalStrokes']for r in rows),'cases':rows,
         'includesStrokeEnvelope':True,'source':str(source)}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':out['passed'],'cases':len(rows),'occlusions':sum(len(r['occlusions'])for r in rows)}))
    if not out['passed']:raise SystemExit(1)
