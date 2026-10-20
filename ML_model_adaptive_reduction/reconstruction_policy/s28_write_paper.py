"""Update the scientific paper and preserve the earlier studies in the notes."""
from s00_reconstruction_common import *
import re

LEARNING=r"""
\section{Learning the remaining Kira cost}
\label{sec:learning}
Exact formulas remove some reductions from the native calculation. For the remaining integrals, the cost still depends on the seed region and on how the coefficients are represented during elimination. We keep the previously validated seed policy and train a new model to choose the algebra procedure. This separates a change in the equations from a change in the arithmetic used to solve them.

\subsection{Seed, equation, and row decisions}
The retained seed model chooses among the wide, tight, and medium regions of Appendix~\ref{app:sparse}. Its cost tree has maximum depth two, and its failure guard uses twelve depth-three trees per action. The original training used 34 batches and sixteen validation batches. We preserve those weights during the present algebra comparison. The companion notes describe that training and a later unsuccessful replacement using complete seed regions.

The separately tested equation model ranks seed--operator pairs before their full coefficients are constructed. It reduces time on its recorded workload, but the present combined application keeps this filter off. The original next-row model scores allowed elimination steps in the changing matrix. Its additional cost exceeded the algebraic savings in the retained comparison, and a later compiled policy did not establish a consistent saving. We omit learned row selection and retain the native elimination rules. Section~\ref{sec:results} gives the separate controls for these three interventions.

\subsection{Choosing the algebra procedure}
Direct symbolic elimination carries rational functions through each operation. Kira can instead solve the equations at finite-field points and use FireFly to reconstruct the rational functions~\cite{Kira2,FireFly2019,FireFly2020}. The preceding native executable uses symbolic reduction without FireFly support. The new executable retains the same project changes to Kira and adds its standard FireFly capability. We use that reconstruction algorithm without changing its mathematics. Our added decision selects direct symbolic reduction or full reconstruction with a probe batch size of 1, 2, 4, 8, or 16. The probe batch size is the number of numerical evaluations grouped by the native calculation. It differs from the number of target integrals in a request.

We prepare 48 training requests, 22 validation requests, and 22 reserved native requests. They contain planar and nonplanar two-loop boxes, massive two-loop sunrise integrals, and a massive three-loop vacuum family. Box batches contain up to six targets with numerator rank at most four. Additional requests test the sector corner and raised propagator powers. The full physical inputs are disjoint between splits; graph structures and some individual target vectors recur. Appendix~\ref{app:reconstruction-inputs} specifies the propagators, targets, kinematics, and split.

Each input has 29 features derived before reduction. They describe loop and external-momentum counts, propagator incidence, masses, sectors, target powers, and the size of the rational kinematic numbers. Family names do not enter the learned features. Appendix~\ref{app:shared} defines the features and training objective. Training measures one complete application per action, and validation measures three. Failed trials retain their elapsed cost and an estimated recovery cost from the measured symbolic control.

We fit ensembles of 32 extremely randomized regression trees~\cite{Geurts2006ExtraTrees}. Each ensemble predicts relative complete cost and an observed failure fraction for all six actions. Separate validation selects the depth, minimum leaf population, and required predicted saving. A fixed control also selects its best action separately for each propagator structure. Thus the learned model must improve on a structure-dependent setting. Deployment requires at least three percent less validation cost and no failed selected validation attempt. Inputs outside the measured feature ranges use the preceding application, and an unsuccessful reconstruction falls back to its symbolic procedure.

The model selects a method before Kira generates and solves the equations. It supplies no reduction coefficients. Exact formulas retain their mathematical admission checks, and the native comparison checks every returned rational coefficient against a separate symbolic reduction in the same master basis. Reconstruction and basis admission alone do not constitute a formal proof for every new input. The independent coefficient checks support the tested results.
"""

