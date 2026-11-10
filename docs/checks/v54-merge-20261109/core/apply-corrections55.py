"""Single bounded correction unit CV55-07..10 from frozen core/EN target."""
from pathlib import Path
import argparse,re
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;D=H/'corrections-20261110';C=Path(argparse.ArgumentParser().parse_known_args()[1][0])
s=(D/'before-name-en55.js').read_text()
s=s.replace('if (!sysText || sysText === commonText) return false;', 'if (!sysText) return false;')
s=s.replace('// Differs-from-school required (toggle visibility, sort keys and verdicts\n// keyed off unwrapped text stay byte-identical where sys equals school);\n// already-parenthesized, unchanged, or digitless names pass through;', '// Intrinsic locants require enclosure even when school and systematic\n// text coincide. Already-parenthesized or digitless names pass through;')
# Full sorting already preserves each group\'s component ids. A group in the\n# middle needs no fallback and must retain its alphabetical position.
a=s.index('    if (_jord) {\n      try {\n        var _jg1');b=s.index('    var pre;',a);s=s[:a]+s[b:]
a=s.index('      if (_ord) {\n        // G1 (if present)');b=s.index('      if (_ord) {',a+20);s=s[:a]+s[b:]
s=s.replace('} else { push("comp3", S(3)); }', '''} else {
          var _bare3 = S(3);
          if (sys && fENSysNeedsParens(_bare3, Sch(3), loc2)) _bare3 = "(" + _bare3 + ")";
          push("comp3", _bare3);
        }''')
s=s.replace('return /yl$/.test(_t) && /(chloro|bromo|fluoro|iodo|nitro)/.test(_t);', '''return /yl$/.test(_t) && (/(chloro|bromo|fluoro|iodo|nitro)/.test(_t) ||
      /^\\d[\\d,]*-(?:di|tri|tetra)?(?:methyl|ethyl|propyl|butyl)/.test(_t));''')
s=s.replace('out.push(/\\d/.test(s2) ? m2[1] + "(" + s2 + ")" : m2[1] + s2);', '''var _mult = fIsSubstitutedStemEN(s2) ? fBisPrefixEN(m2[1]) : m2[1];
        out.push(/\\d/.test(s2) ? _mult + "(" + s2 + ")" : _mult + s2);''')
s=s.replace('// sec-/tert- sort as plain Roman (P-14.5.3 tie-break only).)', '// italic sec-/tert- are ignored until the Roman-letter tie-break).')
s=s.replace('// strips. sec-/tert- sort as plain Roman (P-14.5.3 tie-break only).)', '// strips. Italic sec-/tert- are ignored until the Roman-letter tie-break).')
s=s.replace('return s.replace(/^(di|tri|tetra)(?=[a-z])/, "");', '''return s.replace(/^(di|tri|tetra)(?=[a-z])/, "").replace(/^(sec|tert)-/, "");''')
# Italic retained prefixes decide only after their Roman group names tie.
s=s.replace('      if (ka > kb) return 1;\n      var la = [], lb = [];', '''      if (ka > kb) return 1;
      var italic = function (text) {
        var m = /^(?:di|tri|tetra)?(sec|tert)-/.exec(String(text || "").toLowerCase());
        return m ? m[1] : "";
      };
      var ia = italic(gs[a].name), ib = italic(gs[b].name);
      if (ia < ib) return -1;
      if (ia > ib) return 1;
      var la = [], lb = [];''')
(C/'js/mulermoc-nom-name-en-55.js').write_text(s)
s=(D/'before-core55.js').read_text()
a='''                const _decAll = fGetDecoratedBranchInfo()
                const _decClaimed = {}'''
b='''                const _decAll = fGetDecoratedBranchInfo()
                // Without the decorated merge, this legacy path names direct
                // halogens only. Decline carbon branches rather than omit them.
                if (!_decAll.length && fGetHydrocarbonSubstituentInfo().length) {
                    fDeclineNaming("unsupported alkyl/halogen branch combination")
                }
                const _decClaimed = {}'''
assert s.count(a)==1;s=s.replace(a,b)
a='''                const _decNitro = fGetDecoratedBranchInfo()
                const _decNitroClaimed = {}'''
b='''                const _decNitro = fGetDecoratedBranchInfo()
                if (!_decNitro.length && fGetHydrocarbonSubstituentInfo().length) {
                    fDeclineNaming("unsupported alkyl/nitro branch combination")
                }
                const _decNitroClaimed = {}'''
assert s.count(a)==1;s=s.replace(a,b)
(C/'js/mulermoc-nom-core-55.js').write_text(s)
print('Applied CV55-07/08/09 EN and CV55-10 failclosed safeguards')
