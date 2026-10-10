"""Write the mathematical changes and measured complete costs from verified data."""
import argparse,hashlib,json,math,pathlib,re,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=ROOT/"Kira_comparison/parallel_inference"
def num(x):return f"{x:.3f}"
def interval(d):return "$["+num(d["descriptive_interval"][0])+","+num(d["descriptive_interval"][1])+"]$"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);a=ap.parse_args();assert re.fullmatch("[0-9a-f]{40}",a.data_commit)
 d=json.loads((EXP/"confirmation_summary.json").read_text());audit=json.loads((EXP/"verification.json").read_text());app=json.loads((EXP/"application_verification.json").read_text())
 seed=json.loads((EXP/"seed_parity.json").read_text());row=json.loads((EXP/"arithmetic_check.json").read_text())
 assert d["observed"]==d["planned"]==640 and d["all_exact_and_choice_parity"] and audit["all_passed"] and app["all_passed"]
 seed_ratio=math.exp(statistics.mean(math.log(r["new_seconds"]/r["old_seconds"]) for r in seed["results"]))
 def ratio(key,field="complete_seconds"):return d["comparisons"][key][field]["all"]
 text=r"""\clearpage
\section{Parallel seed evaluation and exact modular inverses}
\label{sec:parallel-inference}
The shared calculations in the preceding section reduce repeated work, but the
remaining model evaluation still contributes to the reduction time. We now
evaluate independent outputs of the seed network together and use a different
exact algorithm for modular division in the row features. We also reduce\nrepeated coefficient parsing and storage allocation. The weights,
thresholds, seed rules and source-row policy remain fixed, so this comparison
measures the cost of calculating the same decisions.

\subsection{Evaluating independent neural outputs together}
Let $W\in\mathbb R^{n\times m}$ be a layer's weight matrix,
$\boldsymbol x\in\mathbb R^m$ its input and $\boldsymbol b\in\mathbb R^n$
its bias. Here $m$ is the number of input components and $n$ is the number
of output components. Each output uses the partial sums
\[
 y_j^{(0)}=0,\qquad
 y_j^{(k+1)}
 =\operatorname{fl}\!\left[y_j^{(k)}
   +\operatorname{fl}(W_{jk}x_k)\right],
 \qquad k=0,\ldots,m-1 ,
\]
where $j$ identifies an output component and $\operatorname{fl}$ denotes
rounding to the existing 32-bit floating-point format. The layer then adds
$b_j$ and applies its activation when required. This expression states the
order of arithmetic used by the preceding implementation.

The previous loop finishes one output before starting the next. The new loop
advances several outputs at each input component $k$. These outputs are
independent, so the compiler can evaluate four of them with one vector
instruction while each output retains its original addition order.
We store the weights with adjacent output entries and include this
rearrangement in the model-loading cost. The shared target-context and
target-pair partial sums from the preceding section remain in use.
We retain separate multiplication and addition, the same activation functions,
and the original target aggregation order.

All thirty-six development contexts give bitwise identical probability
vectors. The selected masks also agree at all six tested thresholds.
The geometric mean ratio of new to preceding preparation and inference
time is """
 text+=num(seed_ratio)+r""". This component comparison uses five alternating
repetitions with loaded models. The complete reductions below include loading
and the weight rearrangement.

\subsection{Computing modular inverses with Euclid's algorithm}
The row policy evaluates rational coefficients at the same two finite-field
points as before. Division by a nonzero field element $a$ requires its
inverse modulo the prime $p=2^{31}-1$. The preceding implementation uses
$a^{-1}=a^{p-2}\bmod p$. The extended Euclidean algorithm gives integers
$x$ and $y$ such that
\[
 ax+py=1,\qquad a^{-1}=x\bmod p .
\]
Here $x$ supplies the inverse because the greatest common divisor of $a$
and $p$ is one. The algorithm repeatedly divides the current integer
remainders and updates the coefficients of $a$ and $p$ until it reaches
that greatest common divisor.

We use this inverse in the same coefficient parser, including negative
integer powers. The prime, evaluation points, cache bounds and
unordered-pair cancellation estimates remain unchanged. A zero denominator
still rejects that estimate and retains the existing fallback. These
finite-field calculations guide the row choice; native Kira performs
the symbolic row operations.

Integer coefficients have the same residue at both dimension points.
For a coefficient $c\in\mathbb Z$, we calculate its residue $r$ once,
\[
 r=c\bmod p,\qquad (c(17),c(19))=(r,r)\quad\text{in }\mathbb F_p^2.
\]
Here the two entries are the coefficient values used in the cancellation
test, and $\mathbb F_p$ is the field of integers modulo $p$. For short
integer expressions, this removes two general expression evaluations and
the cache lookup. Other expressions retain the bounded parser and cache.
We also allocate the evaluated coefficients for a row group in one
contiguous array, which removes separate allocations for each row.
These changes preserve every coefficient value and the order of the
cancellation calculations.

Checks on 100,000 nonzero field elements agree with the preceding inverse
and satisfy $aa^{-1}=1\bmod p$. A further 1,000 sparse-row checks agree
on all six features, including the 210 cases with invalid expressions or
finite-field poles. Five alternating repetitions give a ratio of """
 text+=num(row["ratio"])+r""" for new to preceding row-feature calculation
time with cleared coefficient caches. The complete reductions also exercise
the ordinary cache reuse and source-selection code.

\subsection{Complete reduction costs and exact checks}
We first tested the Euclidean inverse alone with the parallel seed
calculation. Its 144 validation workflows preserved all decisions and exact
exports, but its complete row-time ratio was $1.027$ and its row-decision
ratio was $1.017$. Both missed the conditions stated below, so we retain
this candidate as a rejected development result. The revised candidate
adds the integer evaluation and contiguous storage described above.
These changes use development and validation inputs; confirmation results
do not select them.

The next 144 validation workflows compare native choices, seed selection,
row selection and both learned choices on six batches from three physical
profiles. We fix the adoption conditions before validation and require
identical decisions and exports, lower seed complete time, lower row
decision time and a row complete-time ratio at most $1.02$.
Both component comparisons must also improve.

After validation, we freeze the implementation and run the same four methods
on sixteen batches from the eight physical profiles used in the preceding
comparison. Five repetitions with each implementation give 640 workflows.
These inputs provide a repeated implementation comparison and add no new
independent-family evidence. Model weights and thresholds remain fixed.

Timing includes preparation, loading, prediction, fresh IBP generation,
exact elimination, back substitution, reference checks and every fallback.
Reference preparation, interpreter launch, release-hash verification,
policy lookup and evidence
compression remain outside the timed interval. We alternate the implementations
within each method and rotate method order. We take the median for each batch
and report the same profile-weighted geometric ratios and descriptive
95\% bootstrap intervals as before. A ratio below one means less time.
The internal decision timer covers completed policy paths. The complete
workflow timer also includes feature evaluations that return an invalid
estimate and retain the native source.

"""
 text+=f'All 640 workflows pass the exact reference check, using {d["attempts"]} attempts, including {sum(d["failed_attempts"].values())} unsuccessful attempts. All {d["checked_pairs"]} old--new pairs preserve probability vectors, selected seeds, row-choice digests, committed operations and exact exports. The independent audit verifies {audit["coefficient_comparisons"]:,} coefficient equalities over $\\mathbb Q(d)$ across the 784 validation and confirmation workflows~\\cite{{KiraParallelInferenceData}}.\n\n'
 for method,label in [("native","native control"),("seed","seed model"),("row","row model"),("both","combined method")]:
  x=ratio(method+"_new_over_"+method+"_old")
  text+=r"\begin{samepage}"+"\n"+f'The {label} has a new-to-preceding complete-time ratio of {num(x["ratio"])}, with descriptive interval {interval(x)}.'
  if method in ("row","both"):
   z=ratio(method+"_new_over_"+method+"_old","decision_seconds");f=ratio(method+"_new_over_"+method+"_old","forward_seconds")
   text+=f' Its decision-time ratio is {num(z["ratio"])}, and its forward-stage ratio is {num(f["ratio"])}.'
  text+="\n"+r"\par\end{samepage}"+"\n\n"
 text+="The new native control provides a separate comparison for the cost and benefit of the learned decisions. It uses the same execution settings and exact checks.\n\n"
 for method,label in [("seed","seed model"),("row","row model"),("both","combined method")]:
  x=ratio(method+"_new_over_native_new")
  text+=r"\begin{samepage}"+"\n"+f'Relative to that control, the {label} has a complete-time ratio of {num(x["ratio"])}, with interval {interval(x)}.\n'+r"\par\end{samepage}"+"\n\n"
 text+="All three new-to-preceding complete-time intervals include one. The component timings show lower evaluation cost, while these complete-workflow measurements leave the size of the overall change uncertain. Relative to native choices, the aggregate seed and combined ratios exceed one, and the row-only interval also includes one. The results therefore support lower model-evaluation cost within the measured scope; a general complete-time advantage over native Kira remains unestablished.\n\n"
 text+=r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/parallel_inference_times.pdf}
