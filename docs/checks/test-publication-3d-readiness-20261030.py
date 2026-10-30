"""Targeted public3D follow-up after rapid smoke logged external JSmol null-viewer errors."""
from pathlib import Path
import argparse,traceback
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
exec(compile(Path('docs/checks/test-larger-2d-browser-20261026.py').read_text().split('rows=[]')[0],'existing-bidi-setup','exec'))
r={'completed':False,'models':[]}
try:
 navigate('mulermoc-nom-52.html?v=readiness-20261030');app_ready();until('!!window.JSmolReadyFlag')
 for key,n in [('methane',5),('methyl_2_pentane',20),('ethyl_3_dimethyl_2_5_hexane',32)]:
  ev('document.getElementById('+json.dumps(key)+').click();true')
  until("(()=>{try{const m=Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models;return m&&m.length===1&&m[0].file===new URL(nameExamples[selectedMol].file3D,document.baseURI).href}catch(e){return false}})()")
  row=json.loads(ev("JSON.stringify({key:selectedMol,atoms:Jmol.getPropertyAsArray(jmolAppletNomeclature,'atomInfo').length,parsed:allAtomsTypeList3D.length,file:Jmol.getPropertyAsArray(jmolAppletNomeclature,'modelInfo').models[0].file})"));assert row['atoms']==n and row['parsed']==n,row;r['models'].append(row)
 r['completed']=True
except Exception as e:
 r['failure']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
finally:
 r['javascriptErrors']=js_errors;(args.output/'readiness.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');call('browsingContext.close',{'context':ctx});call('session.end',{});print(json.dumps({'completed':r['completed'],'models':len(r['models']),'jsErrors':len(js_errors)}),flush=True)
if not r['completed']:raise SystemExit(1)
