"""Encode current matrix/actions and apply exact finite-field elementary row operations.

No reference choice, future state or master expansion is an input feature.
The solver supplies its complete allowed action list and row roles.
"""
import collections, functools, hashlib, json, math, re
import numpy as np
from s00_common import config

@functools.lru_cache(maxsize=8192)
def indices(key):
    return tuple(int(x) for x in key.split(","))
def column(a):
    return ",".join(map(str,a))
@functools.lru_cache(maxsize=64)
def is_prime(p):
    if p<2 or p>=2**32:return False
    for v in (2,3,5,7,11,13,17,19,23,29,31,37):
        if p%v==0:return p==v
    d=p-1;s=0
    while d%2==0:d//=2;s+=1
    for a in (2,3,5,7,11):
        x=pow(a,d,p)
        if x in (1,p-1):continue
        for _ in range(s-1):
            x=x*x%p
            if x==p-1:break
        else:return False
    return True
def clean_row(row,p,n):
    out={}
    for key,v in row.items():
        a=indices(key)
        if len(a)!=n or column(a)!=key:raise ValueError("Invalid integral column")
        if type(v)!=int:raise ValueError("Field coefficients must be integers")
        v%=p
        if v:out[key]=v
    return out
def order_key(key):
    a=indices(key);r=sum(max(v,0) for v in a);s=sum(max(-v,0) for v in a)
    t=sum(v>0 for v in a);sector=sum(1<<i for i,v in enumerate(a) if v>0)
    return sector,r-t,s,r,a
def eliminate(destination,source,pivot,p):
    if not source.get(pivot) or not destination.get(pivot):
        raise ValueError("Zero pivot in source or destination")
    factor=destination[pivot]*pow(source[pivot],-1,p)%p
    out=dict(destination)
    for k,v in source.items():
        new=(out.get(k,0)-factor*v)%p
        if new:out[k]=new
        else:out.pop(k,None)
    assert pivot not in out
    return out,factor

def normalize_state(state,cfg=None):
    cfg=cfg or config()
    family=state["family"]
    n=len(family["propagators"]);p=state["prime"]
    if type(p)!=int or not is_prime(p):raise ValueError("Expected a prime below 2**32")
    if not 0<n<=cfg["max_indices"]:raise ValueError("Integral-index capacity exceeded")
    raw=state["rows"]
    if not raw or len(raw)>cfg["max_rows"]:raise ValueError("Matrix-row capacity exceeded")
    if any(len(v)>cfg["max_row_nonzeros"] for v in raw.values()):
        raise ValueError("Row nonzero capacity exceeded")
    if sum(map(len,raw.values()))>cfg["max_nonzeros"]:raise ValueError("Matrix nonzero capacity exceeded")
    matrix={k:clean_row(v,p,n) for k,v in raw.items()}
    masters=set(state["master_columns"])
    if any(len(indices(k))!=n or column(indices(k))!=k for k in masters):
        raise ValueError("Invalid master column")
    roles=state["row_roles"]
    if set(roles)!=set(matrix) or any(v not in ("identity","target") for v in roles.values()):
        raise ValueError("Specify identity/target role for every row")
    actions=state["actions"]
    if len(actions)>cfg["max_actions"]:raise ValueError("Candidate capacity exceeded")
    identifiers=set();triples=set()
    for a in actions:
        aid=a["id"];q=a["source_row"];r=a["destination_row"];k=column(a["pivot_indices"])
        if not isinstance(aid,str) or not aid or aid in identifiers:raise ValueError("Duplicate/empty action ID")
        if (q,r,k) in triples:raise ValueError("Duplicate elementary action")
        identifiers.add(aid);triples.add((q,r,k))
        if q==r or q not in matrix or r not in matrix:raise ValueError("Invalid source/destination")
        if roles[q]!="identity":raise ValueError("Source must be a zero identity")
        if k in masters:raise ValueError("Cannot eliminate a protected master")
        if not matrix[q].get(k) or not matrix[r].get(k):raise ValueError("Zero pivot")
        if state.get("enforce_reference_order",False):
            leadq=max((x for x in matrix[q] if x not in masters),key=order_key,default=None)
            leadr=max((x for x in matrix[r] if x not in masters),key=order_key,default=None)
            if leadq!=k or leadr!=k:raise ValueError("Action violates reference integral order")
    return matrix,masters,p

def public_family(definition):
    keys=("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")
    return {k:definition[k] for k in keys}
@functools.lru_cache(maxsize=1024)
def family_features(text,bins):
    tokens=re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+|\*\*|[^\s]",text)
    result=[0.0]*bins;count=0
    for width in (1,2,3):
        for start in range(len(tokens)-width+1):
            b="\x1f".join(tokens[start:start+width]).encode()
            d=hashlib.blake2b(b,digest_size=8).digest()
            result[int.from_bytes(d[:4],"little")%bins]+=1.0 if d[4]&1 else -1.0
            count+=1
    return tuple(v/math.sqrt(max(1,count)) for v in result)
