"""Freeze the final application and fresh requests without retuning its native model."""
from s00_direct_common import *
from s14_prepare import sha
from s24_deployment_cases import cases

def main():
 assert read(HERE/'summary.json')['complete']
 if (HERE/'validation.json').exists():write(HERE/'candidate_validation.json',read(HERE/'validation.json'))
 m=read(HERE/'trained_model/policy.json');assert not m['enabled']
 original=read(HERE/'protocol.json.gz');sources=dict(original['source_sha256']);sources.update({f.name:sha(f) for f in HERE.glob('s*.py') if 23<=int(f.name[1:3])<=29})
 p=dict(cases=cases(),repetitions=3,seconds_per_application=30,source_sha256=sources,model_sha256=sha(HERE/'trained_model/policy.json'),retained_model_sha256=sha(PRIOR/'trained_model/policy.json'),prior_commit=original['prior_commit'],previous_entry_sha256=original['previous_entry_sha256'],initial_protocol_sha256=sha(HERE/'protocol.json.gz'),deployment_rule='If the replacement model fails validation, retain the preceding native policy; exact extensions remain enabled.')
 assert len(p['cases'])==69;write(HERE/'final_protocol.json.gz',p);print('Final deployment frozen',len(p['cases']),flush=True)
if __name__=='__main__':main()
