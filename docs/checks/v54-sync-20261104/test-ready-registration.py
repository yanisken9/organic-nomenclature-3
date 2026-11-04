from pathlib import Path
import re,json,subprocess,hashlib
H=Path('docs/checks/v54-sync-20261104');hook=Path('js/mulermoc-nom-molview-54.js').read_text().split('var _resizeSentOn3DReady = false;',1)[1]
head=lambda s:re.search(r'jmol_isReady = function \(applet\).*?</script>',s,re.S).group(0).removesuffix('</script>')
rows=[]
for label,p in [('before',H/'review-correction-before-mulermoc-nom-54.html'),('after',Path('mulermoc-nom-54.html'))]:
 code='''var window={__mulerPending3D:'propene'},selectedMol='propene',loads=0,document={querySelector(){return {}}},console={warn(){},error(){}};function setTimeout(){};function fResizeViewers(){};function fJSmolLive(){return window.JSmolReadyFlag===true};function fLoadMol3D(){loads++};function showAtomSymbols3D(){};function showHydrogens3D(){};function rotate3D(){};
'''+head(p.read_text())+''';var actualRegisteredCallback=JSmol_Applet.readyFunction;var _resizeSentOn3DReady=false;'''+hook+''';actualRegisteredCallback({});print(JSON.stringify({ready:window.JSmolReadyFlag,pending:window.__mulerPending3D,loads}));'''
 r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e','eval(JSON.parse(readline()))'],input=json.dumps(code)+'\n',text=True,capture_output=True)
 assert r.returncode==0,(r.stdout[-1000:],r.stderr[-500:]);rows.append({'version':label,**json.loads(r.stdout)})
assert rows[0]['loads']==0 and rows[0]['pending']=='propene',rows
assert rows[1]['loads']==1 and rows[1]['pending']is None and rows[1]['ready'],rows
out={'rows':rows,'sourceHTML_SHA256':hashlib.sha256(Path('mulermoc-nom-54.html').read_bytes()).hexdigest(),'execution':'Actualheadinitialization + actualviewerhook, storedregisteredcallback invoked in memory; functions outside callback path stubbed.'}
(H/'ready-registration-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
