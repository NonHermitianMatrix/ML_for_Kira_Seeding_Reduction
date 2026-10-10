"""Plot complete times relative to the preceding implementation and native control."""
import json,pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 d=json.loads((HERE/"fast_evaluation/confirmation_summary.json").read_text());rows=d["batches"]
 labels=[];names={}
 for r in rows:
  key=(r["topology"],r["group"])
  if key not in names:names[key]=chr(65+sum(k[0]==r["topology"] for k in names))
  title={"sunrise":"2-loop sunrise","double_box":"2-loop box","vacuum3":"3-loop vacuum","ladder3":"3-loop ladder"}[r["topology"]]
  labels.append(f'{title} {names[key]}, {r["size"]}')
 plt.rcParams.update({"font.size":8})
 fig,axes=plt.subplots(1,2,figsize=(7,6.4),sharey=True)
 methods=[("seed","Seed"),("row","Row"),("both","Both"),("auto","Auto")]
 for j,(method,label) in enumerate(methods):
  y=[i+(j-1.5)*.12 for i in range(len(rows))]
  for panel,ax in enumerate(axes):
   ratios=[r["methods"][method+"_new"]["complete_seconds"]/r["methods"][method+"_old" if panel==0 else "native_new"]["complete_seconds"] for r in rows]
   ax.scatter(ratios,y,s=12,label=label)
 for ax in axes:
  ax.axvline(1,color="black",lw=.65);ax.grid(axis="x",alpha=.2);ax.set_axisbelow(True)
  for spine in ["top","right"]:ax.spines[spine].set_visible(False)
 axes[0].set_yticks(range(len(rows)),labels);axes[0].invert_yaxis()
 axes[0].set_xlabel("New time / preceding time");axes[1].set_xlabel("New time / new native time")
 fig.legend(*axes[0].get_legend_handles_labels(),loc="upper center",ncol=4,frameon=False)
 fig.tight_layout(rect=(0,0,1,.94))
 fig.savefig(ROOT/"report/figures/shared_evaluation_times.pdf",bbox_inches="tight");plt.close(fig)
if __name__=="__main__":main()
