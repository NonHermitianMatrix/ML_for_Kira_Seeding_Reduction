"""Make whole-project figures from saved evidence; run no new reductions."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "paper_figures"
SOURCES = {}


def read(name):
    raw = (HERE / name).read_bytes()
    SOURCES[name] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)


def main():
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "savefig.facecolor": "white"})
    old = read("paper_figure_data.json")
    general = read("general_policy_data.json")
    specialist = read("type_specialist_figure_data.json")
    basis = read("basis_completion_figure_data.json")
    scattering = read("scattering_figure_data.json")
    latest = read("rewrite_figure_data.json")
    reconstruction = read("reconstruction_data.json")
    batching = read("batching_figure_data.json")
    portfolio = read("portfolio_data.json")
    preparation = read("parametric_data.json")
    labels = old["seed_label_scores"]
    fig, ax = plt.subplots(figsize=(8.1, 3.1), constrained_layout=True)
    names = ["Candidate precision", "Candidate recall", "Complete set agreement",
             "Selected-set sufficiency", "Full-pool sufficiency"]
    values = [labels["precision"], labels["recall"], labels["set_match"],
              labels["sufficiency"], 100.0]
    ax.barh(names, values, color=["#28668d"] * 3 + ["#ab641c", "#4b7c56"])
    ax.invert_yaxis()
    for i, value in enumerate(values):
        ax.text(value - 1.1, i, f"{value:.2f}%", ha="right", va="center", color="white")
    ax.set_xlim(0, 102)
    ax.set_xlabel("Percentage within each stated test (different denominators)")
    ax.set_title("Learning the reference set does not guarantee a sufficient system")
    save(fig, "project_labels.pdf")

    original_eq = old["equation"]["aggregate"]["complete_seconds"]
    row = old["later_native"]["row"]
    ml = [
        ("Original equation filter / native", original_eq["ratio"], original_eq["interval"]),
        ("Equation filter, new indices / native", latest["ml_ratios"][1], latest["ml_intervals"][1]),
        ("Graph-specific selection / graph-fixed", specialist["aggregate"]["learned_to_family_fixed"]["ratio"],
         specialist["aggregate"]["learned_to_family_fixed"]["interval"]),
        ("Selective expansion / fixed", basis["aggregate"]["selected_to_fixed"]["ratio"],
         basis["aggregate"]["selected_to_fixed"]["interval"]),
        ("Shared structural model / fixed", general["overall"]["ratios"]["fixed"],
         general["overall"]["intervals"]["fixed"]),
        ("Retained box seed model / fixed", latest["ml_ratios"][0], latest["ml_intervals"][0]),
        ("Compiled row policy / native", row["ratio"], row["descriptive_interval"]),
        ("After reconstruction / fixed", latest["ml_ratios"][2], latest["ml_intervals"][2]),
        ("Retrained scattering equations / native", scattering["aggregate"]["equation"]["ratio"],
         scattering["aggregate"]["equation"]["interval95"]),
        ("Original row model / native (point only)", old["row_initial_ratio"], None),
    ]
    fig, ax = plt.subplots(figsize=(9.3, 5.1), constrained_layout=True)
    for y, (label, value, interval) in enumerate(ml):
        color = "#28668d" if interval is not None and interval[1] < 1 else "#ab641c"
        ax.plot(value, y, "o" if interval else "x", color=color)
        if interval:
            ax.plot(interval, [y, y], color=color, linewidth=1.6)
    ax.set_yticks(range(len(ml)))
    ax.set_yticklabels([x[0] for x in ml])
    ax.invert_yaxis()
    ax.axvline(1, color="0.35", linestyle="--", linewidth=1)
    ax.set_xlim(.86, 1.34)
    ax.set_xlabel("Selected-method time / stated control time")
    ax.set_title("ML gains depend on the action, control, and workload")
    ax.grid(axis="x", alpha=.15)
    save(fig, "project_ml.pdf")

    groups = old["cumulative"]["groups"]
    methods = [("original_kira", "Original supplied-equation Kira", "#a55229"),
               ("chain_baseline", "Later executable, same full pool", "#7b7596"),
               ("final", "Exact recurrence and reuse", "#28668d")]
    totals = {}
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.6), constrained_layout=True)
    for key, label, color in methods:
        ys = [g["medians"][key]["roundtrip_seconds"] for g in groups]
        totals[key] = sum(ys)
        axs[0].plot(range(1, 9), ys, "o-", label=label, color=color, markersize=4)
    axs[0].set_yscale("log")
    axs[0].set_ylim(.1, 300)
    axs[0].set_xlabel("Matched group")
    axs[0].set_ylabel("Complete time per group (s, logarithmic)")
    axs[0].set_xticks(range(1, 9))
    axs[0].set_title("Eight groups; five repetitions per method")
    axs[0].legend(fontsize=8, loc="center right")
    axs[0].grid(axis="y", alpha=.2)
    for y, (key, _, color) in enumerate(methods):
        value = totals[key]
        axs[1].plot(value, y, "o", color=color, markersize=7)
        axs[1].text(value, y + .15, f"{value:,.3f} s", ha="center", fontsize=9)
    axs[1].set_xscale("log")
    axs[1].set_xlim(.8, 2600)
    axs[1].set_ylim(2.5, -.5)
    axs[1].set_yticks([0, 1, 2])
    axs[1].set_yticklabels(["Original", "Later full pool", "Exact method"])
    axs[1].set_xlabel("Sum of group medians (s, logarithmic)")
    axs[1].set_title(f"Original / exact = {totals['original_kira']/totals['final']:.1f}")
    axs[1].grid(axis="x", alpha=.2)
    save(fig, "project_cumulative.pdf")

    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.7), constrained_layout=True,
                            gridspec_kw={"width_ratios": [1.25, 1]})
    loops = list(range(1, 13))
    bottom = np.zeros(12)
    statuses = [
        ("Matched reduction", "#28668d", ["verified"]),
        ("Reference/check failed", "#ab641c", ["reference_failed", "independent_check_failed"]),
        ("Above interface limit", "#acb1b7", ["unsupported_native_index_count"]),
    ]
    counts = {}
    for label, color, keys in statuses:
        vals = np.array([sum(general["by_loop"][str(l)]["counts"].get(k, 0) for k in keys)
                         for l in loops])
        counts[label] = vals.tolist()
        axs[0].bar(loops, vals, bottom=bottom, label=label, color=color)
        bottom += vals
    assert int(bottom.sum()) == 110 and sum(counts["Matched reduction"]) == 43
    axs[0].set_xticks(loops)
    axs[0].set_xlabel("Loop order in the native test grid")
    axs[0].set_ylabel("Requests")
    axs[0].set_ylim(0, 20)
    axs[0].set_title("43 of 110 requests give matched native times")
    axs[0].legend(fontsize=8, loc="upper right")
    rows = [("Shared-momentum vacuum", 12), ("Independent products", 13),
            ("Connected bubble trees", 13), ("Triangle products", 13)]
    for y, (label, maximum) in enumerate(rows):
        axs[1].plot(range(1, maximum + 1), [y] * maximum, "o-", color="#4b7c56", markersize=4)
    axs[1].set_yticks(range(len(rows)))
    axs[1].set_yticklabels([x[0] for x in rows], fontsize=9)
    axs[1].invert_yaxis()
    axs[1].set_xlim(.5, 13.5)
    axs[1].set_xticks([1, 3, 5, 7, 9, 11, 13])
    axs[1].set_xlabel("Loop order with a tested exact construction")
    axs[1].set_title("Separate, restricted analytic domains")
    axs[1].grid(axis="x", alpha=.15)
    save(fig, "project_coverage.pdf")
    result = dict(complete=True,editorial_only=True,sources=SOURCES,
                  seed_metrics=values, ml_comparisons=ml,
                  portfolio_totals=portfolio["totals"], preparation_totals=preparation["totals"],
                  vacuum_totals=totals,
                  vacuum_sum_speedup=totals["original_kira"]/totals["final"],
                  vacuum_geometric_speedup=old["cumulative"]["comparison"]["speedup"],
                  native_coverage=counts,
                  basis_sums={k:sum(c["median_seconds"][k] for c in basis["cases"])
                              for k in ["native","selected"]},
                  shared_model=general["overall"],
                  joint_native_ratio=batching["aggregate"]["joint_fixed"],
                  reconstruction_cumulative=reconstruction["cumulative"],
                  figures={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest()
                           for n in ["project_labels.pdf","project_ml.pdf",
                                     "project_cumulative.pdf","project_coverage.pdf"]})
    (HERE/"project_figure_data.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(complete=True,figures=4,vacuum_sum_speedup=result["vacuum_sum_speedup"],
                         basis_sums=result["basis_sums"])))


if __name__ == "__main__":
    main()
