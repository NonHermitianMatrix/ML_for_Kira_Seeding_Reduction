"""Write the checked comparison into the paper and preserve the supplied abstract."""
from s01_common import *
import argparse,shutil,math,datetime
METHOD="\\section{Comparison with Kira}\n\\label{sec:cost-comparison}\nA useful learned choice must reduce the cost of obtaining the final\nmaster coefficients. The sufficiency test in\nSection~\\ref{sec:seed-kira-sufficiency} establishes which stored seed\nsets permit a reduction, while the preceding target-row test measures\nindividual reduction paths. We now compare complete symbolic reductions\nwith Kira's existing equation selection and seeding. The comparisons\nretain both trained models, the held-out families and the seed\nthreshold of one half. The candidate seed lists and prescribed\nmaster bases are inputs; their earlier construction is outside\nthe measured reduction costs.\n\n\\subsection{Targets, baselines and exact checks}\nWe use 19 held-out family instances: one restricted vacuum profile\nat each loop order from one through twelve, three box profiles,\nand one bubble, triangle, tadpole and two-loop propagator family.\nThe three box profiles represent the smallest, middle and largest\ncandidate-pool sizes in that domain. A fixed hash order selects the\nother profiles and the target expressions without consulting previous\nmodel outcomes. Nested batches contain 1, 4 and 16 targets, with\nbatches of 1 and 3 for the three-target tadpole family.\nThis gives 56 batch cases and 291 distinct targets.\nThe restricted vacuum profiles retain the dependent denominators\ndescribed in Section~\\ref{sec:higher-loop-generation}; their loop orders\ndo not represent the complexity of general multiloop scattering.\n\nFor the supplied-equation comparison, Kira receives the connected\npart of the complete stored source pool and applies its own\nequation selection, forward elimination and back substitution.\nThe learned seed method takes the union of the predicted seed sets\nfor the requested batch and supplies the corresponding stored\nIBP identities together with the same background identities.\nIf any target retains an integral outside the prescribed master\nbasis, the method reruns the batch with the complete pool.\nBoth attempts contribute to its cost. This comparison isolates\nselection from a common source library; generating that library\nis outside these timings.\n\nFor the row comparison, the learned model chooses source identities\nusing a fixed finite-field sample, while\nEq.~\\eqref{eq:reduction-action} updates the target coefficients\nsymbolically in $\\mathbb K=\\mathbb Q(\\boldsymbol x,d)$.\nKira then reduces any remaining terms. A second version applies the\nlocal rule from Section~\\ref{sec:reduction-test} through the same\nsymbolic procedure. This control identifies the cost of the learned\nchoice relative to the local choice. Both methods retain fixed\nsource identities and a changing target row, which is the procedure\ncovered by the training data.\n\nWe compare each final coefficient with its constructed rational\nreference and independently evaluate the coefficients and saved\nrow operations at three finite-field points. The physical master\ncoefficients remain present throughout this experiment.\nA reported completion therefore includes the full symbolic target\nexpansion and its checks. Each batch-method pair runs three times\non the same compute node, with the execution order rotated.\nKira and the model each use one computation thread. At most two\ntrials run concurrently on the cluster.\n\n\\subsection{Learned seed bounds in native Kira}\nThe seven families with independent propagator bases also permit\nnative Kira equation generation. Kira reduces the component integrals,\nand its exact algebra combines their results into the requested target\nexpressions. We record generation and reduction separately from this\nfinal combination. Native equation counts refer to the component\nreduction; the later combination has separate counts and contributes\nto every reported total time. For the default baseline, the seeding bounds are\none above the largest values of $r$ and $s$ among the target components\nand prescribed masters. The restricted baseline also bounds\n$n_{\\rm dot}$ one above its largest required value and uses Kira's\nsubsector truncation with $l=N-s_{\\max}$, where $N$ is the number\nof propagators. A third control sets $r$, $s$ and $n_{\\rm dot}$ directly to the\nlargest target/master values, uses the same subsector truncation,\nand falls back to the default bounds if needed. Both this control\nand the learned method reserve 60 seconds for the first native attempt\nand 100 seconds for its fallback, within the complete 180-second limit.\nThese fixed settings retain Kira's own symmetry\nhandling and equation selection~\\cite{Kira3}; they do not represent\nan exhaustive search over its settings.\n\nTo apply the seed model before native equation generation, let\n$\\widehat{\\mathcal S}_S$ be the predicted seeds in sector $S$.\nFor every nonempty set, we pass the bounds\n\\begin{equation}\n \\begin{aligned}\n r_S&=\\max_{\\boldsymbol\\sigma\\in\\widehat{\\mathcal S}_S}r(\\boldsymbol\\sigma),\n &s_S&=\\max_{\\boldsymbol\\sigma\\in\\widehat{\\mathcal S}_S}s(\\boldsymbol\\sigma),\\\\\n n_{{\\rm dot},S}\n &=\\max_{\\boldsymbol\\sigma\\in\\widehat{\\mathcal S}_S}\n           n_{\\rm dot}(\\boldsymbol\\sigma).\n \\end{aligned}\n \\label{eq:native-learned-bounds}\n\\end{equation}\nto Kira. These bounds enclose the selected seeds, and Kira can generate\nadditional seeds within the bounds and inherited subsectors.\nIts own generated and selected equation counts therefore measure\nthe resulting work. An incomplete first attempt triggers the default\nnative bounds. This direct comparison repeats all four native\nmethods on the largest fixed target batch in each of the seven\nfamilies, giving 99 distinct targets and 84 trials. The learned\nmethod uses the same model and threshold as the supplied-pool test.\n\n\\subsection{Measured cost and results}\nWe record the complete elapsed time from process start to a checked\nresult. It includes input loading, model loading, feature preparation,\ninference, exact algebra, any fallback, coefficient checks and output.\nWe also record the time with the family already loaded and the model\nready for use. This second quantity represents repeated use of prepared\ninputs; the complete process time retains the cost of starting the model.\nFor a matched case, we compare the median of the three repeats and\ndefine\n\\begin{equation}\n \\rho_T=\\frac{\\operatorname{median}T_{\\rm learned}}\n              {\\operatorname{median}T_{\\rm baseline}}.\n \\label{eq:cost-ratio}\n\\end{equation}\nThus $\\rho_T<1$ indicates a lower measured time for that case.\nAggregate ratios use the geometric mean of the paired case ratios.\nTrials that reach their time or memory limit remain in the completion\ncounts and are excluded from ratios that require two completed results.\n\nWe distinguish supplied equations, equations selected by Kira,\nlogged forward insertions and coefficient-field operations.\nFor a committed target-row step with $n_q$ nonzero source entries,\nthe last count is $1+2n_q$, as in\nSection~\\ref{sec:reduction-model}. Feature construction also performs\ntrial updates of candidate rows. These counts do not measure the\ninternal polynomial work needed to simplify a rational coefficient.\nRuntime includes that work. Memory is the largest sampled sum of\nresident process memory for the driver, Kira and its algebra process;\nthe sampling interval is 50 ms, and shared pages can contribute to\nmore than one process's count. Every trial has a 180-second limit,\na 1.5 GiB address-space limit per process and a 32 MiB scratch limit.\nThe comparisons use the existing symbolic Kira~3.1 build with Fermat.\nThey do not benchmark finite-field reconstruction.\n"

