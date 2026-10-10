"""Maintain the integration and model guides from the retained run state."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def catalog(folder):
 lines=[]
 for p in sorted(folder.glob("s*")):
  if p.suffix not in [".py",".sh",".h",".cpp"]:continue
  first=p.read_text().splitlines()[0].strip('" /')
  if p.suffix==".sh":
   body=p.read_text();commands=[l for l in body.splitlines() if ".py" in l and not l.startswith("#")]
   first="Scheduler/build wrapper: "+"; ".join(commands) if commands else "Scheduler wrapper."
  lines.append("- "+p.name+": "+first)
 return "\n".join(lines)
def main():
 s=json.loads((HERE/"summary.json").read_text())
 t=json.loads((HERE/"pair_reserved_summary.json").read_text());c=t["comparisons"]
 assert s["outcomes"]["completed"]==560 and t["outcomes"]["completed"]==400
 result=f'The initial comparison completed all 560 workflows. A 400-workflow implementation confirmation on the same eight physical profiles also completed every target with exact reference agreement. In the confirmation, seed, row and combined complete-time ratios to the smaller native control are '+", ".join(f'{c[k]["complete_seconds"]["all"]["ratio"]:.6f}' for k in ["seed_over_small","row_over_small","combined_over_small"])+". The seed ratio for boxes is 0.963700; the aggregate row operation ratio is 0.985327, but its forward-stage time ratio is 1.041202. Neither model has a universal runtime advantage. Read summary.json and pair_reserved_summary.json for grouped intervals, topology results and all failed attempts."
 text="""# Integrated native reductions

This extension runs seed selection before native IBP generation and chooses source rows inside Kira's changing symbolic matrix. Earlier models and comparisons remain preserved. The seed checkpoint is unchanged; compiled_weights.bin is an export of its float32 parameters. The separate row policies are selected from complete native training trajectories.

"""+result+"""

families.json contains six training and three validation physical profiles, each with ordinary and deeper target batches. Related batches share a split. reserved_families.json defines eight new physical profiles and sixteen batches before any reserved timing. freeze.json fixes model files, code, binaries, configuration, thresholds and the five-repeat seven-method protocol. deployment.json records validation-selected settings and automatic method choices. The ladder topology has no new row-training or validation examples.

The models act on exact native IBP reductions over Q(d), with fixed rational kinematics and a prescribed master basis. They neither evaluate master integrals nor provide a generic multiscale or twelve-loop performance claim. Row actions select a source among equations with the same leading integral. The reported operation count is a committed coefficient-update proxy, not Fermat's internal polynomial work.

The common runtime uses bounded dependency-ordered back substitution, compute-node temporary storage and responsive process termination. Both learned and native controls receive these changes. The smaller native control starts at the target bounds and expands if necessary. Learned and deterministic seed subsets fall back to the whole smaller region, then the conservative region. Every attempt contributes to complete time. The native master check is followed by explicit exported-basis admission and exact coefficient comparison. basis_admission_fix.json explains the preserved development rejection; rejected_workflows/ retains its original evidence.

The production workflow includes preparation, model import/loading, prediction, native equation generation, exact reduction, reference comparison, fallback and cleanup. Interpreter launch, common references, shared integrity checks and lossless evidence compression lie outside its time boundary. Methods rotate in order on the same compute node within a profile. Summary intervals resample physical profiles, keeping related batches together.

Use the existing validated Hoffman toolchain and original Kira build under .tools/. s00_build.py applies the row and bounded-back-substitution patch to that build; s44_build_final.sh builds the initial s11_final_policy.h implementation. s67_build_pair.sh builds the current s14_pair_policy.h implementation and records its binary metadata. Seed s06_build_compiled.sh exports unchanged weights, builds the bounded C++ evaluator and checks parity. Tool executables and compiler caches remain outside Git. The final source patch and build metadata are retained here. Rebuilding in another environment creates new binary hashes and requires a new freeze; it does not alter the published frozen evidence.

