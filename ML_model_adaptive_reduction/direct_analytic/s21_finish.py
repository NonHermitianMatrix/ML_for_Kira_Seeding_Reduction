"""Analyze, document, build, and validate the completed frozen study."""
from s16_analyze import main as analyze
from s18_document import main as document
from s19_guides import main as guides
from s20_validate import main as validate
if __name__=='__main__':
 analyze();document();guides();validate()
