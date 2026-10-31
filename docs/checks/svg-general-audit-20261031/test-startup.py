"""Three paired fresh-page starts with warm local HTTP cache, not cold-machine benchmark."""
from pathlib import Path
import os,json,traceback
here=Path(__file__).resolve().parent;repo=here.parents[2];root=Path('/tmp/namelecule-svg-general-audit-20261031')
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8026/'
exec(compile((repo/'docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi','exec'))
out={'runs':[],'completed':False}
preload=call('script.addPreloadScript',{'functionDeclaration':'''()=>{if(window.top!==window)return;window.__auditReady={};let timer=setInterval(()=>{try{if(!window.__auditReady.twoD&&typeof jsmeNomeclatureApplet!=='undefined'&&!!jsmeNomeclatureApplet&&typeof nameExamples!=='undefined'&&!!nameExamples.methyl_3_butene_1?.classification&&document.querySelector('#jsmeNomeclatureSVG svg text'))window.__auditReady.twoD=performance.now();if(!window.__auditReady.threeD&&window.JSmolReadyFlag===true)window.__auditReady.threeD=performance.now();if(window.__auditReady.twoD&&window.__auditReady.threeD)clearInterval(timer)}catch(e){}},10)}'''})['script']
try:
 for i in range(3):
  for version in (['baseline','candidate']if i%2==0 else['candidate','baseline']):
   navigate('app-'+version+'/mulermoc-nom-52.html?audit=startup-'+str(i));until('!!window.__auditReady?.twoD&&!!window.__auditReady?.threeD')
   row=json.loads(ev('JSON.stringify(window.__auditReady)'));row.update(version=version,round=i);out['runs'].append(row);print(row,flush=True)
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(root/'startup.json').write_text(json.dumps(out,indent=2)+'\n');call('script.removePreloadScript',{'script':preload});call('browsingContext.close',{'context':ctx});call('session.end',{})
