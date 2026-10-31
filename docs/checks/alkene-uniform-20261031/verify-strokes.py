"""Exact visible stroke comparison from recorded, actual browser SVGs.

The raster oracle samples at quarter-pixel intervals. This separate interval
union avoids using raster sampling error as a bond-length inequality.
"""
from pathlib import Path
import argparse, json, gzip, xml.etree.ElementTree as ET

def interval(a,b,r):
    lo,hi=0.,1.
    for start,delta,left,right in [(a[0],b[0]-a[0],r[0],r[2]),(a[1],b[1]-a[1],r[1],r[3])]:
        if abs(delta)<1e-12:
            if start<left or start>right:return None
        else:
            x,y=sorted([(left-start)/delta,(right-start)/delta]);lo=max(lo,x);hi=min(hi,y)
            if hi<lo:return None
    return lo,hi

def verify(controls):
    rows=[];ns={'s':'http://www.w3.org/2000/svg'}
    for c in controls['cases']:
        if c['phase'] not in ['selected','zoom-0.5','zoom-6','zoom-2']:continue
        root=ET.fromstring(c['rawFinalSVG']);rects=[]
        for e in root.findall('.//s:rect',ns):
            if e.get('data-namelecule-role')=='backplate':
                x,y,w,h=[float(e.get(v))for v in ['x','y','width','height']];rects.append((x,y,x+w,y+h))
        vals={'CC':[],'CH':[]};lines=root.findall('.//s:line',ns);idx=0
        for a,b,order in c['bondGraph']:
            kind='CC' if c['atomSymbols'][a-1]==c['atomSymbols'][b-1] else 'CH'
            for offset in range(order):
                e=lines[idx];v=c['raster']['lineVisibility'][idx];idx+=1
                axy=tuple(float(e.get(k))for k in ['x1','y1']);bxy=tuple(float(e.get(k))for k in ['x2','y2'])
                spans=sorted(s for r in rects if(s:=interval(axy,bxy,r))is not None)
                covered=end=0.
                for lo,hi in spans:
                    if hi>end:covered+=hi-max(lo,end);end=hi
                vals[kind].append(v['length']*(1-covered))
        row={'key':c['key'],'width':c['width'],'phase':c['phase'],
             'CCVariationCSS':max(vals['CC'])-min(vals['CC']),
             'CHVariationCSS':max(vals['CH'])-min(vals['CH'])}
        assert row['CCVariationCSS']<.12 and row['CHVariationCSS']<.12,row
        rows.append(row)
    assert len(rows)==56
    return {'states':56,'method':'Exact segment/rectangle interval union in saved SVG, scale from actual screen segment length; includes both C=C lines.',
            'maxCCVariationCSS':max(r['CCVariationCSS']for r in rows),
            'maxCHVariationCSS':max(r['CHVariationCSS']for r in rows),'passed':True,'cases':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=verify(json.load(gzip.open(args.controls,'rt')));args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='cases'}))
