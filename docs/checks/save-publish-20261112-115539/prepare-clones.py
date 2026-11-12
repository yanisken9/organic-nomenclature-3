from pathlib import Path
import json,subprocess,hashlib,concurrent.futures
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
s=json.loads((R/'communication/checkpoints/save-publish-20261112-state.json').read_text());old=json.loads((R/'communication/checkpoints/save-publish-20261111-state.json').read_text())
def clone(key):
 dst=Path(s[key]);assert not dst.exists();src=Path(old[key]);expected=s['previousPublic'if key=='publicClone'else'previousCheckpoint']
 assert subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()==expected
 subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(src),str(dst)],check=True)
 subprocess.run(['git','-C',str(dst),'remote','set-url','origin',s['publicRemote']],check=True)
 (dst/'.git/info/attributes').write_bytes(b'* -text -eol -filter -ident\n')
 branch=s['publicBranch'if key=='publicClone'else'checkpointBranch']
 subprocess.run(['git','-C',str(dst),'checkout','--quiet','-B',branch,expected],check=True)
 assert not subprocess.check_output(['git','-C',str(dst),'status','--porcelain'])
 return dst
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:public,checkpoint=list(pool.map(clone,['publicClone','checkpointClone']))
paths=subprocess.check_output(['git','-C',str(public),'ls-files','-z']).split(b'\0')
hashes={p.decode():hashlib.sha256((public/p.decode()).read_bytes()).hexdigest()for p in paths if p}
(H/'public-baseline-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps({'publicFiles':len(hashes),'clonesReady':True,'attributesRaw':True,'sharedObjects':'Previous owned clones; full recovery bundle verified independently before completion.'}))
