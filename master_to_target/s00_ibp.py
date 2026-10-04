#!/usr/bin/env python3
"""Exact IBP identities and finite-field arithmetic for the defined families."""
import itertools
import json
from functools import lru_cache
from pathlib import Path
import sympy as sp
from sympy.polys.fields import field

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
PRIMES = (2147483647, 1000000007, 1000000009)
POINTS = (
    dict(d=37, s=-13, t=-19, s1=-11, s2=-17, s3=-29, s4=-43, m2=7, m12=7, m22=23),
    dict(d=41, s=-31, t=-47, s1=-23, s2=-37, s3=-53, s4=-71, m2=11, m12=11, m22=29),
    dict(d=43, s=-59, t=-73, s1=-41, s2=-61, s3=-83, s4=-101, m2=17, m12=17, m22=47),
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def sector(a):
    return sum(1 << i for i, n in enumerate(a) if n > 0)


def complexity(a):
    t = sum(n > 0 for n in a)
    r = sum(n for n in a if n > 0)
    s = -sum(n for n in a if n < 0)
    return dict(sector=sector(a), t=t, r=r, s=s, dots=r-t)


def key(a):
    return ",".join(map(str, a))


def unkey(text):
    return tuple(map(int, text.split(",")))


class Family:
    def __init__(self, definition, masters):
        self.definition = definition
        self.name = definition["id"]
        self.loops = definition["loop_momenta"]
        self.external = definition["external_momenta"]
        self.L, self.E = len(self.loops), len(self.external)
        self.names = ["d"] + definition["invariants"]
        self.syms = sp.symbols(" ".join(self.names), seq=True)
        self.locals = dict(zip(self.names, self.syms))
        self.F = field(self.syms, sp.QQ)[0]
        self.zero, self.one = self.F.zero, self.F.one
        self.d = self.F.from_expr(self.locals["d"])
        self.masters = [tuple(m["indices"]) for m in masters["masters"]]
        self.master_set = set(self.masters)
        self.N = len(definition["propagators"])
        self.top = definition["top_level_sectors"][0]
        self.t_top = bin(self.top).count("1")
        self.momenta = sp.symbols(" ".join(self.loops + self.external), seq=True)
        momlocals = dict(zip(self.loops + self.external, self.momenta))
        self.q = []
        self.mass = []
        for prop in definition["propagators"]:
            expr = sp.sympify(prop["momentum"], locals=momlocals)
            self.q.append(sp.Matrix([expr.coeff(v) for v in self.momenta]))
            self.mass.append(sp.sympify(prop["mass_squared"], locals=self.locals))
        self.z = sp.symbols("z0:"+str(self.N))
        self.D = sp.symbols("D1:"+str(self.N+1))
        G = sp.zeros(self.L+self.E)
        position = 0
        for i in range(self.L):
            for j in range(i, self.L+self.E):
                G[i,j] = G[j,i] = self.z[position]
                position += 1
        for pair, value in definition["scalarproduct_rules"]:
            i, j = (self.L+self.external.index(p) for p in pair)
            G[i,j] = G[j,i] = sp.sympify(value, locals=self.locals)
        self.G = G
        self.denominators = [sp.expand((q.T*G*q)[0]-mass) for q,mass in zip(self.q,self.mass)]
        A, b = sp.linear_eq_to_matrix([expr-D for expr,D in zip(self.denominators,self.D)], self.z)
        inverse = A.inv()*b
        self.z_to_D = dict(zip(self.z, inverse))
        self.derivatives = {}
        for k in range(self.L):
            for v in range(self.L+self.E):
                terms = []
                for q in self.q:
                    derivative = sp.expand(2*q[k]*sum(q[j]*G[v,j] for j in range(self.L+self.E)))
                    affine = sp.expand(derivative.subs(self.z_to_D, simultaneous=True))
                    c0 = affine.subs(dict.fromkeys(self.D, 0))
                    cD = [affine.coeff(D) for D in self.D]
                    assert sp.expand(affine-c0-sum(c*D for c,D in zip(cD,self.D))) == 0
                    terms.append((self.F.from_expr(c0), [self.F.from_expr(c) for c in cD]))
                self.derivatives[k,v] = terms
        self.symmetries = self._symmetries()

    def parse(self, expression):
        return self.F.from_expr(sp.sympify(expression, locals=self.locals))

    @lru_cache(maxsize=100000)
    def text(self, coefficient):
        return str(coefficient.as_expr())

    def order(self, a):
        if a in self.master_set:
            return (0, self.masters.index(a))
        c = complexity(a)
        return (1, c["sector"], c["dots"], c["s"], c["r"], a)

    def row(self, seed, k, v):
        seed = tuple(seed)
        row = {}
        def add(a, value):
            if value:
                row[a] = row.get(a, self.zero)+value
                if not row[a]:
                    del row[a]
        if k == v:
            add(seed, self.d)
        for i, ai in enumerate(seed):
            if not ai:
                continue
            c0, cD = self.derivatives[k,v][i]
            shifted = list(seed)
            shifted[i] += 1
            add(tuple(shifted), -ai*c0)
            for j,c in enumerate(cD):
                a = shifted.copy()
                a[j] -= 1
                add(tuple(a), -ai*c)
        return row

    def operators(self):
        vectors = {tuple(int(i==j) for i in range(self.L+self.E))
                   for j in range(self.L+self.E)}
        for q in self.q:
            vector = tuple(int(c) for c in q)
            first = next(c for c in vector if c)
            vectors.add(tuple(-c for c in vector) if first < 0 else vector)
        return [(k,vector) for k in range(self.L) for vector in sorted(vectors)]

    def operator_row(self, seed, k, vector):
        result = {}
        for v,weight in enumerate(vector):
            if not weight:
                continue
            for a,c in self.row(seed,k,v).items():
                value = result.get(a,self.zero)+weight*c
                if value:
                    result[a] = value
                else:
                    result.pop(a,None)
        return result

    def _symmetries(self):
        found = {}
        size = self.L+self.E
        for indices in itertools.permutations(range(self.N), self.L):
            for signs in itertools.product((-1,1), repeat=self.L):
                T = sp.eye(size)
                for i,(j,sign) in enumerate(zip(indices,signs)):
                    T[i,:] = (sign*self.q[j]).T
                determinant = T[:self.L,:self.L].det()
                if determinant not in (-1,1):
                    continue
                permutation = []
                for i,q in enumerate(self.q):
                    transformed = T.T*q
                    matches = [j for j,p in enumerate(self.q)
                               if self.mass[i] == self.mass[j] and (transformed == p or transformed == -p)]
                    if len(matches) != 1:
                        break
                    permutation.append(matches[0])
                if len(permutation) != self.N or len(set(permutation)) != self.N:
                    continue
                perm = tuple(permutation)
                if perm == tuple(range(self.N)):
                    continue
                if any(bool(self.top & (1<<i)) != bool(self.top & (1<<j))
                       for i,j in enumerate(perm)):
                    continue
                found[perm] = dict(permutation=list(perm),
                    loop_transformation=[[int(x) for x in T[i,:]] for i in range(self.L)],
                    loop_jacobian_determinant=int(determinant))
        return list(found.values())

    def symmetry_row(self, a, symmetry):
        b = [0]*self.N
        for i,j in enumerate(symmetry["permutation"]):
            b[j] = a[i]
        b = tuple(b)
        return {} if b == tuple(a) else {tuple(a):self.one, b:-self.one}

    @lru_cache(maxsize=200000)
    def evaluate(self, coefficient, sample):
        point, prime = POINTS[sample], PRIMES[sample]
        values = [point[name] % prime for name in self.names]
        def polynomial(poly):
            total = 0
            for powers, c in poly.items():
                cq = sp.Rational(c)
                term = (int(cq.p)*pow(int(cq.q), -1, prime)) % prime
                for x,power in zip(values,powers):
                    term = term*pow(x,power,prime) % prime
                total = (total+term) % prime
            return total
        num, den = polynomial(coefficient.numer), polynomial(coefficient.denom)
        if not den:
            raise ZeroDivisionError("Exceptional finite-field sample")
        return num*pow(den,-1,prime) % prime

    def regular_nonzero(self, c):
        return bool(c) and all(self.evaluate(c,i) != 0 for i in range(len(PRIMES)))

    def serialize_row(self, row):
        return [{"indices":list(a), "coefficient":self.text(c)}
                for a,c in sorted(row.items(), key=lambda p:self.order(p[0])) if c]

    def parse_row(self, terms):
        return {tuple(t["indices"]):self.parse(t["coefficient"]) for t in terms}

    def numeric_row(self, row, sample):
        return {key(a):self.evaluate(c,sample) for a,c in row.items() if self.evaluate(c,sample)}

    def mass_degree(self, c):
        if not c:
            return None
        num = {sum(p[1:]) for p in c.numer.keys()}
        den = {sum(p[1:]) for p in c.denom.keys()}
        if len(num) != 1 or len(den) != 1:
            raise ValueError("Coefficient is not homogeneous in squared masses and invariants")
        return next(iter(num))-next(iter(den))

    def seed_pool(self):
        ranges = [range(-2,4) if self.top & (1<<i) else range(-2,1) for i in range(self.N)]
        result = []
        for a in itertools.product(*ranges):
            c = complexity(a)
            if c["t"] and c["r"] <= self.t_top+2 and c["s"] <= 2 and c["dots"] <= 2:
                result.append(a)
        return sorted(result, key=self.order)


def validate_identity_dimension(family, seed, row):
    for a,c in row.items():
        assert family.mass_degree(c) == sum(a)-sum(seed)


def physics_checks():
    families = read_json(PROJECT/"Master_Integrals/families.json")["families"]
    by_name = {f["id"]:f for f in families}
    def get(name):
        return Family(by_name[name], read_json(PROJECT/"Master_Integrals/families"/name/"masters.json"))
    tad = get("tadpole_massive")
    for a in range(1,5):
        expected = {(a,):tad.parse("d")-2*a, (a+1,):tad.parse("-2*m2")*a}
        assert tad.row((a,),0,0) == expected
    bubble = get("bubble_massless")
    expected = {(1,1):bubble.parse("d-3"), (0,2):bubble.parse("-1"), (1,2):bubble.parse("s")}
    assert bubble.row((1,1),0,0) == expected
    assert any(s["permutation"] == [1,0] for s in bubble.symmetries)
    equal = get("bubble_equal_mass")
    assert any(s["permutation"] == [1,0] for s in equal.symmetries)
    unequal = get("bubble_two_mass")
    assert not unequal.symmetries
    for p in PRIMES:
        assert sp.isprime(p)
    return dict(tadpole_recurrence=True, massless_bubble_identity=True,
                mass_preserving_symmetries=True, prime_fields=True)


if __name__ == "__main__":
    print(json.dumps(physics_checks(), sort_keys=True))
