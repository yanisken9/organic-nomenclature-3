"""Read-only measurements from actual parent/iframe DOM and FontFaceSet."""
from pathlib import Path
exec((Path(__file__).with_name('helpers.py')).read_text())
import hashlib
OUT.update({'textSamples':[],'fontEvidence':[],'heights':[]})
def lesson(index=3,version=55):
 open_page(f'mulermoc-nom-{version}.html?scenario=scenarios/alkanes-user-3.scenario.json&present=1&from=theory-library&textParity=20261111-r1#step={index+1}');ready()
def sample(game,label):
 d=read('''(()=>{let game='''+json.dumps(game)+''',f=document.querySelector('.nl-builder-frame'),doc=game==='builder'?f.contentDocument:document,win=doc.defaultView,h=document.querySelector(game==='builder'?'.nl-builder-heading':'.nl-game-choice-repair .round-heading h1'),l=document.querySelector(game==='builder'?'.nl-builder-logo':'.nl-game-choice-repair .workshop-logo-small'),o=doc.querySelector(game==='builder'?'.objective':'.nl-game-choice-repair .round-objective'),q=doc.querySelector(game==='builder'?'.intro-detail':'.nl-game-choice-repair .compact-steps'),status=game==='builder'?doc.querySelector('#game-status'):null,host=document.querySelector(game==='builder'?'.nl-builder-host':'.nl-game-choice-repair'),d=document.getElementById('nlQuizDialog'),dr=d.getBoundingClientRect(),bar=document.querySelector('.nl-quiz-dialog-header').getBoundingClientRect(),r=h.getBoundingClientRect(),lr=l.getBoundingClientRect(),hr=host.getBoundingClientRect();let style=n=>{let s=n.ownerDocument.defaultView.getComputedStyle(n),r=n.getBoundingClientRect();return{text:n.textContent,fontFamily:s.fontFamily,fontSize:s.fontSize,fontWeight:s.fontWeight,lineHeight:s.lineHeight,letterSpacing:s.letterSpacing,maxWidth:s.maxWidth,textAlign:s.textAlign,width:r.width,height:r.height}};let visible=e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'};return{label:'''+json.dumps(label)+''',game,outerWidth:innerWidth,outerHeight:innerHeight,allocation:game==='builder'?f.contentWindow.innerWidth:host.clientWidth,hostWidth:hr.width,title:style(h),objective:style(o),secondary:style(q),status:status?{...style(status),error:status.classList.contains('error')}:null,logoCount:[...document.querySelectorAll(game==='builder'?'.nl-builder-logo':'.nl-game-choice-repair .workshop-logo-small')].filter(visible).length,logoLoaded:l.complete&&l.naturalWidth>0,logoDecorative:l.alt===''&&l.getAttribute('aria-hidden')==='true',logoWidth:lr.width,logoCenter:lr.x+lr.width/2,hostCenter:hr.x+hr.width/2,headingCenter:r.x+r.width/2,headingTop:r.top,headingBottom:r.bottom,logoTop:lr.top,logoBottom:lr.bottom,stickyBottom:bar.bottom,dialogBottom:dr.bottom,scrollTop:d.scrollTop,focused:document.activeElement===h,tabIndex:h.tabIndex,parentOverflow:document.documentElement.scrollWidth>innerWidth,dialogOverflow:d.scrollWidth>d.clientWidth,childOverflow:game==='builder'?doc.documentElement.scrollWidth>win.innerWidth:false,caption:document.querySelector('.nl-game-choice-repair .round-game-label')?.textContent||null}})()''')
 OUT['textSamples'].append(d);return d

def fonts(label,game):
 wait('!!document.fonts')
 d=json.loads(ev('''(async()=>{let child=document.querySelector('.nl-builder-frame')?.contentDocument;async function inspect(doc){let completed=await Promise.race([doc.fonts.ready.then(()=>true),new Promise(r=>setTimeout(()=>r(false),3000))]);return{status:doc.fonts.status,readyWithin3s:completed,checks:{roboto70040:doc.fonts.check('700 40px "Roboto Condensed"'),system70024:doc.fonts.check('700 24px system-ui')},faces:[...doc.fonts].map(f=>({family:f.family,status:f.status,weight:f.weight,style:f.style,display:f.display})),fontResources:doc.defaultView.performance.getEntriesByType('resource').filter(e=>/fonts\.|\.woff|\.ttf|\.otf/i.test(e.name)).map(e=>({name:e.name,duration:e.duration,transferSize:e.transferSize}))}}return JSON.stringify({label:'''+json.dumps(label)+''',game:'''+json.dumps(game)+''',parent:await inspect(document),iframe:child?await inspect(child):null})})()'''))
 OUT['fontEvidence'].append(d);return d

def top_shot(name):ev('document.getElementById("nlQuizDialog").scrollTop=0;true');pause(.3);shot(name)
def verify(d,label,natural=False):
 expected=20 if d['allocation']<=760 else 24;sec=12 if d['allocation']<=760 else 11.52
 f=lambda v:float(v[:-2])
 check(abs(f(d['objective']['fontSize'])-expected)<.05 and d['objective']['fontWeight']=='700' and abs(f(d['objective']['lineHeight'])-expected*1.45)<.05 and d['objective']['maxWidth']=='810px',label+' objective matches allocated-width 24/20px 700/1.45 max810',d)
 for field in ['secondary']+(['status'] if d['game']=='builder' else []):
  t=d[field];check(abs(f(t['fontSize'])-sec)<.05 and t['fontWeight']=='400' and abs(f(t['lineHeight'])-sec*1.6)<.05,label+' '+field+' matches 11.52/12px 400/1.6',t)
 check(d['logoCount']==1 and d['logoLoaded'] and d['logoDecorative'] and abs(d['headingCenter']-d['hostCenter'])<1 and abs(d['logoCenter']-d['hostCenter'])<1,label+' one centered loaded decorative logo/title',d)
 check(not any(d[k] for k in ['parentOverflow','dialogOverflow','childOverflow']),label+' no parent/dialog/embedded horizontal overflow',d)
 if natural:check(d['focused'] and d['tabIndex']==-1 and d['logoTop']>=d['stickyBottom'] and d['headingBottom']<=d['dialogBottom'],label+' existing title focus and natural visible entry',d)
 if d['game']=='repair':check(d['caption']=='ΣΥΝΕΡΓΕΙΟ ΟΝΟΜΑΤΩΝ',label+' Workshop caption retained')

def stable(label):
 pause(.7);xs=[]
 for i in range(6):xs.append(bread('document.documentElement.scrollHeight'));pause(.2)
 hs=[]
 for i in range(6):hs.append(ev('document.querySelector(".nl-builder-frame").getBoundingClientRect().height'));pause(.2)
 OUT['heights'].append({'label':label,'documentHeights':xs,'frameHeights':hs});check(max(hs)-min(hs)<=1,label+' iframe height settles',hs)
