#!/usr/bin/env python3
"""Read the unified integral collection on Hoffman."""
import argparse,gzip,lzma,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES={'inputs':('target_integrals','inputs.jsonl.gz'),
       'references':('master_to_target','references.jsonl.gz'),
       'traces':('master_to_target','elimination_traces.jsonl.gz'),
       'identities':('master_to_target','identities.jsonl.gz'),
       'proofs':('master_to_target','construction_proofs.jsonl.gz'),
       'seeds':('master_to_target','candidate_seeds.json'),
       'symmetries':('master_to_target','symmetries.json'),
       'definition':('master_integrals','definition.json'),
       'masters':('master_integrals','masters.json'),
       'metadata':('master_to_target','metadata.json')}
def records(family,kind='inputs'):
    if kind not in FILES:raise ValueError('Unknown record kind: '+kind)
    if not family or not family.replace('_','').isalnum():raise ValueError('Invalid family identifier')
    category,filename=FILES[kind]
    path=ROOT/category/'families'/family/filename
    if not path.exists() and path.suffix=='.gz':path=path.with_suffix('.xz')
    op=lzma.open if path.suffix=='.xz' else gzip.open if path.suffix=='.gz' else open
    with op(str(path),'rt',encoding='utf-8') as f:
        if '.jsonl' in filename:
            for line in f:
                if line.strip():yield json.loads(line)
        else:yield json.load(f)
def linked_target(identifier):
    family=identifier.split(':')[0]
    data={}
    for kind in ['inputs','references','traces']:
        match=next((x for x in records(family,kind) if x['id']==identifier),None)
        if match is None:raise KeyError(identifier+' missing from '+kind)
        data[kind]=match
    data['definition']=next(records(family,'definition'))
    basis=next(records(family,'masters'))
    required=set(data['references']['master_ids'])
    data['masters']=[m for m in basis['masters'] if m['id'] in required]
    data['master_basis_file']='master_integrals/families/'+family+'/masters.json'
    return data
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--family');p.add_argument('--kind',choices=list(FILES),default='inputs')
    p.add_argument('--target',help='Return one target with its master coefficients, seeds and elimination trace.')
    p.add_argument('--limit',type=int,default=1);a=p.parse_args()
    if a.target:
        print(json.dumps(linked_target(a.target),sort_keys=True));return
    if not a.family:p.error('--family or --target is required')
    if a.limit<1:p.error('--limit must be positive')
    for i,row in enumerate(records(a.family,a.kind)):
        print(json.dumps(row,sort_keys=True))
        if i+1>=a.limit:break
if __name__=='__main__':main()
