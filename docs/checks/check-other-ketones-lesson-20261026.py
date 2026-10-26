"""Static, actual inventory and baseline protection for the28-step lesson."""
from pathlib import Path
import json,hashlib,subprocess
root=Path(__file__).resolve().parents[2]
s=json.loads((root/'scenarios/other-ketones-nomenclature.scenario.json').read_text());steps=s['steps']
assert s['title']==s['scenario']=='Άλλες κετόνες' and len(steps)==28
keys=['penten_1_one_3','pentyn_4_one_2','penten_1_yn_4_one_3','dimethyl_4_5_hexen_5_yn_1_one_3','methyl_6_hepten_3_dione_2_5','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5']
assert [t['n']for t in steps]==list(range(1,29))
assert list(dict.fromkeys(t['selectedMol']for t in steps))==keys
modes={'compCarbonsCount':'comp5','compBondType':'comp6','compSuffix':'comp9','compBondPos':'comp4','compNumber1':'comp0','compSecondSub1':'comp1','compSecondSub2':'comp3','compEndNumber':'comp7'}
for t in steps:
 assert t['menuSubset']==keys and t['mainChainMode']=='algorithmic'
 assert not t['show']['rule'] and t['selectedRule']is None
 assert t['view3D']['showH'] and t['show']['viewers']['3D']==(t['n']==28)
 assert ':'not in t['note']+t['title']
 assert t['etherNamingMode']==t['styleName']['etherNaming']
 if t['nameAnalysisMode']!='none':assert modes[t['nameAnalysisMode']]not in t['styleName']['hidden']
 for k in keys:assert (root/'mols/nomeclature-moc2'/(k+'_3D.sdf')).is_file()
# Reuse the established in-memory applet adapter, not a new naming implementation.
ns={};exec((root/'docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
tail=ns['body'];tail=tail[tail.index('var MOL2D=window.MOL2D;'):tail.index('if(!probe){fParseSDF3D')]
files=['js/jsme-nick-nomeclature-moc2-data_51.js','js/mulermoc-nom-core-51.js','js/mulermoc-nom-molview-51.js']
prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
body=prefix+'\n'.join((root/p).read_text()for p in files)+tail+'return {key:key,name:currentMolName,parts:nameComponentsList,eligible:fIsAcyclicKetoneGraph(atomConnectivityList,allAtomsTypeList,bondList)&&!fIsAcyclicSaturatedMonoketoneGraph(atomConnectivityList,allAtomsTypeList,bondList)};'
data=(root/files[0]).read_text();js='var keys=(new Function("var window={};"+'+json.dumps(data)+'+";return Object.keys(window.MOL2D);"))(),run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+'),rows=[];for(var k of keys){var r=run(k,"condensed","algorithmic","",null);if(r.eligible)rows.push(r);}print(JSON.stringify(rows));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True)
rows=json.loads(r.stdout);assert set(row['key']for row in rows)==set(keys),rows
bykey={row['key']:row for row in rows}
for t in steps:
 if t['nameAnalysisMode']!='none':
  slot=int(modes[t['nameAnalysisMode']][4:]);assert bykey[t['selectedMol']]['parts'][slot],(t['n'],slot)
Path('docs/checks/other-ketones-lesson-static-20261026.json').write_text(json.dumps({'steps':len(steps),'inventory':rows,'checksPassed':True},ensure_ascii=False,indent=2)+'\n')
# The existing saturated lesson subsection stays byte-identical.
oldlib=Path('/tmp/namelecule-before-other-ketones-lesson-20261026/design/theory-library.html').read_text()
newlib=(root/'design/theory-library.html').read_text()
def monosection(text):
 start=text.index('<section class="lesson-part" aria-labelledby="monoketones-title">')
 return text[start:text.index('</section>',start)]
assert monosection(oldlib)==monosection(newlib)
lib=(root/'design/theory-library.html').read_text();start=lib.index('aria-labelledby="ketones-title"');card=lib[start:lib.index('</article>',start)]
assert '28 βήματα'in card and '2 διαθέσιμα μαθήματα'in card and 'other-ketones-nomenclature.scenario.json'in card and 'C<sub>x</sub>H<sub>y</sub>(CO)<sub>n</sub>'in card
other=card[card.index('aria-labelledby="other-ketones-title"'):];assert 'class="pending"'not in other and '<a 'in other
base=json.loads(Path('/tmp/namelecule-before-other-ketones-lesson-20261026/hashes.json').read_text());allowed={'README.md','design/theory-library.html','design/welcome-proposal.html','js/mulermoc-nom-scenario-51.js','mulermoc-nom-51.html','docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'}
protected=0
for p,h in base.items():
 if p in allowed:continue
 assert (root/p).is_file()and hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
 protected+=1
print('PASS28steps,all7eligiblemolecules,closedrules,optional3D,dualcard;',protected,'protectedfilesunchanged')
