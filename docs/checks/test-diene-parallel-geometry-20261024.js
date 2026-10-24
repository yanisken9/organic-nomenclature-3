// Read-only geometry/scope test of the actual production SVG helper.
const source=readFile('js/mulermoc-nom-molview-50.js');
const start=source.indexOf('function fDrawDieneParallelDoubleBonds()');
const helper=source.slice(start,source.indexOf('\nfunction fUpdateSVG()',start));
const run=new Function('input','mode','key',`
 const nodes=input.map(p=>({p:p.slice(),getAttribute(k){return this.p[['x1','y1','x2','y2'].indexOf(k)]},setAttribute(k,v){this.p[['x1','y1','x2','y2'].indexOf(k)]=Number(v)}}));
 const mode2D=mode,selectedMol=key,bondList=[[1,2,2]],svgBondList=[1];
 const document={querySelector(){return {querySelectorAll(){return nodes}}}};
 ${helper}
 fDrawDieneParallelDoubleBonds();return nodes.map(n=>n.p);
`);
let checks=0;
function check(ok,msg){if(!ok)throw Error(msg);checks++;}
const key='methyl_3_pentadiene_1_3';
for(const degrees of [0,30,90,135,180])for(const reversed of [false,true]){
 const theta=degrees*Math.PI/180,u=[Math.cos(theta),Math.sin(theta)],n=[-u[1],u[0]];
 const at=(t,d)=>[t*u[0]+d*n[0],t*u[1]+d*n[1]];
 let pair=[[...at(-10,-1),...at(10,1)],[...at(-10,1),...at(10,-1)]];
 if(reversed)pair[1]=[...pair[1].slice(2),...pair[1].slice(0,2)];
 const out=run(pair,'skeletal',key);
 for(const p of out){
  const v=[p[2]-p[0],p[3]-p[1]];
  check(Math.abs(v[0]*u[1]-v[1]*u[0])<1e-8,'axis changed '+degrees);
  check(Math.abs(Math.hypot(...v)-20)<1e-8,'bond length changed');
 }
 check(Math.abs(out[0][0]*n[0]+out[0][1]*n[1]+1)<1e-8,'separation lost');
 check(out.flat().every(Number.isFinite),'nonfinite coordinate');
}
const parallel=[[0,-1,20,-1],[0,1,20,1]],crossed=[[0,-1,20,1],[0,1,20,-1]];
check(JSON.stringify(run(parallel,'condensed',key))===JSON.stringify(parallel),'parallel pair changed');
check(JSON.stringify(run(crossed,'other',key))===JSON.stringify(crossed),'mode guard failed');
check(JSON.stringify(run(crossed,'condensed','ethene'))===JSON.stringify(crossed),'molecule guard failed');
print('PASS '+checks+' geometry/scope assertions; horizontal/diagonal/vertical/reversed endpoints');
