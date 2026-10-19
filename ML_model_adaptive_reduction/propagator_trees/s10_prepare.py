"""Run the final domain checks and freeze the complete comparison."""
from s04_prop_checks import main as check
from s06_protocol import main as freeze
check()
freeze()
