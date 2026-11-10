"""Exercise new EN school/systematic assembly and stable component boxes.
Compare actual candidate and upstream55; current54 test elsewhere covers legacy.
"""
from pathlib import Path
import argparse,ast,hashlib,json,subprocess,datetime
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;C=Path(argparse.ArgumentParser().parse_known_args()[1][0]);J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
tree=ast.parse((P/'docs/checks/v54-sync-20261104/core/test-core54.py').read_text());const={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['PREFIX','TAIL']}
tail=const['TAIL'].replace('const answer=state();',r'''const answer=state();
if(task==='variants'){
 const variants=[];for(const variant of ['', 'sys']){
  const en=fPopulateEngineENFromGreek(key,variant),boxes=fNameENBoxes(variant);
  const joined=boxes&&boxes.boxes.map(([id,text])=>text+(boxes.spaceAfter===id?' ':'')).join('');
  variants.push({variant:variant||'school',en,boxes,joined,matches:en===joined});
 }
 return {key,mode,cm,gr:currentMolName,common:currentMolCommonName,commonEN:fMulerENCommonLabel(currentMolCommonName),variants};
}
''')
src=''
for name,folder in [('candidate',C),('upstream',P/'docs/checks/v54-merge-20261109/upstream/target')]:
 files=[C/'js/jsme-nick-nomeclature-moc2-data_54.js']+[folder/f'js/mulermoc-nom-{k}-55.js'for k in ['core','name-en','iupac']]
 src+='var '+name+'=new Function("task","key","mode","cm","extra",'+json.dumps(const['PREFIX']+'\n'.join(p.read_text()for p in files)+'\n'+tail)+');'
src+=r'''
const rows=[],differences=[],mismatches=[];
for(const row of candidate('inventory'))for(const mode of row.modes)for(const cm of ['algorithmic','data']){
 const a=candidate('variants',row.key,mode,cm),b=upstream('variants',row.key,mode,cm);rows.push(a);
 if(JSON.stringify(a)!==JSON.stringify(b))differences.push({key:row.key,mode,cm,candidate:a,upstream:b});
 for(const v of a.variants)if(!v.matches)mismatches.push({key:row.key,mode,cm,...v});
}
print(JSON.stringify({rows,differences,mismatches}));
'''
r=subprocess.run([J,'-e','eval(JSON.parse(readline()))'],input=json.dumps(src)+'\n',text=True,capture_output=True);assert r.returncode==0,(r.stdout[-2000:],r.stderr[-1000:]);out=json.loads(r.stdout)
out['summary']={'cases':len(out['rows']),'variantAssemblies':2*len(out['rows']),'differences':len(out['differences']),'mismatches':len(out['mismatches']),'keysWithMismatches':sorted({r['key']for r in out['mismatches']})}
out['timestampUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
out['sourceSHA256']={str(C/f'js/mulermoc-nom-{k}-55.js'):hashlib.sha256((C/f'js/mulermoc-nom-{k}-55.js').read_bytes()).hexdigest()for k in ['core','name-en','iupac']}
expected={'methyl_4_penten_4_yn_2_ol_1','ethyl_3_methyl_4_hexen_3_yn_5_ol_2','penten_1_yn_4_one_3','dimethyl_4_5_hexen_5_yn_1_one_3','methyl_6_hepten_3_dione_2_5','ethyl_3_methyl_4_octen_3_yn_5_dione_2_7','isopropyl_4_dimethyl_3_6_octen_3_yn_7_dione_2_5'}
assert {r['key']for r in out['differences']}==expected and len(out['differences'])==42
assert all([v['en']for v in r['candidate']['variants']]==[v['en']for v in r['upstream']['variants']]for r in out['differences'])
out['summary']['differenceReason']='Preserved local separator and terminal-e box fusion fixes on seven molecules; names identical to upstream55.'
(H/'en-variants-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['summary'],ensure_ascii=False));assert not out['mismatches'],out['mismatches'][:2]
