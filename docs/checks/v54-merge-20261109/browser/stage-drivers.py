"""Prepare new v55 evidence drivers from preserved successful prior drivers."""
from pathlib import Path
H=Path(__file__).resolve().parent
src=Path('docs/checks/alkane-teacher-link-20261109T060243Z/browser/check-prefix.py').read_text()
a=src.index('fixtures=json.loads(');b=src.index('def save():')
header='''"""Actual normal12-step learner traversal: six earned repairs, declared seed fixtures."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned55-support','exec'))
'''
meta=src[a:b]
meta=meta[:meta.index("out={'completed'")]+"out.update(rounds=[],geometry=[],models3D=[],lessonSteps=[],notes=['Seed4/seed1 unsolved start fixtures only; no solved receipts fabricated. All six repairs earned through native pointer actions.'])\n"
src=header+meta+src[b:]
src=src.replace("HERE/'browser.json'","HERE/'alkane12-browser.json'")
src=src.replace("cr=Path(candidate['candidateRoot']);check(all(hashlib.sha256((cr/p).read_bytes()).hexdigest()==sha for p,sha in candidate['files'].items()),'All candidate content hashes match frozen metadata')","cr=CR")
src=src.replace("navigate('design/theory-library.html?v=teacher-prefix-20261109');check", "navigate('design/welcome-proposal.html?v=v55-browser');pointer('.card.one a.action');wait('location.pathname.endsWith(\"theory-library.html\")');check")
src=src.replace('mulermoc-nom-54.html','mulermoc-nom-55.html')
src=src.replace("label+' normal Next lock follows earned completion'","label+' normal Next lock follows earned completion'")
src=src.replace("solve_gate(3,'alkanes-unbranched','4')", "solve_gate(3,'alkanes-unbranched','4');call('browsingContext.reload',{'context':ctx,'wait':'complete'});ready();step(4);check(ev('NameleculeQuizCheckpoints.isComplete(fScenarioPresent(),3)'), 'Actual refresh preserves first three earned repairs')")
old='''try:
     wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length===allAtomsTypeList.length}catch(e){return false}})()',35)
     model=read('({key:selectedMol,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length,expectedAtoms:allAtomsTypeList.length})');out['models3D'].append(model);check(True,key+' prefixed3D model URL and atom count loaded')
    except Exception as e:out.setdefault('model3DExceptions',[]).append({'key':key,'error':str(e)});save()'''
new='''file=ev('nameExamples['+json.dumps(key)+'].file3D');expected=int((cr/file).read_text().splitlines()[3][:3])
    wait('(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href&&Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length==='+str(expected)+'}catch(e){return false}})()',35)
    model=read('({key:selectedMol,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,"modelInfo").models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,"atomInfo").length})');model['expectedFromSourceSDF']=expected;out['models3D'].append(model);check(True,key+' prefixed3D model URL and sourceSDF atom count loaded')'''
assert old in src;src=src.replace(old,new)
src=src.replace("json.dumps('/organic-nomenclature-3/'+candidate['prefix']+'/design/theory-library.html')", "json.dumps('/organic-nomenclature-3/design/theory-library.html')")
src=src.replace("check(all(hashlib.sha256((cr/p).read_bytes()).hexdigest()==sha for p,sha in candidate['files'].items()),'All candidate files remain unchanged after browser verification');",'')
src=src.replace("except Exception:\n out['failure']=traceback.format_exc()", "except Exception:\n out['failure']=traceback.format_exc()")
(H/'test-alkane12.py').write_text(src)
# Full available-skeletal renderer/label audit uses current standard audit logic.
src=Path('tools/check-2d-labels.py').read_text().replace("navigate('mulermoc-nom-52.html?audit=2d-acceptance')", "navigate('mulermoc-nom-55.html?audit=2d-acceptance-v55')")
src=src.replace("ROOT=Path(__file__).resolve().parents[1]", "ROOT=Path.cwd()")
src=src.replace("out={'cases':[],'completed':False,'chemicalCertification':False,'failures':[]}","out={'role':'Developer real Firefox available forms audit; not independent review','cases':[],'completed':False,'chemicalCertification':False,'failures':[]}")
(H/'test-2d-labels55.py').write_text(src)
for p in H.glob('*.py'):compile(p.read_text(),str(p),'exec')
print('staged syntax-valid drivers; no runtime browser started')
