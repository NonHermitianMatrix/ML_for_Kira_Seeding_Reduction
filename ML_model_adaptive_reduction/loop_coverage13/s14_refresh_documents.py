"""Rebuild the documents from the frozen results without repeating timed reductions."""
from s09_document import main as document
from s10_guides import main as guides
from s11_validate import main as validate
if __name__=='__main__':
 document();guides();validate()
