"""Read-only JSC naming/registry/3D regression for six approved dienes."""
from pathlib import Path
import json,subprocess
cases=[('butadiene_1_3','1,3-βουταδιένιο',4),('butadiene_1_2','1,2-βουταδιένιο',4),('pentadiene_1_4','1,4-πενταδιένιο',5),('methyl_3_pentadiene_1_3','3-μεθυλο-1,3-πενταδιένιο',5),('dimethyl_2_3_pentadiene_1_3','2,3-διμεθυλο-1,3-πενταδιένιο',5),('ethyl_3_dimethyl_4_5_hexadiene_1_4','3-αιθυλο-4,5-διμεθυλο-1,4-εξαδιένιο',6)]
sources='\n'.join(Path(p).read_text() for p in ['js/jsme-nick-nomeclature-moc2-data_50.js','js/mulermoc-nom-core-50.js','js/mulermoc-nom-molview-50.js'])
body="var window={},console={log:function(){},warn:function(){},error:function(){}},document={getElementById:function(){return null},addEventListener:function(){}};"+sources+r'''
var MOL2D=window.MOL2D;selectedMol=key;mode2D=mode;mainChainMode=chainMode;
var text=MOL2D[key][mode],ls=text.split('\n'),na=Number(ls[3].slice(0,3)),nb=Number(ls[3].slice(3,6));
var aa=ls.slice(4,4+na).map(l=>({label:l.slice(31,34).trim()})),bb=ls.slice(4+na,4+na+nb).map(l=>({atoms:[Number(l.slice(0,3)),Number(l.slice(3,6))],order:Number(l.slice(6,9))}));
jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1]};
fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
fParseSDF3D(sdf);fDetectMolType3D();fCalcMainChain3D();
function orders(chain,bonds){return chain.slice(1).map((n,i)=>bonds.find(b=>(b[0]===n&&b[1]===chain[i])||(b[1]===n&&b[0]===chain[i]))[2]);}
return {name:currentMolName,series:fGetMoleculeClassification().seriesKey,chain:mainChainAtomsList,chain3:mainChainAtoms3D,two:orders(mainChainAtomsList,bondList),three:orders(mainChainAtoms3D,bondList3D)};
'''
js='var run=new Function("key","mode","chainMode","sdf",'+json.dumps(body)+');var rows=[];'
for key,expected,n in cases:
 for mode in ['condensed','expanded','skeletal']:
  for chain in ['algorithmic','data']:
   js+='rows.push('+json.dumps([key,expected,n,mode,chain])+'.concat([run('+','.join(json.dumps(x) for x in [key,mode,chain,Path('mols/nomeclature-moc2',key+'_3D.sdf').read_text()])+')]));'
js+='print(JSON.stringify(rows));'
r=subprocess.run(['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc','-e',js],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
for key,expected,n,mode,chain,result in json.loads(r.stdout):
 assert result['name']==expected,(key,mode,chain,result)
 assert result['series']=='alkadienes' and len(result['chain'])==n and len(result['chain3'])==n
 assert result['two']==result['three'],(key,mode,chain,result)
print('PASS36cases:approved names,alkadienes,2D/3D parent length and bond sequences')
