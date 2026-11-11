from pathlib import Path
import subprocess,sys
h=Path(__file__).resolve().parent
for name in ['compatibility.py','migration.py','timeout-retry.py']:
 print('RUN '+name,flush=True)
 r=subprocess.run([sys.executable,str(h/name)])
 if r.returncode:raise SystemExit(r.returncode)
 print('PASS '+name,flush=True)
