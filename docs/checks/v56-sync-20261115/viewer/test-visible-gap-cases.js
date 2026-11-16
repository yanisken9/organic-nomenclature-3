var window=this, allAtomsTypeList=[],bondList=[],_geom={},_purpose='free',_target=[];
var MULER_SELECT_ATOM_R=.35,MULER_SELECT_BOND_HW=.2;
function fMulerSelectGeom(){return _geom;}
function fMulerSelectPurpose(){return _purpose;}
function fMulerQuizTargetSet(){return _target;}
function assert(v,m){if(!v)throw Error(m);}
function same(actual,expected){assert(JSON.stringify(actual)===JSON.stringify(expected),'expected '+JSON.stringify(expected)+', got '+JSON.stringify(actual));}
var results=[];function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
function setup(){window.MulerQuizTarget=null;_target=[];_purpose='free';allAtomsTypeList=['C','C'];bondList=[[1,2,1]];_geom={med:750,groups:[{bond:0,lines:[{x1:4221,y1:2528,x2:4971,y2:2528}]}],anchors:[{atom:0,x:4385.966064453125,y:2586.3636474609375,w:559.02294921875,h:340.000244140625},{atom:1,x:5135.966064453125,y:2586.3636474609375,w:559.02294921875,h:340.000244140625}],comp:[],verts:[{x:4221,y:2528},{x:4971,y:2528}],vassign:[0,1]};}
test('actual measured raw midpoint is inside C1 glyph and correctly selects C1',function(){setup();same(fMulerSelectPick(4596,2528),{kind:'atom',atom:1});});
test('actual independently measured visible gap selects C-C bond',function(){setup();same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('all observed visible samples avoid explicit-atom vertex halos',function(){setup();for(var t=.65;t<=.84;t+=.01)same(fMulerSelectPick(4221+750*t,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('main-chain mission ignores actual visible gap without selecting endpoint',function(){setup();window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';same(fMulerSelectPick(4761,2528),{ignore:true});});
test('bond mission retains native endpoint payload for visible gap',function(){setup();window.MulerQuizTarget='compBondType';_purpose='bond';same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('expanded explicit carbon vertex does not steal visible C-C interior',function(){setup();_geom.anchors=[{atom:0,x:4221,y:2528,w:100,h:100},{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('labeled hetero vertex does not steal visible adjacent bond interior',function(){setup();allAtomsTypeList=['C','O'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4761,2528),{kind:'bond',bond:1,pair:[1,2]});});
test('unlabeled skeletal endpoint retains native implicit-vertex selection',function(){setup();_geom.anchors=[];same(fMulerSelectPick(4761,2528),{kind:'atom',atom:2,vertex:1});});
test('skeletal vertex ownership excludes only explicitly labeled atom',function(){setup();allAtomsTypeList=['C','O'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];same(fMulerSelectPick(4221,2528),{kind:'atom',atom:1,vertex:0});same(fMulerSelectPick(4971,2528),{kind:'atom',atom:2});});
test('explicit expanded H retains native parent redirection',function(){setup();allAtomsTypeList=['C','H'];_geom.anchors=[{atom:1,x:4971,y:2528,w:100,h:100}];window.MulerQuizTarget='compCarbonsCount';_purpose='mainChain';_target=[1];same(fMulerSelectPick(4971,2528),{kind:'atom',atom:1});});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));if(results.some(function(r){return !r.pass;}))quit(1);
