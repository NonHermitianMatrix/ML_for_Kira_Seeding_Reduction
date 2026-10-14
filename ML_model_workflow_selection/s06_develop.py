"""Run bounded pilots, build, training, validation and policy freezing."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
import s03_bounds
s03_bounds.main()
sys.path.insert(0,str(HERE))
import s04_build
s04_build.main()
import s05_study as s
s.prepare()
cases=s.json.loads((HERE/'cases.json').read_text())['cases']
s.measurements(cases,'training',3)
s.train(cases)
s.measurements(cases,'validation',3)
s.freeze(cases)
s.emit(stage='development_complete')
