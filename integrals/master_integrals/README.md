# Master integrals

This folder contains all 9,678 stored master entries for all 1,000 families. It includes the original 16 bases and the 984 bases that were previously stored inside Expanded_Integrals archives.

A master integral is specified by its family and integer index vector:

$$
M_m=I_{\boldsymbol a^{(m)}},\qquad
I_{\boldsymbol a}=\prod_{k=1}^{L}\int\frac{d^d\ell_k}{i\pi^{d/2}}
\prod_{i=1}^{N}D_i^{-a_i}.
$$

Here $L$ is the number of loops, $N$ is the number of physical and auxiliary expressions, $D_i$ is the corresponding inverse propagator or auxiliary expression, and $d=4-2\epsilon$. The family definition supplies the loop momenta, masses and external scalar products. A negative index places its expression in the numerator.

For each family, families/<family>/masters.json lists the master IDs, index vectors, sectors and mass dimensions. masters.txt gives the same integral labels in text form, and definition.json specifies the family. These are symbolic basis definitions. Evaluating their numerical values or epsilon expansions remains a separate calculation.

basis_checks.tar.gz preserves the Kira configurations, discovery and expanded-range outputs, the check at a second point and prime, and the original generation records. All 1,000 bases passed three Kira calculations, giving 3,000 retained checks. Agreement establishes basis stability within the recorded ranges and samples.

The first seed bounds were r <= t_top+2, s <= 2 and n_dot <= 2. The expanded checks increased these bounds by one and enlarged the probe range. Here r is the sum of positive indices, s is minus the sum of negative indices, t_top is the number of physical propagators in the top sector, and n_dot is the number of extra denominator powers. The records retain the exact bounds and sample substitutions used for each family.

[catalog.json](catalog.json) covers every family. The corresponding targets are in [target_integrals](../target_integrals/README.md), and their coefficients and reduction steps are in [master_to_target](../master_to_target/README.md). Each reference reduction lists the master IDs that match the terms in its master expansion.

The collection contains 997 one-loop and three two-loop families. Counts are per family, and related lower-sector integrals can occur in several bases. The stored basis has the stated finite-domain validation; completeness for arbitrary integer indices requires further relations or an independent argument.

The bases use [Kira](https://arxiv.org/abs/1705.05610) and the settings described in the [project report](../../report/report.pdf). The original master-generation programs and toolchain records are preserved in ../master_to_target/generation_source.tar.gz under the historical Master_Integrals prefix.
