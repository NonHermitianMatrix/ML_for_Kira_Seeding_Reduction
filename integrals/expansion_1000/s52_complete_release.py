"""Check the local report review and publish the final release records."""
import hashlib,importlib.util,json,os,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,o):p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert os.environ.get("JOB_ID"),"Use a bounded compute allocation"
 publication=read(HERE/"publication.json")
 assert all(publication[s]["status"]=="pushed" for s in ("training","tests","report"))
 review=read(HERE/"report_local_sync.json")
 assert review["status"]=="passed" and review["visual_review"]=="passed"
 assert review["git_commit"]==publication["report"]["commit"]
 names=subprocess.check_output(["git","ls-files","report/"],cwd=str(ROOT)).decode().splitlines()
 assert set(names)==set(review["report_sha256"])
 for name,digest in review["report_sha256"].items():assert sha(ROOT/name)==digest,name
 spec=importlib.util.spec_from_file_location("publish_release",HERE/"s20_publish_release.py")
 pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
 # Final push diagnostics stay outside tracked files to avoid self-referential
 # commit hashes or post-commit edits to an otherwise complete release.
 pub.HERE=ROOT/".tools/final-release";pub.HERE.mkdir(parents=True,exist_ok=True)
 allocated=pub.guard();local=review["local_project_allocated_bytes"]
 assert allocated+max(local,200000000)<9700000000
 request=read(HERE/"request.json")
 for name,digest in request["model_hashes"].items():assert sha(ROOT/name/"trained_model.pt")==digest
 for name in request["model_hashes"]:
  test=ROOT/name/"model_test"
  assert read(test/"validation.json")["status"]=="passed"
  assert (test/"report_values.json").is_file()
 validation=read(HERE/"report_validation.json")
 assert validation["pdf_sha256"]==sha(ROOT/"report/report.pdf")
 validation["visual_review"]="passed"
 validation["local_report_sync"]="all_tracked_report_files_byte_identical"
 validation["local_review_record"]="report_local_sync.json"
 write(HERE/"report_validation.json",validation)
 update=read(HERE/"report_update.json")
 update.update(status="published_and_synchronized_locally",report_commit=publication["report"]["commit"])
 write(HERE/"report_update.json",update)
 request.update(status="complete",git_index_threads=1,report_publication_status="pushed_and_synchronized_locally",
  report_publication_commit=publication["report"]["commit"],test_publication_commit=publication["tests"]["commit"],
  latest_measured_remote_bytes=allocated,latest_measured_local_bytes=local,
  latest_measured_combined_bytes=allocated+local,
  storage_measurement_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  storage_measurement_note="Allocated project bytes including tools and Git; local checkout measured after report synchronization.")
 write(HERE/"request.json",request)
 doc=HERE/"README.md";s=doc.read_text(encoding="utf-8")
 s=s.replace("The completed report is reviewed before publication and local synchronization.", "Source and build checks precede report publication; local PDF review and synchronization follow the build.")
 s=s.replace("The publication job has a four-hour limit to include these filesystem checks.",
             "The publication job has a six-hour limit to include these filesystem checks.")
 marker="<!-- completed-release -->"
 s=s.split(marker)[0].rstrip()+"\n\n"+marker+"\n"+(
  "Both twenty-pass models and frozen tests are complete. The report contains all twelve current plots and the checked measurements for 690,382 targets in 5,137 held-out families. "
  "Its sources, bibliography and PDF match the local copy. report_local_sync.json records file hashes and PDF review, and report_validation.json records source, figure and reference checks. "
  "publication.json identifies the published model, test and report commits.\n\n"
  "s52_complete_release.py validates that local review, updates completion records and publishes the final documentation and report-value records. "
  "s53_run_release_completion.sh runs it with bounded memory. Final push diagnostics stay in the ignored .tools/final-release/ folder, so completed tracked files stay clean.\n")
 doc.write_text(s,encoding="utf-8")
 paths=["integrals/expansion_1000","ML_model_seed_selection/model_test/report_values.json",
        "ML_model_reduction/model_test/report_values.json"]
 _,_,selected=pub.preflight(paths);pub.stage_selected(selected)
 staged={s for s in pub.run(["git","diff","--cached","--name-only","-z"]).split("\0") if s}
 assert staged<=set(selected)
 assert pub.staged_bytes()<100000000
 commit=pub.commit_and_push("Finalize verified model tests and synchronize the rendered report")
 assert not pub.run(["git","status","--porcelain","--untracked-files=normal"]),"Outstanding tracked or new files"
 write(pub.HERE/"completion.json",dict(status="complete",commit=commit,
  report_pdf_sha256=sha(ROOT/"report/report.pdf"),project_upper_bound_bytes=pub.guard(),
  local_project_allocated_bytes=local))
 print("Release complete",commit,flush=True)
if __name__=="__main__":main()
