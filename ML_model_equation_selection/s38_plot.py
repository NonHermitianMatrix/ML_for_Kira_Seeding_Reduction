"""Plot measured complete costs, preparation work and held-out label scores."""
import json,pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 s=json.loads((HERE/"model_test/summary.json").read_text())
 out=HERE/"model_test/plots";out.mkdir(exist_ok=True)
 plt.rcParams.update({"font.size":9,"pdf.fonttype":42,"ps.fonttype":42})
 keys=sorted(s["comparisons"]);names={"auto":"Validation route","learned":"Learned filter","distance":"Distance filter"}
 batches=s["batches"]
 fig,ax=plt.subplots(figsize=(10,4.1))
 x=np.arange(len(batches))
 for j,key in enumerate(keys):
  vals=[b["methods"][key]["complete_seconds"]/b["methods"]["off:0"]["complete_seconds"] for b in batches]
  ax.plot(x,vals,marker=["o","s","^"][j],label=names[key.split(":")[0]],lw=1.1,ms=4)
 ax.axhline(1,color="black",lw=.8,ls="--")
 ax.set_xticks(x);ax.set_xticklabels([b["case"].replace("equation_test_","")+f'\n{b["size"]} targets' for b in batches],rotation=45,ha="right",fontsize=7)
 ax.set_ylabel("Complete-time ratio to native choices")
 ax.legend(frameon=False,ncol=3);ax.grid(axis="y",alpha=.2)
 fig.tight_layout();fig.savefig(out/"complete_times.pdf");fig.savefig(out/"complete_times.png",dpi=140);plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(10,3.2))
 for ax,field,label in zip(axes,["complete_seconds","equation_preparation_seconds","generated_equations"],["Complete time","Equation preparation time","Generated equations"]):
  for j,key in enumerate(keys):
   z=s["comparisons"][key][field];v=z["ratio"];lo,hi=z["interval95"]
   ax.errorbar(j,v,yerr=[[max(0,v-lo)],[max(0,hi-v)]],fmt="o",capsize=4)
  ax.axhline(1,color="black",lw=.8,ls="--");ax.set_title(label)
  ax.set_xticks(range(len(keys)));ax.set_xticklabels([names[k.split(":")[0]].replace(" ","\n") for k in keys])
  ax.set_ylabel("Ratio to native choices");ax.grid(axis="y",alpha=.2)
 fig.tight_layout();fig.savefig(out/"aggregate_costs.pdf");fig.savefig(out/"aggregate_costs.png",dpi=140);plt.close(fig)
 labels=json.loads((HERE/"model_test/label_metrics.json").read_text());hist=np.array(labels["histogram"])
 fig,ax=plt.subplots(figsize=(6.4,3))
 centers=(np.arange(20)+.5)/20
 ax.bar(centers,hist[:,0],width=.045,label="Support absent from selected set")
 ax.bar(centers,hist[:,1],bottom=hist[:,0],width=.045,label="Support present in selected set")
 ax.set_xlabel("Model score");ax.set_ylabel("Held-out candidate equations");ax.set_yscale("symlog",linthresh=10)
 ax.legend(frameon=False,fontsize=8);fig.tight_layout()
 fig.savefig(out/"label_scores.pdf");fig.savefig(out/"label_scores.png",dpi=140);plt.close(fig)
 for name in ["complete_times","aggregate_costs","label_scores"]:
  (ROOT/"report/figures"/("equation_"+name+".pdf")).write_bytes((out/(name+".pdf")).read_bytes())
if __name__=="__main__":main()
