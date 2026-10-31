from pathlib import Path
import os,json,time,hashlib,urllib.request,gzip,traceback
r=Path('/tmp/namelecule-svg-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
out={'cases':[],'dpr2':[],'completed':False}
try:
 for path in ['main/mulermoc-nom-52.html','main/mulermoc-nom-52.html?libs=cdn','prefix/organic-nomenclature-3/mulermoc-nom-52.html']:
  navigate(path);app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)')
  row=json.loads(ev('JSON.stringify({url:location.href,compat:document.compatMode,service:NameleculeLabelMetrics.state.version,jsmol:Jmol._nameleculeLifecycle.version,scripts:[...document.scripts].map(s=>s.src).filter(v=>v.includes("label-metrics")||v.includes("jsme.nocache")),modules:performance.getEntriesByType("resource").filter(r=>r.name.includes("FEB169")).map(r=>r.name)})'))
  assert row['compat']=='CSS1Compat'and row['service']=='20261031-r1'and row['jsmol']=='20261031-v1';assert len(row['modules'])==1
  raw=urllib.request.urlopen(row['modules'][0]).read();row['moduleSHA256']=hashlib.sha256(raw).hexdigest();assert row['moduleSHA256']=='399be5b9c7d3791965430bc88b9e585269aa1aedaac9b94e6a52372f02ee4b01';out['cases'].append(row)
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});app_ready();assert ev('NameleculeLabelMetrics.state.version')=='20261031-r1';out['reload']=True
 navigate('prefix/organic-nomenclature-3/mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library');until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index===1');ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("design/theory-library.html")');out['prefixedExit']=ev('location.pathname')
 navigate('main/mulermoc-nom-52.html?audit=DPR2');app_ready();until('window.JSmolReadyFlag===true');call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':1500,'height':1000},'devicePixelRatio':2});ev((r/'final-svg-probe.js').read_text())
 for key,mode in [('propene','expanded'),('dimethyl_2_3_butane','expanded'),('pentanoic_acid','condensed'),('ethyl_4_isopropyl_3_methyl_2_hexanal','condensed'),('aminobutanoic_acid_3','condensed'),('nitroethane','skeletal')]:
  ev('selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+';fInitProps();fLoadMol2D();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)');assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")');row=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));row['DPR']=ev('devicePixelRatio');assert row['DPR']==2 and not row['clipped']and not row['raster']['inkWithinHalfCssPixelOfBond']and not row['raster']['fullyHiddenLineCount'];out['dpr2'].append(row)
 # Existing user server remains unchanged; read-only bytes must be current.
 try:
  out['user8013HTMLMatches']=urllib.request.urlopen('http://127.0.0.1:8013/mulermoc-nom-52.html',timeout=5).read()==Path('mulermoc-nom-52.html').read_bytes()
 except Exception as e:out['user8013ReadFailure']=str(e)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'loader.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('loader',out['completed'],'cases',len(out['cases']),'DPR2',len(out['dpr2']),'errors',len(js_errors),flush=True)
