"""Write human-readable guides for the final application and all evidence folders."""
from s00_tensor_common import *

def main():
 s=read(HERE/'fast_summary.json');m=read(HERE/'trained_model/fast_policy.json')
 text='''# Exact tensor reduction and learned identity order

Use this folder for the final combined application.
The new path reduces polynomial numerators in rational one-loop sectors.
It also reduces independent products of those sectors.
Other inputs use the preceding exact rules and native Kira seed model.

Run on a compute node from the project root:

```bash
.tools/seed-model/venv/bin/python ML_model_adaptive_reduction/tensor_reduction/s18_fast_runtime.py --case CASE.json --output ML_model_adaptive_reduction/tensor_reduction/requests/answer.json.gz --method integrated
```

Read fast_protocol.json.gz for complete input examples.
Each case contains a definition and an ordered list of target index vectors.
The definition lists loop and external momenta, propagator momenta and squared masses, scalar-product rules, and the number of physical propagators.
A negative index is a numerator power. A positive index is a denominator power.
The output gives exact coefficients, unit-sector indices, status, selected action, recurrence counts, and model use.
For independent loops, it gives component reductions whose product is the full result.
The unit sectors form a spanning set. Special kinematics can add further relations.
The code does not claim a minimum master set at every kinematic point.
For a product, each method keeps the component factors in its output.
The timing does not include expansion of every product of component masters.

Use --method all_fixed to disable request-dependent learned choices in this control.
For new tensor inputs, this selects the action with the lowest validation total.
For other inputs, it passes all_fixed to the preceding application.
The four explicit tensor actions are tensor_largest, tensor_smallest, powers_largest, and powers_smallest.
Use --method previous to delegate to the preceding application.
The benchmark starts that application directly to avoid charging it for the new wrapper.

## Exact conditions

The added rule accepts one loop with two through five complete scalar-product coordinates.
It requires N-1 external momenta for N coordinates and rational squared masses and scalar products.
At least one target must have a negative index.
Each index has absolute value at most eight. The total negative power and excess positive power are each at most six per target.
The rule rejects cuts, symbolic indices, missing invariants, and a required singular Gram or Cayley matrix.
A request can use at most 12,000 recurrence states and 200,000 accumulated numerator-expansion terms.
The first implementation limits its exact attempt to twelve seconds.
The final implementation uses the same limits and equations.
Both return unsupported requests to the preceding exact and native application.
The factored field accepts only the integer dimension shifts proved in the appendix.
It cancels those factors by exact rational polynomial division.

The formulas apply to one-loop sectors. The current code does not insert them into a coupled graph with other loop momenta as symbolic external vectors.
The high-loop tensor tests use independent products through thirteen loops.
The earlier connected tree rules remain available under their own conditions.
The native binary retains its index and resource limits.

## Model and checks

The model predicts complete cost for four orders of exact operations.
It does not predict coefficients.
The 22 inputs describe target powers, sector sizes, coordinate counts, and batch size.
Training uses 24 requests. Validation uses 12 separate family profiles.
The final model uses times from the factored arithmetic.
The first model and its test remain stored for comparison.
Each model has a fixed-action control, feature-range guard, and predicted-saving margin.
The final reserved collection has 44 requests with three repetitions per method.
It includes massive and mixed-mass tensor sectors, independent products, native boxes, and old exact vacuum cases.
Native box batches are absent from earlier fitting and reserved sets.
Whole tensor families have separate profiles across splits; some index patterns recur.
Reference coefficients enter checks only. The deployed application computes coefficients anew.

The timer includes process start, input read, recognition, model use, exact algebra, native retries, output, and exit.
Reference construction and external coefficient comparison are outside every timed application.
The eighteen-second benchmark deadline is the same for every method.
All failures stay in the records.
Timing ratios use only requests verified in all three repetitions by both compared methods.

## Scripts and order

- s00_tensor_common.py defines features, model choice, lazy prior imports, and storage limits.
- s01_tensor.py implements the first exact angular and signed IBP recurrence in a symbolic field.
- s02_runtime.py is the first combined application.
- s03_cases.py defines the one-loop families and fitting splits.
- s04_pilot.py compares six development cases with native Kira.
- s05_job.sh runs one bounded scheduler job with one CPU thread.
- s06_measure.py measures complete first-application costs and stops timed-out children.
- s07_collect.py collects first training and validation costs.
- s08_train.py fits the first cost model.
- s09_checks.py checks signed IBP residuals, coordinate changes, and rejected inputs.
- s10_prepare.py trains, checks, and freezes the first reserved protocol.
- s11_test.py measures one of two first-test partitions.
- s12_analyze.py computes completion counts and matched time ratios.
- s13_document.py writes the report, notes, bibliography addition, and plot.
- s14_guides.py writes these guides.
- s15_validate.py checks evidence and builds both documents.
- s16_rational.py implements exact arithmetic with factored dimension denominators.
- s17_fast_tensor.py uses the same physics recurrence with that arithmetic.
- s18_fast_runtime.py is the final application entry point.
- s19_fast_measure.py measures the final application and both preceding versions.
- s20_fast_collect.py collects fitting costs for the factored arithmetic.
- s21_fast_train.py fits its cost model and fixed control.
- s22_fast_checks.py compares rational arithmetic with symbolic arithmetic and native pilot outputs.
- s23_fast_prepare.py freezes a fresh final reserved collection.
- s24_fast_test.py measures one of two final-test partitions.
- s25_fast_analyze.py separates arithmetic, model, and preceding-application comparisons.
- s26_finish.py runs both analyses, writes documents and guides, and validates them.
- s27_output_budget.py writes final transient records with a concurrency-safe storage check.

Run s04_pilot.py first.
Run s07_collect.py 0 and s07_collect.py 1 as two scheduler jobs.
After both finish, run s10_prepare.py, then the two s11_test.py workers.
Run s22_fast_checks.py before the two s20_fast_collect.py workers.
After both finish, run s23_fast_prepare.py, then the two s24_fast_test.py workers.
Run s26_finish.py after both final workers finish.
Keep completed evidence before repeating an experiment.
Use at most two native workers at one time.

## Storage and reproduction

resource_plan.json bounds the combined local and remote project allocation below 10,000,000,000 bytes.
The permanent study limit is six MiB. The flat request directory has a separate two MiB limit.
Each saved compressed record is below one MiB.
The native scratch allowance is 32 MiB per worker, within the combined reserve.
The scheduler limits memory, uses one arithmetic thread, and disables core files.
Keep generated data and weights on Hoffman and GitHub only.
Copy the complete report folder to the local machine after publication.

protocol.json.gz and fast_protocol.json.gz fix the cases, model identities, source identities, limits, and repetitions before each test.
summary.json and fast_summary.json give the first and final measurements.
development_checks.json and fast_arithmetic_checks.json give the additional exact checks.
The report derives the physics in tensor_reduction_appendix.tex.
The logs folder contains scheduler logs on Hoffman; GitHub stores its guide and the structured results.
'''
 text+=f"\nThe final application completes {s['all']['new_completed']} of {len(s['rows'])} requests in every repetition. The new identity-order model is {'enabled' if m['enabled'] else 'disabled'} by validation. Read fast_summary.json for the separate fixed-choice comparison and its uncertainty.\n"
 (HERE/'README.md').write_text(text)
 folders={'development':'Six native pilot reductions and all exact action outputs. These cases precede model fitting.','training':'First-implementation training requests, feature vectors, exact references, costs, and outcomes.','validation':'First-implementation validation requests and repeated costs. These records select the first model.','fast_training':'Training costs with factored dimension arithmetic. Original symbolic-field coefficients supply the check.','fast_validation':'Separate validation costs for the final arithmetic and model.','trained_model':'First and final learned trees, fixed actions, feature ranges, and candidate-selection results. policy.json is the first model; fast_policy.json is the final model.','model_test':'First frozen reserved test. Each file stores all timing repetitions, completion flags, statuses, and last-repetition exact outputs.','final_test':'Fresh final reserved test with integrated, all_fixed, first, and previous controls. It stores every outcome, including failures.','requests':'Temporary bounded input and output files only. Completed experiments leave this folder empty except for this guide.','logs':'Scheduler logs on Hoffman. jobs.json records submitted jobs. GitHub stores structured evidence and this guide; local failure logs remain on Hoffman.'}
 for name,desc in folders.items():
  q=HERE/name;q.mkdir(exist_ok=True);(q/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+desc+'\n\nRead ../README.md for the execution order, input format, resource limits, and checks.\n')
 addition='''## Current tensor reduction extension

Use [tensor_reduction](ML_model_adaptive_reduction/tensor_reduction/README.md) for the current combined application.
Its s18_fast_runtime.py adds exact polynomial-numerator reduction with factored dimension denominators.
A measured validation rule selects whether to use the trained identity-order policy or its fixed action.
It retains the previous exact rules and native seed model.
The new tensor high-loop tests use independent products; the report states the connected and factorized domains separately.
Read the folder guide for costs, controls, limits, and commands.

'''
 for q in [ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md']:
  z=q.read_text();block=addition if q.parent==ROOT else addition.replace('ML_model_adaptive_reduction/tensor_reduction/','tensor_reduction/')
  if '## Current tensor reduction extension' not in z:
   i=z.find('\n');z=z[:i+1]+'\n'+block+z[i+1:]
  q.write_text(z)
 q=ROOT/'report/README.md';z=q.read_text();addition='''\nThe current tensor extension appears in tensor_reduction_results.tex and tensor_reduction_appendix.tex.
The appendix derives angular moments, signed-index IBP, and arithmetic with factored dimension poles.
Matching notes files preserve the same derivation and evidence.
The compact data file is tensor_reduction_data.json.
The structured coefficient outputs and model weights stay in the cluster study folder and GitHub.
'''
 if 'The current tensor extension appears' not in z:q.write_text(z.rstrip()+'\n'+addition)
 for q in [HERE/'README.md',ROOT/'README.md',ROOT/'ML_model_adaptive_reduction/README.md',ROOT/'report/README.md']:
  q.write_text(''.join(x.rstrip()+'\n' for x in q.read_text().splitlines()).rstrip('\n')+'\n')
 print('Updated tensor and project guides.',flush=True)
if __name__=='__main__':main()
