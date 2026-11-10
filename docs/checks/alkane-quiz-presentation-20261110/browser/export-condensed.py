"""Export one current Main55 condensed drawing through its existing viewer."""
from pathlib import Path
import os,json,hashlib,ast,traceback,xml.etree.ElementTree as ET
H=Path(__file__).resolve().parent;ROOT=Path.cwd();P=json.loads((H/'process.json').read_text());OUT=ROOT/'games/assets/name-repair/condensed'
os.environ['NAMELECULE_BIDI_PORT']=str(P['bidi_port']);os.environ['NAMELECULE_TEST_BASE_URL']=P['after_url']
exec(compile((ROOT/'tools/namelecule_bidi.py').read_text(),'owned-bidi','exec'))
call('script.addPreloadScript',{'functionDeclaration':'() => { window.MULER_QUIET_FETCH = true; }','contexts':[ctx]})
module=ast.parse((ROOT/'tools/export-name-repair-assets.py').read_text());EXPORT=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EXPORT'for t in n.targets)).replace('structure2D_Expanded','structure2D_Condensed')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=['mulermoc-nom-55.html','js/jsme-nick-nomeclature-moc2-data_55.js','js/mulermoc-nom-core-55.js','js/mulermoc-nom-molview-55.js','js/namelecule-label-metrics.js'];before={p:sha(ROOT/p)for p in paths};record={'date':'2026-11-10','method':'Existing Main55 live condensed viewer SVG; existing computed styles inlined and complete visible bounds framed; no MOL/atom/bond-coordinate edits','sourceFiles':before,'runtimeDependencyUnchangedPaths':paths[1:],'moleculeId':'ethyl_3_dimethyl_2_5_hexane','representation':'condensed','answerHints':False}
try:
 navigate('mulermoc-nom-55.html?libs=local&export=quiz-presentation-20261110');app_ready();ev('document.fonts.ready.then(()=>true)');ev('fInitNamingProps();selectedMol="ethyl_3_dimethyl_2_5_hexane";mode2D="condensed";mainChainMode="algorithmic";nameAnalysisMode="none";numberingFlag=false;fInitProps();fClearHighlights();fLoadMol2D();fShowNameAnalysis();true');until('document.querySelectorAll("#jsmeNomeclatureSVG svg text[data-namelecule-role=label]").length===10')
 row=json.loads(ev(EXPORT));svg=row.pop('svg').encode();mol=row.pop('sourceMol').encode();xml=ET.fromstring(svg);assert row['labels']==10 and row['numbering']==0,row
 assert row['name']=='3-αιθυλο-2,5-διμεθυλοεξάνιο',row['name']
 texts=json.loads(ev('JSON.stringify([...document.querySelectorAll("#jsmeNomeclatureSVG svg text")].map(e=>({text:e.textContent,id:e.id,role:e.getAttribute("data-namelecule-role"),fill:getComputedStyle(e).fill,bounds:e.getBoundingClientRect().toJSON()})))'))
 geometry=json.loads(ev('JSON.stringify({lines:[...document.querySelectorAll("#jsmeNomeclatureSVG svg line")].map(e=>({x1:e.getAttribute("x1"),y1:e.getAttribute("y1"),x2:e.getAttribute("x2"),y2:e.getAttribute("y2"),stroke:getComputedStyle(e).stroke})),atoms:allAtomsTypeList})'))
 assert len(geometry['lines'])==9,len(geometry['lines']);assert all(t['text'].startswith('CH')for t in texts),texts
 OUT.mkdir(parents=True,exist_ok=True);asset=OUT/'ethyl_3_dimethyl_2_5_hexane.svg';assert not asset.exists(),'Refuse overwrite existing target asset';asset.write_bytes(svg)
 record.update(asset=str(asset.relative_to(ROOT)),SHA256=hashlib.sha256(svg).hexdigest(),condensedMOLSHA256=hashlib.sha256(mol).hexdigest(),capture=row,visibleTexts=texts,geometry=geometry)
 record['sourceFilesAtFinish']={p:sha(ROOT/p)for p in paths};assert all(record['sourceFilesAtFinish'][p]==before[p]for p in paths[1:]),'Viewer/core/data/metrics changed'
 (OUT/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');screenshot(H/'source-condensed-Main55.png');print(json.dumps({'asset':record['asset'],'SHA256':record['SHA256'],'labels':row['labels'],'bonds':len(geometry['lines']),'texts':[t['text']for t in texts]},ensure_ascii=False),flush=True)
except Exception:
 (H/'export-failure.txt').write_text(traceback.format_exc());raise
finally:
 (H/'export-browser.json').write_text(json.dumps({'javascriptErrors':js_errors,'events':[e for e in all_events if e.get('method')=='log.entryAdded']},ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{})
