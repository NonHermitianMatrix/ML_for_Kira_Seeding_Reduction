"""Check the primary default-Kira table against the saved measurements."""
import gzip
import hashlib
import json
import statistics
from pathlib import Path

from s05_check_project import expand

HERE = Path(__file__).resolve().parent


def main():
    data = json.loads((HERE / "default_kira_data.json").read_text())
    text = expand("report.tex")
    assert data["complete"] and data["requests"] == 20 and data["repetitions"] == 3
    rows = data["rows"]
    assert len(rows) == 20 and len({r["case"] for r in rows}) == 20
    matched = [r for r in rows if all(r["verified"].values())]
    assert len(matched) == data["matched"]
    for method in ["default", "method"]:
        for row in rows:
            assert len(row["times"][method]) == 3
            assert min(row["times"][method]) > 0
        expected = sum(statistics.median(r["times"][method]) for r in matched)
        assert abs(expected - data["seconds"][method]) < 1e-8
    if matched:
        assert abs(data["speedup"] - data["seconds"]["default"] / data["seconds"]["method"]) < 1e-10
    for name, group in data["groups"].items():
        selected = [r for r in rows if r["group"] == name]
        pairs = [r for r in selected if all(r["verified"].values())]
        assert len(selected) == group["requests"] == 5
        assert len(pairs) == group["matched"]
        for method in ["default", "method"]:
            assert group["completed"][method] == sum(r["verified"][method] for r in selected)
            expected = sum(statistics.median(r["times"][method]) for r in pairs)
            assert abs(expected - group["seconds"][method]) < 1e-8
            if pairs:
                assert f"{expected:.3f}" in text
    assert "73 analytic requests" in text
    assert "eight MiB" in text and "sixty seconds" in text
    assert "tab:comparison-questions" in text and "tab:default-kira-final" in text
    assert "secondary" in text.lower() and "incremental" in text.lower()
    original = HERE.parent / "Kira_comparison/default_kira_final"
    if original.exists():
        assert json.loads((original / "summary.json").read_text()) == data
        protocol = json.loads(gzip.decompress((original / "protocol.json.gz").read_bytes()))
        for name, digest in protocol["sources"].items():
            assert hashlib.sha256((HERE.parent / name).read_bytes()).hexdigest() == digest, name
        records = list((original / "results").glob("*.json.gz"))
        assert len(records) == 120
        checks = 0
        indexed = {}
        for path in records:
            record = json.loads(gzip.decompress(path.read_bytes()))
            key = (record["case"], record["repetition"], record["method"])
            assert key not in indexed
            indexed[key] = record
            checks += record["checks"]
            if record["verified"]:
                assert record["returncode"] == 0 and record["limit"] is None
        assert checks == data["checks"]
        for row in rows:
            for repetition in range(3):
                pair = {m: indexed[(row["case"], repetition, m)] for m in ["default", "method"]}
                assert pair["default"]["host"] == pair["method"]["host"]
                for method, record in pair.items():
                    assert record["seconds"] == row["times"][method][repetition]
            for method in ["default", "method"]:
                assert row["verified"][method] == all(indexed[(row["case"], k, method)]["verified"] for k in range(3))
    assert "The primary timing summary is produced" not in text
    prior = json.loads((HERE / "method_table_validation.json").read_text())
    result = dict(complete=True, primary_reference="original Kira 3.1; default algorithms for stated job",
                  requests=20, measured_runs=120, matched=data["matched"],
                  seconds=data["seconds"], speedup=data["speedup"],
                  all_outputs_verified=data["all_outputs_verified"],
                  other_analytic_requests_without_default_measurement=73,
                  pdf_sha256=prior["pdf_sha256"], secondary_controls_separate=True)
    (HERE / "default_comparison_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
