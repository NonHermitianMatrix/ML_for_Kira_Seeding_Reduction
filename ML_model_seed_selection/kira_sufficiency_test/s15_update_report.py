"""Update the scientific report from the completed Kira sufficiency test."""
import argparse,re
from s02_common import *
METHOD="\\subsection{Sufficiency of the predicted seeds inside Kira}\n\\label{sec:seed-kira-sufficiency}\nTo determine whether the predicted seeds supply enough equations,\nwe use Kira~3.1 to test whether each target belongs to the span of\nits specified masters modulo the available identities. This means\nthat the target can be written as a linear combination of those\nmasters after using the selected equations. We retain the frozen\nmodel, reserved families and threshold of one half from\nEq.~\\eqref{eq:seed-predicted-set}.\n\nLet $\\mathcal E_{\\boldsymbol\\sigma}$ contain the stored IBP identities\nfrom seed $\\boldsymbol\\sigma$, and let $\\mathcal B$ contain the\nbackground identities, including partial fractions and symmetries.\nA supplied seed set $\\mathcal S$ provides the equations\n\\begin{equation}\n \\mathcal A(\\mathcal S)\n =\\mathcal B\\cup\n       \\bigcup_{\\boldsymbol\\sigma\\in\\mathcal S}\n                       \\mathcal E_{\\boldsymbol\\sigma}.\n \\label{eq:kira-selected-relations}\n\\end{equation}\nEvery selected seed contributes all its stored IBP identities.\nThe reference seed labels, construction paths and master coefficients\nsupply no equations to this test.\n\nThe sufficiency condition follows from linear algebra over the field\n$\\mathbb K=\\mathbb Q(\\boldsymbol x,d)$ of rational functions in the\nkinematic parameters $\\boldsymbol x$ and dimension $d$.\nLet $V$ be the vector space with one formal basis vector for each\nintegral in the supplied system, let $v_{\\mathcal T}$ be the coefficient\nvector of the target, and let $\\mathcal R(\\mathcal S)$ be the row space\nof the equations in $\\mathcal A(\\mathcal S)$. Also let\n$V_M$ be the span of the basis vectors for the specified\nmasters. Then\n\\begin{equation}\n \\begin{aligned}\n \\mathcal T=\\sum_m r_{\\mathcal Tm} M_m\n \\quad\\hbox{using }\\mathcal A(\\mathcal S)\n &\\quad\\Longleftrightarrow\\quad\n v_{\\mathcal T}\\in\\mathcal R(\\mathcal S)+V_M,\\\\\n &\\quad\\Longleftrightarrow\\quad\n [v_{\\mathcal T}]=0\n \\quad\\hbox{in }V/(\\mathcal R(\\mathcal S)+V_M).\n \\end{aligned}\n \\label{eq:kira-master-span}\n\\end{equation}\nHere $M_m$ is a specified master, $r_{\\mathcal Tm}\\in\\mathbb K$ is its reduction\ncoefficient, and square brackets denote the equivalence class after\nremoving combinations of available equations and master vectors.\nThis condition tests whether such coefficients exist without\nrequiring their full symbolic reconstruction.\nSufficiency applies to the supplied target expression and permits\nexact cancellation among its terms.\n\nWe implement the condition through Kira's user-defined-equation\ninterface, which accepts homogeneous linear systems with rational\ncoefficients and uses Fermat for symbolic operations\n\\cite{Kira12,Kira3}. Each target has an auxiliary variable\n$Z_{\\mathcal T}$ and the input equation\n\\begin{equation}\n Z_{\\mathcal T}\n -\\sum_{j=1}^{n_T}c_j(\\boldsymbol x,d)\n                         I_{\\boldsymbol a^{(j)}}=0.\n \\label{eq:kira-target-definition}\n\\end{equation}\nAll terms in this equation come from the public target expression\nin Eq.~\\eqref{eq:seed-model-input}. We add one unit row for each\nspecified master vector. These rows impose $M_m=0$ in the formal\nquotient used for the test, where every possible master combination\nrepresents zero. They do not change the physical values of the\nmaster integrals.\n\nKira reduces $Z_{\\mathcal T}$ exactly in this system. A zero remainder\nestablishes the condition in Eq.~\\eqref{eq:kira-master-span}, and a\nnonzero remainder shows that the supplied equations leave an\nindependent contribution outside the specified master span.\nThe conclusion applies to rational functions at generic parameter\nvalues where their denominators are defined. A successful program\nexit alone does not establish sufficiency.\n\nDifferent seed sets use separate copies of every integral variable\nso that they cannot share equations. Targets with the same selected\nset can share a system within one family. We retain every equation\nin a component connected to the target terms and remove only\ndisconnected components. For each target we test its predicted set,\nthe full candidate set $\\mathcal C$, and the empty seed set.\nThe full set checks the available fallback, while the empty set\nmeasures reduction through the target definition, master basis and\nbackground identities alone.\n\nWe independently reconstruct the selected row spaces from the\noriginal identities at each of the three stored finite-field\nsamples. At each sample, sparse elimination checks membership after\nremoving master columns and must agree with Kira's symbolic decision.\nEach nonzero symbolic remainder also has a regular sample with a\nnonzero value, which provides an exact witness that its coefficient\ndoes not vanish identically. The sample coordinates enter these\nchecks after the symbolic calculation; reference master coefficients\nremain outside the full sufficiency test. For two pilot\nfamilies, 765 target-and-seed-set comparisons also agree with\nreductions that retain the masters and compare their explicit\nrational coefficients.\n"

