# ML_for_Kira_Seeding_Reduction

This project studies System 1 models for seed selection and elimination ordering in Kira IBP reduction.

The primary working copy is on Hoffman:

```text
rushil@hoffman2.idre.ucla.edu:/u/home/r/rushil/ML_for_Kira_Seeding_Reduction
```

The complete local project was copied to this folder, including the hidden `.tools/` directory. The directory contains:

```text
ML_for_Kira_Seeding_Reduction/
├── .gitignore
├── README.md
├── rules.md
├── Master_Integrals/
│   ├── README.md
│   ├── s00_prepare_tools.sh
│   ├── s01_build_kira.sh
│   ├── s02_generate_masters.py
│   ├── s03_validate_catalog.py
│   ├── s04_run_masters.sh
│   ├── families.json
│   ├── catalog.json
│   └── families/
├── report/
│   ├── Makefile
│   ├── background.tex
│   ├── references.bib
│   ├── report.tex
│   ├── report.pdf
│   ├── report.log
│   └── report.blg
└── .tools/
    ├── tectonic/
    ├── cache/
    ├── kira/
    ├── Ferl7/
    └── ... (build dependencies)
```

The report source, bibliography, rendered PDF and project rules are versioned here. The tool binaries, TeX cache and build logs remain on Hoffman and are excluded from Git history.

Read the [report PDF](report/report.pdf), [LaTeX source](report/report.tex) and [project rules](rules.md). The [master-integral folder](Master_Integrals/README.md) contains the numbered generation scripts, family definitions and basis records. Target-integral construction and model training have not started.

Project changes will be made in the Hoffman working copy and committed and pushed here so the file structure and report remain visible on GitHub. The project storage limit remains 10 GB, including tools, caches, outputs and copies.
