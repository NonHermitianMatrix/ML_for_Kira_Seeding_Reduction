"""Apply a frozen scattering selector with a supplied master basis."""
import argparse,json
from pathlib import Path
from s00_scattering_study import HERE,ROOT,model_path,sha,workflow,save

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--case',required=True,help='Case ID from cases.json.')
 ap.add_argument('--basis',type=Path,required=True,help='JSON list of master index vectors.')
 ap.add_argument('--policy',choices=['auto','native','seed','equation'],default='native')
 ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args();manifest=json.loads((HERE/'cases.json').read_text());frozen=json.loads((HERE/'freeze.json').read_text())
 case=next(c for c in manifest['cases'] if c['id']==args.case)
 basis=json.loads(args.basis.read_text());assert isinstance(basis,list) and basis
 policy=args.policy
 if policy=='auto':
  choices=[(v['ratio'],t) for t in ['seed','equation'] for v in [frozen['policies'][case['topology_group']+'_'+t]] if v['activate']]
  policy=min(choices)[1] if choices else 'native'
 threshold=.01
 if policy!='native':
  weights=model_path(case,policy)
  assert sha(weights)==frozen['weights'][str(weights.relative_to(ROOT))]
  threshold=frozen['policies'][case['topology_group']+'_'+policy]['threshold']
 result=workflow(case,None,policy,threshold,basis=basis)
 result['requested_policy']=args.policy
 assert args.output.resolve().parent==HERE/'model_test','Keep outputs in the bounded project test folder.'
 save(args.output,result)
 print(json.dumps({k:result[k] for k in ['case','task','success','fallback_count','complete_seconds']}))
 if not result['success']:raise SystemExit(1)
if __name__=='__main__':main()
