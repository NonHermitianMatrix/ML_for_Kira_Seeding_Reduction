# References

Exact reference reductions and checks with a larger numerator bound.
Read [the parent guide](../README.md) for commands, limits, and the full method.

Each compressed JSON record stores a request, its timing, and its exact result.
Training and test records include every recovery attempt.
A reference record stores the common basis and comparison coefficients.
The runtime reads compressed records without keeping an uncompressed copy.
Completion files mark finished stages.
Exclusion records retain failed reference checks.
Equivalent training configurations can point to the same measured record.
Such aliases carry the field `identical_configuration_from`.
They are not extra timing measurements.
