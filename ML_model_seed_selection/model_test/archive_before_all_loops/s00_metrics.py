"""Reference-seed metrics at the fixed 0.5 threshold, with explicit empty-set handling."""
import collections
import numpy as np
KS=(1,5,10,20)
def divide(a,b):
    return float(a)/float(b) if b else None
def micro_metrics(tn,fp,fn,tp):
    precision=divide(tp,tp+fp);recall=divide(tp,tp+fn);specificity=divide(tn,tn+fp)
    return dict(accuracy=divide(tp+tn,tp+tn+fp+fn),precision=precision,recall=recall,
                specificity=specificity,f1=divide(2*tp,2*tp+fp+fn),
                balanced_accuracy=(recall+specificity)/2 if recall is not None and specificity is not None else None)
def target_metrics(p,y,seeds):
    p=np.asarray(p,dtype=np.float64);y=np.asarray(y,dtype=np.bool_)
    assert p.ndim==y.ndim==1 and p.shape==y.shape and len(p)>0
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    chosen=p>=0.5
    tp=int((chosen&y).sum());fp=int((chosen&~y).sum())
    fn=int((~chosen&y).sum());tn=int((~chosen&~y).sum())
    positives=tp+fn;selected=tp+fp
    r=dict(tp=tp,fp=fp,fn=fn,tn=tn,candidates=len(p),reference_seeds=positives,
           selected_seeds=selected,empty_reference=int(positives==0),
           classification_accuracy=(tp+tn)/len(p),precision_at_0_5=divide(tp,selected),
           recall_at_0_5=divide(tp,positives),f1_at_0_5=divide(2*tp,2*tp+fp+fn),
           exact_reference_set_at_0_5=float(tp==positives and fp==0),
           reference_coverage_at_0_5=float(fn==0) if positives else None,
           jaccard_at_0_5=tp/(tp+fp+fn) if tp+fp+fn else 1.0,
           brier=float(np.mean((p-y)**2)),mean_confidence=float(np.where(chosen,p,1-p).mean()))
    # Resolve equal probabilities by lexicographic seed indices for finite-k selections.
    keys=tuple(seeds[:,i] for i in reversed(range(seeds.shape[1])))+(-p,)
    order=np.lexsort(keys);ranked=y[order];sorted_p=p[order]
    if positives:
        cumulative=ranked.cumsum()
        ends=np.r_[np.flatnonzero(sorted_p[:-1]!=sorted_p[1:]),len(p)-1]
        group_tp=cumulative[ends]
        r["average_precision"]=float(np.sum(np.diff(np.r_[0,group_tp])/positives*group_tp/(ends+1)))
        for k in KS:
            hits=int(ranked[:k].sum());actual=min(k,len(p))
            r["precision_at_"+str(k)]=hits/actual
            r["recall_at_"+str(k)]=hits/positives
            r["reference_coverage_at_"+str(k)]=float(hits==positives)
        r["recall_at_reference_size"]=float(ranked[:positives].sum())/positives
        ranks=np.flatnonzero(ranked)+1
        r["worst_reference_rank"]=int(ranks[-1])
    return r
class Aggregate:
    def __init__(self):
        self.sums=collections.Counter();self.denominators=collections.Counter();self.targets=0
    def add(self,values):
        self.targets+=1
        for k,v in values.items():
            if isinstance(v,(int,float)) and v is not None:
                self.sums[k]+=v;self.denominators[k]+=1
    def result(self):
        c={k:int(self.sums[k]) for k in ("tn","fp","fn","tp")}
        return dict(targets=self.targets,candidate_labels=int(self.sums["candidates"]),
                    positive_labels=int(self.sums["reference_seeds"]),
                    empty_reference_targets=int(self.sums["empty_reference"]),
                    confusion=c,micro=micro_metrics(**c),
                    target_macro={k:self.sums[k]/n for k,n in self.denominators.items()},
                    target_macro_denominators=dict(self.denominators))
