var window=this, allAtomsTypeList=[],bondList=[],_geom={},_purpose='free',_target=[];
var MULER_SELECT_ATOM_R=.35,MULER_SELECT_BOND_HW=.2;
function fMulerSelectGeom(){return _geom;}
function fMulerSelectPurpose(){return _purpose;}
function fMulerQuizTargetSet(){return _target;}
function assert(v,m){if(!v)throw Error(m);}
function same(actual,expected){assert(JSON.stringify(actual)===JSON.stringify(expected),'expected '+JSON.stringify(expected)+', got '+JSON.stringify(actual));}
var results=[];
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function label(atom,x,y,w,h){return {atom:atom,x:x,y:y,w:w,h:h};}
function setup(){window.MulerQuizTarget=null;_target=[];_purpose='free';allAtomsTypeList=['C','C'];bondList=[[1,2,1]];_geom={med:750,groups:[{bond:0,lines:[{x1:4221,y1:2528,x2:4971,y2:2528}]}],anchors:[label(0,4385.966064453125,2586.3636474609375,330,290),label(1,5135.966064453125,2586.3636474609375,330,290)],comp:[],verts:[{x:4221,y:2528},{x:4971,y:2528}],vassign:[0,1]};}
test('measured condensed ethane midpoint selects actual C-C bond',function(){setup();same(fMulerSelectPick(4596,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('direct visible carbon label retains atom priority over bond corridor',function(){setup();same(fMulerSelectPick(4385.966064453125,2586.3636474609375),{kind:'atom',atom:1});});
test('wide visible formula label remains selectable beyond loose atom radius',function(){setup();_geom.anchors=[label(0,4385,2586,900,290)];same(fMulerSelectPick(4770,2586),{kind:'atom',atom:1});});
test('bond-purpose armed mission retains native bond endpoint result',function(){setup();window.MulerQuizTarget='compBondType';_purpose='bond';same(fMulerSelectPick(4596,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('parallel multiple-bond strokes retain their source bond identity',function(){setup();bondList=[[1,2,2]];_geom.groups[0].lines.push({x1:4221,y1:2590,x2:4971,y2:2590});same(fMulerSelectPick(4596,2590),{kind:'bond',bond:1,pair:[1,2]});});
test('diagonal bond corridor remains selectable between implicit vertices',function(){setup();_geom.anchors=[];_geom.groups[0].lines=[{x1:0,y1:0,x2:600,y2:600}];_geom.verts=[{x:0,y:0},{x:600,y:600}];same(fMulerSelectPick(300,300),{kind:'bond',bond:1,pair:[1,2]});});
test('main-chain armed mission ignores actual bond interior',function(){setup();window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';same(fMulerSelectPick(4596,2528),{ignore:true});});
test('FG atom-only mission ignores actual bond interior',function(){setup();window.MulerQuizTarget='compSuffix';_purpose='fg';same(fMulerSelectPick(4596,2528),{ignore:true});});
test('loose atom fallback remains available away from any bond or vertex',function(){setup();_geom.verts=[];_geom.vassign=[];same(fMulerSelectPick(4385,2800),{kind:'atom',atom:1});});
test('isolated atom retains loose fallback without bond groups',function(){setup();_geom.groups=null;_geom.anchors=[label(0,100,100,30,30)];_geom.verts=[];same(fMulerSelectPick(250,100),{kind:'atom',atom:1});});
test('empty canvas still returns null',function(){setup();same(fMulerSelectPick(8000,8000),null);});
test('expanded free H label remains literal H selection',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('expanded armed non-target H retains native parent redirect',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';_target=[1];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:1});});
test('expanded target H remains distinct in armed mission',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[label(0,4221,2528,130,180),label(1,4971,2528,100,180)];window.MulerQuizTarget='compSuffix';_purpose='fg';_target=[2];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('skeletal implicit vertex retains topological atom identity',function(){setup();_geom.anchors=[];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1,vertex:0});});
test('skeletal hetero glyph takes priority at its vertex',function(){setup();allAtomsTypeList=['O','C'];_geom.anchors=[label(0,4221,2528,180,200)];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1});});
function compactSetup(){setup();_geom.comp=[{anchor:0,symbol:'C',members:[1,3,4],el:{getBBox:function(){return{x:4300,y:2400,width:300,height:250};}},textBox:{x:4300,y:2400,w:300,h:250},box:{x:4270,y:2370,w:360,h:310},atomBox:{x:4300,y:2400,w:80,h:250}}];}
test('compacted free label retains whole fragment priority',function(){compactSetup();same(fMulerSelectPick(4500,2500),{kind:'fragment',atoms:[1,3,4],compactGroupBox:_geom.comp[0].textBox});});
test('compacted main-chain label retains carbon anchor-only policy',function(){compactSetup();_purpose='mainChain';window.MulerQuizTarget='compCarbonsCount';same(fMulerSelectPick(4500,2500),{kind:'atom',atom:1,compactAnchor:true,compactAtomBox:_geom.comp[0].atomBox});});
test('compacted N/S group retains whole-fragment policy during main-chain purpose',function(){compactSetup();_geom.comp[0].symbol='N';allAtomsTypeList[0]='N';_purpose='mainChain';window.MulerQuizTarget='compCarbonsCount';same(fMulerSelectPick(4500,2500),{kind:'fragment',atoms:[1,3,4],compactGroupBox:_geom.comp[0].box});});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
