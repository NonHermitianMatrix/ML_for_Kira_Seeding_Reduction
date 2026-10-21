# Auxiliary validation: target-dependent sparse seed regions

This worker precomputes the last two cases from the first nonplanar validation profile.
It uses the same frozen candidate boundaries and timing code.
It preserves every result and only fills absent main validation records.
Existing records keep priority.
No reserved target or timing enters this work.

Timing records from this worker are in `../supplementary_validation/`.
`promotion.json` lists completed records copied into the main validation set.
`s00_execution_snapshot.py` preserves the first helper version.
The corrected parent script reuses its completed timings and fixes record promotion.
The correction changes no seed boundary or measured reduction.
No reserved result enters validation.
