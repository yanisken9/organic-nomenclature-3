var results=[];
function assert(v,m){if(!v)throw Error(m);}
function test(name,fn){try{fn();results.push({name:name,pass:true});}catch(e){results.push({name:name,pass:false,error:String(e)});}}
var window=this, mode2D='expanded', compactNumberingLabelMap={}, svgAtomColors2DFlag=false;
var allAtomsTypeList=['C','O','N','H'];
var node=function(atom,symbol,hidden,x){return {dataset:{},style:{display:hidden?'none':''},textContent:symbol,attrs:{'data-namelecule-atom':String(atom),'data-namelecule-role':'label'},getAttribute:function(k){return k==='data-muler-hidden'&&hidden?'spC':this.attrs[k]||null;},hasAttribute:function(k){return !!this.getAttribute(k);},getBBox:function(){return {x:x||0,y:10,width:20,height:30};}};};
var labels=[{node:node(1,'C',true,0)},{node:node(3,'N',false,90)},{node:node(2,'OH',false,50)},{node:node(4,'H',false,130)}];
var molSvg={selectAll:function(sel){return sel.indexOf('text[data-namelecule')===0?labels:[];}};
var document={querySelector:function(){return null;}};
test('skeletal hetero selection follows actual atom IDs despite DOM order',function(){var anchors=fMulerSelectHeteroAnchors(null);assert(anchors.length===2,'hidden C/H were included');var byId={};anchors.forEach(function(a){byId[a.atom]=a;});assert(byId[1].x===60&&byId[2].x===100,'hetero ownership shifted with DOM order');});
test('rendered ownership map keeps source IDs with skeletal omissions',function(){var map=fGetRenderedAtomTextMap(false,false);assert(map[1].node.textContent==='OH'&&map[2].node.textContent==='N'&&!map[3],'wrong atom text ownership or H included');});
// Exercise the actual composed renderer with stage stubs: preparation and
// selection state must precede native SVG read; overlays must follow final
// chemical geometry/metrics/fit, preserving guarded failure handling.
var calls=[], jsmeNomeclatureApplet={getMolecularAreaGraphicsString:function(){calls.push('readSVG');return '<svg></svg>';}};
var $=function(){return {html:function(){calls.push('mountSVG');},toggleClass:function(){}};};
var MuSVG=function(){return {select:function(){return null;}};};
function fApplySkeletalLayout(){calls.push('chemicalGeometry');}
function fMulerSelectPushState(){calls.push('selectionPush');}
function fAddHydrogens2SVG(){calls.push('hydrogens');}
function fMarkExpandedHydrogens(){calls.push('expandedH');}
function fCompactFunctionalGroups2D(){calls.push('compact');}
function fHideSkeletalSpCarbons(){calls.push('sp');}
function patchtheNitrogen(){calls.push('nitrogen');}
function fWrapStandaloneHydrogenTextsAsTspan(){calls.push('wrapH');}
function fApplyAtomColors2DToSVGLabels(){calls.push('atomColor');}
function fApplyCHBondColors2D(){calls.push('bondColor');}
function fHideEsterSkeletalCarbonHydrogens(){calls.push('hideEsterH');}
function fPrepareFixedCCAlkanePrototype(){calls.push('fixedCC');}
function fRefreshLabelBackplates(){calls.push('metrics');}
function fFit2DSVG(){calls.push('fit');}
function fValidate2DBondVisibility(){calls.push('validateVisibleBonds');}
function fMulerSelectRepaint(){calls.push('selectionRepaint');}
function fMulerSelectSeqBadges(){calls.push('sequenceBadges');}
function fMulerNumberAid(){calls.push('numberAid');}
test('composed SVG lifecycle retains local final geometry before native overlays',function(){fBuildMoleculeSVG();for(var pair of [['chemicalGeometry','selectionPush'],['selectionPush','readSVG'],['readSVG','mountSVG'],['hideEsterH','metrics'],['fixedCC','metrics'],['metrics','fit'],['fit','validateVisibleBonds'],['validateVisibleBonds','selectionRepaint'],['selectionRepaint','sequenceBadges'],['sequenceBadges','numberAid']])assert(calls.indexOf(pair[0])<calls.indexOf(pair[1]),pair.join(' must precede '));assert(window.__mulerSelRenderSeq===1&&Array.isArray(window.__mulerRemovedBondIdx),'render epoch/removal cache not reset');});
print(JSON.stringify({cases:results.length,passed:results.filter(function(r){return r.pass;}).length,results:results}));
if(results.some(function(r){return !r.pass;}))quit(1);
