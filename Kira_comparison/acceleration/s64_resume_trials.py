"""Resume storage-interrupted frozen trials on each original compute node."""
import datetime,hashlib,json,pathlib,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def submit(argv):
 text=subprocess.check_output(argv,cwd=ROOT,text=True).strip()
 jid=text.split()[2].split(".")[0]
 assert jid.isdigit(),text
 return int(jid),text
def main():
 old=HERE/"storage_resume.json"
 assert not old.exists(),"Resumption already submitted; inspect the recorded jobs."
 out=HERE/"results";requests=[];jobs=[]
 for case in range(12):
  for size in [16,64]:
   rows=list(out.glob("test_%02d_n%d_r*.json.gz"%(case,size)))
   if len(rows)==30:continue
   ep=out/("environment_test_%02d_sizes%d.json"%(case,size));env=json.loads(ep.read_text())
   hold="15110179"+(",15109980" if case==6 and size==64 else "")
   argv=["qsub","-q","pod_smp.q@"+env["host"],"-hold_jid",hold,"-l","h_rt=01:30:00",
    str(HERE/"s08_run.sh"),"--partition","test","--case",str(case),"--sizes",str(size),
    "--repetitions","5","--policies","frozen","--stage","results"]
   jid,text=submit(argv);jobs.append(jid)
   requests.append(dict(case=case,size=size,existing_records=len(rows),host=env["host"],job=jid,
    original_environment=env,original_environment_sha256=hashlib.sha256(ep.read_bytes()).hexdigest(),submission=text))
 transfer_env=json.loads(next((HERE/"transfer_test").glob("environment_*.json")).read_text())
 transfer,text=submit(["qsub","-q","pod_smp.q@"+transfer_env["host"],"-hold_jid","15110179",str(HERE/"s56_transfer_test.sh")])
 hold=",".join(map(str,[15109980]+jobs))
 alter=subprocess.check_output(["qalter","-hold_jid",hold,"15109981"],text=True).strip()
 release=subprocess.check_output(["qrls","15109981"],text=True).strip()
 maint,text2=submit(["qsub","-hold_jid","15110179",str(HERE/"s63_maintain_archive.sh")])
 record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason="Retained-archive guard stopped admission of new trials before their calculation. Lossless archive conversion creates headroom. Preserve every completed/failed record; resume missing records on original nodes.",
  primary=requests,transfer_job=transfer,transfer_host=transfer_env["host"],transfer_submission=text,
  archive_monitor_job=maint,archive_monitor_submission=text2,audit_dependency_update=alter,audit_hold_release=release,
  frozen_runtime_unchanged=True,original_records_unchanged=True,per_trial_limits_unchanged=True)
 old.write_text(json.dumps(record,indent=2)+"\n");print(json.dumps(record))
if __name__=="__main__":main()
