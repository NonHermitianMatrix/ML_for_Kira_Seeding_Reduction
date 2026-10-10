"""Document the unchanged-choice shortcut and the usable basis-only interface."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def number(x):return f"{x:.3f}"
def interval(x):return "$["+number(x["descriptive_interval"][0])+","+number(x["descriptive_interval"][1])+"]$"
def evidence(x):
 lo,hi=x["descriptive_interval"]
 return "The descriptive interval lies below one." if hi<1 else "The descriptive interval lies above one." if lo>1 else "The descriptive interval includes one."
def main():
 initial=json.loads((HERE/"summary.json").read_text())
 s=json.loads((HERE/"pair_reserved_summary.json").read_text())
 v=json.loads((HERE/"pair_summary.json").read_text());cache=json.loads((HERE/"cache_summary.json").read_text())
 app=json.loads((HERE/"application_verification.json").read_text());audit=json.loads((HERE/"verification.json").read_text())
 assert [audit[k] for k in ["integrated_seed_attempts","used_selected_seeds","integrated_learned_attempts","learned_row_groups","changed_row_sources"]]==[404,147556,324,363759,5795]
 assert s["observed"]==400 and s["outcomes"].get("completed")==400 and app["all_passed"] and app["checks"]==8 and audit["all_passed"]
 def c(name,field="complete_seconds",kind=None):
  a=s["comparisons"][name][field]
  return a["all"] if kind is None else a["by_topology"][kind]
 text=r"""\clearpage
\subsection{Removing redundant features in two-row decisions}
The preceding comparison lowers the row-operation count while leaving the
cost of evaluating row choices visible in the forward stage. The recorded
training data contain 1,923 groups with two source candidates among 2,520
eligible groups. Their algebra supplies an additional way to reduce this cost.

Let $\boldsymbol u$ and $\boldsymbol v$ be two rows with the same leading
integral, and let $u_p$ and $v_p$ be their nonzero leading coefficients.
The two possible elimination updates satisfy
\[
 \boldsymbol v'=\boldsymbol v-\frac{v_p}{u_p}\boldsymbol u,
 \qquad
 \boldsymbol u'=\boldsymbol u-\frac{u_p}{v_p}\boldsymbol v
              =-\frac{u_p}{v_p}\boldsymbol v'.
\]
Their nonzero positions therefore agree. The estimated number of surviving
entries and its square also agree at the finite-field points where both
leading coefficients remain nonzero. For either retained linear score, these
shared terms cancel when we compare the two candidates. The remaining
score difference is
\[
 s(S,1)-s(S,0)=
 \lambda\log\frac{1+n_1}{1+n_0}-\eta,
\]
where $S$ is the current row group, $s(S,i)$ is the score of candidate $i$,
$n_i$ is its number of nonzero entries, and candidate zero is the native
source. The quantity $\lambda$ is the coefficient of source length and $\eta$ is the
coefficient of the native-source indicator. The two retained policies use
$(\lambda,\eta)=(2,0)$ and $(1/2,-0.01)$.

When this comparison selects source zero, the implementation retains that
source without constructing cancellation features. Unsupported modular
expressions already retain the native source, so the same decision also
holds in that case. Other decisions follow the full feature calculation.
The shortcut applies only to the stated sparse linear scores, and detailed
diagnostic traces retain the full calculation.

We compare the shortcut enabled and disabled in 144 complete validation
workflows. All seventy-two pairs agree on source-choice digests, operation
counts, attempt outcomes and exact exports. The enabled path bypasses
cancellation-feature construction in 42,702 row groups. The model-weighted
ratios of decision time, forward-stage time and complete time are
"""
 text+=f"{number(v['model_ratios']['decision_seconds'])}, {number(v['model_ratios']['forward_seconds'])} and {number(v['model_ratios']['complete_seconds'])}, respectively. These ratios compare the same learned policy with and without the shortcut; they describe a reduction in inference cost without changing its algebraic choices.\n"
 text+=f"\nA separate 4,096-entry cache for modular inverses also preserves all 144 validation reductions. Its forward-stage ratio is {number(cache['model_ratios']['forward_seconds'])}, its decision-time ratio is {number(cache['model_ratios']['decision_seconds'])}, and its complete-time ratio is {number(cache['model_ratios']['complete_seconds'])}. It fails the predefined forward-stage improvement criterion, so the retained implementation leaves this additional cache disabled. The original bounded cache of complete coefficient evaluations remains active.\n"
 text+=r"""
