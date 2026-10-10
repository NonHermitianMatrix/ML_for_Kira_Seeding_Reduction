"""Write result prose and numeric provenance from checked, frozen comparisons."""
import collections,datetime,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name):return json.loads((HERE/name).read_text())
def num(v):return f"{v:,.0f}"
def ratio(c):
 if not c.get("paired_batches"):return "no complete paired batches"
 s=f"{c['ratio']:.3f}"
 if c.get("interval95"):s+=f" with descriptive interval $[{c['interval95'][0]:.3f},{c['interval95'][1]:.3f}]$"
 return s
def main():
 s=load("summary.json");v=load("verification.json");f=load("freeze.json")
 assert v["all_passed"] and s["planned"]==324
 def cmp(left,right,size=None,metric="complete_seconds"):
  return next(c for c in s["comparisons"] if (c["left"],c["right"],c["size"],c["metric"])==(left,right,size,metric))
 seed=f["seed_policy"];combined=f["combined_policy"];counts=s["counts"]
 refs=s["reference_calculations"];passed=[r for r in refs if r["success"]]
 text=r"""\subsection{Reserved results and complete-calculation cost}
The frozen comparison contains six reserved cases, two target-batch
sizes, nine policies and three repetitions of each policy. Each trial
begins with physical denominators and includes native IBP equation
generation. The results and exact evidence are available with the
comparison data~\cite{KiraCompleteMultiloopData}.
"""
 text+=f"\nWe measured {s['measured']} of {s['planned']} planned trials, and {s['completed']} completed every target with exact reference coefficients. "
 skipped=s["planned"]-s["measured"];failed=s["measured"]-s["completed"]
 text+=f"The records retain {failed} unsuccessful measured trials and {skipped} skipped trials. "
 text+=f"The independent audit checked {v['successful_reductions']:,} successful native reductions, including the training continuations and reserved attempts, and made {v['coefficient_comparisons']:,} coefficient comparisons by exact polynomial cross multiplication. "
 text+=f"All {v['verified_continuations']} recorded training and validation continuations passed. "
 text+=f"The separate larger-region check completed {v['expanded_bound_completions']} of {v['expanded_bound_attempts']} cases. "
 text+=r"These comparisons verify reduction to the prescribed basis; a finite region check does not prove that the basis is globally minimal."+"\n\n"
 text+=f"The measured workflows contain {s['native_attempts']} native reduction attempts. "
 rejected=sum(bool(a.get("master_admission_rejected")) for a in s["failed_attempts"])
 other=collections.Counter(a["status"] for a in s["failed_attempts"] if not a.get("master_admission_rejected"))
 text+=f"Kira rejected {rejected} attempted subsets because they required masters outside the prescribed basis. "
 if other:
  labels={"time_limit":"elapsed-time limits","scratch_limit":"scratch limits","memory_limit":"physical-memory limits","kira_error":"other Kira errors","exception":"preparation or reduction exceptions"}
  text+="The remaining unsuccessful attempts comprise "+", ".join(f"{n} {labels.get(k,k.replace('_',' '))}" for k,n in sorted(other.items()))+". "
 text+=r"These attempts remain in complete-workflow times, and the fallback sequence determines whether every target can still be reduced within the budget."+"\n\n"
 text+=f"The common reference preparation completed {len(passed)} of {len(refs)} case--batch calculations. "
 if passed:
  times=[r["complete_seconds"] for r in passed]
  text+=f"The successful reference times ranged from {min(times):.3f} to {max(times):.3f} seconds and are outside the paired production timings. "
 for topology,phrase in [("double_box","box"),("vacuum3","vacuum"),("ladder3","ladder")]:
  rr=[r for r in passed if r["size"]==128 and topology in r["case"]]
  if rr:
   masters=", ".join(str(r["master_count"]) for r in rr)
   zeros=", ".join(str(r["zero_targets"]) for r in rr)
   identities=", ".join(str(r["identity_master_targets"]) for r in rr)
   active=", ".join(str(128-r["zero_targets"]-r["identity_master_targets"]) for r in rr)
   assert len(rr)==2
   ma,mb=[r["master_count"] for r in rr]
   basis=f"{ma} master integrals each" if ma==mb else f"{ma} and {mb} master integrals, respectively"
   text+=f"The two 128-target {phrase} cases use {basis}. "
   za,zb=[r["zero_targets"] for r in rr];ia,ib=[r["identity_master_targets"] for r in rr]
   if (za,ia)==(zb,ib):
    text+=f"Both contain {za} zero targets and {ia} targets already in the master basis, leaving {128-za-ia} nonzero targets that require reduction in each case. "
   else:
    for label,r in zip(["first","second"],rr):
     text+=f"The {label} contains {r['zero_targets']} zero targets and {r['identity_master_targets']} targets already in the master basis, leaving {128-r['zero_targets']-r['identity_master_targets']} nonzero targets that require reduction. "
 text+="\n\n"
 text+=r"The following ratios use only case--batch pairs for which both policies completed all three repetitions. We take the median within each case and batch, average log ratios within a case, and then give cases equal weight. Ratios of operation counts also require positive counts in both methods. The intervals use 5,000 resamples of the fixed physical cases, so they describe this sample rather than a general distribution of multiloop families."+"\n\n"
 text+=r"\subsubsection{Seed selection and deterministic controls}"+"\n"
 text+=f"Validation selected the smaller-region learned seed policy at probability threshold $0.01$. Its complete-time ratio to instrumented native Kira was {f['validation_seed_scores'][0]['geometric_ratio']:.3f} on the validation sample; this selection therefore did not establish an aggregate validation gain. "
 text+=f"On reserved tests, its ratio to the responsive stock control is {ratio(cmp(seed,'stock'))}, and its ratio to the instrumented native control is {ratio(cmp(seed,'native'))}. "
 text+=f"Against the smaller deterministic region with fallback, the ratio is {ratio(cmp(seed,'tight'))}. "
 text+=f"Against the same low-complexity coverage rule without ML, the ratio is {ratio(cmp(seed,f['closure_control']))}. "
 text+=r"These controls separate the effects of region size, deterministic coverage, model inference and the learned additions."+"\n\n"
 for size in [32,128]:
  c=cmp(seed,"stock",size)
  text+=f"For {size} targets, the learned seed ratio to responsive stock Kira is {ratio(c)}"
  if c.get("paired_batches"):text+=f", using {c['paired_batches']} complete paired batches. The corresponding geometric mean median times are {c['geometric_left']:.3f} and {c['geometric_right']:.3f} seconds"
  text+=". "
 text+="\n\n"
 for topology,description in [("double_box","two-loop boxes"),("vacuum3","three-loop vacuum integrals"),("ladder3","three-loop ladders")]:
  cs=[c for c in s["topology_comparisons"] if c["topology"]==topology and c["left"]==seed and c["right"]=="stock" and c["size"] is None]
  if cs:
   c=cs[0];text+=f"For the {description}, the seed-to-stock time ratio is {ratio(c)}. "
   for control,label in [("tight","the smaller deterministic region"),(f["closure_control"],"the matched coverage rule")]:
    c=next(c for c in s["topology_comparisons"] if c["topology"]==topology and c["left"]==seed and c["right"]==control and c["size"] is None)
    text+=f"Its ratio to {label} is {ratio(c)}. "
 text+=r"These topology breakdowns retain every case in the stated class. The ladder class tests a topology absent from the new row-training and validation data."+"\n\n"
 for metric,description in [("initial_equations","initially generated equations summed across attempts"),("operations","committed forward coefficient-operation estimate")]:
  text+=f"The learned seed ratio for the {description} is {ratio(cmp(seed,'native',metric=metric))} relative to native Kira. "
 text+=r"The first generation count in each native attempt defines the equation measure; later selection counts are not added to it. The operation estimate follows Eq.~\eqref{eq:continuation-cost}, and all attempted stages contribute when a workflow requires fallback."+"\n\n"
 text+=r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/native_multiloop_times.pdf}
