# Reserved model tests

Each compressed JSON file records a complete calculation and its solver attempts.
The main comparison has 31 batches, four methods and five repetitions.
The methods are the previous native path, integrated native choices, the best fixed strategy, and the learned strategy.
Each batch also has an application that receives its master basis without target reference answers.
`summary.json` contains full-time ratios, exact checks, fallbacks and resource peaks.
`public_application_checks.json` records ten checks of the single-batch command.
`public_joint_checks.json` records ten checks of the joint-request command.
The `public_` records contain their full returned coefficients.
Cold process times are recorded separately and are not the main repeated-time comparison.

Read [the parent guide](../README.md) for commands and record fields.
The [joint-request folder](../request_batching/README.md) contains the separate batching comparison.

`public_best_checks.json` records ten checks of the standard joint command.
The `best_joint_` records contain its full returned coefficients.
This command uses the best fixed strategy from training.
The learned joint command remains available for comparison.
