#!/usr/bin/env python3
"""Validate physical identities, exact constructions and numerical elimination traces."""
import argparse
import json
from pathlib import Path
import resource
import time
import sympy as sp

from s00_ibp import (Family, ROOT, PROJECT, POINTS, PRIMES, complexity, dump_json,
                    key, read_json, physics_checks)
from s01_generate_targets import add_scaled, digest_file, guard, master_combination


def lines(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def independent_ibp_check(fam, source, row):
    """Differentiate the original quadratic forms with respect to Gram variables."""
    k = source["operator"]["k"]
    vector = source["operator"]["vector_coefficients"]
    seed = tuple(source["seed"])
    directions = []
    for i in range(fam.L):
        for j in range(i,fam.L+fam.E):
            directions.append((sum(c*fam.G[v,j] for v,c in enumerate(vector)) if k == i else 0)
                              +(sum(c*fam.G[i,v] for v,c in enumerate(vector)) if k == j else 0))
    prod = sp.prod(fam.D)
    expected = vector[k]*fam.locals["d"]*prod
    for i,ai in enumerate(seed):
        if not ai:
            continue
        derivative = sum(sp.diff(fam.denominators[i],z)*dz for z,dz in zip(fam.z,directions))
        derivative = sp.expand(derivative.subs(fam.z_to_D,simultaneous=True))
        expected -= ai*derivative*sp.prod(D for j,D in enumerate(fam.D) if j != i)
    actual = sp.Integer(0)
    for a,c in row.items():
        powers = [seed[i]-a[i]+1 for i in range(fam.N)]
        assert min(powers) >= 0
        actual += c.as_expr()*sp.prod(D**power for D,power in zip(fam.D,powers))
    assert sp.Poly(sp.expand(expected-actual),*fam.D).is_zero


def validate_family(folder):
    start = time.monotonic()
    definition = read_json(folder/"definition.json")
    name = definition["id"]
    masters_path = PROJECT/"Master_Integrals/families"/name/"masters.json"
    fam = Family(definition,read_json(masters_path))
    summary = read_json(folder/"summary.json")
    assert summary["master_basis_sha256"] == digest_file(masters_path)
    for source,expected in summary["source_sha256"].items():
        assert digest_file(ROOT/source) == expected
    seed_doc = read_json(folder/"candidate_seeds.json")
    assert seed_doc["indices"] == [list(a) for a in fam.seed_pool()]
    assert read_json(folder/"symmetries.json") == fam.symmetries
    equation_docs = lines(folder/"identities.jsonl")
    by_id, choices = {}, {}
    for index,eq in enumerate(equation_docs):
        if index % 100 == 0:
            guard(start)
        source = eq["source"]
        if source["kind"] == "ibp":
            assert source["seed"] in seed_doc["indices"]
            op = source["operator"]
            assert op["differentiated_loop"] == fam.loops[op["k"]]
            vector = op["vector_coefficients"]
            assert (op["k"],tuple(vector)) in fam.operators()
            assert op["vector_expression"] == str(sum(c*p for c,p in zip(vector,fam.momenta)))
            assert op["canonical_operator_decomposition"] == [
                dict(k=op["k"],v=v,multiplier=c) for v,c in enumerate(vector) if c]
            row = fam.operator_row(source["seed"],op["k"],vector)
        else:
            assert source["kind"] == "symmetry"
            row = fam.symmetry_row(source["input_indices"],fam.symmetries[source["symmetry"]])
        assert row == fam.parse_row(eq["terms"])
        lead = max(row,key=fam.order)
        assert list(lead) == eq["leading_indices"]
        assert fam.regular_nonzero(row[lead])
        assert fam.numeric_row(row,0) == eq["modular_terms"]
        assert eq["id"] not in by_id
        by_id[eq["id"]] = dict(row=row,lead=lead,source=source)
        choices.setdefault(lead,[]).append(eq["id"])

    proofs = lines(folder/"construction_proofs.jsonl")
    known = {a:{a:fam.one} for a in fam.masters}
    used_for_independent_check = set()
    for proof in proofs:
        a = tuple(proof["indices"])
        assert a not in known
        eq = by_id[proof["equation"]]
        assert eq["lead"] == a
        rest = {b:c for b,c in eq["row"].items() if b != a}
        assert all(b in known for b in rest)
        derived = master_combination(fam,rest,known)
        derived = {b:-c/eq["row"][a] for b,c in derived.items()}
        assert derived == fam.parse_row(proof["master_coefficients"])
        assert set(map(tuple,proof["dependencies"])) == set(rest)-fam.master_set
        known[a] = derived
        used_for_independent_check.add(proof["equation"])

    input_docs = lines(folder/"inputs.jsonl")
    references = {r["id"]:r for r in lines(folder/"references.jsonl")}
    traces = {r["id"]:r for r in lines(folder/"elimination_traces.jsonl")}
    ids = [x["id"] for x in input_docs]
    assert len(ids) == len(set(ids)) == len(references) == len(traces)
    assert set(ids) == set(references) == set(traces)
    exact_steps = 0
    total_cost = dict(divisions=0,multiplications=0,subtractions=0)
    for index,inp in enumerate(input_docs):
        guard(start)
        ref, recorded_trace = references[inp["id"]], traces[inp["id"]]
        target = fam.parse_row(inp["terms"])
        expected = fam.parse_row(ref["master_coefficients"])
        assert all(a in fam.master_set for a in expected)
        assert inp["split"] == ref["split"] == summary["split"]
        assert inp["family"] == ref["family"] == name
        assert "master_coefficients" not in inp and "sufficient_seeds" not in inp
        assert "construction" not in inp and "source_equations" not in inp
        assert fam.numeric_row(target,0) == inp["modular_terms"]
        assert (folder/inp["master_basis"]).resolve() == masters_path.resolve()
        if inp["kind"] == "single_integral":
            assert len(target)==1 and next(iter(target.values())) == fam.one
        else:
            assert inp["kind"] == "integral_expression"
        assert any(a not in fam.master_set for a in target)
        if inp["split"] != "train":
            assert any(complexity(a)["sector"] == fam.top for a in target)
        construction = ref["construction"]
        if construction["kind"] == "identity_closure":
            a = tuple(construction["root_indices"])
            assert target == {a:fam.one}
            assert expected == known[a]
        else:
            assert construction["kind"] == "reverse_identity_substitution"
            initial = fam.parse_row(construction["initial_master_combination"])
            assert initial and set(initial).issubset(fam.master_set)
            current = initial
            for step in construction["steps"]:
                eq = by_id[step["equation"]]
                a = tuple(step["substituted_indices"])
                factor = fam.parse(step["added_identity_multiplier"])
                assert factor == -current[a]/eq["row"][a]
                assert fam.order(eq["lead"]) > fam.order(max(current,key=fam.order))
                current = add_scaled(fam,current,eq["row"],factor)
            divisor = fam.parse(construction["final_divisor"])
            assert target == {a:c/divisor for a,c in current.items()}
            assert expected == {a:c/divisor for a,c in initial.items()}
        first = next(iter(target))
        mass_sum = sum(first)-fam.mass_degree(target[first])
        assert inp["mass_dimension"] == "%d*d-(%d)" % (fam.L,2*mass_sum)
        for row in (target,expected):
            for a,c in row.items():
                assert fam.mass_degree(c) == sum(a)-mass_sum

        current = target.copy()
        used = []
        cost = dict(divisions=0,multiplications=0,subtractions=0)
        for step in recorded_trace["steps"]:
            a = tuple(step["pivot_indices"])
            assert a == max((b for b in current if b not in fam.master_set),key=fam.order)
            eq = by_id[step["pivot_equation"]]
            assert eq["lead"] == a
            assert step["allowed_pivot_equations"] == choices[a]
            factor = current[a]/eq["row"][a]
            assert fam.parse(step["factor"]) == factor
            after = add_scaled(fam,current,eq["row"],-factor)
            assert step["before"] == fam.numeric_row(current,0)
            assert step["after"] == fam.numeric_row(after,0)
            assert step["pivot_value"] == fam.evaluate(eq["row"][a],0)
            assert step["target_pivot_value"] == fam.evaluate(current[a],0)
            assert step["factor_mod_p"] == fam.evaluate(factor,0)
            assert step["before_nonzeros"] == len(current)
            assert step["after_nonzeros"] == len(after)
            assert step["fill_in"] == sum(b not in current for b in after)
            assert step["cancelled_entries"] == sum(b not in after for b in current)
            operation_cost = dict(divisions=1,multiplications=len(eq["row"]),subtractions=len(eq["row"]))
            assert step["operations"] == operation_cost
            for sample,prime in enumerate(PRIMES):
                numeric = fam.numeric_row(current,sample)
                pivot = fam.numeric_row(eq["row"],sample)
                f = numeric[key(a)]*pow(pivot[key(a)],-1,prime) % prime
                for b,c in pivot.items():
                    value = (numeric.get(b,0)-f*c) % prime
                    if value:
                        numeric[b] = value
                    else:
                        numeric.pop(b,None)
                assert numeric == fam.numeric_row(after,sample)
                assert f == fam.evaluate(factor,sample)
            for k,v in operation_cost.items():
                cost[k] += v
            used.append(step["pivot_equation"])
            used_for_independent_check.add(step["pivot_equation"])
            current = after
            exact_steps += 1
        assert current == expected
        assert recorded_trace["final_master_row"] == fam.numeric_row(expected,0)
        assert cost == ref["arithmetic_operations"] == recorded_trace["total_operations"]
        assert ref["reduction_steps"] == len(recorded_trace["steps"])
        assert ref["source_equations"] == list(dict.fromkeys(used))
        seeds = sorted({tuple(by_id[e]["source"]["seed"]) for e in used
                        if by_id[e]["source"]["kind"] == "ibp"})
        assert ref["sufficient_seeds"] == [list(a) for a in seeds]
        assert ref["source_symmetries"] == [e for e in dict.fromkeys(used)
                                          if by_id[e]["source"]["kind"] == "symmetry"]
        assert ref["optimality"] == "known_valid_sequence; no minimum is claimed"
        for sample in ref["samples"]:
            i = sample["sample"]
            assert sample["prime"] == PRIMES[i]
            assert sample["point"] == {k:POINTS[i][k] for k in fam.names}
            assert sample["master_coefficients"] == fam.numeric_row(expected,i)
        for k,v in cost.items():
            total_cost[k] += v

    independent_count = 0
    for identifier in sorted(used_for_independent_check):
        guard(start)
        eq = by_id[identifier]
        if eq["source"]["kind"] == "ibp":
            independent_ibp_check(fam,eq["source"],eq["row"])
            independent_count += 1
    assert summary["targets"] == len(input_docs)
    assert summary["single_integral"] == sum(x["kind"]=="single_integral" for x in input_docs)
    assert summary["integral_expression"] == sum(x["kind"]=="integral_expression" for x in input_docs)
    summary["status"] = "validated"
    dump_json(folder/"summary.json",summary)
    validation = dict(family=name,status="passed",targets=len(input_docs),
        symbolic_constructions_checked=len(input_docs),
        symbolic_elimination_steps_checked=exact_steps,
        finite_field_points_checked=3,
        equation_rows_rederived=len(by_id),
        source_ibp_rows_checked_by_independent_differentiation=independent_count,
        closure_proofs_checked=len(proofs), arithmetic_operations=total_cost,
        elapsed_seconds=round(time.monotonic()-start,3),
        peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        source_sha256={p.name:digest_file(p) for p in (ROOT/"s00_ibp.py",ROOT/"s02_validate_targets.py")})
    dump_json(folder/"validation.json",validation)
    print(json.dumps(validation,sort_keys=True),flush=True)
    fam.text.cache_clear()
    fam.evaluate.cache_clear()
    return summary,validation,ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-all",action="store_true")
    parser.add_argument("--family",action="append")
    args = parser.parse_args()
    checks = physics_checks()
    definitions = read_json(PROJECT/"Master_Integrals/families.json")["families"]
    expected = {f["id"] for f in definitions}
    folders = sorted(p for p in (ROOT/"families").iterdir() if (p/"summary.json").exists())
    if args.family:
        folders = [p for p in folders if p.name in args.family]
    assert folders
    if args.require_all:
        assert {p.name for p in folders} == expected
    summaries,validations = [],[]
    splits = dict(train=[],validation=[],test=[])
    for folder in folders:
        summary,validation,ids = validate_family(folder)
        summaries.append(summary)
        validations.append(validation)
        splits[summary["split"]].extend(ids)
    assert not (set(splits["train"])&set(splits["validation"]) or
                set(splits["train"])&set(splits["test"]) or
                set(splits["validation"])&set(splits["test"]))
    dump_json(ROOT/"splits.json",dict(
        policy="Entire families held out; validation/test targets must contain their full physical sector.",
        leakage_scope="Shared lower-sector masters remain common problem information. Held-out targets retain distinct full-family kinematics.",
        **splits))
    catalog = dict(status="validated",family_count=len(summaries),
        targets=sum(s["targets"] for s in summaries),
        single_integrals=sum(s["single_integral"] for s in summaries),
        integral_expressions=sum(s["integral_expression"] for s in summaries),
        split_counts={k:len(v) for k,v in splits.items()},
        families=[{k:s[k] for k in ("family","split","targets","single_integral","integral_expression")} for s in summaries],
        samples=[dict(id=i,prime=PRIMES[i],point=POINTS[i],role="training coefficients" if i==0 else "independent check") for i in range(3)],
        limits=dict(seed_dots=2,seed_numerator_power=2,seed_r="t_top+2"),
        scope="Constructed exact examples in the existing one-loop and two-loop families; operation counts describe known sequences, not proven optima.")
    dump_json(ROOT/"catalog.json",catalog)
    dump_json(ROOT/"validation_summary.json",dict(status="passed",physics_checks=checks,
        complete_catalog={p.name for p in folders}==expected, families=validations))
    print(json.dumps(catalog,sort_keys=True),flush=True)


if __name__ == "__main__":
    main()
