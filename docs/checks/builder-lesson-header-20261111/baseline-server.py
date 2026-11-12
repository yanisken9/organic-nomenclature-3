"""Read-only historical browser comparison: four frozen files, protected current dependencies."""
from pathlib import Path
import http.server,json,os,urllib.parse
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
FILES={'js/namelecule-game-choice-checkpoint.js','css/namelecule-quiz-checkpoints.css','mulermoc-nom-54.html','mulermoc-nom-55.html'}
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def translate_path(self,path):
  rel=urllib.parse.unquote(urllib.parse.urlsplit(path).path).lstrip('/')
  if rel in FILES:return str(HERE/'before'/rel)
  return super().translate_path(path)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
record={'PID':os.getpid(),'script':str(Path(__file__).resolve()),'baseURL':'http://127.0.0.1:'+str(server.server_port)+'/','scope':'Frozen4before overrides; allothercurrentdependenciesprotectedunchanged; no appsource mutations.'}
(HERE/'baseline-server.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
try:server.serve_forever()
finally:server.server_close()
