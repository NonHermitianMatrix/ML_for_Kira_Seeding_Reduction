"""Write checked results and pin the report to the published data."""
import argparse,hashlib,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def replace_block(p,tag,text):
 old=p.read_text();start="<!-- "+tag+" -->";end="<!-- /"+tag+" -->"
 block=start+"\n"+text.strip()+"\n"+end
 if start in old:old=re.sub(re.escape(start)+r".*?"+re.escape(end),lambda m:block,old,flags=re.S)
 else:old+="\n\n"+block+"\n"
 p.write_text(old)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--data-commit");args=ap.parse_args()
 r=json.loads((HERE/"summary.json").read_text());v=r["verification"];certs=json.loads((HERE/"optimal_paths/summary.json").read_text())
 assert v["success"] and v["all_expanded_seed_checks_pass"] and r["certificates"]["success"]
 assert r["workflows"]==70 and all(c["joint_optimum"]["minimum_cost"]==7 for c in certs)
 short=(f'The extension contains seven new scattering batches with 88 targets and 70 exact comparison workflows. '
 f'It includes a nonplanar two-loop box, a one-loop pentagon with five independent symbolic invariants, and a one-loop box with an independent external virtuality. '
 f'The frozen equation filter has a complete-time ratio of {r["geometric_mean_learned_to_native"]:.6f} to native choices, including all 35 native fallbacks. '
 'The existing native guard remains active for these unsupported inputs. '
 'Separate exact certificates enumerate every sufficient source subset and every allowed pivot path for a bubble and a tadpole. Each has a joint minimum of seven counted coefficient operations, within its specified finite pool. '
 'These certificates do not prove unrestricted IBP or wall-time optimality.')
 readme=f"""# Scattering, symbolic kinematics and certified paths

{short}

## Contents and physical scope

- [scattering_families](scattering_families/) defines four numerical-profile batches on new nonplanar four-point and five-point graphs.
- [symbolic_kinematics](symbolic_kinematics/) defines three batches with all specified invariants symbolic. The fields are Q(d,s,t), Q(d,s12,s23,s34,s45,s51), and Q(d,s,t,q2). All internal scattering propagators are massless.
- [optimal_paths](optimal_paths/) contains exact source equations, seeds, master coefficients, complete state graphs, all sufficient source subsets, optimal paths, operation counts and independent certificates. These are two small one-loop systems, with three nonmaster columns each.
- references/ contains enlarged native reductions. model_test/ retains all 70 workflows, their failed attempts, exact coefficients, full native inputs, resource samples, solver logs, and independent larger-seed/specialization checks.
- development/ retains four feasibility pilots and the initial symbolic-name parsing failure. Symbolic feasibility pilots share some final targets but select neither a model nor a threshold.
- freeze.json fixes the case list, solver, model and timing sources before reserved timings. runner_provenance.json records the existing native adapter and the symbolic-invariant extension. summary.json and verification.json contain the checked results.

The nonplanar family is the massless limit of topo4 in the original Kira paper, arXiv:1705.05610. The pentagon has five massless external legs. The box virtuality q2 denotes (p1+p2-p3)^2, displayed as v in the report. The complete independent denominator ranks are nine, five and four. Numerical profiles and all target indices are in cases.json.

## Comparison and checks

The unchanged depth-twelve early equation tree uses threshold 0.01. Every comparison starts a fresh native Kira process inside an already running driver. Complete time includes input generation, model work, native IBP generation, exact symbolic algebra, coefficient comparisons, cleanup, every rejected attempt and fallback. Enlarged reference discovery, post-run audits, compression and figure generation lie outside this timer.

Both methods start at the target seed limits and use a common prescribed master basis. A failed learned attempt retries native equations; an incomplete native attempt uses a larger region. All 35 learned workflows needed the native fallback. No test result is used to fit or activate a new policy. Five alternating repetitions give a case-weighted geometric mean learned/native ratio of {r["geometric_mean_learned_to_native"]:.6f}. This is a transfer limit, with no new speedup claim.

The independent audit checks {v["exact_coefficient_pairs"]} coefficient pairs, including {v["unique_coefficient_pairs"]} distinct pairs, from raw native exports. All seven larger-seed checks agree, and fresh rational specializations of all three symbolic results agree with separately generated native reductions. Native Kira also confirms the six coefficients in the two certified systems. The mathematical certificates count rational-function operations; they do not measure Fermat polynomial work or runtime.

## Execution order

Run scientific commands only in scheduled jobs with node-local TMPDIR.

1. s00_native_run.py supplies the bounded native adapter; s01_cases.py defines the physical inputs and verifies independent scalar products.
2. Submit s03_job.sh prepare to create cases and run feasibility pilots. s02_study.py supplies prepare, pilot, freeze and test actions.
3. Submit s06_pipeline.sh after the pilot. It runs frozen comparisons, s04_optimal_paths.py and s05_verify_certificates.py.
4. Submit s09_audit_job.sh after comparisons. It runs s07_audit.py and s08_analyze.py for independent coefficient checks and a timing plot.
5. s11_finish.sh regenerates and verifies the final joint equation/pivot certificates, then refreshes the summary. The original fixed-pool certificates and code remain in optimal_paths/fixed_pool/.
6. Run s10_document.py to update READMEs. After publishing the data commit, use --data-commit COMMIT to update the LaTeX, bibliography and conclusion. Build with make -C report and synchronize the complete report locally.

Scientific records stay on Hoffman and GitHub. The report also stays locally. resource_plan.json gives a conservative combined ceiling of {9958476224:,} bytes, below the 10 GB limit. Each native attempt has a 150-second limit, a 2400 MiB address-space limit, a 2100 MiB sampled process-tree RSS limit and a 32 MiB scratch limit. Only one scientific job runs at once. The fresh storage audit found 8,676,072,960 allocated bytes remotely and 392,683,520 locally before this extension.
"""
 (HERE/"README.md").write_text(readme)
 (HERE/"scattering_families/README.md").write_text("""# Broader scattering families

families.json contains two rational profiles of a massless nonplanar two-loop four-point family and two profiles of a one-loop pentagon. Each batch has sixteen targets; d remains symbolic. The nonplanar propagator list follows the massless limit of topo4 in the original Kira paper. All target indices, scalar-product rules and rank checks are explicit.

../references/ contains bases and master expansions. ../model_test/ contains native and frozen-filter timings and exact source inputs. Match records through the case ID. These tests do not change the original integral collection or its training split. The frozen filter needs native fallback on each profile; the current application guard retains native decisions.

Run the numbered workflow in ../README.md. Preserve existing records and the resource limits.
""")
 (HERE/"symbolic_kinematics/README.md").write_text("""# Independent symbolic kinematics

families.json contains a nonplanar box in Q(d,s,t), a pentagon in Q(d,s12,s23,s34,s45,s51), and a one-loop box in Q(d,s,t,q2). Here q2 is the squared momentum of the one off-shell external leg. All internal masses are zero. No scale is replaced by one.

The native adapter now declares every invariant in Kira's kinematics input. Reference and test files in ../references/ and ../model_test/ retain exact symbolic coefficients, their masters and input files. ../verification.json records the symbols actually present, equality at larger seed bounds, and separate native checks after fresh rational specializations. Rational-function equality supplies the primary comparison.

The seven-batch timing study retains all failures and fallback costs. These finite target lists do not establish performance for arbitrary masses, higher numerator ranks, or general high-loop scattering. Use ../README.md for execution and resource limits.
""")
 (HERE/"optimal_paths/README.md").write_text("""# Certified optimal paths in finite physical IBP systems

massless_bubble.json.gz and massive_tadpole.json.gz contain original symbolic IBP rows, source seeds and operators, master coefficients, every reachable matrix, every permitted pivot and exact operation costs. summary.json records full-pool controls and the joint optimum after source-subset selection. verification.json records an independent symbolic replay. native_*.json.gz contains additional native Kira checks from physical denominators.

Each system has three nonmaster columns and one protected master. The bubble pool has four IBP rows; the tadpole has three. First choose any sufficient subset of this finite pool. Then choose any nonzero active pivot, normalize its row and eliminate its column from all other rows. A counted division applies to each nonzero nonpivot source coefficient when normalization is required; each nonpivot update counts one multiplication and one subtraction. Source selection, assignments, comparisons, structural pivot cancellation, polynomial internals and certificate-search time are excluded.

Every allowed path is included. Both joint minima are seven coefficient operations. With every original equation retained, the minima are thirteen for the bubble and seven for the tadpole. The fixed first-column/first-row control attains those full-pool minima, while the immediate-cost greedy control uses nine operations for the tadpole. The smallest sufficient subsets contain three equations, from two distinct bubble seeds or three tadpole seeds.

The proof checks all outgoing actions, every exact transition and the Bellman minimum at every state. It also enumerates all sufficient original-row subsets and checks the minimum over their roots. These are global minima for the stated finite action space and arithmetic objective. Additional identities, other master bases, other algebraic algorithms and wall-time optimality remain outside the proof.

s04_optimal_paths.py builds the certificates; s05_verify_certificates.py checks them independently. s07_audit.py compares both physical systems with native Kira. fixed_pool/ preserves the preliminary certificates and code from before source-subset optimization; those archived scripts document that version and are not the active entry points. The main scripts reside one directory above.
""")
 for file,link in [("README.md","Kira_comparison/generalization/"),("Kira_comparison/README.md","generalization/"),("ML_model_equation_selection/README.md","../Kira_comparison/generalization/")]:
  replace_block(ROOT/file,"generalization-results",short+f"\n\nCode, definitions, exact results and certificates: [{link}]({link}).")
 rules=ROOT/"rules.md";text=rules.read_text()
 tag="## Scattering, symbolic kinematics and optimality"
 if tag not in text:
  text+="\n\n"+tag+"\n\n- Extend the study to broader scattering families, independent symbolic kinematics and certified reduction paths. Keep new code, definitions, exact results, failures and READMEs on Hoffman and GitHub, and update and synchronize the report. State the tested physical domain. Optimality certificates must specify the finite source pool, protected masters, allowed operations and cost; a bounded certificate does not establish unrestricted IBP or wall-time optimality. Preserve the existing data, models, split assignments and resource limits.\n"
  rules.write_text(text)
 if not args.data_commit:return
 assert re.fullmatch("[0-9a-f]{40}",args.data_commit)
 transfer=(f'All seventy workflows reproduce the exact reference reductions. The independent audit checks {v["exact_coefficient_pairs"]:,} coefficient pairs, including {v["unique_coefficient_pairs"]} distinct pairs. All seven enlarged-seed checks and all three independent kinematic specializations agree. '
 f'The frozen filter requires native fallback in all thirty-five learned workflows. Its case-weighted geometric mean complete-time ratio to native choices is {r["geometric_mean_learned_to_native"]:.3f}, corresponding to {100*(r["geometric_mean_learned_to_native"]-1):.1f}\\% more time on these batches. '
 f'Summing one median per batch gives {r["total_case_median_native"]:.3f} seconds for the native control and {r["total_case_median_learned"]:.3f} seconds for the experimental route. This sum weights the work differently from the geometric mean.\n\n')
 names={"nonplanar_box_symbolic":"symbolic nonplanar box","pentagon_symbolic":"symbolic pentagon","one_mass_box_symbolic":"box with symbolic external virtuality"}
 for c in r["cases"]:
  if c["symbolic"]:
   transfer+=f'The {names[c["case"]]} has median times {c["native_seconds"]:.3f} and {c["learned_seconds"]:.3f} seconds for native and experimental reductions, respectively. '
 transfer+=f'The largest sampled process-tree memory in the comparison is {r["peak_rss_bytes"]/1024**2:.2f} MiB, and the largest sampled solver scratch space is {r["peak_scratch_bytes"]/1024**2:.2f} MiB. These measurements include the unsuccessful filtered attempts.'
 opts=[]
 for c in certs:
  jc=c["joint_optimum"];cv=next(x for x in r["certificates"]["systems"] if x["system"]==c["system"])
  name=c["system"].replace("_"," ")
  opts.append(f'The {name} certificate contains {c["states"]} distinct states and checks {cv["all_edges_verified"]} transitions. It covers {jc["complete_path_count"]} complete paths across {cv["sufficient_subsets_verified"]} sufficient source subsets. The minimum is {jc["minimum_cost"]} coefficient operations when initial equation selection is allowed, and {c["paths"]["optimal"]["cost"]} when the full source pool is retained.')
 optimum="\n\n".join(opts)+r"""

The fixed control chooses the first available nonmaster column and then
the first available source row. It attains the full-pool minima
of thirteen and seven operations. A control that minimizes only the
immediate step cost uses thirteen operations for the bubble and nine
for the tadpole. Thus immediate cost can give a larger complete
cost even in a three-column physical system.
The minimum sufficient equation count is three for each pool,
with two distinct bubble seeds and three tadpole seeds.
All exact state transitions and terminal coefficients pass
independent checks, and six native Kira master coefficients agree
with the two symbolic systems."""
 text=(HERE/"report_template.tex.in").read_text().replace("@TRANSFER_RESULTS@",transfer).replace("@OPTIMUM_RESULTS@",optimum)
 assert "@" not in text
 (ROOT/"report/generalization.tex").write_text(text)
 p=ROOT/"report/report.tex";text=p.read_text()
 abstract=text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]
 assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
 if r"\input{generalization}" not in text:text=text.replace("\\clearpage\n\\section{Conclusion}", "\\input{generalization}\n\n\\clearpage\n\\section{Conclusion}")
 text=text.replace(r"\date{October 10, 2026}",r"\date{October 12, 2026}")
 old="sets. General multiscale coefficients, broader high-loop families and\nglobally minimal reduction paths remain outside the demonstrated scope."
 new=r"""sets. Those native timing comparisons retain their fixed-kinematic scope.
Section~\ref{sec:generalization} extends the tests to new scattering
topologies and independent symbolic invariants and supplies finite
optimality certificates. General high-loop scattering and optimality
over unrestricted identity pools remain open."""
 assert old in text or new in text
 text=text.replace(old,new)
 conclusion=(r"\section{Conclusion}" in text)
 block=(r"\noindent The scattering extension adds new nonplanar four-point and five-point inputs and exact reductions with independent symbolic invariants. "
 f'All seventy comparison workflows pass, while the frozen equation filter requires native fallback in all thirty-five learned workflows and has complete-time ratio {r["geometric_mean_learned_to_native"]:.3f} to native choices. '
 r'The application therefore retains its existing native guard for these domains. '
 r'Separate complete certificates prove seven-operation minima for two small physical systems when equation-subset selection and the stated pivot actions are allowed. '
 r'The certificates cover finite source pools with three nonmaster columns; their costs and native coefficient checks provide exact reference labels without asserting a general minimum for scattering reductions~\cite{KiraGeneralizationData}.')
 start="% BEGIN GENERALIZATION CONCLUSION";end="% END GENERALIZATION CONCLUSION"
 if start in text:text=re.sub(re.escape(start)+r".*?"+re.escape(end),lambda m:start+"\n"+block+"\n"+end,text,flags=re.S)
 else:text=text.replace("\\clearpage\n\\renewcommand{\\refname}",start+"\n"+block+"\n"+end+"\n\n\\clearpage\n\\renewcommand{\\refname}")
 assert text.split(r"\begin{abstract}",1)[1].split(r"\end{abstract}",1)[0]==abstract
 p.write_text(text)
 p=ROOT/"report/Makefile";text=p.read_text()
 if "generalization.tex" not in text:text=text.replace("cumulative_speedup.tex references.bib","cumulative_speedup.tex generalization.tex references.bib")
 p.write_text(text)
 p=ROOT/"report/references.bib";text=p.read_text()
 if "@article{Bellman1952," not in text:text+=r"""
@article{Bellman1952,
 author = {Bellman, Richard},
 title = {On the Theory of Dynamic Programming},
 journal = {Proceedings of the National Academy of Sciences},
 volume = {38},
 number = {8},
 pages = {716--719},
 year = {1952},
 doi = {10.1073/pnas.38.8.716}
}
"""
 entry=(r"""@misc{KiraGeneralizationData,
 author = {Saraswat, Rushil},
 title = {Native scattering reductions with symbolic kinematics and certified finite IBP paths},
 year = {2026},
 howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/""" + args.data_commit +
 r"""/Kira_comparison/generalization}{Physical definitions, frozen comparisons, exact symbolic checks and complete finite certificates}}
}
""")
 if "@misc{KiraGeneralizationData," in text:text=re.sub(r"@misc\{KiraGeneralizationData,.*?\n\}\n",lambda m:entry,text,flags=re.S)
 else:text+="\n"+entry
 p.write_text(text)
 replace_block(ROOT/"report/README.md","generalization-report","generalization.tex adds new scattering families, independent symbolic invariants and finite optimality certificates. It records the frozen model's complete fallback costs and the seven-operation minima for the two specified source pools. The data citation is pinned to "+args.data_commit+". The original abstract and earlier results remain unchanged.")
 print(json.dumps(dict(report_written=True,data_commit=args.data_commit)))
if __name__=="__main__":main()
