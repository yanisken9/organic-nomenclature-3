from pathlib import Path
import json,subprocess,tempfile,urllib.request,time,hashlib
root=Path(__file__).resolve().parents[3]
here=Path(__file__).resolve().parent
url='http://127.0.0.1:49897/mulermoc-nom-55.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&v=choice-games-20261111-r2#step=4'
with urllib.request.urlopen(url.split('#')[0],timeout=10) as response:
 data=response.read();assert response.status==200 and data==(root/'mulermoc-nom-55.html').read_bytes()
profile=Path(tempfile.mkdtemp(prefix='namelecule-lesson-preview-20261111-',dir='/private/tmp'))
log=(profile/'launch.log').open('w')
process=subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox','--no-remote','--profile',str(profile),'--new-window',url],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(3)
assert process.poll() is None,('Firefox exited',process.returncode)
record={'url':url,'pid':process.pid,'profile':str(profile),'userFacing':True,'headless':False,'debugConnection':False,'personalProfileAccessed':False,'htmlHTTPStatus':200,'htmlMatchesDisk':True,'scope':'Normal isolated external Firefox for user; keep open. No personal browser modification or diagnostic control.'}
(profile/'launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(here/'launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
