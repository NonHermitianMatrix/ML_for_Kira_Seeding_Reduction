# Integral data: families, masters, targets, and relations

This collection supplies exact reference reductions for training and testing. It contains 17,100 family instances, 57,979 family-local master entries, and 2,301,272 targets at one through twelve loops. Higher-loop additions mainly use a restricted coupled-vacuum structure. Mass variations count as separate family instances.

## Connect the records

| Location | Stored information |
|---|---|
| [master_integrals](master_integrals/README.md) | Propagators, loop and external momenta, scalar products, and master index vectors. |
| [target_integrals](target_integrals/README.md) | Target integral expressions before reduction. |
| [master_to_target](master_to_target/README.md) | Exact master coefficients, source identities, candidate seeds, and recorded elimination steps. |
| [training](training/README.md) | Linked views of 1,610,890 targets in 11,963 training families. |
| [testing](testing/README.md) | Linked views of 690,382 targets in 5,137 reserved test families. |

The same family folder name connects the three record types. The target `id` connects its input, reference coefficients, and elimination trace. Master identifiers select entries from that family’s basis. Training and testing use links to the original records; they do not duplicate the collection.

The construction starts from known master coefficients and adds valid zero identities. It records a sufficient path back to the masters. That path does not establish the fewest possible operations. Partial-fraction identities have no IBP seed label.

## Inspect a family or target

The reader streams compressed records and accepts both gzip and xz files. These commands use only Python’s standard library and run from the repository root:

```bash
python integrals/s01_read_data.py --family box_massless_four_offshell --kind definition
python integrals/s01_read_data.py --family box_massless_four_offshell --kind inputs --limit 1
python integrals/s01_read_data.py --target FAMILY:ID
```

Replace `FAMILY:ID` with an identifier returned by the input reader. The target command returns the input, reference coefficients, elimination trace, family definition, and required masters together. Supported `--kind` values are `inputs`, `references`, `traces`, `identities`, `proofs`, `seeds`, `symmetries`, `definition`, `masters`, and `metadata`.

`catalog.json` and the category catalogs index the stored families. `splits.json` assigns related mass profiles to training or testing across loop orders. `model_split_summary.json` gives split counts. `validation_summary.json` records collection checks.

## Generation and validation

[higher_loops](higher_loops/README.md), [expansion_250](expansion_250/README.md), and [expansion_1000](expansion_1000/README.md) contain the generation procedures for their respective additions. Their scripts write datasets and require scheduled jobs. Preserve the existing split when reproducing or extending the collection.

Use `s02_validate.py` to check layout, links, and stored records. `s04_run_validation.sh` supplies its scheduler limits. `s00_reorganize.py` and `s03_run_reorganization.sh` reproduce the original layout conversion. `s05_prepare_model_splits.py` creates the linked training and testing views.

## Scripts

| File | Purpose |
|---|---|
| [s00_reorganize.py](s00_reorganize.py) | Reorganize the existing checked collection without generating new integrals. |
| [s01_read_data.py](s01_read_data.py) | Read the unified integral collection on Hoffman. |
| [s02_validate.py](s02_validate.py) | Verify the unified layout, all links and unchanged scientific records. |
| [s03_run_reorganization.sh](s03_run_reorganization.sh) | Scheduler wrapper for run reorganization; its header sets the resource limits. |
| [s04_run_validation.sh](s04_run_validation.sh) | Scheduler wrapper for run validation; its header sets the resource limits. |
| [s05_prepare_model_splits.py](s05_prepare_model_splits.py) | Create non-overlapping train/test directory views without copying integral data. |
