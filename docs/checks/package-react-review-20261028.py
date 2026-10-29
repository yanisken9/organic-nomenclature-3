"""Create the approved review ZIP from an explicit source allowlist; never build/edit the app."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[2]
output = Path('/tmp/namelecule-react-package-20261028')
output.mkdir(exist_ok=True)
package_root = 'Namelecule-React-Review-2026-10-28'
archive = output / 'Namelecule_React_Αξιολόγηση_28-10-2026.zip'
selected = set()
for directory in ['react-preview', 'js', 'css', 'jsme', 'mols', 'scenarios', 'assets', 'imgs', 'spt', 'design/assets']:
    for p in (root / directory).rglob('*'):
        if p.is_file() and not any(part.startswith('.') or part in ['node_modules', '__pycache__'] for part in p.relative_to(root).parts):
            if p.suffix.lower() not in ['.zip', '.log', '.pyc']:
                assert not p.is_symlink(), p
                selected.add(p)
for name in ['index.html', 'mulermoc-nom-52.html', 'design/welcome-proposal.html', 'design/theory-library.html', 'design/ethanol-model.html']:
    selected.add(root / name)
files = {str(p.relative_to(root)): p.read_bytes() for p in sorted(selected)}
for name in ['serve.py', 'README.txt']:
    files[name] = (root / 'docs/packaging/react-review-20261028' / name).read_bytes()
manifest = {
    'snapshotDate': '2026-10-28',
    'reactCatalog': {'molecules': 126, 'forms2D': 377, 'lessons': 12, 'steps': 283},
    'sharedMain': {'version': 52, 'molecules': 136, 'acids': 21, 'lessons': 14, 'steps': 337},
    'requiresInternet': True,
    'buildRegenerated': False,
    'files': {name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)} for name, data in sorted(files.items())},
}
files['PACKAGE-MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name, data in sorted(files.items()):
        info = zipfile.ZipInfo(package_root + '/' + name, date_time=(2026, 10, 28, 12, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, data)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name, data in files.items():
        assert z.read(package_root + '/' + name) == data
sha = hashlib.sha256(archive.read_bytes()).hexdigest()
checksum = archive.with_suffix('.zip.sha256')
checksum.write_text(sha + '  ' + archive.name + '\n')
print(json.dumps({'archive': str(archive), 'files': len(files), 'bytes': archive.stat().st_size, 'sha256': sha}, ensure_ascii=False))
