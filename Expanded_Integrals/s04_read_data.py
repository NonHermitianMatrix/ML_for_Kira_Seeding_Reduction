#!/usr/bin/env python3
"""Stream generated records on Hoffman without extracting family archives."""
import argparse,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES={'inputs':'inputs.jsonl','references':'references.jsonl',
       'traces':'elimination_traces.jsonl','identities':'identities.jsonl',
       'proofs':'construction_proofs.jsonl','seeds':'candidate_seeds.json',
       'definition':'definition.json','masters':'masters.json'}
def records(family,kind='inputs'):
    if kind not in FILES: raise ValueError('Unknown record kind')
    if not family.replace('_','').isalnum(): raise ValueError('Invalid family identifier')
    combined=ROOT/'catalog.json'
    overrides=json.loads(combined.read_text()).get('initial_split_overrides',{}) if combined.exists() else {}
    def projected(row):
        if family in overrides and 'split' in row:
            row=dict(row);row['stored_split']=row['split'];row['split']=overrides[family]
        return row
    expanded=ROOT/'families'/(family+'.tar.gz')
    prefix='Master_Integrals' if kind=='masters' else 'master_to_target'
    relative=prefix+'/families/'+family+'/'+FILES[kind]
    if expanded.is_file():
        with tarfile.open(str(expanded),'r:gz') as archive:
            with archive.extractfile(relative) as stream:
                if FILES[kind].endswith('.jsonl'):
                    for line in stream:
                        if line.strip(): yield projected(json.loads(line))
                else: yield projected(json.load(stream))
    else:
        path=ROOT.parent/relative
        with path.open(encoding='utf-8') as stream:
            if FILES[kind].endswith('.jsonl'):
                for line in stream:
                    if line.strip(): yield projected(json.loads(line))
            else: yield projected(json.load(stream))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--family',required=True);p.add_argument('--kind',choices=list(FILES),default='inputs')
    p.add_argument('--limit',type=int,default=1)
    args=p.parse_args()
    if args.limit<1:p.error('--limit must be positive')
    for index,row in enumerate(records(args.family,args.kind)):
        print(json.dumps(row,sort_keys=True))
        if index+1>=args.limit:break
if __name__=='__main__':main()
