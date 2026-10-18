# Optional basis interface checks

`s23_check_optional_basis.py` calls the public `s22_reduce.py` application. It supplies a family and targets, with no basis or reference coefficients.
It checks a scalar twelve-loop case against the independent recurrence output and a native case against the recorded recovery result.
The reference coefficients enter only the comparison after the application exits. These are interface checks, not a new timing benchmark.
Read the main general_policy guide for commands and limits.
