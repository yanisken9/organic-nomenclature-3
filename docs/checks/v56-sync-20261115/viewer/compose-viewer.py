from pathlib import Path
import re
root=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate')
evidence=Path(__file__).parent
s=(evidence/'merge-raw.js.txt').read_text()
i=0
def resolve(m):
 global i
 i+=1
 local,upstream=m[1],m[2]
 if i in [1,3,4,5,7,9,10,11]:return local
 if i in [2,6,8,15,16,17]:return upstream
 if i in [12,13]:return local+upstream
 if i==14:
  # Finish the local renderer, then retain the 2D font-only repair function
  # and add the native numbering aid as a separate function.
  hooks=upstream.split('// ── Numbering aid')[0].rsplit('}\n',1)[0]
  local=local.replace('  fValidate2DBondVisibility();\n}', '  fValidate2DBondVisibility();\n'+hooks+'}')
  return local+'}\n\n// ── Numbering aid'+upstream.split('// ── Numbering aid',1)[1]
 raise Exception(i)
s=re.sub(r'^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n',resolve,s,flags=re.M|re.S)
assert i==17
s=s.replace('spt/init-3-56.spt','spt/init-56.spt').replace('spt/init-55.spt','spt/init-56.spt')
(root/'js/mulermoc-nom-molview-56.js').write_text(s)
print('resolved',i,'conflicts;',len(s.splitlines()),'lines')
