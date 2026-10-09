"""Plot matched elapsed times and exact coefficient-operation counts."""
import csv,json,pathlib,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 d=json.load(open(HERE/"summary.json"));rows=d["cases"]
 ix={(r["case"],r["policy"]):r for r in rows}
 labels=["Box A","Box B","Box C","Bubble","2-loop","Tadpole","Triangle"]
 x=np.arange(7);figdir=HERE/"figures";figdir.mkdir(exist_ok=True)
 plt.rcParams.update({"font.size":9,"axes.labelsize":10,"legend.fontsize":8,
                      "pdf.fonttype":42,"ps.fonttype":42})
 colors={"stock":"#555555","native":"#2271b2","deterministic":"#009e73","learned":"#d55e00"}
 names={"stock":"Stock Kira","native":"Instrumented Kira","deterministic":"Deterministic control","learned":"Learned policy"}
 fig,axes=plt.subplots(1,2,figsize=(7.2,4.2),constrained_layout=True)
 for j,p in enumerate(["stock","native","deterministic","learned"]):
  y=[ix[(i,p)].get("cold_seconds",np.nan) for i in x]
  axes[0].bar(x+(j-1.5)*.19,y,.19,label=names[p],color=colors[p])
 axes[0].set_ylabel("Complete checked reduction (s)")
 for j,(p,k,label,color) in enumerate([
    ("native","forward_seconds","Kira forward stage","#2271b2"),
    ("deterministic","forward_seconds","Deterministic forward stage","#009e73"),
    ("learned","forward_seconds","Learned, including model load","#d55e00"),
    ("learned","forward_loaded_seconds","Learned, model load excluded","#cc79a7")]):
  y=[ix[(i,p)].get(k,np.nan) for i in x]
  axes[1].bar(x+(j-1.5)*.19,y,.19,label=label,color=color)
 axes[1].set_yscale("log");axes[1].set_ylabel("Forward elimination (s, log scale)")
 for a in axes:
  a.set_xticks(x);a.set_xticklabels(labels,rotation=30,ha="right");a.grid(axis="y",alpha=.2);a.set_axisbelow(True)
  a.legend(loc="upper left",bbox_to_anchor=(0,1.27),frameon=False)
 fig.savefig(figdir/"live_kira_times.pdf",bbox_inches="tight");plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(7.2,3.8),constrained_layout=True)
 for j,p in enumerate(["native","deterministic","learned"]):
  for a,k,label in [(axes[0],"steps","Exact row updates"),(axes[1],"operations","Coefficient operations")]:
   a.bar(x+(j-1)*.24,[ix[(i,p)].get(k,np.nan) for i in x],.24,label=names[p],color=colors[p])
   a.set_ylabel(label);a.set_xticks(x);a.set_xticklabels(labels,rotation=30,ha="right");a.grid(axis="y",alpha=.2);a.set_axisbelow(True)
 axes[0].legend(loc="upper left",bbox_to_anchor=(0,1.22),ncol=2,frameon=False)
 fig.savefig(figdir/"live_kira_operations.pdf",bbox_inches="tight");plt.close(fig)
 for p in figdir.glob("*.pdf"):shutil.copy2(p,ROOT/"report/figures"/p.name)
 keys=["case","family","policy","complete","cold_seconds","native_seconds","forward_seconds",
       "forward_loaded_seconds","steps","operations","model_load_seconds","feature_seconds",
       "inference_seconds","sampling_seconds","peak_rss_bytes"]
 with (HERE/"figure_values.csv").open("w",newline="") as out:
  writer=csv.DictWriter(out,fieldnames=keys,extrasaction="ignore");writer.writeheader();writer.writerows(rows)
 print("Generated two live-matrix comparison figures",flush=True)
if __name__=="__main__":main()

