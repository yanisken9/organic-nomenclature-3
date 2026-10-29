"""Real Firefox/JSME expanded bond directions and label clearance, two widths/three zooms."""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
specs=json.loads(Path('docs/checks/esters-specs-20261029.json').read_text());result={'completed':False,'rows':[],'replay':[]}
measure=r'''(()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
 const labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()&&getComputedStyle(e).visibility!=='hidden'&&!(e.id||'').startsWith('number'));
 const lines=[...svg.querySelectorAll('line')].filter(e=>getComputedStyle(e).visibility!=='hidden');
 const bad=lines.filter(e=>{const dx=+e.getAttribute('x2')-e.getAttribute('x1'),dy=+e.getAttribute('y2')-e.getAttribute('y1');return Math.abs(dx)>.01&&Math.abs(dy)>.01});
 const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([labels[i].textContent,labels[j].textContent]);}
 const ls=jsmeNomeclatureApplet.molFile().split('\n'),pts=ls.slice(4,4+atomsCount).map(l=>[+l.slice(0,10),+l.slice(10,20)]),mean=ids=>ids.reduce((n,i)=>n+pts[i][0],0)/ids.length;
 return {key:selectedMol,mode:mode2D,name:currentMolName,acidLeft:mean(esterInfo.acidFrag)<mean(esterInfo.alcoholFrag),diagonalLines:bad.length,visibleLines:lines.length,
  visibleH:labels.filter(e=>e.textContent==='H').length,overlaps,formylLeft:selectedMol==='tert_butyl_methanoate'?pts[7][0]<pts[0][0]&&pts[7][1]===pts[0][1]:null,
  clipped:labels.filter(e=>{const b=e.getBoundingClientRect();return b.left<outer.left-1||b.right>outer.right+1||b.top<outer.top-1||b.bottom>outer.bottom+1}).map(e=>e.textContent),viewport:[outer.width,outer.height]};
})()'''
try:
 navigate('mulermoc-nom-52.html?v=orthogonal-ester-mol');app_ready();ev('document.fonts.ready.then(()=>true)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
  for spec in specs:
   ev('document.getElementById('+json.dumps(spec['key'])+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();true')
   for zoom in [1,2,4]:
    ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
    row=json.loads(ev('JSON.stringify('+measure+')'));row.update(width=width,zoom=zoom)
    assert row['name']==spec['name']and row['acidLeft']and row['diagonalLines']==0 and not row['overlaps']and not row['clipped'],row
    assert row['visibleH']==2*spec['carbons'],row
    if spec['key']=='tert_butyl_methanoate':assert row['formylLeft'],row
    result['rows'].append(row)
    if width==1500 and zoom==2:
     # Full-page capture avoids viewport clip-coordinate ambiguity.
     time.sleep(.25)
     screenshot(str(args.output/(spec['key']+'-expanded.png')))
 # Repeated highlight/resize and switching back to expanded retain orthogonality.
 for spec in specs:
  ev('document.getElementById('+json.dumps(spec['key'])+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();molZoom2D=2;fReapplyZoomScale2D();true')
  before=ev("jsmeNomeclatureApplet.molFile().split('\\n').slice(3).join('\\n')")
  ev('fShowNameAnalysis();document.getElementById("comp5").click();fReapplyZoomScale2D();true')
  row=json.loads(ev('JSON.stringify('+measure+')'));assert not row['diagonalLines']and not row['overlaps']and row['acidLeft'],row
  assert before==ev("jsmeNomeclatureApplet.molFile().split('\\n').slice(3).join('\\n')"),spec['key']
  result['replay'].append(row);ev('fClearHighlights();fShowNameAnalysis();true')
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(args.output/'orthogonal-browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['rows']),'replay':len(result['replay']),'errors':len(js_errors)}),flush=True)
