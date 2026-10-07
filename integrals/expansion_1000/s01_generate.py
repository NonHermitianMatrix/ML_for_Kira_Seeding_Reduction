"""Generate bounded coupled vacuum families and reverse constructions from their exact masters."""
import argparse,collections,lzma,hashlib,json,os,random,resource,time,subprocess
from pathlib import Path
from s00_exact import *
HERE=Path(__file__).resolve().parent;DATA=HERE.parent;ROOT=DATA.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+".part")
 tmp.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(tmp,p)
def xzwrite(p,records):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+".part")
 with lzma.open(tmp,"wb",preset=3) as out:
  for rec in records:out.write((json.dumps(rec,separators=(",",":"),sort_keys=True)+"\n").encode())
 assert tmp.stat().st_size<67108864
 os.replace(tmp,p)
def profiles():
 # Positive distinct squared masses; rho_1=1 fixes the common rescaling.
 return [(i,tuple([1]+[2+i*3+j*(i+2) for j in range(1+(i-1)%3)])) for i in range(351,1351)]
def splits():
 ids=list(range(351,1351));random.Random(202610061000).shuffle(ids)
 return {i:("train" if i in set(ids[:700]) else "test") for i in range(351,1351)}
def integral(L,b):return (1,)*L+b
def sources(L,rho):
 r=len(rho);out=[];by={}
 def append(row,src):
  assert row and not oracle_row(L,rho,row)
  eid="E%06d"%(len(out)+1);leading=max(row,key=order)
  rec=dict(id=eid,leading_indices=list(leading),terms=terms(row),
    modular_terms=field(row,SAMPLES[0]["point"],SAMPLES[0]["prime"]),source=src)
  out.append((rec,row));by.setdefault(leading,[]).append(eid)
 for b in all_b(r,5):
  a=integral(L,b);row={a:{(1,0):F(L),(0,0):F(-2*(L+sum(b)))}}
  for j,bj in enumerate(b):
   if bj:
    c=list(b);c[j]+=1;row[integral(L,tuple(c))]={(0,1):F(2*bj*rho[j])}
  append(row,dict(kind="ibp",seed=list(a),operator=dict(
   name="sum_i d/d ell_i dot ell_i",
   canonical_operator_decomposition=[dict(k=i,v=i,multiplier=1) for i in range(L)])))
 for b in all_b(r,6):
  active=[j for j,x in enumerate(b) if x]
  for i in active:
   for j in active:
    if i>=j:continue
    bi=list(b);bi[i]-=1;bj=list(b);bj[j]-=1
    row={integral(L,b):{(0,1):F(rho[i]-rho[j])},integral(L,tuple(bi)):P(-1),integral(L,tuple(bj)):P(1)}
    append(row,dict(kind="partial_fraction",mass_slots=[i,j],
      identity="D_i-D_j=(rho_i-rho_j)*m2",ibp_seed=None))
 return out,by
class UnluckySample(Exception):pass

