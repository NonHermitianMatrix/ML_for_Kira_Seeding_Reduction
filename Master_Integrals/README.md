# Master integrals

This folder identifies symbolic master-integral bases for 16 defined one-loop and two-loop families. It contains the family definitions, code, Kira inputs and generated basis records. Target-integral construction and ML training belong to later stages.

For each family, the integral notation is

$$I_{\boldsymbol a}=\left(\prod_{j=1}^{L}\int\frac{d^d k_j}{i\pi^{d/2}}\right)\prod_{i=1}^{N}D_i^{-a_i},\qquad D_i=q_i^2-m_i^2+i0,\qquad d=4-2\epsilon.$$

Here $L$ is the number of loops, $k_j$ are the loop momenta, $N$ is the number of denominator and auxiliary expressions, and $\boldsymbol a$ is their integer index vector. Each family fixes the momenta $q_i$, squared masses and external scalar products. Positive indices select denominators; negative indices represent numerator factors. A master record specifies this integral symbolically. Its numerical value and epsilon expansion require a separate calculation.

The definitions cover a massive tadpole, four bubbles, five triangles, three boxes, a two-loop massless propagator, an equal-mass sunrise and an equal-mass vacuum sunset. The mass patterns and external virtualities distinguish these families. Each top-level sector includes all its subsectors. For the sunrise, the last two expressions complete the scalar-product basis and only allow nonpositive indices.

The scripts have the following roles:

- `s00_prepare_tools.sh` downloads pinned build dependencies and checks their hashes. Run this lightweight setup from the project root.
- `s01_build_kira.sh` is the scheduler job that builds Kira 3.1 with one CPU and a 4 GB allocation. It uses the cluster GiNaC installation and builds YAML-cpp locally.
- `s02_generate_masters.py` writes each family's Kira configuration, runs master identification and saves its basis and validation evidence. `--prepare` only writes configurations; `--family NAME` limits a run to a named family.
- `s03_validate_catalog.py` checks family definitions, index vectors, sector labels, raw Kira lists, basis stability and selected simple-family reference counts.
- `s04_run_masters.sh` is the scheduler job for steps 02 and 03. Pass it to `qsub`; it runs the families sequentially on one CPU.

All commands below start in `/u/home/r/rushil/ML_for_Kira_Seeding_Reduction`. For a fresh checkout, prepare the dependencies and submit the build:

```bash
bash Master_Integrals/s00_prepare_tools.sh
qsub Master_Integrals/s01_build_kira.sh
```

After the build job succeeds, submit master identification:

```bash
qsub Master_Integrals/s04_run_masters.sh
```

To run one family, pass its name:

```bash
qsub Master_Integrals/s04_run_masters.sh --family tadpole_massive
```

The scheduler logs are in `Master_Integrals/logs/`. Completed family records with the same input, generator and executable hashes are reused. Add `--rerun` to recalculate them. Changes to a family definition require a new identification and validation run.

The generator calls Kira with `run_initiate: masters`. Kira generates IBP and symmetry relations and identifies a master basis through finite-field elimination. Symbolic forward elimination and back substitution are disabled. Internal integral domains are used only to identify and check the basis; this stage creates no target-training collection.

For a top sector with $t$ positive indices, the discovery run generates equations through $r=t+2$, $s=2$, and two extra denominator powers. It probes integrals through $r=t+1$, $s=1$, and one extra denominator power. Here $r$ is the sum of positive indices and $s$ is minus the sum of negative indices. The YAML job key `d` bounds extra denominator powers, and `sample.d` supplies the integration dimension. The expanded run increases each bound by one. Kira then repeats the expanded calculation at a second sample point and prime. The discovered basis becomes the preferred basis in the two checks, with `check_masters: true`. All three runs must return the same complete list before the generator publishes a validated family record.

These are finite-domain, finite-field checks of a basis at the stated kinematics. They provide evidence against missing relations in the tested domains and accidental rank changes at one sample point. They do not prove completeness for all integer indices or for exceptional kinematic limits. Extending to a new family requires checking its assumptions and expanding the domains as needed. A changed or missing basis causes the run to fail.

The folder layout is:

```text
Master_Integrals/
  s00_prepare_tools.sh
  s01_build_kira.sh
  s02_generate_masters.py
  s03_validate_catalog.py
  s04_run_masters.sh
  families.json
  catalog.json
  validation_summary.json
  toolchain.json
  scheduler_run.json
  families/<family>/
    definition.json
    config/integralfamilies.yaml
    config/kinematics.yaml
    masters.json
    masters.txt
    status.json
    README.md
    validation/<stage>/
      jobs.yaml
      run.json
      masters.raw
      masters.txt
      preferred_masters       # expanded checks only
      kira.log
```

`masters.json` assigns a family-specific identifier to each master and records its index vector, sector and mass dimension. `run.json` records the actual seed and probe bounds, sample point, prime, command, execution host and timing. `catalog.json` gives the per-family counts and paths. Masters in different families can represent related integrals, so the catalog total counts records rather than globally independent functions.

The generator limits each Kira stage to 300 seconds, checks the combined resident memory of its process session, limits individual output files, and stops if its working data or project directory reaches the configured size ceiling. The project guard is 8 GB, leaving headroom below the user's 10 GB total limit. The original local copy and tools must remain within that total. Build and calculation jobs each request one CPU and 4 GB from Hoffman. Disposable databases and scheduler logs stay outside Git; family definitions, master lists and validation evidence are versioned. Raw Kira logs retain the solver's formatting.

The implementation follows [Kira's reduction method](https://arxiv.org/abs/1705.05610), [Kira 3's master-basis checks](https://arxiv.org/abs/2505.20197), and the [Kira 3.1 source](https://gitlab.com/kira-pyred/kira/-/tree/3.1). The initial one-loop basis checks are consistent with the tadpole, bubble, triangle and box organization in [Ellis and Zanderighi](https://arxiv.org/abs/0712.1851). Jobs follow the [Hoffman production scheduler documentation](https://www.hoffman2.idre.ucla.edu/Using-H2/Computing/Computing-Altair-production.html).

The completed catalog contains 49 family-specific master records across 16 families. Each family passed all three identification checks. The per-family results are:

- [One-loop massive tadpole](families/tadpole_massive/README.md): 1 masters, 1 loop.
- [One-loop massless bubble](families/bubble_massless/README.md): 1 masters, 1 loop.
- [One-loop bubble with one massive line](families/bubble_one_mass/README.md): 2 masters, 1 loop.
- [One-loop equal-mass bubble](families/bubble_equal_mass/README.md): 2 masters, 1 loop.
- [One-loop unequal-mass bubble](families/bubble_two_mass/README.md): 3 masters, 1 loop.
- [One-loop massless triangle with one off-shell leg](families/triangle_massless_one_offshell/README.md): 1 masters, 1 loop.
- [One-loop massless triangle with two off-shell legs](families/triangle_massless_two_offshell/README.md): 2 masters, 1 loop.
- [One-loop massless triangle with three off-shell legs](families/triangle_massless_three_offshell/README.md): 4 masters, 1 loop.
- [One-loop equal-mass triangle with one off-shell leg](families/triangle_equal_mass_one_offshell/README.md): 3 masters, 1 loop.
- [One-loop equal-mass triangle with three off-shell legs](families/triangle_equal_mass_three_offshell/README.md): 5 masters, 1 loop.
- [One-loop massless box with four on-shell legs](families/box_massless_onshell/README.md): 3 masters, 1 loop.
- [One-loop massless box with one off-shell leg](families/box_massless_one_offshell/README.md): 4 masters, 1 loop.
- [One-loop massless box with four off-shell legs](families/box_massless_four_offshell/README.md): 11 masters, 1 loop.
- [Two-loop massless propagator](families/propagator_two_loop_massless/README.md): 2 masters, 2 loops.
- [Two-loop equal-mass sunrise](families/sunrise_two_loop_equal_mass/README.md): 3 masters, 2 loops.
- [Two-loop equal-mass vacuum sunset](families/vacuum_two_loop_equal_mass/README.md): 2 masters, 2 loops.

See [catalog.json](catalog.json) for the machine-readable index and [validation_summary.json](validation_summary.json) for the completed checks.
