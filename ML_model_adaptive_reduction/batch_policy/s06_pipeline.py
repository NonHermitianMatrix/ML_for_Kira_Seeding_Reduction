"""Run training, validation, fitting, and reserved comparison in order."""
from s02_collect import collect
import s04_fit,s05_test
from s00_runtime import HERE
if __name__=='__main__':
 if not (HERE/'trained_model/freeze.json').exists():
  collect('training');collect('validation');collect('validation_off');s04_fit.main()
 s05_test.main()
