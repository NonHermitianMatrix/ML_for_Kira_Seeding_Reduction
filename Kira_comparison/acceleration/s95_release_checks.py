"""Check all declared comparison outputs before publishing the release."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={"results":720,"transfer_test":60,"expression_pilot":2,"expression_thresholds":6,"expression_preflight":18,"expression_small":18,"expression_validation":36,"expression_test":360,"expression_matched":360}
audits={};records=0
for stage,count in expected.items():
 path=HERE/(stage+"_validation.json");a=read(path)
 assert a["passed"] and a["trials"]==count,(stage,a.get("trials"))
 files=list((HERE/stage).glob("*.json.gz"));assert len(files)==count
 assert set(a["result_sha256"])=={p.name for p in files}
 for p in files:assert sha(p)==a["result_sha256"][p.name],p
 audits[stage]=dict(trials=count,exact=a.get("completed",a.get("exact_completions")),audit_sha256=sha(path))
 records+=count
d=read(HERE/"development_summary.json");assert d["all_stages_complete"]
assert sum(v["planned"] for v in d["stages"].values())==26
assert sum(v["exact_successes"] for v in d["stages"].values())==23
for stage,value in d["stages"].items():
 files=list((HERE/stage).glob("*.json.gz"));assert len(files)==value["planned"]
 assert max(p.stat().st_mtime for p in files)<=(HERE/"development_summary.json").stat().st_mtime
for filename in ["frozen_policy.json","transfer_freeze.json","expression_freeze.json","expression_matched_freeze.json"]:
 f=read(HERE/filename)
 for name,digest in f["sha256"].items():assert sha(HERE/name)==digest,(filename,name)
 for name,digest in f.get("input_sha256",{}).items():assert sha(ROOT/name)==digest,(filename,name)
plan=read(HERE/"plan.json")
for file,key in [("ML_model_seed_selection/trained_model.pt","seed_checkpoint_sha256"),("ML_model_reduction/trained_model.pt","row_checkpoint_sha256"),("ML_model_seed_selection/split_manifest.json","split_sha256")]:
 assert sha(ROOT/file)==plan[key],file
sources=list(HERE.glob("s*.py"))
for p in sources:compile(p.read_text(),str(p),"exec")
for p in HERE.glob("s*.sh"):subprocess.run(["bash","-n",str(p)],check=True)
text=(ROOT/"report/report.tex").read_text()
abstract=text.split(chr(92)+"begin{abstract}",1)[1].split(chr(92)+"end{abstract}",1)[0]
assert hashlib.sha256(abstract.encode()).hexdigest()=="1d47cda2f100fe402dc838ef7ac73952eb2098412d69c0ffd5e1d543f1d657ef"
jobs=set()
for name in ["expression_submission.json","expression_matched_submission.json"]:
 f=read(HERE/name);jobs.update(str(f[k]).split(".")[0] for k in ["array_job","audit_job"])
qstat_path=shutil.which("qstat") or str(pathlib.Path(os.environ.get("SGE_ROOT","/u/systems/UGE8.6.4"))/"bin"/os.environ.get("SGE_ARCH","lx-amd64")/"qstat")
qstat=subprocess.check_output([qstat_path,"-u","rushil"],text=True)
assert not jobs.intersection(line.split()[0] for line in qstat.splitlines() if line.split()),"Comparison jobs still active"
retained=sum(p.stat().st_blocks*512 for directory,dirs,files in os.walk(HERE) for p in [pathlib.Path(directory)/n for n in files] if p.is_file())
assert retained<190000000,retained
out=dict(passed=True,date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),audits=audits,
 declared_records=records+26,additional_native_development_records=26,
 development_summary_sha256=sha(HERE/"development_summary.json"),retained_allocated_bytes=retained,
 compiled_python_sources=len(sources),original_model_and_split_hashes_unchanged=True,
 supplied_abstract_unchanged=True,all_declared_jobs_finished=True)
(HERE/"release_validation.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:v for k,v in out.items() if k!="audits"},indent=2),flush=True)
