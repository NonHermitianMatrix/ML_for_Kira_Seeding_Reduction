"""Generate six report figures from fixed saved held-out results."""
import shutil,os,pathlib
os.environ.setdefault("MPLCONFIGDIR",str(pathlib.Path(__file__).resolve().parents[2]/".tools/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from s00_test_common import *
def main():
    result=read(TEST/"test_results.json");families=read(TEST/"family_metrics.json")
    assert read(TEST/"validation.json")["status"]=="passed"
    targets=list(rows(TEST/"target_metrics.jsonl.gz"));tie=read(TEST/"tie_metrics.json")
    overall=result["overall"]
    figures=TEST/"figures";figures.mkdir(exist_ok=True);report=ROOT/"report/figures";report.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "pdf.fonttype":42,"savefig.dpi":180})
    colors={"model":"#235789","greedy":"#c76b28"};saved=[];series_rows=[]
    def save(fig,name):
        fig.tight_layout()
        for ext in ("pdf","png"):fig.savefig(figures/(name+"."+ext),bbox_inches="tight")
        shutil.copy2(figures/(name+".pdf"),report/(name+".pdf"));plt.close(fig);saved.append(name)
    fig,ax=plt.subplots(figsize=(9,4.1))
    names=["Recorded action\n(top 1)","Tie-averaged\n(top 1)","Recorded action\n(top 3)","Same next\nsampled row","Local rule:\nrecorded action","Uniform choice:\nexpected top 1"]
    vals=[overall["top1"],tie["overall"]["tie_neutral_top1"],overall["top3"],overall["equivalent_next_row"],overall["greedy_top1"],overall["uniform_top1"]]
    bars=ax.bar(range(len(vals)),np.asarray(vals)*100,color=[colors["model"],"#5b84b1",colors["model"],colors["model"],colors["greedy"],"#879199"])
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,100*v+1,f"{100*v:.2f}%",ha="center",fontsize=9)
    ax.set(xticks=range(len(vals)),xticklabels=names,ylabel="Choice states (%)",ylim=(0,112))
    ax.grid(axis="y",alpha=.2);save(fig,"reduction_action_accuracy")
    series_rows.extend(dict(figure="action_accuracy",series=names[i].replace("\n"," "),x=i,y=v) for i,v in enumerate(vals))
    fig,axes=plt.subplots(1,2,figsize=(9,3.8))
    rel=overall["reliability"]
    axes[0].plot([0,1],[0,1],"k--",lw=1,label="Confidence equals agreement")
    axes[0].plot([r["mean_confidence"] for r in rel],[r["reference_accuracy"] for r in rel],"o-",color=colors["model"])
    axes[0].set(xlabel="Mean reported confidence",ylabel="Recorded-action agreement",xlim=(0,1.02),ylim=(0,1.02))
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
    axes[1].bar([(r["lower"]+r["upper"])/2 for r in rel],[r["count"] for r in rel],width=.085,color=colors["model"])
    axes[1].set(xlabel="Reported confidence",ylabel="Number of choice states",xlim=(0,1))
    axes[1].set_yscale("log");axes[1].grid(axis="y",alpha=.2);save(fig,"reduction_confidence")
    fig,axes=plt.subplots(1,2,figsize=(9,3.8))
    ranked=sorted([f for f in families.values() if f["state_metrics"]["top1"] is not None],key=lambda f:f["state_metrics"]["top1"])
    axes[0].plot(range(1,len(ranked)+1),[100*f["state_metrics"]["top1"] for f in ranked],color=colors["model"],lw=1.5)
    axes[0].set(xlabel="Test family, sorted by action agreement",ylabel="Recorded-action agreement (%)",ylim=(0,103))
    axes[0].grid(alpha=.2)
    loops=sorted(map(int,result["groups"]))
    for key,label,color,marker in [("top1","Recorded action",colors["model"],"o"),("equivalent_next_row","Same next row","#377b52","s"),("greedy_top1","Local rule",colors["greedy"],"^")]:
        vals=[100*result["groups"][str(loop)]["state_metrics"][key] for loop in loops]
        axes[1].plot(loops,vals,label=label,color=color,marker=marker,markersize=4)
    axes[1].set(xticks=loops,xlabel="Loop order",ylim=(0,105),ylabel="Choice states (%)")
    axes[1].legend(fontsize=8,loc="lower right");axes[1].grid(alpha=.2);save(fig,"reduction_families")
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for ax,key,title in zip(axes,("success_primary","success_all_samples"),("Decision sample","All three samples")):
        for policy,label,marker in (("model","Learned policy","o"),("greedy","Local rule","s")):
            vals=[100*result["groups"][str(loop)][policy][key]/result["groups"][str(loop)]["targets"] for loop in loops]
            ax.plot(loops,vals,marker=marker,label=label,color=colors[policy],markersize=4)
        ax.set(xticks=loops,xlabel="Loop order",ylim=(0,105),ylabel="Targets matching master coefficients (%)",title=title)
        ax.grid(alpha=.2)
    axes[1].legend(loc="lower right",fontsize=8);save(fig,"reduction_rollout_success")
    fig,axes=plt.subplots(1,2,figsize=(9,3.8))
    common=[r for r in targets if r["reference_operations"]>0 and all(r[p]["success_all_samples"] for p in ("model","greedy"))]
    for p,label in (("model","Learned policy"),("greedy","Local rule")):
        ratios=np.sort([r[p]["operations"]/r["reference_operations"] for r in common])
        axes[0].step(ratios,np.arange(1,len(ratios)+1)/len(ratios),where="post",color=colors[p],linestyle="-" if p=="model" else "--",label=label)
        totals=[r[p]["total_field_operations"]/r["reference_operations"] for r in common]
        rsort=np.sort(totals)
        axes[1].step(rsort,np.arange(1,len(rsort)+1)/len(rsort),where="post",color=colors[p],linestyle="-" if p=="model" else "--",label=label)
    for ax in axes:
        ax.axvline(1,color="gray",ls="--",lw=1);ax.set_xscale("log")
        ax.set(ylabel="Fraction of common successful targets",ylim=(0,1.02));ax.grid(alpha=.2);ax.legend(fontsize=8)
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
    axes[0].xaxis.set_major_locator(FixedLocator([0.5,1,2,4]))
    axes[0].xaxis.set_major_formatter(FuncFormatter(lambda value,position:format(value,"g")))
    for ax in axes:ax.xaxis.set_minor_formatter(NullFormatter())
    axes[0].set_xlabel("Committed row operations / recorded path")
    axes[1].set_xlabel("Trial and committed row operations / recorded path")
    save(fig,"reduction_operation_counts")
    fig,axes=plt.subplots(1,2,figsize=(9,3.8))
    for p,label in (("model","Learned policy"),("greedy","Local rule")):
        values=np.sort([1000*r[p]["seconds"] for r in targets])
        axes[0].step(values,np.arange(1,len(values)+1)/len(values),where="post",label=label,color=colors[p],linestyle="-" if p=="model" else "--")
    axes[0].set_xscale("log");axes[0].set(xlabel="Reduction time per target (ms)",ylabel="Fraction of test targets",ylim=(0,1.02))
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
    names=["Median","Mean","90th percentile"]
    for j,(p,label) in enumerate((("model","Learned policy"),("greedy","Local rule"))):
        a=np.asarray([r[p]["seconds"]*1000 for r in targets])
        vals=[float(np.median(a)),float(a.mean()),float(np.quantile(a,.9))]
        bars=axes[1].bar(np.arange(3)+(j-.5)*.35,vals,.35,label=label,color=colors[p])
        for b,v in zip(bars,vals):axes[1].text(b.get_x()+b.get_width()/2,v*1.05,f"{v:.3f}",ha="center",fontsize=8)
        series_rows.extend(dict(figure="runtime",series=label,x=names[i],y=v) for i,v in enumerate(vals))
    axes[1].set(xticks=range(3),xticklabels=names,ylabel="Time per target (ms)")
    axes[1].set_yscale("log");axes[1].legend(fontsize=8,loc="upper left",bbox_to_anchor=(0,1.18),ncol=2);axes[1].grid(axis="y",alpha=.2)
    axes[1].margins(y=.25);save(fig,"reduction_runtime")
    csv_write(TEST/"figure_values.csv",series_rows)
    paired=dict(common_successful_nonzero_reference_targets=len(common),
        zero_reference_targets=sum(r["reference_operations"]==0 for r in targets),
        mean_runtime_ratio=result["model"]["mean_runtime_ms"]/result["greedy"]["mean_runtime_ms"],
        same_committed_operation_counts=sum(r["model"]["operations"]==r["greedy"]["operations"] for r in common),
        model_fewer_than_greedy=sum(r["model"]["operations"]<r["greedy"]["operations"] for r in common),
        model_more_than_greedy=sum(r["model"]["operations"]>r["greedy"]["operations"] for r in common))
    write_json(TEST/"paired_comparison.json",paired)
    manifest=dict(model_sha256=sha(MODEL/"trained_model.pt"),epochs_completed=read(MODEL/"trained_model.json")["epochs_completed"],
                  test_results_sha256=sha(TEST/"test_results.json"),
                  figures=saved,formats=["pdf","png"],matplotlib_version=matplotlib.__version__,
                  hashes={str(p.relative_to(TEST)):sha(p) for p in figures.iterdir() if p.suffix in (".pdf",".png")})
    write_json(TEST/"figure_manifest.json",manifest);print(json.dumps(dict(figures=saved,comparison=paired)),flush=True)
if __name__=="__main__":main()
