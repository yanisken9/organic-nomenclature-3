"""Approved9ester integration from frozen originals; no import-time writes."""
from pathlib import Path
import json,gzip,runpy,hashlib,re,argparse
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
base=json.loads((HERE/'baseline.json').read_text());KEYS=base['keys']
p=runpy.run_path(str(HERE.parent/'comparison/prepare.py'))
parse=p['parse'];literal=p['literal'];DATA=p['helpers']['DATA'];VIEWER='js/mulermoc-nom-molview-52.js';HTML='mulermoc-nom-52.html'
def outputs():
    original=json.load(gzip.open(HERE/'before-sources.json.gz','rt'));data=original[DATA];mols={}
    for key in KEYS:
        match,before=literal(data,key);candidate=p['proposal'](before,key)
        if key in base['accepted']:
            ref=base['accepted'][key];raw=(ROOT/ref['path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==ref['sha256']and raw.decode()==candidate
        mols[key]=candidate;data=data[:match.start(1)]+json.dumps(candidate)+data[match.end(1):]
    result={DATA:data}
    for name,key in base['sourceKeys'].items():
        lines,atoms,bonds=parse(original[name]);updated,new,edges=parse(mols[key]);n=len(atoms)
        assert bonds==edges and lines[:4]==updated[:4]
        assert [x[20:]for x in lines[4:4+n]]==[x[20:]for x in updated[4:4+n]]
        # Keep each original source's exact suffix, including its final blank
        # line; only coordinates need matching across source and embed.
        for i in range(n):lines[4+i]=updated[4+i][:20]+lines[4+i][20:]
        result[name]=''.join(lines)
    viewer=original[VIEWER]
    start=viewer.index('function fPrepareFixedCCAlkanePrototype()');end=viewer.index('function fGetUniform2DLibraryFrame()',start)
    function=viewer[start:end]
    function=function.replace('  const carbonylScale = ','  const esterScale = '+json.dumps(KEYS)+'.includes(selectedMol);\n  const carbonylScale = ',1)
    function=function.replace('(!etherScale && !carbonylScale && ![','(!etherScale && !carbonylScale && !esterScale && ![',1)
    function=function.replace('!((etherScale || carbonylScale) &&','!((etherScale || carbonylScale || esterScale) &&',1)
    viewer=viewer[:start]+function+viewer[end:];result[VIEWER]=viewer
    html=original[HTML]
    for name in [DATA,VIEWER]:
        pattern=re.escape(name)+r'\?v=[^"\s]+'
        assert len(re.findall(pattern,html))==1
        version=hashlib.sha256(result[name].encode()).hexdigest()[:12]
        html=re.sub(pattern,name+'?v=ester-uniform-20261101-'+version,html)
    result[HTML]=html;return original,result
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    original,result=outputs()
    if args.apply:
        for name in result:assert(ROOT/name).read_bytes()==original[name].encode(),('Baseline changed',name)
        for name,code in result.items():(ROOT/name).write_text(code)
    print(json.dumps({'esters':len(KEYS),'appPaths':len(result),'sourceMOLs':len(base['sourceKeys']),'applied':args.apply}))
