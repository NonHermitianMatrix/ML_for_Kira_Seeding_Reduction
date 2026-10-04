"""Audit seed supervision and prepare a reproducible grouped 70:30 split; no fitting."""
import argparse, collections, gzip, hashlib, itertools, json, pathlib, random, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "integrals"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def rows(path):
    with gzip.open(str(path), "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def group_for(d):
    if "profile" in d:
        return "box-kinematics:" + json.dumps(d["profile"]["kinematic_group"], separators=(",", ":"))
    if len(d["loop_momenta"]) != 1 or len(d["propagators"]) != 4:
        return "family:" + d["id"]
    # Identify old one-loop box profiles under propagator permutations as well.
    import sympy as sp
    ext = d["external_momenta"]
    names = ext + d["loop_momenta"] + d["invariants"]
    symbols = {n: sp.Symbol(n) for n in names}
    rules = {tuple(sorted(pair)): sp.sympify(value, locals=symbols)
             for pair, value in d["scalarproduct_rules"]}
    shifts = []
    for p in d["propagators"]:
        expr = sp.sympify(p["momentum"], locals=symbols)
        shifts.append([expr.expand().coeff(symbols[n]) for n in ext])
    values = {}
    for i, j in itertools.combinations(range(4), 2):
        c = [a-b for a,b in zip(shifts[i], shifts[j])]
        values[i,j] = sp.expand(sum(c[a]*c[b]*rules[tuple(sorted((ext[a],ext[b])))]
                                   for a in range(len(ext)) for b in range(len(ext))))
    keys = []
    for perm in itertools.permutations(range(4)):
        labels = {}
        seq = []
        for i,j in itertools.combinations(range(4),2):
            v = str(values[tuple(sorted((perm[i],perm[j])))])
            if v == "0":
                seq.append(0)
            else:
                if v not in labels: labels[v] = len(labels)+1
                seq.append(labels[v])
        keys.append(tuple(seq))
    return "box-kinematics:" + json.dumps(min(keys), separators=(",", ":"))

def main():
    cfg = read(HERE / "config.json")
    families = read(DATA / "catalog.json")["families"]
    stats = []
    hashes = {}
    ids = set()
    maxima = collections.Counter()
    for num, meta in enumerate(families):
        family = meta["family"]
        definition = DATA / meta["definition"]
        master_path = DATA / meta["master_basis"]
        inp = DATA / meta["targets_file"]
        ref = DATA / meta["references"]
        seed_path = DATA / meta["records"] / "candidate_seeds.json"
        d = read(definition)
        seeds = [tuple(s) for s in read(seed_path)["indices"]]
        assert seeds and len(seeds) == len(set(seeds)), family
        seed_set = set(seeds)
        n = len(d["propagators"])
        assert n <= cfg["max_indices"]
        assert all(len(s)==n for s in seeds)
        assert len(seeds) <= cfg["max_candidates"]
        counts = collections.Counter()
        for x,y in itertools.zip_longest(rows(inp), rows(ref)):
            assert x and y and x["id"] == y["id"], family
            assert x["family"] == y["family"] == family
            assert x["id"] not in ids
            ids.add(x["id"])
            wanted = {tuple(s) for s in y["sufficient_seeds"]}
            assert wanted <= seed_set, (x["id"], wanted-seed_set)
            assert x["terms"] and len(x["terms"]) <= cfg["max_terms"]
            assert all(len(t["indices"]) == n for t in x["terms"])
            assert all(len(t["coefficient"]) <= cfg["max_coefficient_chars"] for t in x["terms"])
            counts["targets"] += 1
            counts[x["kind"]] += 1
            counts["positive_seed_labels"] += len(wanted)
            counts["candidate_seed_labels"] += len(seeds)
            counts["empty_reference_seed_sets"] += not bool(wanted)
            maxima["terms"] = max(maxima["terms"], len(x["terms"]))
            maxima["coefficient_chars"] = max(maxima["coefficient_chars"],max(len(t["coefficient"]) for t in x["terms"]))
        assert counts["targets"] == meta["targets"]
        maxima["indices"] = max(maxima["indices"], n)
        maxima["candidates"] = max(maxima["candidates"], len(seeds))
        stats.append(dict(family=family,group=group_for(d),loops=len(d["loop_momenta"]),
                          counts=dict(counts),inputs=str(inp.relative_to(DATA)),
                          references=str(ref.relative_to(DATA)),seeds=str(seed_path.relative_to(DATA)),
                          definition=str(definition.relative_to(DATA)),
                          masters=str(master_path.relative_to(DATA))))
        for p in (definition,master_path,inp,ref,seed_path):
            hashes[str(p.relative_to(DATA))] = sha(p)
        if (num+1)%100 == 0: print("Audited",num+1,"families",flush=True)
    groups = collections.defaultdict(list)
    for x in stats: groups[x["group"]].append(x)
    two_loop_groups = sorted(k for k,v in groups.items() if any(f["loops"]==2 for f in v))
    random.Random(cfg["split_seed"]).shuffle(two_loop_groups)
    forced_train = set(two_loop_groups[:2])
    forced_test = set(two_loop_groups[2:])
    forced_weight = sum(sum(x["counts"]["targets"] for x in groups[k]) for k in forced_train)
    keys = sorted(set(groups)-forced_train-forced_test)
    random.Random(cfg["split_seed"]).shuffle(keys)
    weights = [sum(x["counts"]["targets"] for x in groups[k]) for k in keys]
    total = sum(x["counts"]["targets"] for x in stats)
    desired = round(total*cfg["train_fraction"])-forced_weight
    # Exact subset-sum search over group sizes, not over reduction solutions.
    reachable, history = 1, []
    for w in weights:
        history.append(reachable)
        reachable |= reachable << w
    chosen = min((k for k in range(sum(weights)+1) if (reachable >> k)&1),
                 key=lambda k:(abs(k-desired),k))
    remainder, train_groups = chosen, set(forced_train)
    for i in reversed(range(len(keys))):
        if not ((history[i] >> remainder)&1):
            train_groups.add(keys[i])
            remainder -= weights[i]
    assert remainder == 0
    totals = {s:collections.Counter() for s in ("train","test")}
    for x in stats:
        x["split"] = "train" if x["group"] in train_groups else "test"
        totals[x["split"]].update(x["counts"])
        totals[x["split"]]["families"] += 1
        totals[x["split"]]["two_loop_families"] += x["loops"] == 2
    summary = dict(status="prepared_untrained",source_commit=subprocess.check_output(
        ["git","rev-parse","HEAD"],cwd=str(ROOT),universal_newlines=True).strip(),
        total_targets=total,train_fraction=(chosen+forced_weight)/total,requested_train_fraction=cfg["train_fraction"],
        grouping="Complete families; all mass assignments of a box kinematic profile stay together.",
        split_unit="target with its entire candidate seed list and sufficient-set labels",
        two_loop_grouping="Two complete two-loop families in train and one in test, assigned using the fixed split seed",
        counts={s:dict(c) for s,c in totals.items()},groups=len(groups),maxima=dict(maxima),
        label_semantics="Membership in the stored sufficient seed set; not globally optimal or necessary seeds.",
        limitations=["Shared lower-sector physics can occur in both sets.",
                     "Only 3 two-loop families; this split does not establish high-loop generalization.",
                     "Candidate pools are bounded, not all points of the integral-index lattice."],
        optimizer_steps=0)
    for name, content in [("split_manifest.json",dict(schema_version=1,seed=cfg["split_seed"],families=stats)),
                          ("data_audit.json",summary),("source_hashes.json",hashes)]:
        (HERE/name).write_text(json.dumps(content,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    subprocess.check_call([sys.executable,str(DATA/"s05_prepare_model_splits.py")])
    print(json.dumps(summary,sort_keys=True),flush=True)
if __name__ == "__main__": main()
