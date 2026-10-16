"""Describe the exact preparation changes and the unchanged learned policies."""
import json,re
from pathlib import Path
from s30_analyze_parametric import NAMES
import s24_parametric_runtime as app
ROOT,OUT,HERE=app.ROOT,app.OUT,app.HERE
REPORT=ROOT/'report'
def write(p,s):p.write_text(s.rstrip()+'\n')
def main():
    data=json.loads((OUT/'summary.json').read_text());t=data['totals'];ratio=data['median_ratios'];allr=data['all_ratios']
    fmt=lambda x:f'{x:.3f}'
    change=lambda x:(f'{100*(1-x):.1f}\\% less' if x<=1 else f'{100*(x-1):.1f}\\% more')
    fixed=change(ratio['fixed']);allfixed=change(allr['fixed'])
    table='\n'.join(f"{NAMES[g]} & {v['previous']:.3f} & {v['native']:.3f} & {v['fixed']:.3f} & {v['selected']:.3f}\\\\" for g,v in data['graphs'].items())
    section=r'''\section{Reducing preparation around the learned choices}
\label{sec:parametric}
The previous comparison leaves a substantial cost even after the model has chosen a useful seed region. On a four-loop development batch, the actual row operations take a small fraction of the total time, while sector symmetry preparation and repeated equation generation dominate. We therefore retain the trained policies and change the exact work that surrounds their choices. This comparison tests whether better integration can make the same predictions more useful without adding another model or changing its weights.

\subsection{Avoiding unused polynomial terms and repeated equations}
Kira uses parametric polynomials to identify zero sectors and sector symmetries~\cite{KiraOriginal,Lee2014LiteRed}. Each inverse propagator has a Schwinger parameter, an auxiliary variable in this representation. An auxiliary inverse propagator can occur in a numerator while its index remains nonpositive throughout the declared sector domain. Its Schwinger parameter then vanishes in the sector polynomials used for these checks. The preceding implementation first constructs the full polynomials and removes the unused parameter terms from the zero-sector criterion. We now apply this substitution before polynomial construction and use the resulting restricted polynomials for both zero-sector and symmetry checks. Appendix~\ref{app:parametric} proves that this change gives the same polynomial in every admitted sector. The full propagator list remains available when Kira forms IBP identities and transforms numerators.

Kira also constructs selected symbolic equations to check their remaining masters, then constructs those equations again for the final reduction. We keep the unmodified exact rows from the first construction. When the next selection returns the identical ordered list of source equations, the calculation uses those saved rows. If the selection changes or the storage allowance is exceeded, Kira regenerates the equations normally. The saved rows exist only within that reduction; no previous target answer supplies a later result. This change removes a repeated calculation of an established identity. It does not replace equation selection or symbolic elimination.

The application uses the same trained portfolio, graph-specific predictors, thresholds, seed settings, worker choices, and recovery rules as Section~\ref{sec:portfolio}. We fit no model in this comparison. Thus any change relative to the previous application measures the exact integration changes and timing variation. A matched fixed-portfolio control measures the additional effect of the outer prediction. The earlier separate service remains available for the few requests assigned to it, and its full cost remains in the measurement.

\subsection{Fresh targets and matched controls}
We reserve 26 new batches from the same nine graph structures, with one to three targets per batch and loop orders one through four. The rational cases use a fresh parameter profile. The symbolic nonplanar and pentagon cases move the raised denominator power to a new position, while the virtuality box has two singly dotted denominators. Appendix~\ref{app:parametric} specifies these inputs. The frozen range guard can select native settings when a new target pattern lies outside its training range.

The first reference reduction uses expanded seeds with the revised preparation. A second calculation uses the previous executable and a larger numerator-rank limit to check the resulting coefficients in the same basis. Each timed method then receives the target and that prescribed basis. Reference coefficients enter only the comparison after the calculation. The test checks reduction to this basis, rather than proving that the basis is minimal.

We compare four methods: the previous application; native choices with revised preparation; a graph-specific fixed portfolio with revised preparation; and the selected portfolio with revised preparation. The fixed portfolio can contain an earlier learned policy, so it isolates the added outer choice. All methods use the same two-core allocation, memory limits, and exact checks. Native choices use one Kira worker, while the portfolios retain their chosen one or two workers. The revised controls share the application's input checks and portfolio proposal; the native and fixed controls then override that proposal. We report the effect of removing this common overhead below. Each attempt starts a fresh Kira process with fresh temporary files. Three repetitions rotate method order. Complete time includes decisions, input preparation, algebra, coefficient checks, cleanup, and unsuccessful attempts. Initial model loading, reference construction, and basis discovery remain outside these repeated timings.

\subsection{Results and attribution}
Table~\ref{tab:parametric} sums the median time of each batch. The revised selected application takes @SELECTED@ seconds, compared with @PREVIOUS@ seconds for the previous application. This is @SAVING@ time on the measured collection. The selected actions agree with the previous application for every batch and repetition, so this improvement comes from the exact preparation changes around the existing models. Summing all repetitions gives @ALLSAVING@ time than the previous application.

\begin{table}[!htbp]\centering\small
\caption{Complete times in seconds, summed over batch medians. The previous column uses the earlier preparation. The other columns enable both exact changes for direct Kira attempts; the earlier separate service retains its preparation. Fixed denotes the validation-selected portfolio choice for each graph.}
\label{tab:parametric}
\begin{tabular}{@{}lrrrr@{}}\toprule
Graph & Previous & Native & Fixed & Selected\\\midrule
@TABLE@
\midrule Total & @PREVIOUS@ & @NATIVE@ & @FIXED@ & @SELECTED@\\\bottomrule
\end{tabular}\end{table}

With each candidate implemented in the same way for all controls, the selected method uses @NATIVESAVING@ time than native choices and @FIXEDSAVING@ time than the fixed portfolio. Across all repetitions, its difference from the fixed portfolio is @ALLFIXEDSAVING@ time. These controls keep the effect of learned decisions separate from exact reuse. The graph results in Figure~\ref{fig:parametric} show the measured savings and regressions; a smaller total does not imply that every batch becomes faster.

The common interval for input checks and the outer proposal is at most @DISPATCH@ milliseconds per revised request. Removing this entire measured interval from the native and fixed controls gives optimistic totals of @NATIVEBOUND@ and @FIXEDBOUND@ seconds, respectively. The selected method then uses @FIXEDBOUNDSAVING@ time than this optimistic fixed control. This subtraction removes useful checks as well as the unused proposal and therefore serves as a sensitivity bound, rather than a separately timed implementation.

All 312 timed reductions and 26 further basis-only applications reproduce their checked reference coefficients exactly. The reference checks, timed tests, and applications compare @CHECKS@ target--master coefficients. The revised selected method needs @FALLBACKS@ recovery attempts across its timed tests. The recorded process-tree memory peak among the timed reductions is @RSS@ MiB. The selected method takes @CPU@ seconds in summed batch median CPU time, compared with @OLDCPU@ seconds for the previous application. The bounded replay mechanism activates @REPLAYS@ times across the timed controls and retains at most @CACHE@ MiB of accounted row data in an activation.

\begin{figure}[tbp]\centering
\includegraphics[width=\linewidth]{paper_figures/parametric_results.pdf}
\caption{Left: the same learned actions run with the previous and revised preparation. Right: the selected-to-fixed time ratio with revised preparation; the dashed line marks equal time. Each point or bar uses sums of batch medians within a graph. The right panel isolates the additional outer prediction.}
\label{fig:parametric}
\end{figure}

These results support the revised application for this measured collection. They test new parameters and target patterns within known graph structures, with supplied master bases. They do not establish general high-loop scattering performance or a globally shortest reduction. The earlier row-model result remains unchanged, so the application continues to use native row elimination.
'''
    values={'SELECTED':fmt(t['selected']),'PREVIOUS':fmt(t['previous']),'NATIVE':fmt(t['native']),'FIXED':fmt(t['fixed']),
        'SAVING':change(ratio['previous']),'ALLSAVING':change(allr['previous']),'NATIVESAVING':change(ratio['native']),
        'FIXEDSAVING':fixed,'ALLFIXEDSAVING':allfixed,'TABLE':table,'CHECKS':f"{data['coefficient_checks']:,}",
        'FALLBACKS':str(data['recoveries']['selected']),'RSS':f"{data['maximum_rss_bytes']/1024**2:.1f}",
        'CPU':fmt(data['cpu_totals']['selected']),'OLDCPU':fmt(data['cpu_totals']['previous']),
        'REPLAYS':str(data['replay_hits']),'CACHE':f"{data['maximum_accounted_cache_bytes']/1024**2:.3f}",
        'DISPATCH':f"{data['maximum_dispatch_seconds']*1000:.3f}",
        'NATIVEBOUND':fmt(data['optimistic_control_totals']['native']),
        'FIXEDBOUND':fmt(data['optimistic_control_totals']['fixed']),
        'FIXEDBOUNDSAVING':change(t['selected']/data['optimistic_control_totals']['fixed'])}
    for k,v in values.items():section=section.replace('@'+k+'@',v)
    assert '@' not in section.replace('@{}','')
    write(REPORT/'parametric_results.tex',section)
    appendix=r'''\section{Exact restrictions and selected-equation reuse}
\label{app:parametric}
\subsection{Restricting before constructing the polynomials}
Let $b_i$ be the Schwinger parameter associated with inverse propagator $D_i$. For algebraic preparation, suppress its infinitesimal prescription and write the quadratic form with the same Minkowski sign convention as the integral definition:
\begin{equation}
-\sum_i b_iD_i=-\boldsymbol\ell^{\mathsf T}H(b)\boldsymbol\ell
 +2w(b)^{\mathsf T}\boldsymbol\ell+J(b).
\end{equation}
Here $H$ is a symmetric $L\times L$ matrix of scalar coefficients, $w$ is a vector whose entries are external-momentum combinations, and $J$ contains no loop momentum. Lorentz contractions are implicit in the quadratic form. Completing the square gives
\begin{equation}
-(\boldsymbol\ell-H^{-1}w)^{\mathsf T}H(\boldsymbol\ell-H^{-1}w)
 +J+w^{\mathsf T}H^{-1}w.
\end{equation}
The standard parametric construction~\cite{BognerWeinzierl2010}, with an inessential normalization scale suppressed, therefore uses the polynomials
\begin{equation}
U=\det H,\qquad F=J\det H+w^{\mathsf T}\operatorname{adj}(H)w,
\label{eq:parametric-uf}
\end{equation}
where $\operatorname{adj}(H)$ is the adjugate matrix. The inverse serves only in the derivation; Eq.~\eqref{eq:parametric-uf} remains a polynomial identity when a substituted matrix is singular.

Let $B$ contain the propagator positions that occur in at least one declared top sector. Define $R_B$ by setting $b_i=0$ for $i\notin B$. Substitution preserves addition and multiplication. Expanding the determinant over permutations $\pi$ gives
\begin{align}
R_B(\det H)
 &=R_B\left(\sum_{\pi}\operatorname{sgn}(\pi)\prod_{j=1}^L H_{j,\pi(j)}\right)\\
 &=\sum_{\pi}\operatorname{sgn}(\pi)\prod_{j=1}^L R_B(H_{j,\pi(j)})
 =\det(R_BH).
\end{align}
Each entry of the adjugate is a signed minor, so the same argument gives
$R_B\operatorname{adj}(H)=\operatorname{adj}(R_BH)$. Applying these equalities to Eq.~\eqref{eq:parametric-uf} shows that constructing $U,F$ after the substitution produces exactly $R_BU,R_BF$.

Every admitted sector $S$ is a subset of $B$. Setting the remaining absent parameters to zero then gives
\begin{equation}
R_SR_BP=R_SP
\end{equation}
for any polynomial $P$. The sector polynomials used in zero-sector and symmetry checks are consequently identical to those obtained from the full construction. The Euler criterion also agrees because substitution commutes with differentiation in every retained variable, as derived in Appendix~\ref{app:adaptive}. This proof concerns sector polynomials. It does not set an auxiliary inverse propagator to zero in an integral numerator. The implementation retains those propagators in all IBP and numerator operations. It enables the restriction only for declared-sector calculations without cuts or symbolic propagator powers.

\subsection{Reusing an unchanged set of exact equations}
For one generated system, let $Q=(q_1,\ldots,q_k)$ be its ordered list of selected source-equation numbers and let $E_q=\sum_i c_{qi}I_i$ be the corresponding unmodified symbolic row. The first retrieval supplies $E_{q_1},\ldots,E_{q_k}$ to the basis check. If the subsequent selection returns $Q'=Q$, then
\begin{equation}
(E_{q'_1},\ldots,E_{q'_k})=(E_{q_1},\ldots,E_{q_k}).
\end{equation}
Passing the saved rows to the final reduction therefore supplies the same exact identities. Copies of the original rows preserve them when the basis check sorts or alters its working rows. We require equality of the full ordered source list, keep the same system and coefficient treatment, and use ordinary regeneration when that condition fails. Storage allows at most 4,096 rows and 4 MiB of accounted row payload, plus bounded container overhead. A development check forces a one-byte allowance and confirms that ordinary regeneration returns the same coefficients. This is within-calculation reuse, with no transfer of coefficients between target requests.

\subsection{Reserved inputs and comparison definitions}
The rational families and target construction follow Appendix~\ref{app:adaptive} with $h=307$ and $j=0,1,2$. The planar double box and connected bubble boxes use $s=-4693$ and $t=-5319$, and the two-point families use $p^2=-4693$. The nonplanar and virtuality boxes use $s=-5639$ and $t=-3197$, with virtuality $v=-3833$ for the latter. The pentagon invariants $(s_{12},s_{23},s_{34},s_{45},s_{51})$ are $(-6151,-6153,-6157,-6159,-6163)$. The three-loop vacuum uses the squared masses stated there with the last value $53+2h=667$. Graph-specific momentum conventions remain those of Appendix~\ref{app:families}; the connected bubble boxes retain Appendix~\ref{app:higher-scattering}'s convention. Each dots, mixed, or pinched batch contains up to three distinct indexed targets. The symbolic nonplanar and pentagon targets have power three on the fifth physical denominator. The symbolic virtuality box has power two on its first and fourth denominators. Other physical powers are one and other auxiliary powers are zero.

References use $(r_0+1,s_0+1,d_0+1)$, followed by an independent check with numerator-rank limit increased by one more unit. The four-loop bubble reference instead uses $(12,1,2)$ and $(12,2,2)$, fixed before testing. The first calculation uses the new exact preparation, and the second uses the previous executable. The model files and decision rules remain frozen throughout the comparison. The definitions of complete-time aggregation and relative speedup are those in Appendix~\ref{app:portfolio}. All repetitions and individual batch results remain available; no confidence interval is inferred from three runs.

For the common-dispatch sensitivity calculation, let $D_{bcr}$ be the measured input-check and outer-proposal interval for batch $b$, control $c$, and repetition $r$. We subtract that interval before taking the median:
\begin{equation}
T_c^{\rm optimistic}=\sum_b\operatorname{median}_{r=1,2,3}(T_{bcr}-D_{bcr}).
\end{equation}
The unused proposal occupies only part of $D_{bcr}$. Holding the remaining measured work fixed, removing all of $D_{bcr}$ therefore overstates the saving available from removing that proposal alone. This is a sensitivity calculation on the recorded timings, not a prediction of how a different executable would interact with the operating system.
'''
    write(REPORT/'parametric_appendix.tex',appendix)
    bib=r'''@misc{BognerWeinzierl2010,
 author={Bogner, Christian and Weinzierl, Stefan},
 title={Feynman graph polynomials},
 year={2010}, eprint={1002.3458}, archivePrefix={arXiv}, primaryClass={hep-ph},
 doi={10.1142/S0217751X10049438},
 note={\href{https://arxiv.org/abs/1002.3458}{arXiv:1002.3458}}
}'''
    for name in ['paper_references.bib','type_specialist_references.bib']:
        p=REPORT/name;s=p.read_text()
        if '{BognerWeinzierl2010,' not in s:write(p,s+'\n'+bib)
    report=(REPORT/'report.tex').read_text()
    if '\\input{parametric_results}' not in report:report=report.replace('\\input{portfolio_results}','\\input{portfolio_results}\n\\input{parametric_results}')
    if '\\input{parametric_appendix}' not in report:report=report.replace('\\input{portfolio_appendix}','\\input{portfolio_appendix}\n\\input{parametric_appendix}')
    abstract=(r'Integration-by-parts reduction expresses Feynman integrals in a master basis, while the chosen equations and implementation determine its cost. We train models to select seeds, equations, and complete Kira strategies using measured calculation time. Validation selects useful learned decisions and retains fixed choices elsewhere. We then reduce the exact work around those decisions by restricting sector polynomials before construction and reusing unchanged selected equations within one reduction. On 26 fresh batches from nine known graph structures through four loops, the same frozen model choices take '+fmt(t['selected'])+' seconds with the revised preparation and '+fmt(t['previous'])+' seconds with the previous preparation, or '+change(ratio['previous'])+r' time. These totals sum three-run batch medians. All 312 timed reductions and 26 further applications agree exactly with independently checked reference coefficients. Matched native and fixed-portfolio controls separate the role of the learned decisions from the exact implementation changes. Learned row elimination remains excluded because it has not given a reliable complete-time gain. The results concern the tested graph structures, target patterns, and prescribed master bases; they do not establish a fastest method for arbitrary loop integrals.')
    report=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',report,flags=re.S)
    overview=(r'The latest comparison keeps every trained model fixed and reduces exact preparation around its decisions. On 26 new batches, complete time changes from '+fmt(t['previous'])+' to '+fmt(t['selected'])+' seconds, or '+change(ratio['previous'])+r' time. Section~\ref{sec:parametric} gives the matched controls and graph results. With the revised preparation held fixed, the selected portfolio uses '+fixed+' time than the fixed portfolio by summed medians and '+allfixed+r' time across all repetitions. The previous portfolio study in Section~\ref{sec:portfolio} remains a separate comparison on different targets.')
    begin=report.index('The final portfolio selects a complete calculation before equation generation.',report.index('\\section{Overall performance'))
    end=report.index('\n\nThe earlier model tests',begin);report=report[:begin]+overview+report[end:]
    report=re.sub(r'% BEGIN FINAL PORTFOLIO SUMMARY.*?% END FINAL PORTFOLIO SUMMARY',lambda m:'% BEGIN FINAL PORTFOLIO SUMMARY\nRevised exact preparation & Fresh known-graph batches, loops 1--4 & '+change(ratio['previous'])+' time than the previous implementation\\\\\nAdded outer prediction & Same revised preparation & '+fixed+' time by medians; '+allfixed+' across repetitions\\\\\n% END FINAL PORTFOLIO SUMMARY',report,flags=re.S)
    conclusion=(r'We have trained and tested models for decisions that affect exact Feynman integral reduction with Kira. The retained method chooses seeds and complete strategies before equation generation, uses equation selection in its validated domains, and keeps native row elimination. Its complete-time comparisons include prediction, exact algebra, checks, and recovery.'+'\n\n'+overview+'\n\n'+r'The latest gain comes from restricting polynomial construction to the declared sector domain and reusing an unchanged ordered set of selected equations within a calculation. These are exact changes around the frozen models. All 312 timed comparisons and 26 additional applications reproduce their checked reference coefficients. The fixed control and the native control identify the separate effect of the learned choices, including regressions on individual batches.'+'\n\n'+r'The tests cover known graph structures, fresh rational parameters, selected symbolic targets, and connected scattering through four loops with supplied master bases. The earlier recurrence result through twelve loops retains its separate restricted-vacuum scope. General higher-loop scattering, arbitrary symbolic kinematics, and global optimality remain unverified. The measured application supplies exact recovery and resource limits within this stated scope.')
    report=re.sub(r'\\section\{Conclusion\}.*?\n\\appendix',lambda m:'\\section{Conclusion}\n'+conclusion+'\n\n\\appendix',report,flags=re.S)
    write(REPORT/'report.tex',report)
    notes=(REPORT/'notes.tex').read_text()
    if '\\input{parametric_results}' not in notes:notes=notes.replace('\\input{portfolio_results}','\\input{portfolio_results}\n\\input{parametric_results}')
    if '\\input{parametric_appendix}' not in notes:notes=notes.replace('\\input{portfolio_appendix}','\\input{portfolio_appendix}\n\\input{parametric_appendix}')
    marker='% BEGIN CURRENT PORTFOLIO CONCLUSION'
    notes=re.sub(marker+r'.*?% END CURRENT PORTFOLIO CONCLUSION',lambda m:marker+'\n'+overview+'\n% END CURRENT PORTFOLIO CONCLUSION',notes,flags=re.S)
    write(REPORT/'notes.tex',notes)
    check=(REPORT/'s01_check_paper.py').read_text().replace("'portfolio_results.tex','portfolio_appendix.tex']","'portfolio_results.tex','portfolio_appendix.tex','parametric_results.tex','parametric_appendix.tex']")
    write(REPORT/'s01_check_paper.py',check)
    make=(REPORT/'Makefile').read_text().replace('portfolio_results.tex portfolio_appendix.tex paper_references.bib','portfolio_results.tex portfolio_appendix.tex parametric_results.tex parametric_appendix.tex paper_references.bib')
    write(REPORT/'Makefile',make)
    guide=f'''# Exact preparation around the learned portfolio

The current application uses the frozen models from `../selective_expansion/`.
It restricts sector polynomials before construction and reuses unchanged selected equations within one reduction.
The models and their action choices stay unchanged in this comparison.
The revised method takes {t['selected']:.3f} seconds against {t['previous']:.3f} seconds for the previous implementation.
These totals sum the batch medians of three repetitions on 26 fresh batches.
Read `summary.json` for fixed controls, CPU times, regressions, and individual results.
All 312 timed reductions and 26 additional applications pass exact reference checks.

Use `../s24_parametric_runtime.py --case CASE.json --basis BASIS.json --output RESULT.json.gz` inside a scheduled job.
Use the same case schema as `protocol.json`. The basis file contains a JSON list of integer index vectors.
The application receives no reference coefficients. It reports failure if bounded recovery cannot complete the reduction.
Keep the model files, source files, and the two native builds at their recorded versions.
Cuts, symbolic propagator powers, and positive indices outside the declared sector domain are unsupported.
The public interface rejects invalid index types and out-of-domain targets.

Run `../s22_build_parametric.py` to build from the existing bounded Kira toolchain.
This creates `../s23_parametric_runner.py` and a separate native executable under `.tools/kira-parametric/`.
The build preserves the previous executable and records the exact source patches in `integration/`.
`../s25_parametric_job.sh` runs one two-core job with an 8 GiB memory allocation.
`../s27_profile_parametric.py` and `../s28_profile_selection.py` record development phase costs.
`../s29_check_replay.py` checks replay, forced storage bypass, zero targets, and input guards.
`../s26_parametric_study.py` fixes the new test protocol and runs references, comparisons, and applications.
`../s30_analyze_parametric.py` audits results and draws the comparison plot.
`../s31_report_parametric.py` writes the paper sections and folder guides.
Build both PDFs after the report writer. Then run the paper checker.

`development/` contains earlier preparation trials and the replay checks.
`references/` contains expanded-seed reductions and checks with the previous executable.
`model_test/` contains complete timing records for each method and repetition.
`applications/` contains requests that received only targets and the master basis.
`application_test/` contains input guards and the analytic zero check.
`integration/` contains the build instructions and source patches.
`protocol.json` fixes cases, sources, models, and comparison conditions before testing.
`resource_plan.json` bounds storage and resource use. `jobs.json` records only this study's jobs.
The logs preserve the development and completed calculation outcomes.

Each native attempt has a 6 GiB address limit, a 5,200 MiB process-tree RSS limit, and a 32 MiB scratch limit.
Selected-equation reuse allows at most 4,096 rows and 4 MiB of accounted payload, with bounded container overhead.
`KIRA_SELECTED_CACHE_BYTES=1` forces the tested storage-bypass path.
Do not change the frozen policy from test outcomes. Store generated data only on Hoffman and GitHub.
The complete project must stay below 10,000,000,000 bytes across cluster and local files.
'''
    write(OUT/'README.md',guide)
    for name,description in {'development':'Development profiles and exact replay controls. These records are not reserved cost tests.',
       'references':'Expanded-seed reductions and independent checks in the previous executable.',
       'model_test':'Four methods, 26 reserved batches, and three rotated repetitions. Each gzip file contains JSON.',
       'applications':'Twenty-six additional requests. Each receives only the family, targets, and prescribed master basis.',
       'application_test':'Unknown-graph recovery, invalid-input rejection, and an analytic zero-integral check.',
       'integration':'Exact source patches and compiler commands. The original build and model files remain unchanged.'}.items():
        write(OUT/name/'README.md','# '+name.replace('_',' ').capitalize()+'\n\n'+description+'\nRead [the parent guide](../README.md) for the producer, reader, and limits.\n')
    top=(ROOT/'README.md').read_text();block='''<!-- BEGIN ADAPTIVE REDUCTION -->

## Current reduction method

Use the [revised exact preparation with the learned portfolio](ML_model_adaptive_reduction/parametric_preparation/README.md).
The application keeps the trained policies and reduces repeated preparation around their choices.
Read its checked results for the previous implementation, native choices, and fixed portfolio controls.
The new gain comes from exact integration changes. The study does not attribute this gain to new model training.
The earlier [portfolio comparison](ML_model_adaptive_reduction/selective_expansion/README.md) remains available.

<!-- END ADAPTIVE REDUCTION -->'''
    top=re.sub(r'<!-- BEGIN ADAPTIVE REDUCTION -->.*?<!-- END ADAPTIVE REDUCTION -->',lambda m:block,top,flags=re.S);write(ROOT/'README.md',top)
    for path,text in [(HERE/'README.md','The current interface is `s24_parametric_runtime.py`. Read [the revised preparation guide](parametric_preparation/README.md).\nThe earlier `s17_reduce.py` interface remains available as the matched baseline.'),
        (REPORT/'README.md','`parametric_results.tex` contains the latest complete-time comparison.\n`parametric_appendix.tex` derives the exact changes. `parametric_data.json` supplies its checked numbers.\nThe paper and notes include the new comparison and preserve the earlier results.'),
        (REPORT/'paper_figures/README.md','`parametric_results.pdf` compares unchanged learned choices before and after exact preparation changes.\nIts second panel compares the added prediction with a fixed portfolio.\n`ML_model_adaptive_reduction/s30_analyze_parametric.py` creates this figure.')]:
        s=path.read_text();marker='<!-- BEGIN PARAMETRIC UPDATE -->'
        block=marker+'\n\n'+text+'\n\n<!-- END PARAMETRIC UPDATE -->\n'
        if marker in s:s=re.sub(marker+r'.*?<!-- END PARAMETRIC UPDATE -->\n',lambda m:block,s,flags=re.S)
        else:s=s.split('\n',1)[0]+'\n\n'+block+'\n'+s.split('\n',1)[1]
        write(path,s)
    print('PARAMETRIC_REPORT_WRITTEN',flush=True)
if __name__=='__main__':main()
