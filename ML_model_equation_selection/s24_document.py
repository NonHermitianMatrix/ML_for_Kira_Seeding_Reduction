"""Write measured results and folder documentation after all checks finish."""
import argparse,collections,hashlib,json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def read(p):return json.loads(p.read_text())
def write(p,s):p.write_text(s.strip()+"\n")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",default="main");args=ap.parse_args()
 summary=read(HERE/"model_test/summary.json");audit=read(HERE/"model_test/verification.json")
 app=read(HERE/"model_test/application_verification.json");comp=read(HERE/"model_test/composition.json")
 labels=read(HERE/"model_test/label_metrics.json");config=read(HERE/"trained_model/deployment.json")
 model=read(HERE/"trained_model/model.json")
 assert summary["all_exact"] and summary["workflows"]==280 and audit["all_passed"] and app["all_passed"] and comp["all_passed"]
 keys={k.split(":")[0]:k for k in summary["comparisons"]}
 measures={m:summary["comparisons"][k] for m,k in keys.items()}
 def fmt(z):
  return f'{z["ratio"]:.3f}, with descriptive interval $[{z["interval95"][0]:.3f},{z["interval95"][1]:.3f}]$'
 native=[b["methods"]["off:0"]["complete_seconds"] for b in summary["batches"]]
 cstats={}
 for base in ["row","both"]:
  groups=collections.defaultdict(lambda:collections.defaultdict(list))
  for r in comp["results"]:
   if r["base"]==base:groups[r["group"]][r["mode"]].append(r["complete_seconds"])
  cstats[base]=math.exp(statistics.mean(math.log(statistics.median(d["auto"])/statistics.median(d["off"])) for d in groups.values()))
 t=labels["totals"];precision=t["tp"]/(t["tp"]+t["fp"]);recall=t["tp"]/(t["tp"]+t["fn"]);brier=t["squared_error"]/t["rows"]
 routes=", ".join(f'{k.replace("_"," ")}: {v["mode"]}'+(f' at $\\tau={v["threshold"]:g}$' if v["mode"]=="learned" else "") for k,v in config["by_topology"].items())
 result=r"\subsection{Results and scope}"+"\n"
 result+=f'The validation route is {routes}. Other topologies use native equation choices. The forced learned filter uses $\\tau={config["threshold"]:g}$, while the distance filter retains seeds with $\\delta\\leq {config["distance_threshold"]:g}$. These choices remain fixed throughout the held-out tests.\n\n'
 result+=f'All 280 complete workflows reproduce their native reference coefficients. The independent audit checks {audit["coefficient_pairs"]:,} coefficient pairs, including {audit["distinct_coefficient_pairs"]:,} distinct expression pairs, by exact rational simplification in $d$. The workflows contain {audit["failed_attempts"]} failed filtered attempts before successful fallback, and their times include these attempts. Native median complete times range from {min(native):.3f} to {max(native):.3f} seconds across the fourteen batches.\n\n'
 for mode,label in [("learned","forced learned filter"),("distance","distance filter"),("auto","automatic route")]:
  z=measures[mode]
  result+=f'The {label} has a complete-time ratio of {fmt(z["complete_seconds"])}. Its equation-preparation ratio is {fmt(z["equation_preparation_seconds"])}. The generated-equation ratio is {z["generated_equations"]["ratio"]:.3f}, and the selected-equation ratio is {z["selected_equations"]["ratio"]:.3f}. All ratios use the matched native control, so a value below one indicates a lower measured cost.\n\n'
 z=measures["auto"]["complete_seconds"]
 if z["interval95"][1]<1:
  result+="The automatic route lowers the measured complete time, and its descriptive interval remains below one for these eight profiles. This result supports the stated physical domain and prescribed routing.\n\n"
 elif z["ratio"]<1:
  result+="The automatic route lowers the measured aggregate complete time, but its descriptive interval includes one. This sample does not establish a general complete-time gain.\n\n"
 else:
  result+="The automatic route does not lower the aggregate complete time in this test. Equation-count changes therefore do not establish an overall runtime gain.\n\n"
 result+=r"""\begin{figure}[htbp]
 \centering
 \includegraphics[width=\textwidth]{figures/equation_complete_times.pdf}
 \caption{Median complete-time ratios for the fourteen held-out batches.
 Each point uses five repetitions and includes checks and fallback.
 The dashed line is the native control.}
 \label{fig:equation-complete}
\end{figure}
\begin{figure}[htbp]
 \centering
 \includegraphics[width=\textwidth]{figures/equation_aggregate_costs.pdf}
 \caption{Profile-weighted geometric ratios of complete time, equation
 preparation time and generated-equation count. Bars show descriptive
 intervals from resampling the eight physical profiles.}
 \label{fig:equation-aggregate}
\end{figure}

"""
 result+=f'After freezing the model, we also collect {t["rows"]:,} held-out candidate labels, with {t["positives"]:,} positive labels. At the forced learned threshold, precision is {100*precision:.2f}\\% and recall is {100*recall:.2f}\\%, with mean squared probability error {brier:.4f}. These quantities measure agreement with the native support-membership proxy. Exact coefficient comparisons measure the validity of the resulting reductions.\n\n'
 result+=r"""\begin{figure}[htbp]
 \centering
 \includegraphics[width=.78\textwidth]{figures/equation_label_scores.pdf}
 \caption{Held-out model scores grouped by the native support-membership
 label. The vertical scale is linear near zero and logarithmic above ten
 equations. The labels describe selected supports rather than necessary
 equations.}
 \label{fig:equation-labels}
\end{figure}

"""
 result+=f'A further {comp["workflows"]} complete workflows test the equation route together with the existing row policy and with both existing policies on four profiles. Adding the equation route gives a complete-time ratio of {cstats["row"]:.3f} to the row-only configuration and {cstats["both"]:.3f} to the configuration with both earlier models. These comparisons use three repetitions and retain all fallback costs. All pass the reference checks. Eight application runs also pass exact coefficient comparisons after execution with reference coefficients withheld from the reducer.\n\n'
 result+="The early full-feature implementation and subsequent feature-sharing implementations remain in the evidence collection, including their slower results. The final comparison uses the frozen implementation selected before held-out testing. Its performance depends on target size, topology and the cost of generating and reducing the retained equations. The experiment covers physical two- and three-loop reductions at fixed rational kinematics with symbolic $d$; it does not establish gains on arbitrary higher-loop or fully multiscale problems~\\cite{KiraEquationSelectionData}.\n\\FloatBarrier\n"
 write(ROOT/"report/equation_selection_results.tex",result)
 conclusion=f'\n% BEGIN EQUATION CONCLUSION\nThe third model selects generated identities for the requested targets. Its\\nautomatic route has a complete-time ratio of {fmt(measures["auto"]["complete_seconds"])}.\\nIts equation-preparation ratio is {fmt(measures["auto"]["equation_preparation_seconds"])}.\\nAll 280 held-out workflows reproduce exact reference coefficients, and eight\\napplication checks pass with reference coefficients withheld from the reducer.\\nThe result applies to the recorded two- and three-loop profiles and the\\nvalidation-selected route~\\\\cite{{KiraEquationSelectionData}}.\\n% END EQUATION CONCLUSION\\n'.replace("\\n","\n").replace("\\\\cite","\\cite")
 p=ROOT/"report/report.tex";text=p.read_text()
 start=text.find("% BEGIN EQUATION CONCLUSION")
 if start>=0:
  end=text.index("% END EQUATION CONCLUSION",start)+len("% END EQUATION CONCLUSION")
  text=text[:start]+text[end:]
 text=text.replace("\\clearpage\n\\renewcommand{\\refname}",conclusion+"\n\\clearpage\n\\renewcommand{\\refname}")
 p.write_text(text)
 p=ROOT/"report/references.bib";bib=p.read_text();marker="@misc{KiraEquationSelectionData,"
 if marker in bib:bib=bib[:bib.index(marker)].rstrip()+"\n"
 bib+=f'\n@misc{{KiraEquationSelectionData,\n author = {{Saraswat, Rushil}},\n title = {{Target-dependent equation selection: native training, frozen tests and exact checks}},\n year = {{2026}},\n howpublished = {{GitHub repository}},\n url = {{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{args.data_commit}/ML_model_equation_selection}},\n note = {{Code, model, measurements and retained development results}}\n}}\n'
 p.write_text(bib)
 values=dict(measures=measures,composition_ratios=cstats,labels=dict(rows=t["rows"],positives=t["positives"],precision=precision,recall=recall,brier=brier),audit=audit,application=app,config=config,native_median_range=[min(native),max(native)])
 write(HERE/"report_values.json",json.dumps(values,indent=2))
 mainread=f"""# Target-dependent equation selection

This third System 1 model selects generated IBP and Lorentz-invariance identities for requested target integrals. Native Kira performs the exact reduction. The model complements the existing seed and row policies.

The trained CART tree has 233 nodes, maximum depth eight and 23 decision features. It uses 74,692 native training equations from six physical profiles. Its label records integral-support membership in the native final selected system. This is a conservative proxy; it does not identify an optimal or necessary set. Scores are smoothed leaf frequencies without a calibration claim.

Training, validation and testing use distinct physical profiles: six, three and eight respectively. The native performance domain is two- and three-loop integrals at fixed rational masses and invariants with symbolic dimension d. The test includes an unseen ladder topology. It does not inherit a claim of general twelve-loop runtime performance from the earlier constructed dataset.

The frozen deployment route gives complete-time ratio {measures["auto"]["complete_seconds"]["ratio"]:.4f} and equation-preparation ratio {measures["auto"]["equation_preparation_seconds"]["ratio"]:.4f} to native choices. See model_test/summary.json for descriptive intervals and every batch. All 280 main test workflows pass exact checks. Failed attempts and native fallbacks remain in the totals.

Folders:
- training/: native equation features, labels, reductions and training summary.
- validation/: final implementation threshold comparisons; earlier variants remain in named validation archives.
- trained_model/: model.json, compiled-evaluator weights.txt, deployment.json and the pre-test SHA-256 freeze.
- model_test/: all held-out workflows, exact audits, label scores, composition checks, basis-only applications and plots.
- integration/: numbered C++ policy headers, build records, patches and feature/probability parity checks.
- references/: additional native reference reductions; unchanged older references are linked by path in the records.
- development_v1/ and development_v2/: rejected label-collection attempts, retained with explanations. Training excludes them.

Use s11_reduce.py with a supported family description, prescribed master basis, target count, output path inside this folder, and --base native, seed, row or both. Reference target coefficients are not required. Automatic routing uses validation choices; --force-model is an explicit experimental override. Use the family definition, ordered target list and topology metadata schema in families.json. The --size argument selects the first entries from that target list. Deployment has been tested on the recorded topologies.

On the configured Hoffman installation, s25_build_lazy.sh builds the final policy from the recorded Kira source and existing acceleration objects. s04_experiment.py collects native training data, s06_train.py fits the tree, s12_freeze.py selects deployment from validation and locks the experiment, and s19_test.sh executes the frozen tests and exact audits. Earlier numbered build and validation scripts document development variants. Fresh experiments need a separate output directory and fresh held-out cases; do not overwrite the published freeze or evidence.

s23_plot.py generates plots, and s24_document.py writes report results and these summaries from checked measurements. s02_records.py writes bounded compressed evidence. s03_run.py enforces native memory, time and scratch limits. The resource plan permits one experiment trial at a time and keeps the combined project bound below 10 GB. Generated data and models stay on Hoffman and GitHub; only the report is synchronized to the laptop.
"""
 write(HERE/"README.md",mainread)
 docs={
 "training":"Native training reductions and per-equation features/labels. summary.json hashes each source record and records the six grouped profiles, 74,692 rows, 5,978 positive labels and training cost. Each compressed record contains the native reduction and tab-separated candidate records. Exclude failed records and all development archives when fitting.",
 "validation":"Final implementation comparisons on three held-out validation profiles and five target batches. Each grid point has three repetitions. summary.json retains complete timings, fallback costs and exact checks. trained_model/deployment.json uses only these results; the separate model_test set does not choose thresholds.",
 "trained_model":"model.json contains the 233-node CART tree and feature definitions. weights.txt stores the same tree for native C++ inference. deployment.json stores validation-selected thresholds and routes; freeze.json records SHA-256 hashes before the first test. Probabilities estimate the native support-membership label. They are not calibrated probabilities of sufficiency or optimality.",
 "model_test":"The main test comprises 280 frozen workflows across eight profiles and fourteen batches. summary.json gives paired medians and profile-weighted ratios; verification.json independently checks exact rational coefficients and frozen hashes. labels/ and label_metrics.json measure a support-membership proxy after freezing. composition/ and composition.json contain 48 checks with prior models. application/ and application_verification.json contain eight reductions without reference coefficients supplied to the reducer. plots/ contains PDFs and PNGs. All attempts, including failures followed by fallback, remain in the timing totals.",
 "integration":"Numbered headers preserve each integration version. s04_lazy_equation_policy.h is the final evaluator: shared seed features, compact seed/operator keys, cached omissions, and equation features evaluated on demand. Build JSON records contain source and binary hashes; binaries remain in the ignored cluster tools folder. fast_verification.json, cached_verification.json and lazy_verification.json check probabilities and decision features. Coefficient-string length is diagnostic only. Earlier failed parity evidence is explicitly archived.",
 "references":"Additional unfiltered native reductions supply benchmark reference coefficients. Records can also reference unchanged native results in Kira_comparison. These answers are used for benchmark checks, never as model inputs. The production application requires a prescribed master basis and receives no reference target coefficients.",
 "validation_full_features":"Earlier valid-label validation with a 24-feature decision tree, including coefficient-string length. This variant was rejected because equivalent coefficient spellings can change that feature. The archived trained_model preserves its model. Its complete and stage costs remain development evidence.",
 "validation_fast_features":"Complete 150-workflow development grid using the stable 23-feature tree and shared seed features. Its threshold results narrowed later validation; this is not the final implementation or held-out test.",
 "validation_compact":"Complete 105-workflow validation using compact keys and cached omissions. This preserves the intermediate implementation comparison before on-demand equation features.",
 "model_test/plots":"Scientific plots generated from checked model_test summaries by s23_plot.py. PDF files are also copied to report/figures. Complete times include prediction, algebra, exact checks and fallback. Intervals resample physical profiles."
 }
 for folder,body in docs.items():
  d=HERE/folder
  if d.exists():write(d/"README.md",body)
 for name in ["README.md","Kira_comparison/README.md"]:
  p=ROOT/name;s=p.read_text();marker="\n## Target-dependent equation selection\n"
  if marker in s:s=s[:s.index(marker)]
  target="ML_model_equation_selection" if name=="README.md" else "../ML_model_equation_selection"
  s+=marker+f"\nThe third native policy and its trained tree are in [{target}]({target}/README.md). The frozen test contains 280 complete reductions with exact checks, plus composition and basis-only application checks. The validation route has complete-time ratio {measures['auto']['complete_seconds']['ratio']:.4f} to native choices; its recorded interval and physical scope appear in the model README, test summaries and report. Earlier models and negative results remain available.\n"
  p.write_text(s)
 print(json.dumps(dict(written=True,complete_ratio=measures["auto"]["complete_seconds"],preparation_ratio=measures["auto"]["equation_preparation_seconds"],audit=audit),indent=2))
if __name__=="__main__":main()
