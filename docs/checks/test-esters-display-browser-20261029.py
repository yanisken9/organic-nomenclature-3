"""Firefox checks for approved ester H/orientation fixes, including actual label positions."""
from pathlib import Path
import argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
keys=['methyl_methanoate','ethanoic_methyl_ester','propanoic_methyl_ester','isopropyl_ethanoate','tert_butyl_methanoate','sec_butyl_ethanoate','butyl_propanoate','isobutyl_2_methylpropanoate','isopropyl_2_3_dimethylbutanoate']
result={'completed':False,'rows':[],'baseline':[],'existingOverlaps':[],'controls':[],'replay':[]}
measure=r'''(()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),visible=e=>getComputedStyle(e).visibility!=='hidden';
 const labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()&&visible(e)&&!(e.id||'').startsWith('number'));
 const ls=jsmeNomeclatureApplet.molFile().split('\n'),pts=ls.slice(4,4+atomsCount).map(l=>[+l.slice(0,10),+l.slice(10,20)]);
 const mean=ids=>ids.reduce((n,i)=>n+pts[i][0],0)/ids.length;
 const carbon=document.getElementById('C'+(esterInfo.carbonylC+1));
 const c=carbon&&[...carbon.children].find(e=>e.textContent==='C'),h=carbon&&carbon.querySelector('.svgHydrogenPart');
 const carbonH=bondList.flatMap(([a,b,o])=>o===1&&((allAtomsTypeList[a-1]==='C'&&allAtomsTypeList[b-1]==='H')||(allAtomsTypeList[b-1]==='C'&&allAtomsTypeList[a-1]==='H'))?[{c:allAtomsTypeList[a-1]==='C'?a-1:b-1,h:allAtomsTypeList[a-1]==='H'?a-1:b-1}]:[]);
 const formyl=carbonH.find(e=>e.c===esterInfo.carbonylC);
 const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([labels[i].textContent,labels[j].textContent]);}
 return {svg:svg.outerHTML,key:selectedMol,mode:mode2D,name:currentMolName,acidLeft:mean(esterInfo.acidFrag)<mean(esterInfo.alcoholFrag),labels:labels.map(e=>e.textContent),
  carbonLabel:carbon?.textContent||null,formylHLeft:h&&c?h.getBoundingClientRect().right<c.getBoundingClientRect().left:null,
  expandedHLeft:formyl?pts[formyl.h][0]<pts[formyl.c][0]&&Math.abs(pts[formyl.h][1]-pts[formyl.c][1])<.0001:null,
  clipped:labels.filter(e=>{const r=e.getBoundingClientRect();return r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1}).map(e=>e.textContent),overlaps,
  lines:svg.querySelectorAll('line').length,expectedLines:bondList.reduce((n,b)=>n+b[2],0),
  hiddenHLines:svg.querySelectorAll('line[data-hidden-carbon-h]').length,explicitCarbonH:carbonH.length,
  visibleStandaloneH:labels.filter(e=>e.textContent==='H').length,viewport:[outer.width,outer.height]};
})()'''
def measured():
 row=json.loads(ev('JSON.stringify('+measure+')'));row['svgSha256']=hashlib.sha256(row.pop('svg').encode()).hexdigest();return row

try:
 call('browsingContext.navigate',{'context':ctx,'url':'http://127.0.0.1:8024/mulermoc-nom-52.html?v=display-baseline','wait':'complete'});app_ready();ev('document.fonts.ready.then(()=>true)')
 baseline={}
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
  for key in keys:
   ev('document.getElementById('+json.dumps(key)+').click();true')
   for index,mode in enumerate(['condensed','expanded','skeletal']):
    ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
    for zoom in [1,2,4]:
     ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
     row=measured();row.update(width=width,zoom=zoom);baseline[(key,mode,width,zoom)]=row;result['baseline'].append(row)
 navigate('mulermoc-nom-52.html?v=ester-display-check');app_ready();ev('document.fonts.ready.then(()=>true)')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
  for key in keys:
   ev('document.getElementById('+json.dumps(key)+').click();true')
   for index,mode in enumerate(['condensed','expanded','skeletal']):
    ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
    for zoom in [1,2,4]:
     ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
     row=measured();row.update(width=width,zoom=zoom)
     assert row['acidLeft'] and not row['clipped'],row
     if row['overlaps']:
      previous=baseline[(key,mode,width,zoom)]
      assert row['overlaps']==previous['overlaps'] and row['svgSha256']==previous['svgSha256'],row
      result['existingOverlaps'].append(row)
     if mode=='skeletal':
      assert row['visibleStandaloneH']==0 and row['hiddenHLines']==row['explicitCarbonH'],row
      assert row['lines']==row['expectedLines'],row
     if key=='methyl_methanoate' and mode=='condensed':assert row['carbonLabel']=='C' and row['visibleStandaloneH']==1,row
     if key=='tert_butyl_methanoate' and mode=='condensed':assert row['carbonLabel']=='HC' and row['formylHLeft'],row
     if key=='tert_butyl_methanoate' and mode=='expanded':assert row['expandedHLeft'],row
     result['rows'].append(row)
     if width==1500 and zoom==2:screenshot(str(args.output/(key+'-'+mode+'.png')))
 # Replay/resize/highlight must not accumulate geometry changes or reveal H.
 for key in ['methyl_methanoate','tert_butyl_methanoate','sec_butyl_ethanoate']:
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[2].click();true')
  # JSME regenerates its header timestamp on export; compare indexed content.
  before=ev("jsmeNomeclatureApplet.molFile().split('\\n').slice(3).join('\\n')")
  for width in [1500,390,1500]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
   ev('fShowNameAnalysis();document.getElementById("comp5").click();fReapplyZoomScale2D();true')
   row=measured();assert row['acidLeft'] and row['visibleStandaloneH']==0,row
   assert ev("jsmeNomeclatureApplet.molFile().split('\\n').slice(3).join('\\n')")==before,key
   result['replay'].append(dict(width=width,**row))
  ev('fClearHighlights();fShowNameAnalysis();true')
 # Shared hydrogen accounting: actual acid/aldehyde condensed controls.
 for key in ['methanoicacid','methanal','ethanal']:
  ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[0].click();molZoom2D=2;fReapplyZoomScale2D();true')
  row=json.loads(ev("JSON.stringify({key:selectedMol,name:currentMolName,labels:[...document.querySelectorAll('#jsmeNomeclatureSVG text')].map(e=>e.textContent),remaining:allAtomsTypeList.map((t,i)=>t==='C'?fRemainingImplicitCarbonHydrogens(i):null)})"));result['controls'].append(row)
  screenshot(str(args.output/(key+'-condensed.png')))
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors;(args.output/'display-browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['rows']),'replay':len(result['replay']),'controls':len(result['controls']),'errors':len(js_errors)}),flush=True)
