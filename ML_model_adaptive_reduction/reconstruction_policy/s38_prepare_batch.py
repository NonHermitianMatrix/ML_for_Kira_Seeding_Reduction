"""Freeze a timing-only implementation comparison on the verified request grid."""
from s00_reconstruction_common import *

def main():
 dest=HERE/'batch_protocol.json.gz'
 if dest.exists():return
 prior=read(HERE/'test_protocol.json.gz')
 assert all(sha(HERE/n)==h for n,h in prior['source_sha256'].items())
 assert read(HERE/'validation.json')['complete']
 cases=prior['cases']
 assert len(cases)==75
 refs={}
 for c in cases:
  p=HERE/'test_references'/(c['id']+'.json.gz')
  assert read(p)['success'];refs[c['id']]=sha(p)
 names=sorted(p.name for p in HERE.glob('s*.py') if int(p.name[1:3])<=24 or 37<=int(p.name[1:3])<=39)
 p=dict(cases=cases,repetitions=3,methods=['earlier_separate','separate','earlier_batch','batch'],
  source_sha256={n:sha(HERE/n) for n in names},
  model_sha256=prior['model_sha256'],binary_sha256=prior['binary_sha256'],
  reference_sha256=refs,preceding_protocol_sha256=sha(HERE/'test_protocol.json.gz'),
  seconds_per_separate_application=90,seconds_per_batch=330,
  purpose='Implementation regression comparison; existing verified inputs, no new fit or transfer claim.',
  timer='Complete execution including process loading, reduction, output, exit, reading returned data and cleanup; reference checking excluded from both methods.',
  workers=2)
 write(dest,p)
 print('Frozen batch comparison:',len(cases),'requests')

if __name__=='__main__':main()