def generate(L,profile,rho):
 fid="vacuum_L%02d_profile%03d"%(L,profile)
 folders={k:DATA/k/"families"/fid for k in ("master_integrals","target_integrals","master_to_target")}
 mb,tb,rb=[folders[k] for k in folders];done=rb/"manifest.json"
 signature={p.name:sha(p) for p in HERE.glob("s0[01]_*.py")}
 if done.exists():
  saved=json.loads(done.read_text(encoding="utf-8"))
  assert saved["generator"]==signature
  assert all(sha(DATA/p)==v["sha256"] for p,v in saved["files"].items())
  return saved["summary"]
 start=time.time();r=len(rho);split=splits()[profile];massmasters=[integral(L,tuple(int(i==j) for i in range(r))) for j in range(r)]
 masters=set(massmasters)
 edges=[dict(vertices=[0,r],momentum="ell%d"%(i+1),mass_squared="0") for i in range(L)]
 edges += [dict(vertices=[j,j+1],momentum="+".join("ell%d"%(i+1) for i in range(L)),mass_squared=str(v)+"*m2") for j,v in enumerate(rho)]
 assert len(edges)-(r+1)+1==L
 definition=dict(id=fid,title="Coupled %d-loop vacuum integral, mass profile %d"%(L,profile),
   loop_momenta=["ell%d"%(i+1) for i in range(L)],external_momenta=[],invariants=["m2"],
   scalarproduct_rules=[],propagators=[dict(momentum=e["momentum"],mass_squared=e["mass_squared"],
      denominator="("+e["momentum"]+")**2+("+e["mass_squared"]+")") for e in edges],
   normalization="product d^d ell/pi^(d/2), Euclidean momenta",prescription="Euclidean analytic continuation",
   dimension="d=4-2*epsilon",top_level_sectors=[(1<<(L+r))-1],
   assumptions=["m2>0","generic complex d","distinct positive mass ratios","massless powers fixed to one; nonnegative massive powers with nonzero sum"],
   mass_ratios=list(rho),graph=dict(vertices=list(range(r+1)),edges=edges,loops=L),
   scope="Restricted scalar vacuum family with dependent massive denominators; no arbitrary numerator or complete irreducible scalar-product basis.")
 basis=dict(schema_version=2,family=fid,status="analytically_verified_restricted_basis",
   scope=definition["scope"],masters=[dict(id=fid+":M%03d"%(j+1),family=fid,indices=list(a),
     sector=order(a)[0],mass_dimension="%d*d-%d"%(L,2*sum(a)),
     expression=fid+"["+key(a)+"]") for j,a in enumerate(massmasters)],
   analytic_formula="M_j=(rho_j*m2)**(L*d/2-L-1)*Gamma(L-(L-1)*d/2)*Gamma(d/2-1)**L*Gamma(L+1-L*d/2)/Gamma(d/2)",
   basis_argument="Partial fractions and Euler IBP span this restricted domain; distinct mass-ratio exponential functions of d are independent over rational functions in d,m2.",
   solver="analytic partial fractions and total Euler IBP; no Kira run claimed")
 source,by=sources(L,rho);equations={rec["id"]:row for rec,row in source}
 source_records={rec["id"]:rec for rec,row in source}
 def reduce(row,tid,trace=True):
  original=dict(row);steps=[];ops=collections.Counter()
  while set(row)-masters:
   assert len(steps)<256
   pivot=max(set(row)-masters,key=order);allowed=sorted(by[pivot]);choices=[]
   for eid in allowed:
    src=equations[eid];factor=div(row[pivot],src[pivot]);after=rowadd(row,src,scale(factor,-1))
    assert not after.get(pivot)
    choices.append(((len(set(after)-masters),len(after),1+2*len(src),eid),eid,after,factor))
   _,eid,after,factor=min(choices,key=lambda x:x[0]);src=equations[eid]
   operations=dict(divisions=1,multiplications=len(src),subtractions=len(src));ops.update(operations)
   sample=SAMPLES[0];point,p=sample["point"],sample["prime"]
   steps.append(dict(before=field(row,point,p),after=field(after,point,p),
      before_nonzeros=len(row),after_nonzeros=len(after),fill_in=len(set(after)-set(row)),
      cancelled_entries=len(set(row)-set(after)),allowed_pivot_equations=allowed,pivot_equation=eid,
      pivot_indices=list(pivot),factor=expr(factor),factor_mod_p=ev(factor,point,p),
      pivot_value=ev(src[pivot],point,p),target_pivot_value=ev(row[pivot],point,p),operations=operations))
   # Cross multiplication checks each chosen row update in three independent finite fields.
   for s in SAMPLES:
    a=field(row,s["point"],s["prime"]);b=field(src,s["point"],s["prime"]);c=field(after,s["point"],s["prime"]);p=s["prime"];pk=key(pivot)
    if pk not in b or pk not in a:raise UnluckySample("Recorded pivot vanishes at a verification sample")
    assert all(c.get(k,0)*b[pk]%p==(a.get(k,0)*b[pk]-a[pk]*b.get(k,0))%p for k in set(a)|set(b)|set(c))
   row=after
  assert row==oracle_row(L,rho,original)
  return row,steps,dict(ops)
 # Scalar proofs are generated first; reverse replay constructs all later targets from masters.
 roots=[integral(L,b) for b in all_b(r,5) if sum(b)>=2]
 roots.sort(key=lambda a:(not all(a[L:]),sum(a[L:]),a))
 full_roots=[a for a in roots if all(a[L:]) and sum(a[L:])>r]
 proofs={}
 for a in roots:
  reduced,steps,ops=reduce({a:P(1)},"scalar")
  proofs[a]=(reduced,steps,ops)
 inputs=[];references=[];traces=[];construction=[];seen=set();seedtotal=0;empty=0;singles=0
 rng=random.Random(10000*L+profile);attempt=0;unlucky=0
 while len(inputs)<128:
  attempt+=1;assert attempt<10000
  if len(inputs)<min(32,len(roots)):
   weights={roots[len(inputs)]:P(1)}
  else:
   picked=[rng.choice(full_roots)]
   picked+=rng.sample([a for a in roots if a not in picked],rng.randrange(0,3))
   # Equalize physical mass dimension of every term with powers of m2.
   B=max(sum(a[L:]) for a in picked)
   weights={a:{(rng.randrange(0,2),sum(a[L:])-B):F(rng.choice([-3,-2,-1,1,2,3]),rng.choice([1,2,3]))} for a in picked}
  canonical=tuple((a,expr(c)) for a,c in sorted(weights.items()))
  if canonical in seen:continue
  seen.add(canonical);tid=fid+":T%05d"%(len(inputs)+1)
  expected=oracle_row(L,rho,weights)
  # Actually start at the master combination and add reversed source identities.
  built=dict(expected);reverse=[]
  for a,w in sorted(weights.items()):
   _,ss,_=proofs[a]
   current={a:P(1)};factors=[]
   for step in ss:
    src=equations[step["pivot_equation"]];piv=tuple(step["pivot_indices"])
    f=div(current[piv],src[piv]);factors.append((step["pivot_equation"],f));current=rowadd(current,src,scale(f,-1))
   for eid,f in reversed(factors):
    g=mul(w,f);built=rowadd(built,equations[eid],g)
    reverse.append(dict(source_equation=eid,multiplier=expr(g),operation="add multiple of exact zero identity"))
  assert built==weights
  try:reduced,steps,ops=reduce(built,tid)
  except UnluckySample:
   unlucky+=1;continue
  ids=list(dict.fromkeys(s["pivot_equation"] for s in steps))
  seeds=sorted({tuple(source_records[e]["source"]["seed"]) for e in ids if source_records[e]["source"]["kind"]=="ibp"})
  partial=[e for e in ids if source_records[e]["source"]["kind"]=="partial_fraction"]
  kind="single_integral" if len(built)==1 and next(iter(built.values()))==P(1) else "integral_expression"
  singles+=int(kind=="single_integral");seedtotal+=len(seeds);empty+=int(not seeds)
  paths=dict(family_definition=str((mb/"definition.json").relative_to(DATA)),master_basis=str((mb/"masters.json").relative_to(DATA)),
     candidate_seeds=str((rb/"candidate_seeds.json").relative_to(DATA)),equation_pool=str((rb/"identities.jsonl.xz").relative_to(DATA)),
     elimination_records=str((rb/"elimination_traces.jsonl.xz").relative_to(DATA)),reference_records=str((rb/"references.jsonl.xz").relative_to(DATA)))
  inputs.append(dict(id=tid,family=fid,kind=kind,terms=terms(built),
     modular_terms=field(built,SAMPLES[0]["point"],SAMPLES[0]["prime"]),sample=0,
     integral_order="protected_masters_then_sector_dots_numerator_sum_positive_sum_indices",split=split,
     mass_dimension="%d*d-%d"%(L,2*(L+max(sum(a[L:]) for a in built))),**paths))
  refsamples=[dict(s,master_coefficients=field(reduced,s["point"],s["prime"])) for s in SAMPLES]
  references.append(dict(id=tid,family=fid,master_coefficients=terms(reduced),
     master_ids=[basis["masters"][massmasters.index(a)]["id"] for a in sorted(reduced)],
     sufficient_seeds=[list(a) for a in seeds],source_equations=ids,partial_fraction_equations=partial,
     reduction_steps=len(steps),arithmetic_operations=ops,samples=refsamples,
     construction=dict(kind="reverse_exact_identities",record=str((rb/"construction_proofs.jsonl.xz").relative_to(DATA))),
     origin="reverse_from_masters",optimality="known valid sequence; no minimum is claimed",**paths))
  traces.append(dict(id=tid,prime=SAMPLES[0]["prime"],sample=0,steps=steps,
      final_master_row=field(reduced,SAMPLES[0]["point"],SAMPLES[0]["prime"]),total_operations=ops,
      system_representation="immutable source equations plus one changing target row"))
  construction.append(dict(id=tid,initial_master_coefficients=terms(expected),steps=reverse,final_terms=terms(built),
      scalar_proofs=[dict(indices=list(a),coefficient=expr(w)) for a,w in sorted(weights.items())],
      checks=dict(exact_symbolic_reverse_replay=True,independent_partial_fraction_oracle=True,finite_field_samples=3)))
 nc=len(all_b(r,5))
 summary=dict(family=fid,loops=L,profile=profile,mass_ratios=list(rho),split=split,
    group="coupled_vacuum_mass_profile_%03d"%profile,master_count=r,
    counts=dict(targets=len(inputs),single_integral=singles,integral_expression=len(inputs)-singles,
      candidate_seed_labels=nc*len(inputs),positive_seed_labels=seedtotal,empty_reference_seed_sets=empty),
    rejected_unlucky_targets=unlucky,source_equations=len(source),elimination_steps=sum(len(t["steps"]) for t in traces),
    elapsed_seconds=time.time()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 write(mb/"definition.json",definition);write(mb/"masters.json",basis)
 (mb/"masters.txt").write_text("\n".join(m["expression"] for m in basis["masters"])+"\n",encoding="utf-8")
 write(rb/"candidate_seeds.json",dict(indices=[list(integral(L,b)) for b in all_b(r,5)],
    bounds=dict(massless_powers=1,massive_total_power_max=5,source_total_power_max=6),
    note="Complete Euler-IBP seed pool within stated bounds. Partial-fraction identities have no IBP seed."))
 xzwrite(rb/"identities.jsonl.xz",[rec for rec,row in source]);xzwrite(tb/"inputs.jsonl.xz",inputs)
 xzwrite(rb/"references.jsonl.xz",references);xzwrite(rb/"elimination_traces.jsonl.xz",traces)
 xzwrite(rb/"construction_proofs.jsonl.xz",construction)
 xzwrite(rb/"scalar_proofs.jsonl.xz",[dict(indices=list(a),master_coefficients=terms(v[0]),steps=v[1],operations=v[2]) for a,v in sorted(proofs.items())])
 write(rb/"symmetries.json",[]);write(rb/"metadata.json",dict(summary,status="generated_and_exactly_checked",samples=SAMPLES,
    identity_checks="Every identity vanishes under an independent partial-fraction oracle.",
    limitations="Restricted coupled vacuum families; mass profiles share topology. Reference sequences and seed sets are sufficient, with no optimality claim."))
 for kind,folder in folders.items():
  (folder/"README.md").write_text("# "+fid+"\n\n"+definition["title"]+". This restricted Euclidean family has "+str(L)+" loops and "+str(r)+" masters. Massless propagator powers equal one; massive powers vary within the stored bounds.\n\n"+
    "definition.json and masters.json in the matching master folder define the integral and basis. The target folder stores 128 targets. The relation folder stores source identities, separate IBP seed labels, exact reverse constructions, scalar proofs, reference master coefficients and elimination traces at three finite-field samples. Algebraic partial fractions carry no IBP seed. Reference paths are sufficient; minimality is not established. See integrals/expansion_1000/README.md.\n",encoding="utf-8")
 files={str(p.relative_to(DATA)):dict(bytes=p.stat().st_size,sha256=sha(p)) for folder in folders.values() for p in folder.iterdir() if p.is_file() and p.name!="manifest.json"}
 write(done,dict(family=fid,generator=signature,files=files,summary=summary))
 return summary
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--loops",type=int,nargs="+",default=list(range(1,13)));ap.add_argument("--profiles",type=int,nargs="+");args=ap.parse_args()
 started=time.time();results=[]
 for L in args.loops:
  for profile,rho in profiles():
   if args.profiles and profile not in args.profiles:continue
   if len(results)%50==0:
    used=int(subprocess.check_output(["du","-s","-B1",str(ROOT)]).split()[0]);assert used<7000000000,used
   result=generate(L,profile,rho);results.append(result)
   write(HERE/"progress.json",dict(completed=len(results),latest=result,elapsed_seconds=time.time()-started))
   if len(results)%10==0:print(json.dumps(dict(completed=len(results),latest=result)),flush=True)
 write(HERE/("pilot_summary.json" if args.profiles else "generation_summary.json"),dict(status="complete",families=results,
   elapsed_seconds=time.time()-started,master_count=sum(v["master_count"] for v in results),targets=sum(v["counts"]["targets"] for v in results)))
 print("Finished",len(results),"families",flush=True)
if __name__=="__main__":main()
