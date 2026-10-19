"""Explain the new physics domain, complete times, and separate ML contribution."""
from s00_prop_common import *
REPORT=ROOT/'report'

def main():
    s=read(HERE/'summary.json');p=s['groups']['propagator'];ml=s['ml'];allr=s['all']
    dev=read(HERE/'development.json');native=sum(r['checks'] for r in dev['native'])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10.5})
    fig,axes=plt.subplots(1,2,figsize=(8,3.1),constrained_layout=True)
    rr=[r for r in s['rows'] if r['group']=='propagator']
    loops=range(1,14)
    for method,label,color in [('integrated','Exact two-point rule','#236b8e'),('previous','Previous: completed cases','#a94432')]:
        xs=[];ys=[]
        for L in loops:
            rows=[r for r in rr if r['loops']==L and all(r['success'][method])]
            if rows:xs.append(L);ys.append(sum(r['median_seconds'][method] for r in rows)/len(rows))
        axes[0].plot(xs,ys,'o-',label=label,color=color,markersize=4)
    axes[0].set(xlabel='Number of loops',ylabel='Complete application time (s)',yscale='log',title='Exact reduction completes all 34 trees')
    axes[0].set_xticks([1,3,5,7,9,11,13]);axes[0].legend(frameon=False,fontsize=8.5)
    labels=['Two-point rule\nmatched cases','Retained ML\nnative boxes'];vals=[p,ml]
    for i,r in enumerate(vals):
        a,b=r['interval'];axes[1].errorbar(i,r['ratio'],yerr=[[max(0,r['ratio']-a)],[max(0,b-r['ratio'])]],fmt='o',color=['#236b8e','#6d8b45'][i],capsize=4)
    axes[1].axhline(1,color='0.5',linestyle='--');axes[1].set_xticks([0,1]);axes[1].set_xticklabels(labels)
    axes[1].set(xlim=(-.55,1.55),ylim=(0,max(1.15,max(v['interval'][1] for v in vals)*1.08)),ylabel='New time / control time',title='Separate analytic and learned effects')
    for ax in axes:ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.grid(axis='y',alpha=.2)
    fig.savefig(REPORT/'paper_figures/propagator_trees.pdf');plt.close(fig)
    text=r'''\section{Connected two-point reductions and the native index limit}
\label{sec:prop-tree}
The preceding triangle identity suggests a further reduction: a connected tree of massless bubbles also closes analytically when its root is a two-point integral. We implement this extension before the existing analytic and learned choices. It recognizes the momenta, masses, and powers, integrates each nonroot bubble, and evaluates the remaining root bubble. The dimension-dependent powers transferred between subintegrals are retained exactly. Appendix~\ref{app:prop-tree} defines the family and derives the rational target-to-master coefficient. This use of massless subintegrals follows established parametric propagator methods~\cite{Ruijl2017Forcer}.

This extension also clarifies the apparent loop limit. Kira requires a complete set of $N=L(L+1)/2+LE$ scalar-product coordinates for $L$ loops and $E$ independent external momenta~\cite{Kira3}. The installed native build rejects more than 31 indices, including auxiliary scalar-product coordinates. Consequently, its complete-coordinate limit is seven loops for vacuum families, six for two-point families, and five for families with two or three independent external momenta. Appendix~\ref{app:prop-tree} derives the coordinate count. Exact integration bypasses this native input within the stated analytic domain; it does not remove the restriction for an arbitrary remaining graph.

We freeze 34 distinct two-point tree structures with seven targets each, covering every loop order from one through thirteen. Their scale remains symbolic. Three fresh processes compare the extended application with the preceding application under a twelve-second limit per call. Sixteen triangle requests check the unchanged exact path, while sixteen native two-loop box requests also compare the retained trained choices with fixed choices. The complete timer includes startup, recognition, coefficient calculation or native reduction, model evaluation when used, output, and exit. Independent checks follow timing on both sides.

'''
    text+=f"All {p['new_completed']} two-point requests complete with the new rule. The preceding application completes {p['old_completed']} in every repetition. Among its 31 unsuccessful requests, 21 exceed the native index limit, nine reach the application deadline, and one fails the master-basis verification. We retain these failures in the completion counts and calculate speed ratios only from matched completed requests. The reserved two-point targets pass {s['gamma_checks']} independent Gamma checks at 80-digit precision and scaled error tolerance $10^{{-60}}$. Development also supplies {native} exact coefficient comparisons with native Kira. These checks test the derived identity; the high-loop results do not represent native high-loop IBP solves.\n\n"
    text+=r'''\begin{table}[!htbp]\centering\small
\caption{Complete times from sums of three-run request medians. The completion columns count requests completed in all repetitions. Times use only requests completed by both methods. The ML row uses fixed native choices as its control.}
\label{tab:prop-tree}
\begin{tabularx}{\linewidth}{@{}Yrrrr@{}}\toprule
Comparison & Control/new complete & Paired & Control (s) & New (s)\\\midrule
'''
    for label,r in [('Two-point trees',p),('Triangle checks',s['groups']['triangle']),('Native path checks',s['groups']['native']),('Retained ML versus fixed',ml)]:
        text+=f"{label} & {r['old_completed']}/{r['new_completed']} & {r['matched_completed']} & {r['old_seconds']:.3f} & {r['new_seconds']:.3f}"+r' \\'+'\n'
    text+=r'\bottomrule\end{tabularx}\end{table}'+'\n\n'
    text+=f"For the {p['matched_completed']} matched two-point requests, total time falls from {p['old_seconds']:.3f} to {p['new_seconds']:.3f} seconds, a reduction of {p['saving_percent']:.1f}\\%. The time ratio is {p['ratio']:.3f}, with a request-resampling interval of $[{p['interval'][0]:.3f},{p['interval'][1]:.3f}]$. Across all {allr['matched_completed']} matched requests in this comparison, time changes from {allr['old_seconds']:.3f} to {allr['new_seconds']:.3f} seconds. The analytic extension accounts for the new two-point gain. No new ML model is fitted for this identity.\n\n"
    text+=f"The matched collection-wide ratio is {allr['ratio']:.3f}, with request interval $[{allr['interval'][0]:.3f},{allr['interval'][1]:.3f}]$. This interval includes equal time, so the collection-wide point estimate does not establish a gain across integral families. The unchanged triangle and native paths also have intervals that include equal time.\n\n"
    text+=f"On the sixteen native requests, the retained learned choices take {ml['new_seconds']:.3f} seconds against {ml['old_seconds']:.3f} seconds for fixed choices, giving ratio {ml['ratio']:.3f} and request-resampling interval $[{ml['interval'][0]:.3f},{ml['interval'][1]:.3f}]$. "
    audit=read(HERE/'model_application_audit.json')
    assert audit['top_level_model_used_requests']==16
    text+='The trained batch policy runs on all sixteen requests, choosing the wider sparse seed setting thirteen times and the tighter setting three times. '
    text+=('This fresh comparison does not resolve a reliable ML gain because the interval includes equal time. ' if ml['interval'][0]<=1<=ml['interval'][1] else 'The interval describes this finite collection of native requests. ')
    text+='The earlier controlled seed and equation-selection gains remain separate evidence. The new two-point reduction retains the preceding ML policy for its eligible native inputs. It supports the specified connected massless trees and preserves the documented failures for general massive, multiscale, and irreducible scattering families.\n\n'
    text+=r'''\begin{figure}[!htbp]\centering
\includegraphics[width=\linewidth]{paper_figures/propagator_trees.pdf}
\caption{The exact rule completes the defined two-point trees through thirteen loops. The left panel uses a logarithmic time axis and averages request medians at each loop order. Control points include completed requests only; missing points have no completed control and imply no finite speed factor. The right panel separates the exact extension from the retained native ML contribution, using matched completed requests and request-resampling intervals.}
\label{fig:prop-tree}
\end{figure}
\FloatBarrier
'''
    (REPORT/'propagator_trees_results.tex').write_text(text)
    (REPORT/'propagator_trees_appendix.tex').write_bytes((HERE/'propagator_trees_appendix.tex').read_bytes())
    (REPORT/'propagator_trees_data.json').write_text(json.dumps(s,indent=2)+'\n')
    q=REPORT/'report.tex';z=q.read_text()
    if '\\input{propagator_trees_results}' not in z:z=z.replace('\\section{Overall interpretation}','\\input{propagator_trees_results}\n\n\\section{Overall interpretation}')
    if '\\input{propagator_trees_appendix}' not in z:z=z.replace('\\input{gamma_cancellation_appendix}','\\input{gamma_cancellation_appendix}\n\\input{propagator_trees_appendix}')
    q.write_text(z)
    for part in ['results','appendix']:
        z=(REPORT/f'propagator_trees_{part}.tex').read_text()
        for prefix in ['sec:prop-tree','app:prop-tree','eq:prop-tree','tab:prop-tree','fig:prop-tree','app:loop-tree','eq:loop-tree','app:gamma-cancel','eq:gamma-cancel']:
            z=z.replace(prefix,prefix.replace(':',':notes-'))
        (REPORT/f'notes_propagator_trees_{part}.tex').write_text(z)
    q=REPORT/'notes.tex';z=q.read_text()
    block='\\input{notes_propagator_trees_results}\n\\input{notes_propagator_trees_appendix}\n'
    marked='% BEGIN CURRENT WORKFLOW UPDATE\n'+block+'% END CURRENT WORKFLOW UPDATE\n'
    if block not in z:z=z.replace('\\bibliographystyle',marked+'\\bibliographystyle',1)
    elif marked not in z:z=z.replace(block,marked,1)
    q.write_text(z)
    q=REPORT/'paper_abstract.tex'
    q.write_text(r'''\begin{abstract}
We study how exact integral identities and machine learning reduce the time needed to express loop integrals in terms of master integrals with Kira. The application first integrates supported subgraphs analytically, then uses trained choices to select the remaining native reduction work. We derive exact rational coefficients for connected massless bubble trees with either a one-scale triangle or a two-point root. Recursive bubble integration retains dimension-dependent powers, and cancellation of Gamma factors produces finite rational products. The new two-point comparison completes all 34 defined structures through thirteen loops. '''+f"On its {p['matched_completed']} matched completed requests, time falls from {p['old_seconds']:.3f} to {p['new_seconds']:.3f} seconds. "+r'''A separate triangle comparison reduces large-batch time from 14.305 to 6.731 seconds by cancelling factors before expansion. These gains come from exact algebra. '''+f"The retained ML policy has time ratio {ml['ratio']:.3f} against fixed choices on sixteen fresh native box requests. "+('Its request interval includes equal time. ' if ml['interval'][0]<=1<=ml['interval'][1] else '')+r'''Earlier controlled tests establish separate seed and equation-selection gains. Learned row selection remains omitted. All timings include the stated application costs, and failed controls remain in the coverage results. The analytic domains have explicit mass, kinematic, and numerator restrictions; general high-loop scattering remains outside the demonstrated coverage.
\end{abstract}
''')
    q=REPORT/'paper_conclusion.tex'
    conclusion=r"""\section{Conclusion}
\label{sec:conclusion}
We combine exact subintegral integration with learned choices for the remaining Kira reduction. The exact stage uses proved identities within explicit domains, while the trained native policies choose seed and equation work using measured reduction costs. The solver retains responsibility for the algebra. Learned row selection remains omitted because its measured timing improvement is unresolved.

For the connected triangle trees, cancelling Gamma factors before finite expansion reduces the large-batch time from 14.305 to 6.731 seconds in the comparison of Section~\ref{sec:gamma-cancel}. """
    conclusion+=f"The two-point extension completes all 34 defined connected structures through thirteen loops. On its {p['matched_completed']} matched completed requests, time falls from {p['old_seconds']:.3f} to {p['new_seconds']:.3f} seconds (Table~\\ref{{tab:prop-tree}}). These added gains come from exact algebra. Failed controls remain in the coverage counts and receive no finite speedup factor.\n\n"
    conclusion+=f"On the sixteen native box requests in the latest comparison, the retained ML policy takes {ml['new_seconds']:.3f} seconds against {ml['old_seconds']:.3f} seconds for fixed choices. Its time ratio is {ml['ratio']:.3f}, with request interval $[{ml['interval'][0]:.3f},{ml['interval'][1]:.3f}]$. "
    if ml['interval'][0]<=1<=ml['interval'][1]:conclusion+='This interval includes equal time, so this fresh sample does not resolve a reliable ML gain. '
    conclusion+=r"""Earlier controlled comparisons establish separate seed and equation-selection gains. The preceding forty-box experiment found 2.7\% less time from its added batch decision under its own timer. These results use different workloads and controls, so their speed factors cannot be multiplied into a universal gain.

The installed native build accepts at most 31 indices, including auxiliary scalar-product coordinates. Its loop limit therefore depends on the number of independent external momenta. The derived subintegral identities avoid that input for their supported families. The implementation and tests cover the stated analytic domains through thirteen loops; general massive, multiscale, and irreducible high-loop scattering remain outside the demonstrated coverage. The preceding broad grid still completes 68 of 110 requests. All reported gains apply to their defined comparisons and establish no globally minimum reduction time.
"""
    q.write_text(conclusion)
    q=REPORT/'Makefile';z=q.read_text();line=next(x for x in z.splitlines() if x.startswith('report.pdf:'))
    if 'propagator_trees_results.tex' not in line:z=z.replace(line,line+' propagator_trees_results.tex propagator_trees_appendix.tex')
    q.write_text(z)
    for q in [REPORT/'report.tex',REPORT/'notes.tex',REPORT/'paper_abstract.tex',REPORT/'paper_conclusion.tex',*REPORT.glob('*propagator_trees*.tex')]:q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
    print('Report and notes updated.',flush=True)
if __name__=='__main__':main()
