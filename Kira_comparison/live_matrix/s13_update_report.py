"""Write the measured live-matrix section and synchronize its scientific scope."""
import argparse,hashlib,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPORT=ROOT/"report"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("data_commit");args=ap.parse_args()
 assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 d=json.load(open(HERE/"summary.json"));v=d["validation"]
 assert d["trials"]==84 and not v["incomplete"]
 rows=d["cases"]
 def ratio(base,metric):
  c=next(x for x in d["comparisons"] if x["baseline"]==base and x["policy"]=="learned")
  return c["metrics"][metric]
 def fmt(n):return format(n,",") if isinstance(n,int) else "%.3f"%n
 active=[r for r in rows if r["policy"]=="native" and r["steps"]>0]
 ml=[r for r in rows if r["policy"]=="learned" and r["steps"]>0]
 vals=dict(TRIALS=str(d["trials"]),CHECKS=fmt(v["independent_master_sample_checks"]),
   ROWCHECKS=fmt(v["row_sample_checks"]),CHOICES=fmt(v["live_choices"]),
   CHANGED=fmt(v["choices_using_previously_updated_source"]),
   STOCK=fmt(ratio("stock","cold_seconds")["geometric_mean_ratio"]),
   NATIVE=fmt(ratio("native","cold_seconds")["geometric_mean_ratio"]),
   CONTROL=fmt(ratio("deterministic","cold_seconds")["geometric_mean_ratio"]),
   FWD=fmt(ratio("native","forward_seconds")["geometric_mean_ratio"]),
   READY=fmt(ratio("native","forward_loaded_seconds")["geometric_mean_ratio"]),
   PAIRS=str(ratio("native","forward_seconds")["pairs"]),
   OPML=fmt(int(ratio("native","operations")["sum_policy"])),
   OPNATIVE=fmt(int(ratio("native","operations")["sum_baseline"])),
   OPCONTROL=fmt(int(ratio("deterministic","operations")["sum_baseline"])),
   STEPSML=fmt(int(ratio("native","steps")["sum_policy"])),
   STEPSNATIVE=fmt(int(ratio("native","steps")["sum_baseline"])),
   NMIN="%.6f"%min(r["forward_seconds"] for r in active),
   NMAX="%.6f"%max(r["forward_seconds"] for r in active),
   MMIN=fmt(min(r["forward_seconds"] for r in ml)),
   MMAX=fmt(max(r["forward_seconds"] for r in ml)))
 def fill(text):
  for k,value in vals.items():text=text.replace("@@"+k+"@@",value)
  assert "@@" not in text
  return text
 section=r"""\section{Learned Elimination Inside Kira's Evolving Matrix}
\label{sec:live-matrix}
The row comparison in Section~\ref{sec:cost-comparison} used fixed
source identities to simplify target expressions before the final Kira
call. To test the intended use inside the solver, we now apply the frozen
row model during Kira's symbolic forward elimination. The input is the
current selected IBP matrix, and every exact row update changes the state
used for the next prediction. Kira continues to generate and select
equations, preserve its integral ordering, normalize the triangular
system and perform back substitution~\cite{Kira3}.

\subsection{Choices in the current IBP matrix}
We retain the matrix notation of Eq.~\eqref{eq:reduction-action}.
At step $n$, $A^{(n)}_{rj}$ is the coefficient of integral $j$ in
identity row $r$.
Let $w(j)$ be Kira's ordering weight for integral column $j$, with larger
weights denoting integrals to eliminate earlier. The leading column of a
nonzero row $r$ and the rows with a common leading column are
\begin{equation}
 h_n(r)=\mathop{\rm arg\,max}_{j:A^{(n)}_{rj}\ne0}w(j),
 \qquad
 R_k^{(n)}=\{r:h_n(r)=k\}.
\end{equation}
At each step we take the largest-weight column that leads at least two
rows. If this column is $k_n$, the allowed choices are
\begin{equation}
 \mathcal A_n=
 \{(q,r,k_n):q,r\in R_{k_n}^{(n)},\ q\ne r\}.
 \label{eq:live-actions}
\end{equation}
Here $q$ is the source row and $r$ is the destination row.
The prescribed master columns remain protected. A proposed elimination
of a protected master, or a zero pivot at the public sampling point,
causes the learned trial to fail its interface check.

The model assigns probabilities to every pair in
Eq.~\eqref{eq:live-actions} and selects the largest score. Kira then uses
its existing symbolic update to calculate
\begin{equation}
 A^{(n+1)}_{rj}
 =A^{(n)}_{rj}
 -\frac{A^{(n)}_{rk_n}}{A^{(n)}_{qk_n}}A^{(n)}_{qj}.
 \label{eq:live-update}
\end{equation}
All these rows represent zero identities, so this operation preserves
their solution space. The new destination row has a lower leading
integral, or becomes zero and leaves the matrix. It can supply a source
row in a later step. The next prediction therefore uses the updated
identities throughout the matrix.

We use the saved 132-feature representation and model weights without
retraining. The family definition, master labels and current rows supply
the features; construction records and reference master coefficients
remain outside the predictions. Rational coefficients at the fixed
public finite-field point supply cancellation features. Kira and Fermat
perform the actual row updates with symbolic rational coefficients.
The process holding the model remains available during one forward
solve, and it receives the initial matrix followed by each changed row.
A system with no allowed row updates does not load the model.

\subsection{Matched controls and measurements}
We use the same seven families with independent master bases and 99 targets as the
native comparison in Section~\ref{sec:cost-comparison}. They include three
one-loop box profiles, a one-loop bubble, triangle and tadpole, and a
two-loop propagator. All methods use the same restricted native seed
bounds, target components, preferred masters and symbolic output checks.

Four methods distinguish the learned choice from changes needed to
measure it. Stock Kira uses the installed solver. Instrumented Kira
retains that solver's forward algorithm and records its exact updates.
The deterministic control uses the largest repeated leading integral
defined above and selects a source by Kira's row-length and integral-order
rule. A stable row identifier selects its destination. The learned
method uses the same serial schedule and selects both rows from the
allowed pairs. This control separates the model's decisions from the
effect of the new schedule. Both methods return the triangular system
to Kira for normalization and back substitution.

Each method runs three times per family on the same node, with rotated
execution order and one computation thread. Complete elapsed time
includes preparation, inference, exact algebra, target combination and
coefficient verification. We also time the forward-elimination phase
directly inside Kira and record model loading separately. The diagnostic
quantity
\begin{equation}
 T_{\mathrm{fwd,load\ excluded}}
 =T_{\mathrm{fwd}}-T_{\mathrm{model\ load}}
\end{equation}
subtracts that recorded loading interval; it retains feature construction,
scoring, communication and exact row updates. It is a timing
decomposition of these runs; a separate run with a preloaded model
has not been measured. Ratios use three-repeat medians and the
paired geometric mean of Eq.~\eqref{eq:cost-ratio}. Forward-stage ratios
include only cases with actual row updates in both methods.
The tadpole batch needs no forward row updates and does not contribute
to those phase ratios.

For each committed update, we retain the convention
$1+2n_q$, where $n_q$ is the source-row nonzero count.
This counts coefficient-field operations and excludes the internal
polynomial work in rational simplification. Elapsed time includes that
work and the candidate trial updates used to prepare features.
The tests keep the action capacity at 10,000, the matrix capacity at
10,000 rows and 250,000 nonzeros, and use bounded time and memory.
These limits bound the systems and action sets tested here.

\subsection{Exact checks and measured results}
All @@TRIALS@@ final trials produced the prescribed symbolic master
coefficients. Independent evaluation of the archived native exports
passed @@CHECKS@@ checks of target coefficients at independent sample
points, and the saved row updates passed
@@ROWCHECKS@@ independent finite-field checks. The model made
@@CHOICES@@ choices across its repeated runs. In @@CHANGED@@ choices,
its source row had already changed in an earlier elimination.
These records establish that the model acted on an evolving identity
matrix~\cite{KiraLiveMatrixData}.

The complete elapsed-time ratios for the learned method were
@@STOCK@@ against stock Kira, @@NATIVE@@ against instrumented Kira,
and @@CONTROL@@ against the deterministic control. Within forward
elimination itself, the ratio against instrumented Kira was
@@FWD@@ over @@PAIRS@@ active family batches. After subtracting the
recorded model-loading interval, the ratio was @@READY@@.
For those active batches, the native forward-stage medians ranged from
@@NMIN@@ to @@NMAX@@ seconds, while the learned medians ranged from
@@MMIN@@ to @@MMAX@@ seconds.

Summing one median operation count per family gives @@OPML@@
coefficient operations for the learned method, @@OPNATIVE@@ for
instrumented Kira and @@OPCONTROL@@ for the deterministic control.
The corresponding learned and native row-update totals were
@@STEPSML@@ and @@STEPSNATIVE@@.
These sums count each family once, while the independent checks above
cover all repeated runs. Figures~\ref{fig:live-times}
and~\ref{fig:live-operations} show the family-level measurements.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/live_kira_times.pdf}
\caption{Complete checked reduction time and the forward-elimination
time measured inside Kira. Bars show three-repeat medians. The forward
panel uses a logarithmic time axis and separately shows the learned time
after subtracting the recorded model-loading interval. The tadpole
case has no row updates, so its forward time measures phase overhead.
Box A, B and C denote profiles 0173, 0633 and 0156, respectively.}
\label{fig:live-times}
\end{figure}
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figures/live_kira_operations.pdf}
\caption{Committed row updates and coefficient-field operations for the
same evolving matrices. Each update contributes $1+2n_q$ operations.
The count excludes candidate scoring and polynomial simplification,
whose costs remain in the time measurements.}
\label{fig:live-operations}
\end{figure}
\FloatBarrier

\subsection{Implications for the proposed reduction policy}
This experiment tests learned choices inside Kira's changing selected
IBP matrix. The measured cost includes the consequences of those choices
for later rows and for the final exact reduction. The current model
increases aggregate runtime, and its summed coefficient-operation count
also exceeds the native count. Excluding model loading does not produce
a forward-elimination speedup in this comparison.

Kira's native forward phase is already short for these selected systems.
The added feature construction and scoring therefore have a small
available time budget. The model was trained on target-row reductions
with fixed source identities, so its application to changing identity
rows also tests transfer beyond those training states. The results apply
to the stated one- and two-loop families and a forward policy that
preserves Kira's integral ordering. Larger independent multiloop systems, other admissible
pivot-column choices and learned back-substitution order remain outside
the present experiment.
"""
 (REPORT/"kira_live_matrix.tex").write_text(fill(section),encoding="utf-8")
 p=REPORT/"report.tex";text=p.read_text(encoding="utf-8")
 original_abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(original_abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 if r"\input{kira_live_matrix}" not in text:
  text=text.replace(r"\input{kira_comparison}",r"\input{kira_comparison}"+"\n"+r"\input{kira_live_matrix}")
 start=text.index(r"\section{Conclusion}");end=text.index(r"\clearpage",start)
 conclusion=r"""\section{Conclusion}
\label{sec:conclusion}
We constructed exact master-based integral data and tested learned
policies for seed selection and row reduction. The collection contains
17,100 family instances, 57,979 family-local master entries and
2,301,272 targets with recorded identities, seed sets and reduction
paths. These paths establish valid constructions and reference costs;
they do not establish globally minimal reductions.

On the 690,382 held-out targets, the seed model reached 96.318\%
$F_1$, and its predicted stored equations supplied complete master-span
reductions for 94.515\% of targets. The full candidate pool supplied a
sufficient fallback for all targets. The earlier sampled row test
reproduced reference coefficients for 99.988\% of targets and required
17.657 times the local rule's mean reduction time
\cite{SeedModelTestData,KiraSeedSufficiencyData,ReductionModelTestData}.

The 876 earlier cost-comparison trials all matched their exact master
coefficients. Learned seed filtering reduced supplied equations to
0.251 times the full-pool count, while Kira's selected-equation count
was 1.027 times the baseline. Complete and prepared-input time ratios
were 1.720 and 1.116. Target-row preprocessing gave corresponding
ratios of 1.719 and 1.205. Direct learned seed bounds gave ratios of
1.671 and 1.373 against restricted native Kira. These results include
prediction, exact algebra, checks and required fallback
\cite{KiraCostComparisonData}.

The additional @@TRIALS@@ trials place the frozen row policy inside
Kira's evolving selected IBP matrix. Every final reduction passed its
exact checks. The learned method took @@STOCK@@ times the complete
stock-Kira time and used @@OPML@@ committed coefficient operations
against @@OPNATIVE@@ for Kira's native policy. The forward-stage
time ratio remained @@READY@@ after subtracting recorded model
loading. The tested implementations increased aggregate runtime,
and this evolving-matrix policy also increased the summed
coefficient-operation count~\cite{KiraLiveMatrixData}.

The higher-loop collection varies mass profiles within restricted
coupled vacuum families, and all tested loop orders occur in training.
Native timing tests and the evolving-matrix experiment cover seven
independent-basis families at one and two loops. The current evidence
supports conclusions within these domains and the specified action
sets. Tests on larger independent multiloop systems and training on
their changing IBP matrices remain necessary to assess broader
performance.

"""
 text=text[:start]+fill(conclusion)+text[end:];p.write_text(text,encoding="utf-8")
 p=REPORT/"reduction_model.tex";t=p.read_text()
 t=t.replace("Performance on Kira's full\nevolving system will require a separate study with its admissible actions\nand ordering~\\cite{Kira3}.",
 """Section~\\ref{sec:live-matrix} tests the frozen policy on Kira's evolving
selected IBP matrix using admissible actions that retain its integral
ordering~\\cite{Kira3}. This test changes the inference states while retaining
the target-row training described here.""")
 p.write_text(t)
 p=REPORT/"kira_comparison.tex";t=p.read_text()
 t=t.replace("The row model acts on fixed source identities and target rows.",
 "The row comparison in this section acts on fixed source identities and target rows.\\nSection~\\\\ref{sec:live-matrix} extends the test to changing identity rows inside Kira.")
 # Normalize the inserted newline and TeX escape without changing earlier results.
 t=t.replace("rows.\\nSection~\\\\ref","rows.\nSection~\\ref")
 t=t.replace("A learned policy for every pivot of Kira's evolving matrix, general\nhigh-loop scattering families and finite-field reconstruction\nrequires further tests.",
 "General high-loop scattering families and finite-field reconstruction\nrequire further tests.")
 p.write_text(t)
 p=REPORT/"references.bib";t=p.read_text();key="@misc{KiraLiveMatrixData,"
 if key in t:t=t[:t.index(key)]
 t+=("\n"+key+"\n  author = {Saraswat, Rushil},\n"
     "  title = {Frozen Learned Row Choices Inside the Evolving Symbolic Matrix of {Kira}},\n"
     "  year = {2026},\n  howpublished = {\\href{https://github.com/NonHermitianMatrix/"
     "ML_for_Kira_Seeding_Reduction/tree/"+args.data_commit+
     "/Kira_comparison/live_matrix}{Source changes, frozen protocol, exact row records and repeated comparisons}}\n}\n")
 p.write_text(t)
 p=REPORT/"Makefile";t=p.read_text().replace("kira_comparison.tex references.bib",
     "kira_comparison.tex kira_live_matrix.tex references.bib");p.write_text(t)
 p=REPORT/"README.md";t=p.read_text();marker="<!-- live-matrix-comparison -->"
 if marker in t:t=t[:t.index(marker)]
 t=t.replace("It includes the new symbolic master-span sufficiency test in Kira and identifies the native equation-generation and total-cost comparisons still needed to assess a solver speedup.",
 "It includes the symbolic master-span sufficiency test, native equation-generation comparisons and evolving-matrix cost measurements.")
 t+="\n"+marker+"\nkira_live_matrix.tex describes 84 repeated trials with the frozen row model inside Kira's symbolic forward elimination. It compares stock Kira, instrumented Kira, the deterministic schedule control and the learned policy on seven independent-basis families and 99 targets. The new time and operation figures are live_kira_times.pdf and live_kira_operations.pdf. The data release is "+args.data_commit+". All final reductions passed their exact checks. The supplied abstract is unchanged.\n"
 p.write_text(t)
 (HERE/"report_values.json").write_text(json.dumps(vals,indent=2)+"\n")
 print(json.dumps(vals,indent=2),flush=True)
if __name__=="__main__":main()

