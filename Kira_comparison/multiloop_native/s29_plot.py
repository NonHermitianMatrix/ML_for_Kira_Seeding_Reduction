"""Plot complete times, algebraic counts and completion including fallback."""
import csv,json,os,pathlib,shutil
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
os.environ["MPLCONFIGDIR"]=str(ROOT/".tools/cache/kira-cost-plots")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
def main():
 s=json.loads((HERE/"summary.json").read_text());f=json.loads((HERE/"freeze.json").read_text())
 with (HERE/"trials.csv").open() as stream:rows=list(csv.DictReader(stream))
 folder=ROOT/"report/figures";folder.mkdir(exist_ok=True);out=HERE/"model_test/plots";out.mkdir(exist_ok=True)
 labels={"stock":"Stock conservative","native":"Instrumented native","tight":"Smaller region + fallback",
  "row_full":"Cost-trained rows","closure_safe":"Coverage + fallback","closure_full_safe":"Full-region coverage",
  "seed_safe":"Learned seeds","seed_full_safe":"Learned full-region seeds","seed_full_low_safe":"Learned seeds, lower threshold",
  "combined_safe":"Learned seeds and rows","combined_full_safe":"Full-region seeds and rows",
  "combined_full_low_safe":"Lower-threshold seeds and rows","split_native":"Native groups of 32",
  "split_combined_safe":"Learned groups of 32"}
 colors=["#325c9c","#be6a35"];plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
 def comp(a,b,size,metric="complete_seconds"):
  return next((c for c in s["comparisons"] if (c["left"],c["right"],c["size"],c["metric"])==(a,b,size,metric)),None)
 def save(fig,name):
  fig.tight_layout();fig.savefig(folder/(name+".pdf"),bbox_inches="tight");shutil.copy2(folder/(name+".pdf"),out/(name+".pdf"));plt.close(fig)
 policies=[p for p in f["policies"] if p!="stock"]
 fig,ax=plt.subplots(figsize=(7.0,5.1))
 yt=[]
 for i,p in enumerate(policies):
  counts=[]
  for j,size in enumerate([32,128]):
   c=comp(p,"stock",size);counts.append(c.get("paired_batches",0) if c else 0)
   if c and "ratio" in c:
    v=c["ratio"];ci=c["interval95"] or [v,v]
    ax.errorbar(v,i+(j-.5)*.26,xerr=np.array([[max(0,v-ci[0])],[max(0,ci[1]-v)]]),
      fmt="o",markersize=4,capsize=2,color=colors[j],label=f"{size} targets" if i==0 else None)
  yt.append(labels[p]+f" [{counts[0]}/{counts[1]}]")
 ax.axvline(1,color=".4",lw=.8,ls="--");ax.set_xscale("log");ax.set_yticks(range(len(policies)));ax.set_yticklabels(yt)
 ax.invert_yaxis();ax.set_xlabel("Complete-time ratio to stock Kira");ax.legend(frameon=False,loc="best")
 ax.grid(axis="x",alpha=.18);save(fig,"native_multiloop_times")
 cases=[c for c in json.loads((HERE/"families.json").read_text())["cases"] if c["split"]=="reserved"]
 short=["Box A","Box B","Vacuum A","Vacuum B","Ladder A","Ladder B"]
 fig,axes=plt.subplots(2,1,figsize=(7.0,5.8),sharex=True)
 specs=[("row_full","native","operations","Forward coefficient-operation ratio"),
        (f["seed_policy"],"native","initial_equations","Generated-equation ratio, including fallback")]
 for ax,(a,b,metric,title) in zip(axes,specs):
  for j,size in enumerate([32,128]):
   c=comp(a,b,size,metric)
   pairs={p["case"]:p["ratio"] for p in c.get("pairs",[])} if c else {}
   xx=[i+(j-.5)*.17 for i,case in enumerate(cases) if case["id"] in pairs]
   yy=[pairs[case["id"]] for case in cases if case["id"] in pairs]
   ax.plot(xx,yy,"o",color=colors[j],label=f"{size} targets",markersize=4)
  ax.axhline(1,color=".4",ls="--",lw=.8);ax.set_ylabel(title);ax.grid(axis="y",alpha=.18)
 axes[0].legend(frameon=False);axes[1].set_xticks(range(len(cases)));axes[1].set_xticklabels(short)
 save(fig,"native_multiloop_operations")
 fig,axes=plt.subplots(1,2,figsize=(8.0,5.3),sharey=True)
 policies=f["policies"]
 for ax,size in zip(axes,[32,128]):
  initial=[];rescued=[];planned=[]
  for p in policies:
   a=[r for r in rows if r["policy"]==p and int(r["size"])==size]
   first=sum(r["success"]=="True" and r["initial_success"]=="True" for r in a)
   complete=sum(r["success"]=="True" for r in a)
   initial.append(first);rescued.append(complete-first);planned.append(len(a))
  y=np.arange(len(policies))
  ax.barh(y,initial,color="#325c9c",label="First attempt")
  ax.barh(y,rescued,left=initial,color="#87a9cb",label="Completed by fallback")
  for i,(a,b,total) in enumerate(zip(initial,rescued,planned)):ax.text(total+.25,i,f"{a+b}/{total}",va="center",fontsize=7)
  ax.set_xlim(0,max(planned)+3.5);ax.set_title(f"{size} targets");ax.set_xlabel("Exactly completed trials")
  ax.set_yticks(y);ax.set_yticklabels([labels[p] for p in policies]);ax.grid(axis="x",alpha=.15)
 axes[0].invert_yaxis();handles,legend_labels=axes[1].get_legend_handles_labels();fig.legend(handles,legend_labels,frameon=False,loc="lower center",bbox_to_anchor=(.63,-.06),ncol=2,fontsize=7)
 save(fig,"native_multiloop_completion")
 print("Wrote three standalone figure PDFs and retained their source CSV",flush=True)
if __name__=="__main__":main()
