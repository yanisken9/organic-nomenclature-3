from pathlib import Path
import json,hashlib,os,ast,xml.etree.ElementTree as ET
os.environ['NAMELECULE_BIDI_PORT']='9244'
exec(compile(Path('tools/namelecule_bidi.py').read_text(),'bidi','exec'))
base=Path('docs/checks/alkane-two-sets-20261104');assets=Path('games/assets/name-repair')
module=ast.parse(Path('tools/export-name-repair-assets.py').read_text());EXPORT=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EXPORT'for t in n.targets))
record={'method':'Main54 live expanded SVG, existing computed styles/full-label framing; no MOL or coordinate edits','sourceFiles':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in ['js/jsme-nick-nomeclature-moc2-data_54.js','js/mulermoc-nom-core-54.js','js/mulermoc-nom-molview-54.js','js/namelecule-label-metrics.js']},'assets':[],'reusedAssets':[{'file':'butane.svg','originalProvenance':'provenance.json','SHA256':hashlib.sha256((assets/'butane.svg').read_bytes()).hexdigest(),'method':'Unchanged reuse of original Main52 export; expanded MOL matches current Main54'}]}
try:
 navigate('mulermoc-nom-54.html?libs=local&export=alkane-two-sets');app_ready();ev('document.fonts.ready.then(()=>true)');ev('fInitNamingProps();true')
 for key,name,labels in [('ethane','αιθάνιο',8),('pentane','πεντάνιο',17)]:
  ev('selectedMol='+json.dumps(key)+';mode2D="expanded";mainChainMode="algorithmic";nameAnalysisMode="none";numberingFlag=false;fInitProps();fClearHighlights();fLoadMol2D();fShowNameAnalysis();true');until('!!document.querySelector("#jsmeNomeclatureSVG svg text[data-namelecule-role=label]")');row=json.loads(ev(EXPORT));assert row['name']==name and row['labels']==labels,row
  svg=row.pop('svg').encode();ET.fromstring(svg);mol=row.pop('sourceMol').encode();filename=key+'.svg';assert not (assets/filename).exists(),filename;(assets/filename).write_bytes(svg);row.update(file=filename,moleculeId=key,SHA256=hashlib.sha256(svg).hexdigest(),expandedMOLSHA256=hashlib.sha256(mol).hexdigest());record['assets'].append(row);screenshot(base/'browser'/('source-'+key+'.png'))
 (assets/'alkane-sets-provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'exported':len(record['assets']),'labels':[r['labels']for r in record['assets']],'names':[r['name']for r in record['assets']]},ensure_ascii=False))
finally:
 (base/'export-browser.json').write_text(json.dumps({'javascriptErrors':js_errors,'record':record},ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
