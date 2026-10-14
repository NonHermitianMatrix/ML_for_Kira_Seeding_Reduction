# Execution logs

These text files record the scheduled development and test jobs.
`pilot.log` records the initial ordering and threshold probes.
`bounds.log` and `build.log` preserve the initial import and compiler failures.
`develop.log` and `develop_fixed.log` preserve earlier development runs.
`develop_expanded.log` contains the resumed collection with seven strategies and three timing repetitions.
`refit.log` records the final comparison of twelve fitted models before reserved testing.
`test_and_analysis.log` records the main tests, single-batch application checks and joint-request comparisons.
`joint_application.log` records the joint application checks, final plot and evidence audit.
Completed records permit a job to resume without repeating its finished calculations.
Read [the parent guide](../README.md) for commands and resource limits.

`test_resume.log` records completion after the plot API correction.
`joint_application_resume.log` records the successful follow-up joint checks.
`default_application.log` records checks of the best fixed training strategy.
The earlier plot and dependent-job failures remain in their original logs.
