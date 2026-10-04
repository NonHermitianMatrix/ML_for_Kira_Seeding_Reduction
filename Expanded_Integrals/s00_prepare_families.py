#!/usr/bin/env python3
"""Enumerate inequivalent one-loop four-propagator families."""
import argparse, hashlib, itertools, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EDGES=list(itertools.combinations(range(4),2))
PERMS=list(itertools.permutations(range(4)))
EDGE_MAPS=[[EDGES.index(tuple(sorted((p[i],p[j])))) for i,j in EDGES] for p in PERMS]
POINTS=[
 dict(d=37,m1=7,m2=13,m3=23,m4=31,u1=-11,u2=-19,u3=-29,u4=-43,u5=-59,u6=-71),
 dict(d=41,m1=11,m2=17,m3=29,m4=43,u1=-31,u2=-47,u3=-61,u4=-79,u5=-97,u6=-113),
 dict(d=43,m1=17,m2=23,m3=37,m4=53,u1=-41,u2=-67,u3=-83,u4=-101,u5=-127,u6=-149)]
PRIMES=[2147483647,1000000007,1000000009]

def normalized(seq):
    labels={0:0}; result=[]
    for x in seq:
        if x not in labels: labels[x]=len(labels)
        result.append(labels[x])
    return tuple(result)

def patterns(n,prefix=(),largest=0):
    if len(prefix)==n:
        yield prefix
    else:
        for k in range(largest+2):
            yield from patterns(n,prefix+(k,),max(largest,k))

def canonical(masses,distances):
    return min((normalized(tuple(masses[i] for i in p)),
                normalized(tuple(distances[i] for i in edges)))
               for p,edges in zip(PERMS,EDGE_MAPS))

def det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
          -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
          +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))

def valid_gram(edges):
    for point,prime in zip(POINTS,PRIMES):
        dist={(i,j):point['u'+str(k)] if k else 0 for (i,j),k in zip(EDGES,edges)}
        def x(i,j): return 0 if i==j else dist[tuple(sorted((i,j)))]
        twice=[[x(0,i)+x(0,j)-x(i,j) for j in range(1,4)] for i in range(1,4)]
        if not det3(twice)%prime: return False
    return True

def definition(index,signature):
    masses,edges=signature
    invariant=lambda k: 'u'+str(k) if k else '0'
    mass=lambda k: 'm'+str(k) if k else '0'
    dist={pair:invariant(k) for pair,k in zip(EDGES,edges)}
    def x(i,j): return '0' if i==j else dist[tuple(sorted((i,j)))]
    rules=[]
    for i in range(1,4):
        for j in range(i,4):
            value=x(0,i) if i==j else '('+x(0,i)+'+'+x(0,j)+'-'+x(i,j)+')/2'
            rules.append([['p'+str(i),'p'+str(j)],value])
    digest=hashlib.sha256(json.dumps(signature,separators=(',',':')).encode()).hexdigest()
    # The distance equality pattern stays in one split across all mass assignments.
    distance_group=canonical((0,0,0,0),edges)[1]
    bucket=int(hashlib.sha256(json.dumps(distance_group).encode()).hexdigest()[:8],16)%10
    split='test' if bucket==0 else 'validation' if bucket==1 else 'train'
    legacy_train={canonical((0,0,0,0),e)[1] for e in [(0,1,0,0,2,0),(0,1,2,0,3,0)]}
    if distance_group in legacy_train: split='train'
    return dict(id='box_profile_%04d'%index,title='One-loop box mass and kinematic profile %04d'%index,
        loop_momenta=['l1'],external_momenta=['p1','p2','p3'],
        top_level_sectors=[15],
        propagators=[dict(momentum='l1' if i==0 else 'l1-p'+str(i),mass_squared=mass(k)) for i,k in enumerate(masses)],
        invariants=['u'+str(k) for k in range(1,max(edges)+1)]+['m'+str(k) for k in range(1,max(masses)+1)],
        scalarproduct_rules=rules,
        assumptions=['Generic independent nonzero squared scales; distinct positive labels specify independent variables.',
          'Zero and equality conditions are exact; m labels and u labels are independent.',
          'External Gram matrix is nonsingular at all three recorded samples.',
          'These are four-propagator one-loop families with different parameter constraints, not distinct graph topologies.'],
        profile=dict(mass_labels=masses,distance_labels=edges,distance_order=EDGES,
          canonical_sha256=digest,kinematic_group=list(distance_group),split=split),
        samples=[dict(prime=p,point={k:v for k,v in pt.items() if k=='d' or k in
          ['u'+str(x) for x in edges if x]+['m'+str(x) for x in masses if x]})
          for p,pt in zip(PRIMES,POINTS)])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--count',type=int,default=984)
    args=parser.parse_args()
    exclude={canonical((0,0,0,0),e) for e in [(0,1,0,0,2,0),(0,1,2,0,3,0),(1,2,3,4,5,6)]}
    found=set()
    for masses in patterns(4):
        for edges in patterns(6):
            # Keep up to three independent mass scales and three momentum scales.
            if not max(edges) or max(edges)>3 or max(masses)>3: continue
            signature=canonical(masses,edges)
            if signature in found or signature in exclude: continue
            if valid_gram(signature[1]): found.add(signature)
    # Spread kinematic groups and mass counts instead of taking a single block.
    ranked=sorted(found,key=lambda s:hashlib.sha256(json.dumps(s).encode()).hexdigest())
    if len(ranked)<args.count: raise RuntimeError('Only %d inequivalent profiles'%len(ranked))
    selected=ranked[:args.count]
    families=[definition(i,s) for i,s in enumerate(selected,1)]
    ROOT.mkdir(exist_ok=True)
    data=dict(schema_version=2,new_family_count=len(families),original_family_count=16,
      total_family_count=len(families)+16,eligible_inequivalent_profiles=len(found),
      equivalence='All 24 permutations of the four propagators, with independent relabelling of nonzero mass and distance variables.',
      selection='Deterministic hash ordering; exact parameter constraints, not numerical resampling.',
      split_policy='Complete kinematic equality/zero profiles grouped across all mass assignments.',
      families=families)
    (ROOT/'families.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k!='families'},sort_keys=True),flush=True)
if __name__=='__main__': main()
