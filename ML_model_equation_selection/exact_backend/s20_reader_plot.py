"""Plot exact arithmetic, complete output costs and learned strategy results."""
from s14_reader import *
def main():
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 import shutil
 s=read(HERE/"reader_final_test/summary.json");out=HERE/"reader_final_test/plots";out.mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False})
 names=["baseline","integer","native_json","native_binary","learned"];labels=["Previous arithmetic","Integer polynomials","GMP, JSON output","GMP, binary output","Learned strategy"]
 fig,axs=plt.subplots(1,2,figsize=(9,3.5))
 for ax,metric,title in zip(axs,["external_seconds","roundtrip_seconds"],["Including startup and saving","Including output decoding"]):
  for arm,label in zip(names,labels):ax.plot(range(1,13),[g["medians"][arm][metric] for g in s["groups"]],marker="o",markersize=3,label=label)
  ax.set(xlabel="Reserved batch",ylabel="Median time (s)",title=title);ax.grid(alpha=.2)
 fig.legend(*axs[0].get_legend_handles_labels(),loc="lower center",ncol=3,frameon=False);fig.tight_layout(rect=(0,.16,1,1));fig.savefig(out/"exact_backend_reader_times.pdf");plt.close(fig)
 fig,axs=plt.subplots(1,2,figsize=(9,3.5))
 for i,(arm,label) in enumerate([("baseline","Previous"),("native","GMP + binary"),("learned","Learned"),("deployed","Deployed")]):
  for ax,metric in zip(axs,["external_seconds","roundtrip_seconds"]):
   ax.bar([k+(i-1.5)*.18 for k in range(3)],[s["sequences"][k]["medians"][arm][metric] for k in range(3)],width=.18,label=label)
 for ax,title in zip(axs,["Complete four-batch stream","With output decoding"]):
  ax.set_xticks(range(3));ax.set_xticklabels(["Stream 1","Stream 2","Stream 3"]);ax.set(title=title,ylabel="Median time (s)");ax.grid(axis="y",alpha=.2)
 axs[0].legend(fontsize=8);fig.tight_layout();fig.savefig(out/"exact_backend_reader_streams.pdf");plt.close(fig)
 for p in out.glob("*.pdf"):shutil.copyfile(p,ROOT/"report/figures"/p.name)
if __name__=="__main__":main()
