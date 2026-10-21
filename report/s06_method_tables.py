"""Create the study's type-by-type tables from saved measurements only."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def write(name, text):
    (HERE / name).write_text(text.rstrip() + "\n")


def main():
    tensor = read("tensor_reduction_data.json")["final"]["rows"]
    groups = [
        ("Massive bubbles", ("tensor_P2_N3_massive", "tensor_P2_N4_massive")),
        ("Massive triangles", "tensor_P3_N4_massive"),
        ("Massive boxes", "tensor_P4_N5_massive"),
        ("Massless bubble", "tensor_P2_N3_massless"),
        ("Mixed-mass bubble", "tensor_P2_N4_mixed"),
        ("Mixed-mass triangle", "tensor_P3_N4_mixed"),
        ("Mixed-mass box", "tensor_P4_N5_mixed"),
    ]
    lines = []
    tensor_rows = []
    for title, prefix in groups:
        prefixes = (prefix,) if isinstance(prefix, str) else prefix
        rows = [r for r in tensor if any(r["case"].startswith(p + "_") for p in prefixes)]
        assert rows, prefix
        assert all(all(r["success"][m]) for r in rows for m in ["previous", "integrated"])
        old = sum(r["median_seconds"]["previous"] for r in rows)
        new = sum(r["median_seconds"]["integrated"] for r in rows)
        lines.append(f"{title} & {len(rows)} & {old:.3f} & {new:.3f} & "
                     f"${old/new:.2f}\\times$ & ${100*(1-new/old):.1f}\\%$ \\\\")
        tensor_rows.append(dict(name=title, requests=len(rows), control=old,
                                method=new, speedup=old/new, saving=100*(1-new/old)))
    assert sum(r["requests"] for r in tensor_rows) == 20
    TENSOR_HEADER = r"""\begin{table}[!htbp]\centering\small
\caption{Exact one-loop numerator reduction by integral type. These gains use angular reduction, power recurrences, and factored coefficient arithmetic. The tensor-order ML model was disabled. Times are sums of three-run request medians.}
\label{tab:tensor-type-summary}
\begin{tabularx}{\linewidth}{@{}Yrrrrr@{}}\toprule
Integral type & Requests & Before (s) & Exact (s) & Speedup & Less time\\\midrule
"""
    TENSOR_FOOTER = r"""
\bottomrule\end{tabularx}
\end{table}"""
    write('paper_tensor_type_rows.tex', TENSOR_HEADER + "\n".join(lines) + TENSOR_FOOTER)

    data = read("general_policy_data.json")
    classes = [
        ("bubble_box", "Box with bubble insertions", r"Four-point scattering with bubble subgraphs~\cite{Weinzierl2022}."),
        ("ladder", "Four-point ladder", r"Four-particle scattering, including planar double boxes~\cite{Smirnov1999}."),
        ("nonplanar_box", "Nonplanar double box", r"Crossed two-loop four-point integrals~\cite{Tausk1999}."),
        ("one_mass_box", "One-virtuality box", r"Four-point amplitudes with one off-shell leg~\cite{DennerDittmaier2006}."),
        ("pentagon", "Pentagon", r"Five-parton QCD scattering amplitudes~\cite{Agarwal2024}."),
        ("propagator_massive", "Massive two-point", r"Mass-dependent propagator corrections~\cite{Weinzierl2022}."),
        ("propagator_massless", "Massless two-point", r"Massless propagator corrections and QCD renormalization~\cite{Ruijl2017Forcer}."),
        ("vacuum_all_mass", "Distinct-mass vacuum", r"Massive vacuum sectors in heavy-quark matching~\cite{SchroderSteinhauser2006}."),
        ("vacuum_one_mass", "One-mass vacuum", r"Massive vacuum sectors in heavy-quark matching~\cite{SchroderSteinhauser2006}."),
    ]
    lines = []
    native_rows = []
    for key, name, context in classes:
        row = data["by_family_class"][key]
        cases = [r for r in data["rows"] if r["group"] == key or r["group"].startswith(key + "_L")]
        assert len(cases) == row["cases"]
        loops = sorted({r["loops"] for r in cases})
        loop_text = str(loops[0]) if len(loops) == 1 else f"{loops[0]}--{loops[-1]}"
        t = row["summed_median_seconds"]
        for method in ["native", "fixed", "learned"]:
            assert abs(t[method] - sum(r["medians"][method] for r in cases)) < 1e-9
        sn, sf = (100*(1-row["ratios"][m]) for m in ["native", "fixed"])
        lo, hi = row["intervals"]["fixed"]
        lines.append(f"{name}, {loop_text} loop{'s' if loop_text != '1' else ''} & {context} & "
                     f"{row['cases']} & {t['native']:.3f} & {t['fixed']:.3f} & {t['learned']:.3f} & "
                     f"${sn:+.1f}\\%$ / ${sf:+.1f}\\%$ & $[{lo:.3f},{hi:.3f}]$ \\\\ \\addlinespace[3pt]")
        native_rows.append(dict(name=name, loops=loops, cases=row["cases"], times=t,
                                saving_native=sn, saving_fixed=sf,
                                fixed_ratio_interval=[lo, hi]))
    assert sum(r["cases"] for r in native_rows) == 43
    NATIVE_HEADER = r"""\begin{landscape}
\small\setlength{\tabcolsep}{5pt}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.8cm}>{\raggedright\arraybackslash}p{4.4cm}rrrr>{\raggedright\arraybackslash}p{3.1cm}>{\raggedright\arraybackslash}p{3.1cm}@{}}
\caption{Secondary shared-model comparisons for every completed physical class. The native and fixed controls use the same earlier implementation as the model; the unmodified default-Kira comparison appears in Table~\ref{tab:default-kira-final}. Times sum request medians; negative savings mean slower. The last column gives the learned/fixed time-ratio interval from the saved paired resampling. An interval containing one leaves the added gain unresolved. Small classes do not establish population-level transfer.}\label{tab:native-type-summary}\\
\toprule
Integral class and matched loops & Physical context & Cases & Native (s) & Fixed (s) & ML (s) & Saving vs native / fixed & ML/fixed interval\\\midrule
\endfirsthead
\multicolumn{8}{l}{\tablename~\thetable\ continued}\\
\toprule Integral class and matched loops & Physical context & Cases & Native (s) & Fixed (s) & ML (s) & Saving vs native / fixed & ML/fixed interval\\\midrule
\endhead
\bottomrule\endfoot
"""
    NATIVE_FOOTER = r"""
\end{longtable}
\end{landscape}"""
    write('paper_native_type_rows.tex', NATIVE_HEADER + "\n".join(lines) + NATIVE_FOOTER)

    sources = ["tensor_reduction_data.json", "general_policy_data.json",
               "lightlike_data.json", "direct_data.json", "analytic_batch_data.json",
               "propagator_trees_data.json", "gamma_cancellation_data.json",
               "project_figure_data.json", "triangle_monitor_summary.json"]
    evidence = dict(editorial_only=True, scientific_runs=0, tensor=tensor_rows, native=native_rows,
                    sources={n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in sources})
    write("method_table_data.json", json.dumps(evidence, indent=2))
    print(json.dumps(dict(tensor_requests=20, native_requests=43, scientific_runs=0)))


if __name__ == "__main__":
    main()
