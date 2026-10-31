var a={},frames=new Map(),timers=new Map(),next=0,counts={A:0,B:0,page:0,newA:0},cancelledFrames=[],cancelledTimers=[];
function requestAnimationFrame(fn){var id=++next;frames.set(id,fn);return id}
function cancelAnimationFrame(id){cancelledFrames.push(id);frames.delete(id)}
function setTimeout(fn){var id=++next;timers.set(id,fn);return id}
function clearTimeout(id){cancelledTimers.push(id);timers.delete(id)}
function assert(ok,message){if(!ok)throw Error(message)}
eval(readFile('/tmp/namelecule-jsmol-lifecycle-prototype-20261031/lifecycle-helper.js'));
var life=a._nameleculeLifecycle,A={_id:'A',_appletPanel:{}},B={_id:'B',_appletPanel:{}};
a.repaint=function(applet){counts[applet._id]++};
life.paint(A,A._appletPanel,true,function(){counts.A++});var stale=[...frames.values()][0];
life.paint(B,B._appletPanel,true,function(){counts.B++});requestAnimationFrame(function(){counts.page++});life.resize(A);life.resize(B);
life.dispose(A);assert(cancelledFrames.length===1,'only owned A frame cancelled');assert(cancelledTimers.length===1,'only owned A timer cancelled');stale();
for(var fn of [...frames.values()])fn();for(var fn of [...timers.values()])fn();
assert(counts.A===0&&counts.B===2&&counts.page===1,'B and page work survives; stale A cannot draw');
life.resize(A);life.paint(A,A._appletPanel,false,function(){counts.A++});assert(counts.A===0&&!life.live(A),'destroyed owner cannot schedule new work');
var newA={_id:'A',_appletPanel:{}};life.paint(newA,newA._appletPanel,false,function(){counts.newA++});assert(counts.newA===1,'new object with same id is live');
var source=readFile('/tmp/namelecule-jsmol-lifecycle-prototype-20261031/vendor-candidate/JSmol.min.js'),start=source.indexOf('a.repaint=function(b,c){'),end=source.indexOf(';a.loadImage=',start);eval(source.slice(start,end));
var dimensions=0,draws=0,C={_id:'C',_appletPanel:{setScreenDimension:function(){dimensions++},update:function(){draws++}}};a.$=function(){return {width:function(){return 400},height:function(){return 300}}};
a.repaint(C,false);assert(dimensions===1&&draws===1,'live sync paint preserved');life.dispose(C);a.repaint(C,false);assert(dimensions===1&&draws===1,'entry after dispose cannot access panel');
var D={_id:'D',_appletPanel:{setScreenDimension:function(){throw Error('dimension touched after reentrant close')}}};a.$=function(){return {width:function(){life.dispose(D);return 400},height:function(){return 300}}};a.repaint(D,false);
print(JSON.stringify({passed:true,ownedCancellation:true,otherOwnerAndPageSurvive:true,lateCallbackGuard:true,newObjectSameID:true,liveSyncPaint:true,postDestroyEntry:true,reentrantCloseDuringMeasure:true,counts:counts}));
