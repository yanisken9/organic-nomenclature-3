"""Bounded real pointer checks of additional v56 selection entry contracts."""
from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'support.py').read_text(),'owned56-extra-support','exec'))
def select(mol,mode='condensed'):
    ev('selectedMol='+json.dumps(mol)+';mode2D='+json.dumps(mode)+';fSelectMol();true');pause(450)
def atom(a):
    point=read('(()=>{const a=fMulerSelectAnchors().find(p=>p.atom==='+str(a-1)+');const g=document.querySelector("#jsmeNomeclatureSVG svg g");const p=new DOMPoint(a.x,a.y).matrixTransform(g.getScreenCTM());return{x:p.x,y:p.y}})()');pointer_at(point);pause(220)
def bond_point(order):
    script=r"""(()=>{
      const geom=fMulerSelectGeom(),group=geom.groups.find(g=>bondList[g.bond][2]===__ORDER__&&allAtomsTypeList[bondList[g.bond][0]-1]==='C'&&allAtomsTypeList[bondList[g.bond][1]-1]==='C');
      if(!group)throw Error('Missing C-C bond');const l=group.lines[0],map=fGetRenderedAtomRectMap(false,mode2D==='expanded')||{};
      const boxes=Object.values(map).map(v=>{const n=v.node||v,b=n.getBBox();return{x:b.x,y:b.y,w:b.width,h:b.height}}).concat(geom.anchors.filter(a=>a.w>0&&a.h>0).map(a=>({x:a.x-a.w/2,y:a.y-a.h/2,w:a.w,h:a.h})));
      const samples=Array.from({length:99},(_,i)=>{const t=(i+1)/100;return{t,x:l.x1+t*(l.x2-l.x1),y:l.y1+t*(l.y2-l.y1)}}).filter(p=>!boxes.some(b=>p.x>=b.x&&p.x<=b.x+b.w&&p.y>=b.y&&p.y<=b.y+b.h));
      if(!samples.length)throw Error('No bond stroke outside labels');const center=(samples[0].t+samples[samples.length-1].t)/2,q=samples.slice().sort((a,b)=>Math.abs(a.t-center)-Math.abs(b.t-center))[0];
      const g=document.querySelector('#jsmeNomeclatureSVG svg g'),screen=new DOMPoint(q.x,q.y).matrixTransform(g.getScreenCTM());
      return{x:screen.x,y:screen.y,bond:group.bond+1,rawBondIndex:group.bond,rawBond:bondList[group.bond],world:q,pick:fMulerSelectPick(q.x,q.y),glyphs:geom.anchors};
    })()"""
    return read(script.replace('__ORDER__',str(order)))

try:
    navigate('mulermoc-nom-56.html?lang=en&mol=ethane&v=native-extra56-'+str(time.time_ns()));app_ready();wait('window.JSmolReadyFlag===true',60);call('browsingContext.activate',{'context':ctx});pause(800)
    for mode in ['condensed','expanded','skeletal']:
        select('ethane',mode)
        if not ev('fMulerSelectActive()'):pointer('#selectAtomsBtn')
        point=bond_point(1);out.setdefault('bondProbes',[]).append({'mode':mode,'point':point});pointer_at(point);pause(200)
        check(read('MulerUserSelection.bonds2D')==[point['bond']],mode+': actual free bond pick selects correct bond')
        pointer_at(point);pause(200);check(ev('MulerUserSelection.bonds2D.length===0'),mode+': re-click removes free bond')
    select('butene_1','expanded');pointer('#comp6');wait('window.MulerQuizTarget==="compBondType"')
    point=bond_point(2);pointer_at(point);pause(250)
    check(ev('!window.MulerQuizTarget&&document.querySelector("#comp6").classList.contains("selected")'),'actual double-bond mission produces native successful reward')
    select('ethanol','expanded');pointer('#comp9');wait('window.MulerQuizTarget==="compSuffix"')
    targets=read('fMulerQuizTargetSet().slice()');out['functionalGroupTargets']=read('fMulerQuizTargetSet().map(a=>({atom:a,element:allAtomsTypeList[a-1]}))')
    check(len(targets)>0 and any(x['element']=='O'for x in out['functionalGroupTargets']),'alcohol mission resolves actual O-containing group')
    for a in targets:atom(a)
    check(ev('!window.MulerQuizTarget&&document.querySelector("#comp9").classList.contains("selected")'),'actual functional-group pointer selection earns native reward')
    pointer('#viewerSettingsBtn');pause(300);pointer('#allowSelectCheck');pause(200)
    check(ev('!fMulerSelectActive()') and not visible('#selectAtomsBtn'),'unchecking Allow selections exits and hides selection')
    pointer('#allowSelectCheck');pause(200);check(visible('#selectAtomsBtn'),'Allow selections restores entry');pointer('#viewerSettingsBtn')
    pointer('#selectAtomsBtn');pause(200);check(ev('fMulerSelectActive()'),'selection re-arms before draft')
    pointer('#newMolBtn');wait('!!window.MulerDraft')
    check(ev('!fMulerSelectActive()&&document.querySelector("#selectAtomsBtn").classList.contains("btnInactive")'),'draft entry exits selection and dims entry')
    pointer('#molDraftCancelBtn');wait('!window.MulerDraft');pause(250)
    check(visible('#selectAtomsBtn') and ev('!document.querySelector("#selectAtomsBtn").classList.contains("btnInactive")'),'Cancel restores selection entry without stale active state')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:shot('native-extra-failure');out['failureState']=read('({mol:selectedMol,mode:mode2D,target:window.MulerQuizTarget,selection:window.MulerUserSelection})')
    except Exception:pass
finally:finish('native-extra56-browser')
if not out['completed']:raise SystemExit(1)
