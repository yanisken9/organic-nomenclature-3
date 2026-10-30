"""Actual Firefox before/after label-mask checks; uses existing BiDi9237 harness."""
from pathlib import Path
import argparse
import traceback

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],
             'existing-firefox-bidi-harness','exec'))
result={'completed':False,'comparisons':[],'interactions':[]}


def data(expression):
    return json.loads(ev('JSON.stringify('+expression+')'))


install=r'''(()=>{
 window.__padAfter=fPadExpandedAlkaneBranchLabels;window.__padBefore=()=>{};
 window.__inspectGap=()=>{
  const svg=document.querySelector('#jsmeNomeclatureSVG svg'),outer=svg.getBoundingClientRect();
  const labels=[...svg.querySelectorAll('text')].filter(e=>e.textContent.trim()&&!(e.id||'').startsWith('number'));
  const texts=fGetRenderedAtomTextMap(false,true),rects=fGetRenderedAtomRectMap(false,true),gaps=[];
  const alkaneEdges=mode2D==='expanded'&&nameExamples[selectedMol]?.classification?.seriesKey==='alkanes'?bondList:[];
  for(const[a,b,order]of alkaneEdges){
   if(order!==1||allAtomsTypeList[a-1]!=='C'||allAtomsTypeList[b-1]!=='C')continue;
   const first=texts[a-1],second=texts[b-1];if(!first||!second||Math.abs(+first.attr('x')-+second.attr('x'))>.01)continue;
   for(const[i,j]of[[a-1,b-1],[b-1,a-1]]){
    const label=texts[i].node.getBoundingClientRect(),mask=rects[i].node.getBoundingClientRect(),other=texts[j].node.getBoundingClientRect();
    gaps.push({atom:i+1,other:j+1,pixels:other.top<label.top?label.top-mask.top:mask.bottom-label.bottom});
   }
  }
  const overlaps=[];for(let i=0;i<labels.length;i++)for(let j=0;j<i;j++){
   const a=labels[i].getBoundingClientRect(),b=labels[j].getBoundingClientRect();
   if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)overlaps.push([i,j]);
  }
  return {gaps,overlaps,clipped:labels.filter(e=>{const r=e.getBoundingClientRect();return r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1}).map(e=>e.textContent),
   lines:[...svg.querySelectorAll('line')].map(e=>e.outerHTML),texts:labels.map(e=>e.outerHTML),
   masks:[...svg.querySelectorAll('rect')].map(e=>e.outerHTML),viewBox:svg.getAttribute('viewBox'),svg:svg.outerHTML};
 };
 window.__renderPad=fn=>{fPadExpandedAlkaneBranchLabels=fn;fInitProps();numberingFlag=false;fLoadMol2D();return __inspectGap()};
 return true;
})()'''

try:
    navigate('mulermoc-nom-52.html?v=alkane-label-gap-20261030');app_ready()
    ev('document.fonts.ready.then(()=>true)');ev(install)
    keys=data('Object.keys(window.MOL2D)')
    for start in range(0,len(keys),20):
        batch=keys[start:start+20]
        rows=data('(()=>{const rows=[];for(const key of '+json.dumps(batch)+'){for(const mode of ["condensed","expanded","skeletal"]){if(!MOL2D[key][mode])continue;selectedMol=key;mode2D=mode;const a=__renderPad(__padBefore),b=__renderPad(__padAfter);rows.push({key,mode,name:currentMolName,sameSVG:a.svg===b.svg,sameLines:JSON.stringify(a.lines)===JSON.stringify(b.lines),sameText:JSON.stringify(a.texts)===JSON.stringify(b.texts),sameViewBox:a.viewBox===b.viewBox,sameMasks:JSON.stringify(a.masks)===JSON.stringify(b.masks),beforeGaps:a.gaps,afterGaps:b.gaps,overlapsEqual:JSON.stringify(a.overlaps)===JSON.stringify(b.overlaps),clippedEqual:JSON.stringify(a.clipped)===JSON.stringify(b.clipped)})}}return rows})()')
        for row in rows:
            assert row['sameLines'] and row['sameText'] and row['sameViewBox'] and row['overlapsEqual'] and row['clippedEqual'],row
            target=row['mode']=='expanded' and row['key'] in ['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']
            if target:
                assert not row['sameMasks'] and row['afterGaps'],row
                assert all(.1<g['pixels']<3 for g in row['afterGaps']),row
            else:
                assert row['sameSVG'],row
        result['comparisons'].extend(rows)
        print('Compared molecules',min(start+20,len(keys)),'/',len(keys),flush=True)
    for width in [1500,390]:
        call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1});time.sleep(.2)
        for key in ['methyl_2_pentane','dimethyl_2_3_butane','ethyl_3_dimethyl_2_5_hexane']:
            ev('document.getElementById('+json.dumps(key)+').click();document.querySelectorAll("#radio2DMode .mode2DOption")[1].click();fShowNameAnalysis();true')
            for component in ['comp5','comp1']:
                ev('fClearHighlights();fShowNameAnalysis();document.getElementById('+json.dumps(component)+').click();true')
                until("!numberingFlag||nameAnalysisMode!=='compCarbonsCount'||document.querySelectorAll('#jsmeNomeclatureSVG text[id^=number]').length===numbersSVGElements.length",seconds=15)
                for factor in [1,1.25,1]:
                    ev('molZoom2D=MOL_ZOOM_DEFAULT*'+str(factor)+';fReapplyZoomScale2D();true')
                    row=data('(()=>{const r=__inspectGap();delete r.svg;delete r.lines;delete r.texts;delete r.masks;return r})()');row.update(key=key,width=width,component=component,zoomFactor=factor)
                    assert row['gaps'] and all(.1<g['pixels']<3 for g in row['gaps']) and not row['overlaps'] and not row['clipped'],row
                    result['interactions'].append(row)
            ev('fClearHighlights();fShowNameAnalysis();true')
            if width==1500:
                ev('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true))))')
                screenshot(str(args.output/(key+'-expanded.png')))
    ev("window.__png=null;window.__exportSvg=null;window.__create=URL.createObjectURL;URL.createObjectURL=function(b){if(b.type==='image/png')window.__png=b;if(b.type.startsWith('image/svg'))b.text().then(t=>window.__exportSvg=t);return window.__create.call(URL,b)};HTMLAnchorElement.prototype.click=function(){};document.getElementById('save2DBtn').click();true")
    until('!!window.__png&&!!window.__exportSvg')
    assert ev("window.__png.size>1000&&!new DOMParser().parseFromString(__exportSvg,'image/svg+xml').querySelector('parsererror')")
    result['export']='PNG blob >1000bytes and parseable SVG after mask update'
    assert not js_errors,js_errors
    result['completed']=True
except Exception as error:
    result['failure']=str(error);result['traceback']=traceback.format_exc();print(result['traceback'],flush=True)
finally:
    result['javascriptErrors']=js_errors
    (args.output/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':result['completed'],'comparisons':len(result['comparisons']),'interactions':len(result['interactions']),'errors':len(js_errors)}),flush=True)
if not result['completed']:raise SystemExit(1)