DESIGN=r"""
\section{Comparison design}
\label{sec:design}
We fix the trained weights, selected settings, procedures, and reserved inputs before the final comparison. The native test contains 22 new physical requests. A separate analytic test contains 53 previously verified requests: thirteen two-mass vacuum products, 34 connected one-mass vacuum trees, three zero-invariant tensor bubbles, and three ordinary one-loop tensor requests. The two vacuum grids cover every loop order from one through thirteen. These analytic requests test preservation of the exact methods and are excluded from the new model's training. The companion notes also retain the preceding 26-request repeated-mass and scaleless coverage test.

Four applications process the same requests. The earlier application precedes the direct vacuum additions. The preceding application includes those formulas and the retained native seed model. The fixed application adds a validated algebra setting for each propagator structure. The integrated application enables the new cost model only if validation admits it. The fixed and integrated applications share all exact formulas, native settings, and preceding seed decisions. Their comparison isolates the additional algebra-selection model. Comparing the integrated and earlier applications measures the cumulative change across these two extensions on one matched workload.

A subsequent paired comparison uses the same 22 reserved native requests to isolate the inherited learned choices. It holds the validated reconstruction settings fixed and compares the retained learned procedure with its existing all-fixed procedure. Both use the same protected bases, exact references, and resource bounds. This comparison performs no additional fitting or selection from reserved outcomes. Its timings are measured together and are reported separately from the first four-method experiment.

Each timed application starts a fresh process. Its elapsed time includes imports, input preparation, model loading and prediction, exact formulas, native equation generation and solution, any recovery, output, and exit. Reference preparation and the external coefficient comparison lie outside this timer. We run one computational thread per application, use three repetitions, and rotate method order on the same worker. An application has a 90-second outer limit; the bounded native runner can impose an earlier limit on an individual attempt. All methods use the same protected master basis where the native reduction requires one.

Vacuum-product references use independent symbolic partial fractions. The connected-tree comparison checks the preceding exact rule, supported by the derivation in Appendix~\ref{app:trees}. Native and tensor references use separate symbolic Kira calculations. Reference preparation records unsuccessful attempts separately from failures inside a timed application. A request counts as complete only if all repetitions agree with the corresponding exact reference. We report failure and completion counts beside time ratios.

The primary time estimator is the ratio of summed per-request median times on the matched completed subset. Appendix~\ref{app:statistics} defines it and the paired request-resampling interval. This measures the sampled collection, so results for distinct workloads are not multiplied into a general speed factor. The four-method comparison provides the cumulative result directly.
"""

