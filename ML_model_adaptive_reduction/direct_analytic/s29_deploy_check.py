"""Check frozen final sources and their relation to the original experiment."""
from s00_direct_common import *
from s14_prepare import sha

def check():
 p=read(HERE/'final_protocol.json.gz');assert all(sha(HERE/n)==h for n,h in p['source_sha256'].items());assert sha(PRIOR/'trained_model/policy.json')==p['retained_model_sha256'];assert sha(HERE/'trained_model/policy.json')==p['model_sha256'];assert not read(HERE/'trained_model/policy.json')['enabled'];assert sha(PRIOR/'s05_runtime.py')==p['previous_entry_sha256']
 return p
if __name__=='__main__':check();print('Final scientific sources are unchanged.')
