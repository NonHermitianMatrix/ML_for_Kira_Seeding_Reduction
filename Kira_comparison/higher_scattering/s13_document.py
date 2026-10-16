"""Write human-readable guides for the verification study and its evidence."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def update(p,title,text):
    begin='<!-- BEGIN HIGHER SCATTERING VERIFICATION -->';end='<!-- END HIGHER SCATTERING VERIFICATION -->'
    old=p.read_text() if p.exists() else ''
    part=begin+'\n\n## '+title+'\n\n'+text.strip()+'\n\n'+end+'\n'
    if begin in old:
        a=old.index(begin);b=old.index(end,a)+len(end);old=old[:a]+part.rstrip()+old[b:]
    else:old=old.rstrip()+'\n\n'+part
    p.write_text(old)
def main():
    d=json.loads((HERE/'summary.json').read_text());v=json.loads((HERE/'validation.json').read_text())
    text='''# Higher-loop scattering and component comparisons

This study checks where each model and exact method saves complete reduction time.
All existing model weights stay fixed.
The data remain on Hoffman and GitHub.
The local report contains only report sources, figures, and compact result summaries.

## Comparisons

The first comparison uses 14 batches from seven known graph structures.
It uses two new rational parameter profiles and three targets per batch.
Ten methods have three timing repetitions each.
The methods use the same targets, prescribed master basis, and two-core allocation.
The 420 reductions pass exact checks.
The first fixed controls use the settings selected from earlier training.

A further 96 comparisons disable only one learned decision at a time.
The control uses the fixed setting selected during the earlier validation.
Earlier stages remain the same in each pair.
These pairs isolate the added decision more closely than a comparison with a different complete strategy.

New scattering families are connected four-point ladders and boxes with bubble subgraphs.
The first probes use four, five, and six loops.
The protocol also includes a four-loop case with symbolic invariants.
That attempt has no retained measurement and is excluded from numerical results.
New native comparisons use three and four loops at separate rational profiles.
A follow-up uses a longer time allowance at another fresh profile.
A further check uses more memory reserved through the scheduler.
The native and learned methods use the same limits in each comparison.
The complete family definitions and target lists are in the protocol files.

The vacuum recurrence is outside the domain of these scattering families.
The complete strategy selectors return native choices for these unknown structures.
Separate transfer tests apply the frozen equation tree and row model.
The test does not change the production model selection rules.

## Initialization experiment

The original executable checks sectors containing positive auxiliary indices during initialization.
The optional patch restricts this step to declared top sectors and their subsectors.
It uses the original zero-sector criterion inside that domain.
It does not set omitted integrals to zero.
The report derives closure of the domain under IBP identities.
Seven earlier graph types pass exact coefficient comparisons before the new graph tests.
The experiment uses one family, no cut propagators, and no symbolic propagator powers.
The original executable and source remain unchanged.

The new executable is `.tools/kira-higher-scattering/kira`.
The option is `KIRA_RESTRICT_SECTOR_INIT=1`.
The patch is an experiment in this project, not a standard upstream option.
Unset the variable to use the original initialization in the same new executable.
The Kira source is covered by the upstream GPL license.
See `../../.tools/kira-source/COPYING` and the existing Kira build instructions.

## Code and execution order

Run scientific calculations in a scheduled job.
Run one scientific job at a time.
Use the existing Python environment and Kira build on Hoffman.
Do not replace a frozen model or a completed record.

1. Run `s00_cases.py` to write the first family definitions and protocol.
2. Submit `s02_job.sh s01_pilot.py` to run the bounded native probes.
3. Submit `s02_job.sh s03_ablation.py` with two slots for the 420 comparisons.
4. Submit `s02_job.sh s06_sector_test.py` after the first comparisons finish.
   This script calls `s04_build_sector_test.py` if the new binary is absent.
5. Submit `s02_job.sh s10_extended.py` for the longer follow-up.
6. Submit `s02_job.sh s11_choice_controls.py` for the 96 decision controls.
7. The memory follow-up uses `s16_memory_job.sh` with two slots.
8. Run `s07_analyze.py` and `s09_validate.py` to audit the completed records.

The user paused remaining repetitions before the new model redesign.
`pause.json` records that change of scope.
Do not run the old automatic finish script for the current publication.
The new model folder supplies the current analysis and report workflow.

Use `-pe shared 2 -l h_data=2G,h_vmem=4G` for jobs that can use two workers.
Use `-hold_jid JOB_ID` when submitting a dependent job.
Use a four-hour scheduler allowance for the longer follow-up.
The per-attempt limits still apply within that job.
The logs retain the actual submitted jobs and any failed attempts.

`s00_cases.py` completes and checks each family's scalar-product basis.
`s01_pilot.py` records native initialization and reduction limits.
`s02_job.sh` loads the environment and enforces process limits.
`s03_ablation.py` compares the ten frozen methods on matching targets.
`s04_build_sector_test.py` builds the optional initialization patch without replacing an earlier binary.
`s05_native_runner.py` is the generated bounded native driver for that binary.
`s06_sector_test.py` checks earlier coefficients and tests new scattering cases.
`s07_analyze.py` reads completed evidence and creates the summary and plot.
`s08_write_report.py` writes the scientific result sections and updates both documents.
`s09_validate.py` checks the scientific records, model identity, and report summaries.
`s10_extended.py` retains the short-limit failures and uses a longer allowance on fresh profiles.
`s11_choice_controls.py` changes one selector at a time to its frozen validation control.
`s12_finish.py` completes the missing symbolic probe, analysis, documentation, PDF builds, and checks.
`s13_document.py` writes these guides from the completed audit.
`s14_memory_followup.py` repeats the enlarged checks with a larger reserved memory allowance, then compares native and equation-model reductions.
`s15_memory_runner.py` is generated from the earlier driver with only memory limits changed.
`s16_memory_job.sh` reserves two slots with 4 GiB per slot and starts the memory follow-up.

## Records

Each `.json.gz` file contains compressed JSON.
Times use seconds. Memory and storage values use bytes.
The records include targets, decisions, exact coefficients, attempts, and stopping conditions.
Failed attempts remain in their records.
All failed attempts and retries contribute to the measured complete time.
A failed reference or failed enlarged-basis check supplies no complete-time speedup.
An output that only returns the targets as masters does not qualify as a nontrivial reduction.

The main table sums one median per batch.
Other saved ratios use geometric means and are identified in the summary.
Three repetitions do not establish a universal speed guarantee.
The one-off row probe in the extended test is a diagnostic, not a repeated timing estimate.
The models and caller are loaded before timing.
Offline reference construction, training, and later evidence archiving are outside the reduction timer.
Each solver attempt starts a fresh Kira process.

## Limits and restarts

`resource_plan.json` gives the combined storage bound.
The full project must remain below 10,000,000,000 bytes.
The study retains at most 16 MiB of files.
Each solver attempt uses a 32 MiB temporary-storage limit.
The initial address-space and resident-memory limits are 2,400 MiB and 2,100 MiB.
The memory follow-up raises these limits to 6,144 MiB and 5,200 MiB under its larger scheduler allocation.
The monitor stops an attempt when a sampled limit is reached.
The first pilot uses a smaller temporary-storage allowance.
The native driver reserves ten seconds of the requested time for checks and cleanup.
The short allowance is 120 seconds, and the follow-up allowance is 600 seconds.

The first symbolic pilot reached its artifact-size guard before its record could be saved.
The user paused the follow-up before the missing probe was repeated.
The unsaved trial is excluded from numerical results.
The earlier saved probes remain unchanged.

`summary.json` contains complete comparisons and failed cases.
`validation.json` records the final evidence audit.
The report copies are `higher_scattering_data.json` and `higher_scattering_validation.json`.
No speedup is assigned to an unfinished calculation.
The experiments cover specified families and targets, not every higher-loop scattering integral.
'''
    (HERE/'README.md').write_text(text)
    purposes={'development':'Initial bounded native probes. The records include time, memory, allocation, and family-size limits.',
      'logs':'Scheduler output and progress messages. These logs include incomplete attempts and the artifact-size guard.',
      'references':'Enlarged native reductions and independent larger-seed checks for the seven known graph types.',
      'ablation_test':'The 420 paired-workload timing records for the ten frozen methods.',
      'parity':'Exact comparisons between restricted initialization and the earlier native coefficient references.',
      'higher_references':'Native references and larger-seed checks for the new three-loop and four-loop scattering families.',
      'higher_test':'Completed short-allowance scattering comparisons and any failed test attempts.',
      'extended_references':'Fresh-profile reference attempts with the longer time allowance.',
      'extended_test':'Longer-allowance native, equation-filter, and shared-request comparisons. Row probes have one repetition.',
      'choice_control_test':'The 96 comparisons that disable only one enabled learned decision at a time.',
      'memory_references':'References and enlarged checks under the larger scheduler-reserved memory allowance. Reused earlier references are marked.',
      'memory_test':'Three completed native timings and two completed equation-model timings. The user paused the remaining work for model redesign. The unfinished attempt has no timing result.'}
    for name,purpose in purposes.items():
        p=HERE/name
        if p.exists():(p/'README.md').write_text('# '+name.replace('_',' ').capitalize()+'\n\n'+purpose+'\n\nRead the [study guide](../README.md) for the producer scripts, input definitions, units, and limits.\nDo not edit a completed record.\nUse the analysis script to read the compressed JSON files.\nFailed records remain part of the evidence.\n')
    shared='''The [component and higher-loop study](higher_scattering/README.md) tests each decision with matching targets and exact checks.
It preserves the earlier models and results.
It also records connected scattering tests, initialization costs, and incomplete calculations.
Read its summary for the measured contributions and tested domain.'''
    update(ROOT/'Kira_comparison/README.md','Component and higher-loop verification',shared)
    update(ROOT/'README.md','Component and higher-loop verification',shared.replace('(higher_scattering/','(Kira_comparison/higher_scattering/'))
    for model in ['ML_model_seed_selection','ML_model_equation_selection','ML_model_reduction','ML_model_workflow_selection']:
        update(ROOT/model/'README.md','Independent component checks',shared.replace('(higher_scattering/','(../Kira_comparison/higher_scattering/'))
    update(ROOT/'report/README.md','Component effects and higher-loop scattering','''`higher_scattering_results.tex` compares the methods on common targets and records the new scattering tests.
`higher_scattering_appendix.tex` defines the families and derives the initialization-domain restriction.
`higher_scattering_data.json` contains compact measured values.
`higher_scattering_validation.json` records the evidence audit.
The new section separates learned decisions, fixed strategies, shared requests, and the restricted vacuum recurrence.
It retains failed cases and gives no speedup for an unfinished calculation.
The initial editorial audit remains a record of the earlier language-only revision.
The current revision adds new scientific results.
Run the [study analysis](../Kira_comparison/higher_scattering/s07_analyze.py) before rebuilding its figure.
Run both report checks after building the PDFs.
The main paper and the current additions in the notes include the new results.''')
    p=ROOT/'report/README.md';s=p.read_text()
    s=s.replace('This revision changes no model, dataset, or measured result.','The October 14 editorial revision changed no model, dataset, or measured result. The October 15 verification adds the measurements described below.')
    p.write_text(s)
    update(ROOT/'report/paper_figures/README.md','Component comparison figure','''`component_ablation.pdf` compares complete strategies and separately disables one learned decision at a time.
The upper panel uses all fourteen target batches.
The lower panel uses the graph subset on which each model is enabled.
Each value divides sums of three-run batch medians.
The panels retain the equal-time reference and use separate readable axis ranges.
The source is `Kira_comparison/higher_scattering/s07_analyze.py`.
The figure gives measured changes on these batches, not a universal ML speedup.''')
    rules=ROOT/'rules.md'
    update(rules,'Component attribution and higher-loop verification (October 15, 2026)','''Verify defined higher-loop scattering families and compare the separate contributions of the models and reuse on matching physical targets.
Keep exact coefficient and basis checks, preserve failed cases, and count retries and prediction costs.
Distinguish learned decisions from fixed strategies, initialization changes, and mathematical reuse.
Revise the whole paper in clear, connected English so that its abstract, methods, results, and conclusion agree with the measured evidence.
Keep the notes, affected guides, cluster files, GitHub, and local report copy current under the existing resource rules.''')
    print(json.dumps(dict(documented=True,finished=v['finished_test_reductions'],failed=v['unsuccessful_test_reductions'])))
if __name__=='__main__':main()