s81_reduce.py is the integration entry point. Run it in a scheduled job with node TMPDIR, one arithmetic worker, the documented memory limit and an output path inside this experiment folder. Supply one family case JSON object, a batch size and a JSON list of prescribed master indices, or a JSON object with a masters field containing that list. Target reference coefficients are optional. The family object uses the same definition/targets/id/group/topology_group fields as families.json. Select --policy native, seed, row, both, or auto. Auto uses the rule fixed from validation and retains native execution for unknown input classes. The explicit model modes permit controlled transfer tests. It reports the applied policy and complete workflow record. The saved model probabilities express model preference; they are not calibrated guarantees.

A typical command in that bounded scheduled environment is:

    .tools/seed-model/venv/bin/python Kira_comparison/integrated_runtime/s81_reduce.py --family-file CASE.json --size 32 --masters-file MASTERS.json --output Kira_comparison/integrated_runtime/application/CASE.json.gz --policy auto

The interface calculates target coefficients from native exact IBP identities and row operations. It admits a result only when every target is reduced and each right-hand-side integral belongs to the prescribed basis; otherwise it expands the seed region. An optional --reference RECORD.json.gz replaces --masters-file and adds an independent coefficient comparison. The records distinguish native_exact_basis from reference_coefficients. Eight application checks provide only master indices to the reducer, then pass independent postrun coefficient comparisons. application_verification.json records these checks and source hashes. Basis discovery is separate preparation. Complete trials reuse no previous equation database. The application record includes input/routing and workflow time; evidence compression and optional release hash checks remain outside this boundary.

resource_plan.json and cache_resource_plan.json reserve at most 9,753,098,240 combined bytes, less than 10,000,000,000 combined project bytes, including local report copies, publication objects, caches and scratch. At most two production reductions use 128 MiB scratch each, or one reference uses 256 MiB. Solver address space is 2400 MiB and monitored solver-tree RSS is bounded at 2100 MiB. The retained cap covers this folder and both new model-runtime folders. Atomic shared records enforce that cap. Do not launch reference and production arrays together.

pair_freeze.json freezes the two-row implementation and the 400-workflow confirmation. pair_reserved_test/ repeats the original eight reserved profiles with five methods and five repetitions per batch; it adds no independent physical families. pair_summary.json records 144 validation workflows with unchanged decisions and exact outputs. cache_summary.json retains the rejected inverse-cache experiment. s79_run_application.py and s80_workflow_application.py implement optional-reference production use; s81_reduce.py is the current public entry point. application_checks/ retains the eight basis-only interface checks.\n\nshared/ stores content-addressed compressed fields; workflow_attempts/ retains every attempt. Use s03_records.read_record to restore a record. Validation folders preserve earlier alternatives, including rejected database settings and failed scheduling pilots. These results are not removed when a faster configuration is selected. s30_verify.py checks shared hashes, reparses exports independently, compares exact rational polynomials and audits workflow accounting.

The normal sequence is development/collection, fitting, parity checks, validation, freeze, sequential references, reserved tests, summary/audit, plots and report. s55_freeze_and_references.sh combines freeze and references for a fresh experiment. Existing frozen files and records are immutable; use a distinct experiment for another tuning cycle. s47_basis_admission.py is the retained one-time development migration and must not be reapplied to finished data.

## Script order

"""+catalog(HERE)+"\n"
 (HERE/"README.md").write_text(text)
 seed=ROOT/"ML_model_seed_selection/runtime_inference"
 (seed/"README.md").write_text("""# Seed inference for complete native reductions

This folder reuses the original trained neural checkpoint and supplies two equivalent feature/inference interfaces. s00_vector_seed.py computes unchanged features with bounded NumPy arrays. s02_seed_runtime.cpp and s04_compiled_seed.py implement the same float32 network through a small compiled library. compiled_export.json records the source checkpoint/configuration and compiled_weights.bin contains the exported parameters. No reserved examples retrain these weights.

