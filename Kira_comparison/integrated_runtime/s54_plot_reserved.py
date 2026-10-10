"""Render exact paired complete-time and operation comparisons."""
import json,pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 data=json.loads((HERE/"summary.json").read_text())["batches"]
 plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.labelsize":9,"pdf.fonttype":42})
 labels=[];names={"sunrise":"2-loop sunrise","double_box":"2-loop box","vacuum3":"3-loop vacuum","ladder3":"3-loop ladder"}
 for r in data:
  index=int(r["case"].split("_")[2]);labels.append(f'{names[r["topology"]]} {chr(65+index%2)}, {r["size"]} targets')
 for field,stem,xlabel,comparisons in [
  ("complete_seconds","integrated_runtime_times","Complete time / smaller native time",[("seed","small","Seed model"),("row","small","Row model"),("combined","small","Both models")]),
  ("operations","integrated_runtime_operations","Committed forward operations / control",[("seed","small","Seed / native"),("row","small","Row / native"),("combined","seed","Both / seed")])]:
  fig,ax=plt.subplots(figsize=(6.8,6.2));ys=np.arange(len(data))
  for j,(a,b,label) in enumerate(comparisons):
   x=[r["methods"][a][field]/r["methods"][b][field] if r["methods"][a]["complete_repeats"] and r["methods"][b]["complete_repeats"] else np.nan for r in data]
   ax.plot(x,ys+(j-1)*.17,"o",markersize=4,label=label)
  ax.axvline(1,color=".35",linewidth=.8);ax.set_yticks(ys);ax.set_yticklabels(labels);ax.invert_yaxis();ax.set_xlabel(xlabel)
  ax.grid(axis="x",alpha=.2);ax.legend(loc="upper center",bbox_to_anchor=(.5,1.1),ncol=3,frameon=False)
  ax.spines[["top","right"]].set_visible(False)
  fig.tight_layout();fig.savefig(ROOT/"report/figures"/(stem+".pdf"),bbox_inches="tight");plt.close(fig)
if __name__=="__main__":main()
