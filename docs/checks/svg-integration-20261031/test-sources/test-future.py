from pathlib import Path
import os,json,gzip,math,traceback
r=Path('/tmp/namelecule-svg-integration-20261031');repo=Path.cwd();os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8031/'
exec(compile((r/'bidi.py').read_text(),'bidi','exec'))
original=json.loads((repo/'docs/checks/svg-text-root-20261031/propene.json').read_text())['annotated'];fixtures=[]
for factor in [1,.375,.1]:
 for angle in [0,45,90]:
  lines=original.split('\n');n=int(lines[3][:3]);nb=int(lines[3][3:6]);xy=[list(map(float,s[:30].split()))for s in lines[4:4+n]]
  for line in lines[4+n:4+n+nb]:
   i,j=int(line[:3])-1,int(line[3:6])-1
   if lines[4+i][31:34].strip()=='H':i,j=j,i
   if lines[4+j][31:34].strip()=='H':xy[j]=[xy[i][d]+(xy[j][d]-xy[i][d])*factor for d in range(3)]
  a=math.radians(angle)
  for i,(x,y,z)in enumerate(xy):
   coords=[x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z];lines[4+i]=''.join(f'{v:10.4f}'for v in coords)+lines[4+i][30:]
  fixtures.append({'factor':factor,'angle':angle,'mol':'\n'.join(lines)})
out={'cases':[],'completed':False}
try:
 navigate('main/mulermoc-nom-52.html?audit=future-inputs');app_ready();until('window.JSmolReadyFlag===true');ev('document.fonts.ready.then(()=>true)');ev((r/'final-svg-probe.js').read_text());ev('window.__originalPropene=nameExamples.propene.structure2D_Expanded;true')
 for width in [1500,390]:
  call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':1000},'devicePixelRatio':1})
  for f in fixtures:
   ev('selectedMol="propene";mode2D="expanded";nameExamples.propene.structure2D_Expanded='+json.dumps(f['mol'])+';fInitProps();fLoadMol2D();new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))).then(()=>true)')
   row={k:v for k,v in f.items()if k!='mol'};row['width']=width;row['accepted']=ev('!!document.querySelector("#jsmeNomeclatureSVG svg")')
   if row['accepted']:
    row['drawing']=json.loads(ev('auditFinalSvg().then(v=>JSON.stringify(v))'));assert not row['drawing']['raster']['inkWithinHalfCssPixelOfBond'] and not row['drawing']['raster']['fullyHiddenLineCount'] and not row['drawing']['clipped']
   else:row['status']=ev('document.querySelector("#jsmeNomeclatureSVG [role=status]")?.textContent');assert row['status']
   if f['factor']==.1:assert not row['accepted'],'Crowded input should be refused'
   if f['factor']==1:assert row['accepted'],'Normal input should remain visible'
   out['cases'].append(row);print('future',width,f['factor'],f['angle'],'accepted',row['accepted'],flush=True)
 ev('nameExamples.propene.structure2D_Expanded=__originalPropene;fInitProps();fLoadMol2D();true');assert ev('!!document.querySelector("#jsmeNomeclatureSVG svg")');out['restored']=True;out['completed']=True
except Exception as e:out['failure']=str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
finally:
 out['javascriptErrors']=js_errors;(r/'future.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False).encode(),mtime=0));call('browsingContext.close',{'context':ctx});call('session.end',{});print('future',out['completed'],'rows',len(out['cases']),'errors',len(js_errors),flush=True)
