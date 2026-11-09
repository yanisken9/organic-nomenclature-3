"""Bounded lesson contracts, actual42naming/2D3D cases and task-baseline preservation. --read-only avoids writes."""
from pathlib import Path
import json,subprocess,hashlib,gzip,base64,runpy,sys,re,difflib
s=json.loads(Path('scenarios/other-carboxylic-acids-nomenclature.scenario.json').read_text());steps=s['steps'];keys=steps[0]['menuSubset']
assert s['title']==s['scenario']=='Άλλα καρβοξυλικά οξέα'and s['scenarioVersion']==1 and s['app']=='mulermoc-nom-52'
assert not s['showStepNumbers']and s['reserveTitleSpace']
assert len(steps)==26 and [t['n']for t in steps]==list(range(1,27))
assert len(keys)==len(set(keys))==7 and list(dict.fromkeys(t['selectedMol']for t in steps))==keys
modes={'compCarbonsCount':'comp5','compBondType':'comp6','compSuffix':'comp9','compNumber1':'comp0','compSecondSub1':'comp1','compSecondSub2':'comp3','compBondType2':'comp8','compAcidNumber3':'acidPrefixNumber3','compAcidSub3':'acidPrefixSub3'}
for t in steps:
 assert t['menuSubset']==keys and t['mainChainMode']=='algorithmic'and t['chainIdx']==0
 assert t['mode2D']=='condensed'and t['style2D']['zoom']==2
 assert t['styleName']['cross']==bool(t['styleName']['hidden'])
 assert not t['show']['rule']and t['selectedRule']is None and not t['audio']['narrate']
 assert t['show']['viewers']['3D']==(t['n']==26)
 assert ':'not in t['note']and not any(q in t['note']for q in ['σωστή απάντηση','ισομέρ','E/Z','R/S'])
 if t['nameAnalysisMode']!='none':assert modes[t['nameAnalysisMode']]not in t['styleName']['hidden']
ns={};exec(Path('docs/checks/test-other-acids-naming-20261028.py').read_text().split("\njs='var run")[0],ns)
sdfs={k:Path('mols/nomeclature-moc2',k+'_3D.sdf').read_text()for k in keys}
js='var run=new Function("key","mode","chainMode","sdf","probe",'+json.dumps(ns['body'])+'),sdfs='+json.dumps(sdfs)+',rows=[];for(var k of '+json.dumps(keys)+')for(var mode of ["condensed","expanded","skeletal"])for(var chain of ["algorithmic","data"])rows.push({key:k,mode:mode,chainMode:chain,result:run(k,mode,chain,sdfs[k],null)});print(JSON.stringify(rows));'
def jsc(js):
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(js)+'\n',capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr);return r.stdout
rows=json.loads(jsc(js));parents=[3,3,5,6,5,6,7]
for row in rows:
 x=row['result'];assert len(x['chain'])==parents[keys.index(row['key'])]and x['signature']==x['signature3'],row
 names={r['key']:r['result']['name']for r in rows}
for k in keys:
 group=[r['result']for r in rows if r['key']==k];assert all(x['name']==group[0]['name']and x['signature']==group[0]['signature']for x in group)
# Exact eligibility from all current molecular graphs, independent of scenario selection.
helper=runpy.run_path('docs/checks/update-carboxyl-oh-20261028.py');inv=helper['inventory']();eligible=set()
for k,forms in inv.items():
 _,_,_,_,_,types,_,edges,groups=helper['parse'](forms['condensed'])
 multiple=any(types[a]==types[b]=='C'and order in [2,3]for a,b,order in edges)
 if multiple and len(groups)in[1,2]and types.count('O')==2*len(groups)and all(t in ['C','O','H','[H]']for t in types):eligible.add(k)
assert set(keys)==eligible and len(eligible)==7
assert 'δύο καρβοξυλομάδες'in steps[11]['note']and '-διικό οξύ'in steps[11]['note']
assert all(not any(q in t['note']for q in ['κετοπροπανικό','οξοβουτανικό','υδροξυ','αμινο'])for t in steps)
base=json.loads(Path('docs/checks/unsaturated-acids-lesson-before-20261028.json').read_text())['files'];old={p:base64.b64decode(v).decode()for p,v in json.loads(gzip.decompress(Path('docs/checks/unsaturated-acids-lesson-before-source-20261028.json.gz').read_bytes())).items()}
allowed=set(old)|{'docs/SESSION-NOTES.md','docs/YANNIS-CONTRIBUTIONS.md'};protected=0
for p,h in base.items():
 if p in allowed:continue
 assert Path(p).is_file()and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,('protected',p);protected+=1
lib=Path('design/theory-library.html').read_text();before=old['design/theory-library.html']
start='      <article class="lesson" id="carboxylic-acids-card"';assert before[:before.index(start)]==lib[:lib.index(start)]
assert lib.count('href="../mulermoc-nom-52.html?scenario=')==14
assert sum(len(json.loads(Path(f).read_text())['steps'])for f in re.findall(r'scenario=([^&"<>]+)',lib))==337
subprocess.run(['git','diff','--check'],check=True)
result={'passed':True,'steps':26,'molecules':7,'activeLessons':14,'totalLessonSteps':337,'names':names,'namingFormChainCases':len(rows),'eligibleKeys':sorted(eligible),'protectedFiles':protected,'core52SHA256':hashlib.sha256(Path('js/mulermoc-nom-core-52.js').read_bytes()).hexdigest()}
if '--read-only'not in sys.argv:
 Path('docs/checks/unsaturated-acids-lesson-static-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 Path('docs/checks/unsaturated-acids-lesson-source-20261028.diff').write_text(''.join(''.join(difflib.unified_diff(text.splitlines(True),Path(f).read_text().splitlines(True),fromfile='before/'+f,tofile='after/'+f))for f,text in old.items()))
print(json.dumps(result,ensure_ascii=False,indent=2))
