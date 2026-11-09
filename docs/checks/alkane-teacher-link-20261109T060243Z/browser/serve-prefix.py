from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import sys,urllib.parse
root=Path(sys.argv[1]).resolve();port=int(sys.argv[2]);prefix='/organic-nomenclature-3/'
class H(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  p=urllib.parse.urlsplit(path).path
  if not p.startswith(prefix):return str(root/'__missing_outside_github_pages_prefix__')
  p=urllib.parse.unquote(p[len(prefix):]);parts=Path(p).parts
  if '..' in parts:return str(root/'__unsafe_path__')
  return str(root.joinpath(*parts))
ThreadingHTTPServer(('127.0.0.1',port),H).serve_forever()