COST_APPENDIX=r"""
\section{Measured-cost learning}
\label{app:shared}
For training request $i$ and action $a$, let $t_{ia}$ be measured elapsed time, $f_{ia}$ the fraction of unsuccessful repetitions, and $b_i$ the measured preceding-application time. We define the training cost and relative cost by
\begin{equation}
 C_{ia}=t_{ia}+f_{ia}b_i,\qquad y_{ia}=C_{ia}/b_i.
 \label{eq:reconstruction-cost}
\end{equation}
The first expression adds the measured failed attempt and the estimated cost of recovery. The second expresses this cost relative to the same request's control. These are training definitions. The reserved comparison measures actual complete applications, including actual recovery.

The ensemble predicts the vector $\boldsymbol z_i=(y_{i1},\ldots,y_{i6},f_{i1},\ldots,f_{i6})$. It minimizes weighted squared error at its regression leaves, following the extremely randomized tree construction of Ref.~\cite{Geurts2006ExtraTrees}. For one component $z$ and a leaf containing requests $S$, its loss is $\sum_{i\in S}b_i(z_i-\mu)^2$. Differentiation with respect to $\mu$ gives
\begin{equation}
 0=2\sum_{i\in S}b_i(\mu-z_i),\qquad
 \widehat z(S)=\frac{\sum_{i\in S}b_i z_i}{\sum_{i\in S}b_i}.
 \label{eq:reconstruction-leaf}
\end{equation}
For a cost component, inserting $z_i=C_{ia}/b_i$ gives
\begin{equation}
 \widehat y_a(S)=\frac{\sum_{i\in S}C_{ia}}{\sum_{i\in S}b_i},
 \qquad
 \arg\min_a\widehat y_a(S)=\arg\min_a\sum_{i\in S}C_{ia}.
 \label{eq:reconstruction-leaf-choice}
\end{equation}
The denominator is independent of the action, which proves the second equality. Thus a leaf ranks actions by their aggregate measured cost on its requests. The ensemble averages the 32 leaf predictions. Weighting by $b_i$ gives slower baseline requests more influence, while relative costs permit one model to represent different physical structures. This local cost interpretation does not prove global minimum time on unseen requests.

Validation compares maximum depths 2, 4, and 6, minimum leaf populations 2 and 4, and predicted saving margins $\eta=0,0.05,0.10,0.20$. For the fixed action $b$ selected for a propagator structure, we choose the least predicted relative cost among actions with predicted failure fraction at most 0.02. We use that action $a_*$ only if
\begin{equation}
 \widehat y_{a_*}<(1-\eta)\widehat y_b.
 \label{eq:reconstruction-margin}
\end{equation}
This inequality is the defined fractional saving condition. If no alternative satisfies it, the action remains $b$. A feature outside the training minimum or maximum uses the preceding procedure. Validation must then show a complete-cost ratio below 0.97 with no failed selected attempt before deployment enables the model. Failure scores describe observed training outcomes; a zero score does not certify an unseen reduction.

To specify the features, define target excess power $D=\sum_j\max(a_j-1,0)$, numerator rank $R=\sum_j\max(-a_j,0)$, and line count $P_T=\sum_j{\bf1}_{a_j>0}$. A line is incident on a loop momentum when that momentum occurs in its inverse propagator. The 29 features are listed in Table~\ref{tab:reconstruction-features}. Every feature follows from the supplied indices and propagator definitions.
\begin{table}[!htbp]\centering\small
\caption{Inputs to the algebra-cost model. Means and extrema over targets use the complete requested batch.}
\label{tab:reconstruction-features}
\begin{tabularx}{\linewidth}{@{}lY@{}}\toprule
Positions & Quantities\\\midrule
1--6 & Number of loops, external momenta, integral coordinates, physical propagators, symbolic external invariants, and $\log(1+n_T)$ for $n_T$ targets\\
7--13 & Maximum and mean $D$, maximum and mean $R$, minimum and maximum $P_T$, and number of distinct sectors\\
14--18 & Number of massive coordinates; number of physical lines containing several loops; maximum loop incidence per physical line; maximum physical-line incidence per loop; mean external-momentum incidence per coordinate\\
19--22 & Minimum $D$, minimum $R$, mean $P_T$, and maximum absolute index\\
23--25 & Mean excess power on massive coordinates; mean numerator rank weighted by loop incidence; mean excess power weighted by loop incidence\\
26--29 & Maximum sum of positive powers; maximum number of absent physical lines; maximum numerator and denominator bit lengths among rational masses and scalar products\\\bottomrule
\end{tabularx}\end{table}
The ordering within positions 7--10 is maximum $D$, maximum $R$, mean $D$, mean $R$. The remaining entries follow the listed order. The bit lengths describe the supplied rational numbers and do not encode a family identifier.
"""

BIB=r"""
@article{FireFly2019,
 author={Klappert, Jonas and Lange, Fabian},
 title={Reconstructing Rational Functions with {FireFly}},
 journal={Computer Physics Communications}, volume={247}, pages={106951}, year={2020},
 doi={10.1016/j.cpc.2019.106951}, eprint={1904.00009}, archivePrefix={arXiv}}
@article{FireFly2020,
 author={Klappert, Jonas and Klein, Sven Yannick and Lange, Fabian},
 title={Interpolation of Dense and Sparse Rational Functions and other Improvements in {FireFly}},
 journal={Computer Physics Communications}, volume={264}, pages={107968}, year={2021},
 doi={10.1016/j.cpc.2021.107968}, eprint={2004.01463}, archivePrefix={arXiv}}
"""

def save(path,text):
 path.write_text(text.strip()+'\n')

