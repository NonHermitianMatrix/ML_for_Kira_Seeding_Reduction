"""Write the test section and documentation from validated fixed results."""
import argparse,re
from s00_test_common import *
def replace_text(path,old,new):
    text=path.read_text(encoding="utf-8")
    if old in text:path.write_text(text.replace(old,new),encoding="utf-8")
    elif new not in text:raise ValueError("Missing expected report passage: "+str(path))
def marker(path,name,text):
    start="<!-- "+name+":start -->";end="<!-- "+name+":end -->"
    body=path.read_text(encoding="utf-8")
    if start in body:body=body[:body.index(start)]+start+"\n"+text+"\n"+body[body.index(end):]
    else:body=body.rstrip()+"\n\n"+start+"\n"+text+"\n"+end+"\n"
    path.write_text(body,encoding="utf-8")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--validate-build",action="store_true");args=ap.parse_args()
    r=read(TEST/"test_results.json");v=read(TEST/"validation.json")
    assert v["status"]=="passed" and r["weights_unchanged"] and r["optimizer_updates"]==0
    assert sha(MODEL/"trained_model.pt")==test_config()["model_sha256"]
    if args.validate_build:
        log=(ROOT/"report/report.log").read_text(encoding="utf-8",errors="replace")
        assert "undefined references" not in log.lower() and "undefined citations" not in log.lower()
        assert not re.search(r"(Reference|Citation).*undefined",log)
        assert "Overfull" not in log
        artifacts={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/"report").rglob("*") if p.is_file() and p.suffix in (".tex",".bib",".pdf")}
        write_json(TEST/"report_validation.json",dict(status="passed",model_sha256=sha(MODEL/"trained_model.pt"),
            report_hashes=artifacts,report_pdf_bytes=(ROOT/"report/report.pdf").stat().st_size,
            undefined_references=False,undefined_citations=False,overfull_boxes=False))
        print("Report build and hashes checked",flush=True);return
    s=r["overall"];m=r["model"];g=r["greedy"];two=r["groups"]["2"]
    ties=read(TEST/"tie_metrics.json")["overall"];pair=read(TEST/"paired_comparison.json")
    targets=list(rows(TEST/"target_metrics.jsonl.gz"));kind=collections.Counter(t["kind"] for t in targets)
    assert sum(kind.values())==72142 and set(kind)=={"single_integral","integral_expression"}
    num=lambda x:format(int(x),",")
    pct=lambda x:format(100*x,".3f")
    dec=lambda x:format(x,".4f")
    values=dict(SINGLE=num(kind["single_integral"]),EXPRESSIONS=num(kind["integral_expression"]),
        STATES=num(s["states"]),CHOICES=num(s["choice_states"]),FORCED=num(s["forced_states"]),
        TOP1=pct(s["top1"]),TOP3=pct(s["top3"]),SAMEROW=pct(s["equivalent_next_row"]),
        TARGETMACRO=pct(r["target_mean_top1"]),FAMILYMACRO=pct(r["family_mean_top1"]),
        CONFIDENCE=pct(s["mean_confidence"]),ECE=dec(s["ece"]),NLL=dec(s["nll"]),BRIER=dec(s["brier"]),
        TIES=pct(ties["top_tie_fraction"]),TIENEUTRAL=pct(ties["tie_neutral_top1"]),
        ONELOOP=pct(r["groups"]["1"]["state_metrics"]["top1"]),TWOLOOP=pct(two["state_metrics"]["top1"]),
        TWOCHOICES=num(two["state_metrics"]["choice_states"]),TWOSAMEROW=pct(two["state_metrics"]["equivalent_next_row"]),
        SUCCESS=num(m["success_all_samples"]),SUCCESSPCT=pct(m["success_all_samples"]/r["targets"]),
        GREEDYSUCCESS=num(g["success_all_samples"]),GREEDYSUCCESSPCT=pct(g["success_all_samples"]/r["targets"]),
        BLOCKED=num(m["statuses"].get("no_allowed_action",0)),
        BOUNDED=num(sum(m["statuses"].get(k,0) for k in ("row_limit","input_limit","step_limit"))),
        SAMPLEFAIL=num(m["statuses"].get("complete",0)-m["success_all_samples"]),
        TWOSUCCESS=num(two["model"]["success_all_samples"]),TWOGREEDYSUCCESS=num(two["greedy"]["success_all_samples"]),
        FEWER=num(m["lower"]),EQUAL=num(m["equal"]),MORE=num(m["higher"]),
        COMMON=num(pair["common_successful_nonzero_reference_targets"]),
        LESSGREEDY=num(pair["model_fewer_than_greedy"]),SAMEGREEDY=num(pair["same_committed_operation_counts"]),
        MOREGREEDY=num(pair["model_more_than_greedy"]),
        MODELTIME=dec(m["mean_runtime_ms"]),GREEDYTIME=dec(g["mean_runtime_ms"]),
        TIMERATIO=format(pair["mean_runtime_ratio"],".2f"),MODELMEDIAN=dec(m["median_runtime_ms"]),GREEDYMEDIAN=dec(g["median_runtime_ms"]))
    relation="more" if m["success_all_samples"]>g["success_all_samples"] else "fewer" if m["success_all_samples"]<g["success_all_samples"] else "the same number of"
    time_relation="higher" if m["mean_runtime_ms"]>g["mean_runtime_ms"] else "lower"
    values["INTERPRETATION"]=(
        "The learned policy completed "+relation+" targets than the fixed local rule\n"
        "and had a "+time_relation+" mean measured reduction time. "
        +("The present implementation therefore provides no speedup over this local rule.\n" if time_relation=="higher" else
          "This time comparison applies to the stated implementation and test collection.\n")
        +"The operation-count comparison above measures the cost of the completed\n"
        "paths, while the failure counts identify targets whose supplied equations\n"
        "did not support the sequence selected by the policy.")
    failed=collections.defaultdict(set)
    for row in targets:
        if row["greedy"]["status"]=="complete" and not row["greedy"]["success_all_samples"]:
            failed[row["family"]].add(row["id"])
    sample_counts=collections.Counter();details=[]
    for fid,ids in failed.items():
        for row in rows(TEST/"families"/fid/"trajectories.jsonl.gz"):
            if row["id"] in ids:
                checks=row["greedy"]["sample_checks"]
                sample_counts.update(c["status"] for c in checks if not c["agreement"])
                details.append(dict(target=row["id"],sample_statuses=[c["status"] for c in checks]))
    write_json(TEST/"additional_sample_failures.json",dict(policy="greedy",complete_but_not_all_samples=len(details),
        failed_sample_statuses=dict(sample_counts),details=details))
    if values["BOUNDED"]=="0" and values["SAMPLEFAIL"]=="0":
        values["MODELFAILURES"]=(
            "The remaining "+values["BLOCKED"]+" learned paths stopped at a row with\n"
            "no allowed next action. Every completed learned path matched all three\n"
            "samples, and all attempts stayed within the prescribed size and step bounds.")
    else:
        values["MODELFAILURES"]=(
            "The learned policy stopped with no allowed action for "+values["BLOCKED"]+" targets,\n"
            "reached a size or step bound for "+values["BOUNDED"]+" targets, and completed\n"
            +values["SAMPLEFAIL"]+" paths that failed at least one coefficient comparison.")
    values["GREEDYBLOCKED"]=num(g["statuses"].get("no_allowed_action",0))
    values["GREEDYSAMPLEFAIL"]=num(g["statuses"].get("complete",0)-g["success_all_samples"])
    values["GREEDYPRIMARY"]=num(g["success_primary"])
    template=(TEST/"report_template.tex").read_text(encoding="utf-8")
    for k,value in values.items():template=template.replace("@@"+k+"@@",value)
    assert "@@" not in template
    (ROOT/"report/reduction_test.tex").write_text(template,encoding="utf-8")
    write_json(TEST/"report_values.json",values)
    report=ROOT/"report/report.tex"
    replace_text(report,r"\input{reduction_model}"+"\n",r"\input{reduction_model}"+"\n"+r"\input{reduction_test}"+"\n") if r"\input{reduction_test}" not in report.read_text(encoding="utf-8") else None
    replace_text(report,"seed-selection test results, and reduction-model training","seed-selection and reduction-model test results")
    replace_text(report,"describes the implemented next-step model for reduction propagation.",
        "describes the implemented next-step model for reduction propagation,\nand Section~\\ref{sec:reduction-test} gives its held-out results.")
    replace_text(report,"Measurements of complete reduction time remain a later stage.",
        "Section~\\ref{sec:reduction-test} measures complete target-row sequences\nand their selection costs. Measurements of full Kira jobs remain a later stage.")
    replace_text(report,"We will\nmeasure model accuracy and performance in subsequent studies.",
        "Sections~\\ref{sec:seed-test-results} and \\ref{sec:reduction-test}\nmeasure the two models on the current grouped split.")
    replace_text(ROOT/"report/Makefile","reduction_training.tex references.bib","reduction_training.tex reduction_test.tex references.bib")
    training=ROOT/"report/reduction_training.tex"
    replace_text(training,"the training history; the final parameters have not been evaluated\non the reserved families.",
        "the training history. Section~\\ref{sec:reduction-test} evaluates the\nfinal parameters on the reserved families.")
    replace_text(training,
        "rank the supplied steps at a current state. Tests of full learned\nreduction sequences, confidence calibration, unseen families and\nintegration into Kira remain subsequent stages. In particular, the\npresent training measurements establish neither a minimum operation\ncount nor an end-to-end reduction speedup.",
        "rank the supplied steps at a current state. Section~\\ref{sec:reduction-test}\ntests complete learned target-row sequences on reserved families and\ncompares confidence with recorded-action agreement. The training\nmeasurements above describe fitting on the training data. Minimum\noperation counts and performance in complete Kira jobs require\nseparate studies.")
    bib=ROOT/"report/references.bib"
    entries=r"""
@misc{GuoCalibration,
  author = {Guo, Chuan and Pleiss, Geoff and Sun, Yu and Weinberger, Kilian Q.},
  title = {On Calibration of Modern Neural Networks},
  year = {2017},
  eprint = {1706.04599},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  note = {\href{https://arxiv.org/abs/1706.04599}{arXiv:1706.04599}; Proceedings of ICML 2017}
}
@misc{ReductionModelTestData,
  author = {Saraswat, Rushil},
  title = {Frozen Reduction-Propagation Model: Held-Out Predictions, Paths and Test Results},
  year = {2026},
  howpublished = {\href{https://github.com/NonHermitianMatrix/ML_for_Kira_Seeding_Reduction/tree/main/ML_model_reduction/model_test}{GitHub test records}},
  note = {Saved-model hash and input provenance accompany the probability records, exact sampled paths, metrics and figures; accessed 5 October 2026}
}
"""
    content=bib.read_text(encoding="utf-8")
    if "{ReductionModelTestData," not in content:bib.write_text(content.rstrip()+"\n"+entries,encoding="utf-8")
    summary=(f"The frozen reduction model was tested on {r['targets']:,} targets in {r['families']} held-out families. "
             f"It matched {100*s['top1']:.3f}% of recorded choices on {s['choice_states']:,} states with at least two actions. "
             f"Complete learned paths matched all three sampled master expansions for {m['success_all_samples']:,} targets; "
             f"the fixed local rule passed {g['success_all_samples']:,}. "
             f"Mean attempted reduction times were {m['mean_runtime_ms']:.4f} ms and {g['mean_runtime_ms']:.4f} ms, respectively. "
             "Reference paths are valid without a proof of minimality. These are target-row tests; no full Kira speedup was measured.")
    marker(MODEL/"README.md","completed-testing",summary+"\n\n"
        "See [model_test/README.md](model_test/README.md) for saved predictions, complete paths, metric definitions, six figures and reproduction commands. "
        "The model weights and training records are unchanged. Historical training status files describe the state at training completion. "
        "After regenerating training-only report text, run the test report updater to restore the current cross-references.")
    replace_text(MODEL/"README.md",
        "Testing, probability calibration, complete learned rollouts and Kira timing comparisons remain separate tasks.",
        "The fixed model has now been tested through complete target-row sequences and confidence reliability measurements in model_test/. "
        "Fitting a calibration map and full Kira timing comparisons remain separate tasks.")
    replace_text(MODEL/"README.md","These are training measurements; held-out testing and calibration remain deferred.",
        "These are training measurements. The completed held-out comparison is recorded below; no calibration map has been fitted.")
    replace_text(ROOT/"README.md","held-out testing remains separate.",
        "completed held-out results appear in [model_test/](ML_model_reduction/model_test/README.md) and Section 10 of the report.")
    marker(ROOT/"README.md","reduction-test",summary)
    marker(ROOT/"report/README.md","reduction-test",
        "reduction_test.tex contains the frozen reduction-model test and six new PDF figures in figures/. "
        "The report covers recorded-choice agreement, confidence, complete sampled reductions, operation counts and timing. "
        "Raw probability archives and exact trajectories stay in ML_model_reduction/model_test/ on Hoffman and GitHub. "
        "The sources, bibliography, figures and rendered PDF are also synchronized locally.")
    marker(ROOT/"integrals/testing/README.md","reduction-test",
        "The trained reduction-propagation model has now used this reserved view for frozen evaluation. "
        "No records from this view were added to training, and no parameters, confidence map or data split were adjusted. "
        "The resulting probabilities, paths, comparisons and figures are in ../../ML_model_reduction/model_test/.")
    marker(TEST/"README.md","test-results",summary)
    print(json.dumps(dict(report="report/reduction_test.tex",values=values)),flush=True)
if __name__=="__main__":main()
