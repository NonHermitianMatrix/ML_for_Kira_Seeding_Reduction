"""Future held-out comparison with recorded sufficient sets; no exact-reduction claim."""
import argparse, collections, json, pathlib
import torch
from s01_data import HERE, examples, storage_guard, verify_sources
from s02_model import reference_loss
from s04_predict import load_model

def seed_metrics(probabilities, labels):
    p=probabilities.detach().cpu()
    y=labels.detach().cpu().bool()
    order=torch.argsort(p,descending=True)
    ranked=y[order]
    positives=int(y.sum())
    result={"brier":float(((p-y.float())**2).mean()),
            "empty_reference":int(positives==0),
            "empty_reference_mean_probability":float(p.mean()) if positives==0 else None}
    chosen=p>=0.5
    union=int((chosen|y).sum())
    result["jaccard_at_0_5"]=float((chosen&y).sum())/union if union else 1.0
    if positives:
        precision=ranked.float().cumsum(0)/torch.arange(1,len(p)+1,dtype=torch.float32)
        result["average_precision"]=float((precision*ranked).sum())/positives
        for k in (1,5,10,20):
            hits=int(ranked[:k].sum())
            result["recall_at_"+str(k)]=hits/positives
            result["reference_coverage_at_"+str(k)]=float(hits==positives)
        result["recall_at_reference_size"]=float(ranked[:positives].sum())/positives
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,default=HERE/"runs"/"test_metrics.json")
    args=p.parse_args()
    model,cfg,checkpoint=load_model(args.checkpoint)
    verify_sources();storage_guard()
    sums=collections.defaultdict(lambda:collections.Counter())
    counts=collections.defaultdict(lambda:collections.Counter())
    def add(group,values):
        for key,value in values.items():
            if value is not None:
                sums[group][key]+=value
                counts[group][key]+=1
    with torch.no_grad():
        for target,x,y in examples("test",cfg):
            logits=model(x)
            values=seed_metrics(logits.sigmoid(),y)
            values["binary_cross_entropy"]=float(reference_loss(logits,y))
            for group in ("all",target["kind"],"family:"+target["family"]): add(group,values)
    means={g:{k:sums[g][k]/n for k,n in c.items()} for g,c in counts.items()}
    family_means=[v for g,v in means.items() if g.startswith("family:")]
    metrics=sorted({k for v in family_means for k in v})
    means["family_macro"]={k:sum(v[k] for v in family_means if k in v)/sum(k in v for v in family_means) for k in metrics}
    result=dict(status="evaluated",optimizer_steps=checkpoint["optimizer_steps"],
                means=means,denominators={g:dict(c) for g,c in counts.items()},
                interpretation="Reference-set agreement, not optimal-seed distance or exact reduction success.")
    if args.output.exists(): raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result["means"]["all"],sort_keys=True))
if __name__=="__main__":main()
