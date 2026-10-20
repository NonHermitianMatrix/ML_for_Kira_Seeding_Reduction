"""Verify the whole-project paper against existing evidence after PDF rendering."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(name, visited=None):
    visited = set() if visited is None else visited
    assert name not in visited, name
    visited.add(name)
    return re.sub(r"\\input\{([^}]+)\}",
                  lambda m: expand(m[1]+".tex", visited),
                  (HERE/name).read_text())


def main():
    text = expand("report.tex")
    data = json.loads((HERE/"project_figure_data.json").read_text())
    prior = json.loads((HERE/"rewrite_validation.json").read_text())
    assert data["complete"] and data["editorial_only"] and prior["complete"]
    for name, digest in data["sources"].items():
        assert sha(HERE/name) == digest, name
    for name, digest in data["figures"].items():
        assert sha(HERE/"paper_figures"/name) == digest, name
    assert len(data["figures"]) == 4
    assert 11_963+5_137 == 17_100 and 1_610_890+690_382 == 2_301_272
    for value in ["17,100","57,979","2,301,272","1,610,890","690,382",
                  "652,517","95.750","96.892","84.332","94.515"]:
        assert value in text, value
        assert value in (HERE/"notes.tex").read_text() or any(
            value in (HERE/n).read_text() for n in
            ["seed_model_test.tex","seed_kira_test.tex","reduction_training.tex"]), value
    for name in ["portfolio_totals", "preparation_totals"]:
        for key in ["native", "fixed", "selected"]:
            assert f'{data[name][key]:.3f}' in text
    totals = data["vacuum_totals"]
    assert abs(data["vacuum_sum_speedup"]-totals["original_kira"]/totals["final"]) < 1e-10
    assert f'{data["vacuum_sum_speedup"]:.1f}' in text
    for key in ["original_kira", "final"]:
        assert f"{totals[key]:,.3f}" in text
    assert f'{data["vacuum_geometric_speedup"]:.1f}' in text
    for key in ["native","selected"]:
        assert f'{data["basis_sums"][key]:.2f}' in text
    for key in ["native","fixed","learned"]:
        assert f'{data["shared_model"]["summed_median_seconds"][key]:.3f}' in text
    assert sum(data["native_coverage"]["Matched reduction"]) == 43
    assert sum(sum(v) for v in data["native_coverage"].values()) == 110
    assert abs(data["joint_native_ratio"]["ratio"]-.5174741975477563) < 1e-10
    cumulative = data["reconstruction_cumulative"]
    for key in ["old_seconds","new_seconds"]:
        assert f'{cumulative[key]:.3f}' in text
    assert "39.1" in text and "48.3" in text
    for phrase in ["supplied-equation", "complete candidate pool",
                   "does not prove a globally shortest", "matched fixed",
                   "failed", "reference", "13"]:
        assert phrase in text, phrase
    root=(HERE/"report.tex").read_text()
    assert "\\input{paper_project_results}" in root
    assert root.index("\\input{paper_project_results}") < root.index("\\appendix")
    assert root.index("\\input{paper_latest_appendix}") > root.index("\\appendix")
    labels=re.findall(r"\\label\{([^}]+)\}",text)
    references=set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",text))
    assert len(labels)==len(set(labels))
    assert references<=set(labels),references-set(labels)
    figs=re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}",text)
    assert len(figs)==7
    for n,h in prior["pdf_sha256"].items():
        assert sha(HERE/(n+".pdf"))==h
    result=dict(complete=True,editorial_only=True,new_training_or_reductions=0,
                whole_project_main_text=True,latest_comparison_in_appendix=True,
                source_count=len(data["sources"]),figures=len(figs),
                native_requests=110,native_matched=43,
                constructed_targets=2301272,training_targets=1610890,test_targets=690382,
                vacuum_sum_speedup=data["vacuum_sum_speedup"],
                pdf_sha256=prior["pdf_sha256"],
                negative_results_retained=True,
                original_notes_preserved=prior["original_notes_reconstructable"])
    (HERE/"project_validation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))


if __name__=="__main__":
    main()
