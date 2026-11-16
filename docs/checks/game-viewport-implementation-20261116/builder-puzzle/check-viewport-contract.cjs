/* Developer source-contract checks. No browser, timers, storage or app writes. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../../..'),Levels=require(path.join(root,'js/namelecule-game-levels.js'));
let checks=0;const records=[];
function check(label,fn){fn();records.push(label);checks++;}
function declaration(source,name){const at=source.indexOf('  function '+name+'(');assert.ok(at>=0,name);let i=source.indexOf('{',at),depth=1;for(i++;depth;i++){if(source[i]==='{')depth++;if(source[i]==='}')depth--;}return source.slice(at,i);}
for(const game of ['builder','puzzle']){
 const file='js/namelecule-'+(game==='builder'?'name-builder':'molecular-puzzle')+'.js',source=fs.readFileSync(path.join(root,file),'utf8');
 const context=Levels.makeContext({source:'enriched',level:3,seed:'1234'}),moleculeId=Levels.contextIds(context)[0];
 const channel='namelecule-'+(game==='builder'?'builder':'puzzle')+'-lesson-v1';
 const current={requestId:7,attemptId:'attempt-7',moleculeId,context};
 const packet={channel,session:'viewport_fixture_session',requestId:7,attemptId:'attempt-7',moleculeId,context,width:390,height:430};
 const ctx={Levels,lesson:{current},lessonChannel:channel,CHANNEL:channel,lessonSession:'viewport_fixture_session'};
 vm.createContext(ctx);vm.runInContext(declaration(source,'validateLessonContext')+'\n'+declaration(source,'validViewportMessage')+'\nglobalThis.validate=validViewportMessage;',ctx);
 check(game+' validated same-attempt viewport accepted',()=>assert.equal(ctx.validate(packet),true));
 for(const [field,bad] of Object.entries({channel:'wrong',session:'wrong',requestId:8,attemptId:'attempt-8',moleculeId:'methane',width:0,height:Infinity}))check(game+' rejects viewport '+field+' mismatch',()=>assert.equal(ctx.validate({...packet,[field]:bad}),false));
 check(game+' rejects mixed/present-null context without legacy fallback',()=>{assert.equal(ctx.validate({...packet,context:null}),false);assert.equal(ctx.validate({...packet,context:{...context,extra:true}}),false);assert.equal(ctx.validate({...packet,context:{...context,seed:'4321'}}),false);});
 check(game+' legacy viewport accepts only absent context',()=>{delete current.context;const legacy={...packet};delete legacy.context;assert.equal(ctx.validate(legacy),true);assert.equal(ctx.validate({...legacy,context}),false);});
 check(game+' child viewport opt-in explicitly requires query on lesson',()=>assert.ok(source.includes("(!lesson || new URL"))); 
 check(game+' legacy resize and reveal retain opted-out branch',()=>{assert.match(source,game==='builder'?/function scheduleSize\(\) \{\s*if \(viewportEnabled\)/:/function postSize\(\) \{\s*if \(viewportEnabled\)/);assert.match(source,game==='builder'?/function revealRange\(purpose, region\) \{\s*if \(viewportEnabled\)/:/function reveal\(el\) \{\s*if \(viewportEnabled\)/);});
 const html=fs.readFileSync(path.join(root,'games/'+(game==='builder'?'name-builder':'molecular-puzzle')+'.html'),'utf8');
 check(game+' helper loads before controller and native entry unchanged',()=>{assert.ok(html.indexOf('namelecule-game-viewport.js')<html.indexOf(game==='builder'?'namelecule-name-builder.js':'namelecule-molecular-puzzle.js'));if(game==='builder')assert.ok(source.includes("frame.src = 'name-builder-viewer.html?v=alkane-pool-20261116-r1&session='"));else assert.ok(source.includes('graph.nodes.length >= E.MAX_NODES'));});
}
const output={role:'Developer read-only source-contract validation; no visual/browser claim',checks,passed:checks,records};
fs.writeFileSync(path.join(__dirname,'viewport-contract-results.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));