def main(commit):
 assert re.fullmatch(r"[0-9a-f]{40}",commit)
 r=read(HERE/"results.json");v=read(HERE/"validation.json")
 assert v["passed"] and v["result_sha256"]==sha(HERE/"results.json")
 n=r["targets"];passed=r["policies"]["predicted"].get("sufficient",0);failed=n-passed
 full=r["policies"]["full"].get("sufficient",0);background=r["policies"]["background"].get("sufficient",0)
 different=r["reference_set_agreement"].get("different_complete",0)
 vacuum=r["by_domain"]["coupled_vacuum"];boxes=r["by_domain"]["box"]
 minor=[]
 for domain,name in [("bubble","bubble"),("triangle","triangle"),("propagator","propagator"),("tadpole","tadpole")]:
  item=r["by_domain"][domain];count=item["predicted"].get("sufficient",0);size=item["targets"]
  minor.append(rf"{count:,} of {size:,} {name} targets ({100*count/size:.3f}\%)")
 minor_summary=", ".join(minor[:-1])+", and "+minor[-1]
 pct=lambda a:100*a/n
 out=ROOT/"report";main=out/"report.tex";s=main.read_text()
 abstract=s.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 results=rf"""
\subsection{{Sufficiency results and the role of additional seeds}}
The test includes all {n:,} reserved targets from {r["families"]:,}
families. The predicted sets supply enough equations for {passed:,}
targets ({pct(passed):.3f}\%), while {failed:,} ({pct(failed):.3f}\%)
have a nonzero remainder outside the master span.
The full candidate pool is sufficient for {full:,} targets
({pct(full):.3f}\%), and background identities alone suffice for
{background:,} ({pct(background):.3f}\%).
Within the coupled-vacuum subset, the predicted sets suffice for
{vacuum["predicted"].get("sufficient",0):,} of {vacuum["targets"]:,}
targets ({100*vacuum["predicted"].get("sufficient",0)/vacuum["targets"]:.3f}\%).
Within the one-loop box subset, they suffice for
{boxes["predicted"].get("sufficient",0):,} of {boxes["targets"]:,}
targets ({100*boxes["predicted"].get("sufficient",0)/boxes["targets"]:.3f}\%).
For the other one-loop samples, the predicted sets suffice for
{minor_summary}. The overall fraction therefore depends on the
mixture of tested family domains.
All symbolic membership decisions agree with the independent
row-space checks at the three stored samples.
All requested targets have a recorded outcome, and the final
evaluation has no unresolved solver or export errors
\cite{{KiraSeedSufficiencyData}}.

\begin{{figure}}[htbp]
 \centering
 \includegraphics[width=\linewidth]{{figures/kira_seed_sufficiency.pdf}}
 \caption{{Targets that belong to the specified master span after
 using the supplied identities, shown for predicted seeds, all
 candidate seeds and no IBP seeds. Each loop-order fraction uses every reserved target at that
 order. All three policies retain the same background identities.}}
 \label{{fig:kira-seed-sufficiency}}
\end{{figure}}

Of the targets with sufficient predicted sets, {different:,}
use a seed set different from the recorded reference set.
This comparison shows that a model can supply enough equations
through an alternative selection, so reference-set agreement and
algebraic sufficiency measure different properties.
The model selects {r["mean_selected_seeds"]:.3f} seeds per target on
average. Across all target--candidate pairs, it selects
{100*r["selected_candidate_fraction"]:.3f}\% of the supplied candidates.
This fraction describes selection within the bounded pools; it
does not measure a runtime improvement over Kira's usual strategies.

\begin{{figure}}[htbp]
 \centering
 \includegraphics[width=\linewidth]{{figures/kira_seed_sets.pdf}}
 \caption{{The selected fraction of candidate seeds at each loop
 order, and the relation between reference-set agreement and seed sufficiency
 in Kira. Numbers above the bars are target counts.
 Different sufficient sets account for the difference between the
 two tests.}}
 \label{{fig:kira-seed-sets}}
\end{{figure}}

The all-candidate control supplies a direct check of the fallback
within the stored equation domain. A predicted set that leaves
extra integrals requires further equations before we accept its
reduction. We solve the full-pool control independently, which checks whether
adding all candidates would supply a sufficient fallback. This test
does not identify the smallest necessary addition or measure reuse
of a preceding elimination.
Its conclusions concern rational functions at generic parameter
values, where the denominators in the reduction are defined.

These results establish algebraic sufficiency rates inside Kira
for the stored identities. The user-defined interface is needed
for the present family representation, including the dependent
massive denominators of the higher-loop vacuum families.
An insufficient outcome refers to the stored identities for the
selected seeds. Additional valid IBP operators at the same seeds can
enlarge that pool. Native Kira equation generation from predicted
seeds and comparisons with its own seeding heuristics remain
separate tests. The grouped
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
 new="""The present experiments test seed-reference agreement, whether
