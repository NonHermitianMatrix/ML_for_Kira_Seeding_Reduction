"""Check the rewritten paper against its saved evidence without new experiments."""
import hashlib
import json
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(name, visited=None):
    visited = set() if visited is None else visited
    assert name not in visited, name
    visited.add(name)
    text = (HERE / name).read_text()
    return re.sub(r"\\input\{([^}]+)\}",
                  lambda m: expand(m[1] + ".tex", visited), text)


def main():
    text = expand("report.tex")
    final = json.loads((HERE / "triangle_monitor_summary.json").read_text())
    figures = json.loads((HERE / "rewrite_figure_data.json").read_text())
    audit = json.loads((HERE / "paper_validation.json").read_text())
    assert final["complete"] and final["comparison_completed"]
    assert final["recorded_verified_results"] == final["recorded_application_results"] == 837
    assert final["checks"] == 13401
    for label, result in final["methods"].items():
        assert len(result["times"]) == 3
        assert result["median"] == statistics.median(result["times"])
        assert result["minimum"] == min(result["times"])
        assert result["maximum"] == max(result["times"])
        for key in ["median", "minimum", "maximum"]:
            assert f'{result[key]:.3f}' in text, (label, key)
    ratio = final["methods"]["integrated"]["median"] / final["methods"]["published"]["median"]
    assert abs(ratio - final["ratio"]) < 1e-12
    assert f"{100 * (1 - ratio):.1f}" in text
    assert sum(g["requests"] for g in final["groups"].values()) == 93
    for group in ["double_box", "nonplanar_box", "sunrise", "vacuum3"]:
        row = final["groups"][group]
        for method in ["published", "integrated"]:
            assert f'{row["seconds"][method]:.3f}' in text, (group, method)
        assert f'{row["ratio"]:.3f}' in text
    failed = final["parallel_comparison"]
    assert not failed["comparison_completed"]
    assert failed["recorded_application_results"] == 651
    assert failed["recorded_verified_results"] == 650
    assert "650" in text and "651" in text and "20 masters" in text and "16" in text
    for name, digest in figures["sources"].items():
        assert sha(HERE / name) == digest, name
    for name, digest in figures["figures"].items():
        assert sha(HERE / "paper_figures" / name) == digest, name
    assert len(figures["figures"]) == 3
    assert set(figures["triangle_loop_ratios"]) == set(map(str, range(1, 14)))
    assert figures["triangle_loop_ratios"]["7"] > 1
    assert all(r >= .97 for r in figures["validation_ratios"])
    assert audit["original_notes_reconstructable"]
    assert audit["original_supporting_files_preserved"] == 91
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    refs = set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", text))
    assert len(labels) == len(set(labels)) and refs <= set(labels)
    for label in ["eq:intro-recurrence", "eq:tadpole-derivative-proof",
                  "eq:collection-ratio", "eq:reconstruction-leaf-choice",
                  "app:triangle", "app:triangle-inputs"]:
        assert label in labels, label
    pdfs = {}
    for name in ["report", "notes"]:
        pdf = HERE / (name + ".pdf")
        assert pdf.read_bytes().startswith(b"%PDF")
        assert pdf.stat().st_size < 32 * 1024**2
        log = (HERE / (name + ".log")).read_text(errors="replace")
        assert not re.search(r"Overfull|undefined|^! ", log, re.I | re.M), name
        blg = HERE / (name + ".blg")
        if blg.exists():
            assert not re.search(r"error message|Repeated entry|I couldn.t|Warning--",
                                 blg.read_text(), re.I), name
        pdfs[name] = sha(pdf)
        assert pdfs[name] == audit["pdf_sha256"][name]
    result = {
        "complete": True, "editorial_revision_only": True,
        "new_training_or_reductions": 0, "pdf_sha256": pdfs,
        "figures": figures["figures"], "main_labels": len(labels),
        "main_references": len(refs), "source_citations_checked": True,
        "original_notes_reconstructable": True,
        "original_supporting_files_preserved": 91,
        "final_requests": 93, "final_results": 837, "coefficient_checks": 13401,
        "final_collection_ratio": ratio, "negative_results_retained": True,
        "source_files": {p.name: sha(p) for p in HERE.glob("paper_*.tex")
                         if p.name in ["paper_abstract.tex", "paper_background.tex",
                                       "paper_methods.tex", "paper_study_design.tex",
                                       "paper_results.tex", "paper_discussion.tex",
                                       "paper_conclusion.tex", "paper_project_data.tex",
                                       "paper_project_results.tex", "paper_project_appendix.tex",
                                       "paper_project_structural.tex", "paper_latest_appendix.tex"]},
    }
    (HERE / "rewrite_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