\caption{Complete reduction times for the unchanged learned policies. The left
panel compares the new implementation with the preceding shared calculations.
The right panel compares each new method with the new native control.
Each point is the median of five repetitions for one target batch, including
failed attempts and fallback.}
\label{fig:parallel-inference}
\end{figure}

Eight further application checks supply family definitions, targets and
master indices without supplying target coefficients. Independent comparisons
after execution pass in all eight cases. The production interface uses the
validated implementation with the unchanged routing rule.

The algebraic operation counts remain fixed between the two implementations.
The time change comes from evaluating the same model decisions with different
arithmetic. This distinguishes a reduction in model cost from a reduction in
the algebra needed by Kira. The comparisons concern two- and three-loop
inputs with fixed rational kinematics and symbolic dimension $d$; they do
not establish a general speed advantage across unrestricted higher-loop
or multiscale reductions.
\clearpage
"""
 (ROOT/"report/kira_parallel_inference.tex").write_text(text)
 p=ROOT/"report/report.tex";main=p.read_text()
 if r"\input{kira_parallel_inference}" not in main:main=main.replace(r"\section{Conclusion}",r"\input{kira_parallel_inference}"+"\n\n"+r"\section{Conclusion}")
 start=main.index(r"\section{Conclusion}");end=main.index("\nThe data construction provides",start)
 conclusion=r"""\section{Conclusion}
