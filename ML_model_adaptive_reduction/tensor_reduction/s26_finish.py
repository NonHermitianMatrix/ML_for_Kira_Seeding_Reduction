"""Complete both analyses, documents, folder guides, and validation."""
from s12_analyze import main as first
from s25_fast_analyze import main as final
from s13_document import main as document
from s14_guides import main as guides
from s15_validate import main as validate
if __name__=='__main__':
 first();final();document();guides();validate()
