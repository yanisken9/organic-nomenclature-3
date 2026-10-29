"""Raster measurement of actual JSME output, before/after MOL harmonization.

Measures the upper oxygen glyph against nearby black bond pixels, in CSS pixels.
It is a depiction comparison, not a physical bond-length or chemistry test.
"""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--before-embedded',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-harness','exec'))
specs=json.loads(Path('docs/checks/esters-specs-20261029.json').read_text())
newkeys=[v['key'] for v in specs]
oldkeys=['ethanoic_methyl_ester','propanoic_methyl_ester','methyl_methanoate','isopropyl_ethanoate']
measure=r'''(async()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
 const oxygens=[...svg.querySelectorAll('text')].filter(t=>t.textContent==='O');
 const oxygen=oxygens.sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top)[0];
 const box=oxygen.getBoundingClientRect(),scale=4;
 const canvas=document.createElement('canvas');canvas.width=Math.ceil(outer.width*scale);canvas.height=Math.ceil(outer.height*scale);
 const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);
 const img=new Image();img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(new XMLSerializer().serializeToString(svg))));await img.decode();
 ctx.drawImage(img,0,0,canvas.width,canvas.height);
 const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data,red=[],black=[];
 const x0=Math.max(0,Math.floor((box.left-outer.left-8)*scale)),x1=Math.min(canvas.width,Math.ceil((box.right-outer.left+8)*scale));
 const y0=Math.max(0,Math.floor((box.top-outer.top-8)*scale)),y1=Math.min(canvas.height,Math.ceil((box.bottom-outer.top+8)*scale));
 for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){const i=4*(y*canvas.width+x),r=pixels[i],g=pixels[i+1],b=pixels[i+2];if(r>150&&g<100&&b<100)red.push([x,y]);else if(r<80&&g<80&&b<80)black.push([x,y]);}
 if(!red.length||!black.length)throw Error('No oxygen/bond pixels in region');
 let d2=Infinity;for(const a of red)for(const b of black)d2=Math.min(d2,(a[0]-b[0])**2+(a[1]-b[1])**2);
 return {key:selectedMol,mode:mode2D,gapPixels:Math.sqrt(d2)/scale,redPixels:red.length,blackPixels:black.length,viewport:[outer.width,outer.height]};
})()'''
result={'completed':False,'rows':[]}
try:
 navigate('mulermoc-nom-52.html?v=carbonyl-final');app_ready();ev('document.fonts.ready.then(()=>true)')
 ev('window.__finalMOL=structuredClone(window.MOL2D);window.__beforeMOL='+args.before_embedded.read_text()+';true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.3)
  for variant,keys in [('reference',oldkeys),('before',newkeys),('after',newkeys)]:
   for key in keys:
    for mode in ['condensed','expanded','skeletal']:
     ev('window.MOL2D='+('__beforeMOL' if variant=='before' else '__finalMOL')+';selectedMol='+json.dumps(key)+';mode2D='+json.dumps(mode)+";for(const m of ['Condensed','Expanded','Skeletal'])nameExamples[selectedMol]['structure2D_'+m]=window.MOL2D[selectedMol][m.toLowerCase()];mainChainMode='algorithmic';nameAnalysisMode='none';numberingFlag=false;fInitProps();fLoadMol2D();true")
     row=json.loads(ev(measure+'.then(value=>JSON.stringify(value))'))
     result['rows'].append(dict(width=width,variant=variant,**row))
     if variant=='after':
      assert row['gapPixels']>=1.0,(width,row)
    if width==1500 and variant=='after':screenshot(str(args.output/(key+'-skeletal.png')))
 result['completed']=True
finally:
 result['javascriptErrors']=js_errors
 (args.output/'carbonyl.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 call('browsingContext.close',{'context':ctx});call('session.end',{})
 print(json.dumps({'completed':result['completed'],'cases':len(result['rows']),'errors':len(js_errors)}),flush=True)