\subsection{Confirming the reduced inference cost}
We freeze the two-row shortcut after validation and run a second comparison
on the same eight previously reserved profiles. This confirmation preserves
the model weights, seed thresholds, physical inputs, reference bases and
routing rule. It does not supply eight additional independent families.
The smaller native control, deterministic cancellation control, seed model,
row model and combined policy each receive five repetitions on all sixteen
batches, giving 400 workflows.

Every model and control uses the same new executable and temporary-storage
settings. All 400 workflows complete and match their exact reference
coefficients. They use 460 attempts, including sixty failed subset attempts
whose time contributes to the completed workflows. Their selected seed masks, committed operations, row-group
counts and native exports also agree with the corresponding initial trials.
Figure~\ref{fig:integrated-pair-times} separates complete time from the
forward stage in this confirmation~\cite{KiraIntegratedRuntimeData}.
"""
 for label,k in [("seed model","seed_over_small"),("row model","row_over_small"),("combined policy","combined_over_small")]:
  x=c(k);y=c(k,"forward_seconds")
  text+=f"\nThe {label} has a complete-time ratio of {number(x['ratio'])} to the smaller native control, with interval {interval(x)}. {evidence(x)} Its forward-stage ratio is {number(y['ratio'])}, with interval {interval(y)}.\n"
 for kind,label in [("sunrise","two-loop sunrise"),("double_box","two-loop box"),("vacuum3","three-loop vacuum"),("ladder3","three-loop ladder")]:
  a=c("seed_over_small",kind=kind);b=c("row_over_small",kind=kind);d=c("row_over_small","forward_seconds",kind);e=c("combined_over_small",kind=kind)
  text+=f"\nFor the {label} profiles, the seed, row and combined complete-time ratios are {number(a['ratio'])}, {number(b['ratio'])} and {number(e['ratio'])}. The complete-time intervals are {interval(a)}, {interval(b)} and {interval(e)}, respectively. The row policy's forward-stage ratio is {number(d['ratio'])}, with interval {interval(d)}.\n"
 x=c("combined_over_seed");y=c("combined_over_seed","forward_seconds")
 text+=f"\nApplying the row policy within the learned-seed workflow gives a complete-time ratio of {number(x['ratio'])} to seed selection alone, with interval {interval(x)}. Its forward-stage ratio in that comparison is {number(y['ratio'])}, with interval {interval(y)}. These measurements include the model cost and the algebraic consequences of its choices.\n"
 x=c("row_over_fill_small")
 text+=f"\nThe row model's complete-time ratio to the deterministic cancellation rule is {number(x['ratio'])}, with interval {interval(x)}. The deterministic rule receives the same two-row shortcut, which keeps this comparison matched.\n"
 text+=r"""
The native integration audit verifies that every used seed belongs to the
selected mask and that each learned row attempt loads the frozen policy for
its physical class. It records 404 learned-seed attempts with 147,556 used
selected seeds, and 324 learned-row attempts with 363,759 eligible groups
and 5,795 changes from the native source. These counters show that the
models affect native equation generation and the evolving elimination.

The aggregate row-operation reduction therefore does not establish a reduction
in forward-stage time. The complete-time interval for the row policy includes
one, while always enabling seed selection or both models increases aggregate
complete time. The box cases support a conditional seed-model gain.
The automatic rule remains the rule fixed on validation; the confirmation
results do not retune it.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/integrated_pair_times.pdf}
\caption{The implementation confirmation compares the same frozen models with
the smaller native control after reducing two-row inference cost. The left
panel shows complete-time ratios and the right panel shows forward-stage
ratios. Each point uses five repeated complete reductions of the indicated
batch. The physical profiles repeat those in the initial comparison; all
algebraic choices and exact exports remain unchanged.}
\label{fig:integrated-pair-times}
\end{figure}

