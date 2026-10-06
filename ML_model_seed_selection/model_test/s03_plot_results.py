"""Create report figures from completed evaluation records without changing or rerunning the model."""
import csv,json,pathlib,shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent
MODEL=HERE.parent;REPORT=MODEL.parent/"report"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def csv_write(name,rows):
    if not rows:return
    with (HERE/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    results=read(HERE/"test_results.json");curves=read(HERE/"curves.json");families=read(HERE/"family_metrics.json")
    assert results["status"]=="completed"
    overall=results["overall"];micro=overall["micro"];macro=overall["target_macro"]
    figures=HERE/"figures";figures.mkdir(exist_ok=True)
    report_figures=REPORT/"figures";report_figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "savefig.dpi":180,"pdf.fonttype":42,"ps.fonttype":42})
    saved=[]
    def save(fig,name):
        fig.tight_layout()
        for ext in ("pdf","png"):fig.savefig(str(figures/(name+"."+ext)),bbox_inches="tight")
        shutil.copy2(str(figures/(name+".pdf")),str(report_figures/(name+".pdf")))
        saved.append(name);plt.close(fig)
    history=read(MODEL/"runs/all_loops_history.json")
    csv_write("training_history.csv",history)
    fig,ax=plt.subplots(figsize=(6.5,3.5))
    ax.plot([r["epoch"] for r in history],[r["mean_loss"] for r in history],"o-",color="#235789")
    ax.set(xlabel="Completed expanded-data training pass",ylabel="Mean training binary cross-entropy",xticks=list(range(1,len(history)+1,2)))
    ax.set_yscale("log");ax.grid(alpha=.2);save(fig,"training_loss")
    confusion=overall["confusion"]
    counts=np.array([[confusion["tn"],confusion["fp"]],[confusion["fn"],confusion["tp"]]])
    percentages=counts/counts.sum(axis=1,keepdims=True)
    fig,axes=plt.subplots(1,2,figsize=(9.3,3.8),gridspec_kw={"width_ratios":[1,1.1]})
    ax=axes[0];ax.imshow(percentages,cmap="Blues",vmin=0,vmax=1)
    for i in range(2):
        for j in range(2):
            ax.text(j,i,f"{counts[i,j]:,}\n{100*percentages[i,j]:.2f}% of row",ha="center",va="center",
                    color="white" if percentages[i,j]>.55 else "black",fontsize=9)
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=["0","1"],yticklabels=["0","1"],
           xlabel="Predicted seed label",ylabel="Recorded seed label",title="Candidate decisions at p = 0.5")
    ax=axes[1];keys=["accuracy","precision","recall","f1"]
    vals=[100*micro[k] for k in keys];bars=ax.bar(range(4),vals,color=["#738290","#235789","#e07a1f","#357a38"])
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.9,f"{v:.2f}%",ha="center",fontsize=9)
    base=100*results["baseline_all_zero"]["micro"]["accuracy"]
    ax.plot([-.4,.4],[base,base],"k--",lw=1.4,label=f"All-zero accuracy: {base:.2f}%")
    ax.set(xticks=range(4),xticklabels=["Accuracy","Precision","Recall","F1"],ylim=(0,112),ylabel="Percent")
    ax.legend(loc="lower right",fontsize=8);ax.grid(axis="y",alpha=.2);save(fig,"seed_classification")
    fig,ax=plt.subplots(figsize=(6.5,4))
    recall=np.asarray(curves["recall"]);precision=np.asarray(curves["precision"])
    ax.plot(recall,precision,color="#235789",label="Pooled curve (4096 probability bins)")
    ax.scatter([micro["recall"]],[micro["precision"]],color="#b54422",s=45,zorder=4,label="Fixed threshold p = 0.5")
    prevalence=results["baseline_all_zero"]["positive_prevalence"]
    ax.axhline(prevalence,color="gray",linestyle="--",label=f"Positive-label fraction: {100*prevalence:.3f}%")
    ax.set(xlabel="Recall of recorded seeds",ylabel="Precision of selected seeds",xlim=(0,1.02),ylim=(0,1.04))
    ax.grid(alpha=.2);ax.legend(loc="lower left",fontsize=8);save(fig,"precision_recall")
    fig,axes=plt.subplots(1,2,figsize=(9.3,3.6),sharey=True)
    ks=[1,5,10,20];ranking_rows=[]
    series=[("All targets",macro,"#235789","o"),
            ("Individual integrals",results["groups"]["kind:single_integral"]["target_macro"],"#357a38","s"),
            ("Integral expressions",results["groups"]["kind:integral_expression"]["target_macro"],"#e07a1f","^")]
    for label,values,color,marker in series:
        rec=[100*values["recall_at_"+str(k)] for k in ks]
        cov=[100*values["reference_coverage_at_"+str(k)] for k in ks]
        axes[0].plot(ks,rec,marker=marker,color=color,label=label)
        axes[1].plot(ks,cov,marker=marker,color=color,label=label)
        ranking_rows += [dict(group=label,k=k,mean_recall=rec[i]/100,complete_reference_coverage=cov[i]/100) for i,k in enumerate(ks)]
    for ax in axes:ax.set(xlabel="Number of highest-ranked candidates",xticks=ks,ylim=(0,103));ax.grid(alpha=.2)
    axes[0].set_ylabel("Mean fraction of recorded seeds recovered (%)")
    axes[1].set_ylabel("Targets with every recorded seed recovered (%)")
    axes[1].legend(loc="lower right",fontsize=8);save(fig,"ranked_seed_recovery")
    csv_write("ranked_seed_recovery.csv",ranking_rows)
    csv_write("confidence_reliability.csv",curves["confidence_reliability"])
    csv_write("probability_reliability.csv",curves["probability_reliability"])
    fig,axes=plt.subplots(1,2,figsize=(9.3,3.7),sharex=True,sharey=True)
    for label,ax in enumerate(axes):
        rows=[r for r in curves["confidence_reliability"] if r["predicted_label"]==label]
        ax.plot([.5,1],[.5,1],"k--",lw=1,label="Equal confidence and agreement")
        ax.plot([r["mean_confidence"] for r in rows],[r["reference_accuracy"] for r in rows],
                color=["#235789","#e07a1f"][label],lw=1)
        for row in rows:
            ax.scatter(row["mean_confidence"],row["reference_accuracy"],
                       s=20+13*np.log10(row["count"]),color=["#235789","#e07a1f"][label],zorder=3)
        ax.set(title="Returned label "+str(label),xlabel="Mean confidence in returned label",xlim=(.48,1.01),ylim=(0,1.03))
        ax.grid(alpha=.2)
    axes[0].set_ylabel("Fraction of returned labels matching the reference")
    axes[1].legend(loc="lower right",fontsize=7.5);save(fig,"confidence_calibration")
    fig,axes=plt.subplots(1,2,figsize=(9.3,3.8))
    fap=[f["target_macro"]["average_precision"] for f in families.values() if "average_precision" in f["target_macro"]]
    axes[0].hist(fap,bins=np.linspace(0,1,21),color="#235789",edgecolor="white")
    axes[0].set(xlabel="Mean target average precision within a family",ylabel="Number of test families",xlim=(0,1))
    loops=sorted({f["loops"] for f in families.values()})
    for key,label,color,marker in [("precision","Precision","#235789","o"),("recall","Recall","#e07a1f","s"),("f1","F1","#357a38","^")]:
        vals=[100*(results["groups"]["loops:"+str(loop)]["micro"][key] or 0) for loop in loops]
        axes[1].plot(loops,vals,marker=marker,label=label,color=color,markersize=4)
    axes[1].set(xticks=loops,xlabel="Loop order",ylim=(0,105),ylabel="Seed metric (%)")
    axes[1].legend(fontsize=8,loc="lower left");axes[1].grid(alpha=.2)
    save(fig,"family_performance")
    rows=[]
    for fid,f in families.items():
        rows.append(dict(family=fid,loops=f["loops"],targets=f["targets"],candidate_labels=f["candidate_labels"],
                         precision=f["micro"]["precision"],recall=f["micro"]["recall"],f1=f["micro"]["f1"],
                         mean_average_precision=f["target_macro"].get("average_precision"),
                         exact_reference_set_fraction=f["target_macro"]["exact_reference_set_at_0_5"]))
    csv_write("family_metrics.csv",rows)
    (HERE/"figure_manifest.json").write_text(json.dumps(dict(figures=saved,formats=["pdf","png"],report_copies="report/figures",matplotlib_version=matplotlib.__version__),indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(status="figures_created",figures=saved)),flush=True)
if __name__=="__main__":main()
