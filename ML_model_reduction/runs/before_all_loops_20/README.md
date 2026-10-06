# Snapshot before expanded-data training

This directory preserves the preceding model, optimizer checkpoint, metadata and source before the twenty-pass extension across loop orders. The exact warm-start file is runs/latest.pt. The current model's lineage records its SHA-256 and completed earlier progress. Files here describe the earlier dataset and remain historical; current counts and results appear in the parent model folder.
