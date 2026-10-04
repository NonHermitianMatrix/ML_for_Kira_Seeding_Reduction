# Target integrals

This folder contains all 240,472 targets from all 1,000 families. Each family has one inputs.jsonl.gz file containing both its original targets and its additional individual targets.

The kind field distinguishes 55,768 individual integrals from 184,704 integral expressions. An individual target has one normalized integral term. An expression contains several family integrals with exact rational coefficient functions:

$$
T=\sum_{\boldsymbol a}w_{\boldsymbol a}(\boldsymbol x,d)I_{\boldsymbol a}.
$$

Here $T$ is the target, $I_{\boldsymbol a}$ is a family integral, $\boldsymbol x$ denotes its masses and momentum invariants, and $w_{\boldsymbol a}$ is its coefficient. The data retain the exact functions and their values at the recorded finite-field sample.

Each input record specifies the target ID, family, split, terms, integral indices, sector information, mass dimension and sampled coefficient row. Its file links identify the family definition, master basis, candidate seed pool, source equations, reference reductions and elimination traces. These paths are relative to integrals/.

The same target ID connects this input to references.jsonl.gz and elimination_traces.jsonl.gz in the corresponding [master_to_target](../master_to_target/README.md) family directory. The reference supplies the exact master coefficients, sufficient seeds, construction history and operation counts. The master definitions are in [master_integrals](../master_integrals/README.md).

[catalog.json](catalog.json) lists the families and target counts. The combined [split file](../splits.json) contains 198,527 training targets, 19,600 validation targets and 22,345 test targets. Validation contains 183 individual integrals; testing contains 202. The additional individual targets involve numerator factors in one-propagator sectors. The split policy and its limits are described in the [collection README](../README.md).

The records now carry their current combined split directly. For the two original families moved from validation to training, stored_split preserves their earlier label. Their target expressions and reference reductions remain unchanged.

Use the unified reader on Hoffman:

    python3 integrals/s01_read_data.py \
      --family box_profile_0001 --kind inputs --limit 2

    python3 integrals/s01_read_data.py \
      --target box_profile_0001:T00001

Target construction started from master combinations and used exact IBP and symmetry identities to introduce other integrals while retaining a known master expansion. The full construction and reduction evidence belongs to the corresponding relation records. A recorded reduction supplies a verified reference sequence; minimum seed sets and operation counts remain unproved.

The current seed-model division is available through [training](../training/README.md) and [testing](../testing/README.md). Their family links point to the files stored here; they do not duplicate integral data. The present run uses only the training view.
