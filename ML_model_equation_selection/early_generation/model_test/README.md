# Frozen tests

summary.json contains all batch medians and profile-weighted comparisons. verification.json checks 288 workflows, including eight applications without reference target answers. plots/ contains standalone PDF figures. The methods, targets and repeats follow ../families_test.json and ../trained_model/freeze.json.

Load workflows through s04_workflows.read to resolve exact payloads in ../objects/. Each record includes every attempt, timing, log, native export and exact check. Training and routing stayed fixed during tests. See the parent README for timing exclusions and scope.
