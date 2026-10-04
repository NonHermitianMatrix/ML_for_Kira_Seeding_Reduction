# Relations between masters and targets

This folder links every target to its master expansion and to the identities and operations used to construct and reduce it. It covers all 240,472 targets across all 1,000 families.

For each target T, the reference records give

$$
T=\sum_m c_m(\boldsymbol x,d)M_m.
$$

Here $M_m$ is a master integral in the target's family, $\boldsymbol x$ denotes the mass and momentum-invariant parameters, $d$ is the dimension, and $c_m$ is an exact rational function. Each reference has the same target ID as its input and elimination trace. Its master_ids match the order of the terms in master_coefficients, so each coefficient links directly to a definition in the family's masters.json.

## Records for each family

references.jsonl.gz contains the exact master coefficients, master IDs, construction history, sufficient seed set, source-equation IDs, number of elimination steps, arithmetic operation counts and checks at three finite-field points.

elimination_traces.jsonl.gz contains the target row before and after each step, the available pivot equations, the selected equation and integral, the multiplier, new and cancelled nonzero entries, and operation counts.

identities.jsonl.gz contains the source equations, exact coefficients, sampled coefficients and the IBP seed and derivative operator or symmetry transformation that produced each equation.

construction_proofs.jsonl.gz records how individual integrals and zero-integral dependencies follow from the masters and earlier identities. References to this proof library identify the required construction.

candidate_seeds.json contains the candidate indices and their bounds. symmetries.json describes the retained transformations of loop variables and propagators.

metadata.json gives the combined family counts, operation totals and provenance. manifest.json records file hashes and sizes for that family across all three data folders. generation_records.tar.gz preserves the original generation summaries, validation reports and family metadata. The additional target records are integrated into the main input, reference and trace files; their validation metadata remain in this archive.

## Construction and elimination

The construction starts from known masters and their linear combinations. An identity

$$
R=\sum_{\boldsymbol b}r_{\boldsymbol b}I_{\boldsymbol b}=0
$$

can replace a term w_a I_a in the current expression through

$$
T_{n+1}=T_n-\frac{w_{\boldsymbol a}}{r_{\boldsymbol a}}R,
\qquad r_{\boldsymbol a}\ne0.
$$

This step introduces other integrals while preserving the master expansion. The records retain the actual identity, its seed and the multiplier. Individual-integral proofs also solve identities whose other terms already have known master expansions.

During the recorded reduction, each selected source row cancels a nonmaster integral from the target coefficient row. The source equations stay fixed while the target row changes. The available pivots respect the stored integral order. Applying a learned policy within Kira will require matching Kira's evolving system and available actions.

Each step counts one finite-field division and one multiplication and subtraction per selected source-row term. The collection contains 832,924 recorded elimination steps. These counts cover the stated target-row operations. Equation generation, construction of combined derivative operators, symbolic simplification, model inference and rational reconstruction require separate accounting.

The completed mathematical checks rederived 3,299,902 equations, independently differentiated 227,330 used IBP equations and replayed every target reduction symbolically and at three finite-field points. The layout audit compares the moved records against this checked collection and verifies their links and operation totals.

## Reading related records

The [unified reader](../s01_read_data.py) returns one target with its reference reduction, seeds, construction history, elimination trace and the masters used:

    python3 integrals/s01_read_data.py \
      --target box_profile_0001:U00001

Use --family with --kind references, traces, identities, proofs, seeds, symmetries or metadata to read shared family records. [catalog.json](catalog.json) supplies the file locations, and all active paths are relative to integrals/.

The seed model can use the target, family definition, basis and candidate seeds as problem information. The elimination model can use the current target row, source equations and allowed pivots. Keep the reference master coefficients, construction history and recorded choices separate from model inputs.

## Preserved generation source

generation_source.tar.gz contains the original generation programs, original README files, catalogs and validation summaries. generation_source_manifest.json records their hashes and the source commit. The archived programs retain their original paths and source bytes so their recorded hashes remain verifiable. They describe the completed generation runs; the current collection is read and checked through the programs in integrals/.

The source remains viewable in the [preserved Git commit](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/82ebe3c870d8382f2f72f4f1598092f102a6fdc2). The [project report](../../report/report.pdf) explains the physics, mathematical construction and scope. The data provide known valid reductions, while minimum seed and operation counts remain unproved.

The current seed-model division is available through [training](../training/README.md) and [testing](../testing/README.md). Their family links point to the files stored here; they do not duplicate integral data. The present run uses only the training view.
