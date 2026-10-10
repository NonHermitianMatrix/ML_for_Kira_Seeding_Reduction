"""Plot complete and forward-stage costs after the two-row shortcut."""
import json,pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 data=json.loads((HERE/"pair_reserved_summary.json").read_text())["batches"]
 names={"sunrise":"2-loop sunrise","double_box":"2-loop box","vacuum3":"3-loop vacuum","ladder3":"3-loop ladder"}
 labels=[f'{names[r["topology"]]} {chr(65+int(r["case"].split("_")[2])%2)}, {r["size"]}' for r in data]
 plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"pdf.fonttype":42})
 fig,axes=plt.subplots(1,2,figsize=(7,6),sharey=True);ys=np.arange(len(data))
 for ax,field,title in zip(axes,["complete_seconds","forward_seconds"],["Complete time / native","Forward time / native"]):
  for j,(v,label) in enumerate([("seed","Seed"),("row","Row"),("combined","Both")]):
   values=[r["methods"][v][field]/r["methods"]["small"][field] if r["methods"][v]["complete_repeats"] and r["methods"]["small"]["complete_repeats"] else np.nan for r in data]
   ax.plot(values,ys+(j-1)*.17,"o",markersize=3.7,label=label)
  ax.axvline(1,color=".4",linewidth=.8);ax.grid(axis="x",alpha=.2);ax.set_xlabel(title)
  for edge in ["top","right"]:ax.spines[edge].set_visible(False)
 axes[0].set_yticks(ys);axes[0].set_yticklabels(labels);axes[0].invert_yaxis();axes[0].set_ylabel("Physical profile and target count")
 handles,legend=axes[0].get_legend_handles_labels();fig.legend(handles,legend,ncol=3,loc="upper center",frameon=False)
 fig.tight_layout(rect=(0,0,1,.95));fig.savefig(ROOT/"report/figures/integrated_pair_times.pdf",bbox_inches="tight");plt.close(fig)
if __name__=="__main__":main()
