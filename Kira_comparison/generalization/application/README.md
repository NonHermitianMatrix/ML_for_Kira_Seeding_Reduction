# Symbolic reduction application

s12_reduce.py in the parent folder accepts physical family definitions, indexed targets and a prescribed master list. It receives no target coefficients. Native choices are the default for the new domains; an explicit experimental flag tests the unchanged equation filter with native fallback.

freeze.json records the application source and ten fixed checks. Seven native applications and three explicitly requested experimental applications use the same family/target inputs as the comparison. verification.json compares their coefficients with the reference only after execution. The gzip files retain every attempt and the native input/output. This is an implementation check, not a new independent performance sample.

Run the entry point and scheduler wrapper as described in ../README.md. Generated output must stay in this study folder, on Hoffman and GitHub.
