from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
import os,socket,json,time
H=Path(__file__).resolve().parent;ROOT=Path.cwd();OVERLAY=H/'original-before'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def translate_path(self,path):
  clean=urlsplit(path).path.lstrip('/')
  if (OVERLAY/clean).is_file():return str(OVERLAY/clean)
  return super().translate_path(path)
 def do_GET(self):
  clean=urlsplit(self.path).path;fault=json.loads((H/'fault-control.json').read_text())
  if clean==fault.get('path') and fault.get('mode')=='delay':
   started=time.monotonic()
   with (H/'original-fault-requests.jsonl').open('a') as log:log.write(json.dumps({'path':clean,'mode':'delay','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})+'\n')
   while time.monotonic()-started<30 and json.loads((H/'fault-control.json').read_text()).get('mode')=='delay':time.sleep(.05)
  return super().do_GET()
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);port=server.server_address[1];p=json.loads((H/'process.json').read_text());p.update({'serverPID':os.getpid(),'serverScript':str(Path(__file__).resolve()),'before_url':f'http://127.0.0.1:{port}/','before_port':port,'scope':'Owned additional HTTPonly original R0five-source overlay; reuse alreadyowned isolatedFirefox only.'});assert not(H/'original-process.json').exists();(H/'original-process.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps({'serverPID':os.getpid(),'port':port}),flush=True);server.serve_forever()
