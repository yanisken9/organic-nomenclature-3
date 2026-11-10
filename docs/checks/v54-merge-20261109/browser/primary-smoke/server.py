"""Separately owned PRIMARY localhost server; launch only after root install-complete."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import os,sys
port=int(sys.argv[1]);root=Path(sys.argv[2]).resolve();os.chdir(root)
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  prefix='/organic-nomenclature-3/'
  if path.startswith(prefix):path='/'+path[len(prefix):]
  return super().translate_path(path)
print('Owned primary server',os.getpid(),port,str(root),flush=True);ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