\caption{Complete-time ratios to responsive stock Kira for 32 and 128 indexed targets. Points use medians of three exact repetitions and equal case weights. Bars show descriptive case-resampling intervals; the labels give complete paired batch counts. A ratio below one means lower measured time in the stated paired cohort.}
\label{fig:native-multiloop-times}
\end{figure}
"""
 text+=r"\subsubsection{Repeated row decisions in the changing matrix}"+"\n"
 text+=f"The cost-trained row tree has a complete-time ratio of {ratio(cmp('row_full','native'))} to the instrumented native policy. "
 text+=f"Its forward coefficient-operation ratio is {ratio(cmp('row_full','native',metric='operations'))}, while the measured forward-stage time ratio is {ratio(cmp('row_full','native',metric='forward_seconds'))}. "
 text+=f"The paired geometric mean forward times are {cmp('row_full','native',metric='forward_seconds')['geometric_right']:.3f} seconds for native choices and {cmp('row_full','native',metric='forward_seconds')['geometric_left']:.3f} seconds for the tree, while their complete times are {cmp('row_full','native')['geometric_right']:.3f} and {cmp('row_full','native')['geometric_left']:.3f} seconds. Most measured time therefore lies outside this recorded forward stage. "
 text+=r"The sampled continuation objective measures one altered source choice followed by native choices. Repeated tree choices change the later matrices and can therefore change the cost in a different direction. The full-workflow results determine whether the trained model saves work in this use."+"\n\n"
 text+=f"The combined seed and row policy has a complete-time ratio of {ratio(cmp(combined,'stock'))} to responsive stock Kira. "
 text+=f"Its paired geometric mean median time is {cmp(combined,'stock')['geometric_left']:.3f} seconds, compared with {cmp(seed,'stock')['geometric_left']:.3f} seconds for seeds alone. The row addition therefore does not lower this point estimate. "
 text+=r"Combining two decisions requires a separate measurement because a different seed set changes the equations on which the row policy acts."+"\n\n"
 text+=r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/native_multiloop_operations.pdf}
\caption{Per-case median work ratios in the reserved comparison. The row panel measures committed forward coefficient operations relative to the same instrumented native policy. The seed panel measures initial generated equations, summed over attempts, relative to native Kira. Cases A and B follow the parameter order given in the text. Counts concern different stages and do not measure Fermat's internal polynomial work.}
\label{fig:native-multiloop-operations}
\end{figure}
"""
 text+=r"\subsubsection{Completion of larger target batches}"+"\n"
 for size in [32,128]:
  c=s["counts_by_size"][str(size)]
  text+=f"With {size} targets, responsive stock Kira completed {c['stock']['completed']} of {c['stock']['planned']} trials. "
  for policy,label in [(seed,"the learned seed workflow"),(combined,"the combined workflow"),("split_native","native groups of 32 targets"),("split_combined_safe","combined groups of 32 targets")]:
   r=c[policy];text+=f"For {label}, {r['completed']} of {r['planned']} completed, including {r['rescued_by_fallback']} rescued by fallback. "
  text+="\n\n"
 text+=f"For 128 targets, splitting the native workflow gives a time ratio of {ratio(cmp('split_native','stock',128))} to stock Kira. "
 text+=f"Splitting the combined workflow gives {ratio(cmp('split_combined_safe','stock',128))}. "
 text+=r"The separate fallback counts show whether completion improves; the paired times include repeated generation and process startup."+"\n\n"
 text+=r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/native_multiloop_completion.pdf}
