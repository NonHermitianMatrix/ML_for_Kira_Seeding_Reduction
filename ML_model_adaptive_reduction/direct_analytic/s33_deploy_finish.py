"""Write the final deployment study after the original experiment remains preserved."""
from s28_deploy_analyze import main as analyze
from s18_document import main as write_document
def document():return write_document(final=True)
from s19_guides import main as guides
from s32_deploy_validate import main as validate
if __name__=='__main__':
 analyze();document();guides();validate()
