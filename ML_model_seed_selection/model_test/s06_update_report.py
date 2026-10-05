"""Write the scientific test-results section from the frozen evaluation summary."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    r=read(HERE/"test_results.json");curves=read(HERE/"curves.json")
    assert r["status"]=="completed" and r["model_unchanged"] and r["optimizer_updates"]==0
    overall=r["overall"];m=overall["micro"];a=overall["target_macro"];c=overall["confusion"]
    fmt=lambda x:f"{100*x:.3f}"
    values={k:fmt(m[k]) for k in ("accuracy","precision","recall","f1")}
    values.update({k:f"{c[k]:,}" for k in ("tp","tn","fp","fn")})
    values.update(prevalence=fmt(r["baseline_all_zero"]["positive_prevalence"]),
                  baseline_accuracy=fmt(r["baseline_all_zero"]["micro"]["accuracy"]),
                  exact_set=fmt(a["exact_reference_set_at_0_5"]),containment=fmt(a["reference_coverage_at_0_5"]),
                  test_bce=f'{a["binary_cross_entropy"]:.6f}',mean_ap=f'{a["average_precision"]:.6f}',
                  family_ap=f'{r["family_macro"]["average_precision"]:.6f}',brier=f'{a["brier"]:.6f}',
                  input_inference_ms=f'{1000*(r["encoding_seconds"]+r["model_inference_seconds"])/72142:.3f}')
    for k in (1,5,10,20):
        values["recall"+str(k)]=fmt(a["recall_at_"+str(k)])
        values["coverage"+str(k)]=fmt(a["reference_coverage_at_"+str(k)])
    for label in (0,1):
        rows=[v for v in curves["confidence_reliability"] if v["predicted_label"]==label]
        n=sum(v["count"] for v in rows)
        values["q"+str(label)]=fmt(sum(v["count"]*v["mean_confidence"] for v in rows)/n)
        values["q"+str(label)+"_agreement"]=fmt(sum(v["count"]*v["reference_accuracy"] for v in rows)/n)
    for prefix,group in (("single","kind:single_integral"),("expression","kind:integral_expression"),("one","loops:1")):
        for metric in ("precision","recall"):values[prefix+"_"+metric]=fmt(r["groups"][group]["micro"][metric])
    two=r["groups"]["loops:2"];two_p=two["micro"]["precision"];two_r=two["micro"]["recall"]
    if two_p is None:
        statement=("For the "+str(two["targets"])+" targets in the massless two-loop propagator family, "
                   "the model selected no seeds at this threshold, giving zero recall and undefined precision.")
    else:
        statement=("The "+str(two["targets"])+" targets in the massless two-loop propagator family gave "+
                   fmt(two_p)+r"\% precision and "+fmt(two_r)+r"\% recall.")
    statement+=(" Its predicted set exactly matched the reference for "+
               fmt(two["target_macro"]["exact_reference_set_at_0_5"])+r"\% of targets. "
               "The highest-ranked 20 candidates contained the full reference set for "+
               fmt(two["target_macro"]["reference_coverage_at_20"])+r"\% of its nonempty-reference targets.")
    values["two_loop_statement"]=statement
    text=(HERE/"report_section_template.tex").read_text(encoding="utf-8")
    for key,value in values.items():text=text.replace("@@"+key+"@@",value)
    assert "@@" not in text
    report=HERE.parent.parent/"report"
    (report/"seed_model_test.tex").write_text(text,encoding="utf-8")
    (HERE/"report_values.json").write_text(json.dumps(values,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("Wrote seed_model_test.tex from completed test_results.json",flush=True)
if __name__=="__main__":main()
