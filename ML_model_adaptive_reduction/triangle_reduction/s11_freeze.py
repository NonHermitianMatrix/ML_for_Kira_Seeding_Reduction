"""Freeze the new application before reserved tests; preserve old regression cases."""
from s00_triangle_common import *
from s02_triangle_cases import native_cases,triangle_cases,triangle

def main():
 assert read(HERE/'training_summary.json')['complete'];assert read(HERE/'formula_checks.json')['complete']
 cases=native_cases('reserved')+triangle_cases('reserved')
 # More single-loop batches support a native Kira comparison at fresh scales.
 for i in range(1,8):
  ts=[[1,1,1],[1+(i%3),1+(i%2),1],[1,0,1],[2,0,1],[0,1,1]]
  c=triangle(1,211+2*i,[list(t) for t in dict.fromkeys(map(tuple,ts))],'reserved');cases.append(c)
 old=read(PRIOR/'batch_protocol.json.gz')['cases'];regression=[c for c in old if c.get('test_group')!='native']
 p=dict(cases=cases,regression=regression,actions=['previous','fixed','integrated'],repetitions=3,source_sha256={f.name:sha(f) for f in HERE.glob('s*.py') if int(f.name[1:3])<=16},model_sha256=sha(HERE/'trained_model/policy.json'),formula_checks_sha256=sha(HERE/'formula_checks.json'),baseline_commit='11f34b4c47e185a38ec201d26d83780b5902fd8b',timing='Fresh application process, output read and cleanup; external exact reference comparison excluded equally. Product formula checks at all loop orders supplement native one-loop comparisons.')
 write(HERE/'test_protocol.json.gz',p);print('frozen',len(cases),'new and',len(regression),'regression',flush=True)
if __name__=='__main__':main()
