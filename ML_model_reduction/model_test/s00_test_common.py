"""Shared held-out metrics, bounded outputs and exact sample arithmetic."""
import ast,collections,csv,functools,gzip,hashlib,json,math,os,pathlib,sys,time
import numpy as np
TEST=pathlib.Path(__file__).resolve().parent
MODEL=TEST.parent;ROOT=MODEL.parent
sys.path.insert(0,str(MODEL))
from s00_common import read,rows,record_path,sha,write_json,storage_guard
from s01_state import column,indices,order_key,clean_row,eliminate,public_family,state_from_step
from s05_predict import Predictor
def test_config():return read(TEST/"test_config.json")
def status(stage,**extra):
    write_json(TEST/"status.json",dict(stage=stage,utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),**extra))
def signature():
    scripts={p.name:sha(p) for p in list(TEST.glob("s0[0-2]_*.py"))+[TEST/"s10_parallel_test.py"]}
    return dict(model_sha256=sha(MODEL/"trained_model.pt"),config_sha256=sha(TEST/"test_config.json"),
                split_sha256=sha(ROOT/"ML_model_seed_selection/split_manifest.json"),
                encoder_sha256=sha(MODEL/"s01_state.py"),predictor_sha256=sha(MODEL/"s05_predict.py"),
                scripts=scripts)
def write_npz(path,**arrays):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".part")
    with tmp.open("wb") as f:np.savez_compressed(f,**arrays)
    if tmp.stat().st_size>test_config()["max_family_output_bytes"]:raise RuntimeError("Family output size limit")
    os.replace(str(tmp),str(path))
def write_gzip(path,objects):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".part")
    with gzip.open(str(tmp),"wt",encoding="utf-8") as f:
        for obj in objects:f.write(json.dumps(obj,separators=(",",":"),allow_nan=False)+"\n")
    if tmp.stat().st_size>test_config()["max_family_output_bytes"]:raise RuntimeError("Family output size limit")
    os.replace(str(tmp),str(path))
def csv_write(path,records):
    if not records:return
    with pathlib.Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
@functools.lru_cache(maxsize=8192)
def parsed(text):
    if len(text)>131072:raise ValueError("Coefficient expression exceeds bound")
    tree=ast.parse(text,mode="eval").body
    if sum(1 for _ in ast.walk(tree))>16384:raise ValueError("Coefficient tree exceeds bound")
    return tree
def literal_int(node):
    if isinstance(node,ast.Constant) and type(node.value)==int:return node.value
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
        v=literal_int(node.operand);return -v if isinstance(node.op,ast.USub) else v
    raise ValueError("Only integer powers are supported")
def coefficient(text,point,prime):
    def ev(node):
        if isinstance(node,ast.Constant) and type(node.value)==int:return node.value%prime
        if isinstance(node,ast.Name):return int(point[node.id])%prime
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
            v=ev(node.operand);return -v%prime if isinstance(node.op,ast.USub) else v
        if isinstance(node,ast.BinOp):
            a=ev(node.left)
            if isinstance(node.op,ast.Pow):
                power=literal_int(node.right)
                if abs(power)>256:raise ValueError("Power exceeds bound")
                if not a and power<0:raise ZeroDivisionError("Singular coefficient")
                return pow(a,power,prime)
            b=ev(node.right)
            if isinstance(node.op,ast.Add):return (a+b)%prime
            if isinstance(node.op,ast.Sub):return (a-b)%prime
            if isinstance(node.op,ast.Mult):return a*b%prime
            if isinstance(node.op,ast.Div):
                if not b:raise ZeroDivisionError("Singular coefficient")
                return a*pow(b,-1,prime)%prime
        raise ValueError("Unsupported coefficient syntax")
    return ev(parsed(str(text)))
def eval_terms(terms,point,prime):
    result={}
    for term in terms:
        key=column(term["indices"])
        v=(result.get(key,0)+coefficient(term["coefficient"],point,prime))%prime
        if v:result[key]=v
        else:result.pop(key,None)
    return result
