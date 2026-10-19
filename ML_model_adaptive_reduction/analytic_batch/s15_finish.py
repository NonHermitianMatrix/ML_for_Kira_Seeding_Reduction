"""Complete analysis, documentation, and exact evidence checks."""
from s10_analyze import main as analyze
from s12_document import main as document
from s14_readmes import main as guides
from s13_validate import main as validate
if __name__=='__main__':
 analyze();document();guides();validate()
