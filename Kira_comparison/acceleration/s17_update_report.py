"""Write checked native-acceleration results into the report."""
import argparse,hashlib,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);args=ap.parse_args()
assert re.fullmatch(r"[0-9a-f]{40}",args.data_commit)
def read(name):return json.loads((HERE/name).read_text())
s=read("summary.json");a=read("results_validation.json");f=read("frozen_policy.json");e=read("cpp_equivalence.json")
assert a["passed"] and e["passed"] and a["trials"]==s["planned_records"]==f["expected_trials"]
seed=f["selected_seed_policy"];policies=[seed,"row_cpp","combined"]
names={seed:"the learned seed filter","row_cpp":"the compiled row policy","combined":"the combined method",
       "trim":"restricted native Kira","tight":"the target-bound control","pool_filter":"the full candidate-pool control"}
def c(p,b="trim",m="total_seconds"):
 return next(x for x in s["comparisons"] if (x["numerator"],x["denominator"],x["metric"])==(p,b,m))
def ratio(x):
 if x["ratio"] is None:return "no complete paired batches"
 lo,hi=x["interval95"]
 return f'{x["ratio"]:.3f} (descriptive 95\\% interval {lo:.3f}--{hi:.3f}; {x["batches"]} batches)'
def num(x):return format(x,",")
def st(p):
 t=s["totals"][p]
 return f'{num(t["exact_successes"])} exact completions, {num(t["failed_attempts"])} failed trials and {num(t["skipped"])} skipped repetitions'
out=[r"\subsection{Reserved results and exact checks}",r"\label{sec:acceleration-results}"]
out.append(f'The frozen comparison contains {s["planned_records"]} planned records across twelve family instances, two target-batch sizes, six methods and five repetitions. We executed {s["executed_trials"]} trials and obtained {s["exact_successes"]} exact completions; the remaining {s["executed_trials"]-s["exact_successes"]} executed trials exceeded a resource limit or failed to complete. The early-stop rule left {s["skipped_repetitions"]} repetitions unexecuted. These skipped records contain no timing measurement. The retained inputs, policy choices, successful reductions and failure records accompany the data release~\\cite{{KiraNativeAccelerationData}}.')
selected=(r'the complete target expression with threshold $\tau=0.01$' if seed=="ml_lower"
          else r'individual components with threshold $\tau=0.5$ and the neighbourhood in Eq.~\eqref{eq:seed-neighbours}')
out.append('Validation selected '+selected+'. This configuration and both trained checkpoints remained fixed during the reserved tests. Each method used the same master basis and targets in a batch.')
out.append('For the three controls, '+names["trim"]+' produced '+st("trim")+', '+names["tight"]+' produced '+st("tight")+', and '+names["pool_filter"]+' produced '+st("pool_filter")+'. These counts describe the bounded experiment and do not measure whether an unlimited calculation would complete.')
low,high=s["totals"]["trim"]["observed_successful_time_range"]
if low is not None:
 out.append(f'Successful restricted-native trials took {low:.2f}--{high:.2f} seconds for the complete checked calculation. This range includes different family instances, target-batch sizes and CPU models. The paired ratios compare methods on the same node within each batch.')
out.append('For the learned methods, '+names[seed]+' produced '+st(seed)+', '+names["row_cpp"]+' produced '+st("row_cpp")+', and '+names["combined"]+' produced '+st("combined")+'. Completed seed and combined trials used the standard fallback '+str(s["totals"][seed]["completed_fallbacks"])+' and '+str(s["totals"]["combined"]["completed_fallbacks"])+' times, respectively.')
out.append('Every completed final expression matched its recorded rational master coefficients. The independent audit performed '+num(a["independent_master_sample_checks"])+' additional master-coefficient sample checks and '+num(a["row_sample_checks"])+' exact-row sample checks. It checked '+num(a["compiled_model_choices"])+' compiled model choices and '+num(a["compiled_forced_actions"])+' forced source actions. Trace checks cover completed native attempts; '+str(a["unaudited_failed_attempt_traces"])+' failed attempts had incomplete traces. The final coefficient checks still apply to any successful fallback. Input and checkpoint hashes agree with the values frozen before testing.')
out.append(r"\subsection{Complete reduction time and algebraic work}")
out.append(r'For each family and batch size, we take the median of five successful repetitions. We then form the ratio of learned time to control time and report the geometric mean across complete paired batches. A ratio below one means a lower measured time. We resample complete kinematic groups 10,000 times to obtain descriptive 95\% intervals, keeping related profiles and batch sizes together. These intervals describe the completed subset of this small collection; failed and skipped trials remain in the completion counts above.')
for p in policies:
 x=c(p);native=c(p,m="native_with_inference_seconds")
 out.append('Restricted native Kira completed all five repetitions in '+str(len(x["control_only_batches"]))+' batches where '+names[p]+' did not, while '+names[p]+' completed all five repetitions in '+str(len(x["learned_only_batches"]))+' batches where that control did not.')

 out.append(names[p].capitalize()+' has a complete-time ratio of '+ratio(x)+' against restricted native Kira. Its native-calculation subtotal, including seed prediction when used, has ratio '+ratio(native)+'. The subtotal excludes input preparation, final target combination and verification, which remain included in the complete time.')
