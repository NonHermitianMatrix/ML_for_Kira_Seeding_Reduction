"""Write the mathematical cancellation study and its complete-time results."""
from s00_gamma_common import *
REPORT=ROOT/'report'

def main():
    s=read(HERE/'summary.json');assert s['complete'];a=s['analytic'];large=s['groups']['large']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'axes.titlesize':10.5})
    fig,axes=plt.subplots(1,2,figsize=(8,3.2),constrained_layout=True)
    loops=list(range(1,14))
    for method,label,color in [('previous','Previous finite products','#a94432'),('integrated','Cancel Gamma factors first','#236b8e')]:
        values=[]
        for L in loops:
            rows=[r for r in s['rows'] if r['group']=='large' and r['loops']==L]
            values.append(sum(r['median_seconds'][method] for r in rows)/len(rows))
        axes[0].plot(loops,values,'o-',label=label,color=color,markersize=3)
    for group,label,color in [('large','Large target batches','#236b8e'),('small','Seven-target batches','#6d8b45')]:
        values=[]
        for L in loops:
            rr=[r for r in s['rows'] if r['group']==group and r['loops']==L]
            values.append(sum(r['median_seconds']['integrated'] for r in rr)/sum(r['median_seconds']['previous'] for r in rr))
        axes[1].plot(loops,values,'o-',label=label,color=color,markersize=3)
    axes[0].set(ylabel='Complete application time (s)',title='Early cancellation reduces total time',ylim=(0,None))
    axes[1].axhline(1,color='0.5',linestyle='--',linewidth=1)
    axes[1].set(ylabel='New time / previous time',title='Short calls show no clear gain',ylim=(0,None))
    for ax in axes:
        ax.set_xlabel('Number of loops');ax.set_xticks([1,3,5,7,9,11,13]);ax.legend(frameon=False,fontsize=10);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',alpha=.2)
    fig.savefig(REPORT/'paper_figures/gamma_cancellation.pdf');plt.close(fig)
    text=r'''\section{Cancelling common factors before expansion}
\label{sec:gamma-cancel}
The connected identity removes the need to generate an IBP system for the supported trees, but a large target batch still requires many rational coefficients. The preceding implementation expands integer shifts of individual Gamma ratios and then cancels their common linear factors. We instead collect and cancel complete Gamma factors across the full integral before producing any finite products. We also calculate the dimension-dependent part of each subintegral power and the reference-master arguments once per batch. Appendix~\ref{app:gamma-cancel} derives these steps from the same bubble and triangle identities.

For each common dimension coefficient $B$, the method combines the signed multiplicities of $\Gamma(A+Bd/2)$. Their sum vanishes in the target-to-master ratio. The finite-product identity in Appendix~\ref{app:gamma-cancel} then produces only intervals with nonzero net multiplicity. This avoids forming factors that would cancel later. Integer arithmetic keeps the result exact. The method uses the same master and physical domain as the preceding connected reduction, while other integrals retain the existing exact and learned Kira workflow.

We compare 34 distinct tree structures through thirteen loops, with a small and a large symbolic-scale batch for each structure. The small batch contains seven targets. The large batch contains 128 targets with physical powers up to four, except at one loop, where its full allowed set has 96 targets. Four further requests check the unchanged analytic and native paths. Each method runs five times in a fresh process, with rotated order and the same output procedure. The timer includes loading, recognition, coefficient calculation, output, and exit. Independent comparisons occur after timing. The control uses the preceding coefficient routine in the same application, which isolates the combined effect of early mathematical cancellation and shared batch calculations.

'''
    text+=f"All 72 requests complete in every repetition. The {a['targets']:,} connected target entries agree exactly with the preceding canonical rational coefficients, and {s['gamma_checks']:,} independent Gamma evaluations pass at 80-digit precision with relative tolerance $10^{{-60}}$. The Gamma checks use three selected targets from each connected request at the three dimensions defined in Appendix~\\ref{{app:loop-tree}}. They test the implementation of the proved identity and do not constitute new native high-loop reductions.\n\n"
    text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete application times for the cancellation comparison. Each total sums request medians from five repetitions. The interval resamples complete requests. A ratio below one denotes less time.}
