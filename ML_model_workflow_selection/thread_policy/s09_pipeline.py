"""Fit worker-count policies, freeze them, and compare complete times."""
import argparse,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,filename):
 spec=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
import s05_fit as model
w=model.w
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--train-only',action='store_true');ap.add_argument('--test-only',action='store_true');args=ap.parse_args();assert not(args.train_only and args.test_only)
 configurations=['previous','threads2','threads4']
 w.write(HERE/'candidate_selection.json',dict(configurations=configurations,rule='Compare all three predefined worker counts. All methods receive the same four-core allocation. Training and validation select the policy; reserved outcomes do not change it.'))
 if args.test_only:assert (HERE/'trained_model/freeze.json').exists()
 if not (HERE/'trained_model/freeze.json').exists():
  sys.argv=[__file__,'--configurations',*configurations];model.main()
 if args.train_only:return
 load('thread_tests','s06_test.py').main()
 load('thread_analysis','s08_analyze.py').main()
 load('thread_public','s10_public_checks.py').main()
 w.emit(stage='pipeline_complete')
if __name__=='__main__':main()
