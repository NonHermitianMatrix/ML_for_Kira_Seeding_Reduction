"""Document the proven specialization separately from measured ML benefits."""
import re
from s01_study import HERE,ROOT,inputs,rt
R=ROOT/'report'

def replace_block(s,name,text,anchor):
    begin='% BEGIN '+name+'\n';end='% END '+name+'\n';new=begin+text+'\n'+end
    if begin in s:return re.sub(re.escape(begin)+'.*?'+re.escape(end),lambda _:new,s,flags=re.S)
    assert anchor in s;return s.replace(anchor,new+anchor,1)

def main():
    d=rt.read(HERE/'summary.json');f=rt.read(HERE/'native_followup/summary.json');a=rt.read(HERE/'application/summary.json')
    rows=f['matched'];assert rows
    ratios=[r['speedup'] for r in rows]
    text=r'''\section{An exact higher-loop specialization alongside the learned method}
\label{sec:banana}
The learned choices above apply to the physical structures represented in their training and validation data. A useful reduction workflow can also use a proved integral identity when the requested family permits one. We implement this choice for massless two-point banana integrals, which have two vertices connected by $L+1$ massless lines at $L$ loops. Repeated one-loop convolution gives their coefficients directly~\cite{Grozin2004Banana}. This saving comes from the analytic identity and is measured separately from the learned decisions.

Let $p$ be the external momentum, with $p^2\ne0$, and let the physical denominators be $\ell_1^2,\ldots,\ell_L^2$ and $(p-\sum_j\ell_j)^2$. Each denominator has a positive integer power $a_i$. There are no numerator insertions in this specialization. Define $n=L+1$, $b_i=a_i-1$, $K=\sum_i b_i$, and the corner integral $M_L=B_L(1,\ldots,1)$. Appendix~\ref{app:banana} defines the measure and derives
\begin{equation}
 B_L(\boldsymbol a)=
 \frac{(n-Ld/2)_K(n+1-nd/2)_K}
 {(p^2)^K\prod_{i=1}^{n}(2-d/2)_{b_i}b_i!}\,M_L,
 \label{eq:banana-main}
\end{equation}
where $(z)_k=\prod_{j=0}^{k-1}(z+j)$ and $(z)_0=1$. Thus all scalar targets in this class have rational reduction coefficients in $d$ and $p^2$.

Before applying Eq.~\eqref{eq:banana-main}, the workflow checks the propagator momenta, zero masses, nonzero external squared momentum, and allowed indices. It forms and cancels exact linear factors in $d$. Other families pass to the native Kira workflow with the frozen batch and equation choices. Both the ML-enabled and ML-disabled comparison paths use the same analytic identity. The identity therefore contributes no saving to the reported ML comparison.

\subsection{Checks and measured time}
The first native comparison asks Kira to use the corner master with seed limits set directly by the targets. It completes the one-loop requests and fails in eight higher-loop requests. These failures include rejection of the supplied basis and an allocation failure during topology preparation. We retain all of them, then compare four fixed seed choices on a separate development point and freeze the fastest successful choice for each loop count and kinematic form. A new point supplies the matched comparison in Table~\ref{tab:banana}. Appendix~\ref{app:banana} gives the seed definitions and repetitions.
'''
    text+=f"\nThe follow-up completes {len(rows)} matched requests and leaves {len(f['failed'])} request without a completed comparison. Six-loop development reports allocation failures during topology preparation under the imposed memory limit. Since no fixed seed choice passes, the six-loop reserved request does not run and receives no timing ratio. The completed requests check {f['coefficient_checks']} native coefficients exactly. The complete-time speedup ranges from {min(ratios):.1f} to {max(ratios):.1f} times across the completed requests. Both paths include an exact coefficient check, and the direct path also includes its domain check. These timings exclude shared Python imports.\n"
    text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete times in seconds for the defined scalar banana targets. Native uses the development-selected fixed seeds with all ML disabled. Direct uses the proved formula. Each native time is the median of three repetitions.}
\label{tab:banana}
\begin{tabular}{@{}llrrr@{}}\toprule
Loops & $p^2$ & Native & Direct & Speedup\\\midrule
'''
    for r in rows:text+=f"{r['loops']} & "+('Symbolic' if r['symbolic'] else 'Rational')+f" & {r['native_seconds']:.4f} & {r['formula_checked_seconds']:.4f} & {r['speedup']:.1f}"+r'$\times$\\'+'\n'
    text+=r'''\bottomrule\end{tabular}\end{table}
