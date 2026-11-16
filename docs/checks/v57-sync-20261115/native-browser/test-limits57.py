"""Actual UI fallback for unsupported stereo and raw SUP normalization; no guard relaxation."""
from pathlib import Path
exec(compile(Path(__file__).with_name('test-native57.py').read_text().split('\ntry:\n')[0],'native57-limithelpers','exec'))
try:
    assert frozen();call('script.addPreloadScript',{'functionDeclaration':'()=>{window.MULER_QUIET_FETCH=true;}','contexts':[ctx]})
    navigate('mulermoc-nom-57.html?libs=cdn&lang=en');app_ready();wait('window.JSmolReadyFlag===true',70)
    out['runtimeExamples']=[]
    for m in ['trimethyl_3_4_4_pentanone_2','methyl_3_penten_2_dial','methanoicacid']:
        select(m,'condensed' if m=='methanoicacid' else 'expanded');active()
        maps=read('(()=>{const a=fParseMolV2000(jsmeNomeclatureApplet.molFile()),b=fParseMolV2000(molAtomMapSource3D),f=fMulerSelectFullMap();return{mol:selectedMol,mode:mode2D,mapped:!!f,properties2:a.properties,parity3:b.atoms.filter(x=>x.parity).length,stereo3:b.bonds.filter(x=>Number(String(x.tail||"").slice(0,3))!==0).length}})()');out['runtimeExamples'].append(maps)
        if m!='methanoicacid':
            check(not maps['mapped'],'Actual runtime stereo source refuses unsupported cross-map: '+m,maps)
            if not ev('window.MulerQuizTarget==="compCarbonsCount"'):click('#comp5')
            wait('window.MulerQuizTarget==="compCarbonsCount"');a=read('allAtomsTypeList3D.indexOf("C")+1');pick3(a)
            check(ev('window.MulerQuizTarget==="compCarbonsCount"&&!fMulerSelectState().atoms2D.length&&!fMulerSelectState().atoms3D.length&&document.querySelector("#mulerQuizVerdict").textContent.includes("reliable")'),'Genuine unsupported3D pick explains2D fallback without false reward: '+m)
            for atom in read('fMulerMainChainResolved().slice()'):pick2(atom)
            check(ev('!window.MulerQuizTarget&&document.querySelector("#comp5").classList.contains("selected")'),'Same actual native mission remains solvable through2D: '+m)
        else:
            check((not maps['properties2'] and maps['mapped']) or (maps['properties2'] and not maps['mapped']),'Actual methanoic-acid SUP normalization and mapping outcome recorded consistently',maps)
    check(frozen(),'All17 frozen hashes unchanged during unsupported-source UI checks');shot('native57-supported-fallback');out['completed']=True
except Exception:
    out['failure']=traceback.format_exc();print(out['failure'],flush=True)
    try:shot('native57-limits-failure');out['modelAtFailure']=model_state()
    except Exception:pass
finally:finish('limits57')
if not out['completed']:raise SystemExit(1)
