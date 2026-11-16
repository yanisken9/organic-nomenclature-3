"""Actual naming functions: all raw-supported library forms and EN assemblies.
No browser, actual JSME, external oracle or source-label coercion.
"""
from pathlib import Path
import ast,hashlib,json,subprocess,datetime
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;C=Path('/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate');J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
tree=ast.parse((P/'docs/checks/v54-sync-20261104/core/test-core54.py').read_text());const={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
tail=const['TAIL'].replace('const answer=state();',r'''const answer=state();
if(task==='variants'){
 const variants=[];for(const variant of ['', 'sys']){
  const en=fPopulateEngineENFromGreek(key,variant),boxes=fNameENBoxes(variant);
  const joined=boxes&&boxes.boxes.map(([id,text])=>text+(boxes.spaceAfter===id?' ':'')).join('');
  const ids=boxes&&boxes.boxes.map(([id])=>id);
  variants.push({variant:variant||'school',en,boxes,joined,matches:en===joined,uniqueIDs:ids&&new Set(ids).size===ids.length});
 }
 return {key,mode,cm,gr:currentMolName,common:currentMolCommonName,variants};
}
''')
src=''
for name,folder,ver in [('candidate',C,57),('local56',P,56),('raw56',P/'docs/checks/v56-sync-20261115/upstream/target',56)]:
 files=[C/'js/jsme-nick-nomeclature-moc2-data_57.js']+[folder/f'js/mulermoc-nom-{k}-{ver}.js'for k in ['core','name-en','iupac']]
 src+='var '+name+'=new Function("task","key","mode","cm","extra",'+json.dumps(const['PREFIX']+'\n'.join(p.read_text()for p in files)+'\n'+tail)+');'
src+=r'''
const rows=[],differences=[],mismatches=[],rawExcluded=[];
for(const row of candidate('inventory'))for(const mode of row.modes)for(const cm of ['algorithmic','data']){
 if(row.key==='penten_3_yne_1'&&mode==='expanded'){
  let reason=null;try{candidate('variants',row.key,mode,cm)}catch(e){reason=String(e)}
  if(!reason||!reason.includes('unsupported element [H]'))throw Error('literal [H] exclusion lost');
  rawExcluded.push({key:row.key,mode,cm,reason});continue;
 }
 const a=candidate('variants',row.key,mode,cm),b=local56('variants',row.key,mode,cm);rows.push(a);
 if(JSON.stringify(a)!==JSON.stringify(b))differences.push({key:row.key,mode,cm,candidate:a,local56:b});
 for(const v of a.variants)if(!v.matches||!v.uniqueIDs)mismatches.push({key:row.key,mode,cm,...v});
}
const eFusion=[['yn','-2,7-dione','yne'],['en','2,5-diol','ene'],['yn','-1-ol','yn'],['en','-2-one','en'],['yn','dioic acid','yne']];
print(JSON.stringify({rows,differences,mismatches,rawExcluded}));
'''
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout[-4000:],r.stderr[-1000:]);out=json.loads(r.stdout)
out['summary']={'molecules':len({x['key']for x in out['rows']}),'rawSupportedForms':len(out['rows'])//2,'cases':len(out['rows']),'variantAssemblies':2*len(out['rows']),'differences':len(out['differences']),'keysChanged':sorted({r['key']for r in out['differences']}),'mismatches':len(out['mismatches']),'rawExcluded':out['rawExcluded']}
out['sourceSHA256']={str(C/f'js/mulermoc-nom-{k}-57.js'):hashlib.sha256((C/f'js/mulermoc-nom-{k}-57.js').read_bytes()).hexdigest()for k in ['core','name-en','iupac']}
out['timestampUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(D/'en-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['summary'],ensure_ascii=False));assert not out['mismatches'],out['mismatches'][:2]
