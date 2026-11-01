"""Build fair, font-normalized SVG pairs from actual captured renderer output."""
from pathlib import Path
import gzip,json,hashlib,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
def image_url(name):
    return name+'?v='+hashlib.sha256((HERE/name).read_bytes()).hexdigest()
d=json.load(gzip.open(HERE/'browser.json.gz','rt'));assert d['completed']and not d['javascriptErrors']
geometry=json.loads((HERE/'geometry.json').read_text());gallery=[]
for item in geometry['molecules']:
    key=item['key'];rows=[r for r in d['cases']if r['key']==key and r['width']==1500];assert len(rows)==2
    left=min(r['bounds']['left']for r in rows)-1;right=max(r['bounds']['right']for r in rows)+1
    top=min(r['bounds']['top']for r in rows)-1;bottom=max(r['bounds']['bottom']for r in rows)+1;box=[left,top,right-left,bottom-top]
    accent=[]
    for edge in item['stems']:
        index=next(i for i,b in enumerate(rows[0]['bondGraph'])if set(b[:2])==set(edge['atoms']))
        start=sum(b[2]for b in rows[0]['bondGraph'][:index]);accent.extend(range(start,start+rows[0]['bondGraph'][index][2]))
    for row in rows:
        source=E.fromstring(row['rawSVG']);lines=list(source.iter('{'+NS+'}line'))
        for i in accent:
            style=lines[i].get('style','');lines[i].set('style',style+';stroke:#a45f36;');lines[i].set('stroke','#a45f36')
        # Remove only the native canvas background, never atom backplates.
        for parent in source.iter():
            for node in list(parent):
                if node.tag=='{'+NS+'}rect'and node.get('x')=='0'and node.get('y')=='0'and node.get('rx')is None and node.get('ry')is None:parent.remove(node)
        root=E.Element('{'+NS+'}svg',{'viewBox':' '.join(map(str,box)),'width':str(box[2]*26),'height':str(box[3]*26),'preserveAspectRatio':'xMidYMid meet','role':'img'})
        title=E.SubElement(root,'{'+NS+'}title');title.text=row['name']+' — '+row['variant']
        group=E.SubElement(root,'{'+NS+'}g',{'transform':'translate(%s %s) scale(%s)'%(-row['cx']/row['fontRoot'],-row['cy']/row['fontRoot'],1/row['fontRoot'])})
        for child in source:group.append(child)
        (HERE/(key+'-'+row['variant']+'.svg')).write_bytes(E.tostring(root,encoding='utf-8',xml_declaration=True))
    gallery.append({'key':key,'name':rows[0]['name'],'viewBox':box,'widthEm':box[2],'heightEm':box[3],
                    'stems':item['stems'],'verticalEthylTurns':item['verticalEthylTurns'],
                    'layoutAdjustments':item['layoutAdjustments'],
                    'highlightedNativeLineIndices':accent,'sameFontNormalization':True,
                    'parentMidpointAligned':True,'images':{v:image_url(key+'-'+v+'.svg')for v in ['before','proposed']}})
(HERE/'figure-framing.json').write_text(json.dumps({'defaultAtomFontCSS':26,'molecules':gallery,'applicationFramingChanged':False},ensure_ascii=False,indent=2)+'\n')
template=(HERE/'template.html').read_text();payload=json.dumps(gallery,ensure_ascii=False).replace('<','\\u003c')
(HERE/'index.html').write_text(template.replace('PAGE_DATA',payload))
print(json.dumps({'figures':len(gallery)*2,'sameFrameWithinEachPair':True,'sameGlyphSizeAcrossAllPairs':True}))
