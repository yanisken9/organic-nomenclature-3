from pathlib import Path
import json,hashlib,subprocess,shutil,zipfile,re,plistlib,urllib.parse
R=Path.cwd();H=R/'docs/checks/publication-20261101';SP=R/'communication/checkpoints/save-publish-20261101-state.json';s=json.loads(SP.read_text());C=Path(s['checkpointClone']);A=R/'communication/checkpoints'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(p,*args,**kw):return subprocess.check_output(['git','-C',str(p),*args],**kw)
def invariant():
 assert git(R,'rev-parse','HEAD').decode().strip()==s['activeHead'];assert git(R,'branch','--show-current').decode().strip()==s['activeBranch'];assert sha(R/'.git/index')==s['indexSHA256'];assert sha(R/'js/mulermoc-nom-core-52.js')==s['coreSHA256']
def save(generation):
 invariant();paths={p.decode()for p in git(R,'ls-files','--cached','--others','--exclude-standard','-z').split(b'\0')if p}
 for directory in ['react-preview/dist','react-preview/public']:
  paths.update(str(p.relative_to(R))for p in(R/directory).rglob('*')if p.is_file()and p.name!='.DS_Store'and p.suffix!='.log')
 paths=sorted(p for p in paths if(R/p).is_file());hashes={p:sha(R/p)for p in paths};findings=[]
 patterns=[r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'AKIA[A-Z0-9]{16}',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
 for p in paths:
  if(R/p).stat().st_size>2_000_000:continue
  try:text=(R/p).read_text()
  except UnicodeError:continue
  if any(re.search(pattern,text)for pattern in patterns):findings.append(p)
 assert not findings,('Recognizable secret pattern found; paths only',findings)
 old={p.decode()for p in git(C,'ls-files','-z').split(b'\0')if p}
 for p in old-set(paths):(C/p).unlink()
 for p in paths:
  assert not(R/p).is_symlink(),('Unexpected symlink',p)
  target=C/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/p,target)
 subprocess.run(['git','-C',str(C),'add','-A'],check=True)
 subprocess.run(['git','-C',str(C),'add','-f','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode()for p in paths)+b'\0',check=True)
 ordered=[]
 for row in git(C,'ls-files','-s','-z').split(b'\0'):
  if row:
   fields,p=row.split(b'\t',1);ordered.append((p.decode(),fields.split()[1].decode()))
 assert set(p for p,o in ordered)==set(paths)
 raw=git(C,'cat-file','--batch',input=''.join(o+'\n'for p,o in ordered).encode());pos=0
 for p,o in ordered:
  end=raw.index(b'\n',pos);n=int(raw[pos:end].split()[2]);pos=end+1;blob=raw[pos:pos+n];pos+=n+1;assert hashlib.sha256(blob).hexdigest()==hashes[p],('Staged bytes changed',p)
 subprocess.run(['git','-C',str(C),'commit','--quiet','--allow-empty','-m','Save complete Namelecule '+generation+' state — 1 November 2026'],check=True)
 commit=git(C,'rev-parse','HEAD').decode().strip();name='Namelecule-'+s['stamp']+'-'+generation
 archive=A/(name+'.zip');assert not archive.exists()
 manifest={'date':'2026-11-01','generation':generation,'checkpointCommit':commit,'publicReleaseCommit':s.get('publicReleaseCommit'),'files':hashes,'exclusions':'git/dependencies/caches/oldcommunicationarchives/privateuntrackedsettings; React dist/public included; launcher and communication recovery copied separately'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in paths:z.write(R/p,'Namelecule/'+p)
  z.writestr('Namelecule/SNAPSHOT-MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for p,d in hashes.items():assert hashlib.sha256(z.read('Namelecule/'+p)).hexdigest()==d,p
 bundle=A/(name+'.bundle');assert not bundle.exists();subprocess.run(['git','-C',str(C),'bundle','create',str(bundle),'--all'],check=True,stdout=subprocess.DEVNULL);subprocess.run(['git','-C',str(C),'bundle','verify',str(bundle)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 recovery=A/(name+'-recovery.zip');recoveryfiles={str(p.relative_to(R)):sha(p)for p in(R/'communication').rglob('*')if p.is_file()and p.suffix not in ['.zip','.bundle','.log','.sha256']and p.name!='.DS_Store'}
 with zipfile.ZipFile(recovery,'w',zipfile.ZIP_DEFLATED)as z:
  for p in recoveryfiles:z.write(R/p,p)
  z.writestr('RECOVERY-MANIFEST.json',json.dumps(recoveryfiles,indent=2))
 with zipfile.ZipFile(recovery)as z:
  assert z.testzip()is None
  for p,d in recoveryfiles.items():assert hashlib.sha256(z.read(p)).hexdigest()==d
 lessons=sorted(set(re.findall(r'scenario=(scenarios/[^&"\s]+)',(R/'design/theory-library.html').read_text())));assert len(lessons)==14;assert sum(len(json.loads((R/p).read_text())['steps'])for p in lessons)==337
 app=Path.home()/'Desktop/Namelecule.app';appfiles=[p for p in app.rglob('*')if p.is_file()and p.name!='.DS_Store'];assert appfiles
 reportbase='https://yanisken9.github.io/organic-nomenclature-3/docs/professor-20261101/update.html';links=json.loads((R/'docs/professor-20261101/links.json').read_text());copies=[]
 for folder in s['externalFolders']:
  dest=Path(folder);dest.mkdir(parents=True,exist_ok=True)
  for p in [archive,bundle,recovery]:
   target=dest/p.name;shutil.copy2(p,target);assert sha(target)==sha(p);(dest/(p.name+'.sha256')).write_text(sha(p)+'  '+p.name+'\n')
  report=dest/'Αναφορά καθηγητή';report.mkdir(exist_ok=True)
  for p in(R/'docs/professor-20261101').iterdir():
   if p.is_file():shutil.copy2(p,report/p.name)
  text=(report/'update.html').read_text();text=re.sub(r'href="([^"#][^"]*)"',lambda m:'href="'+urllib.parse.urljoin(reportbase,m.group(1))+'"',text)
  for image in re.findall(r'<img[^>]*src="([^"]+)"',text):
   source=(R/'docs/professor-20261101'/image).resolve();shutil.copy2(source,report/source.name);text=text.replace('src="'+image+'"','src="'+source.name+'"')
  (report/'update.html').write_text(text)
  for p in ['links.json','links.txt','message-to-professor.txt']:shutil.copy2(R/'docs/professor-20261101'/p,dest/p)
  for title,key in [('Αναφορά καθηγητή','report'),('Namelecule — Υποδοχή','welcome')]:(dest/(title+'.webloc')).write_bytes(plistlib.dumps({'URL':links[key]}))
  scenario_dir=dest/'Σενάρια JSON';scenario_dir.mkdir(exist_ok=True)
  for p in lessons:shutil.copy2(R/p,scenario_dir/Path(p).name);assert sha(R/p)==sha(scenario_dir/Path(p).name)
  shutil.copytree(app,dest/'Namelecule.app',dirs_exist_ok=True)
  for p in appfiles:assert sha(p)==sha(dest/'Namelecule.app'/p.relative_to(app))
  for p in ['SESSION-NOTES.md','YANNIS-CONTRIBUTIONS.md']:shutil.copy2(R/'docs'/p,dest/p)
  (dest/'ΔΙΑΒΑΣΕ ΠΡΩΤΑ.txt').write_text('Namelecule — Συνολική αποθήκευση 1/11/2026\nΓενιά: '+generation+'\nΑναφορά: '+links['report']+'\nΥποδοχή: '+links['welcome']+'\nΠλήρες ZIP: '+archive.name+'\nCheckpoint: '+commit+'\nΤο πλήρες αντίγραφο πηγών δεν είναι offline πακέτο συνεδρίου. Τα παλιότερα αντίγραφα διατηρούνται.\n')
  copies.append({'directory':str(dest),'archiveHashesVerified':True,'activeScenarioJSON':14,'launcherFiles':len(appfiles),'linksAndReportSaved':True})
 invariant();s.update(latestLocalCheckpointCommit=commit,sourceFileCount=len(paths),archive=str(archive.relative_to(R)),archiveSHA256=sha(archive),bundle=str(bundle.relative_to(R)),bundleSHA256=sha(bundle),bundleVerified=True,recoveryArchive=str(recovery.relative_to(R)),recoveryArchiveSHA256=sha(recovery),recoveryFiles=len(recoveryfiles),externalCopies=copies,sourceZIPAllHashesAndCRCVerified=True,coreChangedThisSaveSession=False,generation=generation,activeBranchHeadIndexPreserved=True,secretPatternScanFindings=[])
 SP.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');receipt=A/('final-save-state-'+s['stamp']+'.json');receipt.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
 for item in copies:shutil.copy2(receipt,Path(item['directory'])/'final-save-state.json')
 print(json.dumps({'generation':generation,'commit':commit,'files':len(paths),'ZIP':str(archive),'externalVerified':len(copies),'coreChanged':False},ensure_ascii=False),flush=True)
if __name__=='__main__':
 import sys;save(sys.argv[1])
