"""Single separately granted stage-specific Continue diagnostic; no launch at import.

Reuses the frozen original runner and its genuine UI answers. Replaces only its
in-memory observation code with the recorded stage-observation.js artifact.
Transparent observation wrappers change test runtime execution, not source bytes.
"""
from pathlib import Path
import ast, hashlib, os

HERE_STAGE = Path(__file__).resolve().parent
assert os.environ.get('NAMELECULE_FOUR_GAME_CONTINUE_STAGE_DIAGNOSTIC') == 'granted', 'New root exclusive Firefox slot grant required'
base = HERE_STAGE/'runner.py'
assert hashlib.sha256(base.read_bytes()).hexdigest() == 'd4332b3d8383dbad2c0a6a91b196bbf0d460a2a6d00a333338c40581cc0d31a9', 'Original runner drift'
observation = HERE_STAGE/'stage-observation.js'
tree_stage = ast.parse(base.read_text())
changed = set()
for item in tree_stage.body:
 if isinstance(item, ast.Assign) and any(isinstance(n,ast.Name) and n.id=='OBSERVE' for n in item.targets):
  item.value = ast.Constant(value=observation.read_text()); changed.add('OBSERVE')
 if isinstance(item, ast.Assign) and any(isinstance(n,ast.Name) and n.id=='DEST' for n in item.targets):
  for descendant in ast.walk(item.value):
   if isinstance(descendant,ast.Constant) and descendant.value=='run-':descendant.value='run-stage-';changed.add('DEST')
 if isinstance(item,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='OUT' for n in item.targets):
  item.value.keys.extend([ast.Constant(value='controlledInstrumentation'),ast.Constant(value='observationSHA256'),ast.Constant(value='baseRunnerSHA256')])
  item.value.values.extend([ast.Constant(value='Runtime observational wrappers around main iframe remove/fScenarioGo and native speechSynthesis.cancel/Jmol.script; preserves original this,args,return,exceptions. This is not identical uninstrumented execution.'),
    ast.Constant(value=hashlib.sha256(observation.read_bytes()).hexdigest()),ast.Constant(value=hashlib.sha256(base.read_bytes()).hexdigest())]);changed.add('OUT')
 for subitem in ast.walk(item):
  if isinstance(subitem,ast.Try):
   for index, statement in enumerate(subitem.body):
    if isinstance(statement,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='trace_phase' for n in statement.targets) and isinstance(statement.value,ast.Constant) and statement.value.value=='activation-pending':
     proof=ast.parse("with trace_lock:\n proof_packets=[r['browser'] for r in trace if r['browser'].get('reason')=='stage-wrappers-installed']\ncheck(len(proof_packets)==1 and len(proof_packets[0]['wrappers'])==6 and all(item['installed'] for item in proof_packets[0]['wrappers']),'all6 observation wrappers/pagehide captures installed',proof_packets)").body
     subitem.body[index:index]=proof;changed.add('proof');break
assert changed=={'OBSERVE','DEST','OUT','proof'}, changed
os.environ['NAMELECULE_FOUR_GAME_CONTINUE_DIAGNOSTIC']='granted'
exec(compile(ast.fix_missing_locations(tree_stage),str(base),'exec'))
