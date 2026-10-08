"""Update the scientific report from the completed Kira sufficiency test."""
import argparse,re
from s02_common import *
METHOD="\\subsection{Complete reductions from predicted seed sets}\n\\label{sec:seed-kira-sufficiency}\nTo determine whether the predicted seeds supply enough equations,\nwe pass their stored identities to Kira~3.1 and reduce the complete\ntarget expressions symbolically. We retain the same model, reserved\nfamilies and threshold used above. For the candidate set $\\mathcal C$\nin Eq.~\\eqref{eq:seed-model-input}, the selected set is\n\\begin{equation}\n \\widehat{\\mathcal S}_{\\mathcal T}\n =\\{\\boldsymbol\\sigma_b\\in\\mathcal C:p_b\\geq 1/2\\}.\n \\label{eq:kira-selected-seeds}\n\\end{equation}\nLet $\\mathcal E_{\\boldsymbol\\sigma}$ contain the stored IBP identities\ngenerated from seed $\\boldsymbol\\sigma$, and let $\\mathcal B$ contain\nthe stored background identities, including partial fractions and\nsymmetries. For any supplied seed set $\\mathcal S$, Kira receives\n\\begin{equation}\n \\mathcal R(\\mathcal S)\n =\\mathcal B\\cup\n       \\bigcup_{\\boldsymbol\\sigma\\in\\mathcal S}\n                       \\mathcal E_{\\boldsymbol\\sigma}.\n \\label{eq:kira-selected-relations}\n\\end{equation}\nThis construction makes each selected seed available through all its\nstored IBP identities. It uses no reference seed labels, recorded\nreduction paths or reference master coefficients to supply equations.\n\nWe use Kira's user-defined-equation interface, which accepts\nhomogeneous linear relations with rational coefficients and performs\nthe symbolic reduction with Fermat~\\cite{Kira12,Kira3}.\nFor a target with several terms, we add its input definition\n\\begin{equation}\n Z_{\\mathcal T}\n -\\sum_{j=1}^{n_T}c_j(\\boldsymbol x,d)\n                        I_{\\boldsymbol a^{(j)}}=0,\n \\label{eq:kira-target-definition}\n\\end{equation}\nwhere $Z_{\\mathcal T}$ is an auxiliary variable representing the\ncomplete target. This equation contains only the supplied target\nterms. Kira eliminates $Z_{\\mathcal T}$ and expresses its answer\nthrough the integral variables that remain after reduction.\n\nWe place the chosen masters before the other integral variables\nin the elimination ordering and give different seed selections\nseparate copies of every variable. Targets with the same selected\nset can share their equations within one family. This arrangement\nallows Kira to solve several independent systems together while\npreventing one selection from using identities assigned to another.\nWe retain every equation connected to the target terms and discard\nonly disconnected components.\n\nFor each result, we check whether Kira obtains\n\\begin{equation}\n \\mathcal T\n =\\sum_{m=1}^{N_M}\\widehat r_{\\mathcal Tm}(\\boldsymbol x,d)M_m\n  +\\sum_{\\ell=1}^{N_U}u_{\\mathcal T\\ell}(\\boldsymbol x,d)U_\\ell .\n \\label{eq:kira-sufficiency-result}\n\\end{equation}\nHere $N_M$ is the number of specified masters, $U_\\ell$ denotes a\nremaining integral outside that basis, and $N_U$ is their number.\nA complete reduction has no nonzero coefficient $u_{\\mathcal T\\ell}$,\nand every coefficient $\\widehat r_{\\mathcal Tm}$ must equal its\nstored reference $r_{\\mathcal Tm}$ as a rational function.\nWe test this equality by exact cross multiplication of integer\npolynomials and check the resulting coefficients independently\nat the three stored finite-field samples. A successful program\nexit alone does not establish completion in the specified basis.\n\nWe apply the same procedure to the full candidate set\n$\\mathcal S=\\mathcal C$ and to the empty seed set\n$\\mathcal S=\\varnothing$. The first control tests whether the\navailable pool can complete the target and supplies a fallback\nwhen the prediction is insufficient. The second measures how\nmany targets reduce through their definitions and background\nidentities alone.\n"

