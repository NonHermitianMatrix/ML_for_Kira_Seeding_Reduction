"""Summarize fixed-test timings with physical-profile resampling."""
import collections,json,math,statistics
import numpy as np
from s04_workflows import HERE,read,guard
from s06_validate import aggregate,gmean,rows
from s14_test import check

def comparison(bs,method,base):
    fields=["complete_seconds","equation_preparation_seconds","forward_seconds"]
    ans={}
    for field in fields:
        groups=collections.defaultdict(list)
        for b in bs:
            groups[b["group"]].append(math.log(b["methods"][method][field]/b["methods"][base][field]))
        logs=np.array([sum(v)/len(v) for _,v in sorted(groups.items())])
        rng=np.random.RandomState(917241)
        means=np.exp(logs[rng.randint(0,len(logs),size=(10000,len(logs)))].mean(axis=1))
        ans[field]=dict(ratio=float(np.exp(logs.mean())),interval=[float(x) for x in np.percentile(means,[2.5,97.5])],profiles=len(logs))
    ans["workflows"]=sum(b["methods"][method]["repetitions"] for b in bs)
    ans["fallback_workflows"]=sum(b["methods"][method]["fallback_workflows"] for b in bs)
    ans["failed_attempts"]=sum(b["methods"][method]["failed_attempts"] for b in bs)
    return ans

def main():
    frozen=check()
    audit=json.loads((HERE/"model_test/verification.json").read_text());assert audit["all_passed"]
    rs=rows(HERE/"model_test");assert len(rs)==frozen["workflows"]
    bs=aggregate(rs);assert len(bs)==14
    fields={
        "filter_seconds":lambda r:sum(a.get("equation_metrics",{}).get("filter_seconds",0) for a in r["attempts"]),
        "operations":lambda r:sum(m.get("operations",0) for a in r["attempts"] for m in a.get("metrics",[])),
        "constructed_calls":lambda r:r["constructed_calls"],
        "peak_rss_bytes":lambda r:max(a["peak_rss_bytes"] for a in r["attempts"]),
        "back_substitution_seconds":lambda r:r["stage_seconds"].get("back_substitution",0),
        "preparation_seconds":lambda r:sum(a["preparation_seconds"] for a in r["attempts"]),
        "kira_seconds":lambda r:sum(a["kira_seconds"] for a in r["attempts"]),
    }
    for b in bs:
        for label,v in b["methods"].items():
            subset=[r for r in rs if r["case"]==b["case"] and r["size"]==b["size"] and r["label"]==label]
            assert len(subset)==frozen["repetitions"]
            for field,fn in fields.items():v[field]=statistics.median(fn(r) for r in subset)
            v["other_seconds"]=v["complete_seconds"]-v["equation_preparation_seconds"]-v["forward_seconds"]-v["back_substitution_seconds"]
    comparisons={method+"_vs_native":comparison(bs,method,"native") for method in frozen["methods"] if method!="native"}
    comparisons.update(deployed_vs_previous=comparison(bs,"deployed","previous"),deployed_vs_control=comparison(bs,"deployed","control"))
    active=[b for b in bs if b["topology"]!="sunrise"]
    by_topology={top:{method+"_vs_native":comparison([b for b in bs if b["topology"]==top],method,"native") for method in frozen["methods"] if method!="native"} for top in sorted({b["topology"] for b in bs})}
    totals={method:sum(b["methods"][method]["complete_seconds"] for b in bs) for method in frozen["methods"]}
    resources=dict(peak_rss_bytes=audit["peak_process_tree_rss_bytes"],peak_scratch_bytes=audit["peak_scratch_bytes"],
        extension_allocated_bytes=sum(p.stat().st_blocks*512 for p in HERE.rglob("*") if p.is_file()))
    model_summary={}
    for name in ["early_d8","early_d12"]:
        model=json.loads((HERE/"trained_model"/name/"model.json").read_text())
        model_summary[name]={k:model[k] for k in ["training_rows","training_positives","training_groups","maximum_depth","minimum_child_rows","training_seconds","decision_feature_count"]}
        model_summary[name]["nodes"]=len(model["nodes"])
    summary=dict(all_exact=True,workflows=len(rs),basis_only_applications=audit["basis_only_applications"],profiles=8,batches=14,repetitions=frozen["repetitions"],methods=frozen["methods"],comparisons=comparisons,active_domain_comparisons={method+"_vs_native":comparison(active,method,"native") for method in frozen["methods"] if method!="native"},by_topology=by_topology,batch_median_total_seconds=totals,batch_median_sum_ratio=totals["deployed"]/totals["native"],batches_detail=bs,models=model_summary,resources=resources,estimator="Median of five alternating repeats per batch; average log-ratios over sizes within each physical profile, then equal profile-weighted geometric mean. Descriptive 95 percent interval from 10,000 physical-profile bootstrap samples. Known topologies and fixed ordered target indices; new mass/kinematic profiles.",timing="Includes routing, input generation, model inference, Kira startup, exact reductions, basis and coefficient checks, cleanup and every fallback. The experiment driver is already running. Independent reference/basis preparation, post-run audit and evidence compression are outside timing.")
    (HERE/"model_test/summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    guard()
    print(json.dumps({k:summary[k] for k in ["comparisons","active_domain_comparisons","by_topology","batch_median_total_seconds","batch_median_sum_ratio","resources","models"]},indent=2),flush=True)
if __name__=="__main__":main()
