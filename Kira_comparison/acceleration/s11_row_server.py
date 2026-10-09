"""Score admissible live Kira row operations with the frozen reduction model."""
import ast, functools, gzip, json, math, os, pathlib, sys, time
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"ML_model_reduction"))
started=time.perf_counter()
import numpy as np
from s09_fast_row import FastRow
from s01_state import encode_state, public_family, column
context=json.load(open(os.environ["KIRA_LIVE_CONTEXT"]))
predictor=FastRow()
load_seconds=time.perf_counter()-started
point=context["point"]; prime=context["prime"]
rows={}; symbolic={}; decisions=0; features_seconds=0.; inference_seconds=0.
sampling_seconds=0.; changed_sources=set(); seen_destinations=set()
logpath=pathlib.Path(os.environ["KIRA_LIVE_TRACE"]+".policy.jsonl.gz")
log=gzip.open(logpath,"at",encoding="utf-8")
def emit(x):
    log.write(json.dumps(x,separators=(",",":"),allow_nan=False)+"\n")
@functools.lru_cache(maxsize=32768)
def evaluate(text):
    tree=ast.parse(text.replace("^","**"),mode="eval").body
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value)==int:return n.value%prime
        if isinstance(n,ast.Name):return int(point[n.id])%prime
        if isinstance(n,ast.UnaryOp):
            v=walk(n.operand)
            if isinstance(n.op,ast.USub):return -v%prime
            if isinstance(n.op,ast.UAdd):return v
        if isinstance(n,ast.BinOp):
            a=walk(n.left)
            if isinstance(n.op,ast.Pow):
                e=ast.literal_eval(n.right)
                if type(e)!=int:raise ValueError("Noninteger exponent")
                return pow(a,e,prime)
            b=walk(n.right)
            if isinstance(n.op,ast.Add):return (a+b)%prime
            if isinstance(n.op,ast.Sub):return (a-b)%prime
            if isinstance(n.op,ast.Mult):return a*b%prime
            if isinstance(n.op,ast.Div):return a*pow(b,-1,prime)%prime
        raise ValueError("Unsupported rational expression")
    return walk(tree)
def readrow(n):
    terms={}
    for _ in range(n):
        label,expr=sys.stdin.readline().rstrip("\n").split("\t",1)
        if not label.startswith("F[") or not label.endswith("]"):
            raise ValueError("Expected physical integral labels")
        k=label[2:-1]
        if k in terms:raise ValueError("Repeated integral column")
        terms[k]=expr
    return terms
def sampled(terms):
    global sampling_seconds
    t=time.perf_counter()
    out={k:evaluate(v) for k,v in terms.items()}
    sampling_seconds+=time.perf_counter()-t
    return {k:v for k,v in out.items() if v}
print("READY",flush=True)
try:
    for line in sys.stdin:
        fields=line.rstrip("\n").split("\t");op=fields[0]
        if op=="ROW":
            rid=fields[1];terms=readrow(int(fields[2]))
            symbolic[rid]=terms;rows[rid]=sampled(terms)
        elif op=="UPDATE":
            rid=fields[1];terms=readrow(int(fields[2]))
            symbolic[rid]=terms;rows[rid]=sampled(terms)
            if not terms:del symbolic[rid];del rows[rid]
            seen_destinations.add(rid)
            emit(dict(event="update",row=rid,terms=terms))
        elif op=="CHOOSE":
            if decisions==0:emit(dict(event="initial",rows=symbolic))
            group=fields[1].split(",")
            pivot=fields[2][2:-1]
            if pivot in context["master_columns"]:raise ValueError("Protected master pivot")
            # Require the same nonzero pivot at the public sample for every listed row.
            if any(not rows[r].get(pivot) for r in group):
                raise ValueError("Singular public sample; no silent action removal")
            actions=[dict(id="%08d:%08d"%(int(q),int(r)),source_row=q,
                          destination_row=r,pivot_indices=list(map(int,pivot.split(","))))
                     for q in group for r in group if q!=r]
            scoring_rows=rows
            roles={r:"identity" for r in rows}
            if os.environ.get("KIRA_ROW_SCOPE")=="source":
                destination=max(group,key=int)
                actions=[a for a in actions if a["destination_row"]==destination]
                scoring_rows={r:rows[r] for r in group}
                roles={r:("target" if r==destination else "identity") for r in group}
            state=dict(family=context["family"],prime=prime,rows=scoring_rows,
                       row_roles=roles,
                       master_columns=context["master_columns"],actions=actions,
                       enforce_reference_order=False)
            t=time.perf_counter();f=encode_state(state,predictor.cfg)
            ft=time.perf_counter()-t;features_seconds+=ft
            t=time.perf_counter()
            probabilities=predictor.probabilities(f)
            it=time.perf_counter()-t;inference_seconds+=it
            best=min(range(len(actions)),key=lambda i:(-float(probabilities[i]),actions[i]["id"]))
            a=actions[best];q=a["source_row"];r=a["destination_row"]
            if q in seen_destinations:changed_sources.add(q)
            emit(dict(event="choice",step=decisions,rows=len(rows),nonzeros=sum(map(len,rows.values())),
                      pivot=pivot,group=group,candidate_actions=actions,feature_rows=len(scoring_rows),selected=a,confidence=float(probabilities[best]),
                      probabilities=[float(v) for v in probabilities],
                      feature_seconds=ft,inference_seconds=it,
                      source_previously_updated=q in seen_destinations))
            decisions+=1
            print(q,r,float(probabilities[best]),flush=True)
        elif op=="DONE":
            emit(dict(event="summary",decisions=decisions,load_seconds=load_seconds,
                      feature_seconds=features_seconds,inference_seconds=inference_seconds,
                      sampling_seconds=sampling_seconds,previously_updated_sources=len(changed_sources),
                      context=context,checkpoint=str(ROOT/"ML_model_reduction/trained_model.pt")))
            log.close();print("DONE",flush=True);break
        else:raise ValueError("Unknown live protocol")
except Exception as e:
    emit(dict(event="error",message=str(e)));log.close()
    raise

