from pathlib import Path
import subprocess,re
P=Path.cwd();C=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate')
local=(P/'js/mulermoc-nom-molview-54.js').read_text();up=(P/'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-molview-55.js').read_text()
s=subprocess.run(['git','merge-file','-p',str(P/'js/mulermoc-nom-molview-54.js'),str(P/'docs/checks/v54-merge-20261109/upstream/base/js/mulermoc-nom-molview-54.js'),str(P/'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-molview-55.js')],capture_output=True).stdout.decode()
n=0
def resolve(m):
 global n
 n+=1;a,b=m.group(1),m.group(2)
 if n in (2,3,4,10,11,12,13):
  if n==2:b=b.replace('init-3.spt','init-54.spt')
  if n==10:b=b.replace('currComp = _slots[i];','currComp = !_grSysMode && i === 3 && acidPrefixGroups.length === 3 ? acidPrefixGroups[1].label : _slots[i];')
  if n==11:b+='    if (!_grSysMode && i === 3 && acidPrefixGroups.length === 3) {\n'+a.split('    if (i === 3 && acidPrefixGroups.length === 3) {\n',1)[1]
  if n==12:b=b.replace('if (i === 3 && displayComp === currComp) {','if (i === 3 && displayComp === currComp &&\n        !(typeof fScenarioUseLegacyNameBoxes === "function" && fScenarioUseLegacyNameBoxes())) {')
  return b
 return a
s=re.sub(r'^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n',resolve,s,flags=re.S|re.M)
def section(t,a,b):return t[t.index(a):t.index(b,t.index(a))]
def replace_section(t,a,b,v):return t[:t.index(a)]+v+t[t.index(b,t.index(a)):]
# Preserve local atom-anchored numbering; the shared font/fixed-C-C calibration
# already uses the effective applet scale, so a second overlay compensation
# would count the same factor twice.
s=replace_section(s,'function fShowNumbering(time,','// ── fNumberingTimeout',section(local,'function fShowNumbering(time,','// ── fNumberingTimeout')) if '// ── fNumberingTimeout' in local else s
# Build acceptance from the bounded local acquisition transaction, adopting
# the upstream single-slot/fork derivation and source/oracle/save-all metadata.
a=section(local,'async function fMolDraftAccept()','// Edit-entry visual state:')
u=section(up,'async function fMolDraftAccept()','// Edit-entry visual state:')
a=a.replace('if (!d.pubchem || !d.sdf3D) {','if (!d.sdf3D) {').replace('fMolDraftT("acceptNeedsPubChem3D", "Acceptance requires a PubChem record with 3D — coming back with RDKit.")','fMolDraftT("acceptNeeds3D", "Acceptance requires a 3D model.")')
a=a.replace('  // RDKit TODO: without local 3D generation, only PubChem-3D molecules are\n  // acceptable. Pending fetch -> wait; confirmed-missing -> blocked, stay in\n  // draft. Revisit when ETKDG lands (generate locally, then accept).','  // Every source is graph-checked; provisional geometry requires confirmation.')
a=a.replace('  d.accepting = true;\n',section(u,'  // Edit-different confirm:','  d.accepting = true;')+'  d.accepting = true;\n',1)
a=a.replace('  // Freshness:', '  var _myEpochA = d._epoch, _mySidA = d._submitId;\n  // Freshness:',1)
a=a.replace('      ((typeof selectedMol', '      d._epoch === _myEpochA && d._submitId === _mySidA &&\n      ((typeof selectedMol',1)
a=a.replace('  // Condensed/expanded preserve the drawn slot; skeletal is generated on\n  // acceptance, including skeletal edits. Generator gaps retain the drawing.','  // Same-identity edits replace only their edited slot; forks generate all forms.')
a=a.replace('      var a = fParseMolV2000(d.molText), b = fParseMolV2000(text);','      if (!text) return false;\n      text = String(text).replace(/\\[C\\]/g, "C  ");\n      var a = fParseMolV2000(d.molText), b = fParseMolV2000(text);',1)
a=replace_section(a,'  var molC = null, molE = null, molS = null;','  // Input once;',section(u,'  var molC = null, molE = null, molS = null;','  // Stray-H guard')+section(u,'  // Stray-H guard','  }  // SMILES-to-MOL').replace('  if (d && d.mode === "edit"','  if (isUpdate && d && d.mode === "edit"')+'  }\n')
a=replace_section(a,'  var _vc = {','  fMolDraftTeardownDisplay();',section(u,'  var _vc = {','  fMolDraftTeardownDisplay();'))
a=a.replace('  rec.structure2D_Condensed = molC;','  if (!liveDraft()) return;\n  rec.structure2D_Condensed = molC;',1)
# Confirmation callbacks cannot reacquire before the transaction finally runs.
a=a.replace('d._forkConfirmed = true;','d._forkConfirmed = true;').replace('d._strayConfirmed = true; d.accepting = false;','d._strayConfirmed = true; d.accepting = false;')
s=replace_section(s,'async function fMolDraftAccept()','// Edit-entry visual state:',a)
s=s.replace('spt/init-3.spt','spt/init-54.spt')
(C/'js/mulermoc-nom-molview-55.js').write_text(s)
print('resolved',n,'conflicts;',len(s),'bytes')
