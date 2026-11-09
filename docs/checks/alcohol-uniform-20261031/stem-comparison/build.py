# -*- coding: utf-8 -*-
"""Build comparison figures from actual captured SVG labels/geometry.

A common font-normalized frame is used for every panel, independent of the
application's currently open viewport-fitting diagnostic. Main sources untouched.
"""
from pathlib import Path
import gzip,json,xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
d=json.load(gzip.open(HERE/'browser.json.gz','rt'));assert d['completed']and not d['javascriptErrors'];cases=d['cases']
left=min(c['bounds']['left']for c in cases)-1;right=max(c['bounds']['right']for c in cases)+1;top=min(c['bounds']['top']for c in cases)-1;bottom=max(c['bounds']['bottom']for c in cases)+1
box=[left,top,right-left,bottom-top];sizes=[]
for c in cases:
 source=E.fromstring(c['rawSVG']);root=E.Element('{'+NS+'}svg',{'viewBox':' '.join(map(str,box)),'width':'1100','height':str(1100*box[3]/box[2]),'preserveAspectRatio':'xMidYMid meet','role':'img'})
 title=E.SubElement(root,'{'+NS+'}title');title.text={'current':'Πριν από την αλλαγή','proposed':'Προτεινόμενη διάταξη με λίγο κοντύτερο σύνδεσμο','equal-invalid':'Μη αποδεκτή διάταξη: δύο υδρογόνα στην ίδια θέση'}[c['case']]
 group=E.SubElement(root,'{'+NS+'}g',{'transform':'translate(%s %s) scale(%s)'%(-c['cx']/c['fontRoot'],-c['cy']/c['fontRoot'],1/c['fontRoot'])})
 for child in source:group.append(child)
 if c['case']=='equal-invalid':
  point=c['collisionPoint'];E.SubElement(root,'{'+NS+'}circle',{'cx':str(point['x']),'cy':str(point['y']),'r':'.7','fill':'none','stroke':'#b33343','stroke-width':'.09'})
  detail=E.fromstring(E.tostring(root));detail.set('viewBox','%s %s 5 5'%(point['x']-2.5,point['y']-2.5));detail.set('width','300');detail.set('height','300');(HERE/'collision-detail.svg').write_bytes(E.tostring(detail,encoding='utf-8',xml_declaration=True))
 (HERE/(c['case']+'.svg')).write_bytes(E.tostring(root,encoding='utf-8',xml_declaration=True));sizes.append({'case':c['case'],'nativeFontInRoot':c['fontRoot'],'fontNormalized':True})
(HERE/'figure-framing.json').write_text(json.dumps({'sameViewBoxForAll':box,'sameFontNormalization':True,'parentMidpointAligned':True,'cases':sizes,'applicationFramingUnchanged':True},indent=2))
print(json.dumps({'commonViewBox':box,'figures':len(cases)}))
