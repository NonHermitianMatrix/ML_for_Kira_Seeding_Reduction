# Detailed experiment notes

`notes.pdf` records the development experiments behind the reduction method. It includes the original seed and row models, native Kira tests, exact recurrences, later cost models, and unsuccessful comparisons. Each result belongs to its stated inputs, reference method, and timing boundary.

`notes.tex` assembles the document. Supporting section files, `figures/`, and selected `paper_figures/` supply its text and plots. `references.bib`, `notes_additional_references.bib`, and `type_specialist_references.bib` supply citations. `notes_paper_reading_guide.tex` connects the detailed studies with the research paper.

The notes are a record of individual experiments. An earlier successful model is not necessarily deployed in the combined application. Document and source hashes in old validation files refer to the versions used for those checks.

Build this document with `make notes.pdf` from the report folder. [The document guide](README.md) explains Tectonic, figure producers, and validation commands. `s01_check_paper.py` also checks preservation of the original notes and their supporting files.
