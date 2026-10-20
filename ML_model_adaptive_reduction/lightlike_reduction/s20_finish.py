"""Analyze the frozen comparison, write both documents, and validate the result."""
from s16_analyze import main as analyze
from s17_document import main as document
from s18_guides import main as guides
from s19_validate import main as validate
if __name__=='__main__':
 analyze();document();guides();validate()
