"""Read-only protection and authored lesson reference checks."""
from pathlib import Path
import json,hashlib
base=Path('/tmp/namelecule-before-alkoxy-rule-20261026')
s=json.load(open('scenarios/saturated-monoethers-nomenclature.scenario.json'));old=json.loads((base/'scenarios/saturated-monoethers-nomenclature.scenario.json').read_text())
active=[4,5,6,8,9,10,11,12,14,15,16,17,19,20,22,23,25,26,27]
assert len(s['steps'])==len(old['steps'])==27
for a,b in zip(s['steps'],old['steps']):
 c=json.loads(json.dumps(a))
 if a['n'] in active:
  assert a['show']['alkoxyRule'] is True
  assert 'Ονόματα αλκοξυομάδων και προθέματα' in a['note']
  assert a['note'].startswith(b['note']+'\n')
  c['note']=b['note'];del c['show']['alkoxyRule']
 else:assert 'alkoxyRule' not in a['show']
 assert c==b,('unapproved step changes',a['n'])
 assert ':' not in a['note']+a['title']
assert {k:v for k,v in s.items() if k!='steps'}=={k:v for k,v in old.items() if k!='steps'}
allowed={'js/mulermoc-nom-teaching-51.js','js/mulermoc-nom-molview-51.js','js/mulermoc-nom-scenario-51.js','mulermoc-nom-51.html','scenarios/saturated-monoethers-nomenclature.scenario.json','design/theory-library.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
manifest=json.loads((base/'manifest.json').read_text());n=0
for path,h in manifest.items():
 if path in allowed:continue
 assert Path(path).is_file() and hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
 n+=1
print('PASS 19 reference notes/flags,27steps otherwise identical;',n,'protected files unchanged including core/data/MOL/other lessons')
