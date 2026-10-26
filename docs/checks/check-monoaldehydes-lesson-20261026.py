"""Focused static/protection checks; read-only, no dependencies."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[2]
s=json.loads((root/'scenarios/saturated-monoaldehydes-nomenclature.scenario.json').read_text())
steps=s['steps'];assert len(steps)==24
keys=steps[0]['menuSubset'];assert len(keys)==len(set(keys))==9
counts=[1,2,3,4,4,5,6,8,12];count=dict(zip(keys,counts))
assert [count[x['selectedMol']] for x in steps]==sorted(count[x['selectedMol']] for x in steps)
assert list(dict.fromkeys(x['selectedMol'] for x in steps))==keys
assert [x['n'] for x in steps]==list(range(1,25))
data=(root/'js/jsme-nick-nomeclature-moc2-data_51.js').read_text()
for key in keys:assert key in data,key
for x in steps:
 assert x['menuSubset']==keys
 assert x['etherNamingMode']==x['styleName']['etherNaming']
 assert not x['show']['rule']
 assert x['mainChainMode']=='algorithmic'
 assert x['show']['viewers']['3D']==(x['n']==24)
 assert x['view3D']['showH']
 assert '?' not in x['note'] and 'κουίζ' not in x['note']
 assert ':' not in x['title']+x['note']
lib=(root/'design/theory-library.html').read_text()
assert 'ΑΛΔΕΫΔΕΣ' in lib and '24 βήματα' in lib
assert 'scenarios/saturated-monoaldehydes-nomenclature.scenario.json' in lib
assert 'other-aldehydes-title' in lib and '1 διαθέσιμο μάθημα' in lib
assert 'propynal' not in keys
baseline=Path('/tmp/namelecule-before-aldehyde-lesson-20261026/manifest.json')
if baseline.exists():
 m=json.loads(baseline.read_text());allowed={'README.md','design/theory-library.html','design/welcome-proposal.html','js/mulermoc-nom-scenario-51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
 changed=[p for p,h in m.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
 assert set(changed)<=allowed,changed
 print('PASS baseline protection: all pre-existing scenarios, MOL/SDF, data, core/viewer/teaching unchanged')
print('PASS 24 sequential steps, 9 ordered existing molecules, matching naming state, manual rules, optional 3D, library link')
