"""Freeze the validation-selected whole-expression interface and submit confirmation."""
import datetime,hashlib,json,pathlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
summary=read(HERE/"expression_summary.json")
policy=summary["selected_policy"]
assert policy in ("stored_ml_lower","stored_ml_lower_checked"), "No validation-qualified learned interface"
assert not (HERE/"expression_freeze.json").exists(),"Preserve the existing frozen confirmation"
protocol=read(HERE/"expression_validation_protocol.json")
for n,h in protocol["sha256"].items():assert sha(HERE/n)==h,n
baseline=read(HERE/"frozen_policy.json");plan=read(HERE/"plan.json")
names=["s01_fast_seed.py","seed_weights.npz","s69_expression_preflight.py","s78_expression_controls_worker.py","s79_expression_test_run.py","s80_expression_test_audit.py","s82_expression_test_array.sh"]
freeze=dict(date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected_policy=policy,
 policies=["stored_pool","stored_distance",policy],partition="test",cases=list(range(12)),sizes=[1,16],repetitions=5,expected_trials=360,
 threshold=.01,distance_control_budget=64,validation_summary_sha256=sha(HERE/"expression_summary.json"),
 plan_sha256=sha(HERE/"plan.json"),seed_checkpoint_sha256=plan["seed_checkpoint_sha256"],
 input_sha256=baseline["input_sha256"],sha256={n:sha(HERE/n) for n in names},
 scope="Same twelve original-held-out box instances as the native comparison; these targets have not selected the whole-expression interface. Reused physics families and targets are disclosed. Offline identity-pool generation is excluded from both supplied-equation policies.",
 resource_limits=dict(concurrent_trials=4,threads=1,child_address_space=1900000000,rss_bytes=1700000000,scratch_bytes=67108864,complete_seconds=180),
 total_project_storage_ceiling=10000000000)
(HERE/"expression_freeze.json").write_text(json.dumps(freeze,indent=2)+"\n")
job=subprocess.check_output(["qsub","-terse","-t","1-24","-tc","4",str(HERE/"s82_expression_test_array.sh")],cwd=ROOT,text=True).strip()
audit=subprocess.check_output(["qsub","-terse","-hold_jid",job.split(".")[0],str(HERE/"s84_expression_finalize.sh")],cwd=ROOT,text=True).strip()
(HERE/"expression_submission.json").write_text(json.dumps(dict(array_job=job,audit_job=audit,expected_trials=360),indent=2)+"\n")
print(json.dumps(dict(array_job=job,audit_job=audit,selected_policy=policy,expected_trials=360)),flush=True)