\clearpage
\subsection{Reducing new targets from a known master basis}
The reference answers above provide an independent benchmark check.
The production interface also accepts only the physical family, target
indices and prescribed master indices. It then determines the target
coefficients through native IBP generation and exact elimination.

To state this distinction mathematically, let $\boldsymbol I$ be the vector
of integrals in the generated system and let $A(d)$ be its IBP coefficient
matrix. The identities give $A(d)\boldsymbol I=0$. Native exact row operations
replace this system by $U(d)A(d)\boldsymbol I=0$, where $U(d)$ represents the
valid elementary row operations. Once elimination expresses all requested
targets through the prescribed masters, it gives
\[
 \boldsymbol I_{\mathcal T}=R_{\mathcal T}(d)\boldsymbol M.
\]
Here $\boldsymbol I_{\mathcal T}$ contains the requested targets,
$\boldsymbol M$ contains the supplied master integrals, and
$R_{\mathcal T}(d)$ is the rational coefficient matrix calculated by Kira.
The learned model chooses seeds and admissible source rows; the exact
identities and row operations determine this relation.

The controller checks that every target has a reduction and that every
integral on its right-hand side belongs to the supplied basis.
An additional integral triggers the fixed seed expansion. The interface
reports incompleteness if the allowed attempts fail. These checks establish
completion relative to the supplied basis under native exact IBP algebra.
They do not establish that an arbitrary supplied basis is globally minimal.
If reference coefficients are available, the interface can additionally
compare them exactly, and its records distinguish these two verification modes.

Eight application checks exercise native, seed, row, combined and automatic
execution on sunrise and box inputs. The reducer receives master indices
without target coefficients. After each run, a separate caller compares the
result with the retained exact reference, and all eight checks pass.
The application record includes input and routing time as well as the complete
reduction time. It excludes lossless evidence compression and optional common
release-integrity checks.

Automatic execution retains the routing rule fixed from validation. It enables
a learned method only in the tested feature classes where validation found
the required advantage, and uses native execution elsewhere. The individual
model modes remain available for controlled comparisons. The reported
model effects concern fixed rational kinematics, a known basis and symbolic
dimension $d$. Generic multiscale reconstruction, unrestricted higher-loop
families and global minimality remain outside this measured domain.
"""
 (ROOT/"report/kira_integrated_pair.tex").write_text(text)
 p=ROOT/"report/report.tex";main=p.read_text()
 if "\\input{kira_integrated_pair}" not in main:main=main.replace("\\section{Conclusion}","\\input{kira_integrated_pair}\n\n\\section{Conclusion}")
 seed=c("seed_over_small");row=c("row_over_small");both=c("combined_over_small");rf=c("row_over_small","forward_seconds");box=c("seed_over_small",kind="double_box");ops=c("row_over_small","operations")
 conclusion=r"""\section{Conclusion}
\label{sec:conclusion}
We integrated a compiled seed-selection network and a learned source-row
policy with native exact Kira reduction. """
 conclusion+=f"The initial 560 workflows and the 400-workflow implementation confirmation all match their exact reference coefficients. In the latter comparison, complete-time ratios to the smaller native control are {number(seed['ratio'])}, {number(row['ratio'])} and {number(both['ratio'])} for the seed, row and combined methods. The row policy's forward-stage ratio is {number(rf['ratio'])}, with descriptive interval {interval(rf)}, while its complete-time interval is {interval(row)}. These measurements include model loading, fresh IBP generation, exact algebra, checks and fallback~\\cite{{KiraIntegratedRuntimeData}}.\n"
 conclusion+=f"\nThe seed model's complete-time ratio on the two-loop box profiles is {number(box['ratio'])}, with interval {interval(box)}. The row policy gives an aggregate committed coefficient-operation ratio of {number(ops['ratio'])}. The physical-class results specify where the measured timing changes occur; the aggregate values retain slower cases. The automatic interface uses the routing rule fixed from validation and keeps native execution for other input classes.\n"
 native=initial["comparisons"]["small_over_native"]["complete_seconds"]["all"]
 conclusion+=f"\nShared execution changes also contribute to the calculation time. Dependency-ordered back substitution bounds helper-worker creation, and node temporary storage reduces the measured storage overhead. Both models and controls receive these changes. Starting from the smaller native region gives a complete-time ratio of {number(native['ratio'])} to the conservative region in the initial comparison. The two-row identity then lowers inference cost while preserving the learned source choices. A finite comparison of these strategies establishes measured costs on the stated inputs and does not prove a globally fastest reduction.\n"
 conclusion+=r"""
