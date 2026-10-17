"""Measure ordering and seed changes on development inputs only."""
import sys
from s00_engine import *
g=sys.argv[1]
cases=[make(g,901,r,s,'development') for r,s in [(3,'single'),(4,'distributed'),(4,'single')]]
actions=['previous','native']+['fixed_o'+str(o) for o in [1,2,3,4,5,6,7,8]]+['thin_o1','rank_o1','wide_o1','slope_o1','fixed_o1_p2','fixed_o1_p4']
save(HERE/'protocols'/('pilot_'+g+'.json'),dict(cases=cases,actions=actions))
for c in cases:
 for name in actions:evaluate(c,name,'pilot')
save(HERE/'pilot'/(g+'_completion.json'),dict(complete=True,cases=len(cases),actions=actions))
