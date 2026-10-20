"""Draw the paper figures from saved results. Do not run reductions or training."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = read("triangle_monitor_summary.json")
    fresh = read("triangle_summary.json")
    seed = read("vacuum_learning_data.json")["ml"]
    equation = read("equation_refinement_data.json")["index_transfer"]
    retained = read("reconstruction_retained_data.json")["all"]
    original = HERE.parent / "ML_model_adaptive_reduction/triangle_reduction/training_summary.json"
    evidence = HERE / "rewrite_cost_evidence.json"
    if original.exists():
        raw = json.loads(original.read_text())
        cost = {key: raw[key] for key in [
            "complete", "training", "measured_training", "validation",
            "fixed_seconds", "model_seconds", "enabled", "fixed"
        ]}
        cost["source"] = str(original.relative_to(HERE.parent))
        cost["source_sha256"] = digest(original)
        evidence.write_text(json.dumps(cost, indent=2) + "\n")
    else:
        cost = read(evidence.name)
    assert summary["comparison_completed"] and summary["checks"] == 13401
    assert summary["application_results"] == 837
    assert not cost["enabled"]
    plt.rcParams.update({
        "font.size": 10.5, "axes.labelsize": 10.5, "axes.titlesize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 180,
    })
    blue, orange, grey = "#21618c", "#b65420", "#657079"
    out = HERE / "paper_figures"

    fig, ax = plt.subplots(figsize=(7.1, 2.55), constrained_layout=True)
    methods = ["published", "previous", "integrated"]
    for row, (method, color) in enumerate(zip(methods, [grey, blue, orange])):
        v = summary["methods"][method]
        y = [row - .10, row, row + .10]
        ax.plot([v["minimum"], v["maximum"]], [row, row], color=color, lw=1.4)
        ax.scatter(v["times"], y, s=25, color=color, alpha=.75, zorder=3)
        ax.scatter([v["median"]], [row], marker="D", s=56, color=color,
                   edgecolors="white", linewidths=.7, zorder=4)
        ax.text(v["maximum"] + .08, row, f'{v["median"]:.3f} s',
                va="center", fontsize=10)
    ax.set(yticks=range(3), yticklabels=["Preceding", "Intermediate", "Final"],
           xlabel="Complete time for 93 requests (s)", xlim=(39.8, 47.1),
           ylim=(2.45, -.45), title="Final collection: 8.8% less median time")
    ax.grid(axis="x", color=".9", lw=.7)
    fig.savefig(out / "rewrite_total.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.5), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.05, 1]})
    names = ["double_box", "nonplanar_box", "sunrise", "vacuum3", "one_scale_triangle"]
    labels = ["Planar box (5)", "Nonplanar box (5)", "Sunrise (5)",
              "Vacuum, 3 loops (5)", "Triangles (20)"]
    ax = axes[0]
    ratios = [fresh["groups"][g]["ratio"] for g in names]
    low = [r - fresh["groups"][g]["interval"][0] for r, g in zip(ratios, names)]
    high = [fresh["groups"][g]["interval"][1] - r for r, g in zip(ratios, names)]
    ax.errorbar(ratios, range(5), xerr=[low, high], fmt="o", capsize=3,
                color=blue, markersize=5, lw=1.2)
    ax.axvline(1, color=grey, ls="--", lw=1)
    ax.set(yticks=range(5), yticklabels=labels, ylim=(4.55, -.55),
           xlabel="Intermediate time / preceding time", xlim=(.45, 1.11),
           title="Fresh calls: gains vary by structure")
    ax.grid(axis="x", color=".9", lw=.7)
    ax = axes[1]
    loops = list(range(1, 14))
    values = [fresh["triangle_loops"][str(i)]["ratio"] for i in loops]
    ax.scatter(loops, values, s=28, color=blue, zorder=3)
    ax.scatter([7], [values[6]], s=35, color=orange, zorder=4)
    ax.annotate("slower at 7 loops", (7, values[6]), xytext=(4, 1.16),
                fontsize=9, arrowprops={"arrowstyle": "-", "color": grey})
    ax.axhline(1, color=grey, ls="--", lw=1)
    ax.set(xticks=[1, 3, 5, 7, 9, 11, 13], xlabel="Independent triangle loops",
           ylabel="Intermediate time / preceding time", ylim=(.4, 1.22),
           xlim=(.5, 13.5), title="Restricted product family: 1–13 loops")
    ax.grid(axis="y", color=".9", lw=.7)
    fig.savefig(out / "rewrite_scope.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.1), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.05, 1]})
    points = [seed["ratio"], equation["ratio"], retained["ratio"]]
    intervals = [seed["interval"], equation["repeat_interval"], retained["interval"]]
    ax = axes[0]
    ax.errorbar(points, range(3),
                xerr=[[r - v[0] for r, v in zip(points, intervals)],
                      [v[1] - r for r, v in zip(points, intervals)]],
                fmt="o", color=blue, capsize=3, markersize=5)
    ax.axvline(1, color=grey, ls="--", lw=1)
    ax.set(yticks=range(3),
           yticklabels=["Earlier seeds (32)", "Earlier equations (24)",
                        "With reconstruction (22)"],
           ylim=(2.55, -.55), xlim=(.915, 1.015),
           xlabel="Learned time / matched fixed time",
           title="Model-only gains depend on the test")
    ax.grid(axis="x", color=".9", lw=.7)
    ax = axes[1]
    val = [cost["model_seconds"] / cost["fixed_seconds"],
           summary["equation_validation"]["ratio"]]
    ax.scatter(val, [0, 1], color=orange, s=35, zorder=3)
    ax.axvline(1, color=grey, ls="--", lw=1)
    ax.axvline(.97, color=blue, ls=":", lw=1)
    for row, value in enumerate(val):
        ax.text(value + .025, row, f"{value:.3f}", va="center", fontsize=10)
    ax.set(yticks=[0, 1], yticklabels=["Arithmetic selector", "Equation filter"],
           ylim=(1.6, -.6), xlim=(.90, 1.89),
           xlabel="Candidate validation cost / fixed cost",
           title="Latest additions: neither accepted")
    ax.grid(axis="x", color=".9", lw=.7)
    fig.savefig(out / "rewrite_ml.pdf")
    plt.close(fig)
    sources = ["triangle_monitor_summary.json", "triangle_summary.json",
               "vacuum_learning_data.json", "equation_refinement_data.json",
               "reconstruction_retained_data.json", evidence.name]
    record = {
        "complete": True, "no_new_reductions_or_training": True,
        "sources": {s: digest(HERE / s) for s in sources},
        "figures": {p.name: digest(p) for p in out.glob("rewrite_*.pdf")},
        "collection_ratio": summary["ratio"],
        "collection_saving_percent": 100 * (1 - summary["ratio"]),
        "fresh_group_ratios": dict(zip(names, ratios)),
        "triangle_loop_ratios": dict(zip(map(str, loops), values)),
        "ml_ratios": points, "ml_intervals": intervals,
        "validation_ratios": val,
        "intervals": {
            "collection": "Three observed values; no confidence interval.",
            "fresh_groups": "Paired request bootstrap.",
            "seed": "Paired request bootstrap.",
            "equation": "Paired repetition resampling on fixed requests.",
            "reconstruction_ablation": "Paired request bootstrap.",
            "triangle_loops": "One request per loop except eight at loop one; no error bars.",
        },
    }
    (HERE / "rewrite_figure_data.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"complete": True, "figures": list(record["figures"])}))


if __name__ == "__main__":
    main()