def exact_row_check(before,source,pivot,after,p):
    assert pivot not in after
    for key in set(before)|set(source)|set(after):
        assert after.get(key,0)*source[pivot]%p==(before.get(key,0)*source[pivot]-before[pivot]*source.get(key,0))%p
def ordered_indices(probabilities,ids):
    return sorted(range(len(ids)),key=lambda i:(-float(probabilities[i]),ids[i]))
def classify(probabilities,reference,ids):
    order=ordered_indices(probabilities,ids);rank=order.index(reference)+1
    p=np.asarray(probabilities,dtype=np.float64);onehot=np.zeros(len(p));onehot[reference]=1
    return dict(predicted=order[0],rank=rank,confidence=float(p[order[0]]),
                correct=int(order[0]==reference),nll=-math.log(max(float(p[reference]),1e-38)),
                clipped_nll=int(float(p[reference])<1e-38),brier=float(((p-onehot)**2).sum()))
def reliability(confidence,correct,bins=10):
    confidence=np.asarray(confidence);correct=np.asarray(correct)
    which=np.minimum((confidence*bins).astype(int),bins-1)
    records=[]
    for i in range(bins):
        mask=which==i;n=int(mask.sum())
        if n:records.append(dict(bin=i,lower=i/bins,upper=(i+1)/bins,count=n,
             mean_confidence=float(confidence[mask].mean()),reference_accuracy=float(correct[mask].mean())))
    return records
def metric_summary(data):
    count=np.diff(data["offsets"]);mask=count>1
    def avg(key,m=mask):return float(np.asarray(data[key])[m].mean()) if m.any() else None
    rel=reliability(data["confidence"][mask],data["correct"][mask])
    n=int(mask.sum())
    return dict(states=len(count),choice_states=n,forced_states=int((count==1).sum()),
        candidate_actions=int(count.sum()),top1=avg("correct"),top3=float((data["rank"][mask]<=3).mean()) if n else None,
        top5=float((data["rank"][mask]<=5).mean()) if n else None,
        reciprocal_rank=float((1/data["rank"][mask]).mean()) if n else None,
        equivalent_next_row=avg("same_row"),greedy_top1=avg("greedy_correct"),
        mean_confidence=avg("confidence"),nll=avg("nll"),brier=avg("brier"),
        uniform_top1=float((1/count[mask]).mean()) if n else None,
        nll_clipped=int(data["clipped_nll"][mask].sum()),
        ece=sum(r["count"]*abs(r["mean_confidence"]-r["reference_accuracy"]) for r in rel)/n if n else None,
        all_state_top1=avg("correct",np.ones(len(count),bool)),
        mean_prediction_ms=1000*float(data["seconds"].mean()) if len(count) else None,
        reliability=rel)
def merge_arrays(parts):
    keys=[k for k in parts[0] if k not in ("offsets","probabilities","action_ids","target_ids")]
    result={k:np.concatenate([p[k] for p in parts]) for k in keys}
    counts=np.concatenate([np.diff(p["offsets"]) for p in parts])
    result["offsets"]=np.concatenate(([0],np.cumsum(counts)))
    return result
def ratio_summary(records,policy):
    selected=[r for r in records if r[policy]["success_all_samples"] and r["reference_operations"]>0]
    ratios=np.asarray([r[policy]["operations"]/r["reference_operations"] for r in selected])
    return dict(targets=len(records),success_primary=sum(r[policy]["status"]=="complete" and r[policy]["primary_agreement"] for r in records),
        success_all_samples=sum(r[policy]["success_all_samples"] for r in records),
        statuses=dict(collections.Counter(r[policy]["status"] for r in records)),
        comparison_targets=len(selected),lower=int(sum(v<1 for v in ratios)),equal=int(sum(v==1 for v in ratios)),higher=int(sum(v>1 for v in ratios)),
        median_operation_ratio=float(np.median(ratios)) if len(ratios) else None,
        total_operations=sum(r[policy]["operations"] for r in selected),
        total_reference_operations=sum(r["reference_operations"] for r in selected),
        mean_runtime_ms=1000*float(np.mean([r[policy]["seconds"] for r in records])) if records else None,
        median_runtime_ms=1000*float(np.median([r[policy]["seconds"] for r in records])) if records else None)
