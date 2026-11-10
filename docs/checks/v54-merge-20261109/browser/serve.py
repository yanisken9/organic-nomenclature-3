"""Owned candidate HTTP server with a GitHub Pages-shaped path prefix."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import os,sys
root=Path(sys.argv[1]).resolve();port=int(sys.argv[2]);os.chdir(root)
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  prefix='/organic-nomenclature-3/'
  if path.startswith(prefix):path='/'+path[len(prefix):]
  return super().translate_path(path)
server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
print('Owned candidate server',os.getpid(),root,port,flush=True);server.serve_forever()
