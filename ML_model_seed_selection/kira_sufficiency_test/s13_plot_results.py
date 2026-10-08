"""Plot exact seed sufficiency and the selected candidate fractions."""
import shutil,os
from pathlib import Path
cache=Path(__file__).resolve().parents[2]/".tools/cache/matplotlib"
cache.mkdir(parents=True,exist_ok=True)
os.environ["MPLCONFIGDIR"]=str(cache)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from s02_common import *
def main():
 r=read(HERE/"results.json");assert read(HERE/"validation.json")["passed"]
 dest=HERE/"figures";dest.mkdir(exist_ok=True)
 plt.rcParams.update({"font.size":11,"pdf.fonttype":42,"ps.fonttype":42})
 labels=["Predicted seeds","All candidates","No IBP seeds"];policies=["predicted","full","background"]
 colors=["#245a81","#bd6b25","#777777"];loops=sorted(map(int,r["by_loop"]))
 fig,axes=plt.subplots(1,2,figsize=(8.4,3.6),gridspec_kw={"width_ratios":[1,1.7]})
 rates=[100*r["policies"][p].get("sufficient",0)/r["targets"] for p in policies]
 bars=axes[0].bar(range(3),rates,color=colors,width=.65)
 axes[0].set_xticks(range(3));axes[0].set_xticklabels(["Predicted","All","None"]);axes[0].set_ylabel("Targets with sufficient seeds (%)")
 axes[0].set_xlabel("Supplied IBP seed set");axes[0].set_ylim(0,110)
 for bar,rate in zip(bars,rates):axes[0].text(bar.get_x()+bar.get_width()/2,rate+2,f"{rate:.2f}%",ha="center",fontsize=9)
 x=np.arange(len(loops));width=.25
 for i,(p,label,c) in enumerate(zip(policies,labels,colors)):
  rates=[100*r["by_loop"][str(l)][p].get("sufficient",0)/r["by_loop"][str(l)]["targets"] for l in loops]
  axes[1].bar(x+(i-1)*width,rates,width,label=label,color=c)
 axes[1].set_xticks(x);axes[1].set_xticklabels(loops);axes[1].set_xlabel("Number of loops");axes[1].set_ylim(0,112)
 axes[1].set_ylabel("Targets with sufficient seeds (%)");axes[1].legend(frameon=False,ncol=3,fontsize=8,loc="upper center")
 for a in axes:
  for name in ["top","right"]:a.spines[name].set_visible(False)
 fig.tight_layout()
 for ext in ["pdf","png"]:fig.savefig(dest/("kira_seed_sufficiency."+ext),dpi=160)
 plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(8.4,3.6))
 fractions=[100*r["by_loop"][str(l)]["selected_seeds"]/r["by_loop"][str(l)]["candidate_seeds"] for l in loops]
 axes[0].bar(x,fractions,color=colors[0]);axes[0].set_xticks(x);axes[0].set_xticklabels(loops)
 axes[0].set_xlabel("Number of loops");axes[0].set_ylabel("Candidate seeds selected (%)")
 g=r["reference_set_agreement"]
 counts=[g.get("same_complete",0),g.get("different_complete",0),g.get("same_incomplete",0)+g.get("different_incomplete",0)]
 labels=["Same set,\nsufficient","Different set,\nsufficient","Insufficient"]
 bars=axes[1].bar(range(3),[100*n/r["targets"] for n in counts],color=[colors[0],colors[1],colors[2]])
 axes[1].set_xticks(range(3));axes[1].set_xticklabels(labels);axes[1].set_ylabel("All tested targets (%)")
 for bar,n in zip(bars,counts):axes[1].text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f"{n:,}",ha="center",fontsize=8)
 axes[1].set_ylim(0,max(bar.get_height() for bar in bars)*1.17)
 for a in axes:
  for name in ["top","right"]:a.spines[name].set_visible(False)
 fig.tight_layout()
 for ext in ["pdf","png"]:fig.savefig(dest/("kira_seed_sets."+ext),dpi=160)
 plt.close(fig)
 for name in ["kira_seed_sufficiency.pdf","kira_seed_sets.pdf"]:shutil.copyfile(str(dest/name),str(ROOT/"report/figures"/name))
 write(dest/"manifest.json",{p.name:sha(p) for p in sorted(dest.glob("*")) if p.suffix in (".pdf",".png")})
if __name__=="__main__":main()
