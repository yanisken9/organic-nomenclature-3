var _modelName='original';
function fMolDraftReadBackSDF(){_reads.push(_modelName);return 'candidate';}
function fMolDraftMeanDisplacement(){return 0;}
function fJSmolScript(a,c){_writes.push(_modelName+':'+c);return '';}
var wrong=mol([atom('C',0,0),atom('N',1,0,1),atom('O',2,1,0)],[[1,2,1],[2,3,1]]);
var methane=mol([atom('C',0,0)],[]);
assert(fMolDraftValidSDF3D(wrong,3),'before mismatch did not reproduce');
assert(!fMolDraftValidSDF3D(methane,1),'before methane failure did not reproduce');
var p=fMolDraftLocal3DRelaxBoth(3);drainMicrotasks();_modelName='replacement';settle(p);
assert(_reads.indexOf('replacement')>=0&&_writes.some(function(c){return /replacement:.*UFF/.test(c);}), 'before stale UFF failure did not reproduce');
print(JSON.stringify({reproduced:['CV55-04 wrong identity same heavy count accepted','CV55-06 one-heavy methane rejected','VV55-01 replacement read and UFF fired after first wait'],writes:_writes,reads:_reads}));

function fMolDraft3DInvalidate() {}
function fJSmolScriptEcho(){return _model;}
var calls=0;
fMolDraftLocal3DFromMol=async function(){calls++;return {sdf:null,prepared:false};};
fMolDraftMinimizeDialog=function(msg,cb){cb();};
reset();window.MulerDraft.sdf3D=fixture();window.MulerDraft.sdf3DSource='jsmol-unminimized';settle(fMolDraftManualMinimize());assert(calls===0,'before retry failure did not reproduce');
reset();settle(fMolDraftManualMinimize());assert(window.MulerDraft.sdf3DSource==='jsmol-unminimized'&&!window.MulerDraft.sdf3DStatus&&!window.MulerDraft.sdf3DProvenance,'before durable status gap did not reproduce');
print(JSON.stringify({reproduced:['VV55-02 existing provisional SDF prevents visible manual retry','CV55-05 explicit manual OK stores fallback without durable provisional status'],source:window.MulerDraft.sdf3DSource,status:window.MulerDraft.sdf3DStatus||null}));
