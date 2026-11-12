"""User-review localhost server; no browser control or app mutations."""
from pathlib import Path
import http.server,json,os
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
record={'PID':os.getpid(),'script':str(Path(__file__).resolve()),'baseURL':'http://127.0.0.1:'+str(server.server_port)+'/','scope':'Only a read-only local preview server; no personal Firefox control.'}
(HERE/'preview-server.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
try:server.serve_forever()
finally:server.server_close()
