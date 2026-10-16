"""Compare selective seed expansion, worker counts, and the published workflow."""
import json, os, resource, subprocess, sys, time
from pathlib import Path
import s05_study as study
import s12_graph_policy as graph

rt = study.rt
HERE, ROOT = rt.HERE, rt.ROOT
OUT = HERE / 'selective_expansion'
ACTIONS = ['adaptive1', 'rank1', 'adaptive2', 'rank2', 'published']

def cpu():
    return sum(resource.getrusage(k).ru_utime + resource.getrusage(k).ru_stime
               for k in [resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN])

class Portfolio:
    def __init__(self):
        self.frozen = json.loads((HERE/'trained_model/freeze.json').read_text())
        self.guard = json.loads((HERE/'trained_model/graph_gate.json').read_text())
        self.server = subprocess.Popen([sys.executable, str(HERE/'s13_previous_server.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        assert json.loads(self.server.stdout.readline()) == {'ready': True}

    def close(self):
        if self.server.poll() is None:
            self.server.stdin.write('{"stop":true}\n'); self.server.stdin.flush()
            self.server.wait(timeout=15)

    def direct(self, case, basis, selected, workers):
        attempts, seen = [], set()
        captured = rt.native.run
        def threaded(*args, **kwargs):
            kwargs['threads'] = workers
            return captured(*args, **kwargs)
        rt.native.run = threaded
        try:
            for action in dict.fromkeys([selected, 'native', 'expanded']):
                bounds = rt.bounds(case, 'native' if action == 'rank_plus' else action)
                if action == 'rank_plus': bounds[1] += 1
                bounds[0] = max(bounds[0], max(s.bit_count() if hasattr(s,'bit_count') else bin(s).count('1')
                    for s in case['definition']['top_level_sectors']))
                key = (tuple(bounds), 5 if action == 'order5' else 1, action == 'equation')
                if key in seen: continue
                seen.add(key)
                r = rt.attempt(case, basis, 'native' if action == 'rank_plus' else action, custom=bounds)
                r['selected_action'] = action
                attempts.append(rt.compact(r))
                if r['success']: break
            return dict(case=case['id'], success=r['success'], coefficients=r.get('coefficients', {}),
                attempts=attempts, fallback_count=len(attempts)-1, seed_action=selected, workers=workers)
        finally:
            rt.native.run = captured

    def run(self, case, basis, action, reference=None):
        start, cpu0 = time.perf_counter(), cpu()
        decision0 = time.perf_counter()
        seed = graph.select(self.frozen, self.guard, case)
        decision = time.perf_counter() - decision0
        if action == 'published' and case['topology_group'] in study.KINDS:
            self.server.stdin.write(json.dumps(dict(case=case, basis=basis, workers=2))+'\n')
            self.server.stdin.flush()
            response = json.loads(self.server.stdout.readline())
            assert 'result' in response, response
            r = response['result']
            server_cpu = r.get('cpu_seconds', 0.)
        else:
            # The previous method has no trained graph policy for bubble boxes.
            # Use its documented native fallback with the common exact build.
            seed = 'native' if action == 'published' else 'rank_plus' if action.startswith('rank') else seed
            r = self.direct(case, basis, seed, 2 if action.endswith('2') else 1)
            server_cpu = 0.
        if reference: rt.verify(case, r, reference)
        r.update(action=action, decision_seconds=decision, complete_seconds=time.perf_counter()-start,
            cpu_seconds=cpu()-cpu0+server_cpu)
        assert all(a.get('binary_sha256') == self.frozen['binary_sha256'] for a in r['attempts'])
        return r

def pilot():
    OUT.mkdir(exist_ok=True)
    cases=json.loads((HERE/'cases.json').read_text())['cases']
    p=Portfolio()
    try:
        for identifier in ['ladder3_p301_dots', 'double_box_p301_mixed']:
            case=next(c for c in cases if c['id']==identifier)
            ref=HERE/'references'/(identifier+'.json.gz');basis=rt.read(ref)['masters']
            for action in ACTIONS:
                path=OUT/'development'/f'{identifier}_{action}.json.gz'
                if path.exists():continue
                r=p.run(case,basis,action,ref);rt.save(path,r)
                study.emit(stage='portfolio_pilot',case=identifier,action=action,
                    seconds=r['complete_seconds'],success=r['success'],seed=r.get('seed_action',r.get('seed_configuration')))
                assert r['success'] and r['reference_checked']
    finally:p.close()

if __name__=='__main__':pilot()