parity.json records bitwise vector-feature and probability agreement. compiled_parity.json and compiled_threshold_parity.json check probability tolerance and identical seed masks on thirty-six development contexts. cold_benchmark.json includes imports, loading and inference in forty-eight fresh-process checks. The compiled arithmetic is slower when warm; reduced startup cost motivates its production use.

threshold_policy.json fits execution thresholds from ninety-six complete training workflows, including failed subsets and native fallback. It preserves the earlier classification test's threshold. The allowed execution thresholds are 0.003, 0.01, 0.03, 0.1, 0.3 and 0.5. Unknown classes use the frozen transfer threshold for explicit model tests. Auto deployment separately retains native execution for unvalidated classes.

The native candidate region is finite. Coverage retains target seeds, the prescribed masters, sector corners and the specified first neighbours. The model does not enumerate all integer seed indices. Full costs and independent physical tests are in Kira_comparison/integrated_runtime/. That folder's resource cap also covers these files.

## Script order

"""+catalog(seed)+"\n")
 row=ROOT/"ML_model_reduction/runtime_training"
 (row/"README.md").write_text("""# Row policies trained on native Kira cost

This folder contains separate lightweight row policies and preserves the earlier neural model and cost tree in their original directories. Native collection samples 2520 training and 1372 validation groups from six training and three validation physical profiles, with ordinary/deeper batches kept together. Twenty-four features include bounded modular estimates of symbolic cancellation. Modular values are heuristic features; exact Kira arithmetic and final coefficient checks determine accepted reductions.

s05_train.py fits immediate-time, coefficient-length and hybrid trees. s08_policy_candidates.py defines eighteen bounded linear candidates, and s09_select_trajectory.py ranks their full native training trajectories by committed forward operations. The trajectory_candidates/ folders hold each saved weight vector. trajectory_selection.json retains the training ranking and lineage. Subsequent validation chooses the final topology-specific policy; Kira_comparison/integrated_runtime/deployment.json is authoritative. Final test results never select weights.

s14_pair_policy.h applies the selected source inside Kira's current same-leading-integral row group. It computes only the features used by the sparse score, bounds modular parsing/caching and retains native behavior outside the supported group bounds. Its deterministic cancellation control receives the same optimization. In a two-row group, the alternative updates differ by a nonzero scalar, so cancellation features agree; the sparse score can sometimes retain the native source without computing those features. pair_summary.json records 144 validation workflows and 72 exact parity pairs: decision time ratio 0.344835 and forward time ratio 0.955232 compare the same learned policy with the shortcut disabled. The subsequent 400-workflow confirmation preserves the weights and decisions. These implementation ratios do not compare ML with native Kira. The additional modular-inverse cache failed its forward-stage adoption criterion and remains disabled. Choice traces include the selected source and normalized score confidence when tracing is enabled. Production timing disables detailed traces and retains aggregate operations and stage times.

Feature tests, full/shared-feature parity and sparse/full-policy parity remain preserved. Complete costs, references, all failed attempts, independent export checks and the comparison report reside in Kira_comparison/integrated_runtime/. The operation proxy excludes internal polynomial arithmetic and back substitution. Any speedup claim must use complete measured costs and the stated domain. The shared retained-data and memory caps apply.

## Script order

"""+catalog(row)+"\n")
 for name in ["README.md","Kira_comparison/README.md","ML_model_seed_selection/README.md","ML_model_reduction/README.md"]:
  p=ROOT/name;s=p.read_text();marker="<!-- integrated-runtime-current -->"
  if marker in s:s=s[:s.index(marker)]
  s+="\n"+marker+"\nThe current native-integration extension is in Kira_comparison/integrated_runtime/. It combines compiled seed inference, complete-trajectory row policies and matched native/deterministic controls. The model additions are in ML_model_seed_selection/runtime_inference/ and ML_model_reduction/runtime_training/. "+result+" Earlier data, checkpoints and tests remain preserved. See that folder's README for the integration entry point, exact checks, resources and reproducible execution order.\n"
  p.write_text(s)
if __name__=="__main__":main()
