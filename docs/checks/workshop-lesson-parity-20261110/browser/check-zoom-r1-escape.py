from pathlib import Path
exec((Path(__file__).parent/'driver-common.py').read_text(),globals())
try:
 source_guard();viewport(390,760);direct();click('.diagram-tools button');wait('!!document.querySelector(".zoom-image")&&document.querySelector(".zoom-image").naturalWidth>0');OUT['method']='Escape';OUT['open']=read('({disabled:document.querySelector(".diagram-tools button").disabled,expanded:document.querySelector(".diagram-tools button").getAttribute("aria-expanded")})');key('\ue00c');pause(700);OUT['afterClose']=read('({disabled:document.querySelector(".diagram-tools button").disabled,expanded:document.querySelector(".diagram-tools button").getAttribute("aria-expanded"),modalPresent:!!document.querySelector(".zoom-dialog"),focusOpener:document.activeElement===document.querySelector(".diagram-tools button")})');OUT['reopenBlocked']=OUT['afterClose']['disabled'];OUT['completed']=True
 print(json.dumps({'open':OUT['open'],'afterClose':OUT['afterClose'],'reopenBlocked':OUT['reopenBlocked']}),flush=True)
finally:finish()
