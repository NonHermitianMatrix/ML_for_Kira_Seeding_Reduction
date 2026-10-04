# From master integrals to target integrals

This folder constructs targets from the symbolic bases in [Master_Integrals](../Master_Integrals/README.md). It contains the code, generated examples, source identities and exact reference reductions. The examples cover the existing one-loop and two-loop families. Model training belongs to a later stage.

## Completed collection

The validated collection contains 1,662 targets across 16 families: 309 individual integrals and 1,353 integral expressions. The split contains 1,290 training examples, 185 validation examples and 187 test examples. [catalog.json](catalog.json) gives the per-family counts and sample points.

The validator checked every target and all 5,138 recorded elimination steps with exact rational functions and three finite-field samples. It rederived 55,654 source equations and checked 2,699 used IBP equations by independent differentiation. [validation_summary.json](validation_summary.json) records the completed checks.

The held-out validation examples are integral expressions. The test collection contains one individual integral and 186 expressions. A study restricted to individual-integral generalization will require additional held-out constructions.

## Construction from the masters

For each defined family, we use

$$
I_{\boldsymbol a}(\boldsymbol x,d)
=\prod_{k=1}^{L}\int\frac{\mathrm d^d\ell_k}{\mathrm i\pi^{d/2}}
\prod_{i=1}^{N}D_i^{-a_i},
\qquad D_i=q_i^2-m_i^2+\mathrm i0,\qquad d=4-2\epsilon.
$$

Here $L$ is the number of loops, $N$ is the number of physical and auxiliary expressions, and $\boldsymbol a$ contains their integer powers. The family fixes the momenta, masses and external scalar products. Negative indices supply numerator factors. The auxiliary sunrise indices remain nonpositive.

We initialize each master $M_m$ with its unit coefficient vector and derive source equations from

$$
0=\int_\ell\frac{\partial}{\partial\ell_k^\mu}
\left(v^\mu\prod_iD_i^{-a_i}\right).
$$

Each equation retains its seed, differentiated loop momentum and vector $v$. The vectors include loop momenta, external momenta and propagator momenta. The records specify how each propagator momentum combines the canonical loop and external vectors, so its equation can also be obtained from the canonical IBP equations at that seed.

The code also derives symmetry identities from explicit changes of loop variables with determinant $+1$ or $-1$. It accepts a transformation only when every inverse propagator maps to another with the same squared mass and an allowed index position.

We construct two kinds of examples. For an individual integral, a relation with one remaining unknown gives

$$
h_0 I_{\boldsymbol b}+\sum_jh_j I_{\boldsymbol a^{(j)}}=0,
\qquad
C_{\boldsymbol b m}
=-\sum_j\frac{h_j}{h_0}C_{\boldsymbol a^{(j)}m}.
$$

We accept the step when the other integrals already have exact master expansions and $h_0\ne0$. Repeating these steps constructs further integrals from the masters. Some steps prove that an integral vanishes; we retain these proofs as dependencies. The target collection contains nonzero examples with complete reductions. This initial implementation uses identities that close in this way and leaves unresolved coupled systems for later work.

For an integral expression, we select a subset of masters and form

$$
\mathcal T_0=\sum_m c_m(\boldsymbol x,d)M_m.
$$

If the current expression contains $w_{\boldsymbol a}I_{\boldsymbol a}$, we choose a source identity $R=\sum_{\boldsymbol b}r_{\boldsymbol b}I_{\boldsymbol b}=0$, with $r_{\boldsymbol a}\ne0$, and set

$$
\mathcal T_{n+1}
=\mathcal T_n-\frac{w_{\boldsymbol a}}{r_{\boldsymbol a}}R.
$$

This cancels the chosen term and introduces other family integrals while preserving the known master expansion. We require the identity to introduce a new leading nonmaster integral, so reversing the steps gives an ordered elimination path. If the expression contains one integral, we divide by its coefficient and store a normalized individual target.

The kind field distinguishes individual integrals from expressions containing several index vectors. An identity establishes the relation of every accepted target to its masters.

## Coefficients and numerical samples

We retain exact rational functions of $d$, squared masses and external momentum invariants. Initial expression weights include constants and rational functions. Powers of a nonzero squared-mass or momentum-invariant scale balance the mass dimensions of different masters:

$$
[\mathcal T]_{\rm mass}=Ld-2A,\qquad
[c_m]_{\rm mass}=2\left(\sum_i a_i^{(m)}-A\right).
$$

Here $A$ sets the target dimension and $\boldsymbol a^{(m)}$ is the master index vector. Generation and validation check coefficient homogeneity.

For numerical elimination, we substitute parameter values into these same functions and work modulo a prime. The first of three points supplies the stored model inputs; the other two provide separate checks. [catalog.json](catalog.json) lists all primes and assignments. Each family uses its own parameters and preserves its specified zeros and equal masses. All required denominators remain nonzero at the samples.

These numbers are exact finite-field values of the symbolic coefficients. The integrals remain symbolic. The construction requires no numerical integration or rational-function reconstruction.

## Seeds and elimination records

The candidate set contains all allowed seeds in nonempty physical sectors within

$$
r\leq t_{\rm top}+2,\qquad s\leq2,\qquad n_{\rm dot}\leq2.
$$

