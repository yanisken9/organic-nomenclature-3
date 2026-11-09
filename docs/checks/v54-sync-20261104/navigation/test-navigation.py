"""Evidence-only welcome/game navigation checks using real Firefox input."""
from pathlib import Path
import os
os.environ['NAMELECULE_BIDI_PORT']='9246'
os.environ['NAMELECULE_TEST_BASE_URL']='http://127.0.0.1:8013/'
support=Path('docs/checks/game-repair-20261103/test-browser.py').read_text().split('\ntry:\n',1)[0]
support=support.replace('HERE = ROOT / "docs/checks/game-repair-20261103"',
                        'HERE = ROOT / "docs/checks/v54-sync-20261104/navigation"')
exec(compile(support,'existing-game-input-support','exec'))

def viewport(width):
    call('browsingContext.setViewport',{'context':ctx,'viewport':{'width':width,'height':980},'devicePixelRatio':1})

def press(selector,touch):
    (lambda s:click(s,True) if touch else activate(s))(selector)

def welcome():
    until('location.pathname.endsWith("/design/welcome-proposal.html")&&!!document.querySelector(".card.two a.action")')

def game():
    until('location.pathname.endsWith("/games/name-repair.html")&&!!document.querySelector(".intro-start")')

def logo(selector,label):
    until('!!document.querySelector('+json.dumps(selector)+')&&document.querySelector('+json.dumps(selector)+').naturalWidth>0')
    check(ev('document.querySelector('+json.dumps(selector)+').currentSrc.endsWith("/workshop-logo-3d-v1.png")'),label)

try:
    for width,touch in [(1500,False),(390,True)]:
        viewport(width);navigate('design/welcome-proposal.html?v=v54-navigation-check');welcome()
        no_overflow('Welcome no horizontal overflow '+str(width))
        check(ev('document.querySelector(".card.two a.action").href.includes("/games/name-repair.html")'), 'Game card has direct game anchor '+str(width))
        if width==390:screenshot(HERE/'welcome-390.png')
        for panel in ['teacher','login']:
            press('[data-panel='+panel+']',touch)
            until('document.querySelector("#details").open')
            check(ev('document.querySelector("#dialog-copy").textContent.includes("υπό σχεδιασμό")'),'Existing '+panel+' dialog '+str(width))
            check(ev('document.querySelector("#dialog-link").hidden')==(panel=='login'),'Dialog link visibility '+panel+' '+str(width))
            press('#details form button',touch);until('!document.querySelector("#details").open')
        press('.card.one a.action',touch)
        until('location.pathname.endsWith("/design/theory-library.html")&&!!document.querySelector("main")')
        check(ev('document.querySelector("h1").textContent==="Βιβλιοθήκη θεωρίας"&&!!document.querySelector("a[href*=scenario]")'),'Existing theory library route '+str(width))
        call('browsingContext.traverseHistory',{'context':ctx,'delta':-1});welcome()
        press('.card.two a.action',touch);game()
        check(not ev('!!document.querySelector("dialog[open]")'),'Game entry opens page without modal '+str(width))
        logo('.workshop-logo','Intro accepted 3D logo '+str(width));no_overflow('Game intro no overflow '+str(width))
        screenshot(HERE/('game-intro-'+str(width)+'.png'))
        press('.intro-start',touch)
        for index,r in enumerate(GAME['rounds']):
            ready();logo('.workshop-logo-small','Mission accepted 3D logo '+str(width)+' '+r['id'])
            no_overflow('Mission no overflow '+str(width)+' '+r['id'])
            if index==0:screenshot(HERE/('game-round-'+str(width)+'.png'))
            solve(r,keyboard=not touch,touch=touch)
            check(ev('document.querySelector(".success-explanation").textContent')==r['successText'],'Success rule text '+str(width)+' '+r['id'])
            press('.round-next button',touch)
        until('!!document.querySelector(".results")')
        summary=json.loads(ev('JSON.stringify([...document.querySelectorAll(".stat-number")].map(n=>Number(n.textContent)))'))
        check(summary==[4,4],'Five-round result counters '+str(width),summary=summary)
        screenshot(HERE/('game-results-'+str(width)+'.png'))
        no_overflow('Results no overflow '+str(width))
        press('.results-actions a',touch);welcome()
        check(True,'Results return welcome '+str(width))
        call('browsingContext.traverseHistory',{'context':ctx,'delta':-1})
        until('location.pathname.endsWith("/games/name-repair.html")&&!!document.querySelector("#game-root")')
        check(True,'Browser Back restores game document '+str(width))
        call('browsingContext.traverseHistory',{'context':ctx,'delta':1});welcome()
        check(True,'Browser Forward restores welcome '+str(width))
        press('.card.two a.action',touch);game();press('.intro-start',touch);ready()
        press('.exit-link',touch);welcome();check(True,'Mission Exit returns welcome '+str(width))
        press('.card.two a.action',touch);game();press('a.brand',touch);welcome()
        check(True,'Brand returns welcome '+str(width))
        out['journeys'].append({'width':width,'input':'simulated touch' if touch else 'keyboard Enter',
                               'rounds':5,'summary':summary,'welcomeRoutes':['theory','teacher','login','game'],
                               'returnRoutes':['results','Exit','brand','Back','Forward']})
    out['completed']=True
except Exception as error:
    out.update(failure=str(error),traceback=traceback.format_exc());print(out['traceback'],flush=True)
    try:screenshot(HERE/'navigation-failure.png')
    except Exception:pass
finally:
    out['javascriptErrors']=js_errors
    out['diagnostics']=[e for e in all_events if e.get('method')=='log.entryAdded' and e.get('params',{}).get('level')in ['error','warn']]
    (HERE/'navigation-browser.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    call('browsingContext.close',{'context':ctx});call('session.end',{})
    print(json.dumps({'completed':out['completed'],'checks':len(out['checks']),'javascriptErrors':len(js_errors)}),flush=True)
if not out['completed'] or js_errors:raise SystemExit(1)
