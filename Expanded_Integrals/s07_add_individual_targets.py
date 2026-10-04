#!/usr/bin/env python3
"""Promote checked numerator-integral proofs into held-out individual targets."""
import argparse,gzip,hashlib,json,os,resource,sys,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'master_to_target'))
import s00_ibp as ibp
import s01_generate_targets as gen
import s02_validate_targets as val
from s00_prepare_families import POINTS,PRIMES
ibp.POINTS=POINTS;ibp.PRIMES=PRIMES
gen.POINTS=POINTS;gen.PRIMES=PRIMES
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def load(tf,name):return json.load(tf.extractfile(name))
def lines(tf,name):return [json.loads(line) for line in tf.extractfile(name) if line.strip()]
def run(index):
 start=time.monotonic()
 definitions=json.loads((ROOT/'families.json').read_text())['families']
 definition=definitions[index-1];name=definition['id'];split=definition['profile']['split']
 if split=='train':return
 metadata=json.loads((ROOT/'families'/(name+'.json')).read_text())
 assert metadata['status']=='validated'
 archive=ROOT/'families'/metadata['archive']
 assert sha(archive)==metadata['archive_sha256']
 with tarfile.open(str(archive),'r:gz') as tf:
  mp='Master_Integrals/families/'+name+'/'
  tp='master_to_target/families/'+name+'/'
  masters=load(tf,mp+'masters.json')
  equations=lines(tf,tp+'identities.jsonl')
  proofs=lines(tf,tp+'construction_proofs.jsonl')
  previous=lines(tf,tp+'inputs.jsonl')
 existing={tuple(p['terms'][0]['indices']) for p in previous if p['kind']=='single_integral'}
 selected=[p for p in proofs if p['master_coefficients'] and all(x!=0 for x in p['indices']) and any(x<0 for x in p['indices'])
           and tuple(p['indices']) not in existing]
 fam=ibp.Family(definition,masters)
 docs={e['id']:e for e in equations}
 choices={}
 for e in equations:choices.setdefault(tuple(e['leading_indices']),[]).append(e['id'])
 proofmap={tuple(p['indices']):p for p in proofs}
 recipes={a:p['equation'] for a,p in proofmap.items()}
 needed=set()
 def dependencies(a):
  if a in fam.master_set:return
  p=proofmap[a];eqid=p['equation']
  if eqid in needed:return
  needed.add(eqid)
  for b in p['dependencies']:dependencies(tuple(b))
 for p in selected:dependencies(tuple(p['indices']))
 byid={}
 for eqid in needed:
  e=docs[eqid];source=e['source'];row=fam.parse_row(e['terms'])
  if source['kind']=='ibp':
   op=source['operator']
   assert row==fam.operator_row(source['seed'],op['k'],op['vector_coefficients'])
  else:
   assert row==fam.symmetry_row(source['input_indices'],fam.symmetries[source['symmetry']])
  byid[eqid]=dict(row=row,lead=tuple(e['leading_indices']),source=source)
 inputs=[];references=[];traces=[]
 steps_checked=0;sectors={}
 for number,p in enumerate(selected,1):
  a=tuple(p['indices']);target={a:fam.one};expected=fam.parse_row(p['master_coefficients'])
  reduced,steps,used,cost=gen.trace(fam,target,recipes,byid,choices)
  assert reduced==expected
  identifier=name+':U%05d'%number
  source_ids=list(dict.fromkeys(used))
  seeds=sorted({tuple(byid[e]['source']['seed']) for e in used if byid[e]['source']['kind']=='ibp'})
  for b,c in expected.items():assert fam.mass_degree(c)==sum(b)-sum(a)
  inp=dict(id=identifier,family=name,split=split,kind='single_integral',
    terms=fam.serialize_row(target),modular_terms=fam.numeric_row(target,0),sample=0,
    integral_features=[dict(indices=list(a),**ibp.complexity(a))],
    mass_dimension='%d*d-(%d)'%(fam.L,2*sum(a)),
    candidate_seeds='candidate_seeds.json',equation_pool='identities.jsonl',
    master_basis='../../../Master_Integrals/families/'+name+'/masters.json',
    integral_order='protected_masters_then_sector_dots_numerator_sum_positive_sum_indices',
    heldout_criterion='All four family expressions occur with nonzero powers; full kinematic profile is held out.',
    source_archive='families/'+metadata['archive'])
  ref=dict(id=identifier,family=name,split=split,origin='checked_numerator_integral',
    master_coefficients=fam.serialize_row(expected),
    construction=dict(kind='identity_closure',root_indices=list(a),proof_library='construction_proofs.jsonl'),
    sufficient_seeds=[list(s) for s in seeds],source_equations=source_ids,
    source_symmetries=[e for e in used if byid[e]['source']['kind']=='symmetry'],
    reduction_steps=len(steps),arithmetic_operations=cost,
    optimality='known_valid_sequence; no minimum is claimed',
    samples=[dict(sample=i,prime=PRIMES[i],point={k:POINTS[i][k] for k in fam.names},
                  master_coefficients=fam.numeric_row(expected,i)) for i in range(3)])
  trace=dict(id=identifier,sample=0,prime=PRIMES[0],steps=steps,
    final_master_row=fam.numeric_row(expected,0),total_operations=cost,
    system_representation='immutable source equations plus one changing target row')
  # Rebuild serialized rows and replay every operation and all three numeric fields.
  current=fam.parse_row(inp['terms'])
  computed_cost=dict(divisions=0,multiplications=0,subtractions=0)
  actual_used=[]
  for step in trace['steps']:
   pivot=tuple(step['pivot_indices']);eq=byid[step['pivot_equation']]
   assert pivot==max((b for b in current if b not in fam.master_set),key=fam.order)==eq['lead']
   assert step['allowed_pivot_equations']==choices[pivot]
   multiplier=current[pivot]/eq['row'][pivot]
   assert fam.parse(step['factor'])==multiplier
   after=gen.add_scaled(fam,current,eq['row'],-multiplier)
   assert step['before']==fam.numeric_row(current,0)
   assert step['after']==fam.numeric_row(after,0)
   assert step['before_nonzeros']==len(current) and step['after_nonzeros']==len(after)
   assert step['fill_in']==sum(b not in current for b in after)
   assert step['cancelled_entries']==sum(b not in after for b in current)
   for sample,prime in enumerate(PRIMES):
    numerical=fam.numeric_row(current,sample)
    source=fam.numeric_row(eq['row'],sample)
    factor=numerical[ibp.key(pivot)]*pow(source[ibp.key(pivot)],-1,prime)%prime
    for b,c in source.items():
     value=(numerical.get(b,0)-factor*c)%prime
     if value:numerical[b]=value
     else:numerical.pop(b,None)
    assert numerical==fam.numeric_row(after,sample)
    assert factor==fam.evaluate(multiplier,sample)
   local=dict(divisions=1,multiplications=len(eq['row']),subtractions=len(eq['row']))
   assert local==step['operations']
   for k,v in local.items():computed_cost[k]+=v
   actual_used.append(step['pivot_equation'])
   current=after;steps_checked+=1
  assert current==fam.parse_row(ref['master_coefficients'])
  assert computed_cost==cost and list(dict.fromkeys(actual_used))==source_ids
  assert len(a)==4 and all(x!=0 for x in a) and any(x<0 for x in a)
  assert inp['integral_features']==[dict(indices=list(a),**ibp.complexity(a))]
  sectors[str(ibp.complexity(a)['t'])]=sectors.get(str(ibp.complexity(a)['t']),0)+1
  inputs.append(inp);references.append(ref);traces.append(trace)
 document=dict(family=name,status='validated',split=split,
    source_archive='families/'+metadata['archive'],source_archive_sha256=metadata['archive_sha256'],
    inputs=inputs,references=references,elimination_traces=traces,
    validation=dict(status='passed',targets=len(inputs),
       symbolic_constructions_checked=len(inputs),symbolic_elimination_steps_checked=steps_checked,
       finite_field_points_checked=3,source_rows_rederived=len(needed),
       source_identity_validation='Original archive independently checked every used source identity and all closure proofs.',
       denominator_counts=sectors),
    elapsed_seconds=round(time.monotonic()-start,3),
    peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    source_sha256=sha(Path(__file__)))
 folder=ROOT/'individual_targets';folder.mkdir(exist_ok=True)
 path=folder/(name+'.json.gz');temporary=path.with_suffix('.part')
 with gzip.open(str(temporary),'wt',encoding='utf-8',compresslevel=6) as f:
  json.dump(document,f,separators=(',',':'),sort_keys=True)
 if temporary.stat().st_size>4_000_000:raise RuntimeError('Supplement file size guard')
 temporary.replace(path)
 print(json.dumps(dict(family=name,split=split,targets=len(inputs),steps=steps_checked,
                       elapsed_seconds=document['elapsed_seconds'])),flush=True)
def main():
 if not os.environ.get('JOB_ID'):raise RuntimeError('Use the Hoffman scheduler.')
 task=int(os.environ.get('SGE_TASK_ID','1'))
 definitions=json.loads((ROOT/'families.json').read_text())['families']
 selected=[i for i,f in enumerate(definitions,1) if f['profile']['split']!='train']
 run(selected[task-1])
if __name__=='__main__':main()
