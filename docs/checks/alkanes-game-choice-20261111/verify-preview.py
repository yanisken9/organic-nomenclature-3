from pathlib import Path
import json,hashlib,urllib.request
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
paths=['mulermoc-nom-55.html','js/namelecule-quiz-checkpoints.js','js/namelecule-generated-repair-checkpoint.js','js/namelecule-game-choice-checkpoint.js','scenarios/alkanes-user-3.scenario.json']
result=[]
for p in paths:
 with urllib.request.urlopen('http://127.0.0.1:49897/'+p+'?v=choice-games-20261111-r2',timeout=10)as response:
  data=response.read();assert response.status==200 and data==(R/p).read_bytes();result.append({'path':p,'status':response.status,'sha256':hashlib.sha256(data).hexdigest(),'equalsDisk':True})
(H/'preview-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Verified normal previewHTTP/SHA for',len(result),'paths')
