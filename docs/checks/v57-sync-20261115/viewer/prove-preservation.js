const fs=require('fs'),crypto=require('crypto'),assert=require('assert');
const H=__dirname,C='/private/tmp/namelecule-v57-sync-20261115-l4r9e5_s/candidate/js/mulermoc-nom-molview-57.js';
function hash(s){return crypto.createHash('sha256').update(s).digest('hex');}
function functions(source){
 const matches=[...source.matchAll(/^(?:async )?function (\w+)\(/gm)],out={};
 for(let i=0;i<matches.length;i++){
  const end=i+1<matches.length?matches[i+1].index:source.length,part=source.slice(matches[i].index,end);
  for(let j=part.lastIndexOf('}');j>=0;j=part.lastIndexOf('}',j-1)){
   const candidate=part.slice(0,j+1);try{const value=Function('return ('+candidate+'\n)')();if(typeof value==='function'){out[matches[i][1]]=hash(value.toString());break;}}catch(e){}
  }
  assert(out[matches[i][1]],'Could not parse '+matches[i][1]);
 }
 return out;
}
const before=fs.readFileSync(H+'/before.js','utf8'),after=fs.readFileSync(C,'utf8'),upstream=fs.readFileSync(H+'/../upstream/target/js/mulermoc-nom-molview-57.js','utf8');
const B=functions(before),A=functions(after),U=functions(upstream);
const unchanged=Object.keys(B).filter(n=>A[n]===B[n]),changed=Object.keys(B).filter(n=>A[n]!==B[n]),added=Object.keys(A).filter(n=>!B[n]);
const draft=Object.keys(B).filter(n=>/^fMolDraft|^fJSmolLoadInlineSDF$/.test(n));
for(const n of draft)assert.strictEqual(A[n],B[n],'Changed protected draft function '+n);
const exactUpstream=Object.keys(A).filter(n=>A[n]===U[n]&&A[n]!==B[n]);
const result={comparison:'Version-renamed local reviewed56 baseline to candidate57; exact upstream57 function identities separately identified',beforeSHA256:hash(before),afterSHA256:hash(after),unchangedCount:unchanged.length,changed,added,allExistingDraftFunctionsByteIdentical:draft.length,unchanged,exactUpstreamImports:exactUpstream,functions:Object.fromEntries(Object.keys(A).map(n=>[n,{before:B[n]||null,after:A[n],upstream:U[n]||null}]))};
fs.writeFileSync(H+'/function-identities.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({unchanged:unchanged.length,changed,added,protectedDraft:draft.length,exactUpstream},null,2));
