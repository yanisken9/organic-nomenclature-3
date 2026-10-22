from pathlib import Path
import json,subprocess
jsc='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
roots={'v48':Path.cwd(),'v49':Path.cwd()};results={}
for label,root in roots.items():
 version=label[1:];data=(root/('js/jsme-nick-nomeclature-moc2-data_'+version+'.js')).read_text();core=(root/('js/mulermoc-nom-core-'+version+'.js')).read_text()
 body='''var window={},console={log:function(){},warn:function(){},error:function(){}};
 var selectedMol=key,mode2D=mode,mainChainMode=chainMode,etherNamingMode='iupac';
 '''+data+'\nvar MOL2D=window.MOL2D;\n'+core+'''
 const mol=MOL2D[key][mode];if(!mol)return {unavailable:true};
 const ls=mol.split('\\n'),na=Number(ls[3].slice(0,3)),nb=Number(ls[3].slice(3,6));
 const aa=ls.slice(4,4+na).map(x=>({label:x.slice(31,34).trim()}));
 const bb=ls.slice(4+na,4+na+nb).map(x=>({atoms:[Number(x.slice(0,3)),Number(x.slice(3,6))],order:Number(x.slice(6,9))}));
 var jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1]};
 fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
 return {name:nameComponentsList.filter(Boolean).join(''),parts:nameComponentsList,chain:mainChainAtomsList,classification:fGetMoleculeClassification()};
 '''
 outer='var window=this;'+data+'\nvar run=new Function("key","mode","chainMode",'+json.dumps(body)+');var out=[];'
 outer+='''for(var key of Object.keys(nameExamples))for(var mode of ['condensed','expanded','skeletal'])for(var chainMode of ['algorithmic','data']){try{out.push({key,mode,chainMode,result:run(key,mode,chainMode)});}catch(e){out.push({key,mode,chainMode,error:String(e)});}}print(JSON.stringify(out));'''
 p=Path('/tmp/check-names-'+label+'-20261022.js');p.write_text(outer);r=subprocess.run([jsc,str(p)],capture_output=True,text=True);assert r.returncode==0,r.stdout[:500];results[label]=json.loads(r.stdout)
 a=results[label];print(label,'cases',len(a),'unavailable',sum(x.get('result',{}).get('unavailable',False) for x in a),'errors',[x for x in a if 'error' in x],flush=True)
a,b=results.values();diffs=[(x,y) for x,y in zip(a,b) if x!=y];assert len(a)==len(b)==438
print('Differences:',json.dumps(diffs,ensure_ascii=False)[:2000]);assert not diffs
Path('/tmp/v49-naming-results-20261022.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
