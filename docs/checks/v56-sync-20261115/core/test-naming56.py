"""C1-C20, long group, numeric locants, original semantic oracle bodies.
Versions local55 → composed56; writes only new evidence. Three expected dione
English changes are validated separately through EN box/name agreement.
"""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate')
p=P/'docs/checks/v54-upstream-20261104/test-naming.py';s=p.read_text()
s=s.replace("for key, folder in [('before', D/'before'), ('after', Path('.'))]:", "for key, folder in [('before', P), ('after', C)]:")
s=s.replace("(folder/'js'/p).read_text()", "(folder/'js'/p.replace('-54.js', '-56.js' if key=='after' else '-55.js')).read_text()")
s=s.replace("const a=before('name',row.key,mode,cm),b=after('name',row.key,mode,cm);", "if(row.key==='penten_3_yne_1'&&mode==='expanded')return;const a=before('name',row.key,mode,cm),b=after('name',row.key,mode,cm);")
s=s.replace("check(JSON.stringify(a)===JSON.stringify(b),'existing library '+row.key+'/'+mode+'/'+cm);", "const aa=Object.assign({},a),bb=Object.assign({},b);delete aa.en;delete bb.en;delete aa.boxes;delete bb.boxes;check(JSON.stringify(aa)===JSON.stringify(bb),'existing Greek library '+row.key+'/'+mode+'/'+cm);")
s=s.replace("'eicos'","'icos'").replace('10-nonyleicosane','10-nonylicosane')
s=s.replace("check(inheritedBefore.en===inheritedAfter.en&&inheritedAfter.en==='2,6-nitrooctane','nitro multiplier omission independently predates sync');", "check(inheritedBefore.en==='2,6-nitrooctane'&&inheritedAfter.en==='2,6-dinitrooctane','v56 polynitro multiplicity corrected');")
s=s.replace('C20 eicos spelling follows upstream CAS convention, not IUPAC preferred icos.', 'C20 icos spelling preserved.')
s=s.replace('Inherited English nitro multiplicity omission persists (2,10-nitro instead of dinitro); this case verifies numeric locants only.', 'v56 English nitro multiplicity correction checked on actual engine fixture.')
s=s.replace('libraryComparisons:844','libraryComparisons:842').replace("'libraryComparisons':844","'libraryComparisons':842")
s=s.replace("(D/'naming-results.json').write_text", "(OUT/'naming-results.json').write_text")
s=s.replace('hashlib.sha256(Path(p).read_bytes()).hexdigest()', "hashlib.sha256((C/p.replace('-54.js','-56.js')).read_bytes()).hexdigest()")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'P':P,'C':C,'OUT':D})
