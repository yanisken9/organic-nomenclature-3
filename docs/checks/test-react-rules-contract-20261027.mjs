import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { validRules } from '../../react-preview/src/rule-data.js';
const element = (tag='div', children=[], classes=[], row=null) => ({tag,children,classes,row});
const rule = () => ({id:'component',title:'Κανόνας',text:['C',element('sub',['ν']),element('sup',['2']),element('br')],textClasses:[],table:[element('div',['μεθύλιο'],['ruleRow','selected'],'alkyl-μεθύλιο')]});
let checked=0;
const check=(value,expected)=>{assert.equal(validRules(value),expected);checked++;};
check([],true);check([rule()],true);check([rule(),{...rule(),id:'alkoxy'}],true);
for (const invalid of [null,{},'text',[rule(),rule()],[rule(),{...rule(),id:'unknown'}],[rule(),{...rule(),id:'alkoxy'},rule()]]) check(invalid,false);
for (const patch of [{title:''},{title:' '.repeat(20)},{title:'a'.repeat(181)},{textClasses:['onclick']},{textClasses:['HFlex','HFlex']},{onClick:'bad'},{text:null},{table:'<script>'}]) check([{...rule(),...patch}],false);
for (const node of [element('script',['alert(1)']),element('img'),{...element(),style:'color:red'},element('div',[],['onclick']),element('div',[],[],'bad row'),element('br',['bad']),{...element(),children:null}]) check([{...rule(),table:[node]}],false);
check([{...rule(),table:[element('div',['<img src=x onerror=bad>'])]}],true); // text remains text
check([{...rule(),table:['x'.repeat(20001)]}],false);
check([{...rule(),text:['x'.repeat(12000)],table:['x'.repeat(12000)]}],false);
check([{...rule(),table:Array(601).fill('')}],false);
let nested='text';for(let i=0;i<14;i++)nested=element('div',[nested]);check([{...rule(),table:[nested]}],false);
assert(!/dangerouslySetInnerHTML|innerHTML/.test(await readFile(new URL('../../react-preview/src/RulePanels.jsx',import.meta.url),'utf8')));
console.log(JSON.stringify({passed:true,contractCases:checked,boundedData:true,noRawHTMLAPI:true}));
