model.json contains the 233-node CART tree and feature definitions. weights.txt stores the same tree for native C++ inference. deployment.json stores validation-selected thresholds and routes; freeze.json records SHA-256 hashes before the first test. Probabilities estimate the native support-membership label. They are not calibrated probabilities of sufficiency or optimality.

The current restricted route is deployment_confirmed.json, frozen by confirmation_freeze.json before six fresh profiles were reduced. deployment.json remains the original broad-test route. Both use the same tree and weights.

Current use: s35_reduce.py reads deployment_final.json. deployment_verification.json checks agreement with measured successful arms. The equation model stays off when an earlier seed or row model is requested, because the measured composition was slower. Both original freezes and preceding configurations remain unchanged.
