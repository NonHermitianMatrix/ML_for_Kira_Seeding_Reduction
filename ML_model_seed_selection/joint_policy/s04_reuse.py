"""Bounded exact reuse under a common positive change of the momentum scale."""
import collections,json
from fractions import Fraction

class ScaleCache:
 def __init__(self,max_bytes=1024**2,max_entries=32):
  self.entries=collections.OrderedDict();self.max_bytes=max_bytes;self.max_entries=max_entries;self.bytes=0

 def identify(self,c,basis,signatures):
  from s00_engine import inputs
  d=c['definition']
  if d.get('cut_propagators') or d.get('symbolic_ibp') or d.get('invariants'):return None
  if any(p['mass_squared']!='0' for p in d['propagators']):return None
  sig=inputs.signature(c)
  if sig not in signatures:return None
  try:values=[Fraction(v) for _,v in d['scalarproduct_rules']]
  except (ValueError,TypeError,ZeroDivisionError):return None
  scale=next((abs(v) for v in values if v),None)
  if scale is None:return None
  key=json.dumps([sig,[str(v/scale) for v in values],sorted(c['targets']),sorted(basis)],separators=(',',':'))
  return key,scale

 def get(self,identity):
  if identity is None:return None
  key,scale=identity
  if key not in self.entries:return None
  self.entries.move_to_end(key);saved=self.entries[key];ratio=scale/saved['scale'];rows={}
  for t,row in saved['coefficients'].items():
   target_sum=sum(map(int,t.split(',')));out={}
   for m,c in row.items():
    factor=ratio**(sum(map(int,m.split(',')))-target_sum)
    out[m]=c if factor==1 or c=='0' else '('+str(factor)+')*('+c+')'
   rows[t]=out
  return dict(success=True,coefficients=rows,route='exact_scale_reuse',scale_ratio=str(ratio),fallbacks=0,attempts=[],reference_coefficients_supplied=False)

 def put(self,identity,result):
  if identity is None or not result.get('success'):return
  key,scale=identity;coefficients=result['coefficients']
  raw=json.dumps([key,str(scale),coefficients],separators=(',',':'));size=len(raw.encode())
  if size>self.max_bytes:return
  if key in self.entries:self.bytes-=self.entries.pop(key)['bytes']
  while self.entries and (self.bytes+size>self.max_bytes or len(self.entries)>=self.max_entries):self.bytes-=self.entries.popitem(last=False)[1]['bytes']
  self.entries[key]=dict(scale=scale,coefficients=json.loads(json.dumps(coefficients)),bytes=size);self.bytes+=size