out.append('Against the target-bound control, complete-time ratios are '+', '.join(ratio(c(p,"tight")) for p in policies)+', in seed, row and combined order. Against the full candidate-pool control, the corresponding ratios are '+', '.join(ratio(c(p,"pool_filter")) for p in policies)+'. Each ratio uses its own complete paired cohort, so comparisons with different failure patterns can contain different batches.')
out.append(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/native_acceleration_times.pdf}
\caption{Learned-to-control time ratios in the reserved native comparison.
The upper panel includes the complete checked reduction, and the lower panel
shows the native subprocess subtotal plus seed prediction. Points show
geometric mean ratios and lines show descriptive intervals obtained by
resampling kinematic groups. The label $n$ gives the number of paired
batches with five successful repeats for both methods.}
\label{fig:native-acceleration-time}
\end{figure}""")
for p in policies:
 out.append(names[p].capitalize()+' has a generated-equation ratio of '+ratio(c(p,m="generated_equations"))+', a selected-equation ratio of '+ratio(c(p,m="selected_equations"))+' and a forward-update ratio of '+ratio(c(p,m="forward_updates"))+' against restricted native Kira. These are counters from the native reduction passes, including completed fallback passes.')
out.append('Generation counters count equations reported in successive generation passes and can include repeated equations. A forward update is one committed elimination step; this count does not measure every polynomial or rational-function operation. Failed attempts can have truncated work counters, so the complete time and completion status remain the primary measures.')
out.append(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/native_acceleration_work.pdf}
\caption{Generated-equation and forward-update ratios on complete paired
batches. The controls and cohort labels follow
Fig.~\ref{fig:native-acceleration-time}. These counters measure reported
generation work and committed updates, while symbolic coefficient
complexity can change the cost of each update.}
\label{fig:native-acceleration-work}
\end{figure}
\FloatBarrier""")
out.append(r"\subsection{Numerical inference and scope of the result}")
out.append('The compiled-model development audit checked '+num(e["candidate_feature_vectors"])+' action feature vectors and '+num(e["independent_coefficient_samples"])+' sampled coefficients. The maximum feature difference was '+format(e["max_feature_error"],".3g")+', and the largest probability difference from the independent double-precision calculation was $'+format(e["max_probability_error"],".3g").replace("e-",r"\times10^{-")+(r"}$" if "e-" in format(e["max_probability_error"],".3g") else "$")+'. All selected sources agreed with the original single-precision model in these development trials. The separate maximum probability difference from that original arithmetic was $'+format(e["max_original_float32_probability_difference"],".3g").replace("e-",r"\times10^{-")+(r"}$" if "e-" in format(e["max_original_float32_probability_difference"],".3g") else "$")+'.')
out.append('The largest sampled process-tree memory was '+f'{s["peak_rss_bytes"]/1e9:.3f}'+' GB, and the largest trial scratch directory was '+f'{s["peak_scratch_bytes"]/1e6:.2f}'+' MB. The bounded runs kept their scientific records and model files on Hoffman; the report contains the derived plots and results.')
strong=[p for p in policies if c(p)["ratio"] is not None and c(p)["interval95"][1]<1 and not c(p)["control_only_batches"]]
mixed=[p for p in policies if c(p)["ratio"] is not None and c(p)["ratio"]<1]
if strong:
 interpretation='The completed paired comparisons support a time reduction against restricted native Kira for '+', '.join(names[p] for p in strong)+'. The control comparisons and failed-case counts define the extent of that result.'
elif mixed:
 interpretation='Some complete paired geometric mean times are below the restricted native baseline. Intervals that include one or losses of completed batches limit the evidence for a consistent gain over the full tested set.'
else:
 interpretation='The complete paired comparisons do not show a lower aggregate runtime than restricted native Kira for these learned methods. Lower inference costs alone do not ensure that the chosen seeds and rows save enough algebraic work.'
