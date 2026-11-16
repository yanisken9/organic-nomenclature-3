"""Measure visible bond intervals independently of native picking before claiming a cause."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned56-visible-bond-support','exec'))
try:
    navigate('mulermoc-nom-56.html?lang=en&mol=ethane&v=visible-bond-'+str(time.time_ns()));app_ready();wait('window.JSmolReadyFlag===true',60);call('browsingContext.activate',{'context':ctx});pause(600)
    before=(HERE.parent/'viewer/bond-pick-before.js.txt').read_text();start=before.index('function fMulerSelectPick(');before=before[start:before.index('\nfunction fMulerSelectToggle(',start)];ev('window.__oldPick=('+before+');true')
    out['cases']=[]
    for mol,mode in [('ethane','condensed'),('ethane','expanded'),('ethane','skeletal'),('propane','condensed'),('butene_1','expanded')]:
        ev('selectedMol='+json.dumps(mol)+';mode2D='+json.dumps(mode)+';fSelectMol();true');pause(350)
        if not ev('fMulerSelectActive()'):pointer('#selectAtomsBtn');pause(150)
        row=read('''(()=>{
          const g=fMulerSelectGeom(), group=g.groups.find(x=>allAtomsTypeList[bondList[x.bond][0]-1]==='C'&&allAtomsTypeList[bondList[x.bond][1]-1]==='C');
          const l=group.lines[0], m=fGetRenderedAtomRectMap(false,mode2D==='expanded')||{}, rects=Object.entries(m).map(([atom,v])=>{const n=v.node||v,b=n.getBBox();return{atom:Number(atom),x:b.x,y:b.y,w:b.width,h:b.height}});
          const glyphs=g.anchors.filter(a=>a.w>0&&a.h>0).map(a=>({atom:a.atom,x:a.x-a.w/2,y:a.y-a.h/2,w:a.w,h:a.h}));
          const boxes=rects.concat(glyphs), inside=(p,r)=>p.x>=r.x&&p.x<=r.x+r.w&&p.y>=r.y&&p.y<=r.y+r.h;
          const samples=Array.from({length:99},(_,i)=>{const t=(i+1)/100,p={x:l.x1+t*(l.x2-l.x1),y:l.y1+t*(l.y2-l.y1)};return{t,...p,visible:!boxes.some(r=>inside(p,r)),clearance:Math.min(...boxes.map(r=>Math.hypot(Math.max(r.x-p.x,0,p.x-r.x-r.w),Math.max(r.y-p.y,0,p.y-r.y-r.h))))}});
          const visible=samples.filter(p=>p.visible), choice=visible.slice().sort((a,b)=>b.clearance-a.clearance)[0]||null;
          const mid={x:(l.x1+l.x2)/2,y:(l.y1+l.y2)/2},matrix=document.querySelector('#jsmeNomeclatureSVG svg g').getScreenCTM(),point=choice?new DOMPoint(choice.x,choice.y).matrixTransform(matrix):null;
          return{mol:selectedMol,mode:mode2D,bond:group.bond,rawBond:bondList[group.bond],line:l,anchors:g.anchors,rects,glyphs,mid:{...mid,insideGlyph:glyphs.filter(r=>inside(mid,r)).map(r=>r.atom),old:__oldPick(mid.x,mid.y),now:fMulerSelectPick(mid.x,mid.y)},visibleSamples:visible.map(p=>({t:p.t,old:__oldPick(p.x,p.y),now:fMulerSelectPick(p.x,p.y)})),choice:choice?{...choice,old:__oldPick(choice.x,choice.y),now:fMulerSelectPick(choice.x,choice.y),screen:{x:point.x,y:point.y}}:null};
        })()''')
        if row['choice']:
            pointer_at(row['choice']['screen']);pause(200);row['actualSelection']=read('({atoms:MulerUserSelection.atoms2D,bonds:MulerUserSelection.bonds2D})')
        out['cases'].append(row)
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:finish('visible-bond-diagnostic')
if not out['completed']:raise SystemExit(1)
