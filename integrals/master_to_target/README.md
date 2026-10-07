# Master to target

The collection contains 17100 family instances, 57979 family-local master entries and 2301272 targets. It includes 2,247 one-loop families, 1,353 two-loop families and 1,350 families at each loop order from three through twelve.

master_integrals/ stores definitions and bases; target_integrals/ stores input targets; master_to_target/ stores exact master coefficients, IBP seeds, source identities, reverse constructions, elimination traces and operation counts. IDs join all three folders. training/ and testing/ are disjoint linked views; canonical data is stored once.

The latest 12,000 added families vary 1,000 new positive mass profiles across twelve loop orders, following the earlier additions of 1,100 and 3,000 families. Each is a restricted coupled vacuum integral. Massless powers equal one, and two to four distinct massive denominators share the sum of the loop momenta. Partial fractions and Euler IBP give an exact basis and reference reductions. These mass profiles share topology and do not establish coverage of general high-loop scattering families. See higher_loops/README.md and expansion_1000/README.md for equations, generation and checks.

Training contains 1610890 targets from 11963 families; testing contains 690382 targets from 5137 families. Related mass profiles stay in one split across loop orders. Existing assignments are preserved. Paths in model_split_summary.json and the split manifests define the current assignment. Reference seed sets and paths are sufficient; no optimality claim is made.

Each family subfolder keeps its own definitions or records. catalog.json lists paths and counts. Higher-loop families contain a README describing their restricted domain; historical initial and expanded collections retain their original detailed records.
