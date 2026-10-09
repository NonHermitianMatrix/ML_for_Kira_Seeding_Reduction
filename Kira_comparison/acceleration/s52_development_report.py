"""Render the checked, separate early-admission development results."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=json.loads((HERE/"development_summary.json").read_text());assert s["all_stages_complete"]
stages=s["stages"];pairs=[]
for stage in ("adaptive_pilot","adaptive_validation"):
 rows=stages[stage]["rows"]
 for case in sorted({r["case"] for r in rows}):
  d={r["policy"]:r for r in rows if r["case"]==case}
  if d["adaptive_ml"]["success"] and d["trim_checked"]["success"]:
   pairs.append(d["adaptive_ml"]["seconds"]/d["trim_checked"]["seconds"])
r={x["policy"]:x for x in stages["residual_pilot"]["rows"]}
assert len(pairs)==4 and all(x["success"] for x in r.values())
text=r"""\subsection{Checking and expanding an incomplete seed set}
In separate development trials, we tested whether Kira's initial
finite-field master check could reject an incomplete seed set before
symbolic elimination \cite{Kira3}. This check compares the integrals
left by the generated system with the prescribed master basis. A
rejected set can then be enlarged before Kira starts the more expensive
symbolic calculation. The final coefficients still require exact
checks, since a numerical rank check alone does not prove the full
symbolic reduction. We retained the frozen policies in the reserved
comparison while testing these extensions.

For the first expansion rule, we rank each candidate seed by its
largest model score across the supplied expressions,
\begin{equation}
 Q_\theta(\boldsymbol b)
 =\max_\nu p_\theta(\boldsymbol b\mid\mathcal T_\nu).
\end{equation}
We begin with the first $k_0=32$ seeds and, after a rejected master
check, increase the budget according to
\begin{equation}
 k_{j+1}=\min(2k_j,|\mathcal C|).
\end{equation}
Here $j$ is the number of completed expansion steps and $\mathcal C$
is the candidate pool defined above. A control ranks seeds by their
smallest index distance to a component of a target expression, and
uses the same budget rule. The full candidate pool and restricted
native seeding provide two further controls.

A second rule begins with 64 seeds and uses the additional integrals
returned by the master check as new model inputs. Each such input
contains one integral with coefficient one. We add its four
highest-ranked unused candidates and repeat the check, using the full
pool after five rejected checks. A distance-based control applies the
same expansion to the same additional integrals. These checks require
every component to reduce in the prescribed basis, which can be
stricter than reducing the complete expression when terms cancel.

The 26 development trials gave 23 exact completions and three bounded
incomplete calculations. The latter used 64-target batches and affected
the native control and both learned variants in the initial check
experiment. All completed outputs passed @CHECKS@ independent
finite-field target checks. Across four complete 16-target comparisons,
the doubling rule with learned ranking took @LOW@--@HIGH@ times the
native control's complete time. In the subsequent residual-driven
trial, learned ranking reached a complete basis with @SEEDS@ seeds,
while the distance control used @DISTANCE@. Its complete-time ratio
against native seeding was @RATIO@. These are single development
measurements; they do not establish a repeatable speedup for either
expansion strategy \cite{KiraNativeAccelerationData}.
"""
values={"@CHECKS@":str(sum(x["independent_master_sample_checks"] for x in stages.values())),
 "@LOW@":f"{min(pairs):.3f}","@HIGH@":f"{max(pairs):.3f}","@SEEDS@":str(r["residual_ml"]["selected"]),
 "@DISTANCE@":str(r["residual_distance"]["selected"]),"@RATIO@":f'{r["residual_ml"]["seconds"]/r["trim_checked"]["seconds"]:.3f}'}
for k,v in values.items():text=text.replace(k,v)
(ROOT/"report/kira_adaptive_development.tex").write_text(text)
print(json.dumps(values))