\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/massless_banana_times.pdf}
\caption{The direct coefficient formula avoids the native equation system for the displayed scalar family. Times include exact coefficient checks. The logarithmic time axis shows both methods, and only completed native comparisons appear. These are analytic gains, separate from ML.}
\label{fig:banana}\end{figure}\FloatBarrier
'''
    text+=f"\nAn additional {d['gamma_checks']} numerical checks compare the finite rational formula with the uncancelled Gamma-function expression at one through twelve loops and at 16, 24, and 32 loops. They use 70-digit arithmetic at two noninteger dimensions. The general derivation supports this scalar family at every positive loop count; the numerical checks test its implementation at the stated counts. General higher-loop scattering remains outside this analytic specialization.\n"
    ana=a['analytic'];nat=a['native']
    text+=f"\nA separate test starts a new application process for each request. All {a['timed']} executions use the combined routing interface, and every successful output passes an exact check. It also passes {a['guard_checks']} domain checks. The four analytic requests use one, four, eight, and twelve loops; their summed median application time is {ana['totals']['learned']:.4f} seconds. The same formula serves both comparison paths."
    if nat['cases']:
        text+=f" The {nat['cases']} matched native requests take {nat['totals']['learned']:.3f} seconds with the frozen learned workflow and {nat['totals']['fixed_off']:.3f} seconds with the separately tuned ML-disabled workflow. These native requests repeat the predeclared application subset of the batch study, so they test integration and startup rather than new physical coverage."
    text+='\n'
    (R/'massless_banana_results.tex').write_text(text)
    (R/'massless_banana_appendix.tex').write_text((HERE/'derivation.tex').read_text())
    summary=f"The separate analytic specialization reduces scalar massless banana targets through one corner master, with a derived coefficient valid at every positive loop count. Its {len(rows)} completed native comparisons give a speedup of {min(ratios):.1f}--{max(ratios):.1f} times for the stated targets. These gains come from exact mathematics and are separate from the ML gains (Section~\\ref{{sec:banana}})."
    p=R/'report.tex';s=p.read_text()
    for old,new in [('\\input{batch_policy_results}','\\input{batch_policy_results}\n\\input{massless_banana_results}'),('\\input{batch_policy_appendix}','\\input{batch_policy_appendix}\n\\input{massless_banana_appendix}')]:
        if new not in s:assert old in s;s=s.replace(old,new,1)
    abstract=f"For scalar massless two-point banana families, a separate exact formula gives a speedup of {min(ratios):.1f}--{max(ratios):.1f} times on {len(rows)} native comparisons at one through five loops. The formula has a derivation at arbitrary positive loop order under the stated assumptions; these gains are analytic."
    s=replace_block(s,'BANANA ABSTRACT',abstract,'\\end{abstract}')
    s=replace_block(s,'BANANA OVERALL',summary,'\\subsection{What the model comparisons establish}')
    s=replace_block(s,'BANANA CONCLUSION',summary,'\\appendix')
    p.write_text(s)
    p=R/'notes.tex';s=p.read_text();rev=rt.read(R/'notes_revision.json')
    for old,new in [('\\input{batch_policy_results}','\\input{batch_policy_results}\n\\input{massless_banana_results}'),('\\input{batch_policy_appendix}','\\input{batch_policy_appendix}\n\\input{massless_banana_appendix}')]:
        if new not in s:assert s.count(old)==1;s=s.replace(old,new)
    tag='% END CURRENT WORKFLOW UPDATE'
    if summary not in s:s=s.replace(tag,summary+'\n'+tag,1)
    p.write_text(s);inputs.write(R/'notes_revision.json',rev)
    bib=r'''@article{Grozin2004Banana,
 author={Grozin, A. G.},
 title={Lectures on multiloop calculations},
 journal={International Journal of Modern Physics A},
 volume={19}, pages={473--520}, year={2004},
 doi={10.1142/S0217751X04016775},
 eprint={hep-ph/0307297}, archivePrefix={arXiv}
}
'''
    for n in ['paper_references.bib','type_specialist_references.bib']:
        p=R/n;s=p.read_text()
        if 'Grozin2004Banana' not in s:p.write_text(s.rstrip()+'\n\n'+bib)
    p=R/'s01_check_paper.py';s=p.read_text()
    if "'massless_banana_results.tex'" not in s:s=s.replace("'batch_policy_appendix.tex']","'batch_policy_appendix.tex','massless_banana_results.tex','massless_banana_appendix.tex']",1)
    p.write_text(s)
    p=R/'Makefile';s=p.read_text()
    if 'massless_banana_results.tex' not in s:s=s.replace('report.pdf:','report.pdf: massless_banana_results.tex massless_banana_appendix.tex',1)
    p.write_text(s)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.6,3.6),constrained_layout=True)
    for symbolic,ax in zip([False,True],axs):
        part=[r for r in rows if r['symbolic']==symbolic]
        ax.set_title('Symbolic squared momentum' if symbolic else 'Rational squared momentum')
        ax.plot([r['loops'] for r in part],[r['native_seconds'] for r in part],'o-',color='#b44736',label='Native Kira')
        ax.plot([r['loops'] for r in part],[r['formula_checked_seconds'] for r in part],'s-',color='#166b85',label='Exact formula')
        ax.set_yscale('log');ax.set_xlabel('Number of loops');ax.set_ylabel('Complete time (seconds)')
        ax.set_xticks(sorted({r['loops'] for r in part}));ax.grid(True,axis='y',alpha=.2);ax.legend(frameon=False)
    fig.savefig(R/'paper_figures/massless_banana_times.pdf');plt.close(fig)
    print('BANANA_DOCUMENT_UPDATED',flush=True)

if __name__=='__main__':main()
