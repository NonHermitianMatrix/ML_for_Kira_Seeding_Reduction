"""Write the scientific report from frozen exact-test summaries."""
import argparse,hashlib,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def num(x):return f"{x:.3f}"
def interval(x):return "$["+num(x["descriptive_interval"][0])+","+num(x["descriptive_interval"][1])+"]$"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);a=ap.parse_args();assert re.fullmatch("[0-9a-f]{40}",a.data_commit)
 summary=json.loads((HERE/"summary.json").read_text());audit=json.loads((HERE/"verification.json").read_text());assert audit["all_passed"]
 C=summary["comparisons"]
 def comp(k,field="complete_seconds",topology=None):
  return C[k][field]["all"] if topology is None else C[k][field]["by_topology"][topology]
 text=r"""\subsection{Independent tests of the integrated calculation}
The final comparison uses eight physical profiles that did not select the
weights, thresholds or execution rules. Two two-loop sunrise profiles have
squared masses $(1,2,2)$ and $(1,2,4)$, with external invariant $p^2=-5$ and
$p^2=-7$, respectively. Two massless double-box profiles have
$(s,t)=(-11,-13)$ and $(-13,-17)$. The three-loop vacuum profiles have squared
masses $(1,1,1,1,1,3)$ and $(1,1,1,3,3,3)$. The three-loop ladder profiles have
one squared mass equal to one, all other physical propagator masses equal
to zero, and $p^2=-3$ or $-5$. All values use the common arbitrary mass unit
and denominator conventions of Section~\ref{sec:complete-multiloop}.
The dimension $d$ remains symbolic. The ladder topology remains absent
from the new row-policy training and validation data.

Each sunrise profile supplies its ordinary twenty-one-target batch and
a deeper thirty-two-target batch. Each other profile supplies batches of
thirty-two and 128 targets. We compare seven methods on these sixteen
batches: the conservative native region, the smaller native region,
the deterministic cancellation rule, deterministic seed coverage, the
seed model, the row model and both models together.
Five repetitions per method give 560 planned workflows. We rotate and
reverse method order within each physical profile. All methods use the
same prescribed master basis, exact coefficient checks, temporary storage
and single-worker schedule~\cite{KiraIntegratedRuntimeData}.

The validation-selected row score emphasizes source length for the boxes
and uses the mixed score for the sunrise and vacuum cases. The transfer
test also uses the mixed score for the ladder topology. Seed thresholds
come from the training classes; an unseen class uses the predefined
threshold $0.01$. The complete comparison executes the model ablations
even where validation recommends native execution, so an unfavorable model
cost remains visible in the results.

The recorded time begins with per-workflow preparation and ends after
the final exact check and cleanup. It includes model import, weight loading,
feature construction, prediction, every native generation and elimination
attempt, and every fallback. Python interpreter launch, the common reference
calculation, shared integrity checks and result compression remain outside
this interval. Every candidate model and control uses the same timing
boundary.

For each batch and method, we take the median of five repetitions.
We then form paired ratios, average their logarithms within each physical
profile and give the eight profiles equal weight. The descriptive intervals
resample whole physical profiles while retaining their two batches.
A topology-specific interval therefore contains only two independent profiles.
Repeated timings measure execution variation; they do not create additional
independent integral families.
"""
 text+=f"\nThe comparison records {summary['observed']} workflows, of which {summary['outcomes'].get('completed',0)} complete every target with the prescribed coefficients. It retains all {summary['attempts']} native attempts, including unsuccessful seed subsets. The independent audit reparses native exports and checks rational coefficients by exact polynomial cross multiplication in $\\mathbb Q(d)$. Across the full development and test record, it reparses {audit['native_successes']:,} successful native reductions and checks {audit['coefficient_comparisons']:,} coefficient comparisons. The separately retained development basis rejection remains a failed attempt and supplies no accepted reduction.\n"
 text+=r"""
\subsection{Measured model effects against matched native choices}
Figure~\ref{fig:integrated-runtime-times} compares each model with the smaller
native control. This control receives the same runtime improvements and
starts from the same target bounds. The comparison therefore tests whether
the learned decisions save enough work to cover their own cost.
"""
 for name,k in [("seed policy","seed_over_small"),("row policy","row_over_small"),("combined policy","combined_over_small")]:
  x=comp(k);change="decrease" if x["ratio"]<1 else "increase"
  text+=f"\nThe {name} has a complete-time ratio of {num(x['ratio'])}, with descriptive interval {interval(x)}, relative to the smaller native control. Its point estimate corresponds to a {100*abs(1-x['ratio']):.1f}\\% {change} in the profile-weighted complete time.\n"
 text+=r"""
These aggregate values combine inputs with different equation-generation and
elimination costs. The separate physical classes show where a model contributes
a measured saving and where its additional attempt or decision cost dominates.
"""
 for topology,label in [("sunrise","two-loop sunrise"),("double_box","two-loop double-box"),("vacuum3","three-loop vacuum"),("ladder3","three-loop ladder")]:
  x=comp("seed_over_small",topology=topology);y=comp("row_over_small",topology=topology);z=comp("combined_over_small",topology=topology)
  text+=f"\nFor the {label} profiles, the seed, row and combined complete-time ratios are {num(x['ratio'])}, {num(y['ratio'])} and {num(z['ratio'])}, respectively. Their descriptive intervals are {interval(x)}, {interval(y)} and {interval(z)}. These values average the two tested batches within each of the two physical profiles.\n"
 text+=r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/integrated_runtime_times.pdf}
