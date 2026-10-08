"""Plot the direct native seed-envelope comparison."""
from s01_common import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def main():
 data=read(HERE/"native_seed/summary.json");figdir=HERE/"figures";figdir.mkdir(exist_ok=True)
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 comparisons=data["comparisons"]
 for ax,field,title in zip(axes,["cold_ratio","warm_ratio"],["Complete process","In-process work"]):
  for j,base in enumerate(["kira_native","kira_native_trim"]):
   c=next((x for x in comparisons if x["baseline"]==base),None)
   if c:
    v=[x[field] for x in c["pairs_detail"]]
    ax.scatter([j+(k-(len(v)-1)/2)*.025 for k in range(len(v))],v,color="#2166ac",s=30)
  ax.axhline(1,ls="--",color="black",lw=.8);ax.set_xticks([0,1]);ax.set_xticklabels(["Default Kira","Restricted Kira"])
  ax.set_yscale("log");ax.set_ylabel("Learned native bounds / baseline time");ax.set_title(title)
  for side in ("top","right"):ax.spines[side].set_visible(False)
  ax.grid(axis="y",alpha=.18)
 fig.tight_layout();fig.savefig(figdir/"kira_native_learned_seeds.pdf",bbox_inches="tight")
 fig.savefig(figdir/"kira_native_learned_seeds.png",dpi=135,bbox_inches="tight");plt.close(fig)
if __name__=="__main__":main()
