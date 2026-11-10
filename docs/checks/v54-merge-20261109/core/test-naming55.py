"""Reuse complete GR/EN numeric-locant/C9-C20 oracle suite on candidate55.
Current54 is the comparison baseline; evidence writes only this directory.
"""
from pathlib import Path
import argparse
P=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
C=Path(argparse.ArgumentParser().parse_known_args()[1][0])
p=P/'docs/checks/v54-upstream-20261104/test-naming.py'
s=p.read_text()
s=s.replace("for key, folder in [('before', D/'before'), ('after', Path('.'))]:", "for key, folder in [('before', P), ('after', C)]:")
s=s.replace("(folder/'js'/p).read_text()", "(folder/'js'/p.replace('-54.js', '-55.js' if key=='after' else '-54.js')).read_text()")
s=s.replace("'eicos'","'icos'").replace("10-nonyleicosane","10-nonylicosane").replace("C20 eicos spelling follows upstream CAS convention, not IUPAC preferred icos.","C20 uses approved upstream IUPAC icos spelling.")
s=s.replace("(D/'naming-results.json').write_text", "(H/'naming-results.json').write_text")
# Record the actual candidate files; iupac55 may be managed concurrently by root.
s=s.replace("hashlib.sha256(Path(p).read_bytes()).hexdigest()", "hashlib.sha256((C/p.replace('-54.js','-55.js')).read_bytes()).hexdigest()")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'P':P,'H':H,'C':C})
