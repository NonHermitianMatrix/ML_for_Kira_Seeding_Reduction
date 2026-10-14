"""Reduce in a temporary basis, complete that basis, and check exact coefficients."""
import copy,gzip,hashlib,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'ML_model_workflow_selection/type_specialists'))
import s04_train_test as old
st=old.st
sys.path.insert(0,str(HERE))
import s00_native as native
CAP=16*1024**2
FROZEN=json.loads((st.HERE/'trained_model/freeze.json').read_text())
old.check_freeze(FROZEN)

def write(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(r,indent=2)+'\n')
def save(p,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 data=gzip.compress(json.dumps(r,separators=(',',':')).encode(),mtime=0)
 assert len(data)<1024**2
 used=sum(x.stat().st_blocks*512 for x in HERE.rglob('*') if x.is_file())
 assert used+len(data)+4096<CAP,(used,len(data))
 tmp=p.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(p)
def read(p):return st.read(p)
def emit(**r):st.emit(**r)
def cases(h,split):
 out=[];seen=set()
 for k in st.KINDS:
  for s in old.SHAPES:
   c=st.make_case(k,h,s,split)
   key=(k,tuple(map(tuple,c['targets'])))
   if key not in seen:out.append(c);seen.add(key)
 return out
def reference(c):
 p=HERE/'references'/(c['id']+'.json.gz')
 if not p.exists():
  r=st.attempt(c,None,'expanded');save(p,st.compact(r))
  emit(stage='reference',case=c['id'],success=r['success'],seconds=r['complete_seconds'])
 assert read(p)['success'],c['id']
 return p
def run_native(c,basis,delta=(0,0,0),auxiliary=False,restrict=False):
 cc=copy.deepcopy(c)
 if restrict:cc['definition']['top_level_sectors']=st.sectors(cc)
 raw,bounds=st.seed_bounds(cc,'native')
 bounds=[v+d for v,d in zip(bounds,delta)]
 st.previous.study.setup('off')
 os.environ.update(KIRA_RUNTIME_BINARY=str(st.previous.BINARY),KIRA_EPHEMERAL_DB='1')
 return native.run(cc,cc['size'],'native',HERE/'unused',timeout=120,margin=0,reference=None,
  records=False,archive=False,check_masters=not auxiliary,basis=basis,bounds=bounds,
  scratch_cap=32*1024**2,ordering=1,allow_auxiliary=auxiliary)
def complete_basis(c,basis,restricted=True):
 attempts=[];first=run_native(c,basis,auxiliary=True);attempts.append(st.compact(first))
 result=dict(success=False,attempts=attempts,status=first['status'],conversion_seconds=0.)
 if not first['success']:return result
 extra=first.get('unresolved_integrals',[])
 result['temporary_masters']=extra
 if not extra:
  result.update(success=True,status='completed',coefficients=first['coefficients']);return result
 bridge=copy.deepcopy(c);bridge.update(id=c['id']+'_basis',targets=extra,size=len(extra))
 second=run_native(bridge,basis,(1,1,1),restrict=restricted);attempts.append(st.compact(second))
 if not second['success']:result['status']=second['status'];return result
 start=time.perf_counter()
 import sympy as sp
 rows={}
 for target,row in first['coefficients'].items():
  acc={}
  for master,coefficient in row.items():
   factor=sp.sympify(coefficient.replace('^','**'),rational=True)
   for final,value in second['coefficients'].get(master,{master:'1'}).items():
    acc[final]=acc.get(final,0)+factor*sp.sympify(value.replace('^','**'),rational=True)
  rows[target]={k:str(v) for k,expr in acc.items() if (v:=sp.cancel(expr))!=0}
 result.update(success=True,status='completed',coefficients=rows,conversion_seconds=time.perf_counter()-start)
 return result
def verify(c,r,basis,ref=None):
 start=time.perf_counter();allowed={','.join(map(str,a)) for a in basis}
 rows=r.get('coefficients',{});expected={','.join(map(str,a)) for a in c['targets']}
 r['basis_admitted']=set(rows)==expected and all(set(row)<=allowed for row in rows.values())
 r['mismatches']=[];checks=0
 if ref and r['basis_admitted']:
  want=read(ref)['coefficients']
  import sympy as sp
  for t,row in rows.items():
   for m in set(row)|set(want[t]):
    checks+=1;a=row.get(m,'0');b=want[t].get(m,'0')
    if a!=b and sp.cancel(sp.sympify(a.replace('^','**'),rational=True)-sp.sympify(b.replace('^','**'),rational=True))!=0:r['mismatches'].append([t,m])
 r['success']=r['success'] and r['basis_admitted'] and not r['mismatches']
 r.update(reference_checked=bool(ref and r['success']),coefficient_checks=checks,verification_seconds=time.perf_counter()-start)
 return r
def workflow(c,basis,config,ref=None):
 start=time.perf_counter();prior=lambda:st.workflow(c,None,old.select(FROZEN,c)[0],basis)
 if config=='previous':
  r=prior();r['coefficients']=r['attempts'][-1].get('coefficients',{})
 elif config.startswith('completion'):
  r=complete_basis(c,basis,restricted=config!='completion_full')
 else:
  delta=tuple(map(int,config.split('_')[1]));a=run_native(c,basis,delta)
  r=dict(success=a['success'],status=a['status'],attempts=[st.compact(a)],coefficients=a.get('coefficients',{}))
 r.setdefault('fallback_count',0)
 if not r['success'] and config!='previous':
  fallback=prior();r['attempts'].extend(fallback['attempts'])
  r.update(success=fallback['success'],status='fallback',coefficients=fallback['attempts'][-1].get('coefficients',{}),fallback_count=1+fallback['fallback_count'])
 verify(c,r,basis,ref)
 r.update(case=c['id'],configuration=config,complete_seconds=time.perf_counter()-start)
 return r
