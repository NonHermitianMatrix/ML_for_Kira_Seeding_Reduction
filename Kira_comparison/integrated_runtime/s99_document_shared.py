"""Explain shared neural and row calculations using the completed comparisons."""
import argparse,hashlib,json,math,pathlib,re,statistics
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];EXP=HERE/"fast_evaluation"
def n(x):return f"{x:.3f}"
def interval(x):return "$["+n(x["descriptive_interval"][0])+","+n(x["descriptive_interval"][1])+"]$"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit",required=True);a=ap.parse_args();assert re.fullmatch("[0-9a-f]{40}",a.data_commit)
 s=json.loads((EXP/"confirmation_summary.json").read_text());v=json.loads((EXP/"validation_summary.json").read_text())
 audit=json.loads((EXP/"verification.json").read_text());app=json.loads((EXP/"application_verification.json").read_text())
 component=json.loads((EXP/"seed_parity.json").read_text())
 assert s["observed"]==s["planned"]==800 and s["all_exact_and_choice_parity"] and audit["all_passed"] and app["all_passed"]
 ratio=math.exp(statistics.mean(math.log(r["new_seconds"]/r["old_seconds"]) for r in component["results"]))
 def c(key,field="complete_seconds",kind=None):
  d=s["comparisons"][key][field]
  return d["all"] if kind is None else d["by_topology"][kind]
 text=r"""\clearpage
\section{Reusing model calculations without changing reductions}
\label{sec:shared-evaluation}
The preceding comparison shows that model evaluation can offset savings in
algebraic work. We therefore reduce repeated calculations inside the same
models, while retaining their weights, seed thresholds, row choices and
automatic routing rule. This section measures how the change affects both
model evaluation and the complete reduction.

\subsection{Sharing calculations in the seed network}
The seed network uses the same family and target context for every candidate.
Let $\boldsymbol c\in\mathbb R^{5h}$ be that context,
$\boldsymbol z_j\in\mathbb R^h$ the embedding of candidate seed $j$, and
$\boldsymbol a_j\in\mathbb R^h$ its attention-weighted target embedding.
The embedding dimension is $h=32$. The first score layer forms
\[
 \boldsymbol h_j=\tanh\!\left(
 W_c\boldsymbol c+W_z\boldsymbol z_j+W_a\boldsymbol a_j+\boldsymbol b
 \right),
\]
where the matrices are the corresponding blocks of the existing weight matrix,
$\boldsymbol b$ is its bias vector, and $\boldsymbol h_j$ is the hidden score
vector. The term $W_c\boldsymbol c$ is common to all candidate seeds.
We calculate its floating-point accumulator once and continue from that
accumulator for each seed. The continuation preserves the original order
of multiplications and additions.

The target-pair layer admits similar reuse. If $\boldsymbol e_i$ and
$\boldsymbol e_k$ are two target embeddings, its pair embedding is
\[
 \boldsymbol p_{ik}=\tanh\!\left(
 U_1\boldsymbol e_i+U_2\boldsymbol e_k+
 U_3(\boldsymbol e_i-\boldsymbol e_k)+
 U_4(\boldsymbol e_i\odot\boldsymbol e_k)+\boldsymbol b_p
 \right).
\]
Here $U_1,\ldots,U_4$ are blocks of the existing pair-layer matrix,
$\boldsymbol b_p$ is its bias, and $\odot$ denotes componentwise multiplication.
The first partial accumulator depends only on $i$, so we reuse it for each
allowed $k$. The remaining operations and ordered-pair aggregation keep their
original order. This removes repeated arithmetic without refitting the network.

All thirty-six development contexts give bitwise identical probability vectors
and identical masks at the six tested thresholds. The largest probability
difference is zero. The geometric mean ratio of new to preceding preparation
and inference time is """
 text+=n(ratio)+r""". These component measurements use repeated calls with the models already
loaded; the complete-workflow comparisons below also include loading and
fallback~\cite{KiraSharedEvaluationData}.

\begin{samepage}
\subsection{Sharing cancellation estimates between source choices}
The two-row identity in the preceding section also applies to each pair
within a larger group of equations. Let $\boldsymbol R_j$ and
$\boldsymbol R_q$ be two coefficient rows whose first nonzero entries
$a_j$ and $a_q$ multiply the same integral. If both entries are nonzero,
the two possible updates give
\[
 \boldsymbol R'_j=\boldsymbol R_j-\frac{a_j}{a_q}\boldsymbol R_q,
 \qquad
 \boldsymbol R'_q=\boldsymbol R_q-\frac{a_q}{a_j}\boldsymbol R_j
             =-\frac{a_q}{a_j}\boldsymbol R'_j .
\]
The updated rows differ by a nonzero scalar and therefore contain the same
nonzero positions. Their predicted surviving-entry counts satisfy
\[
 \widehat n_{jq}=\widehat n_{qj}
\]
at the valid finite-field points used by the policy. Here $\widehat n_{jq}$
is the predicted number of entries after source $q$ updates row $j$.
The union size, cancellation count and zero-row indicator also agree in the
two directions.
\end{samepage}

We evaluate each unordered pair once and add its statistics to both candidate
sources. The previous implementation evaluated both directions separately.
The coefficient parser, finite-field points, cache limits and invalid-input
fallback remain the same. A further change reads fixed policy settings once
per forward-reduction stage and evaluates only nonzero score coefficients.
The policy calculates its normalized confidence when a requested decision
record uses that value. The production path retains the selected source
without calculating an unused confidence.

One thousand sparse-row checks compare all six cancellation features with
the previous implementation. All checks agree, including 210 cases with
invalid expressions or finite-field poles. Full validation then compares
the old and new implementations on six batches from the three validation
profiles. Its 180 workflows preserve probability vectors, masks, row-choice
digests, operation counts, attempt outcomes and exact exports. The validation
conditions require lower seed complete time, lower row decision time and
a row complete-time ratio no larger than $1.02$. These conditions are fixed
before validation.

\begin{samepage}
\subsection{Complete calculations with the unchanged decisions}
After validation, we freeze the implementation and compare five methods:
native choices, the seed model, the row model, both models, and automatic
routing. Each method runs with both implementations on the same sixteen
batches from the eight physical profiles in the preceding section.
Five repetitions give 800 complete workflows. We increase the confirmation
from three to five repetitions before its freeze because validation shows
execution-time variation between runs. This confirmation reuses the earlier
physical profiles and provides no additional independent-family evidence.
\end{samepage}

The time includes preparation, model loading, inference, fresh IBP generation,
exact elimination, back substitution, reference checks and every fallback.
The common reference calculation, interpreter launch, top-level policy lookup
and evidence compression remain outside the interval. Old and new runs
alternate within each method, and method order rotates across repetitions.
We take a median for each batch and use the same profile-weighted geometric
ratios and descriptive bootstrap intervals as before.
"""
 text+=f"\nAll {s['observed']} workflows finish with exact reference agreement, using {s['attempts']} attempts. The retained failures comprise {sum(s['failed_attempts'].values())} unsuccessful attempts and contribute to the completed workflow times. All {s['checked_pairs']} old--new pairs preserve the recorded algebraic choices and outputs. Across validation and confirmation, the independent parser verifies {audit['coefficient_comparisons']:,} coefficient equalities through exact polynomial cross multiplication in $\\mathbb Q(d)$.\n"
 for method,label in [("native","native control"),("seed","seed model"),("row","row model"),("both","combined method"),("auto","automatic method")]:
  x=c(method+"_new_over_"+method+"_old")
  text+=f"\nThe {label} has a new-to-preceding complete-time ratio of {n(x['ratio'])}, with descriptive interval {interval(x)}."
  if method in ("row","both"):
   y=c(method+"_new_over_"+method+"_old","decision_seconds");z=c(method+"_new_over_"+method+"_old","forward_seconds")
   text+=f" Its decision-time ratio is {n(y['ratio'])}, and its forward-stage ratio is {n(z['ratio'])}."
  text+="\n"
 text+=r"""
These comparisons isolate implementation cost while retaining each method's
decisions. Comparing the new model paths with the new native control addresses
the separate question of whether their choices repay the remaining model cost.
"""
 for method,label in [("seed","seed model"),("row","row model"),("both","combined method"),("auto","automatic method")]:
  x=c(method+"_new_over_native_new");z=c(method+"_new_over_native_new","forward_seconds")
  text+=f"\nRelative to the new native control, the {label} has a complete-time ratio of {n(x['ratio'])}, with interval {interval(x)}, and a forward-stage ratio of {n(z['ratio'])}.\n"
 text+=r"""
The seed implementation reduces the complete-time estimate by about $1.8\%$
relative to its preceding implementation, and its descriptive interval remains
below one. The row decision calculation takes about $33\%$ less time, while
the interval for complete row-model time includes one. The row comparison
therefore resolves a reduction in decision cost but does not establish a
reduction in complete time. The seed and row methods both have larger
complete-time estimates than the new native control on this set of inputs.
Automatic routing gives a ratio close to one, with an interval that spans
both a gain and a loss. These measurements support the stated implementation
savings within the tested inputs; they do not establish a general
complete-reduction advantage for the learned policies.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/shared_evaluation_times.pdf}
\caption{Complete-time ratios after sharing model calculations. The left panel
compares each method with its preceding implementation, and the right panel
compares it with the new native control. Every point uses the median of five
repetitions for one target batch. The tests keep model weights and algebraic
choices fixed, include unsuccessful attempts, and reuse the preceding eight
physical profiles.}
\label{fig:shared-evaluation}
\end{figure}

The production interface uses the shared calculations with the unchanged
validation-selected routing rule. Eight additional application checks supply
only the family, target indices and master indices to the reducer, then compare
its outputs independently with retained reference coefficients. All eight
checks pass. The original model checkpoints, preceding implementations and
negative comparisons remain available.

The operation counts are unchanged between implementations because the models
choose the same seeds and source rows. The saving comes from calculating these
choices with less repeated work. The comparison establishes measured costs for
the stated two- and three-loop inputs with fixed rational kinematics and
symbolic dimension $d$. A general gain across unrestricted higher-loop
families and a globally fastest reduction remain outside this evidence.
"""
 text=re.sub(r"\n(Relative to the new native control,[^\n]+)\n",lambda m:"\n"+r"\begin{samepage}"+"\n"+m[1]+"\n"+r"\end{samepage}"+"\n",text)
 text=text.replace(r"\end{samepage}",r"\par\end{samepage}")
 text+=r"\clearpage"+"\n"
 (ROOT/"report/kira_shared_evaluation.tex").write_text(text)
 p=ROOT/"report/report.tex";main=p.read_text().replace(r"\date{October 9, 2026}",r"\date{October 10, 2026}")
 if r"\input{kira_shared_evaluation}" not in main:main=main.replace(r"\section{Conclusion}",r"\input{kira_shared_evaluation}"+"\n\n"+r"\section{Conclusion}")
 start=main.index(r"\section{Conclusion}");end=main.index("\nThe data construction provides",start)
 paragraph=r"""\section{Conclusion}
\label{sec:conclusion}
We integrated seed and source-row policies with exact native Kira reduction
and reduced repeated arithmetic in both models. The shared seed network gives
bitwise identical probabilities in all thirty-six development contexts.
The row feature calculation agrees in one thousand checks, and the 180
validation workflows and 800 confirmation workflows retain the same algebraic
choices and exact results as the preceding implementation.
"""
 for m,label in [("seed","seed"),("row","row"),("both","combined"),("auto","automatic")]:
  x=c(m+"_new_over_"+m+"_old");y=c(m+"_new_over_native_new")
  paragraph+=f"\nThe {label} method has a complete-time ratio of {n(x['ratio'])} to its preceding implementation, with descriptive interval {interval(x)}. Its ratio to the new native control is {n(y['ratio'])}, with interval {interval(y)}.\n"
 row=c("row_new_over_row_old","decision_seconds");rowf=c("row_new_over_native_new","forward_seconds")
 paragraph+=f"\nThe row policy's decision-time ratio to its preceding implementation is {n(row['ratio'])}, while its forward-stage ratio to the new native control is {n(rowf['ratio'])}. The shared calculations preserve the committed algebraic operation counts. The new seed implementation reduces complete time by about $1.8\\%$ relative to its preceding implementation, while the complete row-model comparison does not resolve a time saving. Both model paths have larger complete-time estimates than the new native control on this set of inputs. These results separate reduced inference cost from the effect of learned choices on exact algebra~\\cite{{KiraSharedEvaluationData}}.\n"
 paragraph+=r"""
All complete-time comparisons include native IBP generation, model evaluation,
exact reduction, checks and fallback. The native controls receive the same
shared execution settings. Automatic routing retains the rule fixed from
validation, and the confirmation does not retune weights or thresholds.
"""
 main=main[:start]+paragraph+"\n"+main[end:]
 abstract=main.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 p.write_text(main)
 p=ROOT/"report/Makefile";t=p.read_text()
 if "kira_shared_evaluation.tex" not in t:t=t.replace("kira_integrated_pair.tex","kira_integrated_pair.tex kira_shared_evaluation.tex")
 p.write_text(t)
 p=ROOT/"report/references.bib";t=p.read_text();begin="% shared-evaluation-data-begin";end="% shared-evaluation-data-end"
 if begin in t:t=t[:t.index(begin)]+t[t.index(end)+len(end):]
 t+="\n"+begin+"\n"+r"""@misc{KiraSharedEvaluationData,
 author = {Saraswat, Rushil},
 title = {Shared Model Calculations with Unchanged Native Kira Reductions},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/"""+a.data_commit+r"""/Kira_comparison/integrated_runtime/fast_evaluation}{Frozen implementations, complete timing pairs and independent exact checks}}
}
"""+end+"\n";p.write_text(t)
 (EXP/"report_values.json").write_text(json.dumps(dict(data_commit=a.data_commit,summary_sha256=hashlib.sha256((EXP/"confirmation_summary.json").read_bytes()).hexdigest(),component_ratio=ratio,comparisons=s["comparisons"],audit=audit),indent=2)+"\n")
 p=ROOT/"report/README.md";t=p.read_text();marker="<!-- shared-evaluation -->"
 if marker in t:t=t[:t.index(marker)]
 t+="\n"+marker+"\nThe latest section, kira_shared_evaluation.tex, documents reuse of affine prefixes in the unchanged seed network and unordered-pair cancellation estimates in the unchanged row policy. It reports 180 validation workflows, 800 paired implementation-confirmation workflows, all failed attempts and eight basis-only application checks. Figure shared_evaluation_times.pdf separates improvements over the preceding implementation from comparisons with the native control. The supplied abstract is unchanged. Frozen data commit: "+a.data_commit+".\n";p.write_text(t)
 print(json.dumps(dict(report_written=True,component_ratio=ratio,workflows=s["observed"])),flush=True)
if __name__=="__main__":main()
