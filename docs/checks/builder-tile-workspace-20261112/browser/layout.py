"""Current geometry using one disposable Firefox, never user profiles."""
from pathlib import Path
import datetime, http.server, json, os, socket, subprocess, tempfile, threading, time, traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
profile = tempfile.mkdtemp(prefix='namelecule-builder-layout-headless-20261112-')
log = (HERE / 'firefox.log').open('w')
firefox = subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox', '--headless',
    '--no-remote', '--profile', profile, '--remote-debugging-port', str(port)],
    stdout=log, stderr=subprocess.STDOUT)
process = {'serverPID': os.getpid(), 'serverScript': str(Path(__file__).resolve()),
    'firefoxPID': firefox.pid, 'profile': profile, 'bidiPort': port,
    'baseURL': f'http://127.0.0.1:{server.server_port}/',
    'scope': 'Only a new owned headless Firefox. No personal browser or application edits.'}
(HERE / 'process.json').write_text(json.dumps(process, indent=2) + '\n')
print(json.dumps(process), flush=True)
geometry = '''(() => {
 const rect = s => {const r=document.querySelector(s).getBoundingClientRect();
   return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}};
 return {viewport:[innerWidth,innerHeight],scrollY,bank:rect('#bank-zone'),
   firstTile:rect('#bank-tiles button'),answer:rect('#answer-zone'),
   molecule:rect('.molecule-panel'),candidate:rect('#candidate'),check:rect('#check-answer'),
   bankCount:document.querySelectorAll('#bank-tiles button').length,
   answerCount:document.querySelectorAll('#answer-tiles button').length,
   bodyHeight:document.body.getBoundingClientRect().height};
})()'''
results = {'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'conditions': 'Current app/native viewer, fresh disposable profile. No manual scroll inside a loaded quiz before geometry. Trusted clicks used only to enter lesson/game.',
    'entries': [], 'complete': False}
try:
    deadline=time.monotonic()+25
    while True:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.4):
                break
        except OSError:
            if firefox.poll() is not None or time.monotonic()>deadline:
                raise RuntimeError('Owned Firefox BiDi endpoint did not start')
            time.sleep(.2)
    exec(compile((HERE / 'helpers.py').read_text(), str(HERE / 'helpers.py'), 'exec'))
    for width,height in [(1500,900),(390,760)]:
        viewport(width,height)
        lesson(3,55)
        open_gate()
        choose('builder')
        pause(1)
        child=bread(geometry)
        parent=read('''(() => {
          const dialog=document.getElementById('nlQuizDialog'),frame=document.querySelector('.nl-builder-frame');
          const r=frame.getBoundingClientRect(),d=dialog.getBoundingClientRect(),h=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect();
          return {scrollTop:dialog.scrollTop,dialog:{top:d.top,bottom:d.bottom},
            headerBottom:h.bottom,frame:{top:r.top,bottom:r.bottom,height:r.height},
            progress:document.getElementById('nlQuizProgress').textContent};
        })()''')
        top=parent['frame']['top']+child['firstTile']['y']
        bottom=top+child['firstTile']['height']
        entry={'context':'lesson','viewport':[width,height],'child':child,'parent':parent,
          'firstTileFullyVisible':top>=parent['headerBottom'] and bottom<=parent['dialog']['bottom'],
          'bankToAnswerVerticalGap':child['bank']['y']-child['answer']['bottom'],
          'initialAnswerEmpty':child['answerCount']==0}
        results['entries'].append(entry)
        shot(f'lesson-{width}-after.png')
        print(json.dumps(entry),flush=True)
    viewport(1024,768)
    open_page('games/name-builder.html?molecule=butane')
    wait('!!document.querySelector("#bank-tiles button")',65)
    pause(.5)
    standalone=read(geometry)
    entry={'context':'standalone','viewport':[1024,768],'geometry':standalone,
      'firstTileFullyVisible':standalone['firstTile']['y']>=0 and standalone['firstTile']['bottom']<=768,
      'bankToAnswerVerticalGap':standalone['bank']['y']-standalone['answer']['bottom']}
    results['entries'].append(entry)
    shot('standalone-1024-after.png')
    results['complete']=True
    print(json.dumps(entry),flush=True)
except Exception:
    results['error']=traceback.format_exc()
    print(results['error'],flush=True)
finally:
    (HERE/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    try:
        if 'finish' in globals(): finish()
    except Exception as error:
        results['sessionCleanupError']=repr(error)
    server.shutdown()
    server.server_close()
    if firefox.poll() is None:
        firefox.terminate()
        try: firefox.wait(timeout=10)
        except subprocess.TimeoutExpired:
            firefox.kill();firefox.wait(timeout=5)
    log.close()
    process['ownedFirefoxExited']=firefox.poll() is not None
    process['ownedServerClosed']=True
    (HERE/'cleanup.json').write_text(json.dumps(process,ensure_ascii=False,indent=2)+'\n')
    (HERE/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
if not results['complete']:
    raise SystemExit(1)