\label{tab:gamma-cancel}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Collection & Requests & Previous (s) & New (s) & Ratio\\\midrule
'''
    for group,label in [('large','Large batches'),('small','Seven-target batches'),('fallback','Unchanged-path checks')]:
        v=s['groups'][group];text+=f"{label} & {v['requests']} & {v['old_seconds']:.3f} & {v['new_seconds']:.3f} & {v['ratio']:.3f}"+r' \\'+'\n'
    v=s['all'];text+=f"All requests & {v['requests']} & {v['old_seconds']:.3f} & {v['new_seconds']:.3f} & {v['ratio']:.3f}"+r' \\'+'\n'
    text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
    lo,hi=large['interval']
    text+=f"For the large connected batches, the new method uses {large['saving_percent']:.1f}\\% less total time, with ratio {large['ratio']:.3f} and request-resampling interval $[{lo:.3f},{hi:.3f}]$. All 34 large requests have a shorter median time. "
    small=s['groups']['small'];text+=f"The seven-target ratio is {small['ratio']:.3f}, with request-resampling interval $[{small['interval'][0]:.3f},{small['interval'][1]:.3f}]$ and {small['slower']} slower requests. These short calls include loading and output, so a faster coefficient calculation need not produce a proportional saving in complete time. Across all 68 connected requests, time falls from {a['old_seconds']:.3f} to {a['new_seconds']:.3f} seconds. "
    v=s['all'];text+=f"Including the four unchanged-path checks, total time falls from {v['old_seconds']:.3f} to {v['new_seconds']:.3f} seconds, or {v['saving_percent']:.1f}\\% less time on this 72-request collection. "
    if small['interval'][0]<=1<=small['interval'][1]:text+='The small-batch interval includes equal time, so the comparison does not resolve an improvement for short calls. '
    text+='These savings arise from exact simplification and shared calculation within a batch. The trained native choices remain unchanged, so this comparison does not assign the added gain to ML. It also preserves the preceding coverage limits for massive and multi-scale graphs.\n\n'
    text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/gamma_cancellation.pdf}
\caption{Early cancellation reduces complete time as the coefficient algebra grows. The left panel averages large-batch request medians at each loop order. The right panel divides summed new medians by summed control medians separately for each batch size. The one-loop large batch has 96 targets; the other large batches have 128. Each point compares matching structures and targets.}
\label{fig:gamma-cancel}
\end{figure}
\FloatBarrier
'''
    (REPORT/'gamma_cancellation_results.tex').write_text(text)
    (REPORT/'gamma_cancellation_appendix.tex').write_bytes((HERE/'gamma_cancellation_appendix.tex').read_bytes())
    (REPORT/'gamma_cancellation_data.json').write_text(json.dumps(s,indent=2)+'\n')
    p=REPORT/'report.tex';z=p.read_text()
    if '\\input{gamma_cancellation_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{gamma_cancellation_results}\n\n\\section{Overall interpretation}')
    if '\\input{gamma_cancellation_appendix}' not in z:z=z.replace('\\input{loop_coverage13_appendix}','\\input{loop_coverage13_appendix}\n\\input{gamma_cancellation_appendix}')
    marker='\\section{Overall interpretation}\n\\label{sec:overall-new}\n'
    if 'The cancellation comparison in Section~' not in z:z=z.replace(marker,marker+r'''The cancellation comparison in Section~\ref{sec:gamma-cancel} holds the connected master basis and output procedure fixed. Its reduction in complete time comes from exact factor cancellation and calculations shared by targets in the same batch. The separate native controls continue to determine the added effect of the trained choices.

''')
    p.write_text(z)
    addition=f"A further exact cancellation step reduces the large connected-batch time from {large['old_seconds']:.3f} to {large['new_seconds']:.3f} seconds across 34 requests with symbolic scale and powers up to four. "
    for name in ['paper_abstract.tex','paper_conclusion.tex']:
        p=REPORT/name;z=p.read_text()
        if addition not in z:
            marker='Earlier controlled tests' if name=='paper_abstract.tex' else 'The fresh native comparison'
            assert marker in z;z=z.replace(marker,addition+marker,1)
        p.write_text(z)
    for part in ['results','appendix']:
        z=(REPORT/f'gamma_cancellation_{part}.tex').read_text()
        for prefix in ['sec:gamma-cancel','app:gamma-cancel','eq:gamma-cancel','tab:gamma-cancel','fig:gamma-cancel','app:loop-tree','eq:loop-tree']:z=z.replace(prefix,prefix.replace(':',':notes-'))
        (REPORT/f'notes_gamma_cancellation_{part}.tex').write_text(z)
    p=REPORT/'notes.tex';z=p.read_text()
    if '\\input{notes_gamma_cancellation_results}' not in z:z=z.replace('\\bibliographystyle','% BEGIN CURRENT WORKFLOW UPDATE\n\\input{notes_gamma_cancellation_results}\n\\input{notes_gamma_cancellation_appendix}\n% END CURRENT WORKFLOW UPDATE\n\\bibliographystyle',1)
    p.write_text(z)
    p=REPORT/'Makefile';z=p.read_text();line=next(x for x in z.splitlines() if x.startswith('report.pdf:'))
    if 'gamma_cancellation_results.tex' not in line:z=z.replace(line,line+' gamma_cancellation_results.tex gamma_cancellation_appendix.tex')
    p.write_text(z)
    for p in [REPORT/'report.tex',REPORT/'notes.tex',REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*gamma_cancellation*.tex')]:p.write_text(''.join(x.rstrip()+'\n' for x in p.read_text().splitlines()).rstrip('\n')+'\n')
    print(json.dumps(dict(documents_updated=True)),flush=True)
if __name__=='__main__':main()