def comparison(data,baseline,policy):
 return next(c for c in data["comparisons"] if c["baseline"]==baseline and c["policy"]==policy)
def ratio_fields(c):
 return "%.3f"%c["cold_geomean_ratio"],"%.3f"%c["warm_geomean_ratio"]
def figure(name,caption,label):
 return "\n\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/"+name+".pdf}\n\\caption{"+caption+"}\n\\label{fig:"+label+"}\n\\end{figure}\n"
def replace_once(text,old,new):
 if new in text:return text
 assert text.count(old)==1,old[:100]
 return text.replace(old,new,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("data_commit");args=ap.parse_args()
 assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 a=read(HERE/"summary.json");b=read(HERE/"native_seed/summary.json");breakdown=read(HERE/"cost_breakdown.json")
 assert read(HERE/"validation.json")["passed"] and read(HERE/"native_seed/validation.json")["passed"]
 seed=comparison(a,"kira_pool","ml_seeds");row=comparison(a,"kira_pool","ml_reduction")
 local=comparison(a,"local_reduction","ml_reduction")
 native=comparison(b,"kira_native","ml_native_seeds");trim=comparison(b,"kira_native_trim","ml_native_seeds")
 tight=comparison(b,"kira_native_tight","ml_native_seeds")
 sc,sw=ratio_fields(seed);rc,rw=ratio_fields(row);lc,lw=ratio_fields(local)
 nc,nw=ratio_fields(native);tc,tw=ratio_fields(trim);xc,xw=ratio_fields(tight)
 def complete(data,policy):
  x=data["totals"][policy];return str(x["complete"])+"/"+str(x["trials"])
 pool=complete(a,"kira_pool");seed_done=complete(a,"ml_seeds");row_done=complete(a,"ml_reduction")
 local_done=complete(a,"local_reduction");native_done=complete(b,"ml_native_seeds")
 kdone=complete(b,"kira_native");tdone=complete(b,"kira_native_trim");xdone=complete(b,"kira_native_tight")
 cases={(c["case"],c["size"],c["policy"]):c for c in a["cases"]}
 op=[]
 for c in a["cases"]:
  if c["policy"]!="ml_reduction" or not c["all_complete"] or not c["preprocessor_all_complete"]:continue
  l=cases.get((c["case"],c["size"],"local_reduction"))
  if l and l["all_complete"] and l["preprocessor_all_complete"]:op.append((c,l))
 ops_model=sum(c["coefficient_field_operations"] for c,l in op);ops_local=sum(l["coefficient_field_operations"] for c,l in op)
 ops_ratio=ops_model/ops_local if ops_local else 1
 seedcases=[]
 for c in a["cases"]:
  if c["policy"]!="ml_seeds" or not c["all_complete"]:continue
  p=cases[c["case"],c["size"],"kira_pool"]
  if p["all_complete"]:seedcases.append((c,p))
 input_ratio=sum(c["source_equations"] for c,p in seedcases)/sum(p["source_equations"] for c,p in seedcases)
 selected_ratio=sum(c["selected_equations"] for c,p in seedcases)/sum(p["selected_equations"] for c,p in seedcases)
 row_complete=sum(c["policy"]=="ml_reduction" and c.get("preprocessor_all_complete",False) for c in a["cases"])
 local_complete=sum(c["policy"]=="local_reduction" and c.get("preprocessor_all_complete",False) for c in a["cases"])
 content=METHOD+fr"""
The main comparison contains {a['trials']} trials. The full stored-pool
baseline completed {pool}, learned seeds completed {seed_done},
learned rows completed {row_done}, and local-rule rows completed
{local_done}. On the {seed['pairs']} completed matched batch cases,
learned seed selection gave complete-process and prepared-input time
ratios of {sc} and {sw}, respectively. It used the full-pool fallback
in {a['totals']['ml_seeds']['fallback_trials']} trials.
Across those batches, its supplied source-equation count, including
fallback, was {input_ratio:.3f} times the baseline count, while the
number of equations selected by Kira was {selected_ratio:.3f} times
the baseline. The distinction shows how Kira's existing selection
changes the work left after an external seed choice.
The learned method had lower complete-process median time in
{seed['cold_faster']} of {seed['pairs']} batches and lower prepared-input
median time in {seed['warm_faster']} of {seed['pairs']} batches.

The learned row procedure gave time ratios of {rc} and {rw}
against the full stored-pool baseline over {row['pairs']} matched
cases. Its ratios against the local row rule were {lc} and {lw}.
Before the final Kira call, the learned row procedure completed every
target in {row_complete} of the 56 batches, while the local rule did
so in {local_complete}. Kira completed the remaining terms in the
other batches.
For the {len(op)} batch cases in which both row procedures themselves
finished all targets before the final Kira call, their summed
committed coefficient-operation counts were {int(ops_model):,} and
{int(ops_local):,}, giving a ratio of {ops_ratio:.3f}.
This comparison excludes paths that left part of the reduction to
Kira. The elapsed-time measurements retain all of that later work,
as well as candidate feature preparation and exact coefficient
simplification~\cite{{KiraCostComparisonData}}.

Kira's own equation selection removes much of the redundant input
in the full-pool baseline. The learned seed filter reduces the
supplied pool, and its measured complete cost includes the added
model work and every fallback. Both learned methods have aggregate
complete-process and prepared-input ratios above one in this
comparison. The row-operation ratio also exceeds one relative to the
local rule on the matched complete preprocessing paths. These results
identify added cost in the current implementations and give no
aggregate reduction in the stated time or committed-operation measures.

"""
 content+=figure("kira_comparison_time","Matched time ratios relative to Kira with the full stored source pool. Each point uses a batch's three-repeat median. The left panel includes process and model loading; the right panel uses prepared family inputs and a loaded model. Short solid lines show the median case ratio; the dashed line denotes equal time.","kira-cost-time")
 content+=figure("kira_comparison_equations","Supplied source equations and equations selected by Kira for identical batches. Learned-seed counts include any full-pool fallback. Squares identify batches with fallback, and the diagonal denotes equal counts.","kira-cost-equations")
 content+=figure("kira_comparison_memory_operations","Sampled summed resident-memory ratios and committed coefficient-operation counts. Memory ratios use the largest recorded peak within each three-repeat group. The operation panel compares only batches that both row procedures completely reduced before the final Kira call. These counts exclude polynomial simplification and candidate-scoring work.","kira-cost-memory")
 content+=fr"""
The direct native-seeding comparison completed {native_done} learned
trials, {kdone} default-baseline trials, {tdone} restricted-baseline
trials and {xdone} target-index-bound control trials. Learned bounds required a default-bound fallback in
{b['totals']['ml_native_seeds']['fallback_trials']} trials.
For the {native['pairs']} paired completed family batches, its
complete-process and prepared-input time ratios against default
native Kira were {nc} and {nw}. Against restricted native Kira,
the corresponding ratios were {tc} and {tw} over {trim['pairs']}
paired batches. Against the control that sets bounds directly from target
indices, the ratios were {xc} and {xw} over {tight['pairs']} paired batches.
These measurements include native equation
generation, exact reduction, target combination, coefficient checks
and any repeated attempt.
"""
 native_counts=breakdown["native"]["native_work"]
 content+=fr"""
The learned native method had lower complete-process median time
in {native['cold_faster']} of {native['pairs']} matched batches against
the default baseline, {trim['cold_faster']} of {trim['pairs']} against
the restricted baseline and {tight['cold_faster']} of {tight['pairs']}
against the target-index control. Across the completed paired batches,
the ratios of summed initial equation counts were
{native_counts['kira_native']['summed_initial_equation_ratio']:.3f},
{native_counts['kira_native_trim']['summed_initial_equation_ratio']:.3f}
and {native_counts['kira_native_tight']['summed_initial_equation_ratio']:.3f},
respectively. These counts include repeated attempts.
The learned bounds generate fewer equations than the stated default
bounds, and the restricted deterministic baseline generates still
fewer equations on these batches. The learned method has aggregate
complete-process and prepared-input time ratios above one against
all three native controls. Thus the current native integration adds
total cost under the tested settings.
"""
 content+=figure("kira_native_learned_seeds","Direct native-seeding comparison on the largest frozen batches in seven independent-basis families. Ratios compare learned sector bounds with the three stated native baselines. Equation counts sum the initial system sizes that Kira reports for each attempt; internal regeneration can perform additional work.","native-learned-cost")
 content+=figure("kira_comparison_native","The methods using stored identities compared with native component reduction at the same targets and master basis. Native timings include equation generation and exact combination of the component results. This comparison changes the available source representation as well as the external method, so it does not isolate the benefit of learning.","native-stored-cost")
 failures=read(HERE/"validation.json")["incomplete_trials"]+read(HERE/"native_seed/validation.json")["incomplete_trials"]
 content+=fr"""
Across both comparisons, {len(failures)} trials did not produce a
checked complete result within the stated bounds. Their outcomes
remain in the released records, and the paired timing ratios above
use only cases with three completed repeats for both methods.
The recorded limits and three-repeat design bound the interpretation
of small timing differences on the shared cluster.

These results describe the implemented policies and the stated
symbolic Kira settings. The stored-pool tests reuse previously
generated identities, and the native tests measure learned sector
bounds that can include seeds beyond the model's selected set.
The row model acts on fixed source identities and target rows.
A learned policy for every pivot of Kira's evolving matrix, general
high-loop scattering families and finite-field reconstruction
requires further tests. Reduced input counts alone do not establish
a speed improvement because equation selection, model execution,
exact simplification and fallback all contribute to the total cost.
\FloatBarrier
"""
 report=ROOT/"report";(report/"kira_comparison.tex").write_text(content,encoding="utf-8")
 for p in (HERE/"figures").glob("*.pdf"):shutil.copy2(p,report/"figures"/p.name)
 p=report/"report.tex";text=p.read_text(encoding="utf-8")
 before=text.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]
 assert hashlib.sha256(before.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 backup=ROOT/".tools/kira-comparison-publication/report_before.tex"
 if not backup.exists():backup.write_text(text,encoding="utf-8")
 old="""In a Kira integration, the seed model would act before equation
generation and the elimination model would act when the solver
selects a pivot. Kira would perform the selected algebraic operations.
The present experiments test seed-reference agreement, whether
the stored identities from the predicted seeds suffice for reductions
inside Kira, and reduction of a target coefficient row.
Native Kira equation generation and learned choices on its full
evolving matrix remain separate integration steps."""
 new="""The present experiments test seed-reference agreement, whether
the stored identities from the predicted seeds suffice inside Kira,
and reduction of a target coefficient row. We then compare complete
symbolic reductions with Kira's existing strategies. A native adapter
converts predicted seeds into sector bounds for equation generation,
while the row adapter applies exact symbolic target-row updates before
Kira finishes the reduction. Section~\\ref{sec:cost-comparison} measures
their costs. Learned choices on Kira's full evolving matrix require
a separate integration."""
 text=replace_once(text,old,new)
 text=text.replace("Extending this\nprocedure to Kira requires allowed choices that follow Kira's",
                   "Extending this\nprocedure to Kira's full evolving matrix requires choices that follow its")
 text=text.replace("Kira's existing\nfinite-field reconstruction would remain responsible for obtaining\nsymbolic coefficients in a later solver integration.",
                   "The comparison in Section~\\ref{sec:cost-comparison} measures\ncomplete symbolic reductions with the selected operations.")
 text=text.replace("Measurements of total runtime with native Kira seeding remain a later stage.",
                   "Section~\\ref{sec:cost-comparison} compares complete symbolic reductions, including native Kira seeding.")
 if "\\input{kira_comparison}" not in text:text=text.replace("\\input{reduction_test}","\\input{reduction_test}\n\\input{kira_comparison}")
 oldlast="""The constructed master expansions and checked reduction records
provide a basis for studying learned choices while retaining
explicit mathematical checks. The new Kira test establishes when
the predicted sets suffice within the stored equation pools and
checks the full-pool fallback for incomplete predictions.
Further integration must generate identities from the predicted
seeds through Kira's native family interface and assess the
elimination model on the evolving IBP system. Comparisons must
include feature preparation, model inference and exact algebra,
together with total time, equation counts and memory against Kira's
existing strategies, to determine whether the learned choices
accelerate reduction."""
 conclusion=fr"""The completed Kira comparison measured {a['trials']+b['trials']} bounded trials
with unchanged models and exact coefficient checks. Learned seed
selection from the stored pool gave complete-process and prepared-input
time ratios of {sc} and {sw} against the full-pool baseline;
the learned row procedure gave {rc} and {rw}. The direct native
seed-bound comparison gave ratios of {nc} and {nw} against the
stated default native bounds, {tc} and {tw} against the
restricted bounds, and {xc} and {xw} against the target-index control. These results include model overhead and fallback
and apply to the tested families and implementations.
Both current learned policies increased aggregate elapsed time in
their controlled comparisons. Equation-count reductions must therefore
be assessed together with the measured total cost~\cite{{KiraCostComparisonData}}.

The constructed master expansions and checked records provide a
basis for further tests of learned choices. The present row policy
uses fixed identities and a changing target row. Assessing learned
pivots on Kira's full evolving matrix and larger independent multiloop
families remains necessary before claiming general solver acceleration."""
 marked="%% Kira cost conclusion begin\n"+conclusion+"\n%% Kira cost conclusion end"
 if oldlast in text:text=text.replace(oldlast,marked)
 elif "%% Kira cost conclusion begin" in text:
  text=re.sub(r"%% Kira cost conclusion begin.*?%% Kira cost conclusion end",lambda m:marked,text,flags=re.S)
 else:raise ValueError("Unexpected conclusion text")
 assert text.split("\\begin{abstract}",1)[1].split("\\end{abstract}",1)[0]==before
 from zoneinfo import ZoneInfo
 date=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y").replace(" 0"," ")
 text=re.sub(r"\\date\{[^}]*\}",lambda m:"\\date{"+date+"}",text)
 p.write_text(text,encoding="utf-8")
 p=report/"seed_kira_test.tex";t=p.read_text()
 t=t.replace("Native Kira equation generation from predicted\nseeds and comparisons with its own seeding heuristics remain\nseparate tests.",
 "Section~\\ref{sec:cost-comparison} separately compares native Kira\nseeding through learned sector bounds with the stated native baselines.")
 p.write_text(t)
 p=report/"reduction_test.tex";t=p.read_text()
 sentence="Section~\\ref{sec:cost-comparison} then measures complete symbolic reductions with Kira, including model and fallback costs.\n"
 if sentence not in t:t=t.replace("\\FloatBarrier",sentence+"\\FloatBarrier")
 p.write_text(t)
 p=report/"Makefile";t=p.read_text()
 if "kira_comparison.tex" not in t:t=t.replace("reduction_test.tex references.bib","reduction_test.tex kira_comparison.tex references.bib")
 p.write_text(t)
 p=report/"references.bib";t=p.read_text(encoding="utf-8")
 entry=fr"""
@misc{{KiraCostComparisonData,
  author = {{Saraswat, Rushil}},
  title = {{Exact Reduction Costs with Learned Seeds, Learned Rows and Native Kira Baselines}},
  year = {{2026}},
  howpublished = {{\href{{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/{args.data_commit}/Kira_comparison}}{{Frozen cases, exact reductions, repeated costs and independent checks}}}}
}}
"""
 if "@misc{KiraCostComparisonData," not in t:t+=entry
 p.write_text(t,encoding="utf-8")
 p=report/"README.md";t=p.read_text(encoding="utf-8")
 if "<!-- kira-cost-comparison -->" not in t:
  t+="\n<!-- kira-cost-comparison -->\nkira_comparison.tex reports the complete symbolic cost comparison: 792 main trials in 19 held-out families and 84 direct native seed-bound trials in seven independent-basis families. The same frozen models, targets and prescribed master bases are used throughout. The five new comparison figures show complete and prepared-input time, equation counts, memory, committed row operations and native seeding. Both fallback and incomplete trials remain in the accounting. The report distinguishes stored identities from native generation and target-row preprocessing from full Kira pivot selection. The fixed data release is "+args.data_commit+". The supplied abstract remains unchanged.\n"
 p.write_text(t,encoding="utf-8")
 print(json.dumps(dict(report_written=True,abstract_preserved=True,data_commit=args.data_commit,
  seed_time_ratios=[sc,sw],row_time_ratios=[rc,rw],native_time_ratios=[nc,nw,tc,tw,xc,xw])))
if __name__=="__main__":main()
