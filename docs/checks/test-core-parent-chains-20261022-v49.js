// Run from repository root with JavaScriptCore jsc (provides readFile).
// Real core and MOL data; only JSME's atom/bond API is mocked.
const key = 'ethyl_3_dimethyl_2_5_hexane';
const dataSource = readFile('js/jsme-nick-nomeclature-moc2-data_49.js');
const coreSource = readFile('js/mulermoc-nom-core-49.js');
const sdf = readFile('mols/nomeclature-moc2/' + key + '_3D.sdf');
const run = new Function('fixture', 'sdfText', `
    var window = {}, console = {log:function(){},warn:function(){},error:function(){}};
    var selectedMol='${key}', mode2D='condensed', mainChainMode='algorithmic', etherNamingMode='iupac';
    ${dataSource}
    var MOL2D = window.MOL2D;
    ${coreSource}
    const text = fixture || MOL2D[selectedMol].condensed;
    const lines = text.split('\\n');
    const na=Number(lines[3].slice(0,3)), nb=Number(lines[3].slice(3,6));
    const aa=lines.slice(4,4+na).map(x=>({label:x.slice(31,34).trim()}));
    const bb=lines.slice(4+na,4+na+nb).map(x=>({atoms:[Number(x.slice(0,3)),Number(x.slice(3,6))],order:Number(x.slice(6,9))}));
    var jsmeNomeclatureApplet={totalNumberOfAtoms:()=>na,totalNumberOfBonds:()=>nb,getAtom:(m,i)=>aa[i-1],getBond:(m,i)=>bb[i-1]};
    fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
    const initialName=nameComponentsList.filter(Boolean).join('');
    const variants=mainChainPool.map(p=>{
        mainChainAtomsList=p.chain.slice();fGuessName(true);
        return {chain:p.chain,name:nameComponentsList.filter(Boolean).join('')};
    });
    fParseSDF3D(sdfText || text);fDetectMolType3D();fCalcMainChain3D();
    return {initialName, variants, branches3D:mainChainPool3D.map(p=>fCarbonBranchLocants(p.chain.map(x=>x-1),atomConnectivityList3D,allAtomsTypeList3D))};
`);
function assert(value,msg){if(!value)throw Error(msg);}
function validate(result){
    assert(result.initialName==='3-αιθυλο-2,5-διμεθυλοεξάνιο','initial name');
    assert(result.variants.length===4,'keep four equivalent parent paths');
    assert(result.variants.every(v=>v.name===result.initialName),'all paths same preferred name');
    assert(result.branches3D.length===4,'four 3D paths');
    assert(result.branches3D.every(v=>JSON.stringify(v)==='[2,3,5]'),'3D locants');
}
validate(run(null,sdf));
// Renumber carbon atoms and reverse bond order; the result must depend on the
// graph, not the original atom indices or which branch DFS visits first.
var window=this;load('js/jsme-nick-nomeclature-moc2-data_49.js');
const original=MOL2D[key].condensed.split('\n');
function permute(order,reverseBonds){
    const remap={};order.forEach((old,i)=>remap[old]=i+1);
    const atoms=order.map(old=>original[3+old]);
    let bonds=original.slice(14,23).map(b=>String(remap[Number(b.slice(0,3))]).padStart(3)+String(remap[Number(b.slice(3,6))]).padStart(3)+b.slice(6));
    if(reverseBonds)bonds.reverse();
    return original.slice(0,4).concat(atoms,bonds,['M  END','']).join('\n');
}
let seed=21;
for(let i=0;i<20;i++){
    const order=Array.from({length:10},(_,j)=>j+1);
    for(let j=9;j>0;j--){seed=(seed*1664525+1013904223)>>>0;const k=seed%(j+1);[order[j],order[k]]=[order[k],order[j]];}
    validate(run(permute(order,i%2===1),null));
}
function graphMol(n,edges){
    const atoms=Array.from({length:n},()=>"    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0");
    return 'fixture\n  Test 2D\n\n'+String(n).padStart(3)+String(edges.length).padStart(3)+'  0  0  0  0  0  0  0  0999 V2000\n'+atoms.join('\n')+'\n'+edges.map(e=>e.map(x=>String(x).padStart(3)).join('')+'  0  0  0  0').join('\n')+'\nM  END\n';
}
for(const test of [
    [8,[[1,2,1],[2,3,2],[3,4,1],[4,5,1],[5,6,3],[6,7,1],[4,8,1]],'4-μεθυλο-2-επτεν-5-ίνιο'],
    [5,[[1,2,1],[2,3,1],[3,4,3],[2,5,1]],'3-μεθυλο-1-βουτίνιο'],
    [7,[[1,2,2],[2,3,1],[3,4,1],[4,5,3],[5,6,1],[3,7,1]],'3-μεθυλο-1-εξεν-4-ίνιο']
])assert(run(graphMol(test[0],test[1]),null).initialName===test[2],'multiple-bond priority regression');
print('PASS: PubChem 2D/3D, 20 atom/bond permutations, all parent paths, three unsaturation regressions.');
