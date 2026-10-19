"""Analyze the completed comparison and build its checked documents."""
from s08_analyze import main as analyze
from s09_document import main as document
from s11_guides import main as guides
from s12_validate import main as validate
analyze()
document()
guides()
validate()
