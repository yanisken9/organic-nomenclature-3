"""Main-only 2D readability: actual SVG geometry, controls, export and lesson zoom.
Reuses the existing Firefox BiDi harness. Writes artifacts only under /tmp.
"""
from pathlib import Path
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0], 'existing-firefox-bidi-harness', 'exec'))
import hashlib
folder=Path('/tmp/namelecule-main-2d-scale-20261027');folder.mkdir(exist_ok=True)
result={'completed':False,'cases':[],'checks':[],'lessons':[]}
def geometry():
 return json.loads(ev("""JSON.stringify((()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),o=s.getBoundingClientRect(),labels=[...s.querySelectorAll('text:not([id^=number])')];return {key:selectedMol,mode:mode2D,zoom:molZoom2D,target:Number(s.dataset.uniformAtomFontPixels),viewport:[o.width,o.height],fonts:labels.filter(e=>/[CHO]/.test(e.textContent)).map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)}),clipped:[...s.querySelectorAll('line,text,path')].filter(e=>!e.closest('defs')).filter(e=>{const b=e.getBoundingClientRect();return b.left<o.left-1||b.right>o.right+1||b.top<o.top-1||b.bottom>o.bottom+1}).map(e=>e.textContent||e.tagName)}})())"""))
def drain_numbering():
 ev('clearInterval(myNumberingTimeout);currNumberEl=0;true')
result={'completed':False,'lessons':[],'cases':[]}
try:
 navigate('design/theory-library.html?v=readable-2d-lesson-check')
 links=json.loads(ev("JSON.stringify([...document.querySelectorAll('a[href*=scenario]')].map(a=>a.getAttribute('href')))"));assert len(links)==12
 for link in links:
  ev('document.querySelector('+json.dumps('a[href='+json.dumps(link)+']')+').click()')
  until("typeof fScenarioPresent==='function' && !!fScenarioPresent() && !document.documentElement.classList.contains('lesson-loading')")
  app_ready();assert ev("document.documentElement.getAttribute('data-namelecule-2d-font-size')==='22'")
  data=json.loads(ev('JSON.stringify({title:fScenarioPresent().title,steps:fScenarioPresent().steps})'))
  for index in [0,len(data['steps'])-1]:
   step=data['steps'][index];ev('fScenarioGo('+str(index)+')')
   until('fScenarioPresent().index==='+str(index)+' && selectedMol==='+json.dumps(step['selectedMol']))
   assert ev('molZoom2D')==step.get('style2D',{}).get('zoom',2)
   assert ev('mode2D')==step['mode2D']
   visible=ev("!!document.querySelector('#jsmeNomeclatureSVG svg') && document.getElementById('jsmeNomeclatureSVG').offsetParent!==null")
   row={'lesson':data['title'],'step':index+1,'molecule':step['selectedMol'],'visible2D':visible,'zoom':ev('molZoom2D')}
   if visible:
    g=geometry();assert not g['clipped'],row
    if g['fonts']:assert all(0<f<=22*g['zoom']+.02 for f in g['fonts']),g
    row['geometry']=g
   result['cases'].append(row)
  if len(result['lessons'])==0:
   screenshot('/tmp/namelecule-readable-2d-20261028/alkanes-lesson-final.png')
  result['lessons'].append(data['title']);print('PASS',data['title'],flush=True)
  ev("document.getElementById('scExit').click()")
  until("location.pathname.endsWith('/design/theory-library.html')")
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 known={e['text'] for e in json.loads(Path('docs/checks/main-2d-scale-existing-jsmol-20261027.json').read_text())['javascriptErrors']}
 result['unexpectedJavascriptErrors']=[e for e in js_errors if e.get('text') not in known or not any('chemapps.stolaf.edu/jmol/jsmol/' in f.get('url','') for f in e.get('stackTrace',{}).get('callFrames',[]))]
 Path('/tmp/readable-2d-lessons-20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'lessons':len(result['lessons']),'cases':len(result['cases']),'errors':len(js_errors),'unexpected':len(result['unexpectedJavascriptErrors'])}),flush=True)
 assert not result['unexpectedJavascriptErrors']
