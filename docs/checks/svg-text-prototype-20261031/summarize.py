from pathlib import Path
import gzip,json,math,statistics,hashlib,xml.etree.ElementTree as ET,html
here=Path(__file__).resolve().parent;repo=here.parents[2]
raw=json.loads(gzip.decompress((here/'browser.json.gz').read_bytes()));inv=json.loads(gzip.decompress((here/'invariants.json.gz').read_bytes()))
pairs={};states={}
for r in raw['cases']:pairs.setdefault((r['fixture'],r['font']),{})[r['version']]=r
for r in inv['cases']:states.setdefault((r['fixture'],r['font']),{})[r['version']]=r
assert raw['completed'] and inv['completed'] and not raw['javascriptErrors'] and not inv['javascriptErrors']
assert len(pairs)==92 and len(states)==92
summary={'nativeCases':184,'pairedComparisons':92,'fixtures':23,'fonts':[9,12,14,16],'rasterScale':'64 raster pixels per requested font em; contact means ink within Chebyshev radius 2 of visible bond pixels','versions':{},'invariants':{},'limitations':['Firefox/macOS active FEB169 permutation only','Native producer, no app integration, lesson, JSmol, numbering or highlight interaction tests','No late font-load invalidation or production-safe fallback; missing metrics throws','Timing includes BiDi overhead; not a performance benchmark']}
for version in ['baseline','candidate']:
 rows=[r for r in raw['cases'] if r['version']==version]
 summary['versions'][version]={'cases':len(rows),'casesWithUncoveredGlyphInk':sum(r['raster']['uncoveredInkPixels']>0 for r in rows),'casesWithBondContact':sum(r['raster']['inkPixelsWithin2pxOfBond']>0 for r in rows),'casesWithFullyHiddenLine':sum(r['raster']['hiddenLines']>0 for r in rows),'drawAndTransportMedianMs':statistics.median(r['drawAndTransportMs'] for r in rows)}
maxcoord=0;maxline=0
for key,p in states.items():
 a,b=p['baseline'],p['candidate'];assert a['bonds']==b['bonds'];assert len(a['atoms'])==len(b['atoms'])
 # Only the generated JME timestamp header is excluded, never an atom/bond line.
 assert a['mol'].splitlines()[2:]==b['mol'].splitlines()[2:]
 for x,y in zip(a['atoms'],b['atoms']):
  assert {k:v for k,v in x.items()if k not in ['x','y']}=={k:v for k,v in y.items()if k not in ['x','y']}
  for k in ['x','y']:maxcoord=max(maxcoord,abs(x[k]-y[k]))
for key,p in pairs.items():
 a,b=p['baseline'],p['candidate'];assert len(a['lines'])==len(b['lines'])
 for x,y in zip(a['lines'],b['lines']):
  for k in ['stroke','stroke-width']:assert x.get(k)==y.get(k)
  d=math.hypot((float(x['x2'])-float(x['x1']))-(float(y['x2'])-float(y['x1'])),(float(x['y2'])-float(x['y1']))-(float(y['y2'])-float(y['y1'])))
  maxline=max(maxline,d)
 assert [(l['text'],l['tspans']) for l in a['labels']]==[(l['text'],l['tspans']) for l in b['labels']]
 for x,y in zip(a['labels'],b['labels']):
  assert {k:v for k,v in x['textAttrs'].items()if k not in ['x','y']}=={k:v for k,v in y['textAttrs'].items()if k not in ['x','y']}