\caption{Completion of all requested targets under the fixed time and storage limits. The filled components distinguish successful initial reductions from reductions completed through fallback. Unfilled trials include failed or explicitly skipped outcomes. Each policy has eighteen planned trials at each batch size.}
\label{fig:native-multiloop-completion}
\end{figure}
"""
 text+=r"\subsubsection{Scope and resource outcomes}"+"\n"
 text+=f"The largest recorded production process-tree memory use was {s['peak_tree_rss_bytes']/1024**2:.1f} MiB, and the largest monitored production scratch allocation was {s['peak_scratch_bytes']/1024**2:.1f} MiB. "
 allocation=sum(a.get("allocation_failure",False) for a in s["failed_attempts"])
 recursive=sum(a.get("recursive_termination",False) for a in s["failed_attempts"])
 text+=f"Among unsuccessful attempts, {allocation} logs report an allocation failure and {recursive} report recursive termination; these diagnostic counts can overlap. "
 text+=r"The fixed process limits constrain these outcomes, and the logs alone do not establish exhaustion of physical RAM. The workflow retains their costs and follows the same fallback rule."+" "
 if s.get("scheduler_interruption"):
  text+=r"One scheduler interruption stopped a test worker when the sum of its processes' virtual address spaces exceeded the job limit. We preserved its completed records and resumed only missing work with a larger scheduler address-space allowance, while keeping the measured physical-memory, scratch and elapsed-time limits fixed. This interruption is recorded separately from completed workflow timings. "
 if s.get("without_resumed_case"):
  for a,b,label in [(seed,"stock","learned seed to stock"),("row_full","native","learned row to native")]:
   c=next(c for c in s["without_resumed_case"] if c["left"]==a and c["right"]==b and c["size"] is None)
   text+=f"With the resumed case excluded, the {label} complete-time ratio is {ratio(c)}. "
 text+=r"The tests include two- and three-loop systems at fixed rational kinematics, a finite prescribed seed region and a restricted source-row action. They do not establish a speedup for arbitrary symbolic kinematics, every multiloop topology, or the earlier restricted collection through twelve loops."+"\n\\FloatBarrier\n"
 (ROOT/"report/kira_multiloop_results.tex").write_text(text)
 values=dict(summary_sha256=hashlib.sha256((HERE/"summary.json").read_bytes()).hexdigest(),
  verification_sha256=hashlib.sha256((HERE/"verification.json").read_bytes()).hexdigest(),
  freeze_sha256=hashlib.sha256((HERE/"freeze.json").read_bytes()).hexdigest(),
  planned=s["planned"],measured=s["measured"],completed=s["completed"],counts=s["counts"],
  comparisons=s["comparisons"],topology_comparisons=s["topology_comparisons"],
  reference_calculations=refs,verification=v)
 (HERE/"report_values.json").write_text(json.dumps(values,indent=2)+"\n")
 write_readmes(s,v,f)
 write_conclusion(s,f)
 print(json.dumps(dict(report="report/kira_multiloop_results.tex",planned=s["planned"],completed=s["completed"])))

def write_readmes(s,v,f):
 seed=f["seed_policy"]
 def find(a,b,metric="complete_seconds"):
  return next(c for c in s["comparisons"] if c["left"]==a and c["right"]==b and c["size"] is None and c["metric"]==metric)
 def rtext(c):
  if not c.get("paired_batches"):return "no complete paired batches"
  return f"{c['ratio']:.6f} ({c['paired_batches']} paired batches)"
 lines=[f"The fixed complete-generation experiment has {s['planned']} planned workflows, {s['measured']} measured workflows and {s['completed']} exact completions.",
  f"The selected seed policy's complete-time ratio to responsive stock Kira is {rtext(find(seed,'stock'))}.",
  f"The cost-trained row policy's complete-time ratio to instrumented native Kira is {rtext(find('row_full','native'))}; its forward coefficient-operation ratio is {rtext(find('row_full','native','operations'))}.",
  "These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.",
  "The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup."]
 by_topology=[]
 for topology,label in [("double_box","two-loop boxes"),("vacuum3","three-loop vacua"),("ladder3","three-loop ladders")]:
  c=next(c for c in s["topology_comparisons"] if c["topology"]==topology and c["left"]==seed and c["right"]=="stock" and c["size"] is None)
  by_topology.append(f"{c['ratio']:.6f} for {label}")
 lines.insert(2,"Seed-to-stock time ratios are "+", ".join(by_topology)+". The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.")
 block="\n\n".join(lines)
 marker="<!-- native-multiloop-results-begin -->";end="<!-- native-multiloop-results-end -->"
 for filename,link in [
  ("README.md","Kira_comparison/multiloop_native/README.md"),
  ("Kira_comparison/README.md","multiloop_native/README.md"),
  ("ML_model_reduction/README.md","../Kira_comparison/multiloop_native/README.md"),
  ("ML_model_seed_selection/README.md","../Kira_comparison/multiloop_native/README.md"),
  ("integrals/README.md","../Kira_comparison/multiloop_native/README.md")]:
  p=ROOT/filename;s0=p.read_text()
  if marker in s0:s0=s0.split(marker)[0]+s0.split(end,1)[1]
  s0=s0.rstrip()+"\n\n"+marker+"\n## Complete multiloop cost comparison\n\n"+block+f"\n\n[Methods, raw evidence and outcomes]({link}). Original integral records and neural checkpoints remain unchanged.\n"+end+"\n"
  p.write_text(s0)
 p=HERE/"README.md";text=p.read_text()
 start=text.index("## Current stage") if "## Current stage" in text else text.index("## Completed experiment");stop=text.index("## Procedure")
 text=text[:start]+"## Completed experiment\n\n"+block+"\n\n"+(
  "All 140 final validation workflows passed. The selected seed policy had a validation time ratio of 1.118283 to native Kira. freeze.json fixed its threshold, all weights, executables and scientific settings before reserved tests.\n\n"
  "scheduler_interruption.json records a scheduler address-space interruption. Its completed records were preserved, and missing workflows resumed with the same physical-memory, elapsed-time and scratch limits. This event is separate from measured workflow outcomes.\n\n"
  "summary.json and trials.csv contain every planned outcome. verification.json records independent exact polynomial checks. report_values.json maps report values to their evidence. model_test/plots/ contains the three PDF figures.\n\n")+text[stop:]
 p.write_text(text)
 p=ROOT/"ML_model_reduction/cost_training/README.md";text=p.read_text()
 text=text.replace("Repeated use in a changing matrix needs separate closed-loop testing.","The reserved experiment now tests repeated use in Kira's changing matrix; its complete-time and operation-count results are summarized below.")
 text=text.replace("Reserved tests use fixed weights and policies; complete-calculation claims will use those results.","Reserved testing used fixed weights and policies. Complete-calculation results and exact checks are in model_test/.")
 if marker in text:text=text.split(marker)[0]+text.split(end,1)[1]
 p.write_text(text.rstrip()+"\n\n"+marker+"\n## Reserved outcomes\n\n"+block+"\n"+end+"\n")
 for folder,title,base in [
  (ROOT/"ML_model_reduction/cost_training/model_test","Cost-trained row tests","../../../Kira_comparison/multiloop_native"),
  (ROOT/"ML_model_seed_selection/model_test/native_multiloop","Complete-generation seed tests","../../../Kira_comparison/multiloop_native")]:
  folder.mkdir(parents=True,exist_ok=True)
  (folder/"README.md").write_text("# "+title+"\n\n"+block+f"\n\nThe canonical [trial data]({base}/model_test/), [summary]({base}/summary.json), [plots]({base}/model_test/plots/) and [exact audit]({base}/verification.json) are stored once. This folder contains a small result index. Source choices remain restricted to rows with the same leading integral; the seed model uses its original fixed weights.\n")
  (folder/"results.json").write_text(json.dumps(dict(canonical_evidence=base,summary_sha256=hashlib.sha256((HERE/"summary.json").read_bytes()).hexdigest(),planned=s["planned"],completed=s["completed"],counts=s["counts"],comparisons=[c for c in s["comparisons"] if c["left"] in [seed,"row_full",f["combined_policy"]] and c["right"] in ["stock","native","tight"]],verification=v),indent=2)+"\n")


def write_conclusion(s,f):
 def c(left,right,size=None,metric="complete_seconds"):
  return next(v for v in s["comparisons"] if (v["left"],v["right"],v["size"],v["metric"])==(left,right,size,metric))
 def tc(topology,size):
  return next(v for v in s["topology_comparisons"] if v["topology"]==topology and v["size"]==size and v["left"]==f["seed_policy"] and v["right"]=="stock")
 seed=c(f["seed_policy"],"stock");row=c("row_full","native");ops=c("row_full","native",metric="operations")
 text="The complete-generation comparison adds physical two- and three-loop targets and includes fresh IBP generation in every measured workflow. "
 text+=f"Of {s['planned']} planned trials, {s['completed']} completed every target and matched its exact reference coefficients. "
 text+=f"The learned seed workflow has an aggregate complete-time ratio of {ratio(seed)} to responsive stock Kira. "
 if seed.get("interval95") and seed["interval95"][0]<=1<=seed["interval95"][1]:text+="The interval includes one, so the aggregate timing advantage remains uncertain across these cases. "
 for topology,label in [("double_box","two-loop box"),("vacuum3","three-loop vacuum"),("ladder3","three-loop ladder")]:
  x=tc(topology,None)
  if x.get("paired_batches"):text+=f"Its {label} ratio is {x['ratio']:.3f}. "
 for size in [32,128]:
  x=tc("double_box",size)
  if x.get("paired_batches"):
   direction="lower" if x["ratio"]<1 else "higher"
   text+=f"On the box cases with {size} targets, measured complete time is {abs(1-x['ratio'])*100:.1f}\\% {direction} than the stock control. "
 text+=r"These statements concern the fixed rational kinematics, prescribed master bases and paired completion rules of Section~\ref{sec:complete-multiloop}~\cite{KiraCompleteMultiloopData}."+"\n\n"
 text+="The separate row tree learns from measured native continuation costs in 98 exact training and validation reductions. "
 text+=f"When the model chooses sources repeatedly in the reserved matrices, its complete-time ratio to the instrumented native policy is {row.get('ratio',float('nan')):.3f}, and its forward coefficient-operation ratio is {ops.get('ratio',float('nan')):.3f}. "
 if row.get("ratio",1)>=1 and ops.get("ratio",1)>=1:
  text+="This policy increases both measured quantities in the paired aggregate. "
 elif row.get("ratio",1)>=1:
  text+="The lower operation count does not produce a lower complete time in the paired aggregate. "
 elif ops.get("ratio",1)>=1:
  text+="The point estimate of complete time is lower while the aggregate forward operation count is higher. "
 if row.get("interval95") and row["interval95"][0]<=1<=row["interval95"][1]:text+="The complete-time interval includes one, so a consistent row-policy timing gain is unresolved. "
 text+="The single-choice continuation objective and repeated use in changing matrices therefore require separate evaluation. "
 c128=s["counts_by_size"]["128"]
 text+=f"For 128 targets, the learned seed workflow completes {c128[f['seed_policy']]['completed']} of {c128[f['seed_policy']]['planned']} trials, including {c128[f['seed_policy']]['rescued_by_fallback']} completed through fallback. "
 text+="Batch splitting bounds individual reductions but repeats generation and startup, and its completion and timing results must be assessed together.\n\n"
 text+=r"The original collection through twelve loops varies mass profiles within restricted coupled vacuum families. The present native study extends the evidence to independent scalar-product bases at two and three loops, with the ladder topology absent from new row training and validation. General symbolic multiscale coefficients and unrestricted high-loop scattering families remain outside the demonstrated domain. The measured seed gains support use in the stated cases, while the row results identify the limits of the current cost-trained policy."+"\n"
 p=ROOT/"report/report.tex";old=p.read_text()
 begin="% native-multiloop-conclusion-begin";end="% native-multiloop-conclusion-end"
 if begin in old:start=old.index(begin);stop=old.index(end,start)+len(end)
 else:start=old.index("The higher-loop collection varies mass profiles within restricted");stop=old.index("\\clearpage",start)
 old=old[:start]+begin+"\n"+text+end+"\n\n"+old[stop:]
 p.write_text(old)

if __name__=="__main__":main()
