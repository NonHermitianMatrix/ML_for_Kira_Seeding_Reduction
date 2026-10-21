"""Check the editorial comparison against saved evidence; run after rendering."""
import hashlib
import json
import re
from pathlib import Path

from s05_check_project import expand

HERE = Path(__file__).resolve().parent
TITLE = "Optimizing Methods for Feynman Integral Reduction with Kira"


def main():
    text = expand("report.tex")
    root = (HERE/"report.tex").read_text()
    assert "\\title{" + TITLE + "}" in root
    assert "\\author{}" in root and "\\date{}" in root and "pdfauthor={}" in root
    assert "This project developed" not in text
    assert "We developed and tested" in text
    data = json.loads((HERE/"method_table_data.json").read_text())
    assert data["editorial_only"] and data["scientific_runs"] == 0
    for name, digest in data["sources"].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest, name
    assert sum(r["requests"] for r in data["tensor"]) == 20
    assert sum(r["cases"] for r in data["native"]) == 43 and len(data["native"]) == 9
    # The handwritten formula table must retain the recorded paired times too.
    checks = [
        ("direct_data.json", ["summary", "groups", "vacuum_products"]),
        ("direct_data.json", ["summary", "groups", "connected_vacuum"]),
        ("tensor_reduction_data.json", ["final_tensor_comparison"]),
        ("tensor_reduction_data.json", ["final", "groups", "products"]),
        ("lightlike_data.json", ["summary", "groups", "lightlike"]),
        ("lightlike_data.json", ["summary", "groups", "symbolic"]),
        ("propagator_trees_data.json", ["groups", "propagator"]),
        ("gamma_cancellation_data.json", ["groups", "large"]),
    ]
    for name, keys in checks:
        record = json.loads((HERE/name).read_text())
        for key in keys:
            record = record[key]
        for key in ["old_seconds", "new_seconds"]:
            assert f'{record[key]:.3f}' in text, (name, key)
    triangle = json.loads((HERE/"analytic_batch_data.json").read_text())["comparisons"]["triangle_products"]
    assert triangle["previous"]["matched"] == 13
    for key in ["previous", "previous_prepared"]:
        for field in ["control_seconds", "learned_seconds"]:
            assert f'{triangle[key][field]:.3f}' in text
    for row in data["tensor"]:
        assert abs(row["control"]/row["method"]-row["speedup"]) < 1e-9
        for key in ["control", "method"]:
            assert f'{row[key]:.3f}' in text
    for row in data["native"]:
        for key in ["native", "fixed", "learned"]:
            assert f'{row["times"][key]:.3f}' in text
    for label in ["tab:integral-methods", "tab:tensor-type-summary", "tab:native-type-summary",
                  "tab:model-study-summary", "tab:tradeoffs"]:
        assert "\\label{" + label + "}" in text
    for formula in ["eq:triangle-rational", "eq:tree-bubble", "eq:tree-transfer",
                    "eq:tree-vacuum", "eq:tensor-moment", "eq:tensor-signed-recurrence",
                    "eq:checked-vacuum"]:
        assert "\\label{" + formula + "}" in text
    assert "31 requests have no completed control" in text
    assert "None" not in (HERE/"paper_native_type_rows.tex").read_text()
    assert "all integral types" in text and "disabled" in text
    assert "UVU" in (HERE/"writing_review.md").read_text()
    prior = json.loads((HERE/"project_validation.json").read_text())
    assert prior["complete"]
    for name, digest in prior["pdf_sha256"].items():
        assert hashlib.sha256((HERE/(name+".pdf")).read_bytes()).hexdigest() == digest
    log = (HERE/"report.log").read_text(errors="replace")
    assert not re.search(r"Overfull|undefined|^! ", log, re.I|re.M)
    result = dict(complete=True, editorial_only=prior["editorial_only"], title=TITLE, author_and_date_blank=True,
                  tensor_requests=20, native_requests=43, native_classes=9,
                  formulas_linked_to_derivations=True, controls_and_limits_present=True,
                  scientific_runs=prior["new_training_or_reductions"], pdf_sha256=prior["pdf_sha256"],
                  sources=data["sources"])
    (HERE/"method_table_validation.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k != "sources"}))


if __name__ == "__main__":
    main()
