# One-loop bubble with one massive line

These are symbolic master-integral definitions for the specified family. Numerical values and epsilon expansions are not calculated.

The denominators use $D_i=q_i^2-m_i^2+i0$, with the momenta and squared masses listed below. The dimension is $d=4-2\epsilon$.

- D1: momentum `k`, mass squared `m2`.
- D2: momentum `k-p`, mass squared `0`.

The scalar-product rules and assumptions are in [definition.json](definition.json). The listed top-level sectors include their subsectors.

Kira found 2 master integrals:

```text
bubble_one_mass[1,0]
bubble_one_mass[1,1]
```

All three validation runs returned this basis. Their exact inputs, sample points, primes and raw Kira output are in `validation/`.

The checks establish stability in the recorded domains. They do not prove completeness for every possible integer index or exceptional kinematic limit.
