"""Complete analysis, documentation, guides, and document validation."""
from s12_analyze import main as analyze
from s21_fast_analyze import main as final_analyze
from s13_document import main as document
from s14_guides import main as guides
from s15_validate import main as validate
if __name__=='__main__':
 analyze();final_analyze();document();guides();validate()
