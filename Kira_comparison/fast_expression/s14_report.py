"""Write measured results, a figure and the scientific report after validation."""
import argparse,csv,hashlib,json,math,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/"report"
ABSTRACT="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
def read(p):return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);a=ap.parse_args()
 assert len(a.data_commit)==40 and all(c in "0123456789abcdef" for c in a.data_commit)
 s=read(HERE/"test_summary.json");audit=read(HERE/"test_validation.json");dev=read(HERE/"development_summary.json")
 assert audit["passed"] and s["planned"]==480
 find=lambda n,d,b:next(c for c in s["comparisons"] if (c["numerator"],c["denominator"],c["size"])==(n,d,b))
 def percent(c):return 100*(1-c["ratio"])
 def ci(c):return "$["+f'{c["interval95"][0]:.3f},{c["interval95"][1]:.3f}'+"]$"
 def result(c):
  return f'{c["ratio"]:.3f}, with a descriptive 95\\% interval {ci(c)} from {c["paired_batches"]} complete paired batches'
 primary=find("exit_ml","stock_ml",1);bigger=find("exit_ml","stock_ml",16)
 learned=find("exit_ml","exit_pool",1);learned_big=find("exit_ml","exit_pool",16)
 overall=find("exit_ml","stock_pool",1);direct=find("exit_pool","stock_pool",1)
 text=r"""\subsection{Reducing fixed waits in the exact reduction workflow}
The preceding comparisons show that the cost of using the seed model
depends on the full reduction workflow. Inspection of the Kira version
used here found a fixed one-second wait each time the program closed
a Fermat process. Fermat performs exact rational-function arithmetic,
and this wait occurs after the interface sends its exit command and
closes its pipes. The program then checks whether the child has exited
and forces termination if it is still running.

We replaced this fixed wait with repeated checks of the same child
process at two-millisecond intervals. The modified interface returns
as soon as it observes the exit and retains a one-second grace period
before forced termination. It also handles interrupted checks and
already reaped children. Tests checked normal exits, delayed exits,
forced termination, invalid process identifiers and the absence of
unreaped children. We built this change separately from the original
Kira executable. The symbolic elimination code, rational coefficients,
model weights and seed threshold remain unchanged
\cite{KiraResponsiveExitData}.

This change acts on a distinct part of the complete cost,
\begin{equation}
 T_{\rm total}=T_{\rm input}+T_{\rm model}+T_{\rm algebra}
             +T_{\rm exit}+T_{\rm check}.
\end{equation}
Here $T_{\rm input}$ includes loading and equation preparation,
$T_{\rm model}$ includes loading the seed model and computing its scores,
$T_{\rm algebra}$ is the time spent in exact reduction,
$T_{\rm exit}$ is the time needed to close its arithmetic processes,
and $T_{\rm check}$ is the final coefficient-verification time.
Failed attempts and fallback contribute to the corresponding terms.
Removing the fixed part of $T_{\rm exit}$ can improve a short reduction
without changing its algebraic operation count.

\subsubsection{Separating shutdown costs from learned seed selection}
We compare four complete workflows: the original Kira with all supplied
equations, the original Kira with learned seeds, the modified Kira with
all supplied equations, and the modified Kira with learned seeds.
The learned workflows use the existing model, the fixed threshold
$0.01$, the early master check and the same full-pool fallback.
Thus, comparing the two learned workflows isolates the shutdown change,
while comparing learned selection with the full pool within the modified
Kira measures the remaining benefit of that seed-selection workflow.

Development uses three instances from the original training partition.
The reserved comparison uses twelve other one-loop box instances in
six original-test kinematic groups that were absent from all earlier
box cost-test groups. Each instance has batches of one and sixteen
constructed targets, and each workflow receives five rotated repetitions
on the same node for that instance and batch size. We fixed the cases
before timing the change and froze the executable, code, model and
scientific inputs before the reserved runs.

Every measured time includes a fresh process start, input preparation,
model inference where applicable, exact Kira reduction, failed attempts,
fallback and exact coefficient checks. The prior generation of the shared
IBP identity pools is outside all four methods. Each trial uses one thread,
a 180-second complete-process cap, a 1.7 GB process-tree memory limit and
32 MiB of temporary storage. At most two trials run concurrently.
After a failed measured attempt, further identical repetitions are
marked as skipped and receive no measured time.

The timing comparison uses the median of five successful repetitions
for each method and batch. We form the geometric mean of their paired
time ratios and obtain descriptive 95\% intervals by resampling entire
kinematic groups 10,000 times. These intervals describe the completed
subset, and the separate completion counts retain every planned case.
"""
 text+=f'\nDevelopment produced {dev["exact"]} exact completions from {dev["executed"]} measured trials. The reserved comparison contains {s["planned"]} planned records, {s["executed"]} measured trials and {s["exact"]} exact completions. Independent checks evaluated {audit["independent_master_sample_checks"]:,} target coefficients against the raw Kira exports. Every completed reduction matched its exact reference coefficients.\n\n'
 labels={"stock_pool":"The original full-pool workflow","stock_ml":"The original learned workflow","exit_pool":"The modified full-pool workflow","exit_ml":"The modified learned workflow"}
 for policy,label in labels.items():
  t=s["totals"][policy]
  text+=f'{label} completed {t["exact"]} trials exactly, with {t["failed"]} failed measured trials and {t["skipped"]} skipped repetitions. Its completed trials required fallback {t["completed_fallbacks"]} times.\n\n'
 text+=r"\subsubsection{Measured complete-time changes}"+"\n"
 text+=f'For one target at a time, the modified learned workflow has a complete-time ratio of {result(primary)} relative to the original learned workflow. The corresponding geometric mean times are {primary["denominator_geometric_mean_seconds"]:.3f} and {primary["numerator_geometric_mean_seconds"]:.3f} seconds, a {percent(primary):.1f}\\% reduction. For sixteen targets, the ratio to the original learned workflow is {result(bigger)}.\n\n'
 text+=f'With the responsive shutdown active in both methods, learned seed selection has a one-target complete-time ratio of {result(learned)} relative to the full pool. The corresponding sixteen-target ratio is {result(learned_big)}. '
 if learned["interval95"][1]<1:
  text+=f'The one-target comparison therefore retains a measured {percent(learned):.1f}\\% reduction from the learned seed workflow after the shutdown improvement.'
 else:text+='The one-target interval includes one, so this comparison does not establish a consistent additional benefit from the learned seed workflow.'
 if learned_big["interval95"][1]<1:text+=f' The sixteen-target comparison also gives a measured {percent(learned_big):.1f}\\% reduction.'
 else:text+=' The sixteen-target interval includes one, so a consistent additional benefit remains unresolved for that batch size.'
 text+='\n\n'
 text+=f'The modified learned workflow has a one-target complete-time ratio of {result(overall)} relative to the original full-pool workflow. The full-pool workflow alone has a modified-to-original ratio of {result(direct)}. These controls show that the shutdown improvement applies to the exact solver independently of machine learning. The unchanged seed model supplies a separate choice of equations, whose incremental effect is measured against the modified full-pool control.\n\n'
 text+=f'Across {audit["binary_pair_checks"]} completed original/modified pairs, equation inputs and reported elimination counters agreed. The final raw coefficient exports were identical in {audit["identical_raw_export_pairs"]} pairs, and {audit["unchanged_prediction_pairs"]} paired prediction records agreed exactly. The change therefore improves process completion time while preserving the tested mathematical calculations. It does not establish fewer algebraic operations, a better trained model or a general multiloop speedup. The measured domain remains the specified supplied-identity reductions of constructed one-loop targets.\n\n'
 text+=r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/responsive_exit_times.pdf}
