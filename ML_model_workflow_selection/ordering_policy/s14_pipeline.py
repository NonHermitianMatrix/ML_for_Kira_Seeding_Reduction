"""Run the saved experiment with explicit paths for its summary modules."""
import argparse,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import s05_fit as model
def module(name,filename):
 spec=importlib.util.spec_from_file_location(name,HERE/filename)
 value=importlib.util.module_from_spec(spec);sys.modules[name]=value
 spec.loader.exec_module(value);return value
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--finish-only',action='store_true');args=parser.parse_args()
 analysis=module('ordering_analysis','s08_analyze.py')
 public=module('ordering_public','s10_public_checks.py')
 if args.finish_only:
  frozen=json.loads((HERE/'trained_model/freeze.json').read_text());model.check_freeze(frozen)
  analysis.main()
  saved=json.loads((HERE/'model_test/public_checks.json').read_text())
  assert saved['complete'] and saved['all_exact'] and len(saved['cases'])==7
 else:
  pipeline=module('ordering_saved_pipeline','s09_pipeline.py')
  pipeline.analyze=analysis;pipeline.public=public
  pipeline.main()
 finish=module('ordering_finish','s13_finish.py');finish.main()
if __name__=='__main__':main()
