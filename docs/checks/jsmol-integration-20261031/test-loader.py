"""Actual installed loader, SRI and project-subpath smoke; not offline certification."""
from pathlib import Path
import os,json,gzip,traceback,time,hashlib,urllib.request
root=Path('/tmp/namelecule-jsmol-integration-20261031');os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8030/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
out={'cases':[],'completed':False}
try:
 for path in ['main/mulermoc-nom-52.html','main/mulermoc-nom-52.html?libs=cdn','prefix/organic-nomenclature-3/mulermoc-nom-52.html']:
  before=len(js_errors);navigate(path);app_ready();until('window.JSmolReadyFlag===true')
  row=json.loads(ev('JSON.stringify({url:location.href,patch:Jmol._nameleculeLifecycle.version,script:[...document.scripts].filter(s=>s.src.includes("JSmol.min.js")).map(s=>({src:s.src,integrity:s.integrity})),resources:performance.getEntriesByType("resource").filter(r=>r.name.includes("JSmol.min.js")).map(r=>r.name),j2sPath:jmolAppletNomeclature._j2sPath})'))
  assert row['patch']=='20261031-v1',row
  assert len(row['script'])==1 and row['script'][0]['integrity']=='sha384-y4u4hIq8Whzghkk/SjuVpro+EDm44cNe8bcclNCCcWzLmJpnALhyjwGit8tMghR/'
  data=urllib.request.urlopen(row['script'][0]['src']).read();row['assetSHA256']=hashlib.sha256(data).hexdigest();assert row['assetSHA256']=='d99b1168acbbd55d59073943e6fde174513e8b815ddb88ae8f1bfa927961b323'
  assert row['resources']==[row['script'][0]['src']],row
  row['javascriptErrors']=js_errors[before:];out['cases'].append(row);print('loader',path,'passed',flush=True)
 # Reload same prefixed page: versioned bundle remains selected.
 call('browsingContext.reload',{'context':ctx,'wait':'complete'});app_ready();until('window.JSmolReadyFlag===true');assert ev('Jmol._nameleculeLifecycle.version')=='20261031-v1';out['reloadPassed']=True
 navigate('prefix/organic-nomenclature-3/mulermoc-nom-52.html?scenario=scenarios/alkanes-nomenclature-branches.scenario.json&present=1&from=theory-library')
 until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();until('window.JSmolReadyFlag===true')
 ev('document.getElementById("scNext").click();true');until('fScenarioPresent().index===1');ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("design/theory-library.html")');out['prefixedLessonExit']=ev('location.pathname');assert out['prefixedLessonExit']=='/prefix/organic-nomenclature-3/design/theory-library.html'
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'loader.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));call('browsingContext.close',{'context':ctx});call('session.end',{});print('loader completed',out['completed'],'errors',len(js_errors),flush=True)
