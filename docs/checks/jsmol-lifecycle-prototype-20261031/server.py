from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import time
root=Path('/tmp/namelecule-jsmol-lifecycle-prototype-20261031')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path.startswith('/slow/'):
   self.path=self.path[5:]
   if path.endswith(('.sdf','.spt')):time.sleep(.5)
  return super().do_GET()
ThreadingHTTPServer(('127.0.0.1',8029),Handler).serve_forever()
