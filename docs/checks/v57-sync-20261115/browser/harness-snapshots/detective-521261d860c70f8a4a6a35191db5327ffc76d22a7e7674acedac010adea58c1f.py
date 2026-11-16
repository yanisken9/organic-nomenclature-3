"""One genuine correct answer in the preserved native56 Detective prototype.

Reuses the owned Firefox/loopback lifecycle, never a personal browser/profile.
Selection uses live SVG geometry as a pointer coordinate source; expected ethane
parent-chain atoms [1,2] come from the prior graph oracle, not an injected answer.
"""
from pathlib import Path
import os, textwrap
os.environ.setdefault('NAMELECULE_V57_GAME','detective')
os.environ.setdefault('NAMELECULE_V57_RUN','detective-run1')
driver=Path(__file__).with_name('replay.py').read_text()
prefix,start=driver.split('\ntry:\n server=',1)
exec(compile(prefix,'detective-frozen-replay-helpers','exec'))
OUT['scope']='Preserved Detective prototype, one genuine ethane parent-chain answer using its pinned native56 child; no broad repeat of prior49 answers.'
W='document.querySelector("#molecule-viewer").contentWindow'
S='NameleculeMolecularDetective.snapshot()'
try:
 startup=' server='+start.split(" if GAME=='author':",1)[0]
 exec(compile(textwrap.dedent(startup),'detective-owned-startup','exec'))
 page('games/molecular-detective.html');wait(S+'.phase==="active"',55)
 OUT['before']=read(S)
 check(OUT['before']['moleculeId']=='ethane' and OUT['before']['kind']=='atoms','Detective native56 starts actual ethane atom mission')
 src=read('document.querySelector("#molecule-viewer").src')
 check('molecular-detective-viewer.html?' in src,'Detective uses preserved isolated host',src)
 scripts=read('[...'+W+'.document.scripts].map(e=>e.src).filter(Boolean)')
 check(any('mulermoc-nom-core-56.js' in p for p in scripts) and not any('mulermoc-nom-core-57.js' in p for p in scripts),'Detective child remains pinned to native56',scripts)
 OUT['nativeSnapshot']=read(W+'.NameleculeMolecularDetectiveHost.getSnapshot()')
 check(read(S+'.atoms')==[],'Detective begins with an empty real selection')
 click('#check-answer');wait('!document.querySelector("#feedback").hidden')
 check(not read(S+'.correct'),'Detective genuinely rejects empty attempt')
 OUT['pointerActions']=[]
 for atom in [1,2]:
  ev('document.querySelector("#molecule-viewer").scrollIntoView({block:"center",behavior:"instant"});true');pause(.12)
  point=read('''(()=>{const f=document.querySelector('#molecule-viewer'),w=f.contentWindow,g=w.fMulerSelectGeom(),svg=w.document.querySelector('#jsmeNomeclatureSVG svg'),a=g.anchors.find(a=>a.atom+1===ATOM);if(!a)throw Error('Missing anchor');const p=svg.createSVGPoint();p.x=a.x;p.y=a.y;const s=p.matrixTransform((svg.querySelector('g')||svg).getScreenCTM()),r=f.getBoundingClientRect();return{x:Math.round(r.x+s.x),y:Math.round(r.y+s.y),atom:ATOM}})()'''.replace('ATOM',str(atom)))
  before=read(S+'.selectionRevision')
  call('input.performActions',{'context':ctx,'actions':[{'type':'pointer','id':'v57-detective-pointer','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','x':point['x'],'y':point['y'],'duration':0},{'type':'pointerDown','button':0},{'type':'pointerUp','button':0}]}]})
  wait(S+'.selectionRevision>'+str(before),8);OUT['pointerActions'].append(point)
 check(read(S+'.atoms')==[1,2] and not read(S+'.bonds'),'Detective real native picks select the two expected atoms C')
 click('#check-answer');wait('!document.querySelector("#feedback").hidden&&'+S+'.correct')
 check(read(S+'.correct') and not read('document.getElementById("next-mission").hidden'),'Detective production Check accepts genuine parent-chain answer')
 OUT['after']=read(S);OUT['rounds'].append({'label':'Detective preserved native56 ethane parent-chain','moleculeId':'ethane','practice':True,'state':OUT['after']});shot('detective-native56-correct')
 click('#clear-selection');wait(S+'.atoms.length===0')
 check(not read(S+'.correct'),'Detective clear removes the actual answer and success')
 OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:OUT['failureState']=read('typeof NameleculeMolecularDetective!=="undefined"?'+S+':({url:location.href,body:document.body.innerText.slice(-5000)})');shot('failure')
 except Exception as error:OUT['failureCaptureError']=repr(error)
finally:
 cleanup=driver.rsplit("\nfinally:\n OUT['javascriptErrors']",1)[1].split("\nif not OUT.get('completed')",1)[0]
 exec(compile(textwrap.dedent(" OUT['javascriptErrors']"+cleanup),'detective-owned-cleanup','exec'))
if not OUT.get('completed'):raise SystemExit(1)