def main(commit):
 assert re.fullmatch(r"[0-9a-f]{40}",commit)
 r=read(HERE/"results.json");v=read(HERE/"validation.json")
 assert v["passed"] and v["result_sha256"]==sha(HERE/"results.json")
 n=r["targets"];passed=r["policies"]["predicted"].get("exact_match",0);failed=n-passed
 full=r["policies"]["full"].get("exact_match",0);background=r["policies"]["background"].get("exact_match",0)
 different=r["reference_set_agreement"].get("different_complete",0)
 pct=lambda a:100*a/n
 out=ROOT/"report";main=out/"report.tex";s=main.read_text()
 abstract=s.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 results=rf"""
\subsection{{Sufficiency results and the role of additional seeds}}
The test includes all {n:,} reserved targets from {r["families"]:,}
families. Kira reduces {passed:,} targets ({pct(passed):.3f}\%)
completely with their predicted sets, while {failed:,}
({pct(failed):.3f}\%) retain non-master integrals.
The full candidate pool completes {full:,} targets
({pct(full):.3f}\%), and background identities alone complete
{background:,} ({pct(background):.3f}\%).
Every reported complete result agrees with the reference rational
coefficients and passes the independent sample checks.
All requested targets have a recorded outcome, and the final
evaluation has no unresolved solver or export errors
\cite{{KiraSeedSufficiencyData}}.

\begin{{figure}}[htbp]
 \centering
 \includegraphics[width=\linewidth]{{figures/kira_seed_sufficiency.pdf}}
 \caption{{Complete symbolic reductions in the specified master
 basis, shown for predicted seeds, all candidate seeds and no IBP
 seeds. Each loop-order fraction uses every reserved target at that
 order. All three policies retain the same background identities.}}
 \label{{fig:kira-seed-sufficiency}}
\end{{figure}}

Of the targets with complete predicted reductions, {different:,}
use a seed set different from the recorded reference set.
This comparison shows that a model can supply enough equations
through an alternative selection, so reference-set agreement and
reduction completion measure different properties.
The model selects {r["mean_selected_seeds"]:.3f} seeds per target on
average. Across all target--candidate pairs, it selects
{100*r["selected_candidate_fraction"]:.3f}\% of the supplied candidates.
This fraction describes selection within the bounded pools; it
does not measure a runtime improvement over Kira's usual strategies.

\begin{{figure}}[htbp]
 \centering
 \includegraphics[width=\linewidth]{{figures/kira_seed_sets.pdf}}
 \caption{{The selected fraction of candidate seeds at each loop
 order, and the relation between reference-set agreement and complete
 symbolic reduction. Numbers above the bars are target counts.
 Different sufficient sets account for the difference between the
 two tests.}}
 \label{{fig:kira-seed-sets}}
\end{{figure}}

The all-candidate control supplies a direct check of the fallback
within the stored equation domain. A predicted set that leaves
extra integrals requires further equations before we accept its
reduction. The present test supplies the whole available pool at
that stage; it does not identify the smallest necessary addition.
Its conclusions concern rational functions at generic parameter
values, where the denominators in the reduction are defined.

These results establish algebraic sufficiency rates inside Kira
for the stored identities. The user-defined interface is needed
for the present family representation, including the dependent
massive denominators of the higher-loop vacuum families.
Native Kira equation generation from predicted seeds and comparisons
with its own seeding heuristics remain separate tests. The grouped
execution also shares work among targets with identical selected
sets, so its elapsed times do not provide an end-to-end solver
speedup measurement. The next section addresses the separate
learned choice of an allowed elimination step.
"""
 (out/"seed_kira_test.tex").write_text(METHOD+results)
 p=out/"seed_model_test.tex";text=p.read_text()
 old="""The labels identify one recorded sufficient set. Other seed sets can
also reduce the target, so disagreement with these labels does not
by itself establish failure of the proposed reduction. This test
measures reference-set recovery and confidence. It does not run
Kira with the predicted seed sets, prove seed minimality or measure
a solver speedup. The next model addresses the separate choice of
an allowed elimination step after equations are available.
\\FloatBarrier"""
 new="""The labels identify one recorded sufficient set. Other seed sets can
also reduce the target, so disagreement with these labels does not
by itself establish failure of the proposed reduction.
The classification measurements above describe reference-set recovery
and confidence. To determine whether the selected equations complete
the target, we next use the saved predictions in Kira.
\\FloatBarrier
\\input{seed_kira_test}
\\FloatBarrier"""
 if "\\input{seed_kira_test}" not in text:
  assert old in text;text=text.replace(old,new)
 p.write_text(text)
 old="""The present experiments test seed-reference agreement and reduction
of a target coefficient row against a fixed source-equation pool.
Applying the models to Kira's full evolving system remains a separate
step."""
 new="""The present experiments test seed-reference agreement, complete
symbolic reductions in Kira using the predicted seed-filtered
equation pools, and reduction of a target coefficient row.
Native Kira equation generation and learned choices on its full
evolving matrix remain separate integration steps."""
 assert old in s;s=s.replace(old,new)
 old="""For use inside Kira, a reduction would generate equations from the
predicted seeds and check whether they suffice in the chosen master
basis. An unresolved target would require further seeds. The
seed-model test below measures recovery of the recorded sets; it
does not perform this complete solver test."""
 new="""For use inside Kira, we supply the stored equations associated with
the predicted seeds and check whether they suffice in the chosen
master basis. An unresolved target requires further seeds.
Section~\\ref{sec:seed-test-results} measures recovery of the recorded
sets and then tests their algebraic sufficiency through symbolic
Kira reductions. The second test also checks the full candidate
pool as a fallback."""
 assert old in s;s=s.replace(old,new)
 old="""These measurements show how closely the model recovers the recorded
seeds. The sufficiency of its predicted sets inside Kira still
requires a solver test, because alternative sufficient sets can
differ from the reference and omitted reference seeds can leave
a reduction incomplete~\\cite{SeedModelTestData}."""
 new=rf"""These measurements show how closely the model recovers the recorded
seeds~\cite{{SeedModelTestData}}. We then supplied the corresponding
stored identities to Kira and obtained complete symbolic reductions
for {passed:,} targets ({pct(passed):.3f}\%) with the predicted sets.
The remaining {failed:,} targets retained extra integrals.
The full candidate pool completed {full:,} targets
({pct(full):.3f}\%), which tests the fallback within the stored domain.
The exact coefficients agree with the recorded master expansions,
with additional independent checks at three finite-field samples.
Among the complete predicted reductions, {different:,} used a set
different from the reference~\cite{{KiraSeedSufficiencyData}}."""
 assert old in s;s=s.replace(old,new)
 old="""explicit mathematical checks. To establish their use in Kira,
we must test the seed model through complete reductions and supply
additional seeds when necessary. We must also assess the elimination
model on the evolving IBP system and include feature preparation,
model inference and exact algebra in the cost. These tests must
compare total time, equation counts and memory against Kira's
existing strategies to determine whether the learned choices
accelerate reduction."""
 new="""explicit mathematical checks. The new Kira test establishes when
the predicted sets suffice within the stored equation pools and
checks the full-pool fallback for incomplete predictions.
Further integration must generate identities from the predicted
seeds through Kira's native family interface and assess the
elimination model on the evolving IBP system. Comparisons must
include feature preparation, model inference and exact algebra,
together with total time, equation counts and memory against Kira's
existing strategies, to determine whether the learned choices
accelerate reduction."""
 assert old in s;s=s.replace(old,new)
 main.write_text(s)
 assert s.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]==abstract
 bib=out/"references.bib";text=bib.read_text()
 assert "{KiraSeedSufficiencyData," not in text
 text+=rf"""
@misc{{KiraSeedSufficiencyData,
  author = {{Saraswat, Rushil}},
  title = {{Predicted-Seed Sufficiency through Exact Kira Reductions on Reserved Families}},
  year = {{2026}},
  howpublished = {{\href{{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{commit}/ML_model_seed_selection/kira_sufficiency_test}}{{Frozen protocol, selected identities, symbolic results and independent checks}}}}
}}
"""
 bib.write_text(text)
 p=out/"Makefile";text=p.read_text().replace("seed_model_test.tex reduction_model.tex","seed_model_test.tex seed_kira_test.tex reduction_model.tex");p.write_text(text)
 p=out/"README.md";text=p.read_text()
 text=text.replace("The twelve current PDF plots","The fourteen current PDF plots")
 text=text.replace("It identifies the complete Kira reductions still needed to assess a solver speedup.","It includes the new symbolic Kira sufficiency test and identifies the native equation-generation and total-cost comparisons still needed to assess a solver speedup.")
 text+=f"\nseed_kira_test.tex describes all {n:,} reserved targets reduced with predicted, full and empty IBP seed sets through Kira's user-defined-system interface. Predicted sets complete {passed:,} targets ({pct(passed):.3f}%). The full candidate pool completes {full:,}. The associated results and code are fixed at {commit}; the new PDF figures are kira_seed_sufficiency.pdf and kira_seed_sets.pdf. These are exact symbolic comparisons within the stored source pools, with three additional finite-field checks. This experiment does not measure native Kira seeding or a total solver speedup.\n"
 p.write_text(text)
 print("Report updated; abstract unchanged.")
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--data-commit",required=True);main(parser.parse_args().data_commit)