assert maxcoord<1e-10 and maxline<=math.sqrt(2)+1e-9
assert all(r['sameSVG']for r in inv['rebuild'])
assert summary['versions']['candidate']['casesWithUncoveredGlyphInk']==summary['versions']['candidate']['casesWithBondContact']==summary['versions']['candidate']['casesWithFullyHiddenLine']==0
summary['invariants']={'atomCoordinatesRelativeToAtom1MaxDifference':maxcoord,'svgLineVectorMaxDifferenceFromIntegerRounding':maxline,'molecularGraphAtomIDsChargesIsotopesAndMOLBody':'unchanged in 92 pairs; generated timestamp excluded','labelsColorsFontsSubSuperRanges':'unchanged in 92 pairs; text positions and backplates intentionally change','rebuild':inv['rebuild'],'javascriptErrors':0}
base=json.loads((here/'baseline.json').read_text());summary['productionProtected']={p:hashlib.sha256((repo/p).read_bytes()).hexdigest()==h for p,h in base['production'].items()};assert all(summary['productionProtected'].values())
(here/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# Read-only offline native SVG comparison, with identical scale within each pair.
ET.register_namespace('','http://www.w3.org/2000/svg');ns='{http://www.w3.org/2000/svg}'
def cropped(svg):
 node=ET.fromstring(svg);points=[]
 for g in node.iter(ns+'g'):g.attrib.pop('transform',None)
 for parent in node.iter():
  children=list(parent)
  for i,e in enumerate(children):
   tag=e.tag.rsplit('}',1)[-1]
   paired=i+1<len(children)and children[i+1].tag==ns+'text'
   if tag=='polygon' or(tag=='rect'and not paired):parent.remove(e)
 for e in node.iter():
  tag=e.tag.rsplit('}',1)[-1]
  if tag=='rect':
   x,y,w,h=[float(e.get(k))for k in ['x','y','width','height']];points.extend([(x,y),(x+w,y+h)])
  if tag=='line':points.extend([(float(e.get('x1')),float(e.get('y1'))),(float(e.get('x2')),float(e.get('y2')))])
 lo=[min(p[k]for p in points)-120 for k in [0,1]];hi=[max(p[k]for p in points)+120 for k in [0,1]]
 return node,lo,[hi[k]-lo[k]for k in [0,1]]
parts=[]
for fixture,font,title in [('propene/expanded/annotated',9,'Προπένιο — μέγεθος 9'),('propene/expanded/annotated',14,'Προπένιο — μέγεθος 14'),('dimethyl_2_3_butane/expanded/annotated',9,'2,3-διμεθυλοβουτάνιο — κοντοί C–H'),('synthetic/ammonium',9,'Δοκιμή δείκτη και φορτίου')]:
 p=pairs[(fixture,font)];nodes=[cropped(p[v]['svg'])for v in ['baseline','candidate']];w=max(n[2][0]for n in nodes);h=max(n[2][1]for n in nodes)
 cards=[]
 for label,(node,lo,sz)in zip(['Αρχικό JSME','Δοκιμαστικός παραγωγός'],nodes):
  node.set('viewBox',f'{lo[0]-(w-sz[0])/2} {lo[1]-(h-sz[1])/2} {w} {h}');node.set('width','100%');node.set('height','320')
  cards.append('<figure><figcaption>'+label+'</figcaption>'+ET.tostring(node,encoding='unicode')+'</figure>')
 parts.append('<section><h2>'+title+'</h2><div class="pair">'+''.join(cards)+'</div></section>')
(here/'comparison.html').write_text('<!doctype html><html lang="el"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Δοκιμή αρχικού παραγωγού SVG</title><style>body{font:18px system-ui;margin:30px auto;padding:0 24px;max-width:1250px;color:#214c50;background:#f7faf8}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}figure{margin:0;padding:16px;border:1px solid #abc9c4;border-radius:16px;background:white}figcaption{font-weight:650}h2{font-size:22px}section{margin-top:30px}svg{display:block} @media(max-width:700px){.pair{grid-template-columns:1fr}}</style><h1>Δοκιμή στον παραγωγό του JSME</h1><p>Απομονωμένο πείραμα, χωρίς αλλαγή στην κύρια εφαρμογή. Τα δείγματα εμφανίζονται με μεγέθυνση και κοινή κλίμακα ανά ζεύγος. Πρόκειται για αρχικά SVG χωρίς επεξεργασία του viewer.</p>'+''.join(parts)+'</html>')
print(json.dumps(summary,ensure_ascii=False,indent=2))
