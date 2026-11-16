"""Causal guard regressions: actual raw upstream56 vs composed56 functions.
Old harness bodies retained; evidence always redirected to this new directory.
"""
from pathlib import Path
P=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;C=Path('/private/tmp/namelecule-v56-sync-20261115-nqi71wns/candidate')
p=P/'docs/checks/v54-merge-20261109/core/test-corrections55.py';s=p.read_text()
s=s.replace("C=Path(argparse.ArgumentParser().parse_known_args()[1][0])", 'C=Path('+repr(str(C))+')')
s=s.replace("check='--check' in __import__('sys').argv",'check=True')
s=s.replace("D/'before-core55.js'", "P/'docs/checks/v56-sync-20261115/upstream/target/js/mulermoc-nom-core-56.js'")
s=s.replace("D/'before-name-en55.js'", "P/'docs/checks/v56-sync-20261115/upstream/target/js/mulermoc-nom-name-en-56.js'")
s=s.replace("C/'js/mulermoc-nom-core-55.js'", "C/'js/mulermoc-nom-core-56.js'").replace("C/'js/mulermoc-nom-name-en-55.js'", "C/'js/mulermoc-nom-name-en-56.js'")
s=s.replace("out=D/('after-results.json'if check else'before-results.json')", "out=OUT/'preserved-corrections-results.json'")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'OUT':D})
p=P/'docs/checks/v54-merge-20261109/core/test-causal-probes.py';s=p.read_text()
s=s.replace("C=Path(argparse.ArgumentParser().parse_known_args()[1][0])", 'C=Path('+repr(str(C))+')')
s=s.replace("'current54':P/'js/mulermoc-nom-core-54.js'", "'current54':P/'js/mulermoc-nom-core-55.js'")
s=s.replace("P/'docs/checks/v54-merge-20261109/upstream/target/js/mulermoc-nom-core-55.js'", "P/'docs/checks/v56-sync-20261115/upstream/target/js/mulermoc-nom-core-56.js'")
s=s.replace("C/'js/mulermoc-nom-core-55.js'", "C/'js/mulermoc-nom-core-56.js'")
s=s.replace("assert all(x['status']=='named'for x in result['candidate55']['supported'])", "assert all(x['status']=='named'for x in result['candidate55']['supported'][:2]);assert result['candidate55']['supported'][2]['status']=='declined'")
s=s.replace("'off main chain' in result['candidate55']['fork']['error']", "'NOM-DECLINE' in result['candidate55']['fork']['error']")
s=s.replace("assert result['upstream55']['fork']['status']=='named' and 'αιθυλο' in result['upstream55']['fork']['result']['name']", "assert result['upstream55']['fork']['status']=='named' and 'αιθυλο' in result['upstream55']['fork']['result']['name']")
s=s.replace("'fParseSDF3D','fDetectMolType'", "'fParseSDF3D'")
s=s.replace("(H/'causal-probes-results.json').write_text", "(OUT/'causal-probes-results.json').write_text")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p),'OUT':D})
