"""Define disjoint physical target groups for learned seed-bound selection."""
import copy,hashlib,importlib.util,json,math,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ACTIONS=['native','rank_plus','tight','dots','rank_minus','expanded','truncate','truncate_rank_plus','truncate_dots','truncate_relaxed']
GRAPHS=['sunrise','double_box','vacuum3','ladder3','nonplanar_box','pentagon','one_mass_box','bubble_box3','bubble_box4','massless4']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def definition(kind,h):
 old=json.loads((ROOT/'ML_model_adaptive_reduction/cases.json').read_text())['cases']
 if kind in ['nonplanar_box','pentagon','one_mass_box']:
  gen=module('seed_bound_physics',ROOT/'Kira_comparison/generalization/s01_cases.py');return gen.build(kind,False,h)
 if kind.startswith('bubble_box') or kind=='massless4':
  gen=module('seed_bound_coverage',ROOT/'Kira_comparison/coverage_study/s00_cases.py')
  return gen.definition('bubble_box' if kind.startswith('bubble_box') else 'propagator_massless',int(kind[-1]),h)
 d=copy.deepcopy(next(c['definition'] for c in old if c['topology_group']==kind))
 a,b=1009+12*h,1021+14*h
 if kind in ['sunrise','ladder3']:
  d['scalarproduct_rules']=[[['p','p'],str(-a)]];d['parameters']['p2']=-a
 elif kind=='double_box':
  d['scalarproduct_rules']=[[['p1','p1'],'0'],[['p2','p2'],'0'],[['p3','p3'],'0'],[['p1','p2'],f'-{a}/2'],[['p1','p3'],f'-{b}/2'],[['p2','p3'],f'{a+b}/2']]
  d['parameters'].update(s=-a,t=-b)
 else:d['propagators'][-1]['mass_squared']=str(53+2*h);d['parameters']['masses'][-1]=53+2*h
 return d

def case(kind,h,shape,split):
 d=definition(kind,h);n=len(d['propagators']);p=d['physical_propagators'];a=[int(i<p) for i in range(n)];ts=[]
 for j in range(3):
  t=a.copy();i=(h+j)%p
  if shape=='dots':t[i]+=2
  elif shape=='mixed':
   t[i]+=1
   if n>p:t[p+(h+j)%(n-p)]=-1
   else:t[(i+1)%p]+=1
  elif shape=='pinched':t[i]=0;t[(i+1)%p]+=1
  elif shape in ['rank2','rank3','rank4']:
   if n>p:t[p+(h+j)%(n-p)]=-int(shape[-1])
   else:t[i]+=2
  elif shape=='dot':t[i]+=1
  elif shape=='numerator':
   if n>p:t[p+(h+j)%(n-p)]=-1
  elif shape!='corner':raise ValueError(shape)
  if t not in ts:ts.append(t)
 name=f'{kind}_h{h}_{shape}'
 return dict(id=name,group=f'{kind}_h{h}',topology_group=kind,split=split,definition=d,targets=ts,size=len(ts),shape=shape)
def make(split):
 profiles={'development':[501],'training':[511,512],'validation':[513],'reserved':[515,516]}[split]
 cases=[]
 for h in profiles:
  for kind in GRAPHS:
   shapes=['corner','dot','numerator'] if kind.startswith('bubble_box') or kind=='massless4' else ['dots','mixed','pinched','rank2']
   for shape in shapes:cases.append(case(kind,h,shape,split))
 assert len({c['id'] for c in cases})==len(cases)
 return cases

def bounds(c,action):
 action={'truncate':'native','truncate_rank_plus':'rank_plus','truncate_dots':'dots','truncate_relaxed':'native'}.get(action,action)
 ts=c['targets'];v=[max(sum(max(0,a) for a in t) for t in ts),max(sum(max(0,-a) for a in t) for t in ts),max(sum(max(0,a-1) for a in t) for t in ts)]
 delta={'native':(0,0,0),'rank_plus':(0,1,0),'tight':(-1,-1,-1),'dots':(-1,0,-1),'rank_minus':(0,-1,0),'expanded':(1,1,1)}[action]
 v=[max(0,a+b) for a,b in zip(v,delta)];v[0]=max(v[0],max(bin(s).count('1') for s in c['definition']['top_level_sectors']))
 return v
def truncation(c,action):
 if not action.startswith('truncate'):return None
 t=max(bin(s).count('1') for s in c['definition']['top_level_sectors']);rank=bounds(c,'native')[1]
 return t-rank-(1 if action=='truncate_relaxed' else 0)

def signature(c):
 d=c['definition']
 return json.dumps(dict(loops=d['loop_momenta'],external=d['external_momenta'],propagators=[(p['momentum'],p['mass_squared']=='0') for p in d['propagators']],physical=d['physical_propagators'],sectors=d['top_level_sectors'],invariants=d.get('invariants',[]),products=[(a,v=='0') for a,v in d['scalarproduct_rules']]),sort_keys=True)

FEATURE_NAMES=['loops','external_momenta','indices','physical_denominators','symbolic_invariants','log_targets','max_dots','max_rank','mean_dots','mean_rank','min_positive','max_positive','sectors','massive_denominators','coupled_denominators','max_loop_incidence','max_loop_degree','external_incidence','min_dots','min_rank','mean_positive','max_abs_index','dotted_massive','numerator_loop_incidence','raised_loop_degree','max_positive_sum','max_target_deficit']
def features(c):
 d=c['definition'];ts=c['targets'];lm=d['loop_momenta'];em=d['external_momenta'];p=d['physical_propagators'];prop=d['propagators']
 incidence=[[int(re.search(r'\b'+re.escape(k)+r'\b',a['momentum']) is not None) for k in lm] for a in prop];physical=incidence[:p]
 dots=[sum(max(0,a-1) for a in t) for t in ts];ranks=[sum(max(0,-a) for a in t) for t in ts];lines=[sum(a>0 for a in t) for t in ts]
 vals=[len(lm),len(em),len(prop),p,len(d.get('invariants',[])),math.log1p(len(ts)),max(dots),max(ranks),statistics.mean(dots),statistics.mean(ranks),min(lines),max(lines),len({tuple(a>0 for a in t) for t in ts}),sum(a['mass_squared']!='0' for a in prop),sum(sum(v)>1 for v in physical),max(map(sum,physical)),max(sum(row[i] for row in physical) for i in range(len(lm))),sum(sum(bool(re.search(r'\b'+re.escape(k)+r'\b',a['momentum'])) for k in em) for a in prop)/len(prop),min(dots),min(ranks),statistics.mean(lines),max(abs(a) for t in ts for a in t),statistics.mean(sum(max(0,t[i]-1) for i,a in enumerate(prop) if a['mass_squared']!='0') for t in ts),statistics.mean(sum(max(0,-t[i])*sum(incidence[i]) for i in range(len(prop))) for t in ts),statistics.mean(sum(max(0,t[i]-1)*sum(incidence[i]) for i in range(len(prop))) for t in ts),max(sum(max(0,a) for a in t) for t in ts),max(p-sum(a>0 for a in t[:p]) for t in ts)]
 assert len(vals)==len(FEATURE_NAMES);return vals
