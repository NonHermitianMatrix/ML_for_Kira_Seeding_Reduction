#!/usr/bin/env python3
"""Extend reverse construction through any IBP row containing the current term."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import shutil
import signal
import time

from s00_ibp import (Family, PROJECT, ROOT, POINTS, PRIMES, complexity, dump_json,
                    key, read_json, validate_identity_dimension, physics_checks)

VALIDATION = {"bubble_two_mass", "triangle_massless_three_offshell"}
TEST = {"box_massless_four_offshell", "sunrise_two_loop_equal_mass"}
PROJECT_LIMIT = 8_000_000_000
DATA_LIMIT = 500_000_000
RSS_LIMIT_KIB = 1_800_000


def disk_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())


def guard(start=None):
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > RSS_LIMIT_KIB:
        raise RuntimeError("Memory guard reached")
    if start is not None and time.monotonic()-start > 600:
        raise RuntimeError("Family runtime guard reached")


def write_lines(path, rows):
    with Path(path).open("w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, sort_keys=True, separators=(",",":"))+"\n")
            if out.tell() > 64_000_000:
                raise RuntimeError("Per-file size guard reached")


def digest_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def add_scaled(fam, left, right, factor):
    result = left.copy()
    for a,c in right.items():
        value = result.get(a, fam.zero)+factor*c
        if value:
            result[a] = value
        else:
            result.pop(a, None)
    return result


def master_combination(fam, row, known):
    result = {}
    for a,c in row.items():
        result = add_scaled(fam, result, known[a], c)
    return result


def acceptable(fam, row):
    if len(row) > 48:
        return False
    for c in row.values():
        if len(c.numer) + len(c.denom) > 300:
            return False
        if len(fam.text(c)) > 14000:
            return False
        for sample in range(3):
            fam.evaluate(c,sample)
    return True


def build_equations(fam, seeds, start):
    equations = []
    seen = set()
    def keep(row, source):
        if not row:
            return
        lead = max(row, key=fam.order)
        if lead in fam.master_set or not fam.regular_nonzero(row[lead]):
            return
        # Keep different IBP sources even when they yield the same row.
        signature = (source["kind"], str(source.get("seed")), str(source.get("operator")), str(source.get("symmetry")), str(source.get("input_indices")))
        if signature in seen:
            return
        seen.add(signature)
        eqid = "E%06d" % (len(equations)+1)
        equations.append(dict(id=eqid, row=row, lead=lead, source=source))
    symmetry_inputs = set(seeds)
    for n,a in enumerate(seeds):
        if n % 50 == 0:
            guard(start)
        for k,vector in fam.operators():
            row = fam.operator_row(a,k,vector)
            validate_identity_dimension(fam,a,row)
            symmetry_inputs.update(row)
            keep(row,dict(kind="ibp", seed=list(a),
                          operator=dict(differentiated_loop=fam.loops[k], k=k,
                              vector_coefficients=list(vector),
                              vector_expression=str(sum(c*p for c,p in zip(vector,fam.momenta))),
                              canonical_operator_decomposition=[
                                  dict(k=k,v=v,multiplier=c) for v,c in enumerate(vector) if c])))
    for a in sorted(symmetry_inputs,key=fam.order):
        for index,symmetry in enumerate(fam.symmetries):
            row = fam.symmetry_row(a,symmetry)
            keep(row,dict(kind="symmetry", symmetry=index, input_indices=list(a)))
    return equations


def closure(fam, equations, limit, start):
    known = {a:{a:fam.one} for a in fam.masters}
    proofs = {}
    nonzero = 0
    ordered = sorted(equations,key=lambda e:(fam.order(e["lead"]),len(e["row"]),e["id"]))
    for round_index in range(5):
        changed = 0
        for index,eq in enumerate(ordered):
            if index % 100 == 0:
                guard(start)
            a = eq["lead"]
            if a in known or len(proofs) >= 2400:
                continue
            if any(b not in known for b in eq["row"] if b != a):
                continue
            row = {b:c for b,c in eq["row"].items() if b != a}
            result = master_combination(fam,row,known)
            result = {b:-c/eq["row"][a] for b,c in result.items()}
            if result and nonzero >= limit:
                continue
            if not acceptable(fam,result):
                continue
            known[a] = result
            proofs[a] = dict(equation=eq["id"], round=round_index+1,
                             dependencies=[b for b in row if b not in fam.master_set])
            changed += 1
            nonzero += bool(result)
        if not changed:
            break
    return known, proofs


def trace(fam, target, recipes, by_id, choices):
    current = target.copy()
    actions = []
    used = []
    totals = dict(divisions=0,multiplications=0,subtractions=0)
    while any(a not in fam.master_set for a in current):
        if len(actions) >= 128:
            raise ValueError("Trace length guard")
        a = max((a for a in current if a not in fam.master_set), key=fam.order)
        eqid = recipes[a]
        eq = by_id[eqid]
        assert eq["lead"] == a
        factor = current[a]/eq["row"][a]
        if not fam.regular_nonzero(current[a]):
            raise ValueError("Target coefficient vanishes at a sample")
        before = current
        current = add_scaled(fam,current,eq["row"],-factor)
        count = len(eq["row"])
        cost = dict(divisions=1,multiplications=count,subtractions=count)
        for k,v in cost.items():
            totals[k] += v
        candidates = choices[a]
        assert eqid in candidates
        actions.append(dict(pivot_indices=list(a), pivot_equation=eqid,
            allowed_pivot_equations=candidates,
            factor=fam.text(factor),
            before=fam.numeric_row(before,0), after=fam.numeric_row(current,0),
            pivot_value=fam.evaluate(eq["row"][a],0),
            target_pivot_value=fam.evaluate(before[a],0),
            factor_mod_p=fam.evaluate(factor,0),
            before_nonzeros=len(before), after_nonzeros=len(current),
            fill_in=sum(b not in before for b in current),
            cancelled_entries=sum(b not in current for b in before),
            operations=cost))
        used.append(eqid)
    return current, actions, list(dict.fromkeys(used)), totals


def generate_family(definition, args):
    start = time.monotonic()
    name = definition["id"]
    source = PROJECT/"Master_Integrals/families"/name
    master_data = read_json(source/"masters.json")
    assert master_data["status"] == "validated"
    fam = Family(definition,master_data)
    seeds = fam.seed_pool()
    equations = build_equations(fam,seeds,start)
    by_id = {e["id"]:e for e in equations}
    choices = {}
    by_seed = {}
    for e in equations:
        choices.setdefault(e["lead"],[]).append(e["id"])
        if e["source"]["kind"] == "ibp":
            for term in e["row"]:
                by_seed.setdefault(term,[]).append(e)
    known, proofs = closure(fam,equations,args.max_individual,start)
    split = "test" if name in TEST else "validation" if name in VALIDATION else "train"
    inputs, references, traces = [], [], []
    seen_targets = set()
    def accept(target, expected, construction, recipes, origin):
        if not target or not expected or not acceptable(fam,target) or not acceptable(fam,expected):
            return False
        if all(a in fam.master_set for a in target):
            return False
        if split != "train" and not any(complexity(a)["sector"] == fam.top for a in target):
            return False
        terms = fam.serialize_row(target)
        signature = hashlib.sha256(json.dumps(terms,sort_keys=True).encode()).hexdigest()
        if signature in seen_targets:
            return False
        try:
            reduced, steps, used, cost = trace(fam,target,recipes,by_id,choices)
        except (KeyError,ValueError,ZeroDivisionError):
            return False
        assert reduced == expected
        anchor = min(target,key=fam.order)
        # Target expressions have one common dimension; determine it from any term.
        anchor_sum = sum(anchor)-fam.mass_degree(target[anchor])
        for a,c in {**target}.items():
            assert fam.mass_degree(c) == sum(a)-anchor_sum
        for a,c in expected.items():
            assert fam.mass_degree(c) == sum(a)-anchor_sum
        seen_targets.add(signature)
        identifier = name+":T%05d" % (len(inputs)+1)
        seed_set = sorted({tuple(by_id[e]["source"]["seed"]) for e in used
                           if by_id[e]["source"]["kind"] == "ibp"})
        source_ids = used
        inputs.append(dict(id=identifier, family=name, split=split,
            kind="single_integral" if len(target)==1 and next(iter(target.values())) == fam.one else "integral_expression",
            terms=terms, modular_terms=fam.numeric_row(target,0), sample=0,
            integral_features=[dict(indices=list(a),**complexity(a)) for a in sorted(target,key=fam.order)],
            mass_dimension="%d*d-(%d)" % (fam.L,2*anchor_sum),
            candidate_seeds="candidate_seeds.json", equation_pool="identities.jsonl",
            master_basis="../../../Master_Integrals/families/"+name+"/masters.json",
            integral_order="protected_masters_then_sector_dots_numerator_sum_positive_sum_indices"))
        samples = [dict(sample=i, prime=PRIMES[i],
                        point={k:POINTS[i][k] for k in fam.names},
                        master_coefficients=fam.numeric_row(expected,i)) for i in range(3)]
        references.append(dict(id=identifier, family=name, split=split, origin=origin,
            master_coefficients=fam.serialize_row(expected),
            construction=construction, sufficient_seeds=[list(a) for a in seed_set],
            source_equations=source_ids,
            source_symmetries=[e for e in used if by_id[e]["source"]["kind"]=="symmetry"],
            reduction_steps=len(steps), arithmetic_operations=cost,
            optimality="known_valid_sequence; no minimum is claimed",
            samples=samples))
        traces.append(dict(id=identifier, sample=0, prime=PRIMES[0], steps=steps,
            final_master_row=fam.numeric_row(expected,0),
            system_representation="immutable source equations plus one changing target row",
            total_operations=cost))
        return True

    recipe_map = {a:p["equation"] for a,p in proofs.items()}
    for a in sorted(proofs,key=fam.order):
        if not known[a]:
            continue
        accept({a:fam.one},known[a],dict(kind="identity_closure", root_indices=list(a),
                    proof_library="construction_proofs.jsonl"),recipe_map,"individual_from_masters")

    rng = random.Random(args.seed+int(hashlib.sha256(name.encode()).hexdigest()[:8],16))
    base_scale = fam.parse(definition["invariants"][0])
    maxima = [a for a in fam.masters if complexity(a)["sector"] == fam.top]
    successful_chains = 0
    rejected_extensions = 0
    for chain in range(args.chains):
        guard(start)
        n = 1+chain % min(3,len(fam.masters))
        chosen = rng.sample(fam.masters,n)
        if split != "train" and maxima and not any(a in maxima for a in chosen):
            chosen[0] = rng.choice(maxima)
            chosen = list(dict.fromkeys(chosen))
        anchor = sum(chosen[0])
        initial = {}
        for j,a in enumerate(chosen):
            rational = fam.F(rng.choice((-3,-2,-1,1,2,3)))
            if chain % 3 == 1:
                rational *= (fam.d-2)/(fam.d-4)
            elif chain % 3 == 2:
                rational *= fam.F(j+2)/(fam.d-2)
            initial[a] = rational*base_scale**(sum(a)-anchor)
        current = initial.copy()
        history = []
        chain_recipes = {}
        emitted = False
        for depth in range(args.depth):
            old_lead = max(current,key=fam.order)
            candidates = []
            for a in current:
                for eq in by_seed.get(a,[]):
                    if a not in eq["row"] or not fam.regular_nonzero(eq["row"][a]):
                        continue
                    if fam.order(eq["lead"]) <= fam.order(old_lead):
                        continue
                    candidates.append((a,eq))
            rng.shuffle(candidates)
            selected = None
            for a,eq in candidates[:80]:
                factor = -current[a]/eq["row"][a]
                new = add_scaled(fam,current,eq["row"],factor)
                if new and acceptable(fam,new) and fam.regular_nonzero(new.get(eq["lead"],fam.zero)):
                    selected = a,eq,factor,new
                    break
            if selected is None:
                rejected_extensions += 1
                break
            a,eq,factor,new = selected
            history.append(dict(equation=eq["id"], substituted_indices=list(a),
                                added_identity_multiplier=fam.text(factor)))
            chain_recipes[eq["lead"]] = eq["id"]
            current = new
            normalization = next(iter(current.values())) if len(current)==1 else fam.one
            target = {a:c/normalization for a,c in current.items()}
            expected = {a:c/normalization for a,c in initial.items()}
            construction = dict(kind="reverse_identity_substitution", chain=chain, depth=depth+1,
                initial_master_combination=fam.serialize_row(initial),
                steps=list(history), final_divisor=fam.text(normalization))
            emitted |= accept(target,expected,construction,chain_recipes,"reverse_master_combination")
        successful_chains += emitted

    if not inputs:
        raise RuntimeError(name+": no accepted targets")
    staging = ROOT/".work"/name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    dump_json(staging/"definition.json",definition)
    dump_json(staging/"candidate_seeds.json",dict(
        bounds=dict(r_max=fam.t_top+2,s_max=2,dots_max=2,top_sector=fam.top),
        indices=[list(a) for a in seeds],
        note="All listed seeds are candidates; the solution files identify sufficient subsets."))
    dump_json(staging/"symmetries.json",fam.symmetries)
    write_lines(staging/"identities.jsonl",(
        dict(id=e["id"],source=e["source"],terms=fam.serialize_row(e["row"]),
             leading_indices=list(e["lead"]),modular_terms=fam.numeric_row(e["row"],0))
        for e in equations))
    write_lines(staging/"construction_proofs.jsonl",(
        dict(indices=list(a),equation=p["equation"],round=p["round"],
             dependencies=[list(b) for b in p["dependencies"]],
             master_coefficients=fam.serialize_row(known[a]))
        for a,p in proofs.items()))
    write_lines(staging/"inputs.jsonl",inputs)
    write_lines(staging/"references.jsonl",references)
    write_lines(staging/"elimination_traces.jsonl",traces)
    counts = {kind:sum(x["kind"]==kind for x in inputs) for kind in ("single_integral","integral_expression")}
    summary = dict(family=name,split=split,targets=len(inputs),**counts,
        masters=len(fam.masters),candidate_seeds=len(seeds),equations=len(equations),
        exact_construction_proofs=len(proofs),zero_integral_proofs=sum(not known[a] for a in proofs),
        successful_reverse_chains=successful_chains,stopped_extensions=rejected_extensions,
        elapsed_seconds=round(time.monotonic()-start,3),
        peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        status="generated_pending_validation",
        master_basis_sha256=digest_file(source/"masters.json"),
        generation=dict(seed=args.seed,chains=args.chains,depth=args.depth,max_individual=args.max_individual,
                        reverse_candidates="any_ibp_identity_containing_the_current_integral"),
        source_sha256={p.name:digest_file(p) for p in (ROOT/"s00_ibp.py",ROOT/"s01_generate_targets.py")})
    dump_json(staging/"summary.json",summary)
    if disk_bytes(ROOT) > DATA_LIMIT or disk_bytes(PROJECT) > PROJECT_LIMIT:
        raise RuntimeError("Storage guard reached")
    destination = ROOT/"families"/name
    destination.parent.mkdir(exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    staging.replace(destination)
    print(json.dumps(summary,sort_keys=True),flush=True)
    fam.text.cache_clear()
    fam.evaluate.cache_clear()
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family",action="append")
    parser.add_argument("--chains",type=int,default=24)
    parser.add_argument("--depth",type=int,default=4)
    parser.add_argument("--max-individual",type=int,default=64)
    parser.add_argument("--seed",type=int,default=20261003)
    args = parser.parse_args()
    if not (1 <= args.chains <= 100 and 1 <= args.depth <= 6 and 1 <= args.max_individual <= 128):
        parser.error("Requested bounds exceed this stage's resource limits")
    if disk_bytes(PROJECT) > PROJECT_LIMIT or shutil.disk_usage(PROJECT).free < 2_000_000_000:
        raise RuntimeError("Insufficient storage headroom")
    print(json.dumps({"physics_checks":physics_checks()}),flush=True)
    definitions = read_json(PROJECT/"Master_Integrals/families.json")["families"]
    if args.family:
        unknown = set(args.family)-{f["id"] for f in definitions}
        if unknown:
            parser.error("Unknown families: "+str(unknown))
        definitions = [f for f in definitions if f["id"] in args.family]
    for definition in definitions:
        generate_family(definition,args)
    print("Generation complete; run s02_validate_targets.py before using the data.",flush=True)


if __name__ == "__main__":
    main()
