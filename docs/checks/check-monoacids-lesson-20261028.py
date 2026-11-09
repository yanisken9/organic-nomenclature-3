"""Read-only with --read-only:28steps, actual inventory/naming/graphs, preservation."""
from pathlib import Path
import json,subprocess,hashlib,gzip,base64,runpy,sys,difflib,ast
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
p=Path('scenarios/saturated-monocarboxylic-acids-nomenclature.scenario.json');s=json.loads(p.read_text());steps=s['steps'];title='Κορεσμένα μονοκαρβοξυλικά οξέα'
keys=['methanoicacid','propionicacid','butanoic_acid','methyl_2_propanoic_acid','pentanoic_acid','dimethyl_2_2_propanoic_acid','ethyl_2_methyl_3_pentanoic_acid','ethyl_3_isopropyl_2_dimethyl_4_5_hexanoic_acid']
names=['μεθανικό οξύ','προπανικό οξύ','βουτανικό οξύ','2-μεθυλοπροπανικό οξύ','πεντανικό οξύ','2,2-διμεθυλοπροπανικό οξύ','2-αιθυλο-3-μεθυλοπεντανικό οξύ','3-αιθυλο-2-ισοπροπυλο-4,5-διμεθυλοεξανικό οξύ']
parents=[1,3,4,3,5,3,5,6];counts=[1,3,4,4,5,5,8,13]
assert s['title']==s['scenario']==title and s['app']=='mulermoc-nom-52'and s['scenarioVersion']==1 and s['reserveTitleSpace']and not s['showStepNumbers']
assert len(steps)==28 and [t['n']for t in steps]==list(range(1,29))and list(dict.fromkeys(t['selectedMol']for t in steps))==keys
modes={'compCarbonsCount':'comp5','compBondType':'comp6','compSuffix':'comp9','compNumber1':'comp0','compSecondSub1':'comp1','compSecondSub2':'comp3','compAcidNumber3':'acidPrefixNumber3','compAcidSub3':'acidPrefixSub3'}
for t in steps:
 assert t['menuSubset']==keys and t['mainChainMode']=='algorithmic'and t['chainIdx']==0
 assert t['mode2D']=='condensed'and t['style2D']['zoom']==2
 assert t['styleName']['cross']==(t['n']in[1,2,3,9,10,13,14,16,17,21])
 assert t['selectedRule']is None and not t['show']['rule']and not t['audio']['narrate']
 assert t['view3D']['showH']and t['show']['viewers']['3D']==(t['n']==28)
 if t['nameAnalysisMode']!='none':assert modes[t['nameAnalysisMode']]not in t['styleName']['hidden']
 assert not any(q in t['note']for q in ['σωστή απάντηση','ισομέρ','E/Z','R/S'])
# Reuse the established real JS applet adapter with current52 sources.
ns={};exec(Path('docs/checks/test-alcohols-naming-20261024.py').read_text().split("js='var run")[0],ns)
t=ns['body'];tail=t[t.index('var MOL2D=window.MOL2D;'):t.index('return {name:currentMolName')]
files=['js/jsme-nick-nomeclature-moc2-data_52.js','js/mulermoc-nom-core-52.js','js/mulermoc-nom-molview-52.js'];prefix='var window={},console={log(){},warn(){},error(){}},document={getElementById(){return null},addEventListener(){}};'
ret='return {key:key,name:currentMolName,eligible:fIsAcyclicSaturatedMonoacidGraph(atomConnectivityList,allAtomsTypeList,bondList),chain:mainChainAtomsList,signature:fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList),signature3:fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D)};'
body=prefix+'\n'.join(Path(f).read_text()for f in files)+tail+ret
inv=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py')['inventory']();sdfs={k:Path('mols/nomeclature-moc2',k+'_3D.sdf').read_text()for k in inv}
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(body)+'),inv='+json.dumps(inv)+',sdfs='+json.dumps(sdfs)+',eligible=[],rows=[];for(var k of Object.keys(inv)){var r=run(k,"condensed","algorithmic",sdfs[k],null);if(r.eligible)eligible.push(k);}for(var k of '+json.dumps(keys)+')for(var mode of ["condensed","expanded","skeletal"])for(var chain of ["algorithmic","data"])rows.push({mode:mode,chainMode:chain,result:run(k,mode,chain,sdfs[k],null)});print(JSON.stringify({eligible:eligible,rows:rows}));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
actual=json.loads(r.stdout);assert set(actual['eligible'])==set(keys)
for row in actual['rows']:
 x=row['result'];i=keys.index(x['key']);assert x['name']==names[i]and len(x['chain'])==parents[i]and x['signature']==x['signature3'],row
