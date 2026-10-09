"""Dispatch whole-expression policies while preserving existing workers."""
import sys
if sys.argv[4].endswith("_checked"):
 sys.argv[4]=sys.argv[4][:-8]
 from s69_expression_preflight import main
else:
 from s65_expression_worker import main
if __name__=="__main__":main()
