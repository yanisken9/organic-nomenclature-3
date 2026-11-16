"""Bounded direct native generated-host calibration check (not game handshake)."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'browser-support.py').read_text(),'owned-host-calibration-support','exec'))
keys=['methyl_2_pentane','ethyl_3_dimethyl_2_5_hexane','methyl_2_butane','dimethyl_2_2_propane','ethyl_3_methyl_2_pentane'];out['hosts']=[]
try:
 call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
 for file,version,dataset_key in [('games/name-builder-viewer.html','55','nameBuilder'),('games/molecular-detective-viewer.html','56','molecularDetective')]:
  navigate(file+'?audit=alkane-pool-native-host');app_ready();ev('document.documentElement.dataset.'+dataset_key+'Visible="true";document.documentElement.dataset.'+dataset_key+'Representation="2d";fResizeViewers();true');pause(300)
  check(read('Object.keys(nameExamples).length')==147,version+' generatedhost merges all147records')
  expected=hashlib.sha256((ROOT/f'js/mulermoc-nom-molview-{version}.js').read_bytes()).hexdigest();resources=read('performance.getEntriesByType("resource").map(r=>r.name).filter(s=>s.includes("mulermoc-nom-molview-"))');check(any(expected in u for u in resources),version+' actualhost loads fingerprinted approvednativeviewer',resources)
  host={'file':file,'nativeVersion':version,'resources':resources,'cases':[]}
  for key in keys:
   ev('selectedMol='+json.dumps(key)+';mode2D="expanded";fSelectMol();true');pause(300)
   row=read('''(()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),lines=[...s.querySelectorAll('line')],cc=[];for(let i=0;i<bondList.length;i++){const[a,b]=bondList[i];if(allAtomsTypeList[a-1]==='C'&&allAtomsTypeList[b-1]==='C'){const l=lines[svgBondList[i]-1];cc.push(Math.hypot(Number(l.getAttribute('x2'))-Number(l.getAttribute('x1')),Number(l.getAttribute('y2'))-Number(l.getAttribute('y1'))));}}cc.sort((a,b)=>a-b);const fonts=[...s.querySelectorAll('text[data-namelecule-role="label"]')].filter(t=>['C','H'].includes(t.textContent.trim())).map(t=>parseFloat(t.getAttribute('font-size'))).sort((a,b)=>a-b);return{id:selectedMol,name:currentMolName,ratio:cc[Math.floor(cc.length/2)]/fonts[Math.floor(fonts.length/2)],calibration:s.dataset.alkaneFixedCCScale||null,sourcePack:nameExamples[selectedMol].sourcePack||null}})()''');row['frame']=framing();host['cases'].append(row)
   check(bool(row['calibration'])and abs(row['ratio']-2.6175)<.0001,version+' '+key+' sharedExpanded calibration matches old8',row);check(row['frame']['inside'],version+' '+key+' complete labels/structure fit nativehost')
  shot('host-'+version+'-expanded');out['hosts'].append(host)
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish('host-calibration')
if not out['completed']or js_errors:raise SystemExit(1)
