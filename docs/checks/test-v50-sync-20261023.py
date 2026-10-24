"""Run from repository root. Uses temporary files; does not edit app assets."""
from pathlib import Path
import subprocess, tempfile, json, re
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
def run(path):
    result=subprocess.run([JSC,str(path)],capture_output=True,text=True)
    assert result.returncode==0,(str(path),result.stdout,result.stderr)
    return result.stdout
with tempfile.TemporaryDirectory(prefix='namelecule-v50-tests-') as folder:
    tmp=Path(folder)
    for name in ['test-alkanes-p2-v49.js','test-alkanes-p2-extended-v49.js','test-core-parent-chains-20261022-v49.js']:
        p=tmp/name
        p.write_text((Path('docs/checks')/name).read_text().replace('data_49.js','data_50.js').replace('-49.js','-50.js'))
        print(run(p),flush=True)
    for p in Path('js').glob('*50.js'):
        check=tmp/'syntax.js';check.write_text('new Function('+json.dumps(p.read_text())+');')
        run(check)
    print('PASS v50 JS syntax')
    for old in ['js/jsme-nick-nomeclature-moc2-data_49.js']:
        # Compare complete metadata, insertion order and embedded representations.
        results=[]
        for version in ['49','50']:
            p=tmp/('data'+version+'.js')
            p.write_text('var window={};'+Path(old.replace('49',version)).read_text()+"\nprint(JSON.stringify({names:nameExamples,mols:window.MOL2D}));")
            results.append(json.loads(run(p)))
        assert results[0]==results[1]
        assert list(results[0]['names'])==list(results[1]['names'])
        print('PASS all80 metadata, order and embedded MOLs identical')
    html=Path('mulermoc-nom-50.html').read_text()
    for ref in re.findall(r'(?:src|href)="([^"#]+)"',html):
        if ref.startswith(('http:','https:','//','data:')):continue
        assert Path(ref.split('?')[0]).exists(),ref
    print('PASS local v50 HTML asset paths')
