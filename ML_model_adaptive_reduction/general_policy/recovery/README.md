# Recovery from an incomplete stored basis

`s20_prepare_resilient.py` in the parent folder is the revised preparation application.
Use its `--input` and `--output` arguments as described in the preparation guide.
It retains the learned seed choice and exact checks. If an earlier index basis is rejected even with expanded bounds, it discovers a basis without that constraint.
It also tries an expanded target check if smaller checks fail. The total request budget remains 110 seconds.
The original s14 application and its measurements remain unchanged.

Run `../s21_recovery.py initialize` to freeze the focused profile before measurements.
Run `../s21_recovery.py 0` and `../s21_recovery.py 1` as compute jobs after the preparation workers finish.
Run `../s21_recovery.py analyze` to check all repeated outputs and produce summary.json.
The models and basis cache come from preparation/ and refit/. No model is fitted on these six cases.
The comparison uses three methods and three repetitions for initially successful methods.
Failed requests stay in the summary. A paired ratio requires matching exact outputs and the same master-index set.

The first compact trial exposed a target-dependent basis mismatch: a basis checked for earlier targets can omit masters needed by a new batch. The revised application discards a rejected cached basis after expanded seeding also fails, rediscovers without that constraint, and checks the result. It also permits an expanded target check when smaller checks fail. All steps remain inside the same 110-second request budget. A focused follow-up uses six fresh requests at two through five loops and keeps the models and index cache fixed. All three repetitions complete on 6/6 requests with ML disabled, 6/6 with the neural model, and 6/6 with the cost-and-risk model. The neural model gives a ratio of 0.783 on 6 matched requests, with repeat interval [0.743,0.797], relative to the revised workflow without ML. The cost-and-risk model gives a ratio of 0.801 on 6 matched requests, with repeat interval [0.772,0.857], relative to the revised workflow without ML. The comparison passes 2,352 coefficient checks. It tests the recovery change on fresh parameters of selected structures and does not replace the broad trial.
