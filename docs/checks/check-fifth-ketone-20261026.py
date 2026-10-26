"""Apply existing checked ketone tests to one new molecule/current125-record baseline.

--check assets|naming uses RDKit/JSC; browser checks require local8013/BiDi9237.
Each reused script writes only its own fifth-ketone result, not prior evidence.
"""
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--check',choices=['assets','naming','desktop','narrow','numbering','highlights'],required=True)
args=parser.parse_args()
files={
 'assets':'check-other-ketones-20261026.py',
 'naming':'test-other-ketones-naming-20261026.py',
 'desktop':'test-other-ketones-browser-20261026.py',
 'narrow':'test-other-ketones-narrow-20261026.py',
 'numbering':'test-other-ketones-numbering-20261026.py',
 'highlights':'test-other-ketones-highlights-20261026.py',
}
p=Path('docs/checks')/files[args.check]
source=p.read_text().replace('other-ketones-specs-20261026.json','fifth-ketone-specs-20261026.json')
source=source.replace('namelecule-before-other-ketones-20261026','namelecule-before-fifth-ketone-20261026')
for kind in ['assets','naming','browser','narrow','numbering','highlights']:
 source=source.replace('other-ketones-'+kind+'-20261026.json','fifth-ketone-'+kind+'-20261026.json')
source=source.replace('/tmp/other-ketones-','/tmp/fifth-ketone-')
if args.check=='assets':
 source=source.replace("==121 and obj['newCount']==125","==125 and obj['newCount']==126")
 source=source.replace('oldRecordsUnchanged=121,newCount=125','oldRecordsUnchanged=125,newCount=126')
 # No new core intervention is approved/needed for this addition.
 source=source.replace("'js/mulermoc-nom-core-51.js',",'')
 source=source.replace('PASS 12 forms/graphs/H/geometry/3D/provenance;', 'PASS 3 forms/graphs/H/geometry/3D/provenance;')
 source=source.replace("allowed={", "allowed={'docs/checks/generate-other-ketones-20261026.py',")
exec(compile(source,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
