"""Create standalone scientific plots of the direct cumulative comparison."""
from s00_cumulative import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def main():
 s=read(HERE/"test/summary.json");assert s["all_exact"]
 fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout="constrained")
 x=list(range(1,9));names={"original_kira":"Original Kira, full pool","chain_baseline":"Earlier pipeline, full pool","final":"Final deployed route"}
 for a in ARMS:
  axes[0].plot(x,[g["medians"][a]["roundtrip_seconds"] for g in s["groups"]],marker="o",label=names[a])
 axes[0].set_yscale("log");axes[0].set_ylabel("Median total time, including output reading (s)");axes[0].set_xlabel("Reserved batch")
 axes[0].legend(fontsize=8)
 for a in ["original_kira","chain_baseline"]:
  axes[1].plot(x,[g["medians"][a]["roundtrip_seconds"]/g["medians"]["final"]["roundtrip_seconds"] for g in s["groups"]],marker="o",label=names[a])
 axes[1].set_ylabel("Baseline time / final time");axes[1].set_xlabel("Reserved batch");axes[1].legend(fontsize=8)
 for ax in axes:ax.grid(alpha=.2);ax.set_xticks(x)
 for path in [HERE/"test/cumulative_speedup.pdf",ROOT/"report/figures/cumulative_speedup.pdf"]:
  path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path)
 plt.close(fig)
if __name__=="__main__":main()