\caption{Median complete time for the frozen seed, row and combined policies,
divided by the smaller native control's median time on the same target batch.
Every point uses five repeated workflows with fixed physical input and master
basis. Values below one indicate lower complete time. The preceding text
states the timing boundary and profile-weighted intervals.}
\label{fig:integrated-runtime-times}
\end{figure}

\subsection{Elimination work and the contribution of each model}
A lower total runtime can come from seed generation, elimination or shared
execution changes. We therefore also inspect committed forward operations
and compare the combined method directly with the seed-only method.
"""
 for label,k in [("row policy relative to native choices","row_over_small"),("combined policy relative to the seed-only method","combined_over_seed")]:
  x=comp(k,"operations");y=comp(k,"forward_seconds");z=comp(k)
  text+=f"\nThe {label} gives an operation ratio of {num(x['ratio'])}, a forward-stage time ratio of {num(y['ratio'])}, and a complete-time ratio of {num(z['ratio'])}. The operation count measures the stated coefficient-update proxy. It excludes Fermat's internal polynomial operations, while the two timing measures include the corresponding arithmetic within their stage boundaries.\n"
 x=comp("seed_over_closure");y=comp("row_over_fill_small")
 text+=f"\nThe seed model's complete-time ratio to deterministic coverage is {num(x['ratio'])}, with interval {interval(x)}. The row model's ratio to the deterministic cancellation rule is {num(y['ratio'])}, with interval {interval(y)}. Both deterministic controls receive the same feature and runtime optimizations.\n"
 x=comp("small_over_native");y=comp("combined_over_native")
 text+=f"\nStarting from the smaller native region gives a complete-time ratio of {num(x['ratio'])} to the conservative native region. The combined model gives a ratio of {num(y['ratio'])} to that conservative control. The former comparison changes the initial native region without a learned decision. It therefore identifies a shared source of improvement that must be separated from the models' contributions.\n"
 text+=r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/integrated_runtime_operations.pdf}
\caption{Committed forward coefficient-operation ratios for the seed model
against native choices, the row model against native choices, and the
combined policy against seed selection alone. The last comparison isolates
the additional row policy within the selected seed workflow. These counts
describe the recorded update proxy and do not count internal polynomial work.}
\label{fig:integrated-runtime-operations}
\end{figure}

\subsection{Deployment and remaining limits}
The integrated entry point applies the settings fixed from validation.
It can run either model separately, run both models, or select the
validation-recommended method from the topology and target powers.
Automatic selection requires at least a two-percent validation improvement
over the smaller native control; otherwise it retains that control.
Unknown input classes also retain native execution. This rule avoids
paying for models on inputs where development did not support their use.
The reserved ablations above evaluate the fixed choices; reserved timings
do not change their weights or the deployment rule.

The basis check and exact coefficient comparison remain active under every
mode. Incomplete seed sets expand through the fixed fallback, and a
coefficient disagreement in the admitted basis stops the workflow.
The test uses exact rational functions of $d$ at fixed rational masses and
kinematics, with the master basis supplied in advance. Its measured times
exclude discovering and certifying a new generic symbolic basis.

The new row policies learn from complete native trajectories and act inside
Kira's changing matrix. Their allowed action is the source equation among
rows with the same leading integral. They do not choose arbitrary columns,
sectors or all mathematically possible reductions. The finite policy search,
limited physical profiles and descriptive intervals bound the conclusion:
the report establishes the measured changes on the stated inputs, while
a general gain for both models and a globally fastest reduction require
evidence beyond these comparisons.
"""
 (ROOT/"report/kira_integrated_results.tex").write_text(text)
 p=ROOT/"report/report.tex";main=p.read_text()
 abstract=main.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 if "\\input{kira_integrated_methods}" not in main:main=main.replace("\\section{Conclusion}","\\input{kira_integrated_methods}\n\\input{kira_integrated_results}\n\n\\section{Conclusion}")
 seed=comp("seed_over_small");row=comp("row_over_small");both=comp("combined_over_small")
 conclusion=(r"The final integrated comparison uses 560 frozen workflows on eight new two- and three-loop physical profiles. "
  f"The seed, row and combined complete-time ratios to the smaller native control are {num(seed['ratio'])}, {num(row['ratio'])} and {num(both['ratio'])}, respectively. "
  r"These comparisons include model loading, native equation generation, exact reduction, checks and fallback. "
  r"Shared improvements in back substitution, temporary storage and initial region size also benefit the native control. "
  r"The model effects and their physical-class dependence therefore require the separate comparisons in Section~\ref{sec:integrated-runtime}. "
  r"The integrated code preserves exact coefficient checks and retains native execution where validation provides no sufficient timing advantage. "
  r"The measured best configurations apply to the stated domain and do not establish a globally fastest calculation~\cite{KiraIntegratedRuntimeData}.")
 begin="% integrated-runtime-conclusion-begin";end="% integrated-runtime-conclusion-end"
 if begin in main:main=main[:main.index(begin)]+main[main.index(end)+len(end):]
 main=main.replace("\\clearpage\n\\renewcommand{\\refname}",begin+"\n"+conclusion+"\n"+end+"\n\n\\clearpage\n\\renewcommand{\\refname}")
 p.write_text(main)
 p=ROOT/"report/Makefile";s=p.read_text()
 if "kira_integrated_methods.tex" not in s:s=s.replace("references.bib $(wildcard","kira_integrated_methods.tex kira_integrated_results.tex references.bib $(wildcard")
 p.write_text(s)
 p=ROOT/"report/references.bib";s=p.read_text();begin="% integrated-runtime-data-begin";end="% integrated-runtime-data-end"
 if begin in s:s=s[:s.index(begin)]+s[s.index(end)+len(end):]
 s+=("\n"+begin+"\n"+r"""@misc{KiraIntegratedRuntimeData,
 author = {Saraswat, Rushil},
 title = {Integrated Learned Seed Inference and Native Row Policies with Complete Multiloop Cost Tests},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"""+a.data_commit+r"""/Kira_comparison/integrated_runtime}{Frozen methods, complete workflows, retained failures and independent exact checks}}
}
"""+end+"\n")
 p.write_text(s)
 values=dict(data_commit=a.data_commit,summary_sha256=hashlib.sha256((HERE/"summary.json").read_bytes()).hexdigest(),verification=audit,comparisons=C,observed=summary["observed"],outcomes=summary["outcomes"])
 (HERE/"report_values.json").write_text(json.dumps(values,indent=2)+"\n")
 p=ROOT/"report/README.md";s=p.read_text();marker="<!-- integrated-native-runtime -->"
 if marker in s:s=s[:s.index(marker)]
 s+=f"\n{marker}\nThe latest extension is in kira_integrated_methods.tex and kira_integrated_results.tex. It documents compiled unchanged seed inference, threshold fitting on complete native cost, sparse row features, trajectory-selected policies, bounded back substitution, model-free controls and explicit exported-basis admission. The frozen comparison contains {summary['observed']} workflows in sixteen batches from eight new physical profiles. The new figures are integrated_runtime_times.pdf and integrated_runtime_operations.pdf. Data, models and exact checks are fixed at {a.data_commit}. All earlier results and the exact supplied abstract remain preserved. The reported native baseline receives the same shared runtime improvements as the learned policies.\n"
 p.write_text(s)
 print(json.dumps(dict(report_written=True,seed_ratio=seed["ratio"],row_ratio=row["ratio"],combined_ratio=both["ratio"])),flush=True)
if __name__=="__main__":main()