class Curves:
    def __init__(self):
        self.bins=4096
        self.positive=np.zeros(self.bins,np.int64);self.negative=np.zeros(self.bins,np.int64)
        self.count=np.zeros(10,np.int64);self.sum_p=np.zeros(10);self.sum_y=np.zeros(10,np.int64)
        self.q_count=np.zeros(20,np.int64);self.q_sum=np.zeros(20);self.q_correct=np.zeros(20,np.int64)
    def add(self,p,y):
        p=np.asarray(p,np.float64);y=np.asarray(y,np.bool_)
        indices=np.minimum((p*self.bins).astype(np.int64),self.bins-1)
        self.positive+=np.bincount(indices[y],minlength=self.bins)
        self.negative+=np.bincount(indices[~y],minlength=self.bins)
        b=np.minimum((p*10).astype(np.int64),9)
        self.count+=np.bincount(b,minlength=10);self.sum_p+=np.bincount(b,weights=p,minlength=10)
        self.sum_y+=np.bincount(b[y],minlength=10)
        predicted=p>=0.5;q=np.where(predicted,p,1-p)
        qb=predicted.astype(np.int64)*10+np.minimum((q*10).astype(np.int64),9)
        self.q_count+=np.bincount(qb,minlength=20);self.q_sum+=np.bincount(qb,weights=q,minlength=20)
        self.q_correct+=np.bincount(qb[predicted==y],minlength=20)
    def result(self):
        tp=np.cumsum(self.positive[::-1]);fp=np.cumsum(self.negative[::-1])
        recall=tp/max(1,int(tp[-1]))
        precision=np.divide(tp,tp+fp,out=np.ones(len(tp),float),where=(tp+fp)>0)
        reliability=[dict(lower=i/10,upper=(i+1)/10,count=int(n),
                          mean_probability=float(self.sum_p[i]/n),positive_fraction=float(self.sum_y[i]/n))
                     for i,n in enumerate(self.count) if n]
        confidence=[dict(predicted_label=i//10,lower=(i%10)/10,upper=(i%10+1)/10,count=int(n),
                         mean_confidence=float(self.q_sum[i]/n),reference_accuracy=float(self.q_correct[i]/n))
                    for i,n in enumerate(self.q_count) if n]
        return dict(histogram_bins=self.bins,positive_counts=self.positive.tolist(),
                    negative_counts=self.negative.tolist(),
                    thresholds=(np.arange(self.bins-1,-1,-1)/self.bins).tolist(),
                    precision=precision.tolist(),recall=recall.tolist(),
                    binned_micro_average_precision=float(np.sum(np.diff(np.r_[0,recall])*precision)),
                    probability_reliability=reliability,confidence_reliability=confidence,
                    probability_ece=sum(r["count"]*abs(r["mean_probability"]-r["positive_fraction"]) for r in reliability)/int(self.count.sum()),
                    note="The pooled precision-recall curve uses 4096 probability bins; threshold 0.5 counts and target average precision are exact.")
def self_check():
    seeds=np.arange(4).reshape(-1,1)
    r=target_metrics(np.array([.9,.2,.8,.1]),np.array([1,0,1,0]),seeds)
    assert r["tp"]==2 and r["tn"]==2 and r["average_precision"]==1 and r["f1_at_0_5"]==1
    r=target_metrics(np.ones(4)*.5,np.array([1,0,1,0]),seeds)
    assert r["average_precision"]==.5 and r["selected_seeds"]==4 and r["precision_at_0_5"]==.5
    r=target_metrics(np.array([.4,.3,.2,.1]),np.array([0,1,0,1]),seeds)
    assert abs(r["average_precision"]-.5)<1e-12 and r["precision_at_0_5"] is None and r["recall_at_0_5"]==0
    r=target_metrics(np.zeros(4),np.zeros(4),seeds)
    assert r["exact_reference_set_at_0_5"]==1 and r["recall_at_0_5"] is None and "average_precision" not in r
    curves=Curves();curves.add(np.array([0,.5,1,.499]),np.array([0,1,1,0]))
    c=curves.result();assert sum(c["positive_counts"][2048:])==2 and sum(c["negative_counts"][2048:])==0
    return dict(status="passed",cases=["perfect","tied_probabilities","zero_selected","empty_reference","threshold_boundaries"],
                optimizer_updates=0)
