()=>{
 if(window.top!==window)return;
 const epoch=Date.now()+'-'+Math.random().toString(36).slice(2),rows=[];let departing=false;
 function state(){let a=window.jmolAppletNomeclature,p=a?._appletPanel||a?._applet,v=p?.viewer;return {readyFlag:window.JSmolReadyFlag===true,appletReady:!!a?._ready,panel:!!p,viewer:!!v,selected:typeof selectedMol==='undefined'?null:selectedMol,step:typeof fScenarioPresent==='function'?fScenarioPresent()?.index:null,size:v?[v.screenWidth,v.screenHeight]:null,modelAtoms:v?.ms?.ac??null,visible:document.getElementById('nomeclature3D')?.getBoundingClientRect().height??null};}
 function log(kind,detail){const r={epoch,time:performance.now(),date:Date.now(),kind,departing,url:location.href,detail,state:state()};rows.push(r);if(['error','beforeunload','pagehide','Jmol._destroy:before','Jmol._destroy:after'].includes(kind))console.info('LIFE '+JSON.stringify(r));}
 window.__life={rows,state,log,epoch};log('preload',null);
 addEventListener('beforeunload',()=>{departing=true;log('beforeunload',null)});
 addEventListener('pagehide',e=>log('pagehide',{persisted:e.persisted}));
 addEventListener('error',e=>log('error',{message:e.message,source:e.filename,line:e.lineno,stack:e.error?.stack||null}));
 addEventListener('unhandledrejection',e=>log('error',{rejection:String(e.reason)}));
 function wrap(o,k,label){if(!o||typeof o[k]!=='function'||o[k].__lifeWrapped)return;const original=o[k];function wrapped(...args){const detail=k==='script'?{script:String(args[1]).slice(0,2000)}:k==='resizeApplet'?{dimensions:args[1]}:{args:args.map(a=>typeof a==='string'||typeof a==='boolean'||typeof a==='number'?a:typeof a)};log(label+':before',detail);try{return original.apply(this,args)}finally{log(label+':after',null)}}wrapped.__lifeWrapped=true;o[k]=wrapped;}
 let lastAtoms=null,watched=null;const timer=setInterval(()=>{if(!window.Jmol)return;const a=window.jmolAppletNomeclature;if(a?._applet?.viewer){const ac=a._applet.viewer.ms?.ac;if(ac!==lastAtoms){lastAtoms=ac;log('atom-count-change',{atoms:ac})}if(watched!==a._applet){watched=a._applet;Jmol.setCallback(a,'loadStructCallback',function(...args){log('loadStructCallback',{args:args.map(v=>typeof v==='string'||typeof v==='number'||typeof v==='boolean'?v:typeof v)})})}}for(const k of ['script','resizeApplet','_destroy','_readyCallback'])wrap(Jmol,k,'Jmol.'+k);for(const k of ['fLoadMol3D','fScenarioChrome','fToggleViewer3D','fDeselectMol','fScenarioGo','fScenarioApply','fSelectMol'])wrap(window,k,k);},10);
 addEventListener('pagehide',()=>clearInterval(timer));
}
