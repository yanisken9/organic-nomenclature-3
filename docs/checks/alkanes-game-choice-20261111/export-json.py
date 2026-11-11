from pathlib import Path
import json,hashlib,shutil,datetime
root=Path(__file__).resolve().parents[3]
mapping=json.loads((root/'communication/checkpoints/alkanes-json-export-20261109.json').read_text())
src=root/'scenarios/alkanes-user-3.scenario.json';dst=Path(mapping['destination'])
before=dst.read_bytes();data=src.read_bytes()
assert hashlib.sha256(before).hexdigest()==mapping['sha256'],'Desktop current copy changed since reviewed baseline; preserve before determining export'
now=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=dst.parent/'Namelecule_11-11-2026'/(dst.stem+'-before-game-choice-'+now+'.json')
backup.parent.mkdir(exist_ok=True);assert not backup.exists();shutil.copy2(dst,backup)
dst.write_bytes(data);assert dst.read_bytes()==data and backup.read_bytes()==before
record={'date':'2026-11-11','source':str(src),'destination':str(dst),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'byte_identical':True,'steps':12,'mode':'Approved choice of Workshop or Name Builder at steps4/11; three distinct molecules in one game; other10steps unchanged','Desktop_recovery':str(backup),'previous_destination_sha256':hashlib.sha256(before).hexdigest(),'previous_mapping':'communication/checkpoints/alkanes-json-export-20261109.json','core_changed':False,'no_publication':True}
(root/'communication/checkpoints/alkanes-json-export-20261111-game-choice.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
