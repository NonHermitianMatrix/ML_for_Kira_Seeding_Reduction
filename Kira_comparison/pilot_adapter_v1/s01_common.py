"""Public inputs and exact coefficient arithmetic for paired Kira comparisons."""
import collections,gzip,hashlib,importlib.util,json,lzma,os,pathlib,re,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent;DATA=ROOT/"integrals"
SUFF=ROOT/"ML_model_seed_selection/kira_sufficiency_test"
sys.path.insert(0,str(SUFF))
import s02_common as old
import s03_kira_adapter as adapter
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,v):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_name(p.name+".part");t.write_text(json.dumps(v,indent=2,allow_nan=False)+"\n");t.replace(p)
def sha(p):return old.sha(p)
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def ranking(s):return hashlib.sha256(("kira-cost-v1:"+s).encode()).hexdigest()
def load_case(case,size):
 meta=case["meta"];fid=meta["family"]
 targets=sorted(list(old.rows(DATA/meta["inputs"])),key=lambda t:ranking(t["id"]))[:size]
 definition=read(DATA/meta["definition"]);basis=read(DATA/meta["masters"])
 seeds=read(DATA/meta["seeds"])["indices"]
 identities=list(old.rows(old.family_file(fid,"identities.jsonl.gz")))
 return dict(id=fid,meta=meta,domain=case["domain"],definition=definition,basis=basis,
  targets=targets,seeds=[tuple(s) for s in seeds],masters=[tuple(m["indices"]) for m in basis["masters"]],
  identities=identities)
def connected(eqs,targets,masters):
 # Masters are terminal columns: a target already in the master span needs no equations.
 # Other shared-master connections are retained to match the earlier public-pool protocol.
 start={tuple(t["indices"]) for x in targets for t in x["terms"]}
 if start<=set(masters):return []
 incidence=collections.defaultdict(list)
 for i,e in enumerate(eqs):
  for t in e["terms"]:incidence[tuple(t["indices"])].append(i)
 pending=list(start);seen=set(start);used=set()
 while pending:
  for i in incidence.get(pending.pop(),[]):
   if i in used:continue
   used.add(i)
   for t in eqs[i]["terms"]:
    a=tuple(t["indices"])
    if a not in seen:seen.add(a);pending.append(a)
 return [e for i,e in enumerate(eqs) if i in used]
def rational_rows(terms):
 import sympy as sp
 out={}
 for t in terms:
  a=tuple(t["indices"]);c=sp.sympify(t["coefficient"].replace("^","**"),rational=True)
  out[a]=out.get(a,sp.S.Zero)+c
 return {a:sp.cancel(c) for a,c in out.items() if c!=0}
def expression_terms(row):return [dict(indices=list(a),coefficient=str(c)) for a,c in sorted(row.items()) if c!=0]
def exact_check(rows,family):
 import sympy as sp
 wanted={x["id"] for x in family["targets"]}
 refs={r["id"]:r for r in old.rows(DATA/family["meta"]["references"]) if r["id"] in wanted}
 records=[]
 for t in family["targets"]:
  got=rows.get(t["id"]);ref=refs[t["id"]]
  if got is None:records.append(dict(target=t["id"],status="missing"));continue
  expected=rational_rows(ref["master_coefficients"])
  residual=[a for a,c in got.items() if c!=0 and a not in family["masters"]]
  good=not residual and all(sp.cancel(got.get(a,0)-expected.get(a,0))==0 for a in set(got)|set(expected))
  records.append(dict(target=t["id"],status="exact_match" if good else "residual" if residual else "mismatch",
                      coefficients=expression_terms(got)))
 return records
def sample_point(definition):
 # Fixed public kinematics, independent of labels, choices and test outcomes.
 known={"d":37,"m2":7,"s":-13,"t":-19,"s4":-29,"s1":-31,"s2":-37,"s3":-41}
 return {v:known.get(v,47+2*i) for i,v in enumerate(["d"]+definition["invariants"])},2147483647
