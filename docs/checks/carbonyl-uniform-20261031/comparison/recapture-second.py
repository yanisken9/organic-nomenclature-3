"""Recapture only corrected molecule 2; retain verified unchanged capture inputs."""
from pathlib import Path
import json,gzip,hashlib
HERE=Path(__file__).resolve().parent;SAVED=HERE/'spacing-v-first-attempt'
KEY='ethyl_4_isopropyl_3_methyl_2_hexanal'
prior=json.load(gzip.open(SAVED/'browser.json.gz','rt'))
assert prior['completed']and not prior['javascriptErrors']
hashes=json.loads((SAVED/'input-mol-hashes.json').read_text())
reused=[r for r in prior['cases']if r['key']!=KEY]
for row in reused:
    name=row['key']+'-'+row['variant']+'.mol'
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==hashes[name]
source=(HERE/'capture.py').read_text()
needle="KEYS=runpy.run_path(str(HERE/'prepare.py'))['KEYS']"
assert source.count(needle)==1
scope={'__file__':str(HERE/'capture.py'),'__name__':'__main__'}
exec(compile(source.replace(needle,'KEYS='+repr([KEY])),'targeted-capture','exec'),scope)
current=json.load(gzip.open(HERE/'browser.json.gz','rt'))
assert current['completed']and len(current['cases'])==3 and not current['javascriptErrors']
(HERE/'targeted-orthogonal-browser.json.gz').write_bytes((HERE/'browser.json.gz').read_bytes())
current['cases']=reused+current['cases'];assert len(current['cases'])==18
current['targetedRecapture']={'key':KEY,'newCases':3,'reusedUnchangedInputCases':15,
                             'retainedEvidence':'spacing-v-first-attempt/browser.json.gz',
                             'retainedInputHashes':'spacing-v-first-attempt/input-mol-hashes.json'}
(HERE/'browser.json.gz').write_bytes(gzip.compress(json.dumps(current,ensure_ascii=False).encode(),mtime=0))
print(json.dumps({'completed':True,'cases':18,'targetedRecaptureCases':3,'unchangedCasesReused':15}))
