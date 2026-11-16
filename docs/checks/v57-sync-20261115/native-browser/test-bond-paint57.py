from pathlib import Path
exec(compile(Path(__file__).with_name('test-native57.py').read_text().split('\ntry:\n')[0],'native57-bondhelpers','exec'))
try:
    navigate('mulermoc-nom-57.html?libs=cdn');app_ready();wait('window.JSmolReadyFlag===true',70);select('butane');active()
    cc=read('bondList3D.map((b,i)=>({id:i+1,b})).filter(x=>allAtomsTypeList3D[x.b[0]-1]==="C"&&allAtomsTypeList3D[x.b[1]-1]==="C")');out['cc']=cc;assert len(cc)==3
    chosen=next([a,b] for i,a in enumerate(cc) for b in cc[i+1:] if not set(a['b'][:2])&set(b['b'][:2]));bridge_id=next(b['id'] for b in cc if b not in chosen);out['chosen']=chosen
    for b in chosen:
        a=point3d(b['b'][0]);z=point3d(b['b'][1]);pointer_at({'x':(a['x']+z['x'])/2,'y':(a['y']+z['y'])/2});pause(300)
    check(sorted(sel()['b3'])==sorted([b['id'] for b in chosen]),'Genuine disjoint3D bond picks retain exactly two IDs',sel())
    pause(700);out['paint']=read('Jmol.getPropertyAsArray(jmolAppletNomeclature,"bondInfo","all").map(b=>({id:b._bpt+1,colix:b.colix,ends:[b.atom1.atomno,b.atom2.atomno]}))')
    bridge=next(b for b in out['paint'] if b['id']==bridge_id);out['unselectedBridgeColored']=bridge['colix']!=0
    out['expectedPhase']=os.environ.get('NAMELECULE_PAINT_PHASE','before')
    check(out['unselectedBridgeColored']==(out['expectedPhase']=='before'),'Actual live bondInfo confirms '+out['expectedPhase']+' correction paint oracle',out['paint'])
    shot('disjoint-bonds-'+out['expectedPhase']);out['completed']=True
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:finish('bond-paint57')
if not out['completed']:raise SystemExit(1)
