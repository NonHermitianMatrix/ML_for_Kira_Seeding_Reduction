"""Finalize deployment documentation without changing either frozen experiment."""
import json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parent
def main():
 s=json.loads((HERE/"model_test/confirmation/summary.json").read_text())
 v=json.loads((HERE/"trained_model/deployment_verification.json").read_text());assert v["all_passed"]
 z=s["comparisons"]["learned:0.001"]
 fractions=[b["methods"]["off:0"]["equation_preparation_seconds"]/b["methods"]["off:0"]["complete_seconds"] for b in s["batches"]]
 times=[b["methods"]["off:0"]["complete_seconds"] for b in s["batches"]]
 share=math.exp(statistics.mean(math.log(x) for x in fractions))
 p=ROOT/"report/equation_selection_confirmation.tex";text=p.read_text()
 text=text.replace("The application interface uses this restricted route by default.","The application interface enables this equation policy when it runs with native seed and row choices. Requests for either earlier learned policy retain native equation choices. This guard avoids the slower measured three-model combination.")
 needle="\\begin{figure}[htbp]"
 text=text.replace(needle,f'Native median complete times range from {min(times):.3f} to {max(times):.3f} seconds in these six profiles. The geometric mean preparation fraction of native complete time is {100*share:.2f}\\%. This small fraction explains why the reduction in preparation time produces a smaller change in complete time. The main confirmation has zero failed attempts; all 54 failed attempts in its extended audit arise in the composition comparisons.\\n\\n'.replace("\\n","\n")+needle,1)
 p.write_text(text)
 p=ROOT/"report/equation_selection.tex";text=p.read_text().replace("Creation of the independent references","The experiment driver is already running when timing begins; Kira process startup and model loading are included. Creation of the independent references");p.write_text(text)
 p=ROOT/"report/report.tex";text=p.read_text();needle="% END EQUATION CONCLUSION";text=text.replace(needle,"The measured three-model composition is slower, with time ratio 1.317 to the earlier two-model configuration. The deployed interface therefore retains native equation choices when either earlier learned policy is active.\n"+needle,1);p.write_text(text)
 readme=f"""# Target-dependent equation selection

The current application is s35_reduce.py. It enables the trained equation model for the recorded 21-target two-loop sunrise domain with native seed and row choices. Other target sets, other topologies, and requests for the earlier seed/row models retain native equation choices. The slower three-model combination stays disabled.

On six fresh physical profiles, the equation policy has complete-time ratio {z['complete_seconds']['ratio']:.6f}, descriptive interval {z['complete_seconds']['interval95']}, and equation-preparation ratio {z['equation_preparation_seconds']['ratio']:.6f}, interval {z['equation_preparation_seconds']['interval95']}. This is about 0.6% lower complete time and 21.5% lower preparation time within that domain. Generated-equation ratio is {z['generated_equations']['ratio']:.6f}; selected-equation count is unchanged. Native median complete times range from {min(times):.3f} to {max(times):.3f} seconds. Preparation occupies about {100*share:.2f}% of native complete time.

The fresh main comparison has 162 workflows and no failed attempts. It fixes the model and route before testing six new mass/kinematic profiles, with nine alternating repetitions per method. A further 36 workflows compare all three models with the earlier two-model configuration. That composition is 31.7% slower and includes extra fallback. Six applications use prescribed masters without reference target coefficients. All 204 workflows pass the independent exact audit.

The earlier broad test has 280 complete workflows over eight two- and three-loop profiles, plus 48 composition workflows and eight applications. Its initial route is 9.8% slower overall because new vacuum filters require fallback. These results remain in model_test/. They motivated the restricted route before the fresh confirmation began. This work does not establish a general multiloop speedup.

The trained CART model has 233 nodes, maximum depth eight and 23 decision features. It uses 74,692 native training candidates, including 5,978 positive labels, from six physical profiles. A label records integral-support membership in the final native selected system. It is a conservative proxy rather than a necessity or optimality label. Probabilities are smoothed leaf frequencies without a calibration claim.

Native Kira constructs the identities and performs exact algebra. The integration shares seed features, evaluates equation features when the tree needs them, and caches decisions to skip rebuilding omitted equations. An incomplete reduction retries native equations and then a larger seed region. All attempts, model loading, generation, exact checks and cleanup enter the measured workflow time. The experiment driver is already running; independent-reference creation and evidence compression lie outside the timer.

Folders:

- training/: native features, labels, exact reductions and hashes.
- validation/: final threshold comparisons on three validation profiles; earlier validation variants remain in named archives.
- trained_model/: model.json, weights.txt, both experimental freezes, deployment_final.json and deployment_verification.json.
- model_test/: broad tests, labels, composition and application checks, plus confirmation/ for the fresh restricted-domain study.
- integration/: C++ headers, source patches, build hashes and probability/feature parity checks.
- references/: additional native reference reductions. Some unchanged references remain in Kira_comparison and are identified by path in each record.
- development_v1/ and development_v2/: rejected label-collection attempts, with explanations. Training excludes them.

Use s35_reduce.py inside a scheduled Hoffman job with node-local TMPDIR. Required arguments are --family-file, --masters-file, --size and --output. Use the family definition, ordered target list and topology metadata schema in families.json. The output must lie inside this folder. The optional --base accepts native, seed, row or both. The current interface prevents an equation-filter combination that the tests found slower.

On the configured cluster installation, s25_build_lazy.sh builds the final native evaluator. s04_experiment.py collects training examples, s06_train.py fits the tree, and s12_freeze.py locks the original broad experiment. s19_test.sh performs the broad tests. s30_confirmation.py prepare defines and freezes the six fresh profiles; s32_confirm.sh runs their comparison and independent audit. These completed experiments must remain fixed; use separate folders and fresh profiles for further policy development.

s36_check_deployment.py verifies that the deployed choices match measured successful arms and disable unsupported combinations. s39_finish_report.sh generates plots, documentation and the report from checked measurements. s38_plot.py preserves the original plotting logic with compatibility for the installed Matplotlib version; the originally frozen s23_plot.py remains unchanged. s31_reduce.py and s11_reduce.py preserve preceding experimental interfaces.

The resource plan permits one experiment trial at a time and bounds the complete project below 10 GB. Generated models, data and tests stay on Hoffman and GitHub. The complete report is also synchronized to the laptop.
"""
 (HERE/"README.md").write_text(readme)
 p=HERE/"trained_model/README.md";text=p.read_text()+"\nCurrent use: s35_reduce.py reads deployment_final.json. deployment_verification.json checks agreement with measured successful arms. The equation model stays off when an earlier seed or row model is requested, because the measured composition was slower. Both original freezes and preceding configurations remain unchanged.\n";p.write_text(text)
 for name in ["README.md","Kira_comparison/README.md"]:
  p=ROOT/name;text=p.read_text();marker="\n## Target-dependent equation selection\n";text=text[:text.index(marker)] if marker in text else text
  link="ML_model_equation_selection" if name=="README.md" else "../ML_model_equation_selection"
  text+=marker+f"\nThe trained third model and native integration are in [{link}]({link}/README.md). The current s35_reduce.py route uses the recorded 21-target two-loop sunrise domain with native seed and row choices. Six fresh profiles give complete-time ratio {z['complete_seconds']['ratio']:.4f} and preparation ratio {z['equation_preparation_seconds']['ratio']:.4f}. Other domains and combinations with earlier learned policies retain native equation choices. The report preserves the slower broad and combined results, descriptive intervals, exact checks and current limits.\n";p.write_text(text)
 (HERE/"trained_model/deployment_report_values.json").write_text(json.dumps(dict(complete=z["complete_seconds"],preparation=z["equation_preparation_seconds"],native_time_range=[min(times),max(times)],native_preparation_fraction=share,guarded_compositions=True),indent=2)+"\n")
 print(json.dumps(dict(native_preparation_fraction=share,complete=z["complete_seconds"],preparation=z["equation_preparation_seconds"]),indent=2))
if __name__=="__main__":main()
