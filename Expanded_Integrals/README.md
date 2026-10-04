# Expanded master and target collection

This collection extends the initial 16 families to 1,000 families. The added 984 families use one-loop integrals with four propagators and different exact mass and kinematic conditions. The original three two-loop families remain included. The family count describes parameter-defined integral families; it does not count different graph topologies.

The validated collection contains 1,000 families, 9,678 master-integral entries and 240,472 targets. The targets comprise 55,768 individual integrals and 184,704 integral expressions. The split contains 198,527 training targets, 19,600 validation targets and 22,345 test targets. catalog.json gives the family and target-type counts. Each family has a master basis checked by Kira and targets checked from their source identities. No model has been trained, and the recorded reductions do not establish minimum seed sets or operation counts.

## Family definitions

For the added families,

$$
I_{\boldsymbol a}=\int\frac{d^d\ell}{i\pi^{d/2}}
\prod_{i=0}^{3}\left[(\ell-P_i)^2-m_i^2+i0\right]^{-a_i},
\qquad P_0=0,\qquad d=4-2\epsilon.
$$

The three vectors P1, P2 and P3 supply the external momentum basis. Each squared mass is zero or one of up to three independent nonzero squared masses. Each of the six distances

$$
\Delta_{ij}=(P_i-P_j)^2,\qquad i<j,
$$

is zero or one of up to three independent nonzero momentum invariants. Repeated labels impose equality. Mass labels and momentum-invariant labels remain independent.

The stored mass parameters are m1, m2 and m3, and the momentum invariants are u1, u2 and u3. All these symbols have mass dimension two. The scalar products follow from

$$
P_i\cdot P_j=\frac{\Delta_{0i}+\Delta_{0j}-\Delta_{ij}}{2}.
$$

We require a nonsingular external Gram matrix at the three recorded finite-field points. These substitutions check algebraic relations. The integral definitions and their coefficients remain symbolic.

The enumeration compares all 24 permutations of the four propagators and permits relabelling of independent nonzero variables within each parameter type. It found 1,673 inequivalent profiles satisfying the bounds and sample checks. A deterministic hash ordering selected 984 profiles, excluding the existing massless box families.

## Master identification and target construction

Each added family uses the same three Kira 3.1 basis checks as the initial collection. The first check generates seeds with r <= 6, numerator power <= 2 and extra denominator powers <= 2, with a narrower probe range. The next two checks enlarge the bounds by one, first at the original point and then at a second point and prime. Kira receives the first basis as preferred masters and checks the full basis in the latter runs. Agreement establishes stability in these finite domains and samples.

Target construction starts from these masters. It uses exact IBP and symmetry identities, retains rational coefficient functions, and records both individual-integral constructions and reverse substitutions into master combinations. The added families use 48 attempted reverse sequences with at most four replacements and at most 96 nonzero individual constructions from the identity procedure. The candidate seed pool is fixed before target construction.

When a family has no master in the full sector, the initial seed restriction can prevent reverse paths from reaching that sector. s06_generate_connected_targets.py extends the candidate equations to all retained IBP identities containing the selected current integral. Its seed can lie in a higher sector. The same exact substitution and increasing-leading-integral conditions apply, and the validator checks the complete path. The runner uses this extension when the first construction accepts no targets.

Each accepted example contains its exact master expansion, construction history, sufficient seeds, source identities, allowed pivots and target-row elimination steps. The source equations remain fixed while each trace updates the target row. Adapting the elimination model to Kira requires matching Kira's state and available actions.

The validator rederives the equations, independently differentiates used IBP identities, checks each construction and reduction with exact rational functions, and checks the numerical rows at three finite-field points. The first point supplies numerical model inputs. The other two are separate checks. Family metadata retain the actual points, limits and completed results.

Operation counts include one finite-field division per step and one multiplication and subtraction per selected source-row term. Equation generation, combined-operator construction, symbolic simplification, inference and reconstruction remain outside these counts.

## Training and test separation