@functools.lru_cache(maxsize=8192)
def complexity(key):
    a=indices(key);r=sum(max(0,v) for v in a);s=sum(max(0,-v) for v in a)
    t=sum(v>0 for v in a)
    return r,s,t,r-t
def index_features(key,cfg):
    a=indices(key);n=len(a);padded=list(a)+[0]*(cfg["max_indices"]-n)
    return ([math.copysign(math.log1p(abs(v)),v) if v else 0.0 for v in padded]+
            [float(v>0) for v in padded]+[float(i<n) for i in range(cfg["max_indices"])]+
            [math.log1p(v) for v in (*complexity(key),n)])
def row_features(row,masters):
    keys=list(row);m=len(set(keys)&masters);nnz=len(keys)
    values=[complexity(k) for k in keys]
    means=[sum(v[i] for v in values)/max(1,nnz) for i in range(4)]
    maxima=[max((v[i] for v in values),default=0) for i in range(4)]
    sectors=len({tuple(v>0 for v in indices(k)) for k in keys})
    return [math.log1p(v) for v in (nnz,m,nnz-m,*means,*maxima,sectors)]
def feature_names(cfg=None):
    cfg=cfg or config();n=cfg["max_indices"]
    names=[f"pivot_log_index_{i}" for i in range(n)]
    names +=[f"pivot_positive_{i}" for i in range(n)]+[f"pivot_present_{i}" for i in range(n)]
    names +=["pivot_"+s for s in ("r","s","t","dots","n_indices")]
    rownames=("nnz","masters","nonmasters","mean_r","mean_s","mean_t","mean_dots",
              "max_r","max_s","max_t","max_dots","sectors")
    names +=[prefix+"_"+s for prefix in ("source","destination") for s in rownames]
    names +=["matrix_"+s for s in ("rows","columns","nnz","master_columns","mean_row_nnz",
                                  "max_row_nnz","actions","indices")]
    names +=["action_"+s for s in ("overlap","fill_in","cancelled","result_nnz","result_nonmasters",
                                   "operations","pivot_incidence","overlap_fraction",
                                   "cancelled_fraction","fill_fraction","result_master_fraction")]
    names +=[f"family_hash_{i}" for i in range(cfg["hash_bins"])]
    names +=["family_"+s for s in ("loops","propagators","external_momenta","invariants")]
    return names
def encode_state(state,cfg=None):
    cfg=cfg or config();matrix,masters,p=normalize_state(state,cfg)
    actions=state["actions"]
    if not actions:return np.empty((0,len(feature_names(cfg))),dtype=np.float32)
    fam=public_family(state["family"])
    text=json.dumps(fam,sort_keys=True,separators=(",",":"))
    if len(text)>cfg["max_family_chars"]:raise ValueError("Family text capacity exceeded")
    fv=list(family_features(text,cfg["hash_bins"]))
    fv +=[math.log1p(len(fam[k])) for k in ("loop_momenta","propagators","external_momenta","invariants")]
    incidence=collections.Counter(k for row in matrix.values() for k in row)
    nnz=sum(map(len,matrix.values()));nrows=len(matrix)
    globalv=[math.log1p(v) for v in (nrows,len(incidence),nnz,len(set(incidence)&masters),
                                    nnz/nrows,max(map(len,matrix.values())),len(actions),len(fam["propagators"]))]
    summaries={k:row_features(row,masters) for k,row in matrix.items()}
    features=[]
    for a in actions:
        q=a["source_row"];r=a["destination_row"];k=column(a["pivot_indices"])
        src=matrix[q];dst=matrix[r];after,_=eliminate(dst,src,k,p)
        overlap=len(set(src)&set(dst));fill=len(set(after)-set(dst));cancelled=len(set(dst)-set(after))
        nonmasters=len(set(after)-masters);remaining_masters=len(set(after)&masters)
        local=[math.log1p(v) for v in (overlap,fill,cancelled,len(after),nonmasters,1+2*len(src),incidence[k])]
        local +=[overlap/max(1,len(src)),cancelled/max(1,len(dst)),fill/max(1,len(src)),
                 remaining_masters/max(1,len(after))]
        features.append(index_features(k,cfg)+summaries[q]+summaries[r]+globalv+local+fv)
    result=np.asarray(features,dtype=np.float32)
    if result.shape!=(len(actions),len(feature_names(cfg))) or not np.isfinite(result).all():
        raise ValueError("Invalid feature array")
    return result

def state_from_step(step,identities,family,masters,prime):
    allowed=step["allowed_pivot_equations"]
    matrix={"target":step["before"]}
    matrix.update({eid:identities[eid]["modular_terms"] for eid in allowed})
    return dict(prime=prime,family=public_family(family),rows=matrix,
                row_roles={key:("target" if key=="target" else "identity") for key in matrix},
                master_columns=sorted(masters),enforce_reference_order=True,
                actions=[dict(id=eid,source_row=eid,destination_row="target",
                              pivot_indices=step["pivot_indices"]) for eid in allowed])
