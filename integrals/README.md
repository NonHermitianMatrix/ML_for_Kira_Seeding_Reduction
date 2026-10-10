# Integral collection

The collection contains 17100 family instances, 57979 family-local master entries and 2301272 targets. It includes 2,247 one-loop families, 1,353 two-loop families and 1,350 families at each loop order from three through twelve.

master_integrals/ stores definitions and bases; target_integrals/ stores input targets; master_to_target/ stores exact master coefficients, IBP seeds, source identities, reverse constructions, elimination traces and operation counts. IDs join all three folders. training/ and testing/ are disjoint linked views; canonical data is stored once.

The latest 12,000 added families vary 1,000 new positive mass profiles across twelve loop orders, following the earlier additions of 1,100 and 3,000 families. Each is a restricted coupled vacuum integral. Massless powers equal one, and two to four distinct massive denominators share the sum of the loop momenta. Partial fractions and Euler IBP give an exact basis and reference reductions. These mass profiles share topology and do not establish coverage of general high-loop scattering families. See higher_loops/README.md and expansion_1000/README.md for equations, generation and checks.

Training contains 1610890 targets from 11963 families; testing contains 690382 targets from 5137 families. Related mass profiles stay in one split across loop orders. Existing assignments are preserved. Paths in model_split_summary.json and the split manifests define the current assignment. Reference seed sets and paths are sufficient; no optimality claim is made.

<!-- native-multiloop-results-begin -->
## Complete multiloop cost comparison

The fixed complete-generation experiment has 324 planned workflows, 324 measured workflows and 324 exact completions.

The selected seed policy's complete-time ratio to responsive stock Kira is 0.741945 (12 paired batches).

Seed-to-stock time ratios are 0.563457 for two-loop boxes, 1.265710 for three-loop vacua, 0.572691 for three-loop ladders. The aggregate seed time interval includes one; gains are specific to the tested family classes. The row-time interval also includes one.

The cost-trained row policy's complete-time ratio to instrumented native Kira is 1.007901 (12 paired batches); its forward coefficient-operation ratio is 1.003162 (12 paired batches).

These are paired, three-repeat comparisons at rational kinematics with symbolic d. Results include inference, native generation, exact algebra, verification and fallback. The common reference basis is prepared separately.

The independent audit passed. Family-level results and completion counts must accompany aggregate ratios; none establishes a universal speedup.

[Methods, raw evidence and outcomes](../Kira_comparison/multiloop_native/README.md). Original integral records and neural checkpoints remain unchanged.
<!-- native-multiloop-results-end -->