The added families keep each complete kinematic equality and zero pattern in one split across all mass assignments. This prevents the same kinematic profile appearing under different masses in separate splits. The grouping respects the original training box profiles. The combined split moves the original unequal-mass bubble and massless three-off-shell triangle from validation to training because these occur as lower sectors of expanded training families. The original files retain their initial split labels. The combined catalog and splits.json define the current assignments, and the reader applies these overrides while retaining the stored label. split_overlap_witnesses.json identifies the training-family sectors that motivate these changes.

The initial reverse sequences require validation and test expressions to contain their full physical sector. We also retained additional individual integrals from the checked construction proofs when all four family expressions have nonzero powers and at least one power is negative. Negative powers put these expressions in the numerator. These individual targets lie in lower physical sectors, and related lower-sector masters remain shared problem information. Holding out the complete family profile therefore does not make every lower-sector reduction new. The catalog reports individual-integral and integral-expression counts separately for each split. These counts must guide studies of individual-integral generalization. Collection size alone does not establish model accuracy or high-loop performance.

Keep reference coefficients, construction histories and recorded choices out of model inputs. Use inputs and family definitions for the seed model, and the current target row, source equations and available pivots for the elimination model.

## Stored files

families.json gives all 984 added definitions, their canonical profiles, grouping and sample points.

families/ contains one small JSON summary and one compressed archive per added family. Each archive contains the complete master and target records, Kira inputs and basis-check output, and a manifest with file sizes and SHA-256 hashes. Archives preserve the Master_Integrals/families/ and master_to_target/families/ paths, so they can be extracted into a separate directory on Hoffman if needed.

individual_targets/ contains one compressed JSON document for each added validation or test family. These documents hold the additional individual-integral inputs, exact reference expansions, sufficient seeds, reduction traces and validation results. They link to the original archive for source identities and construction proofs. The catalog gives their hashes and counts, and the reader appends these records when reading inputs, references or traces.

catalog.json combines the new and original collections. splits.json contains the target identifiers in each split. validation_summary.json records the archive, profile and mathematical-check totals.

The initial 16 families remain in ../Master_Integrals/ and ../master_to_target/. Their data are included in the combined counts without making duplicate archives.

All generated data stay on Hoffman and GitHub. The reader can stream records directly from archives on Hoffman:

    python3 Expanded_Integrals/s04_read_data.py \
      --family box_profile_0001 --kind inputs --limit 1

The available kinds are inputs, references, traces, identities, proofs, seeds, definition and masters. The records(family, kind) function also yields these records for later training programs.

## Programs and bounded execution

s00_prepare_families.py enumerates and selects inequivalent family definitions.

s01_generate_family.py identifies a basis, constructs targets, validates them and writes one archive. It reuses the checked physics procedures from the initial collection.

s02_validate_collection.py checks every archive and manifest, the master-check records, profile uniqueness, split separation and combined totals.

s03_run_collection.sh supplies the Hoffman scheduler wrapper. s04_read_data.py reads the completed records without extracting them.

The production array uses at most 64 concurrent tasks, one CPU and 2 GB requested RAM per task. Process address space, runtime and file sizes are bounded. A 6 GB project guard reserves room for Git and temporary files under the 10 GB ceiling. The archive replaces disposable per-family work after validation; scheduler logs and temporary engine state remain outside Git.

The four-family pilot used the same mathematical generation limits. The remaining families run with:

    qsub -t 5-984 -tc 64 Expanded_Integrals/s03_run_collection.sh

s05_check_collection.sh runs the final audit through the scheduler:

    qsub Expanded_Integrals/s05_check_collection.sh

s07_add_individual_targets.py selects the additional numerator integrals from the checked proof library, reconstructs their source rows and verifies every exact and finite-field elimination step. s08_run_individual_targets.sh supplies its scheduler wrapper. Run these after the family generation, then run the final audit:

    qsub -t 1-227 -tc 32 Expanded_Integrals/s08_run_individual_targets.sh

The individual-target array requests one CPU and 2 GB per task, with at most 32 concurrent tasks and a ten-minute limit.

Run the collection audit after every expected family and individual-target document has completed. A completed family is reused only when its archive hash agrees with its metadata.

The source identities follow the IBP method of Chetyrkin and Tkachov (doi:10.1016/0550-3213(81)90199-1). The basis identification uses Kira (arXiv:1705.05610; arXiv:2505.20197). The report gives the equations, results, scope and citations.
