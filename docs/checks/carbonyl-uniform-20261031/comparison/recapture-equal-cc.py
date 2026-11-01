"""Recapture molecules 1/3/6; reuse only unchanged, archived capture inputs."""
from pathlib import Path
import json,gzip,hashlib,tarfile
HERE=Path(__file__).resolve().parent
baseline=json.loads((HERE/'equal-cc-baseline.json').read_text())
archive=HERE.parents[3]/baseline['snapshot']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==baseline['snapshotSHA256']
keys=[json.loads((HERE/'geometry.json').read_text())['molecules'][i]['key']for i in [0,2,5]]
with tarfile.open(archive,'r:gz')as saved:
    prior=json.loads(gzip.decompress(saved.extractfile('comparison/browser.json.gz').read()))
    assert prior['completed']and not prior['javascriptErrors']
    reused=[r for r in prior['cases']if r['key']not in keys]
    for row in reused:
        name=row['key']+'-'+row['variant']+'.mol'
        assert (HERE/name).read_bytes()==saved.extractfile('comparison/'+name).read()
    for name in ['original-calibration.js','preview-calibration.js']:
        assert (HERE/name).read_bytes()==saved.extractfile('comparison/'+name).read()
source=(HERE/'capture.py').read_text();needle="KEYS=runpy.run_path(str(HERE/'prepare.py'))['KEYS']"
assert source.count(needle)==1
exec(compile(source.replace(needle,'KEYS='+repr(keys)),'targeted-equal-cc-capture','exec'),
     {'__file__':str(HERE/'capture.py'),'__name__':'__main__'})
current=json.load(gzip.open(HERE/'browser.json.gz','rt'))
assert current['completed']and len(current['cases'])==9 and not current['javascriptErrors']
(HERE/'targeted-equal-cc-browser.json.gz').write_bytes((HERE/'browser.json.gz').read_bytes())
current['cases']=reused+current['cases'];assert len(current['cases'])==18
current['targetedRecapture']={'keys':keys,'newCases':9,'reusedUnchangedInputCases':9,
                             'retainedEvidenceArchive':str(archive),'inputComparison':'exact archived MOL/calibration bytes'}
(HERE/'browser.json.gz').write_bytes(gzip.compress(json.dumps(current,ensure_ascii=False).encode(),mtime=0))
print(json.dumps({'completed':True,'cases':18,'newCases':9,'unchangedCasesReused':9}))
