from pathlib import Path
import importlib.util,sys,tempfile,unittest.mock as mock,json
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('save_ops',here/'release-ops.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)
with tempfile.TemporaryDirectory(prefix='namelecule-exact-read-')as td:
 p=Path(td)/'payload';p.write_bytes(b'nonempty source bytes\r\n');original=Path.open
 class Proxy:
  def __init__(self,fp,empty):self.fp=fp;self.empty=empty
  def __enter__(self):self.fp.__enter__();return self
  def __exit__(self,*a):return self.fp.__exit__(*a)
  def fileno(self):return self.fp.fileno()
  def read(self):return b''if self.empty else self.fp.read()
 def opened(path,*a,**k):return Proxy(original(path,*a,**k),True)if path==p else original(path,*a,**k)
 assert ops.exact(p)==p.read_bytes();tests=['ordinary exact read']
 with mock.patch.object(Path,'open',opened):
  try:ops.exact(p);raise AssertionError('short read accepted')
  except RuntimeError as e:assert 'short/cloud-empty'in str(e)
 tests.append('nonempty stat plus repeatedly empty reads rejected')
 n=[0]
 def once(path,*a,**k):
  if path!=p:return original(path,*a,**k)
  n[0]+=1;return Proxy(original(path,*a,**k),n[0]==1)
 with mock.patch.object(Path,'open',once):assert ops.exact(p)==b'nonempty source bytes\r\n'and n[0]==2
 tests.append('one transient cloud-empty read retried to exact bytes')
 n=[0]
 def canceled_once(path,*a,**k):
  if path==p:
   n[0]+=1
   if n[0]==1:raise OSError(89,'Operation canceled')
  return original(path,*a,**k)
 with mock.patch.object(Path,'open',canceled_once):assert ops.exact(p)==b'nonempty source bytes\r\n'and n[0]==2
 tests.append('transient macOS canceled read retried without accepting missing bytes')
 def canceled(path,*a,**k):
  if path==p:raise OSError(89,'Operation canceled')
  return original(path,*a,**k)
 with mock.patch.object(Path,'open',canceled):
  try:ops.exact(p);raise AssertionError('persistent cancellation accepted')
  except OSError as e:assert e.errno==89 and 'six attempts'in str(e)
 tests.append('persistent canceled read fails after bounded retries')
 def denied(path,*a,**k):
  if path==p:raise PermissionError(13,'denied')
  return original(path,*a,**k)
 with mock.patch.object(Path,'open',denied):
  try:ops.exact(p);raise AssertionError('permission failure accepted')
  except PermissionError:pass
 tests.append('unrelated I/O failure propagated')
 p.chmod(0o755);dst=Path(td)/'copied';ops.copydata(p,dst);assert dst.read_bytes()==p.read_bytes()and dst.stat().st_mode&0o777==0o755
 tests.append('atomic copied executable retains source permissions and exact bytes')
 p.write_bytes(b'');assert ops.exact(p)==b'';tests.append('genuine zero-length file accepted')
 (here/'exact-read-regression.json').write_text(json.dumps({'passed':True,'checks':tests,'scope':'Controlled real file descriptor/stat with explicit empty-read double; not an iCloud provider reliability guarantee.'},indent=2)+'\n')
 print('PASS',len(tests),'exact-read checks')
