"""Document the restricted deployment and independent confirmation."""
import json,pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/"model_test/confirmation"
def main():
 s=json.loads((OUT/"summary.json").read_text());a=json.loads((OUT/"verification.json").read_text());c=json.loads((OUT/"composition_summary.json").read_text())
 assert s["all_exact"] and a["all_passed"] and a["workflows"]==204 and c["all_exact"]
 z=s["comparisons"]["learned:0.001"];d=s["comparisons"]["distance:4"];joint=c["comparisons"]
 def fmt(v):return f'{v["ratio"]:.3f}, with descriptive interval $[{v["interval95"][0]:.3f},{v["interval95"][1]:.3f}]$'
 plot=OUT/"plots";plot.mkdir(exist_ok=True)
 plt.rcParams.update({"font.size":9,"pdf.fonttype":42})
 fig,axes=plt.subplots(1,2,figsize=(9,3.2));x=np.arange(6)
 for ax,field,label in zip(axes,["complete_seconds","equation_preparation_seconds"],["Complete reduction","Equation preparation"]):
  for key,name,marker in [("learned:0.001","Learned filter","o"),("distance:4","Distance filter","s")]:
   vals=[b["methods"][key][field]/b["methods"]["off:0"][field] for b in s["batches"]]
   ax.plot(x,vals,marker=marker,label=name,lw=1.1,ms=4)
  ax.axhline(1,color="black",lw=.8,ls="--");ax.set_xticks(x);ax.set_xticklabels([f"{i:02d}" for i in range(6)])
  ax.set_xlabel("Fresh sunrise profile");ax.set_ylabel("Median ratio to native choices");ax.set_title(label);ax.grid(axis="y",alpha=.2)
 axes[0].legend(frameon=False);fig.tight_layout()
 fig.savefig(plot/"confirmed_costs.pdf");fig.savefig(plot/"confirmed_costs.png",dpi=140);plt.close(fig)
 (ROOT/"report/figures/equation_confirmed_costs.pdf").write_bytes((plot/"confirmed_costs.pdf").read_bytes())
 text=r"""\clearpage
\subsection{Restricted deployment and fresh confirmation}
The broad test exposes incomplete equation filters in the new vacuum
profiles. Their native fallback retains exact results and adds cost.
We therefore fix a restricted deployment using the same trained tree.
It enables the equation filter at $\tau=0.001$ for the recorded
21-target sunrise batches and retains native equation choices for
other topologies and target sets. The broader test supplies development
evidence for this deployment revision.

Each supported batch contains the top-sector scalar integral and its
one-dot and one-numerator variants, together with the corresponding
integrals in the three two-propagator sectors. This gives 21 targets
whose index vectors are fixed in the deployment definition.
We reserve six additional mass and momentum profiles before running
their reductions. None of these profiles occurs in the preceding
training, validation or broad-test sets. Their squared masses and
external invariant are fixed rational numbers, while $d$ remains symbolic.
The tree, threshold, target domain and new profile definitions are
fixed before this confirmation begins.

Nine alternating repetitions compare the learned filter, native choices
and the previously selected distance control in each profile. These
162 complete workflows use the same timing and exact-check rules
as the preceding test, including every failed attempt.
"""
 text+=f'\nThe learned filter has a complete-time ratio of {fmt(z["complete_seconds"])} and an equation-preparation ratio of {fmt(z["equation_preparation_seconds"])}. Its generated-equation ratio is {z["generated_equations"]["ratio"]:.3f}, and its selected-equation ratio is {z["selected_equations"]["ratio"]:.3f}. The distance control has a complete-time ratio of {fmt(d["complete_seconds"])}.\n\n'
 if z["complete_seconds"]["interval95"][1]<1:
  text+="The complete-time interval remains below one for these six profiles, supporting a measured gain within the restricted domain.\n\n"
 elif z["complete_seconds"]["ratio"]<1:
  text+="The aggregate complete time is lower, and its descriptive interval includes one. The complete-time gain remains uncertain at this sample size.\n\n"
 else:text+="The aggregate complete time does not improve in this confirmation. The component and complete times therefore require separate interpretation.\n\n"
 text+=f'A further 36 workflows compare the existing seed and row policies with the configuration that also includes the equation filter. Adding the third model gives a complete-time ratio of {fmt(joint["complete_seconds"])} and a preparation ratio of {fmt(joint["equation_preparation_seconds"])} to the two-model configuration. This comparison uses three repetitions in each of the six profiles.\n\n'
 text+=f'All 162 main workflows, 36 composition workflows and six basis-only applications pass the independent exact audit, which checks {a["coefficient_pairs"]:,} coefficient pairs. The {a["workflows"]} workflows include {a["failed_attempts"]} failed attempts. The six applications receive the prescribed masters without reference target coefficients, and their outputs pass coefficient comparisons after execution.\n\n'
 text+=r"""\begin{figure}[htbp]
 \centering
 \includegraphics[width=\textwidth]{figures/equation_confirmed_costs.pdf}
 \caption{Fresh confirmation of the restricted sunrise deployment.
 Each profile uses nine repetitions for each method. Complete and
 preparation times include prediction and fallback costs.}
 \label{fig:equation-confirmed}
\end{figure}
The application interface uses this restricted route by default.
The broader initial route and its slower vacuum results remain available
as experimental evidence. The measured domain contains two-loop sunrise
integrals with the stated target set, and extension to other target sets
or topologies requires further independent evidence~\cite{KiraEquationSelectionData}.
\FloatBarrier
"""
 (ROOT/"report/equation_selection_confirmation.tex").write_text(text)
 p=ROOT/"report/equation_selection.tex";v=p.read_text()
 if "\\input{equation_selection_confirmation}" not in v:v+="\n\\input{equation_selection_confirmation}\n"
 p.write_text(v)
 p=ROOT/"report/Makefile";v=p.read_text().replace("equation_selection_domain.tex references.bib","equation_selection_domain.tex equation_selection_confirmation.tex references.bib");p.write_text(v)
 conclusion="\n% BEGIN EQUATION CONCLUSION\n"+f'The third model selects generated identities for the requested targets.\\nThe broad test found that incomplete vacuum filters added fallback cost.\\nA restricted route was then fixed and tested on six fresh sunrise profiles.\\nIt gives a complete-time ratio of {fmt(z["complete_seconds"])}\\nand an equation-preparation ratio of {fmt(z["equation_preparation_seconds"])}.\\nAll 162 confirmation comparisons, 36 checks with the two earlier models\\nand six applications pass exact coefficient checks. The deployed equation\\npolicy uses the recorded 21-target sunrise domain and retains native\\nchoices elsewhere~\\\\cite{{KiraEquationSelectionData}}.\\n'.replace("\\n","\n").replace("\\\\cite","\\cite")+"% END EQUATION CONCLUSION\n"
 p=ROOT/"report/report.tex";v=p.read_text();start=v.index("% BEGIN EQUATION CONCLUSION");end=v.index("% END EQUATION CONCLUSION",start)+len("% END EQUATION CONCLUSION");v=v[:start]+conclusion+v[end:];p.write_text(v)
 info=f"""
The current application entry point is s31_reduce.py, with trained_model/deployment_confirmed.json. It applies the third model only to the recorded 21-target two-loop sunrise domain and uses native equation choices elsewhere. Run it inside a scheduled Hoffman job with node-local TMPDIR; the same family/master/output arguments and --base choices as s11_reduce.py apply. s11_reduce.py and deployment.json preserve the broader initial experimental route.

The broad 280-workflow test found incomplete vacuum filters and extra fallback cost. These negative results remain in model_test/. The narrower policy was fixed before testing six fresh profiles. In model_test/confirmation/, 162 main comparisons give complete-time ratio {z["complete_seconds"]["ratio"]:.4f}, interval {z["complete_seconds"]["interval95"]}, and preparation ratio {z["equation_preparation_seconds"]["ratio"]:.4f}, interval {z["equation_preparation_seconds"]["interval95"]}. All exact checks pass. A further 36 workflows compare all three models with the earlier two-model configuration; six applications omit reference target coefficients.

s30_confirmation.py defines and freezes the new profiles before execution and performs independent rational checks. s32_confirm.sh runs that study, and s33_confirm_document.py creates its plots and report section. The original frozen test files remain unchanged. The confirmation studies a restricted physical domain and does not establish a general multiloop speedup.
"""
 p=HERE/"README.md";v=p.read_text();heading="# Target-dependent equation selection\n";v=v.replace(heading,heading+"\n"+info.strip()+"\n\n",1)
 v=v.replace("The frozen deployment route gives complete-time ratio","The initial experimental route gives complete-time ratio")
 v=v.replace("Use s11_reduce.py with","The initial experimental interface s11_reduce.py accepts")
 p.write_text(v)
 (OUT/"README.md").write_text(info.strip()+"\n")
 (HERE/"trained_model/README.md").write_text((HERE/"trained_model/README.md").read_text()+"\nThe current restricted route is deployment_confirmed.json, frozen by confirmation_freeze.json before six fresh profiles were reduced. deployment.json remains the original broad-test route. Both use the same tree and weights.\n")
 for name in ["README.md","Kira_comparison/README.md"]:
  p=ROOT/name;v=p.read_text();marker="\n## Target-dependent equation selection\n"
  if marker in v:v=v[:v.index(marker)]
  link="ML_model_equation_selection" if name=="README.md" else "../ML_model_equation_selection"
  v+=marker+f"\nThe third model, native integration and results are in [{link}]({link}/README.md). Its current route uses the recorded 21-target two-loop sunrise domain, with complete-time ratio {z['complete_seconds']['ratio']:.4f} and preparation ratio {z['equation_preparation_seconds']['ratio']:.4f} on six fresh profiles. The report includes the descriptive intervals, exact checks, composition results and earlier slower vacuum outcomes. Other target domains retain native equation choices.\n"
  p.write_text(v)
 dirs={
 "model_test/labels":"Held-out native support labels from the initial broad test. These labels did not fit or calibrate the saved tree.",
 "model_test/composition":"Initial broad-route composition checks with row-only and combined seed/row policies. All fallback costs remain in each record.",
 "model_test/application":"Initial basis-only applications. Reference target coefficients were withheld from the reducer and checked after it returned.",
 "model_test/confirmation/composition":"Fresh-profile checks of the two earlier models with and without the restricted equation filter, with three repetitions per method.",
 "model_test/confirmation/application":"Six applications in the confirmed target domain with prescribed masters and no reference target coefficients supplied to the reducer.",
 "model_test/confirmation/plots":"Paired complete/preparation cost plots for the six fresh confirmation profiles; generated from summary.json by s33_confirm_document.py."
 }
 for name,body in dirs.items():(HERE/name/"README.md").write_text(body+"\n")
 (OUT/"report_values.json").write_text(json.dumps(dict(learned=z,distance=d,composition=joint,audit=a),indent=2)+"\n")
 print(json.dumps(dict(learned=z,composition=joint,audit=a),indent=2))
if __name__=="__main__":main()
