"""Focused static and protection checks for the approved26-step lesson."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[2]
p=root/'scenarios/other-aldehydes-nomenclature.scenario.json'
s=json.loads(p.read_text());steps=s['steps']
assert s['title']==s['scenario']=='Άλλες αλδεΰδες' and s['app']=='mulermoc-nom-51'
assert len(steps)==26 and [x['n'] for x in steps]==list(range(1,27))
keys=['propenal','propynal','methyl_2_propenal','propanedial','methyl_3_penten_2_dial','isopropyl_2_buten_2_dial','ethyl_4_penten_4_yn_2_al','ethyl_2_methyl_3_hexen_2_yn_4_dial']
assert list(dict.fromkeys(x['selectedMol'] for x in steps))==keys
for x in steps:
 assert x['menuSubset']==keys
 assert x['mainChainMode']=='algorithmic' and not x['show']['rule']
 assert x['view3D']['showH'] and x['show']['viewers']['3D']==(x['n']==26)
 assert x['etherNamingMode']==x['styleName']['etherNaming']
 assert ':' not in x['title']+x['note']
 for k in keys:
  assert (root/'mols/nomeclature-moc2'/ (k+'_3D.sdf')).is_file()
 assert not any(k in x for k in ['questions','answers','quiz'])
lib=(root/'design/theory-library.html').read_text()
assert '26 βήματα' in lib and '2 διαθέσιμα μαθήματα' in lib
assert 'scenarios/other-aldehydes-nomenclature.scenario.json' in lib
part=lib[lib.index('aria-labelledby="other-aldehydes-title"'):]
assert 'class="pending"' not in part
assert '"Άλλες αλδεΰδες"' in (root/'js/mulermoc-nom-scenario-51.js').read_text()
base=json.loads(Path('/tmp/namelecule-before-other-aldehydes-lesson-20261026/manifest.json').read_text())
allowed={'README.md','design/theory-library.html','design/welcome-proposal.html','js/mulermoc-nom-scenario-51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for name,h in base.items():
 if name in allowed:continue
 assert (root/name).is_file() and hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
 protected+=1
print('PASS26steps,8existingmolecules,manualrules,optional3D;protected',protected)
