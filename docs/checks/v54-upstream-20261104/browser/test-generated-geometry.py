"""Actual browser Edit/Submit/Accept/Update; local stored3D transport fixtures only."""
from pathlib import Path
exec(compile(Path('docs/checks/v54-upstream-20261104/browser/support.py').read_text(),'support','exec'))
def read(s):return json.loads(ev('JSON.stringify('+s+')'))
def submit():
 click('#molDraftSubmitBtn');until('MulerDraft&&MulerDraft.submitted&&!MulerDraft.submitting&&MulerDraft.sdfDone',seconds=40)
def angles():return read('''(()=>{const p=fParseMolV2000(nameExamples[selectedMol].structure2D_Skeletal),rows=[];p.atoms.forEach((a,i)=>{if(!['C','O'].includes(a.el))return;const bs=p.bonds.filter(b=>b[0]===i+1||b[1]===i+1);if(bs.length!==2)return;const ns=bs.map(b=>p.atoms[(b[0]===i+1?b[1]:b[0])-1]),u={x:ns[0].x-a.x,y:ns[0].y-a.y},v={x:ns[1].x-a.x,y:ns[1].y-a.y},sp=a.el==='C'&&(bs.some(b=>b[2]===3)||bs.every(b=>b[2]===2)),angle=Math.acos(Math.max(-1,Math.min(1,(u.x*v.x+u.y*v.y)/(Math.hypot(u.x,u.y)*Math.hypot(v.x,v.y)))))*180/Math.PI;rows.push({atom:i+1,el:a.el,sp,angle,target:sp?180:120})});return rows})()''')
try:
 navigate('mulermoc-nom-54.html?v=final-generator-'+str(time.time_ns()));app_ready();until('!!jsmeEditDraftApplet&&JSmolReadyFlag===true');call('browsingContext.activate',{'context':ctx})
 ev('window.__initialStored=JSON.stringify(MOL2D);true')
 out['fixturePolicy']='Stored local SDF source replaces PubChem3D/name transport. Existing source record is temporarily removed from runtime registry after Submit only, isolating new-accept geometry from duplicate guard; restored after Accept and Update; otherwise the original entry correctly blocks even a custom update as duplicate. Actual JSME/core/registry/renderer/JSmol. Stored MOL registry unchanged.'
 out['cases']=[]
 for mol,ename in [('diethyl_ether','ethoxyethane'),('propadiene','propadiene'),('butyne_1','but-1-yne')]:
  sdf=Path('mols/nomeclature-moc2/'+mol+'_3D.sdf').read_text()
  ev('selectedMol='+json.dumps(mol)+';fSelectMol();true');until('selectedMol==='+json.dumps(mol)+'&&!!document.querySelector("#jsmeNomeclatureSVG svg")')
  if ev('mode2D')!='condensed':click('.mode2DOption:nth-child(1)');until('mode2D==="condensed"')
  ev('window.__fixtureSDF='+json.dumps(sdf)+';fFetchSDF3D_PubChem=async()=>__fixtureSDF;fFetchIUPAC_EN=async()=>({source:"stored-fixture",iupac:'+json.dumps(ename)+',systematic:'+json.dumps(ename)+'});true')
  click('#editMolBtn');until('!!MulerDraft');submit();check(ev('!!MulerDraft.sdf3D'),'Actual3D preview available '+mol)
  ev('window.__fixtureSource=nameExamples['+json.dumps(mol)+'];delete nameExamples['+json.dumps(mol)+'];true');click('#molDraftAcceptBtn');until('!MulerDraft&&selectedMol.startsWith("custom_")',seconds=20)
  first=angles();check(bool(first) and all(abs(r['angle']-r['target'])<.05 for r in first),'Accepted skeletal conventional/sp angles '+mol,first)
  ev('window.__acceptedKey=selectedMol;window.__acceptedRef=nameExamples[selectedMol];true')
  click('.mode2DOption:nth-child(3)');until('mode2D==="skeletal"')
  check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")&&!document.querySelector("#jsmeNomeclatureSVG").getAttribute("data-label-error")'),'Generated skeletal visible '+mol)
  click('#zoomInBtn');click('#zoomOutBtn')
  ev('document.querySelector("#nameAnalysis #comp5").click();true');until('document.querySelectorAll("#jsmeNomeclatureSVG text[id^=number]").length===mainChainAtomsList.length')
  check(True,'Zoom and numbered parent '+mol)
  click('#editMolBtn');until('!!MulerDraft');submit();click('#molDraftAcceptBtn');until('!MulerDraft',seconds=20)
  second=angles();check(ev('selectedMol===__acceptedKey&&nameExamples[selectedMol]===__acceptedRef') and all(abs(r['angle']-r['target'])<.05 for r in second),'Skeletal Update identity and angles '+mol,second)
  for width,height in [(844,390),(1500,1000)]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':height},'devicePixelRatio':1});ev('new Promise(r=>setTimeout(r,180))')
   check(ev('!!document.querySelector("#jsmeNomeclatureSVG svg")'),'Generated skeletal resize '+mol+'/'+str(width))
  ev('nameExamples['+json.dumps(mol)+']=__fixtureSource;true');screenshot_here('generated-'+mol+'.png');out['cases'].append({'molecule':mol,'accepted':first,'updated':second})
 check(ev('JSON.stringify(Object.fromEntries(Object.entries(MOL2D).filter(([k])=>!k.startsWith("custom_"))))===__initialStored'),'All original stored2D records unchanged')
 out['completed']=True
except Exception as e:
 out.update(failure=str(e),traceback=traceback.format_exc());print(out['traceback'],flush=True)
 try:screenshot_here('generated-geometry-failure.png')
 except Exception:pass
finally:
 out['javascriptErrors']=js_errors;(HERE/'generated-geometry-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors),'failure':out.get('failure')}),flush=True)
if not out['completed']or js_errors:raise SystemExit(1)
