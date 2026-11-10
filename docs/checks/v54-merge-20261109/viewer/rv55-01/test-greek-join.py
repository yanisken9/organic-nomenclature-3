from pathlib import Path
import re,json,subprocess,hashlib,datetime
P=Path.cwd();E=P/'docs/checks/v54-merge-20261109/viewer/rv55-01';C=Path('/private/tmp/namelecule-professor-merge-20261109-oxj7hfyy/candidate');V=C/'js/mulermoc-nom-molview-55.js';J='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
baseline=E/'before-viewer55.js'
before=baseline.read_text() if baseline.exists() else V.read_text()
if not baseline.exists():baseline.write_text(before)
start=before.index('function fJoinGreekSysName(slots) {');end=before.index('function fShowNameAnalysis()',start)
section=before[start:end]
fixed=section.replace('    var _parts = slots.filter(function (c) { return c != null && c !== \'\'; });\n','',1).replace('_jpre.slice(3).join("-")','_jpre.slice(3).join("")',1).replace('    return _join(_parts);','    return _join(slots.filter(function (c) { return c != null && c !== \'\'; }));',1)
assert fixed!=section
staged=before[:start]+fixed+before[end:]
S=Path('/private/tmp/namelecule-viewer-rv55-01-staged.js');S.write_text(staged)
(E/'rv55-01.patch').write_bytes(subprocess.run(['git','diff','--no-index','--',str(V),str(S)],capture_output=True).stdout)
def function_sections(s):
 m=list(re.finditer(r'^(?:async )?function (\w+)\(',s,re.M))
 return {x.group(1):s[x.start():m[i+1].start() if i+1<len(m) else len(s)] for i,x in enumerate(m)}
def helpers(src):
 fs=function_sections(src);keys=['fGRSystOneStem','fGRSysNeedsParens','fSystematicGRSubstSlot','fGreekSysSlots','fSysFusedPieces','fJoinGreekSysName','fSplitBranchPieces','fGRSubstSortKey','fGRLocKey','fGRSubstGroups','fGRSortSubstGroups'];return src[src.index('var GR_SYST_SUBST ='):src.index('function fGRSystOneStem(')]+'\n'+'\n'.join(fs[k] for k in keys)
