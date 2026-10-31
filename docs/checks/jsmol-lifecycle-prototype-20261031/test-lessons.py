"""All 14 current lesson entries, bounded actual navigation and terminal 3D.
This is not a full replay of 337 steps or a conference rehearsal.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,parse_qs
import os,json,gzip,traceback,time
root=Path('/tmp/namelecule-jsmol-lifecycle-prototype-20261031');repo=Path.cwd();here=root
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8029/slow/'
exec(compile((root/'bidi.py').read_text(),'bidi','exec'))
preload=call('script.addPreloadScript',{'functionDeclaration':(root/'observe.js').read_text()})['script']
class Links(HTMLParser):
 def __init__(self):super().__init__();self.lessons=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   q=parse_qs(urlparse(dict(attrs).get('href','')).query)
   if 'scenario'in q:self.lessons.append(q['scenario'][0])
parser=Links();parser.feed((repo/'design/theory-library.html').read_text());lessons=list(dict.fromkeys(parser.lessons));assert len(lessons)==14
out={'lessons':[],'completed':False}
try:
 for version in ['baseline','candidate']:
  for path in lessons:
   row={'version':version,'lesson':path,'steps':[]};before=len(js_errors)
   source=json.loads((repo/path).read_text())['steps'];last=len(source)-1
   navigate('app-'+version+'/mulermoc-nom-52.html?scenario='+path+'&present=1&from=theory-library&audit=collateral')
   until("typeof fScenarioPresent==='function'&&!!fScenarioPresent()&&!document.documentElement.classList.contains('lesson-loading')");app_ready();until('window.JSmolReadyFlag===true')
   for method,index in [('initial',0),('scNext',1),('scPrev',0),('jump',last-1),('scNext',last)]:
    if method=='jump':ev('fScenarioGo('+str(index)+');true')
    elif method!='initial':ev('document.getElementById('+json.dumps(method)+').click();true')
    until('fScenarioPresent().index==='+str(index)+'&&selectedMol==='+json.dumps(source[index]['selectedMol'])+'&&mode2D==='+json.dumps(source[index]['mode2D']))
    row['steps'].append(json.loads(ev('JSON.stringify({index:fScenarioPresent().index,key:selectedMol,mode:mode2D,name:currentMolName,analysisMode:nameAnalysisMode,numberCount:document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length,svg:document.querySelector("#jsmeNomeclatureSVG svg")?.outerHTML||null})')))
   time.sleep(.8)
   row['events']=json.loads(ev('JSON.stringify(__life.rows)'))
   # Inspect terminal actual 3D model through the same documented property API
   # used by the project's prior publication checks. Failures are recorded.
   try:
    until("(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href}catch(e){return false}})()",seconds=10)
    row['terminal3D']=json.loads(ev("JSON.stringify({file:Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0].file,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length})"))
   except Exception as e:row['terminal3D']={'failure':str(e)}
   ev('document.getElementById("scExit").click();true');until('location.pathname.endsWith("design/theory-library.html")');row['exitToLibrary']=True
   row['javascriptErrors']=js_errors[before:];out['lessons'].append(row);print(version,path,'navigation',len(row['steps']),'errors',len(row['javascriptErrors']),'terminal3D',bool(row['terminal3D'].get('file')),flush=True)
  (root/'lessons-progress.json.gz').write_bytes(gzip.compress(json.dumps(out).encode(),mtime=0))
 out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;out['bidiEvents']=all_events;call('script.removePreloadScript',{'script':preload});(root/'lessons.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('lessons completed',out['completed'],'rows',len(out['lessons']),'errors',len(js_errors),flush=True)
