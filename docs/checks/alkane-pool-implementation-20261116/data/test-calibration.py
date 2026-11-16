from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'browser-support.py').read_text(),'owned-alkane-support','exec'))
try:
 navigate('mulermoc-nom-57.html?v=alkane-data-calibration-before');app_ready();wait('!!nameExamples.methyl_2_butane?.classification');call('browsingContext.activate',{'context':ctx});pause(300)
 out['comparison']=[]
 for key in ['methyl_2_pentane','methyl_2_butane']:
  ev('selectedMol='+json.dumps(key)+';mode2D="expanded";fSelectMol();true');wait('!!document.querySelector("#jsmeNomeclatureSVG svg")');pause(450)
  row=read('''(()=>{const s=document.querySelector('#jsmeNomeclatureSVG svg'),lines=[...s.querySelectorAll('line')],cc=[];for(let i=0;i<bondList.length;i++){const[a,b]=bondList[i];if(allAtomsTypeList[a-1]==='C'&&allAtomsTypeList[b-1]==='C'){const l=lines[svgBondList[i]-1];cc.push(Math.hypot(Number(l.getAttribute('x2'))-Number(l.getAttribute('x1')),Number(l.getAttribute('y2'))-Number(l.getAttribute('y1'))));}}cc.sort((a,b)=>a-b);const fonts=[...s.querySelectorAll('text')].filter(t=>['C','H'].includes(t.textContent.trim())).map(t=>parseFloat(t.getAttribute('font-size')));fonts.sort((a,b)=>a-b);return{id:selectedMol,name:currentMolName,CC:cc[Math.floor(cc.length/2)],font:fonts[Math.floor(fonts.length/2)],ratio:cc[Math.floor(cc.length/2)]/fonts[Math.floor(fonts.length/2)],calibration:s.dataset.alkaneFixedCCScale||null,displayPolicy:nameExamples[selectedMol].displayPolicy||null,bbox:s.getBoundingClientRect().toJSON()}})()''')
  out['comparison'].append(row);shot('before-'+key);print(json.dumps(row,ensure_ascii=False),flush=True)
 check(len(out['comparison'])==2,'old/new actual native Expanded comparison captured')
 out['completed']=True
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish('calibration')
if not out['completed']:raise SystemExit(1)
