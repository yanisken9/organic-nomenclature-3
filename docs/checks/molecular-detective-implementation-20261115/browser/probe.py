from pathlib import Path
exec(compile((Path(__file__).with_name('support.py')).read_text(), 'detective-support', 'exec'))
try:
    navigate('games/molecular-detective.html')
    wait('!!window.NameleculeMolecularDetective', 10)
    try: wait('NameleculeMolecularDetective.snapshot().phase==="active"', 45)
    except Exception:
        out['pageState'] = read('({state:NameleculeMolecularDetective.snapshot(),status:document.querySelector("#game-status").textContent,host:document.querySelector("iframe").contentWindow.NameleculeMolecularDetectiveHost?.snapshot()})')
        raise
    check(True, 'Initial real game startup active', read('NameleculeMolecularDetective.snapshot()'))
    out['graph'] = read('document.querySelector("iframe").contentWindow.NameleculeMolecularDetectiveHost.getSnapshot()')
    out['geometry'] = read('(()=>{const w=document.querySelector("iframe").contentWindow,g=w.fMulerSelectGeom();return{keys:Object.keys(g),anchors:g.anchors?.slice(0,3),groups:g.groups?.slice(0,3)}})()')
    shot('first-game')
    out['completed'] = True
except Exception:
    out['failure'] = traceback.format_exc()
    try: shot('failure')
    except Exception: pass
finally: finish('probe')
if not out['completed']: raise SystemExit(1)