# The panel prefix is executed directly from fShowNameAnalysis with a box
# recorder. Rendering/DOM is mocked; ordering, text, IDs and common provenance
# come from the actual unchanged panel section and its exact dependencies.
panel=before[before.index('  var _preHTML = "";',before.index('function fShowNameAnalysis()')):before.index('  const acidPrefixGroups',before.index('function fShowNameAnalysis()'))]
panel_fn='''function panelPrefix(slots) {var rows=[];function fNameCompBox(id,cls,text,tip){rows.push({id:id,text:text,tip:tip||null});return "";}var _grSysMode=true,_slots=slots,_grTipPre="Common: ",_grSchoolFull=currentMolName,boxClass="box",crossClass="cross",compCount=slots.length;'''+panel+'\nreturn rows;}\n'
load='''function loadMol(text){const lines=text.split(/\\r?\\n/),n=+lines[3].slice(0,3),b=+lines[3].slice(3,6),aa=lines.slice(4,4+n).map(l=>({label:l.slice(31,34).trim()})),bb=lines.slice(4+n,4+n+b).map(l=>({atoms:[+l.slice(0,3),+l.slice(3,6)],order:+l.slice(6,9)}));jsmeNomeclatureApplet={totalNumberOfAtoms:()=>n,totalNumberOfBonds:()=>b,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1],molFile:()=>text};fAnalyseStructure();fDetectMolType();fInitNamingProps();fGuessName();}'''
base='var window={},console={log(){},warn(){},error(){}},selectedMol,mode2D="condensed",mainChainMode="algorithmic",jsmeNomeclatureApplet;\n'+(C/'js/jsme-nick-nomeclature-moc2-data_55.js').read_text()+'\n'+(C/'js/mulermoc-nom-core-55.js').read_text()+'\n'+load+'\n'
tail='''
var rows=[];
function capture(label,common,expected,prefixIDs,ester){
  if(common){nameComponentsList=common.slice();currentMolName=common.filter(x=>x!=null).join("");functionalGroupsList=ester?["ester"]:[];}
  var original=JSON.stringify(nameComponentsList),sys=fGreekSysSlots()||nameComponentsList.slice(),sysBefore=JSON.stringify(sys),joined=fJoinGreekSysName(sys),prefix=panelPrefix(sys),suffix=sys.slice(4).filter(x=>x!=null&&x!=="").join("");
  var groups=fGRSubstGroups(sys,nameComponentsList),provenanceCorrect=prefix.every(row=>{var group=groups.find(g=>g.nameId===row.id);return row.tip===(group&&group.name!==group.com?"Common: "+currentMolName:null);});
  rows.push({label:label,common:nameComponentsList.slice(),systematicSlots:sys,expected:expected,joined:joined,panelPrefix:prefix,panelJoined:prefix.length?prefix.map(x=>x.text).join("")+suffix:null,inputUnchanged:JSON.stringify(nameComponentsList)===original&&JSON.stringify(sys)===sysBefore,expectedIDs:prefixIDs,provenanceCorrect:provenanceCorrect,pass:provenanceCorrect&&joined===expected&&JSON.stringify(nameComponentsList)===original&&JSON.stringify(sys)===sysBefore&&(!prefixIDs||JSON.stringify(prefix.map(x=>x.id))===JSON.stringify(prefixIDs))&&(!prefix.length||prefix.map(x=>x.text).join("")+suffix===joined)});
}
selectedMol='isopropyl_4_dimethyl_3_5_heptanol_2';loadMol(window.MOL2D[selectedMol].condensed);
capture('actual library: isopropyl+dimethyl',null,'3,5-διμεθυλο-4-(προπαν-2-υλο)-2-επτανόλη',['comp2','comp3','comp0','comp1']);
var common=nameComponentsList.slice();common[2]='-3-';common[3]='μεθυλο-5-αιθυλο';capture('three substituents: ethyl methyl propan-2-yl',common,'5-αιθυλο-3-μεθυλο-4-(προπαν-2-υλο)-2-επτανόλη',['comp3loc','comp3b','comp2','comp3','comp0','comp1']);
var single=common.slice();single[2]='';single[3]='';capture('single transformed substituent retains parenthesization',single,'4-(προπαν-2-υλο)-2-επτανόλη',null);
var identity=single.slice();identity[1]='μεθυλο';capture('unchanged simple branch keeps common text',identity,'4-μεθυλο-2-επτανόλη',null);
var ester=['','','','',null,'προπ','αν','ικ','ός',null,'ισοπροπυλ','εστέρας'];capture('ester two-word boundary unchanged',ester,'προπανικός προπαν-2-υλεστέρας',null,true);
return {cases:rows.length,passed:rows.filter(x=>x.pass).length,rows:rows};
'''
outputs={}
naive=staged.replace('_jpre.slice(3).join("")','_jpre.slice(3).join("-")',1)
for label,source in [('before',before),('naive-refresh-only',naive),('after',staged)]:
 harness='var run = new Function('+json.dumps(base+helpers(source)+panel_fn+tail,ensure_ascii=True)+');print(JSON.stringify(run()));'
 path=E/(label+'-probe.js');path.write_text(harness)
 result=subprocess.run([J,path.name],cwd=E,capture_output=True,text=True)
 (E/(label+'-output.txt')).write_text(result.stdout+result.stderr)
 if result.returncode:raise SystemExit(result.stdout+result.stderr)
 outputs[label]=json.loads(result.stdout);(E/(label+'-results.json')).write_text(json.dumps(outputs[label],indent=2,ensure_ascii=False)+'\n')
fs_before=function_sections(before);fs_after=function_sections(staged);changed=[k for k in fs_before if fs_before[k]!=fs_after[k]];assert changed==['fJoinGreekSysName'],changed
unrelated={k:hashlib.sha256(v.encode()).hexdigest() for k,v in fs_before.items() if k!='fJoinGreekSysName'}
report={'timestampUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'finding':'RV55-01','scope':'Only fJoinGreekSysName changes; panel/group IDs and all other function sections byte unchanged','baseSHA256':hashlib.sha256(before.encode()).hexdigest(),'stagedSHA256':hashlib.sha256(staged.encode()).hexdigest(),'stagedPath':str(S),'candidateUnchangedUntilPrimaryRelease':True,'candidateSHA256':hashlib.sha256(V.read_bytes()).hexdigest(),'changedFunctions':changed,'unrelatedFunctionHashes':unrelated,'before':outputs['before'],'naiveRefreshOnly':outputs['naive-refresh-only'],'after':outputs['after'],'limitation':'Actual naming/core/panel-prefix functions run in JavaScriptCore; browser DOM rendering and independent targeted review remain primary responsibilities.'}
(E/'targeted-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'before':{k:outputs['before'][k]for k in ['cases','passed']},'after':{k:outputs['after'][k]for k in ['cases','passed']},'changedFunctions':changed,'unrelatedFunctionSectionsUnchanged':len(unrelated),'baseSHA256':report['baseSHA256'],'stagedSHA256':report['stagedSHA256']},ensure_ascii=False,indent=2))
assert outputs['after']['passed']==outputs['after']['cases']
