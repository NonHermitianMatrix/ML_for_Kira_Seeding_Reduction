"""Report the confirmation with identical admission checks for both selectors."""
import json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text())
s=read("expression_matched_summary.json");a=read("expression_matched_validation.json");f=read("expression_matched_freeze.json")
assert a["passed"] and a["trials"]==f["expected_trials"]==s["planned"]
policy=s["selected_policy"]
parts=[r"""\subsection{Using the same master check for both seed selectors}
The preceding distance control enters symbolic elimination directly,
while the learned method first checks the selected master basis.
To compare seed choices under the same admission procedure, we fixed
a second confirmation in which both selected sets receive the same
early check and full-pool fallback. The learned scores, threshold,
distance rule, twelve family instances and target batches stay
unchanged. The full-pool Kira control again uses its standard
supplied-equation reduction. We retained every measurement in the
first comparison.

Each method again uses five rotated repetitions on the same node
within a family and batch. This new comparison contains independent
timing repetitions of the same physical cases, so it checks the effect
of matching the admission procedure and does not introduce new
integral families. Complete times and descriptive intervals follow
the definitions in the preceding subsection.
"""]
parts.append(f'The comparison with the same early check contains {s["planned"]} records, of which {s["executed"]} are measured trials. It produced {s["exact"]} exact completions, {s["executed"]-s["exact"]} incomplete measured trials and {s["planned"]-s["executed"]} skipped repetitions. Independent checks evaluated {a["independent_master_sample_checks"]:,} target coefficients against the raw Kira exports. All completed reductions matched their exact reference coefficients.')
for name,label in [(policy,"The learned method"),("stored_pool","The full-pool control"),("stored_distance_checked","The distance control with the early check")]:
 t=s["totals"][name]
 parts.append(f'{label} completed {t["exact"]} trials exactly, with {t["failed"]} failed trials and {t["skipped"]} skipped repetitions. Its completed trials required fallback {t["completed_fallbacks"]} times.')
for c in s["comparisons"]:
 if c["numerator"]!=policy:continue
 control="the full-pool control" if c["denominator"]=="stored_pool" else "the distance control with the same early check"
 scope="Across both batch sizes" if c["size"] is None else f'For batches of {c["size"]} '+("target" if c["size"]==1 else "targets")
 if c["ratio"] is None:parts.append(scope+', no complete paired timing ratio is available against '+control+'.');continue
 lo,hi=c["interval95"]
 parts.append(scope+f', the learned complete-time ratio to {control} is {c["ratio"]:.3f}, with descriptive interval $[{lo:.3f},{hi:.3f}]$ across {c["paired_batches"]} paired batches. The control completed {len(c["control_only"])} additional batches, while the learned method completed {len(c["learned_only"])} additional batches.')
c=next(c for c in s["comparisons"] if c["numerator"]==policy and c["denominator"]=="stored_pool" and c["size"] is None)
dc=next(c for c in s["comparisons"] if c["numerator"]==policy and c["denominator"]=="stored_distance_checked" and c["size"] is None)
interpretation="The complete paired measurements do not establish an aggregate time reduction against the full-pool Kira control."
if c["ratio"] is not None and c["ratio"]<1:
 interpretation=f'The learned workflow has an observed {100*(1-c["ratio"]):.1f}\\% lower geometric mean complete time than the full-pool Kira control on batches where both methods completed all five repetitions.'
 if c["interval95"][1]>=1:
  interpretation+=' Because the descriptive interval includes one, the aggregate timing gain across both batch sizes remains uncertain.'
 if dc["ratio"] is not None and dc["ratio"]>=1:
  interpretation+=' The distance control is faster in the aggregate matched comparison, so the measured improvement over the full pool is also available from a deterministic seed-selection method.'
single=next(x for x in s["comparisons"] if x["numerator"]==policy and x["denominator"]=="stored_pool" and x["size"]==1)
single_distance=next(x for x in s["comparisons"] if x["numerator"]==policy and x["denominator"]=="stored_distance_checked" and x["size"]==1)
single_statement=(f'For the predefined single-target comparison, the learned method reduced geometric mean complete time by {100*(1-single["ratio"]):.1f}\\% relative to the full pool and by {100*(1-single_distance["ratio"]):.1f}\\% relative to the distance rule with the same early check. Both descriptive intervals lie below one, and every method completed all five repeats for all twelve instances. The first confirmation gave a 7.8\\% reduction relative to the full pool for this batch size. These results support a repeated gain for one constructed target expression at a time in this stored-identity setting. The sixteen-target intervals include one, so that batch size does not establish a consistent gain.')
assert single["interval95"][1]<1 and single_distance["interval95"][1]<1
assert single["paired_batches"]==single_distance["paired_batches"]==12 and not single["control_only"] and not single_distance["control_only"]
one=[x for x in s["cases"] if x["size"]==1]
pool_geomean=math.exp(statistics.mean(math.log(x["methods"]["stored_pool"]["median_seconds"]) for x in one))
model_geomean=math.exp(statistics.mean(math.log(x["methods"][policy]["median_seconds"]) for x in one))
single_statement+=f' The geometric means of the twelve per-family median complete times were {pool_geomean:.3f} seconds for the full pool and {model_geomean:.3f} seconds for the learned method.'
parts.append(single_statement)
parts.append(interpretation+' These conclusions concern reduction from the supplied identity pools and the tested constructed target expressions. Native equation generation, arbitrary scattering amplitudes and larger independent multiloop families remain outside this result '+r'\cite{KiraNativeAccelerationData}.')
parts.append(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/whole_expression_matched_times.pdf}
\caption{Complete-time ratios with the same early master check for
learned and distance-selected seeds. Points show geometric means
of five-repeat median ratios, intervals resample kinematic groups,
and $n$ gives the number of complete paired batches. The full-pool
control uses standard supplied-equation Kira reduction.}
\label{fig:whole-expression-matched}
\end{figure}
\FloatBarrier
""")
(ROOT/"report/kira_expression_matched.tex").write_text("\n\n".join(parts)+"\n")
p=ROOT/"report/kira_acceleration.tex";text=p.read_text()
if r"\input{kira_expression_matched}" not in text:text+="\n"+r"\input{kira_expression_matched}"+"\n"
p.write_text(text)
p=ROOT/"report/Makefile";text=p.read_text()
if "kira_expression_matched.tex" not in text:text=text.replace("kira_expression_results.tex","kira_expression_results.tex kira_expression_matched.tex")
p.write_text(text)
(HERE/"matched_report_values.json").write_text(json.dumps(dict(interpretation=interpretation,full_pool=c,distance=dc,single_target=single,single_distance=single_distance,single_target_statement=single_statement),indent=2)+"\n")
print(interpretation)
