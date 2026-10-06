# Master integrals

This folder contains every recorded master basis in the current collection: 12,967 family-local master entries across 2,100 families. A master that occurs in several families has a separate entry for each family, so this count does not mean 12,967 globally distinct functions.

Each families/<family-id>/ folder contains definition.json and masters.json. The definition specifies propagators, momenta, masses, kinematics and loop order. The basis specifies master IDs and their index vectors, normalization, reduction assumptions and validation status. The added vacuum families also contain masters.txt and a family README.

The collection has 997 one-loop families, 103 two-loop families and 100 families at each order from three through twelve. The added 1,100 families contain 3,289 master entries. These are restricted coupled vacuum integrals with fixed massless powers and two to four distinct massive denominators that carry the sum of the loop momenta. Analytic convolution, partial fractions and Euler IBP establish their bases. Their status is analytically_verified_restricted_basis.

[The catalog](../catalog.json) links each basis to its targets and reduction records. [The higher-loop method](../higher_loops/README.md) describes the mathematical domain and independent checks. Current training and testing assignments come from [the training manifest](../training/manifest.json) and [the testing manifest](../testing/manifest.json); historical labels within older records retain their original meaning.