the stored identities from the predicted seeds suffice for reductions
inside Kira, and reduction of a target coefficient row.
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
master basis. An unresolved target requires further identities.
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
 new=rf"""Exact symbolic tests in Kira found the predicted sets sufficient for
{passed:,} targets ({pct(passed):.3f}\%) and the full candidate pool
sufficient for all {full:,}. The full pool therefore supplies a
fallback within the stored domain for {failed:,} incomplete predictions.
All symbolic decisions agree with independent checks at three
finite-field samples, and {different:,} sufficient selections differ
from the reference sets~\cite{{SeedModelTestData,KiraSeedSufficiencyData}}."""
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
 s=s.replace("Measurements of full Kira jobs remain a later stage.", "Measurements of total runtime with native Kira seeding remain a later stage.")
 main.write_text(s)
 assert s.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]==abstract
 bib=out/"references.bib";text=bib.read_text()
 assert "{KiraSeedSufficiencyData," not in text
 text+=rf"""
@misc{{KiraSeedSufficiencyData,
  author = {{Saraswat, Rushil}},
  title = {{Predicted-Seed Sufficiency through Exact Master-Span Tests in {{Kira}}}},
  year = {{2026}},
  howpublished = {{\href{{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{commit}/ML_model_seed_selection/kira_sufficiency_test}}{{Frozen protocol, selected identities, symbolic results and independent checks}}}}
}}
"""
 bib.write_text(text)
 p=out/"Makefile";text=p.read_text().replace("seed_model_test.tex reduction_model.tex","seed_model_test.tex seed_kira_test.tex reduction_model.tex");p.write_text(text)
 p=out/"README.md";text=p.read_text()
 text=text.replace("The twelve current PDF plots","The fourteen current PDF plots")
 text=text.replace("It identifies the complete Kira reductions still needed to assess a solver speedup.","It includes the new symbolic master-span sufficiency test in Kira and identifies the native equation-generation and total-cost comparisons still needed to assess a solver speedup.")
 text+=f"\nseed_kira_test.tex describes all {n:,} reserved targets tested for exact membership in their master span with predicted, full and empty IBP seed sets through Kira's user-defined-system interface. Predicted sets suffice for {passed:,} targets ({pct(passed):.3f}%). The full candidate pool suffices for {full:,}. The associated results and code are fixed at {commit}; the new PDF figures are kira_seed_sufficiency.pdf and kira_seed_sets.pdf. These are exact symbolic membership tests within the stored source pools, with three independent finite-field rank checks. The full experiment does not reconstruct all rational master coefficients. This experiment does not measure native Kira seeding or a total solver speedup.\n"
 p.write_text(text)
 print("Report updated; abstract unchanged.")
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--data-commit",required=True);main(parser.parse_args().data_commit)
