"""Render the completed fixed-policy two-loop transfer comparison."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=json.loads((HERE/"transfer_summary.json").read_text())
audit=json.loads((HERE/"transfer_test_validation.json").read_text())
assert audit["passed"] and audit["trials"]==60
def mathnum(n):return "$"+format(n,".3f")+"$"
parts=[r"""\subsection{Transfer to a two-loop propagator family}
We also applied the unchanged interfaces to the massless two-loop
propagator family used in the earlier cost comparisons. Its five
independent family indices fit the compiled row interface. We fixed
two batches of 16 and 64 stored target expressions and all policies
before this transfer calculation. Each method uses five rotated
repetitions, the same master basis and the same time and memory limits.
Storage-interrupted trials resume on their original node, with earlier
observations preserved. Because this family appeared in earlier
comparisons, this experiment measures transfer of the revised
implementation and does not establish generalization to a newly unseen
family.

Alongside native seeding and the full candidate pool, we include a
deterministic source-row control using the same compiled reduction
structure. This control selects a source by row length and integral ordering
within the same changing leading-column group. Comparing the learned row policy
with this control separates the source choice from changes to the
compiled reduction structure. Every completed reduction receives the
same exact coefficient check and an independent finite-field check.
"""]
parts.append(f"The transfer experiment contains {s['executed']} measured trials among "
 f"{s['planned']} planned records, with {s['exact_successes']} exact completions. "
 f"The independent audit performed {audit['independent_master_sample_checks']:,} "
 f"target-coefficient checks and {audit['row_sample_checks']:,} row-update checks.\n")
names={"ml_lower":"learned seed filter","row_cpp":"learned source-row policy","combined":"combined policy"}
for case in s["cases"]:
 m=case["methods"];base=m["trim"]["median_seconds"]
 if base is None:
  parts.append(f"For the batch of {case['size']} targets, the native control did not complete all five repetitions. "
   "We therefore report completion status without a complete-time ratio for that control.\n")
  continue
 paragraph=f"For {case['size']} targets, the native control's median complete time was {mathnum(base)} seconds. "
 observations=[]
 for mode in ("ml_lower","row_cpp","combined"):
  c=next(x for x in case["comparisons"] if x["learned"]==mode and x["control"]=="trim")
  if c["complete_pair"]:
   lo,hi=c["descriptive_interval"]
   observations.append(f"the {names[mode]} gave a time ratio of {mathnum(c['ratio'])} "
    +"with descriptive interval $["+f"{lo:.3f},{hi:.3f}"+"]$")
  else:observations.append(f"the {names[mode]} completed {m[mode]['successes']} of five repetitions")
 paragraph+="; ".join(observations).capitalize()+". "
 extra=[]
 for mode,control,label in [("ml_lower","pool_filter","learned seed filter relative to the full pool"),
                            ("row_cpp","row_cpp_native","learned source choice relative to the deterministic compiled control")]:
  c=next(x for x in case["comparisons"] if x["learned"]==mode and x["control"]==control)
  if c["complete_pair"]:
   lo,hi=c["descriptive_interval"]
   extra.append(f"the {label} had ratio {mathnum(c['ratio'])} with interval $[{lo:.3f},{hi:.3f}]$")
 if extra:paragraph+="In the matched controls, "+" and ".join(extra)+"."
 parts.append(paragraph+"\n")
parts.append(r"""
The compiled learned-row pipeline reduced the median complete time for
64 targets from 12.770 to 12.460 seconds, a measured reduction of
2.4\%. Its ratio against the deterministic compiled control has an
interval that includes one, so this experiment does not resolve a
benefit caused by the learned source choice itself. The full-pool
control was faster, at 11.773 seconds. For 16 targets, the combined
pipeline reduced the native median by 2.4\%, but the full-pool control
again completed sooner. For 64 targets, every learned-seed and combined
trial required fallback, whose cost is included in the reported time.
These observations establish limited gains relative to the stated
native baseline and also identify stronger deterministic controls.
""")
parts.append(r"""
Figure~\ref{fig:native-transfer} shows all complete paired comparisons.
A ratio below one denotes a lower median complete time. The intervals
come from 10,000 paired resamples of the five repetitions and describe
repeat-to-repeat variation within this one family. They do not measure
uncertainty across different integral families. Incomplete pairs remain
in the completion counts and receive no timing ratio
\cite{KiraNativeAccelerationData}.

\begin{figure}[htbp]
 \centering
 \includegraphics[width=\textwidth]{figures/native_transfer_times.pdf}
 \caption{Complete-time ratios in the two-loop transfer comparison for
 16 targets (upper panel) and 64 targets (lower panel). Points show
 ratios of five-repeat medians, and bars show descriptive paired-repeat
 intervals. All times include prediction, target preparation, exact
 reduction, combination, checks and any required fallback.}
 \label{fig:native-transfer}
\end{figure}
""")
(ROOT/"report/kira_transfer_results.tex").write_text("\n".join(parts))
p=ROOT/"report/kira_acceleration.tex";text=p.read_text()
if r"\input{kira_transfer_results}" not in text:text=text.replace(r"\input{kira_acceleration_results}",r"\input{kira_acceleration_results}"+"\n"+r"\input{kira_transfer_results}")
p.write_text(text)
print(json.dumps(dict(report="kira_transfer_results.tex",exact_completions=s["exact_successes"])))
