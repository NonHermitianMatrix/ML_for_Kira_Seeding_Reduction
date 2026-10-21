# Final method compared with default Kira

This comparison uses the 20 connected native requests from the final 93-request collection.
It includes planar boxes, nonplanar boxes, massive sunrise integrals, and a three-loop vacuum.
It does not measure default Kira for the other 73 analytic requests.

The reference is .tools/kira/bin/kira, the original saved Kira 3.1 executable.
The reference generates its own equations and uses its default algorithms.
The final method uses triangle_reduction/s32_deploy.py with its frozen choices.
Both methods receive the same targets, physical values, and preferred master indices.
The reference receives no target coefficients.
Its positive, numerator, and extra-power bounds equal the respective target maxima plus one.
The positive bound also covers the supplied top sectors.
These required job inputs are explicit settings. They are not learned choices.
The driver removes project KIRA_ environment options before launching the original executable.

Each request starts a fresh process. The comparison uses three repetitions and one thread.
The middle repetition reverses request order and method order.
Timing includes startup, input reading, preparation, model use, algebra, output reading, and cleanup.
It also includes recovery inside the final method.
Independent references and coefficient checks remain outside both timers.
The outer monitor allows 60 seconds and 8 MiB of temporary reduction files per request.
Use one worker under the cluster scheduler with an 8 GiB memory reservation.
Keep the full project below its 10 GB limit.

## Code order

1. s00_original_runner.py writes the Kira job and reads its output. It derives from the saved native runner.
   Its stock action uses the original binary and removes all project KIRA_ options.
2. s01_request.py runs one reference or final-method request.
3. s02_compare.py loads protocol.json.gz, checks frozen sources, runs the comparisons, and checks coefficients.
4. s03_compare.sh schedules the comparison. Submit it from the repository root with qsub.
5. s04_report.py writes the report table and its compact evidence.
   Run it only after summary.json reports completion.

protocol.json.gz contains the inputs, preferred master indices, frozen file hashes, and limits.
results/ contains compressed records with exact outputs.
summary.json contains the matched times, completion counts, and failures.
paper_default_rows.tex and default_kira_data.json in report/ contain the published summary.
Use the original native-driver hash in the protocol to trace the adapter source.
The current method's model weights remain unchanged.

The first driver stopped when Kira removed a file during a storage scan.
initial_monitor_failure.txt and initial_protocol.json.gz preserve that setup failure.
The corrected driver uses the same race-tolerant scanner as the final application.
It retains all completed and unsuccessful measured requests.
The stored test requests were used before. This comparison changes the reference, not the training split.

The next setup run used a scheduler file-size limit below the unchanged native child limit.
It prevented native subprocess launch in both methods.
setup_failed_results/ and setup_failed_summary.json retain all 120 unsuccessful attempts.
The corrected scheduler permits the original 64 MiB per-file limit.
The outer monitor still enforces the 8 MiB total scratch limit.

The first valid measurements stopped at a timeout cleanup error.
interrupted_measurement.log and interrupted_protocol.json.gz retain that interruption.
The correction converts the descendant PID set to a list before cleanup.
Completed matched pairs remain valid and stay in results/.
The remaining pairs use the same inputs, models, and resource bounds.
Each pair runs on one node. Resumption can use another Intel Gold node.

The resumed allocation reserves 4 GiB and allows 8 GiB of virtual memory.
It overrides the scheduler template with -l h_rt=01:10:00,h_data=4G,h_vmem=8G,arch=intel-gold*.
The two box classes and sunrise use finite-field reconstruction with batches of eight evaluations.
The three-loop vacuum keeps the previously validated procedure.
The added learned arithmetic selector remains disabled.
