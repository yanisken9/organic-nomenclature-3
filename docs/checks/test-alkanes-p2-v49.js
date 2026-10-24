// Run from repository root:
// /System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc docs/checks/test-alkanes-p2-v49.js
// Regression expectations are the approved Greek names, never the known bugs.
// Execute the original data49/core49 unchanged; mock only JSME's graph API.
const dataSource = readFile('js/jsme-nick-nomeclature-moc2-data_49.js');
const coreSource = readFile('js/mulermoc-nom-core-49.js');
const run = new Function('fixture', `
    var window = {}, console = {log:function(){},warn:function(){},error:function(){}};
    var selectedMol='ethyl_3_dimethyl_2_5_hexane', mode2D='condensed', mainChainMode='algorithmic', etherNamingMode='iupac';
    ${dataSource}
    var MOL2D = window.MOL2D;
    ${coreSource}
    var jsmeNomeclatureApplet = {
        totalNumberOfAtoms:()=>fixture.n,
        totalNumberOfBonds:()=>fixture.edges.length,
        getAtom:(m,i)=>({label:'C'}),
        getBond:(m,i)=>({atoms:fixture.edges[i-1].slice(),order:1})
    };
    fInitNamingProps();fAnalyseStructure();fDetectMolType();fGuessName();
    const initialName=nameComponentsList.filter(Boolean).join('');
    const variants=mainChainPool.map(p=>{
        mainChainAtomsList=p.chain.slice();fGuessName(true);
        return {chain:p.chain.slice(),name:nameComponentsList.filter(Boolean).join('')};
    });
    return {initialName,variants};
`);

function chain(n) {
    return Array.from({length:n-1},(_,i)=>[i+1,i+2]);
}
const cases = [
    {id:'P2-1 straight propyl',n:13,
     edges:chain(10).concat([[5,11],[11,12],[12,13]]),
     expected:'5-προπυλοδεκάνιο'},
    {id:'P2-2 alphabetical numbering tie',n:10,
     edges:chain(7).concat([[5,8],[8,9],[3,10]]),
     expected:'3-αιθυλο-5-μεθυλοεπτάνιο',checkPaths:true},
    {id:'P2-3 branch locant/name pairing',n:16,
     edges:chain(10).concat([[2,11],[4,12],[12,13],[5,14],[14,15],[14,16]]),
     expected:'4-αιθυλο-5-ισοπροπυλο-2-μεθυλοδεκάνιο'}
];

// These are graph relabelings only: no chemistry or name calculation here.
function permute(test,order) {
    const remap={};order.forEach((old,i)=>remap[old]=i+1);
    return {n:test.n,edges:test.edges.map(e=>[remap[e[1]],remap[e[0]]]).reverse()};
}
let checks=0,failures=0;
function check(label,actual,expected) {
    checks++;
    if(actual===expected)print('PASS '+label);
    else {
        failures++;
        print('FAIL '+label+'\n  expected: '+expected+'\n  actual:   '+actual);
    }
}
function execute(test,label,fixture) {
    try {
        const result=run(fixture);
        check(label+' initial',result.initialName,test.expected);
        if(test.checkPaths) {
            check(label+' has parent paths',result.variants.length>0,true);
            result.variants.forEach((v,i)=>check(label+' path '+(i+1)+' ['+v.chain.join(',')+']',v.name,test.expected));
        }
    } catch(error) {
        check(label+' execution',String(error),'successful naming');
    }
}
cases.forEach(test=>{
    execute(test,test.id,test);
    if(test.checkPaths) {
        const reverse=Array.from({length:test.n},(_,i)=>test.n-i);
        const shuffled=[8,3,10,1,6,9,4,7,2,5];
        execute(test,test.id+' reversed atom/bond order',permute(test,reverse));
        execute(test,test.id+' shuffled atom/bond order',permute(test,shuffled));
    }
});
print('RESULT: '+failures+' failures / '+checks+' checks (original core49; all cases executed).');
// This macOS jsc ignores quit's argument; throw only after reporting every case.
if(failures)throw Error(failures+' alkane regression checks failed');
