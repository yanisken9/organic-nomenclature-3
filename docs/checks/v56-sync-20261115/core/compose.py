from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent
C=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate/js')
resolutions=[]
def resolve(short):
 s=(D/f'{short}-initial-merge.js').read_text()
 def take(m):
  ours,theirs=m.group(1),m.group(2)
  side='ours'
  # The multi-FG prefix block was replaced wholesale upstream; preserve the
  # preceding local fail-closed locant check and adopt target's accumulator.
  if short=='core' and '_locs.push(currXPos)' in theirs:side='theirs'
  if short=='name-en':side='theirs' # comment only, implementation composed below
  resolutions.append({'file':short,'choice':side,'ours':ours,'theirs':theirs})
  return ours if side=='ours' else theirs
 s=re.sub(r'^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n',take,s,flags=re.M|re.S)
 assert '<<<<<<<'not in s
 if short=='name-en':
  # Upstream's eager second-infix restoration is for locant-led suffixes.
  # Bare dial already fuses later; eager restoration otherwise creates yne-dial.
  s=s.replace('if ((infix2 === "en" || infix2 === "yn") && typeof fFuseEnInfixSuffix === "function") {', 'if ((infix2 === "en" || infix2 === "yn") && /^-?\\d[\\d,]*-(di|tri)(one|ol|al|oic)/i.test(suffix) && typeof fFuseEnInfixSuffix === "function") {')
  start=s.index('    for (var _fi = 0; _fi + 1 < boxes.length; _fi++) {',s.index('// Fused suffix locants'))
  end=s.index('    // Abort (Greek render)',start)
  s=s[:start]+'''    for (var _fi = 0; _fi + 1 < boxes.length; _fi++) {
      try {
        var _fb = boxes[_fi];
        var _nextSuffix = _fi + 1, _suffixText = "";
        // Preserve local fusion across a suffix locant while passing the full
        // locant-led suffix to v56's e-restoration rule (yne-2,7-dione).
        while (_nextSuffix < boxes.length && /^-\\d[\\d,]*-$/.test(boxes[_nextSuffix][1])) {
          _suffixText += boxes[_nextSuffix][1];
          _nextSuffix++;
        }
        if ((_fb[0] === "comp6" || _fb[0] === "comp8") && _nextSuffix < boxes.length && boxes[_nextSuffix][0] === "comp9") {
          _suffixText += boxes[_nextSuffix][1];
          var _fused = (typeof fFuseEnInfixSuffix === "function") ? fFuseEnInfixSuffix(_fb[1], _suffixText) : _fb[1];
          if (_fused !== _fb[1]) boxes[_fi] = [_fb[0], _fused];
        }
      } catch (eF) { /* best-effort */ }
    }
'''+s[end:]
 (C/f'mulermoc-nom-{short}-56.js').write_text(s)
for k in ['core','name-en']:resolve(k)
(D/'merge-resolutions.json').write_text(json.dumps(resolutions,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'resolved':len(resolutions),'candidate':str(C)},ensure_ascii=False))
