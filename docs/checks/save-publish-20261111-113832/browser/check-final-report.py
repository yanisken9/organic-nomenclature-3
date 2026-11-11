from pathlib import Path
exec(Path(__file__).with_name("driver.py").read_text())
try:
 open_page("docs/professor-20261111/update.html?v=final-20261111");wait('!!document.getElementById("publication-status")')
 data=read('({title:document.title,status:document.getElementById("publication-status").textContent,links:[...document.querySelectorAll(".links a")].map(e=>e.href),core:document.body.textContent.includes("Δεν έγιναν αλλαγές σε κανένα από τα 11 αρχεία core")})')
 assert "ολοκληρώθηκαν"in data['status']and"6539"in data['status']and"235"in data['status']and data['core']
 shot('final-public-professor-report.png');(HERE/'final-public-report-ui.json').write_text(json.dumps({'passed':True,'page':data,'scope':'Owned Firefox public report DOM/content screenshot only.'},ensure_ascii=False,indent=2)+'\n');print('Final public report rendered',flush=True)
finally:finish()