\label{sec:conclusion}
We integrated seed and source-row policies with exact native Kira reduction
and reduced their evaluation cost while retaining the same decisions.
The latest seed implementation evaluates independent neural outputs together,
and the row implementation combines Euclid's modular inverse with direct\ninteger evaluation and shared coefficient storage.
All probability vectors agree in the thirty-six development contexts.
Checks on 100,000 inverses and 1,000 sparse-row groups also agree.

"""
 conclusion+=f'The new seed component has a time ratio of {num(seed_ratio)} to the preceding shared implementation. The row-feature component has a ratio of {num(row["ratio"])}. These component savings require separate complete-reduction measurements because model evaluation is only one part of the calculation.\n\n'
 for method,label in [("seed","seed"),("row","row"),("both","combined")]:
  x=ratio(method+"_new_over_"+method+"_old");y=ratio(method+"_new_over_native_new")
  conclusion+=f'The {label} method has a complete-time ratio of {num(x["ratio"])} to its preceding implementation, with descriptive interval {interval(x)}. Its ratio to the new native control is {num(y["ratio"])}, with interval {interval(y)}.\n\n'
 conclusion+="The descriptive complete-time intervals include one for all three comparisons with the preceding implementation. Component evaluation is faster, and the complete-workflow gain remains uncertain at this sample size. The seed and combined methods still have aggregate costs above the native control. The row-only comparison with native choices also includes one in its interval.\n\n"
 conclusion+=r"""All 144 validation workflows and 640 confirmation workflows pass the exact
checks and preserve the recorded decisions and operation counts. These times
include IBP generation, model evaluation, exact algebra, checks and fallback.
Eight additional application checks pass with the reference target coefficients
withheld from the reducer. The implementation comparison reuses eight physical
profiles and retains the weights, thresholds and routing selected before
confirmation~\cite{KiraParallelInferenceData}.

"""
 main=main[:start]+conclusion+main[end:]
 abstract=main.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 p.write_text(main)
 p=ROOT/"report/Makefile";s=p.read_text()
 if "kira_parallel_inference.tex" not in s:s=s.replace("kira_shared_evaluation.tex","kira_shared_evaluation.tex kira_parallel_inference.tex")
 p.write_text(s)
 p=ROOT/"report/references.bib";s=p.read_text();begin="% parallel-inference-data-begin";end="% parallel-inference-data-end"
 if begin in s:s=s[:s.index(begin)]+s[s.index(end)+len(end):]
 s+="\n"+begin+"\n"+r"""@misc{KiraParallelInferenceData,
 author = {Saraswat, Rushil},
 title = {Parallel Seed Evaluation and Exact Modular Inverses in Native Kira},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"""+a.data_commit+r"""/Kira_comparison/parallel_inference}{Frozen arithmetic implementations, timing pairs and independent exact checks}}
}
"""+end+"\n";p.write_text(s)
 (EXP/"report_values.json").write_text(json.dumps(dict(data_commit=a.data_commit,component_seed_ratio=seed_ratio,component_row_ratio=row["ratio"],summary_sha256=hashlib.sha256((EXP/"confirmation_summary.json").read_bytes()).hexdigest(),comparisons=d["comparisons"]),indent=2)+"\n")
 p=ROOT/"report/README.md";s=p.read_text();marker="<!-- parallel-inference -->"
 if marker in s:s=s[:s.index(marker)]
 s+="\n"+marker+"\nThe latest section, kira_parallel_inference.tex, explains vector evaluation of independent neural outputs, exact Euclidean field inverses and direct integer features. It preserves 144 rejected-candidate validation workflows and reports 144 final validation workflows, 640 confirmation workflows, all fallback attempts and eight basis-only application checks. The new figure separates implementation costs from comparisons with native choices. The supplied abstract is unchanged. Data commit: "+a.data_commit+".\n";p.write_text(s)
 print(json.dumps(dict(report_written=True,seed_component_ratio=seed_ratio,row_component_ratio=row["ratio"])),flush=True)
if __name__=="__main__":main()
