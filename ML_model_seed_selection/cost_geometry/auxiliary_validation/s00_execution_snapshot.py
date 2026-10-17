"""Collect two validation cases after the planar reserved test finishes."""
import json,os,time
from s03_train import evaluate
from s00_policy import *

def main():
 graph='nonplanar_box';p=rt.read(HERE/'protocols'/('cost_'+graph+'.json'))
 folder=HERE/'auxiliary_validation';folder.mkdir(exist_ok=True)
 (folder/'README.md').write_text('This worker precomputes the last two cases from the first nonplanar validation profile.\nIt uses the same frozen candidate boundaries and timing code.\nIt preserves every result and only fills absent main validation records.\nExisting records keep priority.\nNo reserved target or timing enters this work.\n')
 cases=[c for c in p['validation'] if '_h841_' in c['id'] and c['shape'] in ['distributed3','distributed4']]
 inputs.write(folder/'protocol.json',dict(cases=cases,candidates=p['candidates'],reason='Independent validation collection on the third worker. Main and helper records both remain available.'))
 promoted=[]
 for c in reversed(cases):
  for theta in p['candidates']:
   for rep in range(3):evaluate(c,theta,'supplementary_validation',rep)
  for source in folder.glob(c['id']+'_*.json.gz'):
   dest=HERE/'cost_validation'/source.name
   if dest.exists():continue
   temporary=dest.with_name(dest.name+'.prefill')
   temporary.write_bytes(source.read_bytes())
   try:
    # Link the independent copy to the final name without replacing any record.
    os.link(str(temporary),str(dest));promoted.append(dict(source=str(source.relative_to(HERE)),destination=str(dest.relative_to(HERE)),time=time.time(),sha256=inputs.sha(source)))
   except FileExistsError:pass
   finally:temporary.unlink()
  inputs.write(folder/'promotion.json',dict(records=promoted))
 inputs.write(folder/'completion.json',dict(complete=True,promoted=len(promoted)))
if __name__=='__main__':main()
