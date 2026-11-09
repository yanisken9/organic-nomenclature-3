"""Before/after actual Firefox measurements for the expanded C-H experiment."""
from pathlib import Path
import argparse
import base64
import gzip
import json
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--before',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
# The existing harness supplies json, time, WebSocket/BiDi and browser helpers.
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],
             'existing-firefox-bidi-harness','exec'))
snapshot=json.loads(gzip.decompress(args.before.read_bytes()))
old_code=base64.b64decode(snapshot['sources']['js/jsme-nick-nomeclature-moc2-data_52.js']).decode()
code='var window={};'+old_code+';print(JSON.stringify(window.MOL2D));'
response=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc',
                         '-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',
                        capture_output=True,text=True,check=True)
old={k:v['expanded'] for k,v in json.loads(response.stdout).items() if k in snapshot['keys']}
result={'completed':False,'rows':[]}


measure=r'''(()=>{
 const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
 const labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()&&!(e.id||'').startsWith('number'));
 const overlaps=[];
 for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){
   const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();
   if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([i,labels[i].textContent,j,labels[j].textContent]);
 }
 const map=fGetRenderedAtomTextMap(false,true);
 const point=i=>{const r=map[i].node.getBoundingClientRect();return {x:(r.left+r.right)/2,y:(r.top+r.bottom)/2}};
 const distances={CH:[],CC:[]};
 for(const[a,b]of bondList){const i=a-1,j=b-1;if(!map[i]||!map[j])continue;
   const p=point(i),q=point(j),d=Math.hypot(p.x-q.x,p.y-q.y);
   distances[allAtomsTypeList[i]==='H'||allAtomsTypeList[j]==='H'?'CH':'CC'].push(d);
 }
 return {key:selectedMol,mode:mode2D,name:currentMolName,overlaps,
  visibleC:labels.filter(e=>e.textContent==='C').length,visibleH:labels.filter(e=>e.textContent==='H').length,
  fonts:labels.map(e=>{const m=e.getScreenCTM();return parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)}),
  distances,lines:svg.querySelectorAll('line').length,
  clipped:labels.filter(e=>{const r=e.getBoundingClientRect();return r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1}).map(e=>e.textContent)};
})()'''

try:
    navigate('mulermoc-nom-52.html?v=alkane-ch-half-20261030');app_ready()
    ev('document.fonts.ready.then(()=>true)')
    ev('window.__beforeCH='+json.dumps(old)+';window.__afterCH=Object.fromEntries(Object.keys(__beforeCH).map(k=>[k,nameExamples[k].structure2D_Expanded]));true')
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.2)
        for key in snapshot['keys']:
            for phase in ['before','after']:
                ev('selectedMol='+json.dumps(key)+';nameExamples[selectedMol].structure2D_Expanded=window.__'+phase+'CH[selectedMol];mode2D="expanded";mainChainMode="algorithmic";numberingFlag=false;fInitProps();fLoadMol2D();fShowNameAnalysis();true')
                ev('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true))))')
                row=json.loads(ev('JSON.stringify('+measure+')'));row.update(width=width,phase=phase)
                assert row['visibleH'] == len(row['distances']['CH']) and not row['clipped'],row
                result['rows'].append(row)
                if width==1500 and phase=='after':screenshot(str(args.output/(key+'-expanded.png')))
            ev('nameExamples['+json.dumps(key)+'].structure2D_Expanded=__afterCH['+json.dumps(key)+'];true')
        print('Measured8before/after at width',width,flush=True)
    assert not js_errors,js_errors
    result['completed']=True
finally:
    result['javascriptErrors']=js_errors
    (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':result['completed'],'rows':len(result['rows']),
                      'afterOverlapCases':sum(bool(r['overlaps'])for r in result['rows']if r['phase']=='after'),
                      'errors':len(js_errors)}),flush=True)
