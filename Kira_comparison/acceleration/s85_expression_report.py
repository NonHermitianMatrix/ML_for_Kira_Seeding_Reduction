"""Describe measured whole-expression reductions in the report."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text())
d=read("expression_summary.json")
out=[r"""\subsection{Applying the seed model to complete target expressions}
The native interface reduces each component of
Eq.~\eqref{eq:accel-expression} before combining the result. We also
applied the fast seed model directly to that complete expression,
using Kira's supplied-equation mode. This tests the form of the target
used to train the seed model and allows cancellations between its
components during the reduction.

Let $\mathcal E_{\boldsymbol b}$ be the stored IBP identities generated
from candidate seed $\boldsymbol b$, and let
$\mathcal E_{\rm bg}$ contain the stored symmetry and other background
identities. The selected equation set is
\begin{equation}
 \mathcal E(\mathcal S)=\mathcal E_{\rm bg}\cup
       \bigcup_{\boldsymbol b\in\mathcal S}\mathcal E_{\boldsymbol b}.
\end{equation}
For each requested expression, we add its defining relation
\begin{equation}
 \mathcal T_\nu-
 \sum_{\boldsymbol a\in\mathcal J_\nu}
 c_{\nu\boldsymbol a}I_{\boldsymbol a}=0.
\end{equation}
Kira eliminates the supplied system with the target expressions ordered
above their component integrals and the prescribed masters preferred
at the end of the ordering. It therefore obtains the master expansion
of $\mathcal T_\nu$ in one exact solve. The same public identity pool,
target definitions and master basis enter every compared method.

The model takes the union of candidates whose score reaches
$\tau=0.01$, using the unchanged weights and the fast inference
implementation. We tested this set both with and without an early
finite-field master check. An incomplete selected system triggers a
full-pool calculation within the remaining time allowance. The early
check compares the remaining integrals with the prescribed master
basis; exact final coefficient checks still determine whether the requested reductions
agree with their recorded answers. A global master check can require
more relations than a particular target combination needs.