Here $t_{\rm top}$ is the number of top-sector physical propagators, $r$ is the sum of positive indices, $s$ is minus the sum of negative indices, and $n_{\rm dot}=r-t$, where $t$ is the number of positive indices. Identities can introduce integrals beyond these seed limits.

We fix the candidate set before constructing targets. Reference solutions identify sufficient seed subsets and any symmetry relations. Absence from a recorded subset does not prove that a seed is useless.

The reference order protects the chosen masters from elimination. It orders other integrals by sector number, extra denominator powers, numerator powers, sum of positive indices and the index vector. Each step eliminates the largest remaining nonmaster in the target row. The available pivots are all retained source equations with that leading integral.

Each trace applies the row operation

$$
T_{\boldsymbol b}\leftarrow T_{\boldsymbol b}
-\frac{T_{\boldsymbol a}}{R_{\boldsymbol a}}R_{\boldsymbol b},
$$

where $R$ is the selected source row and $\boldsymbol a$ is its leading integral. Source rows stay available. We retain the target row before and after the step, available pivots, selected equation and integral, multiplier, changes in nonzero entries and operation counts.

The generator obtains these target-row elimination traces from the mathematical identities under the stated reference order. Applying a model within Kira will require matching its available choices and state.

We count one finite-field division per step and one multiplication and subtraction per source-row term. These counts exclude identity generation, forming combined IBP operators, symbolic simplification, model inference and reconstruction. Each sequence is a known valid reduction; no minimum seed count or operation count is claimed.

## Data for the two models

Each family directory contains:

- definition.json: propagators, masses, scalar products and assumptions.
- candidate_seeds.json: candidate indices and their bounds.
- symmetries.json: loop-variable transformations and denominator permutations.
- identities.jsonl: equations, seeds, operators, exact coefficients and numerical coefficients.
- construction_proofs.jsonl: constructions of individual integrals and zero-integral dependencies from the masters.
- inputs.jsonl: targets, index features, dimensions, family, split and numerical target rows.
- references.jsonl: exact master expansions, construction histories, sufficient seeds, source equations, operation counts and three-point checks.
- elimination_traces.jsonl: row states, available pivots and recorded actions.
- summary.json and validation.json: counts, generation limits and checks.

Each JSONL line contains one record. Matching target IDs connect inputs, references and traces. Paths in an input record are relative to its family directory.

For seed selection, use the family, basis definition, candidate indices and target information as inputs. The reference seed sets supply sufficient choices. Keep construction histories and reference master coefficients separate from model inputs.

For elimination, use the current row, source equations, reference order and allowed pivots. The recorded selections and resulting rows supply the training references. The identity collection specifies the unchanged source rows.

[splits.json](splits.json) holds out complete families. Validation uses the unequal-mass bubble and massless triangle with three off-shell legs. Tests use the massless box with four off-shell legs and equal-mass sunrise. Validation and test targets retain terms in the full physical sector, excluding examples confined to shared lower sectors. Related lower-sector masters remain common basis information.

## Scripts and execution on Hoffman

Run from /u/home/r/rushil/ML_for_Kira_Seeding_Reduction. The programs use the existing Python 3.9.6 module and SymPy 1.12.

1. s00_ibp.py supplies the family algebra, derivatives, symmetries and modular arithmetic. Direct execution checks a massive tadpole recurrence, a massless bubble identity, mass-preserving symmetries and prime fields.
2. s01_generate_targets.py constructs targets and their reference data.
3. s02_validate_targets.py validates the data and writes the catalog and split files.
4. s03_run_generation.sh runs generation and validation through the scheduler.

Submit the bounded collection with:

    mkdir -p master_to_target/logs
    qsub master_to_target/s03_run_generation.sh

For a smaller run:

    qsub master_to_target/s03_run_generation.sh \
      --family bubble_massless --chains 4 --max-individual 12

The defaults are 24 attempted expression chains, depth 4 and at most 64 nonzero individual constructions per family. Boundaries, duplicate targets and reduction requirements can lower the accepted count. A rerun replaces outputs for the selected families. Preserve collections intended for comparisons before changing the parameters.

The job requests one CPU and 4 GB RAM. It bounds address space, file size and runtime and checks memory and storage. The data limit is 500 MB and the project guard is 8 GB, leaving headroom below the user's 10 GB ceiling. Temporary files and scheduler logs stay outside Git.

## Validation and limits

The validator rederives all equations from their family and source. It independently checks used IBP equations by differentiating the original quadratic forms with respect to loop scalar products. It replays every construction and elimination with exact rational functions, checks dimensions and seed records, and repeats elimination at all three modular points.

Symbolic replay establishes the accepted target reductions from their recorded identities under the stated generic assumptions. The numerical checks verify the sampled data. The starting basis has the scope documented in [Master_Integrals](../Master_Integrals/README.md).

The collection covers the existing families and bounded seed ranges. It establishes neither completeness for every family integral nor performance at higher loops. No ML model has been trained.

The source identities use the [IBP method of Chetyrkin and Tkachov](https://doi.org/10.1016/0550-3213(81)90199-1). The starting bases come from the project's [Kira](https://arxiv.org/abs/1705.05610) calculations. [Kira 2](https://arxiv.org/abs/2008.06494) describes finite-field reductions, and [Kira 3](https://arxiv.org/abs/2505.20197) describes seed and equation choices relevant to the two models.
