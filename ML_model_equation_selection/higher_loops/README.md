# Higher-loop equation selection

This extension reduces the restricted coupled vacuum family already defined in integrals/higher_loops. It keeps every massless propagator power equal to one and uses two to four massive denominators with the common momentum Q=sum ell_i. It generates Euler IBP and mass partial-fraction equations and passes them to Kira's user-defined-system solver. It does not run Kira's native generic IBP generator.

The exact variable z=L(d-2) removes the loop number from the coefficient equations. One symbolic reduction in z supplies coefficients for any positive integer L after exact substitution. The master integrals themselves remain different functions at different loop orders. Squared masses use a common unit; for a target of total massive power B, restore the factor mu^(1-B) in its master coefficients.

s00_math.py defines the identities, a sufficient dependency construction, features, and an independent Taylor partial-fraction oracle. Every chosen relation lowers total massive power. Single-denominator powers use the Euler identity. Thus model scores affect cost and the generated set remains sufficient in this mathematical domain.

s01_train.py trains small decision trees to choose a partial-fraction pair. The training label is the smallest union of two recursively chosen dependency sets. This local teacher supplies a valid cost reference; it does not prove a global minimum. Leaf frequencies are not calibrated confidence. The model has eighteen exponent features and no loop-order feature.

s02_reduce.py generates equations, calls bounded Kira, reads exact polynomial coefficients, substitutes each requested loop order and checks every coefficient against the independent oracle. Its complete application timing includes input/model loading, generation, prediction, algebra, coefficient parsing, substitution, verification and any fallback. s04_study.py also measures external process time, including Python startup and evidence writing. Temporary solver files are removed after each attempt.

s03_cases.py declares distinct validation and test mass profiles and target lists. Training powers extend through nine, validation uses six and ten, and tests use eight and twelve. The primary tests cover every order one through twelve; additional checks extend above twelve. The training domain contains exponent shapes rather than separate mass-profile labels.

Run from the project root on a compute node:

    qsub ML_model_equation_selection/higher_loops/s05_run.sh pilot
    qsub ML_model_equation_selection/higher_loops/s05_run.sh validation

The archived development_initial/ directory preserves the first 144 validation workflows and three pilots. The final integration adds ordered-index features and an exact reader checked on 277 distinct coefficients. The refined training and validation records are in training/ and validation/.

Then run s06_select.py to select policies using validation results and freeze code, weights, input definitions and the binary before the test job. It compares complete costs with first-pair, smallest-pair, largest-pair and extreme-pair controls. Exact loop reuse and learned selection have separate controls.

An application input contains family="coupled_vacuum_unit_massless", mass_ratios, targets (massive-index vectors), and loops. The normalized squared-mass scale equals one. Only the explicitly validated domain enters this route. Existing native two-/three-loop applications remain available in ../early_generation/.

The higher-loop extension generates exact Euler and mass partial-fraction equations for the restricted coupled vacuum family, then uses Kira's user-defined-system solver. A shared variable z=L(d-2) supports every positive loop order mathematically. Tests cover L=1,...,12, with additional applications at 13, 16, 24 and 32. Across six reserved batches, the deployed route has complete-time ratio 0.155 (descriptive interval 0.132--0.184) to separate full-pool reductions. The learned separate-loop route has ratio 0.911 (descriptive interval 0.815--0.986) to the same full-pool baseline. Learned/shared versus rule/shared has ratio 0.968 (descriptive interval 0.927--1.003). Validation selects the extreme route. These are supplied-identity results, with exact coefficient checks and all runtime costs; they do not establish a generic high-loop native Kira speedup.

All generated data remain on Hoffman and GitHub. One experiment job runs at a time, with bounded solver time, RAM and scratch. See resource_plan.json. Previous checkpoints and native comparisons remain unchanged.

The frozen application is s08_application.py. It selects the validation-approved route automatically; --policy learned runs the saved System 1 model explicitly. s16_export_existing.py prepares scalar-component requests from the existing coupled vacuum collection. The exporter retains the original expression identifiers; combine the returned component reductions with the original target weights when reducing those expressions.

s07_analyze.py audits all saved exports, s09_plot.py makes the figures, and s14_extrapolate.py checks the deployed application above twelve loops. model_test/ contains 90 paired workflows and six additional applications. Its source choices identify every generated equation and Euler seed. Exact exports and solver logs are content-addressed in objects/; each JSON record stores their SHA256 digest.

The application accepts at most 128 scalar components, total massive power at most fourteen, and at most 32 requested loop orders per batch. Each requested loop number may be any positive integer. integration/ under model_test/ contains two successful checks against the existing dataset exporter and a master-only boundary case. All three pass exact checks.