out.append(interpretation+' The new native tests cover one-loop boxes and do not establish performance on independent high-loop scattering families. The existing weights were trained to recover recorded seed sets and row choices, so further cost-oriented training on native Kira trajectories remains a separate experiment.')
(ROOT/"report/kira_acceleration_results.tex").write_text("\n\n".join(out)+"\n")
p=ROOT/"report/references.bib";text=p.read_text()
entry=r"""@misc{KiraNativeAccelerationData,
 author = {Saraswat, Rushil},
 title = {Learned Seed Selection and Row Choices in Exact {Kira} Reductions},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/COMMIT/Kira_comparison/acceleration}{Frozen policies, native and supplied-equation comparisons, and exact checks}}
}
""".replace("COMMIT",args.data_commit)
if "@misc{KiraNativeAccelerationData," in text:text=re.sub(r"@misc\{KiraNativeAccelerationData,.*?\n\}",lambda _:entry.rstrip(),text,flags=re.S)
else:text+="\n"+entry
p.write_text(text)
transfer=read("transfer_summary.json");expr=read("expression_test_summary.json");matched=read("expression_matched_summary.json")
matched_values=read("matched_report_values.json")
mc=next(x for x in matched["comparisons"] if x["numerator"]==matched["selected_policy"] and x["denominator"]=="stored_pool" and x["size"] is None)
md=next(x for x in matched["comparisons"] if x["numerator"]==matched["selected_policy"] and x["denominator"]=="stored_distance_checked" and x["size"] is None)
def cratio(x):
 return "unavailable" if x["ratio"] is None else f'{x["ratio"]:.3f}'
extra=('The separate two-loop transfer gave 60 exact completions. The compiled learned-row pipeline reduced the median complete time for 64 targets from 12.770 to 12.460 seconds, a 2.4\\% decrease. Its advantage over the deterministic compiled source control remained unresolved, and the full-pool control was faster at 11.773 seconds. This limited native-baseline gain does not establish a general benefit from learned row choices.'+'\n\n'+
'Direct reduction of complete target expressions provides a different use of the seed model. The first confirmation contains '+str(expr["planned"])+' planned records and '+str(expr["exact"])+' exact completions. A second comparison applies the same early master check to learned and distance-selected seeds and contains '+str(matched["planned"])+' planned records and '+str(matched["exact"])+' exact completions. In this matched comparison, complete-time ratios are '+cratio(mc)+' against the full supplied-equation pool and '+cratio(md)+' against the fixed distance control. '+matched_values["interpretation"]+' '+matched_values["single_target_statement"]+' Prior generation of the common identity pool is outside these measurements '+r'\cite{KiraNativeAccelerationData}.'+'\n\n')
p=ROOT/"report/report.tex";text=p.read_text().replace("The tested implementations increased aggregate runtime,","The earlier implementations increased aggregate runtime,")
begin=text.find("The new native integration filters individual IBP seeds",text.index("\\section{Conclusion}"))
if begin<0:begin=text.index("The higher-loop collection varies mass profiles")
end=text.index("\\clearpage",begin)
paragraph=('The new native integration filters individual IBP seeds and evaluates the source-row network inside Kira. Its complete-time ratios against restricted native Kira are '+', '.join(f'{c(p)["ratio"]:.3f}' if c(p)["ratio"] is not None else 'unavailable' for p in policies)+', in seed, row and combined order. These ratios use '+', '.join(str(c(p)["batches"]) for p in policies)+' complete paired batches, respectively, with five repetitions per method. '+interpretation+r' All '+str(s["exact_successes"])+r' completed trials matched their exact master coefficients~\cite{KiraNativeAccelerationData}.'+'\n\n'+
extra+
'The higher-loop collection varies mass profiles within restricted\ncoupled vacuum families, and all tested loop orders occur in training.\nThe earlier native comparisons cover seven independent-basis families\nat one and two loops, while the new reserved comparison covers\ntwelve one-loop box instances in six kinematic groups. These results\nsupport conclusions within the tested domains, resource limits and\naction sets. Larger independent multiloop systems and cost-oriented\ntraining on their changing IBP matrices remain necessary to assess\nbroader performance.\n\n')
text=text[:begin]+paragraph+text[end:];p.write_text(text)
abstract=text.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
values=dict(data_commit=args.data_commit,summary_sha256=hashlib.sha256((HERE/"summary.json").read_bytes()).hexdigest(),
 audit_sha256=hashlib.sha256((HERE/"results_validation.json").read_bytes()).hexdigest(),
 planned=s["planned_records"],executed=s["executed_trials"],completed=s["exact_successes"],skipped=s["skipped_repetitions"],
 conclusion=interpretation,primary_comparisons=[c(p) for p in policies],
 whole_expression_summary_sha256=hashlib.sha256((HERE/"expression_test_summary.json").read_bytes()).hexdigest(),
 matched_summary_sha256=hashlib.sha256((HERE/"expression_matched_summary.json").read_bytes()).hexdigest(),
 matched_comparisons=[mc,md],matched_interpretation=matched_values["interpretation"],single_target=matched_values["single_target"])
(HERE/"report_values.json").write_text(json.dumps(values,indent=2)+"\n")
print(json.dumps(values,indent=2))
