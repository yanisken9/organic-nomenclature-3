from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
try:
 source_guard();viewport(1280,800);direct()
 for w,h in [(1280,800),(390,760),(320,700)]:viewport(w,h);top();geometry('authored-r1-entry',w)
 viewport(390,760);click('[id$="part-saturation"]');pause(600)
 a=read('({scroll:scrollY,status:document.querySelector(".part-selection-status").textContent,objective:document.querySelector(".round-objective").textContent,rect:document.querySelector(".part-selection-status").getBoundingClientRect().toJSON(),viewport:innerHeight})');OUT['beforeWrongPart']=a;shot('authored-wrongpart');check(a['status']=='Αυτό το συνθετικό συμφωνεί με τη δομή.','Before authored wrong-part lacks mission reminder',a)
 click('[id$="part-root"]');pause(600);g=read('({scroll:scrollY,rect:document.querySelector(".choice-fieldset").getBoundingClientRect().toJSON(),viewport:innerHeight})');OUT['beforeNoReveal']=g;check(g['rect']['bottom']>g['viewport'],'Before page choice disclosure remains below viewport without reveal',g);shot('authored-no-reveal')
 viewport(1280,800);click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');shot('authored-zoom-text');key('\ue00c')
 direct(True);geometry('generated-basic-entry',1280);click('[id$="part-root"]');OUT['generatedWrongPart']=ev('document.querySelector(".part-selection-status").textContent');shot('generated-basic-wrongpart')
 ev('sessionStorage.clear();true');direct(True,'alkanes-branched','challenge');geometry('generated-challenge-entry',1280);OUT['challengeObjective']=ev('document.querySelector(".round-objective").textContent');OUT['completed']=True
except Exception:
 OUT['failure']=traceback.format_exc();print(OUT['failure'],flush=True)
 try:shot('failure')
 except Exception:pass
finally:finish()
if not OUT['completed']:raise SystemExit(1)
