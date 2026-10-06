# Integral collection

The collection contains 2100 family instances, 12967 family-local master entries and 381272 targets. It includes 997 one-loop families, 103 two-loop families and 100 families at each loop order from three through twelve.

master_integrals/ stores definitions and bases; target_integrals/ stores input targets; master_to_target/ stores exact master coefficients, IBP seeds, source identities, reverse constructions, elimination traces and operation counts. IDs join all three folders. training/ and testing/ are disjoint linked views; canonical data is stored once.

The added 1,100 families vary 100 positive mass profiles across eleven loop orders. Each is a restricted coupled vacuum integral. Massless powers equal one, and two to four distinct massive denominators share the sum of the loop momenta. Partial fractions and Euler IBP give an exact basis and reference reductions. These mass profiles share topology and do not establish coverage of general high-loop scattering families. See higher_loops/README.md for equations, generation and checks.

Training contains 266890 targets from 1463 families; testing contains 114382 targets from 637 families. Related mass profiles stay in one split across loop orders. Existing assignments are preserved. Paths in model_split_summary.json and the split manifests define the current assignment. Reference seed sets and paths are sufficient; no optimality claim is made.

The collection contains 85,732 individual integrals and 295,540 integral expressions. Master counts are family-local entries; some entries represent the same lower-sector integral in different families.

The original s00_reorganize.py and s03_run_reorganization.sh preserve the earlier folder migration. s01_read_data.py reads canonical records. s02_validate.py and s04_run_validation.sh run the current collection audit, and s05_prepare_model_splits.py maintains separate linked model views. New generation, mathematical validation, training finalization and report updates use the documented sequence in [higher_loops](higher_loops/README.md).
