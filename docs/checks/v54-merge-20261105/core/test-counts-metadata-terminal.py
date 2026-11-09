"""Exact session-baseline/current/upstream V2000 and school-layout checks.
Stdlib + macOS JSC; output stays in this directory; C101 is parser-only.
"""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PRIMARY=Path('/Users/yannisskendros/Desktop/Διπλωματική - Ονοματολογία/organic-nomenclature-3')
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
BODY=r'''
function profile(m){return m&&{head:m.head,countsTail:m.countsTail,atoms:m.atoms.map(a=>[a.el,a.x,a.y,a.z,a.charge,a.isotope,a.massDifference,a.radical,a.parity,a.hydrogenCount,a.valence,a.sourceIndex]),bonds:m.bonds.map(b=>[...b,(b.tail||'').trim(),b.sourceIndex]),properties:m.properties&&m.properties.map(p=>/^M  SBV/.test(p)?p.trim().split(/\s+/).slice(0,4).join(' '):p)}}
function short(t){const l=t.split(/\r?\n/);l.splice(0,1);return l.join('\n')}
function source(types,bonds,atoms){return fWriteMolV2000(['fixture','program',''],types.map((el,i)=>Object.assign({el,x:i*1.17,y:0},atoms&&atoms[i])),bonds)}
function angle(m,center){if(!m)return null;const c=m.atoms[center-1],ns=m.bonds.filter(b=>b[0]===center||b[1]===center).map(b=>m.atoms[(b[0]===center?b[1]:b[0])-1]);if(ns.length!==2)return null;
 const a=ns[0],b=ns[1],u=[a.x-c.x,a.y-c.y],v=[b.x-c.x,b.y-c.y];return Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/(Math.hypot(...u)*Math.hypot(...v)))))*180/Math.PI}
const t=source(['C','C','C'],[[1,2,1],[2,3,1]]),l=t.split('\n');
const invalidBond=l.slice();invalidBond[8]='  2  4  1  0  0  0';
const invalidSelf=l.slice();invalidSelf[8]='  2  2  1  0  0  0';
const invalidOrder=l.slice();invalidOrder[8]='  2  3  0  0  0  0';
const truncated=l.slice(0,8).join('\n');
const partialBody=l.slice(0,5).join('\n');
const badCoordinate=l.slice();badCoordinate[4]='       NaN'+badCoordinate[4].slice(10);
const blankElement=l.slice();blankElement[4]=blankElement[4].slice(0,31)+'   '+blankElement[4].slice(34);
const missingEnd=l.filter(x=>x!=='M  END').join('\n');
const invalidCharge=t.replace('M  END','M  CHG  1   9   1\nM  END');
const invalidAtomCount=l.slice();invalidAtomCount[3]=' 3x'+invalidAtomCount[3].slice(3);
const missingBondCount=l.slice();missingBondCount[3]=missingBondCount[3].slice(0,3)+'   '+missingBondCount[3].slice(6);
const invalids={invalidBond:invalidBond.join('\n'),invalidSelf:invalidSelf.join('\n'),invalidOrder:invalidOrder.join('\n'),truncated,partialBody,badCoordinate:badCoordinate.join('\n'),blankElement:blankElement.join('\n'),missingEnd,invalidCharge,invalidAtomCount:invalidAtomCount.join('\n'),missingBondCount:missingBondCount.join('\n')};
const invalid=Object.fromEntries(Object.entries(invalids).map(([k,v])=>[k,{standard:!!fParseMolV2000(v),short:!!fParseMolV2000(short(v))}]));
const standard=fParseMolV2000(t),shortParsed=fParseMolV2000(short(t));
const normalized=shortParsed&&fWriteMolV2000(shortParsed.head,shortParsed.atoms,shortParsed.bonds,shortParsed);
const contiguous=source(Array(101).fill('C'),Array.from({length:100},(_,i)=>[i+1,i+2,1]));
const big=fParseMolV2000(contiguous),bigShort=fParseMolV2000(short(contiguous));
const countLocators=typeof fMolCountsLine==='function'?{
 standard:fMolCountsLine(t.split('\n')),short:fMolCountsLine(short(t).split('\n')),
 contiguous:fMolCountsLine(contiguous.split('\n')),lastBounded:fMolCountsLine(Array(7).fill('').concat([l[3]])),
 beyondBound:fMolCountsLine(Array(8).fill('').concat([l[3]])),
 malformed:fMolCountsLine([invalidAtomCount[3]]),missingField:fMolCountsLine([missingBondCount[3]]),
 v3000:fMolCountsLine([l[3].replace('V2000','V3000')]),
 legacy:fMolCountsLine(['legacy','','',l[3].replace('V2000','')]),
 legacyShort:fMolCountsLine(['legacy','',l[3].replace('V2000','')])}:null;
const empty=source([],[]),legacyStored=fParseMolV2000(actualLegacySDF);
const nitro=window.MOL2D.nitroethane.expanded,metadata={};
for(const [kind,text]of Object.entries({standard:nitro,short:short(nitro),isotope:source(['C','O'],[[1,2,1]],[{isotope:13},{charge:-1}])})){
 const m=fParseMolV2000(text),out=m&&fWriteMolV2000(m.head,m.atoms,m.bonds,m),back=out&&fParseMolV2000(out);
 metadata[kind]={parsed:!!m,charges:m&&m.atoms.map(a=>a.charge),isotopes:m&&m.atoms.map(a=>a.isotope),properties:m&&m.properties,
  roundtrip:!!back&&JSON.stringify(profile(m))===JSON.stringify(profile(back))};
}
const parity=source(['C'],[],[{tail:' 0  0  1  0  0  0  0  0  0  0  0  0'}]),wedge=[1,2,1];wedge.tail='  1  0  0';
const stereo={parityParsed:!!fParseMolV2000(parity),parityRejected:fLinearizeMol(parity,[1])===null,
 wedgeParsed:!!fParseMolV2000(source(['C','F'],[wedge])),wedgeRejected:fLinearizeMol(source(['C','F'],[wedge]),[1])===null};
const nitriles=[];
for(const [types,bonds,center,chains]of [
 [['C','C','N'],[[1,2,1],[2,3,3]],2,[[1,2],[2,1]]],
 [['N','C','C'],[[1,2,3],[2,3,1]],2,[[3,2],[2,3]]]]){
 const text=source(types,bonds);
 for(const chain of chains)for(const [header,input]of [['standard',text],['short',short(text)]]){
  const result=fParseMolV2000(fLinearizeMol(input,chain));nitriles.push({types,chain,header,angle:angle(result,center),bondsPreserved:!!result&&JSON.stringify(result.bonds)===JSON.stringify(bonds)});
 }
}
const terminal=[];
for(const [types,bonds,chain]of [
 [['C','C','O','O'],[[1,2,1],[1,3,2],[1,4,1]],[1,2]],
 [['C','C','O','O'],[[1,2,1],[1,3,2],[1,4,1]],[2,1]],
 [['C','C','O','C'],[[1,2,1],[2,3,1],[3,4,1]],[1,2]],
 [['C','C','O','C'],[[1,2,1],[2,3,1],[3,4,1]],[2,1]]]){
 const result=fParseMolV2000(fLinearizeMol(source(types,bonds),chain));terminal.push({types,chain,points:result&&result.atoms.map(a=>[a.x,a.y]),etherAngle:types[3]==='C'?angle(result,3):null});
}
allAtomsTypeList=['C','C','C'];bondList=[[1,2,1],[2,3,1]];
const horizontal={};for(const [header,text]of [['standard',t],['short',short(t)]]){
 jsmeNomeclatureApplet={molFile:()=>text};horizontal[header]=fHorizontalEquivalentIndex([{chain:[1,2,3]}],[1,2,3]);
}
return {standard:!!standard,short:!!shortParsed,shortAtoms:shortParsed&&shortParsed.atoms.length,normalizedCountsIndex:normalized&&normalized.split('\n').findIndex(v=>v.includes('V2000')),
 contiguous101100:{prefix:contiguous.split('\n')[3].slice(0,6),standard:big&&[big.atoms.length,big.bonds.length],short:bigShort&&[bigShort.atoms.length,bigShort.bonds.length],namingTested:false},
 empty:{standard:!!fParseMolV2000(empty),short:!!fParseMolV2000(short(empty))},
 legacy:{standard:!!fParseMolV2000(t.replace('V2000','')),v3000:!!fParseMolV2000(t.replace('V2000','V3000')),storedPentyn:legacyStored&&[legacyStored.atoms.length,legacyStored.bonds.length]},countLocators,invalid,metadata,stereo,nitriles,terminal,horizontal};
'''
prefix='var window={},selectedMol,mode2D,mainChainMode,jsmeNomeclatureApplet,console={log(){},warn(){},error(){}};\n'
data=(ROOT/'js/jsme-nick-nomeclature-moc2-data_54.js').read_text()
data+='\nconst actualLegacySDF='+json.dumps((ROOT/'mols/nomeclature-moc2/pentyn_4_one_2_3D.sdf').read_text())+';\n'
paths={'before':HERE/'before-core54.js','after':ROOT/'js/mulermoc-nom-core-54.js','upstream':PRIMARY/'docs/checks/v54-merge-20261105/upstream-target/js/mulermoc-nom-core-54.js'}
sources={k:p.read_text() for k,p in paths.items()}
script=''.join('const '+k+'=new Function('+json.dumps(prefix+data+'\n'+s+'\n'+BODY)+');\n'for k,s in sources.items())+'print(JSON.stringify({before:before(),after:after(),upstream:upstream()}));'
r=subprocess.run([JSC,'-e','eval(JSON.parse(readline()))'],input=json.dumps(script)+'\n',text=True,capture_output=True)
assert r.returncode==0,(r.stdout[-4000:],r.stderr[-2000:])
result=json.loads(r.stdout)
(HERE/'counts-metadata-terminal-raw.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
# Session baseline establishes the original short-header failure; raw upstream
# establishes why replacing the strict local parser/sp handling is unsafe.
a,b,u=result['after'],result['before'],result['upstream']
assert b['standard'] and b['shortAtoms']!=3 # baseline may misread first zero coordinate as zero counts
assert a['standard'] and a['short'] and a['normalizedCountsIndex']==3
assert a['empty']=={'standard':True,'short':True}
assert a['legacy']=={'standard':True,'v3000':False,'storedPentyn':[12,11]}
assert b['legacy']['storedPentyn']==[12,11] and u['legacy']['storedPentyn'] is None
assert a['contiguous101100']['prefix']=='101100'
assert a['contiguous101100']['standard']==[101,100] and a['contiguous101100']['short']==[101,100]
assert u['contiguous101100']['standard'] is None
assert a['countLocators']=={'standard':3,'short':2,'contiguous':3,'lastBounded':7,'beyondBound':-1,'malformed':-1,'missingField':-1,'v3000':-1,'legacy':3,'legacyShort':-1}
assert all(not row['standard'] and not row['short'] for row in a['invalid'].values())
assert u['invalid']['invalidBond']['standard']
assert all(row['parsed'] and row['roundtrip'] for row in a['metadata'].values())
assert a['metadata']['standard']['charges'].count(1)==1 and a['metadata']['standard']['charges'].count(-1)==1
assert len(a['metadata']['standard']['properties'])==6
assert a['metadata']['short']['properties']==a['metadata']['standard']['properties']
assert a['metadata']['isotope']['isotopes'][0]==13
assert a['stereo']=={'parityParsed':True,'parityRejected':True,'wedgeParsed':True,'wedgeRejected':True}
assert all(abs(row['angle']-180)<0.0001 and row['bondsPreserved'] for row in a['nitriles'])
assert all(abs(row['angle']-180)>1 for row in u['nitriles'])
assert a['horizontal']=={'standard':0,'short':0} and b['horizontal']=={'standard':0,'short':-1}
for row in a['terminal'][:2]:
 anchor=row['points'][0][0];other=row['points'][1][0];
 assert all((p[0]-anchor)*(anchor-other)>0 for p in row['points'][2:])
assert all(abs(row['etherAngle']-180)<0.0001 for row in a['terminal'][2:])
# Verify every pre-existing top-level function outside the approved three is
# byte-identical, including fZigzagMol and all naming/map/locant safeguards.
def functions(s):
 matches=list(re.finditer(r'^function ([\w$]+)\(',s,re.M))
 return {m.group(1):s[m.start():matches[i+1].start() if i+1<len(matches) else len(s)] for i,m in enumerate(matches)}
bf,af=functions(sources['before']),functions(sources['after'])
# New helper is inserted after a comment attached to fTranslateChain2D3D in this
# lexical slice, so compare that function's executable portion separately.
allowed={'fHorizontalEquivalentIndex','fParseMolV2000','fLinearizeMol','fTranslateChain2D3D'}
unchanged=[k for k in bf if k not in allowed]
assert all(bf[k]==af[k] for k in unchanged)
assert bf['fTranslateChain2D3D'].split('// ── 2D-variant')[0]==af['fTranslateChain2D3D'].split('// ── 2D-variant')[0]
result['verification']={'checksPassed':True,'strictInvalidCases':len(a['invalid'])*2,'terminalSpDirectionsAndHeaders':len(a['nitriles']),
 'unchangedTopLevelFunctions':len(unchanged),'fZigzagMolByteIdentical':bf['fZigzagMol']==af['fZigzagMol'],'operatingConditions':'actual macOS JavaScriptCore; no browser',
 'sourceSHA256':{k:hashlib.sha256(p.read_bytes()).hexdigest()for k,p in paths.items()}}
(HERE/'counts-metadata-terminal-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['verification'],ensure_ascii=False,indent=2))