def chemical_graph(m):
 m=Chem.RemoveHs(m)
 for atom in m.GetAtoms():
  if atom.HasProp('molAtomMapNumber'):atom.ClearProp('molAtomMapNumber')
 return Chem.MolToSmiles(m,isomericSmiles=False)
for k,n in zip(keys,counts):
 reference=None
 for mode,block in inv[k].items():
  if not block:continue
  m=Chem.MolFromMolBlock(block,removeHs=False);assert m
  assert rdMolDescriptors.CalcMolFormula(m)==f'C{n if n>1 else ""}H{2*n}O2'
  graph=chemical_graph(m)
  if reference is None:reference=graph
  assert graph==reference,(k,mode)
 m=Chem.MolFromMolBlock(sdfs[k],removeHs=False);assert m and chemical_graph(m)==reference
# Old lesson JSONs, all molecular data, viewer/core/teaching/React are protected.
base=json.loads(Path('docs/checks/monoacids-lesson-before-20261028.json').read_text())['files'];old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/monoacids-lesson-before-source-20261028.json.gz').read_bytes())).items()}
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'};protected=0
for p,h in base.items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('protected',p);protected+=1
lib=Path('design/theory-library.html').read_text();before=old['design/theory-library.html'];a=before.index('      <article class="lesson" id="carboxylic-acids-card"');b=lib.index('      <article class="lesson" id="carboxylic-acids-card"');assert before[:a]==lib[:b]
a=before.index('          <section class="lesson-part" aria-labelledby="other-carboxylic-acids-title"');b=lib.index('          <section class="lesson-part" aria-labelledby="other-carboxylic-acids-title"');assert before[a:]==lib[b:]
assert '28 βήματα'in lib
assert lib.count('<article class="lesson"')==10 and lib.count('href="../mulermoc-nom-52.html?scenario=')==13
# Compare rule availability for every existing linked lesson step before/after.
player='js/mulermoc-nom-scenario-52.js';oldsrc=old[player];newsrc=Path(player).read_text()
def rule_body(src):
 a=src.index('function fScenarioShowComponentRule(mode)');b=src.index('// Optional authored reference',a)
 return 'var MuLERMoCScenario={present:true};function fScenarioPresent(){return {title:title};}'+src[a:b]+'return fScenarioShowComponentRule(mode);'
oldlessons=[]
import re
for file in re.findall(r'scenario=([^&"<>]+)',before):
 d=json.loads(Path(file).read_text());oldlessons.extend([d['title'],t['nameAnalysisMode']]for t in d['steps'])
js='var a=new Function("title","mode",'+json.dumps(rule_body(oldsrc))+'),b=new Function("title","mode",'+json.dumps(rule_body(newsrc))+');for(var t of '+json.dumps(oldlessons)+')if(a.apply(null,t)!==b.apply(null,t))throw Error(JSON.stringify(t));print("PASS old rule cases");'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr)
# Runtime player validation/capture/apply is also exercised in the browser check.

node='/tmp/namelecule-react-tools/node-v24.22.1-darwin-x64/bin/node'
for f in ['js/mulermoc-nom-scenario-52.js']:subprocess.run([node,'--check',f],check=True)
subprocess.run(['git','diff','--check'],check=True)
assert len(oldlessons)==283
result={'passed':True,'activeLessons':13,'totalLessonSteps':len(oldlessons)+len(steps),'steps':28,'keys':keys,'names':names,'formChainCases':len(actual['rows']),'oldRuleCases':len(oldlessons),'protectedFiles':protected,'existingScenarioFiles':len([p for p in base if p.startswith('scenarios/')and p.endswith('.json')]),'core52SHA256':hashlib.sha256(Path('js/mulermoc-nom-core-52.js').read_bytes()).hexdigest()}
if '--read-only'not in sys.argv:
 Path('docs/checks/monoacids-lesson-static-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 diff=''.join(''.join(difflib.unified_diff(text.splitlines(True),Path(f).read_text().splitlines(True),fromfile='before/'+f,tofile='after/'+f))for f,text in old.items());Path('docs/checks/monoacids-lesson-source-20261028.diff').write_text(diff)
print('PASS',result)
