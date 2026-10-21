# Protocols

These files define the cases and configurations before their comparisons.
Read the parent guide for the profile divisions and execution order.
The training and test scripts consume these definitions.

Read [the parent guide](../README.md) for producers, readers, dependencies, and limits.

## Additional scripts

- [s00_initial_test_worker.py](s00_initial_test_worker.py): Reserved first-request comparisons with frozen models and exact checks.
- [s01_compatibility_initial.py](s01_compatibility_initial.py): Check the existing higher-loop native and analytic paths through the new API.
- [s02_initial_application_worker.py](s02_initial_application_worker.py): Check independent scaled requests, model guards, and fresh processes.
