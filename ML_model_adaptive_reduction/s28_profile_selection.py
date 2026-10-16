"""Keep the full small development log to locate remaining setup costs."""
import json
import s24_parametric_runtime as app
cases=json.loads((app.HERE/'cases.json').read_text())['cases']
c=next(c for c in cases if c['id']=='bubble_box4_p301')
ref=app.HERE/'references'/(c['id']+'.json.gz')
with app.projected():r=app.rt.attempt(c,app.rt.read(ref)['masters'],reference=ref)
app.rt.save(app.OUT/'development/selection_profile.json.gz',r)
print(r['log'][:18000],flush=True)
assert r['success']
