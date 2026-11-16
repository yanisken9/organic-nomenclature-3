from pathlib import Path
source = Path(__file__).with_name('acceptance.py').read_text()
exec(compile(source[:source.index("try:\n    call('script.addPreloadScript'")], 'detective-acceptance-helpers', 'exec'))
out['scope'] = 'Controlled server404 for first generated-child request only; real parent timeout and user Retry, then real native child and actual correct atom picks. Does not claim an external-service outage reproduction.'
try:
    navigate('games/molecular-detective.html')
    wait('!!window.NameleculeMolecularDetective')
    first_session = read('document.querySelector("#molecule-viewer").src')
    check(snapshot()['phase']=='startup' and ev('document.querySelector("#check-answer").disabled'),'Missing child cannot expose an answerable mission')
    wait(S+'.phase==="error"', 52)
    check(ev('!document.querySelector("#retry-load").hidden&&document.querySelector("#viewer-mask").hidden===false'),'Bounded actual startup failure exposes visible Retry')
    click('#retry-load');ready()
    check(read('document.querySelector("#molecule-viewer").src')!=first_session,'Retry creates a new child/session and reaches active actual graph')
    pick('atoms',2);pick('atoms',1);check_result(True)
    check(not js_errors,'Controlled child failure/retry has no captured JavaScript exceptions',js_errors)
    out['runtimeAtFinish']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    check(out['runtimeAtFinish']==hashes,'Eight runtime hashes unchanged during retry check')
    out['completed']=True
except Exception:
    out['failure']=traceback.format_exc()
    try:out['stateAtFailure']=snapshot();shot('failure')
    except Exception:pass
finally:finish('retry')
if not out['completed']:raise SystemExit(1)
