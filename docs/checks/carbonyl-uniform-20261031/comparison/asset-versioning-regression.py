"""Verify URL/content correspondence and isolated rebuild invalidation."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import tempfile,subprocess,shutil,json,gzip,hashlib,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent
def versions(folder):
    out={}
    for item in json.loads((folder/'figure-framing.json').read_text())['molecules']:
        for variant,url in item['images'].items():
            parts=urlsplit(url);digest=hashlib.sha256((folder/parts.path).read_bytes()).hexdigest()
            assert parse_qs(parts.query)=={'v':[digest]}
            out[parts.path]=url
    return out
baseline=json.loads((HERE/'asset-versioning-baseline.json').read_text())
protected=[f for f in baseline['files']if Path(f).suffix in ['.mol','.svg']or
           Path(f).name in ['geometry.json','browser.json.gz','prepare.py','original-calibration.js','preview-calibration.js']]
assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==baseline['files'][f]for f in protected)
live=versions(HERE);assert len(live)==12
with tempfile.TemporaryDirectory(prefix='namelecule-asset-hash-regression-')as work:
    folder=Path(work)
    for name in ['build.py','template.html','geometry.json','browser.json.gz']:shutil.copyfile(HERE/name,folder/name)
    def build():subprocess.run(['python3','-B',str(folder/'build.py')],check=True,capture_output=True)
    build();first=versions(folder);assert first==live
    build();assert versions(folder)==first
    # Alter only a non-rendered SVG description in one isolated capture.
    captures=json.load(gzip.open(folder/'browser.json.gz','rt'))
    key=json.loads((folder/'geometry.json').read_text())['molecules'][0]['key']
    row=next(r for r in captures['cases']if r['key']==key and r['variant']=='proposed'and r['width']==1500)
    root=E.fromstring(row['rawSVG']);E.SubElement(root,'{http://www.w3.org/2000/svg}desc').text='Isolated content-version regression'
    row['rawSVG']=E.tostring(root,encoding='unicode')
    (folder/'browser.json.gz').write_bytes(gzip.compress(json.dumps(captures).encode(),mtime=0))
    build();second=versions(folder)
    changed=[name for name in first if first[name]!=second[name]]
    assert changed==[key+'-proposed.svg'],changed
out={'date':'2026-11-01','passed':True,'versionedFigures':12,'protectedPreviewFilesUnchanged':len(protected),
     'sameInputStableURLs':True,'oneChangedSVGChangesOnlyItsURL':True,
     'mutationIsolatedTemporaryDirectory':True,'changedFixtureImage':changed[0]}
(HERE/'asset-versioning-regression.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
