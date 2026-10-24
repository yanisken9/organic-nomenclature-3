const data = readFile('js/jsme-nick-nomeclature-moc2-data_50.js');
const prior = readFile('/tmp/namelecule-horizontal-all-before/js/mulermoc-nom-core-50.js');
const current = readFile('js/mulermoc-nom-core-50.js');
const registry = new Function('var window={};'+data+';return Object.keys(nameExamples)')();
function runner(core) {
 return new Function('key','mode','sdf','chainMode',`var window={}, console={warn(){},log(){},error(){}},selectedMol=key,mode2D=mode,mainChainMode=chainMode || 'algorithmic',etherNamingMode='iupac';
 ${data}\n${core}
 const text=window.MOL2D[key][mode],lines=text.split('\\n'),n=Number(lines[3].slice(0,3)),nb=Number(lines[3].slice(3,6));
 const atoms=lines.slice(4,4+n).map(x=>({label:x.slice(31,34).trim()}));
 const bonds=lines.slice(4+n,4+n+nb).map(x=>({atoms:[Number(x.slice(0,3)),Number(x.slice(3,6))],order:Number(x.slice(6,9))}));
 var jsmeNomeclatureApplet={totalNumberOfAtoms:()=>n,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>atoms[i-1],getBond:(m,i)=>bonds[i-1],molFile:()=>text};
 fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
 const result={name:currentMolName,chain:mainChainAtomsList.slice(),pool:mainChainPool.map(p=>p.chain.slice()),index:mainChainPoolIdx};
 if(typeof fHorizontalEquivalentIndex==='function' && mainChainPool.length){
  const preferred=fHorizontalEquivalentIndex(mainChainPool,mainChainAtomsList);
  if(mainChainMode==='algorithmic' && preferred>=0 && preferred!==mainChainPoolIdx)throw Error('nonpreferred '+key+' '+mode);
  const selected=fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList);
  if(mainChainMode==='algorithmic' && selected!==fNumberedChainSignature(mainChainPool[0].chain,allAtomsTypeList,bondList))throw Error('chemistry changed '+key);
 }
 fParseSDF3D(sdf);fDetectMolType3D();fCalcMainChain3D();
 if(typeof fNumberedChainSignature==='function'){
  const a=fNumberedChainSignature(mainChainAtomsList,allAtomsTypeList,bondList);
  const b=fNumberedChainSignature(mainChainAtoms3D,allAtomsTypeList3D,bondList3D);
  result.signatureMatch=a===b;result.signatureApplicable=a!==null;result.debug={a,b,chain3:mainChainAtoms3D,pool:mainChainPool3D};
 }
 return result;`);
}
const before=runner(prior),after=runner(current);let rows=[],failures=[];
for(const chainMode of ['algorithmic','data'])for(const key of registry)for(const mode of ['condensed','expanded','skeletal']){
 try{
  const sdf=readFile('mols/nomeclature-moc2/'+key+'_3D.sdf');
  if(key==='methane' && mode==='skeletal')continue;
  const a=before(key,mode,sdf,chainMode),b=after(key,mode,sdf,chainMode);
  if(a.name!==b.name)failures.push({key,mode,problem:'name changed',before:a.name,after:b.name});
  if(JSON.stringify(a.pool)!==JSON.stringify(b.pool))failures.push({key,mode,problem:'pool reordered'});
  if(b.signatureApplicable&&!b.signatureMatch)failures.push({key,mode,problem:'3D signature mismatch',debug:b.debug});
  rows.push({key,mode,chainMode,before:a.chain,after:b.chain,name:b.name,signatureMatch:b.signatureMatch});
 }catch(e){failures.push({key,mode,problem:String(e)})}
}
print(JSON.stringify({rows,failures}));if(failures.length)throw Error(failures.length+' failures');
