# Integral collection

This folder contains all 1,000 families, their 9,678 master entries and their 240,472 targets. The three data folders separate the master bases, the target definitions and the relations between them:

    integrals/
      master_integrals/
        families/<family>/masters.json
        families/<family>/definition.json
        families/<family>/basis_checks.tar.gz
      target_integrals/
        families/<family>/inputs.jsonl.gz
      master_to_target/
        families/<family>/references.jsonl.gz
        families/<family>/elimination_traces.jsonl.gz
        families/<family>/identities.jsonl.gz
        families/<family>/construction_proofs.jsonl.gz
        families/<family>/candidate_seeds.json

[master_integrals](master_integrals/README.md) contains all stored master bases, including the bases that were previously inside the expanded-family archives. [target_integrals](target_integrals/README.md) combines the original targets, expanded targets and additional individual targets in the same per-family layout. [master_to_target](master_to_target/README.md) contains all reduction and construction records.

A family name identifies the same integral definition in all three folders. Each target has an unchanged ID such as box_profile_0001:T00001 or box_profile_0001:U00001. The same ID appears in its input, reference reduction and elimination trace. Each reference also lists master_ids in the same order as its master_coefficients. The corresponding master definitions are in that family's masters.json.

All active data paths are relative to integrals/. JSONL files contain one record per line; their .gz suffix indicates gzip compression. The reader decompresses these files as it reads them. This keeps the collection within the storage limit.

[catalog.json](catalog.json) gives all file locations and counts. [families.json](families.json) lists all 1,000 definitions, and [splits.json](splits.json) retains the established training, validation and test assignments. Each category also has a catalog. [validation_summary.json](validation_summary.json) records the mathematical checks already completed and the checks of this reorganization.

The total of 240,472 targets comprises 55,768 individual integrals and 184,704 integral expressions. There are 198,527 training targets, 19,600 validation targets and 22,345 test targets. The validation and test sets contain 183 and 202 individual integrals, respectively. The 384 additional individual targets contain numerator factors and lie in one-propagator sectors.

The collection covers 997 one-loop and three two-loop families. The 984 added families vary exact mass and kinematic conditions within the one-loop box topology. Full kinematic profiles stay in one split across mass assignments; some lower-sector reduction structure remains shared. The basis checks cover stated finite index ranges and sample points. The data provide verified reference reductions and do not establish minimum reduction costs or high-loop model performance.

## Reading a family or a target

Run these commands from the project directory on Hoffman:

    python3 integrals/s01_read_data.py \
      --family box_profile_0001 --kind masters

    python3 integrals/s01_read_data.py \
      --family box_profile_0001 --kind inputs --limit 2

    python3 integrals/s01_read_data.py \
      --target box_profile_0001:U00001

The last command returns the target, its exact reference expansion, its seeds and construction history, its elimination trace and the master definitions used in the expansion. Shared source identities and proof libraries remain linked through their file paths and record identifiers.

For later programs, records(family, kind) supports inputs, references, traces, identities, proofs, seeds, symmetries, definition, masters and metadata. linked_target(identifier) joins the three target records and their master definitions. Keep reference answers and recorded decisions separate from the information supplied to an ML model.

## Reorganization and checks

The organization changed the locations and links of existing data. Target IDs, integral indices, coefficients, seeds, source identities, proof dependencies, elimination operations and operation counts retain their values. The combined split labels now appear directly in the records; stored_split retains an earlier label where a family was reassigned.

The programs are numbered by their role:

- s00_reorganize.py converts the earlier layout, combines additional targets and preserves the source records.
- s01_read_data.py reads the current layout and joins targets with their master relations.
- s02_validate.py checks every file manifest, master basis, target link, seed reference, elimination trace, operation count and split assignment.
- s03_run_reorganization.sh runs a bounded conversion task through the Hoffman scheduler.
- s04_run_validation.sh runs the collection checks through the scheduler.

The completed migration used a full comparison with the previous data before removing the three old top-level folders. A later integrity check uses:

    mkdir -p .tools/integrals-layout/logs
    qsub integrals/s04_run_validation.sh

The migration program requires the previous layout as its source. It is retained to document and reproduce the move; it does not generate new integrals. The original programs, catalogs and validation reports are preserved in master_to_target/generation_source.tar.gz and remain viewable in the [previous Git commit](https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/82ebe3c870d8382f2f72f4f1598092f102a6fdc2). Historical paths inside these records describe the original calculations.

Conversion uses one CPU per task, at most four concurrent tasks, a 1.5 GB address-space limit and bounded output sizes. A 6 GB project guard reserves space below the 10 GB ceiling. All datasets and temporary copies stay on Hoffman.
