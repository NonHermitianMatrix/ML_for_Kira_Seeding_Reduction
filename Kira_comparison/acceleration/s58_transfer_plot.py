"""Plot full-cost paired ratios for the fixed two-loop transfer check."""
import json,pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=json.loads((HERE/"transfer_summary.json").read_text())
plt.rcParams.update({"font.size":9})
fig,axes=plt.subplots(2,1,figsize=(7.2,7.5))
names={"ml_lower":"Learned seeds","trim":"Kira bounds","pool_filter":"Full pool","row_cpp":"Learned source","row_cpp_native":"Deterministic source","combined":"Combined"}
for ax,case in zip(axes,s["cases"]):
 labels=[]
 for i,c in enumerate(case["comparisons"]):
  labels.append(names[c["learned"]]+" / "+names[c["control"]])
  if c["complete_pair"]:
   v=c["ratio"];lo,hi=c["descriptive_interval"]
   ax.plot([lo,hi],[i,i],color="#356b91",lw=1.5)
   ax.plot(v,i,"o",color="#356b91")
  else:ax.text(.05,i,"Incomplete pair",transform=ax.get_yaxis_transform(),va="center")
 ax.set_yticks(range(len(labels)));ax.set_yticklabels(labels);ax.invert_yaxis();ax.axvline(1,color="black",lw=.8,ls="--")
 ax.set_xscale("log");ax.set_xlabel("Complete time ratio (below 1 is faster)")
 ax.set_title(str(case["size"])+" target expressions");ax.grid(axis="x",alpha=.2)
fig.subplots_adjust(left=.39,right=.97,top=.95,bottom=.08,hspace=.5)
fig.savefig(ROOT/"report/figures/native_transfer_times.pdf");plt.close(fig)
