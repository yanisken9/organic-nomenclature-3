"""Recreate the bounded approved core/EN three-way composition; no source data writes."""
from pathlib import Path
import argparse,re,subprocess
P=Path(__file__).resolve().parents[4]
C=Path(argparse.ArgumentParser().parse_known_args()[1][0])
for kind in ['core','name-en']:
 paths=[P/f'js/mulermoc-nom-{kind}-54.js',P/f'docs/checks/v54-merge-20261109/upstream/base/js/mulermoc-nom-{kind}-54.js',P/f'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-{kind}-55.js']
 t=subprocess.run(['git','merge-file','-p',*[str(p)for p in paths]],capture_output=True,text=True).stdout
 n=[0]
 def resolve(m):
  n[0]+=1;a,b=m.groups();i=n[0]
  if kind=='name-en':
   if i==1:return '// variant "sys": systematic substituent forms, matching engineEN_sys.\n'+a.replace('P-14.4','P-16.7.1(a)')
   return b.replace('directly before a','before a').replace('suffix box regains its terminal "e"','suffix regains its terminal "e", across locants')
  if i in [1,2,3]:return a
  if i==4:return b.replace('// and declared stereochemistry', '// and declared stereochemistry')+'// Missing H use supported charge-aware valences; query, radical and stereo inputs fail closed.\n'
  if i==5:return a.replace('0.78','MOLGEN_CH_LEN')
  if i==6:return '        atoms.push({ x: bestX, y: bestY, el: "H", parentSourceIndex: h + 1 });\n'
  if i in [7,8]:return b
  if i==9:return a.replace('var L = 1.17','var L = MOLGEN_CC_LEN')
  if i==10:return b.replace('sortedFunPositions.sort()','sortedFunPositions.sort((a, b) => a - b)')
  raise ValueError(i)
 t=re.sub(r'^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n',resolve,t,flags=re.M|re.S)
 if kind=='core':
  old='if (L > 8 || !alkylSubstituentNames[L]) return null'
  assert t.count(old)==1
  t=t.replace(old,'// The v1 name describes one rooted path only. A fork would leave\n        // side carbons unnamed; leave it unclaimed so naming declines.\n        if (L !== side.size || L > 8 || !alkylSubstituentNames[L]) return null')
  t=t.replace('_groups[nameMultiPrefix[_dl.length - 1] + nameMainCompObj3.halogen.substitute[_hx]]', '_groups[nameMainCompObj3.halogen.substitute[_hx]]')
  t=t.replace('_groupsN[nameMultiPrefix[_directNitro.length - 1] + nameMainCompObj3.nitro.substitute]', '_groupsN[nameMainCompObj3.nitro.substitute]')
  # Include protected sp branches in the new occupancy mechanism without rotating them.
  t=t.replace('queue.push({ node: br, x: (ci + outward) * DX, y: 0, dx: outward, dy: 0 });', 'queue.push({ node: br, x: (ci + outward) * DX, y: 0, dx: outward, dy: 0 });\n          _claimed[br] = { x: (ci + outward) * DX, y: 0 };')
 assert '<<<<<<<' not in t
 (C/f'js/mulermoc-nom-{kind}-55.js').write_text(t)
 print(kind,'resolved',n[0])