The data construction provides 17,100 family instances, 57,979 family-local
master entries and 2,301,272 targets with recorded identities and reduction
paths. These paths provide valid reference constructions and costs.
On 690,382 held-out targets, the seed model reaches 96.318\% $F_1$, and its
predicted stored equations supply complete master-span reductions for
94.515\% of targets. The full candidate pool supplies the remaining reductions.
These label and sufficiency measures require separate runtime tests; the
earlier cost comparisons and their negative results remain part of the
study~\cite{HigherLoopIntegralData,SeedModelTestData,KiraSeedSufficiencyData,KiraCostComparisonData}.

For production use, the interface needs a prescribed master basis and can
calculate target coefficients without their reference answers. Native exact
IBP operations determine the coefficients, and explicit output-basis admission
detects incomplete seed sets. Eight application checks pass independent
coefficient comparisons after execution with reference answers withheld
from the reducer. The report keeps this native algebraic assurance separate
from the additional reference comparisons used in the benchmark.

The original collection through twelve loops uses restricted coupled vacuum
families. The native performance comparisons cover physical two- and
three-loop inputs at fixed rational kinematics with symbolic $d$.
The ladder topology is absent from the new row-policy training and validation
sets. General multiscale coefficients, broader high-loop families and
globally minimal reduction paths remain outside the demonstrated scope.
"""
 a=main.index("\\section{Conclusion}");b=main.index("\\clearpage\n\\renewcommand{\\refname}",a)
 main=main[:a]+conclusion+"\n\n"+main[b:]
 abstract=main.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 p.write_text(main)
 p=ROOT/"report/kira_integrated_results.tex";x=p.read_text().replace("Independent tests of the integrated calculation","Initial independent tests of the integrated calculation").replace("The final comparison uses","The initial comparison uses").replace("Deployment and remaining limits","Interpretation of the initial comparison");p.write_text(x)
 p=ROOT/"report/Makefile";x=p.read_text()
 if "kira_integrated_pair.tex" not in x:x=x.replace("kira_integrated_results.tex","kira_integrated_results.tex kira_integrated_pair.tex")
 p.write_text(x)
 (HERE/"pair_report_values.json").write_text(json.dumps(dict(confirmation=s,validation=v,application=app,audit=audit),indent=2)+"\n")
 p=ROOT/"report/README.md";x=p.read_text();marker="<!-- two-row-confirmation -->"
 if marker in x:x=x[:x.index(marker)]
 x+="\n"+marker+"\nkira_integrated_pair.tex gives the two-row scalar-multiple identity, the 144-workflow parity and timing validation, and the 400-workflow confirmation on the same eight profiles. All source choices and exact results remain unchanged. figures/integrated_pair_times.pdf separates complete time from forward-stage time. The additional inverse cache remains disabled. Eight basis-only application checks pass independent postrun coefficient comparisons; production use can supply master indices without target answers. The revised conclusion reports the latest measured model effects and their limits. The original abstract remains unchanged.\n"
 p.write_text(x)
 print(json.dumps(dict(report_pair_written=True,seed=seed["ratio"],row=row["ratio"],row_forward=rf["ratio"],combined=both["ratio"])),flush=True)
if __name__=="__main__":main()
