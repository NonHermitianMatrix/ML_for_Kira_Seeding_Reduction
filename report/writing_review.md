# Study report and comparative tables

The title is “Optimizing Methods for Feynman Integral Reduction with Kira”. The author and displayed date are blank; the PDF author field is empty. We use active first-person language for the work performed in the study.

We read the user-supplied [UVU Scientific Writing: IMRaD guide](https://www.uvu.edu/writingcenter/docs/scientificwriting.pdf). We applied its sequence: background and objective, reproducible methods, measured results, then interpretation and limits. We also retained the reader and audience guidance listed below. These guides concern writing; they are not evidence for physics claims.

The report now links integral structures to physical uses, final formulas, and measured gains. The analytic table states each domain and baseline. Separate tables give all twenty one-loop tensor requests by type and all nine completed physical classes in the shared-model study. A model table connects representations, decisions, and measured outcomes. The discussion compares advantages and disadvantages, including failure cost, offline fitting, restricted analytic domains, and unresolved gains.

New physical context uses primary studies of heavy-quark decoupling, planar and nonplanar double boxes, and five-parton QCD amplitudes. Formula cells refer to derivations in the paper. Existing measurements supply every timing entry. No training, integral generation, or benchmark was run for this revision.

Run `s06_method_tables.py` to recreate the two numerical tables from the retained evidence. `method_table_data.json` records their source checksums. Run `s07_check_method_tables.py` after the PDF build to check titles, formulas, counts, and controls. Checksums and implementation details stay in this guide and validation files.

# Whole-project scope correction

The revised main narrative covers the complete study, beginning with known-answer integral data and ending with the combined application. It gives central space to the original-to-optimized vacuum comparison, native ML controls, shared requests, and the 75-request cumulative comparison. The latest 93-request increment is supporting detail. No new training or timing data were produced for this revision.

Own measurements are supported by saved numerical evidence, methods, and named controls. External methods retain primary citations. New appendix material derives target construction, learning losses, basis conversion, request sharing, vacuum recurrences, and timing estimators. The earlier checked writing guidance remains below.

# Writing and evidence review

This revision changes the paper's explanation and structure. It adds no scientific timing measurements.
The title states the reduction problem and names Kira.
The introduction gives the context, task, and route through the paper.
A worked tadpole example connects the derivative identity to a target-to-master coefficient.
The method comes before the physical scope and results.
The discussion states what the measured gain supports.

The structure follows the reader-focused guidance in [Scientific Papers, Nature Scitable](https://www.nature.com/scitable/topicpage/scientific-papers-13815490/).
The prose uses the audience guidance in [Audience and Purpose](https://www.nature.com/scitable/topicpage/audience-and-purpose-13952663/).
These sources guide the writing. They are not physics evidence and are not placed in the scientific bibliography.
The paper's background and method citations refer to the original studies.

## Claim and equation map

- Physics context and dimensional regularization: `Weinzierl2022`.
- Integration-by-parts identity: `ChetyrkinTkachov`; its expansion is derived in Appendix A.
- Ordered reduction and Kira: `Laporta`, `KiraOriginal`, and `Kira3`.
- Finite-field reconstruction: `Kira2`, `FireFly2019`, and `FireFly2020`; the sample constraint is derived in the reconstruction appendix.
- Related learned seed search: `Song2025`.
- Related one-loop methods: `DennerDittmaier2006` and `Hu2025`.
- Triangle Gamma representation: `DavydychevOsland1998`; the paper derives its normalization, signs, bubble coefficient, and recurrence.
- Gamma definition and shift relation: `NISTGamma`.
- The original row-model set representation: `DeepSets`.
- Tree fitting methods: `CART1984` and `Geurts2006ExtraTrees`.
- Bootstrap construction: `Efron1979`. Each reported interval retains its original sampling unit.
- Tadpole example: the product-rule calculation in `focused_derivations.tex`.
- Tensor recurrences: `focused_tensor_appendix.tex`.
- Zero-invariant bubble: `lightlike_appendix.tex`.
- Connected trees: `focused_trees_appendix.tex`.
- Vacuum partial fractions and analytic tadpole values: `direct_appendix.tex`.
- Weighted regression objective and timing ratios: definitions and derivations in `focused_derivations.tex`.
- Physical inputs and bounds: explicit definitions in the appendices. They describe this implementation and test, not a universal integral classification.

The paper labels its own numerical results as measurements from this study.
An external citation cannot establish these measurements.
The following saved records support them:

- Native executable version and configuration: the recorded `reconstruction_policy/build.json` on Hoffman.
- Final 93-request comparison: `triangle_monitor_summary.json`.
- Fresh-call family and loop comparison: `triangle_summary.json`.
- Earlier seed comparison: `vacuum_learning_data.json`, field `ml`.
- Earlier equation comparison: `equation_refinement_data.json`, field `index_transfer`.
- Original and compiled row comparisons: `paper_figure_data.json`.
- Reconstruction-era learned control: `reconstruction_retained_data.json`.
- Earlier cumulative comparison: `reconstruction_data.json`.
- Latest cost-selector validation: `rewrite_cost_evidence.json`, copied from the original training summary.

## Interpretation checks

The 8.8% result is the final incremental comparison on 93 requests. The paper also presents the original-to-optimized vacuum result and the independent native ML controls.
The control already includes earlier exact and learned methods.
The external coefficient audit is outside the final application timer for every method.
Internal group sums have a different timing boundary from complete-collection time.
The report does not multiply percentages from different workloads.
The plots show equal-time reference lines where ratios are used.
The three collection observations are shown directly and are not called a confidence interval.
The equation interval resamples repetitions; the seed and reconstruction intervals resample requests.
The seven-loop triangle product and the final sunrise group remain visible as slower cases.
The rejected arithmetic selector, rejected equation filter, and unresolved parallel basis check remain in the paper.
The notes keep the full historical tests.

The analytic results through thirteen loops cover stated products and tree families.
The final native comparison covers connected two- and three-loop inputs at rational kinematic points.
The report does not claim exhaustive high-loop coverage or a new learned gain in the final test.

## Reproduction

Run `s02_rewrite_figures.py`, render both documents with `make`, then run both paper checkers.
`s01_check_paper.py` retains the old evidence and notes-preservation checks.
`s03_check_rewrite.py` checks the new numerical claims, figures, references, and rendered document records.
Inspect the rendered pages after these checks.
The document review record stores that inspection separately from the scientific measurements.
