"""Owned disposable public candidate under a GitHub Pages-shaped prefix."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,os
ROOT=Path(__file__).resolve().parents[3]
STATE=json.loads((ROOT/'communication/checkpoints/save-publish-20261105-state.json').read_text())
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=STATE['publicClone'],**kwargs)
    def translate_path(self,path):
        prefix='/organic-nomenclature-3/'
        if path.startswith(prefix):path='/'+path[len(prefix):]
        return super().translate_path(path)
    def log_message(self,*args):pass
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',8057),Handler)
    print('Ownedpublicationserver',os.getpid(),STATE['publicClone'],flush=True)
    server.serve_forever()
