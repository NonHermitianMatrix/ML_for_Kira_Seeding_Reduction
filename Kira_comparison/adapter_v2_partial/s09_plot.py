"""Plot verified matched runtime, solver work, model work and memory."""
from s01_common import *
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def main():
 data=read(HERE/"summary.json");figdir=HERE/"figures";figdir.mkdir(exist_ok=True)
 labels={"ml_seeds":"Learned seeds + Kira","ml_reduction":"Learned rows + Kira","local_reduction":"Local rows + Kira"}
 colors={"ml_seeds":"#2166ac","ml_reduction":"#b2182b","local_reduction":"#59656f"}
 def save(fig,name):
  fig.tight_layout();fig.savefig(figdir/(name+".pdf"),bbox_inches="tight")
  fig.savefig(figdir/(name+".png"),dpi=135,bbox_inches="tight");plt.close(fig)
 def clean(ax):
  for side in ("top","right"):ax.spines[side].set_visible(False)
  ax.grid(axis="y",alpha=.18)
 matched=[c for c in data["comparisons"] if c["baseline"]=="kira_pool"]
 fig,axes=plt.subplots(1,2,figsize=(10,4.0))
 for ax,kind,title in zip(axes,["cold_ratio","warm_ratio"],["Complete process, including model load","In-process work, excluding model load"]):
  for k,c in enumerate(matched):
   values=[x[kind] for x in c["pairs_detail"]]
   offsets=np.linspace(-.1,.1,len(values))
   ax.scatter(k+offsets,values,s=13,alpha=.55,color=colors[c["policy"]])
   ax.plot([k-.2,k+.2],[np.median(values)]*2,color="black",lw=2)
  ax.axhline(1,color="black",ls="--",lw=.8)
  ax.set_xticks(range(len(matched)));ax.set_xticklabels([labels[c["policy"]].replace(" + Kira","\n+ Kira") for c in matched],fontsize=9)
  ax.set_yscale("log");ax.set_ylabel("Time / Kira with full stored pool");ax.set_title(title,fontsize=10);clean(ax)
 save(fig,"kira_comparison_time")
 cases=data["cases"];lookup={(x["case"],x["size"],x["policy"]):x for x in cases}
 pairs=[]
 for x in cases:
  if x["policy"]!="ml_seeds" or not x["all_complete"]:continue
  b=lookup[x["case"],x["size"],"kira_pool"]
  if b["all_complete"]:pairs.append((x,b))
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for ax,field,label in zip(axes,["source_equations","selected_equations"],["Supplied source equations","Equations selected by Kira"]):
  for x,b in pairs:
   marker="s" if x["fallback_repeats"] else "o"
   ax.scatter(b[field],x[field],marker=marker,color="#2166ac",alpha=.65,s=28)
  maximum=max([max(b[field],x[field]) for x,b in pairs]+[1])
  ax.plot([0,maximum],[0,maximum],ls="--",color="black",lw=.8)
  ax.set_xlabel("Kira with full stored pool");ax.set_ylabel("Learned seeds, including fallback");ax.set_title(label,fontsize=10);clean(ax)
 axes[1].text(.03,.96,"Square: fallback used",transform=axes[1].transAxes,va="top",fontsize=9)
 save(fig,"kira_comparison_equations")
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for c in matched:
  v=[x["rss_ratio"] for x in c["pairs_detail"]]
  k=list(labels).index(c["policy"]);axes[0].scatter(k+np.linspace(-.1,.1,len(v)),v,s=13,alpha=.5,color=colors[c["policy"]])
 axes[0].set_xticks(range(3));axes[0].set_xticklabels(["Learned seeds","Learned rows","Local rows"],fontsize=9)
 axes[0].set_ylabel("Peak summed RSS / full-pool Kira");axes[0].axhline(1,ls="--",lw=.8,color="black");clean(axes[0])
 for x in cases:
  if x["policy"]!="ml_reduction" or not x["all_complete"]:continue
  b=lookup.get((x["case"],x["size"],"local_reduction"))
  if b and b["all_complete"]:axes[1].scatter(b["coefficient_field_operations"],x["coefficient_field_operations"],s=23,color="#b2182b",alpha=.6)
 limit=max(axes[1].get_xlim()[1],axes[1].get_ylim()[1]);axes[1].plot([0,limit],[0,limit],ls="--",lw=.8,color="black")
 axes[1].set_xlabel("Local-rule coefficient operations");axes[1].set_ylabel("Learned coefficient operations");clean(axes[1])
 save(fig,"kira_comparison_memory_operations")
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for ax,baseline,title in zip(axes,["kira_native","kira_native_trim"],["Native Kira: default seeding","Native Kira: restricted seeding"]):
  for k,policy in enumerate(["ml_seeds","ml_reduction","local_reduction"]):
   c=next((c for c in data["comparisons"] if c["baseline"]==baseline and c["policy"]==policy),None)
   if c:
    v=[x["cold_ratio"] for x in c["pairs_detail"]]
    ax.scatter(k+np.linspace(-.1,.1,len(v)),v,s=17,alpha=.6,color=colors[policy])
  ax.axhline(1,ls="--",lw=.8,color="black");ax.set_xticks(range(3));ax.set_xticklabels(["Learned seeds","Learned rows","Local rows"],fontsize=9)
  ax.set_yscale("log");ax.set_ylabel("Complete time / native Kira");ax.set_title(title,fontsize=10);clean(ax)
 save(fig,"kira_comparison_native")
 print("Four PDF/PNG plots written")
if __name__=="__main__":main()
