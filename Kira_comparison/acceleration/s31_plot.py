"""Create exportable plots from completed, matched native comparisons."""
import json,os,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".tools/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator,NullLocator,FuncFormatter
s=json.loads((HERE/"summary.json").read_text())
seed=s["selected_seed_policy"];learned=[seed,"row_cpp","combined"];controls=["trim","tight","pool_filter"]
names={seed:"Learned seeds","row_cpp":"Learned rows","combined":"Both models",
       "trim":"restricted Kira","tight":"target bounds","pool_filter":"full seed pool"}
colors={seed:"#0072B2","row_cpp":"#D55E00","combined":"#009E73"}
lookup={(x["numerator"],x["denominator"],x["metric"]):x for x in s["comparisons"]}
pairs=[(a,b) for a in learned for b in controls]
plt.rcParams.update({"font.size":9,"axes.titlesize":10,"pdf.fonttype":42,"ps.fonttype":42})
def figure(metrics,titles,name):
 fig,axes=plt.subplots(2,1,figsize=(7.2,7.5),sharey=True)
 for axis,metric,title in zip(axes,metrics,titles):
  endpoints=[]
  for j,(a,b) in enumerate(pairs):
   x=lookup[a,b,metric];y=len(pairs)-1-j
   if x["ratio"] is None:
    axis.text(.03,y,"No complete pairs",transform=axis.get_yaxis_transform(),color=".45",fontsize=8)
    continue
   value=x["ratio"];lo,hi=x["interval95"];endpoints += [lo,hi,value]
   axis.errorbar(value,y,xerr=[[max(0,value-lo)],[max(0,hi-value)]],fmt="o",color=colors[a],capsize=3,markersize=4)
   axis.text(1.015,y,"n=%d"%x["batches"],transform=axis.get_yaxis_transform(),va="center",fontsize=8)
  axis.axvline(1,color=".3",linestyle="--",linewidth=.9)
  axis.set_xscale("log")
  axis.xaxis.set_major_locator(LogLocator(base=10,subs=(1.,2.,3.,4.,6.)))
  axis.xaxis.set_major_formatter(FuncFormatter(lambda value,pos:format(value,"g")))
  axis.xaxis.set_minor_locator(NullLocator())
  if endpoints:axis.set_xlim(min(.9,min(endpoints)*.8),max(1.1,max(endpoints)*1.2))
  axis.set_yticks(range(len(pairs)))
  axis.set_yticklabels([names[a]+" / "+names[b] for a,b in reversed(pairs)])
  axis.set_title(title);axis.set_xlabel("Ratio to control; lower values indicate less cost")
  axis.grid(axis="x",alpha=.2)
  axis.spines[["top","right"]].set_visible(False)
  for y in [2.5,5.5]:axis.axhline(y,color=".85",linewidth=.6)
 axes[1].tick_params(labelleft=True)
 fig.subplots_adjust(left=.39,right=.92,bottom=.07,top=.95,hspace=.42)
 fig.savefig(ROOT/"report/figures"/name,bbox_inches="tight");plt.close(fig)
figure(["total_seconds","native_with_inference_seconds"],
 ["Complete checked reduction time","Native Kira time plus seed inference"],"native_acceleration_times.pdf")
figure(["generated_equations","forward_updates"],
 ["Equations reported across generation passes","Committed forward row updates"],"native_acceleration_work.pdf")
print("Native comparison figures written")
