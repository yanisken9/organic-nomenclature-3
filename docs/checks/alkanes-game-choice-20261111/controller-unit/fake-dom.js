class FakeNode{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.handlers={};this.parentNode=null;this.className='';this.open=false;this.hidden=false;this.focusCalls=0;this._text='';const names=new Set();this.classList={toggle:(name,on)=>on?names.add(name):names.delete(name),add:name=>names.add(name),remove:name=>names.delete(name),contains:name=>names.has(name)};}
 get isConnected(){return this===body||!!(this.parentNode&&this.parentNode.isConnected);}
 get textContent(){return this._text+this.children.map(child=>child.textContent).join('');}
 set textContent(value){this.replaceChildren();this._text=String(value);}
 append(...items){for(const item of items){if(item.parentNode)item.remove();item.parentNode=this;this.children.push(item);}}
 appendChild(item){this.append(item);return item;}
 remove(){if(this.parentNode){this.parentNode.children=this.parentNode.children.filter(item=>item!==this);this.parentNode=null;}}
 replaceChildren(...items){for(const item of this.children)item.parentNode=null;this.children=[];this._text='';this.append(...items);}
 setAttribute(key,value){this.attributes[key]=String(value);}
 removeAttribute(key){delete this.attributes[key];}
 addEventListener(name,handler){(this.handlers[name]||(this.handlers[name]=[])).push(handler);}
 fire(name,extra={}){for(const handler of this.handlers[name]||[])handler({target:this,preventDefault(){},stopPropagation(){},...extra});}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 querySelectorAll(selector){const match=node=>selector[0]==='#'?node.id===selector.slice(1):selector[0]==='['?Object.prototype.hasOwnProperty.call(node.attributes,selector.slice(1,-1)):selector[0]==='.'?node.className.split(/\s+/).includes(selector.slice(1)):selector.split(',').some(tag=>node.tagName===tag.toUpperCase());const found=[];function walk(node){for(const child of node.children){if(match(child))found.push(child);walk(child);}}walk(this);return found;}
 find(id){return this.id===id?this:this.querySelector('#'+id);}
 showModal(){this.open=true;}
 close(){this.open=false;this.fire('close');}
 focus(){this.focusCalls++;}
}
let body;
const rounds=[];
let destroyCalls=0,storageReads=0,storageWrites=0;
let liveScenario=null,navigation=[];
const storage=new Map();
function resetEnvironment(){
 body=new FakeNode('body');rounds.length=0;destroyCalls=0;storageReads=0;storageWrites=0;storage.clear();liveScenario=null;navigation=[];
 global.document={body,baseURI:'http://memory.test/',readyState:'loading',createElement:tag=>new FakeNode(tag),getElementById:id=>body.find(id),querySelectorAll:selector=>body.querySelectorAll(selector)};
 global.sessionStorage={getItem(key){storageReads++;return storage.has(key)?storage.get(key):null;},setItem(key,value){storageWrites++;storage.set(key,value);}};
 global.MuLERMoCScenario={present:true};global.fScenarioPresent=()=>liveScenario;
 global.fScenarioPlayUi=()=>{};global.fScenarioGo=index=>navigation.push(index);
 global.NameleculeRepairGame={mountRound(host,options){const handle={destroyed:false,destroy(){if(!this.destroyed){this.destroyed=true;destroyCalls++;}}};rounds.push({host,options,handle});return handle;}};
}
