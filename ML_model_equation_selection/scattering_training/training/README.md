# Native training records

These compressed JSON records contain training reductions and candidate equation labels.
Each tab-separated equation record gives its seed and operator, label, 24 stored features, score and keep flag.
Only seventeen features enter the equation tree.
The seed tree removes the operator feature and groups equations by seed.
Coefficient-expression features never enter either new tree.
The record also stores the exact check against the native reference.

Use `s00_scattering_study.py collect` to produce the records.
Use `s00_scattering_study.py train` to fit the models.
Read [the study guide](../README.md) before either action.