def main():
 s=read(HERE/'summary.json');assert s['complete']
 report=ROOT/'report';source=(report/'report.tex').read_text()
 source=source.replace('For the remaining supported native calculations, we compare trained cost selection with a fixed seed region before Kira generates the identities.','For the remaining supported native calculations, we retain the seed policy and compare learned selection of symbolic or finite-field algebra with a fixed setting for each propagator structure.')
 if 'The present extension evaluates vacuum factors' in source:
  begin=source.index('The present extension evaluates vacuum factors')
  end=source.index(r'\section{The decomposition problem',begin)
  source=source[:begin]+r"""The method combines exact partial fractions, tensor and scalar recurrences, and analytic values for specific connected trees. We then address the remaining native coefficient algebra with finite-field reconstruction and a trained cost selector. A matched comparison separates the direct formulas, the established reconstruction algorithm, and the added learned decision. Earlier equation-selection and row-selection results remain separate, and the companion notes preserve their full experiments.

"""+source[end:]
 source=source.replace('Seed region & Generation and solution of the IBP system & Retained seed-cost model; complete-region replacement rejected by validation','Seed region & Generation and solution of the IBP system & Retained seed-cost model')
 source=source.replace('The three learned interventions occur at distinct points (Table', 'The original three learned interventions occur at distinct points (Table')
 if 'The present extension adds a model that selects the coefficient-algebra procedure' not in source:
  source=source.replace('All three can change cost without predicting the physical coefficients themselves.','All three can change cost without predicting the physical coefficients themselves. The present extension adds a model that selects the coefficient-algebra procedure for the remaining native reductions.')
 source=re.sub(r'\\date\{[^}]*\}',lambda _:r'\date{October 20, 2026}',source)
 begin=source.index(r'\section{Learning the remaining Kira cost}')
 end=source.index(r'\input{reconstruction_results}' if r'\input{reconstruction_results}' in source else r'\input{direct_results}',begin)
 source=source[:begin]+LEARNING.strip()+'\n\n'+DESIGN.strip()+'\n\n'+source[end:]
 source=source.replace(r'\input{direct_results}',r'\input{reconstruction_results}')
 if r'\input{reconstruction_appendix}' not in source:source=source.replace(r'\input{direct_appendix}',r'\input{direct_appendix}'+'\n'+r'\input{reconstruction_appendix}')
 save(report/'report.tex',source)
 deriv=(report/'focused_derivations.tex').read_text()
 begin=deriv.index(r'\section{Measured-cost learning}')
 end=deriv.index(r'\section{Physical test inputs}',begin)
 deriv=deriv[:begin]+COST_APPENDIX.strip()+'\n\n'+deriv[end:]
 deriv=deriv.replace('4,000 such ratios','5,000 such ratios')
 stats=deriv.index(r'\section{Time ratios and uncertainty}')
 tail=deriv[stats:].replace(r' R=\frac{S_{\rm new}}{S_{\rm control}}',r' \rho=\frac{S_{\rm new}}{S_{\rm control}}').replace('=1-R.','=1-\\rho.').replace('gives $R$','gives $\\rho$').replace('recompute $R$','recompute $\\rho$')
 deriv=deriv[:stats]+tail
 deriv=deriv.replace('The planar profiles use $(s,t)=(-1009-12h,-1021-14h)$ and the nonplanar profiles use $(-113-18h,-127-10h)$.','The low-rank profiles use $(s,t)=(-1009-12h,-1021-14h)$ for the planar graph and $(-113-18h,-127-10h)$ for the nonplanar graph. Appendix~\\ref{app:reconstruction-inputs} gives the independently chosen high-rank invariants.')
 deriv=deriv.replace('Every native target is','Every high-rank box target is').replace('The current split uses the profiles and batch counts in Appendix~\\ref{app:direct-inputs}.','The current split uses the profiles and batch counts in Appendix~\\ref{app:reconstruction-inputs}.')
 save(report/'focused_derivations.tex',deriv)
 # Preserve historical exact-input details in notes; the paper retains current definitions.
 direct=(report/'direct_appendix.tex').read_text()
 if 'The native inputs use Eqs.' in direct:
  begin=direct.index('The native inputs use Eqs.')
  end=direct.index('An independent symbolic partial-fraction calculation',begin)
  direct=direct[:begin]+'The new native reconstruction inputs are specified in Appendix~\\ref{app:reconstruction-inputs}.\n\n'+direct[end:]
 direct=direct.replace(r'\section{Inputs and checks for the direct-evaluation comparison}',r'\section{Analytic inputs and checks}')
 save(report/'direct_appendix.tex',direct)
 for name in ['paper_references.bib','notes_additional_references.bib']:
  text=(report/name).read_text();allbib=text
  if name.startswith('notes'):allbib+=''.join((report/n).read_text() for n in ['references.bib','type_specialist_references.bib'])
  for entry in BIB.strip().split('@article'):
   if not entry:continue
   key=entry.split(',')[0][1:]
   if not re.search(r'@\w+\{'+re.escape(key)+',',allbib):text+='\n@article'+entry.strip()+'\n'
  save(report/name,text)
 make=(report/'Makefile').read_text().replace('report.pdf: direct_results.tex','report.pdf: reconstruction_results.tex reconstruction_appendix.tex direct_results.tex')
 save(report/'Makefile',make)
 # The result writer provides the current abstract, conclusion, and result section.
 # Append full current methods to the notes with unique reference labels.
 notes=(report/'notes.tex').read_text()
 history=r"""
\section{Development checks and excluded trials}
The development study compared direct symbolic algebra, full finite-field reconstruction, and reconstruction restricted to back-substitution. Full reconstruction was faster than reconstructed back-substitution on all four initial box requests, so the six training actions retain symbolic algebra and five full-reconstruction probe batch sizes. Additional development requests covered sector corners, numerators, raised powers, massive sunrise integrals, and a three-loop vacuum. Some separate probe-size pilots used different nodes; their individual timings were used to retain candidates, rather than to claim a precise cross-node speed ratio.

Two initial coefficient comparisons used different master bases. A separate symbolic reduction in the protected application basis resolved both comparisons, and all affected coefficients agreed. The original output and the corrected comparison remain preserved.

The first expanded reference regions generated substantially more equations and reached the reference time limit. Further complete-region reference checks also reached their bound on high-rank nonplanar requests. The preceding application completed these requests symbolically and supplied the independent coefficients used to check reconstruction. These failures belong to reference preparation, outside the complete application timer.

An early nonplanar input generator used the planar sign convention for the third external momentum. Its fourth leg therefore did not satisfy the intended massless condition. Those inputs and unsuccessful preparation trials were excluded before estimator fitting. The corrected generator checks all 76 box inputs across the three splits: the three listed legs and the convention-dependent fourth leg are massless, and invariant metadata agree with the scalar products. The reserved outcomes did not select the correction or the trained model.
"""
 block=LEARNING+'\n'+DESIGN+'\n'+(report/'reconstruction_results.tex').read_text()+'\n'+COST_APPENDIX+'\n'+(report/'reconstruction_appendix.tex').read_text()+'\n'+history
 local=set(re.findall(r'\\label\{([^}]+)\}',block))
 prior=set(re.findall(r'\\label\{([^}]+)\}',notes))
 def remap(m):
  key=m.group(2)
  if key in local:key='notes-reconstruction-'+key
  elif 'notes-direct-'+key in prior:key='notes-direct-'+key
  return '\\'+m.group(1)+'{'+key+'}'
 block=re.sub(r'\\(label|ref|eqref)\{([^}]+)\}',remap,block)
 marked='% BEGIN CURRENT WORKFLOW UPDATE\n% RECONSTRUCTION UPDATE BEGIN\n'+block.strip()+'\n% RECONSTRUCTION UPDATE END\n% END CURRENT WORKFLOW UPDATE\n'
 notes=re.sub(r'% BEGIN CURRENT WORKFLOW UPDATE\n% RECONSTRUCTION UPDATE BEGIN\n.*?% RECONSTRUCTION UPDATE END\n% END CURRENT WORKFLOW UPDATE\n','',notes,flags=re.S)
 notes=notes.replace(r'\bibliographystyle{unsrt}',marked+r'\bibliographystyle{unsrt}')
 save(report/'notes.tex',notes)
 print('Paper methods and preserved notes updated',flush=True)
if __name__=='__main__':main()
