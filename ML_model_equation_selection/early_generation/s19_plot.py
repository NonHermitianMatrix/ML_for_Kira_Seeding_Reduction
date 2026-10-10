"""Draw comparisons from the frozen, independently checked test results."""
import json,os,pathlib,shutil
from s04_workflows import HERE,ROOT,guard
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".tools/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
NAMES={"sunrise":"Two-loop sunrise","double_box":"Two-loop double box","vacuum3":"Three-loop vacuum","ladder3":"Three-loop ladder"}
def main():
 s=json.loads((HERE/"model_test/summary.json").read_text());assert s["all_exact"]
 out=HERE/"model_test/plots";out.mkdir(exist_ok=True)
 order=["sunrise","double_box","vacuum3","ladder3"]
 plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
 fig,axes=plt.subplots(1,2,figsize=(10.5,4.2),sharey=True)
 for ax,field,title in zip(axes,["complete_seconds","equation_preparation_seconds"],["Complete reduction time","Equation preparation time"]):
  for offset,method,label,color in [(-.2,"previous","Previous release","#666666"),(0,"deployed","Early equation model","#1d6685"),(.2,"control","Distance control","#a76524")]:
   points=[s["by_topology"][top][method+"_vs_native"][field] for top in order]
   values=np.array([v["ratio"] for v in points])
   err=np.array([[v["ratio"]-v["interval"][0] for v in points],[v["interval"][1]-v["ratio"] for v in points]])
   ax.errorbar(values,np.arange(4)+offset,xerr=err,fmt="o",ms=4,capsize=2,color=color,label=label)
  ax.axvline(1,color="black",linewidth=.8,linestyle="--");ax.set_title(title)
  ax.set_xlabel("Time / native time")
  ax.set_yticks(range(4));ax.set_yticklabels([NAMES[x] for x in order]);ax.grid(axis="x",alpha=.2)
 axes[0].invert_yaxis()
 axes[1].legend(fontsize=8,loc="best")
 fig.tight_layout();fig.savefig(out/"early_equation_costs.pdf");plt.close(fig)
 bs=s["batches_detail"]
 fig,ax=plt.subplots(figsize=(10.5,5.8))
 x=np.arange(len(bs))
 for method,color,label in [("native","#888888","Native"),("previous","#a76524","Previous release"),("deployed","#1d6685","Early equation model")]:
  ax.plot(x,[b["methods"][method]["complete_seconds"] for b in bs],"o-",ms=4,linewidth=1,color=color,label=label)
 labels=[]
 per_top={}
 for b in bs:
  ids=per_top.setdefault(b["topology"],{})
  ids.setdefault(b["case"],len(ids)+1)
  labels.append(b["topology"].replace("_"," ")+" "+str(ids[b["case"]])+"\n"+str(b["size"])+" targets")
 ax.set_xticks(x);ax.set_xticklabels(labels,rotation=60,ha="right",fontsize=8)
 ax.set_ylabel("Median complete time (seconds)");ax.legend(ncol=3);ax.grid(axis="y",alpha=.2)
 fig.tight_layout();fig.savefig(out/"early_equation_batches.pdf");plt.close(fig)
 for p in out.glob("*.pdf"):shutil.copyfile(p,ROOT/"report/figures"/p.name)
 guard();print(json.dumps({"plots":[str(p.relative_to(ROOT)) for p in out.glob("*.pdf")]}))
if __name__=="__main__":main()