These calculations begin with stored IBP identities, whose prior
generation cost is excluded for every method. The measured complete
time includes loading those inputs, prediction, equation selection and
export, Kira's exact calculation, admission checks when used, failed
attempts, fallback and final verification. Thus the result concerns
repeated reduction from a common identity pool. It does not measure
native generation of a new family's equations.
"""]
out.append(f'The separate development and adapter-validation collection contains {d["planned"]} trials, with {d["exact"]} exact completions and {d["planned"]-d["exact"]} incomplete calculations. Independent checks evaluated {d["independent_checks"]:,} target coefficients at stored finite-field points. The six adapter-validation family instances belong to the original training partition and use two batch sizes, one and sixteen targets. We retained every measured cost and selected a learned interface only when its geometric mean complete-time ratio to the full-pool control was below one and it preserved every control completion.')
for c in d["validation_comparisons"]:
 desc="with the early master check" if c["policy"].endswith("_checked") else "without the early master check"
 value="unavailable" if c["ratio"] is None else f'{c["ratio"]:.3f}'
 out.append(f'The validation ratio {desc} was {value} across {len(c["pairs"])} complete paired batches. The full-pool control completed {len(c["control_only"])} additional batches that this learned interface did not complete. These single validation measurements select the interface and do not establish a repeatable timing gain.')
if (HERE/"expression_test_summary.json").exists():
 s=read("expression_test_summary.json");a=read("expression_test_validation.json");f=read("expression_freeze.json")
 assert a["passed"] and a["trials"]==f["expected_trials"]==s["planned"]
 policy=s["selected_policy"];checked=policy.endswith("_checked")
 out.append(r"\subsection{Reserved tests of complete-expression reduction}")
 out.append('Validation selected '+('the early master check' if checked else 'direct symbolic elimination without the early master check')+'. We froze this choice before applying it to the twelve original-held-out box instances used in the native comparison. The network weights and threshold remain fixed. Each instance supplies batches of one and sixteen target expressions, with five rotated repetitions per method on the same node. These are reused physical families and constructed targets; the new comparison tests the revised interface on original-held-out model data.')
 out.append('The controls use the full stored identity pool and a fixed set of 64 seeds ranked by their smallest index distance to any target component. The distance control uses the same exact reduction and full-pool fallback as the learned method. This first distance control proceeds directly to symbolic elimination, while the selected learned method uses the early master check. Their time ratio therefore includes both seed selection and the difference in admission checks.')
 out.append(f'The frozen plan contains {s["planned"]} records. We executed {s["executed"]} trials and obtained {s["exact"]} exact completions; {s["executed"]-s["exact"]} measured trials failed to complete within the bounds, and {s["planned"]-s["executed"]} remaining repeats were skipped after an earlier failure. Every completed master expansion matched its exact reference, and the independent audit checked {a["independent_master_sample_checks"]:,} target coefficients directly against the exported Kira reductions. Skipped repetitions have no assigned runtime.')
 for method,label in [(policy,"The learned interface"),("stored_pool","The full-pool control"),("stored_distance","The distance control")]:
  t=s["totals"][method]
  out.append(f'{label} produced {t["exact"]} exact completions, {t["failed"]} failed trial{"s" if t["failed"] != 1 else ""} and {t["skipped"]} skipped repeats. Completed trials used fallback {t["completed_fallbacks"]} times.')
 out.append(r'We form a median from five successful repetitions for each method and batch, and take geometric mean ratios over complete paired batches. Descriptive 95\% intervals resample the six kinematic groups 10,000 times, preserving the relationship between profiles and batch sizes. Completion losses remain separate from these ratios.')
 for c in s["comparisons"]:
  if c["numerator"]=="stored_distance" or c["size"] is not None:continue
  label="full-pool control" if c["denominator"]=="stored_pool" else "distance control"
  if c["ratio"] is None:out.append(f'No batch completed all five repeats for both the learned interface and the {label}.');continue
  lo,hi=c["interval95"]
  out.append(f'The learned interface has a complete-time ratio of {c["ratio"]:.3f} against the {label}, with descriptive interval $[{lo:.3f},{hi:.3f}]$ across {c["paired_batches"]} paired batches. The control completed all repeats in {len(c["control_only"])} additional batches, and the learned method completed all repeats in {len(c["learned_only"])} additional batches.')
 c=next(c for c in s["comparisons"] if c["numerator"]==policy and c["denominator"]=="stored_pool" and c["size"] is None)
 if c["ratio"] is not None and c["ratio"]<1:
  statement=f'The observed geometric mean complete time is {100*(1-c["ratio"]):.1f}\\% lower than the full-pool Kira control on batches where both methods completed all five repetitions.'
  if c["interval95"][1]>=1:
   statement+=' Because the descriptive interval includes one, the aggregate timing gain across both batch sizes remains uncertain.'
 else:statement='The complete paired comparisons do not show an aggregate time reduction against the full-pool Kira control.'
 out.append(statement+' The result applies to these constructed target expressions and their existing identity pools; it does not establish a speedup for general multiloop amplitude reductions '+r'\cite{KiraNativeAccelerationData}.')
 out.append(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/whole_expression_times.pdf}
\caption{Complete-time ratios for direct reduction of complete target
expressions. Points show geometric means of five-repeat median ratios,
and intervals resample kinematic groups. The label $n$ gives the
number of complete paired batches. Failed and skipped trials remain
in the completion counts.}
\label{fig:whole-expression-time}
\end{figure}
\FloatBarrier
""")
else:
 out.append('No learned interface met the stated validation condition, so this stage supplies no reserved confirmation of a faster whole-expression policy '+r'\cite{KiraNativeAccelerationData}.')
(ROOT/"report/kira_expression_results.tex").write_text("\n\n".join(out)+"\n")
p=ROOT/"report/kira_acceleration.tex";text=p.read_text()
if r"\input{kira_expression_results}" not in text:text += "\n"+r"\input{kira_expression_results}"+"\n"
p.write_text(text)
p=ROOT/"report/Makefile";text=p.read_text()
if "kira_expression_results.tex" not in text:text=text.replace("kira_transfer_results.tex","kira_transfer_results.tex kira_expression_results.tex")
p.write_text(text)
print("Whole-expression report section updated")
