from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();H=R/'docs/checks/alkane-pool-implementation-20261116'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'role':'Developer source verification; not browser or independent review','viewerChanges':[]}
addition='''  // Registered, verified additions can opt into the same display calibration
  // through data. Existing library paths keep their original behavior.
  const registeredAlkaneScale = (() => {
    try {
      const entry = typeof nameExamples !== "undefined" && nameExamples[selectedMol];
      return mode2D === "expanded" && entry?.displayPolicy === "namelecule-alkane-20261030" &&
        allAtomsTypeList.length > 0 && allAtomsTypeList.every(type => type === "C" || type === "H") &&
        bondList.every(bond => bond[2] === 1) &&
        typeof fGetMoleculeClassification === "function" && fGetMoleculeClassification().seriesKey === "alkanes";
    } catch (_) { return false; }
  })();
'''
for v in (55,56,57):
 p=f'js/mulermoc-nom-molview-{v}.js';s=(R/p).read_text();b=(H/'before'/p).read_text()
 assert s.count(addition)==1
 restored=s.replace(addition,'').replace('(!registeredAlkaneScale && !etherScale','(!etherScale')
 assert restored==b,p
 subprocess.run(['node','--check',str(R/p)],check=True)
 report['viewerChanges'].append({'path':p,'before':sha(H/'before'/p),'after':sha(R/p),'allOtherBytesIdentical':True})
base=json.loads((H/'baseline.json').read_text())
report['coresUnchanged']=all(sha(R/p)==v for p,v in base['cores'].items());assert report['coresUnchanged']
report['HEAD']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert report['HEAD']==base['HEAD']
report['indexUnchanged']=sha(R/'.git/index')==base['indexSHA256'];assert report['indexUnchanged']
old=json.loads((R/'docs/checks/v57-sync-20261115/baseline.json').read_text())['protected']
approved=set(base['beforeHashes'])|set(base['newPaths'])|{f'js/mulermoc-nom-molview-{v}.js' for v in (55,56,57)}
mismatch=[p for p,v in old.items() if p not in approved and sha(R/p)!=v]
report['priorRecoveryProtectedPathsChecked']=len([p for p in old if p not in approved]);report['priorRecoveryMismatches']=mismatch;assert not mismatch,mismatch
report['approvedPreservation']={p:sha(R/p) for p in ['scenarios/alkanes-user-3.scenario.json','games/data/alkane-structures.json','mulermoc-nom-55.html','mulermoc-nom-56.html']}
(H/'root/shared-calibration-source.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