\caption{Complete-time ratios for responsive Fermat shutdown and learned
seed selection. Points show geometric means of paired five-repeat
medians; intervals resample kinematic groups. Each row compares the
same physical targets, and values below one indicate less complete time.}
\label{fig:responsive-exit-times}
\end{figure}
\FloatBarrier
"""
 (REPORT/"kira_fast_expression.tex").write_text(text)
 conclusion=f'The responsive Fermat shutdown further reduces the complete cost of the learned seed workflow. In twelve new held-out one-loop instances, its one-target time ratio to the original learned workflow is {primary["ratio"]:.3f}, with descriptive interval {ci(primary)}, and the paired geometric mean times decrease from {primary["denominator_geometric_mean_seconds"]:.3f} to {primary["numerator_geometric_mean_seconds"]:.3f} seconds. This {percent(primary):.1f}\\% reduction comes from closing arithmetic processes promptly; model weights and symbolic row operations remain unchanged. Against the full pool with the same shutdown improvement, the learned workflow has a one-target ratio of {learned["ratio"]:.3f}, with interval {ci(learned)}. All {s["exact"]} completed trials matched their exact reference coefficients. These comparisons retain failed attempts and measure existing IBP pools, so their conclusions concern the stated supplied-equation domain \\cite{{KiraResponsiveExitData}}.\n\n'
 mainpath=REPORT/"report.tex";maintext=mainpath.read_text()
 if r"\input{kira_fast_expression}" not in maintext:
  maintext=maintext.replace(r"\input{kira_acceleration}",r"\input{kira_acceleration}"+"\n"+r"\input{kira_fast_expression}")
 begin="% responsive-exit-conclusion-begin";end="% responsive-exit-conclusion-end"
 if begin in maintext:maintext=maintext.split(begin)[0]+maintext.split(end,1)[1].lstrip("\n")
 anchor="The higher-loop collection varies mass profiles within restricted"
 assert maintext.count(anchor)==1
 maintext=maintext.replace(anchor,begin+"\n"+conclusion+end+"\n\n"+anchor)
 abstract=maintext.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()==ABSTRACT
 mainpath.write_text(maintext)
 bib=REPORT/"references.bib";b=bib.read_text();key="@misc{KiraResponsiveExitData,"
 if key in b:b=b[:b.index(key)].rstrip()+"\n"
 b+=f'\n@misc{{KiraResponsiveExitData,\n  author = {{Rushil Saraswat}},\n  title = {{Responsive Fermat shutdown and learned seed selection in exact Kira reductions}},\n  year = {{2026}},\n  howpublished = {{\\url{{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{a.data_commit}/Kira_comparison/fast_expression}}}},\n  note = {{Frozen code, original and modified solver comparisons, exact checks and repeated complete timings}}\n}}\n'
 bib.write_text(b)
 make=REPORT/"Makefile";t=make.read_text()
 if "kira_fast_expression.tex" not in t:t=t.replace("kira_expression_matched.tex","kira_expression_matched.tex kira_fast_expression.tex")
 make.write_text(t)
 import matplotlib;matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 chosen=[primary,bigger,learned,learned_big,overall,direct]
 names=["Modified ML / original ML; 1 target","Modified ML / original ML; 16 targets","Modified ML / modified pool; 1 target","Modified ML / modified pool; 16 targets","Modified ML / original pool; 1 target","Modified pool / original pool; 1 target"]
 fig,ax=plt.subplots(figsize=(8,4.3))
 for i,c in enumerate(chosen):
  y=len(chosen)-1-i;r=c["ratio"];lo,hi=c["interval95"]
  ax.errorbar(r,y,xerr=[[max(0,r-lo)],[max(0,hi-r)]],fmt="o",capsize=3,color="#0072B2" if i<2 else "#D55E00")
  ax.text(1.01,y,f'n={c["paired_batches"]}',transform=ax.get_yaxis_transform(),va="center",fontsize=9)
 ax.axvline(1,color="0.4",linestyle="--",linewidth=1);ax.set_yticks(range(len(names)),list(reversed(names)),fontsize=9)
 ax.set_xlabel("Complete-time ratio; values below one indicate less time")
 ax.spines[["top","right"]].set_visible(False);ax.set_ylim(-.5,len(names)-.5)
 fig.tight_layout();fig.savefig(REPORT/"figures/responsive_exit_times.pdf",bbox_inches="tight");plt.close(fig)
 with (HERE/"figure_values.csv").open("w") as f:
  w=csv.writer(f);w.writerow(["numerator","denominator","size","ratio","lower95","upper95","pairs"])
  for c in s["comparisons"]:w.writerow([c["numerator"],c["denominator"],c["size"],c["ratio"],*(c["interval95"] or [None,None]),c["paired_batches"]])
 values=dict(data_commit=a.data_commit,primary=primary,modified_seed_effect=learned,modified_batch_effect=learned_big,abstract_sha256=ABSTRACT)
 (HERE/"report_values.json").write_text(json.dumps(values,indent=2)+"\n")
 print(json.dumps({"primary_reduction_percent":percent(primary),"exact_completions":s["exact"]}),flush=True)
if __name__=="__main__":main()
