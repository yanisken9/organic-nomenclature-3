"""Compare restored ester SVGs to the actual pre-ester viewer at identical sizes/zoom.

Requires isolated Firefox BiDi9237, current app8013, baseline snapshot8024.
All output is under --output. Programmatic menu activation; no physical mobile.
"""
from pathlib import Path
import argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'bidi-harness','exec'))
oldkeys=['ethanoic_methyl_ester','propanoic_methyl_ester','methyl_methanoate','isopropyl_ethanoate']
newkeys=[v['key'] for v in json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())]
result={'completed':False,'rows':[],'baselineComparisons':[]}
try:
 for variant,base,keys in [('baseline','http://127.0.0.1:8024/',oldkeys),('restored','http://127.0.0.1:8013/',oldkeys+newkeys)]:
  call('browsingContext.navigate',{'context':ctx,'url':base+'mulermoc-nom-52.html?v=restore-compare','wait':'complete'});app_ready();ev('document.fonts.ready.then(()=>true)')
  for width in [1500,390]:
   call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
   for key in keys:
    ev('document.getElementById('+json.dumps(key)+').click();true')
    for index,mode in enumerate(['condensed','expanded','skeletal']):
     ev('document.querySelectorAll("#radio2DMode .mode2DOption")['+str(index)+'].click();true')
     for zoom in [1,2]:
      ev('molZoom2D='+str(zoom)+';fReapplyZoomScale2D();true')
      row=json.loads(ev(r'''JSON.stringify((()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect(),labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()),ls=jsmeNomeclatureApplet.molFile().split('\n'),pts=ls.slice(4,4+atomsCount).map(l=>[+l.slice(0,10),+l.slice(10,20)]);return {name:currentMolName,key:selectedMol,mode:mode2D,svg:svg.outerHTML,viewport:[outer.width,outer.height],labels:labels.map(e=>e.textContent),clipped:labels.filter(e=>{const r=e.getBoundingClientRect();return r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1}).map(e=>e.textContent),acidLeft:esterInfo.acidFrag.reduce((n,i)=>n+pts[i][0],0)/esterInfo.acidFrag.length<esterInfo.alcoholFrag.reduce((n,i)=>n+pts[i][0],0)/esterInfo.alcoholFrag.length};})())'''))
      svg=row.pop('svg');row.update(variant=variant,width=width,zoom=zoom,svgSha256=hashlib.sha256(svg.encode()).hexdigest())
      stem=f'{variant}-{key}-{mode}-{width}-z{zoom}';(args.output/(stem+'.svg')).write_text(svg)
      if width==1500 and zoom==1:
       b64=ev(r'''(async()=>{const svg=document.querySelector('#jsmeNomeclatureSVG svg'),b=svg.getBoundingClientRect(),c=document.createElement('canvas');c.width=Math.ceil(b.width*2);c.height=Math.ceil(b.height*2);const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,c.width,c.height);const i=new Image();i.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(svg.outerHTML)));await i.decode();x.drawImage(i,0,0,c.width,c.height);return c.toDataURL('image/png').split(',')[1]})()''')
       (args.output/(stem+'.png')).write_bytes(base64.b64decode(b64))
      result['rows'].append(row)
 baseline={(r['key'],r['mode'],r['width'],r['zoom']):r for r in result['rows'] if r['variant']=='baseline'}
 for row in result['rows']:
  if row['variant']!='restored' or row['key'] not in oldkeys:continue
  previous=baseline[(row['key'],row['mode'],row['width'],row['zoom'])]
  same=row['svgSha256']==previous['svgSha256']
  result['baselineComparisons'].append({k:row[k] for k in ['key','mode','width','zoom']}|{'identicalSVG':same,'sameName':row['name']==previous['name']})
 assert all(r['identicalSVG'] and r['sameName'] for r in result['baselineComparisons']),result['baselineComparisons']
 assert not js_errors,js_errors
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 (args.output/'restore-browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['rows']),'baselineComparisons':len(result['baselineComparisons']),'errors':len(js_errors)}),flush=True)
