"""Plot complete-cost ratios for the frozen whole-expression confirmation."""
import argparse,json,os,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".tools/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator,NullLocator,FuncFormatter
ap=argparse.ArgumentParser();ap.add_argument("--matched",action="store_true");args=ap.parse_args()
s=json.loads((HERE/("expression_matched_summary.json" if args.matched else "expression_test_summary.json")).read_text())
rows=s["comparisons"]
plt.rcParams.update({"font.size":9,"pdf.fonttype":42,"ps.fonttype":42})
fig,ax=plt.subplots(figsize=(7.3,4.4))
labels=[]
for i,row in enumerate(rows):
 size=row["size"];scope="all batches" if size is None else "%d target%s"%(size,"" if size==1 else "s")
 name="Distance / full pool" if row["numerator"].startswith("stored_distance") else "ML / "+("full pool" if row["denominator"]=="stored_pool" else "distance")
 labels.append(name+"; "+scope)
 y=len(rows)-1-i
 if row["ratio"] is not None:
  v=row["ratio"];lo,hi=row["interval95"]
  ax.errorbar(v,y,xerr=[[max(0,v-lo)],[max(0,hi-v)]],fmt="o",capsize=3,color="#0072B2" if row["denominator"]=="stored_pool" else "#D55E00")
  ax.text(1.02,y,"n=%d"%row["paired_batches"],transform=ax.get_yaxis_transform(),va="center",fontsize=8)
 else:ax.text(.05,y,"No complete pairs",transform=ax.get_yaxis_transform())
ax.set_yticks(range(len(rows)));ax.set_yticklabels(list(reversed(labels)))
ax.axvline(1,color=".4",linestyle="--")
ax.set_xscale("log");ax.xaxis.set_major_locator(LogLocator(base=10,subs=(1.,2.,3.,4.,6.)))
ax.xaxis.set_major_formatter(FuncFormatter(lambda value,pos:format(value,"g")));ax.xaxis.set_minor_locator(NullLocator())
ax.set_xlabel("Complete-time ratio; lower values indicate less cost")
ax.set_title("Same early master check for both seed-selection methods" if args.matched else "Direct reduction of complete target expressions")
ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False)
fig.subplots_adjust(left=.36,right=.89,bottom=.15,top=.89)
fig.savefig(ROOT/("report/figures/whole_expression_matched_times.pdf" if args.matched else "report/figures/whole_expression_times.pdf"),bbox_inches="tight");plt.close(fig)
print("Whole-expression timing figure written")
