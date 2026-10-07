"""Streaming inputs with a strict boundary between problem features and reference labels."""
import collections, functools, gzip, hashlib, itertools, json, math, pathlib, random, re
import torch
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "integrals"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def config():
    return read(HERE/"config.json")

def rows(path):
    with gzip.open(str(path), "rt", encoding="utf-8") as f:
        for line in f: yield json.loads(line)

@functools.lru_cache(maxsize=8192)
def text_features(text, bins):
    # Signed token 1-, 2-, 3-gram counts; no learned vocabulary or test-data fit.
    tokens = re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+|\*\*|[^\s]", text)
    result = [0.0]*bins
    count = 0
    for width in (1,2,3):
        for start in range(len(tokens)-width+1):
            key = "\x1f".join(tokens[start:start+width]).encode("utf-8")
            digest = hashlib.blake2b(key,digest_size=8).digest()
            result[int.from_bytes(digest[:4],"little")%bins] += 1.0 if digest[4]&1 else -1.0
            count += 1
    scale = math.sqrt(max(1,count))
    return tuple(x/scale for x in result)

def index_features(indices, cfg):
    n = len(indices)
    if not n or n > cfg["max_indices"]:
        raise ValueError("Integral index length exceeds the configured capacity")
    a = list(indices) + [0]*(cfg["max_indices"]-n)
    r = sum(max(0,x) for x in indices)
    s = sum(max(0,-x) for x in indices)
    t = sum(x>0 for x in indices)
    dots = r-t
    return ([math.copysign(math.log1p(abs(x)),x) if x else 0.0 for x in a] +
            [float(x>0) for x in a] + [float(i<n) for i in range(len(a))] +
            [math.log1p(x) for x in (r,s,t,dots,n)])

def public_family(definition, master_basis):
    # Explicit allowlist: source IDs, stored splits, histories, samples and answers cannot enter.
    return dict(loop_momenta=definition["loop_momenta"],
                external_momenta=definition["external_momenta"],
                propagators=definition["propagators"],invariants=definition["invariants"],
                scalarproduct_rules=definition["scalarproduct_rules"],
                master_indices=[m["indices"] for m in master_basis["masters"]])

def encode_shared(family,seeds,cfg):
    """Encode immutable family, master and candidate inputs once per family pass."""
    n=len(family["propagators"])
    if not seeds or len(seeds)>cfg["max_candidates"]:
        raise ValueError("Candidate count exceeds the configured capacity")
    if len({tuple(s) for s in seeds})!=len(seeds):
        raise ValueError("Duplicate candidate seed")
    if any(len(s)!=n for s in seeds):
        raise ValueError("Candidate index length does not match the family")
    structure={k:v for k,v in family.items() if k!="master_indices"}
    family_vec=list(text_features(json.dumps(structure,sort_keys=True,separators=(",",":")),cfg["hash_bins"]))
    family_vec += [math.log1p(v) for v in (len(family["loop_momenta"]),n,
                   len(family["external_momenta"]),len(family["invariants"]))]
    return dict(family=torch.tensor(family_vec,dtype=torch.float32),
                masters=torch.tensor([index_features(a,cfg) for a in family["master_indices"]],dtype=torch.float32),
                seeds=torch.tensor([index_features(s,cfg) for s in seeds],dtype=torch.float32))

def encode(target,family,seeds,cfg,shared=None):
    terms=target["terms"]
    n=len(family["propagators"])
    if not terms or len(terms)>cfg["max_terms"]:
        raise ValueError("Target term count exceeds the configured capacity")
    if shared is None: shared=encode_shared(family,seeds,cfg)
    feature_rows=[]
    for j,term in enumerate(terms):
        if len(term["indices"])!=n: raise ValueError("Term index length does not match family")
        c=term["coefficient"]
        if len(c)>cfg["max_coefficient_chars"]:
            raise ValueError("Coefficient text exceeds the configured capacity")
        feature_rows.append(index_features(term["indices"],cfg)+list(text_features(c,cfg["hash_bins"]))+
                            [j/max(1,len(terms)-1),1/len(terms)])
    return dict(shared,terms=torch.tensor(feature_rows,dtype=torch.float32))

def labels(reference, seeds):
    wanted = {tuple(s) for s in reference["sufficient_seeds"]}
    if not wanted <= {tuple(s) for s in seeds}:
        raise ValueError("Reference seed absent from candidate pool")
    return torch.tensor([float(tuple(s) in wanted) for s in seeds],dtype=torch.float32)

def family_records(meta, cfg, shuffle_seed=None):
    definition = read(DATA/meta["definition"])
    master_basis = read(DATA/meta["masters"])
    family = public_family(definition,master_basis)
    seeds = read(DATA/meta["seeds"])["indices"]
    iterator = itertools.zip_longest(rows(DATA/meta["inputs"]),rows(DATA/meta["references"]))
    if shuffle_seed is not None:
        # Bounded shuffle buffer; never materialize a complete global dataset.
        rng = random.Random(shuffle_seed)
        def shuffled(source):
            buf = []
            for item in source:
                buf.append(item)
                if len(buf)>=32: yield buf.pop(rng.randrange(len(buf)))
            while buf: yield buf.pop(rng.randrange(len(buf)))
        iterator = shuffled(iterator)
    for target,reference in iterator:
        if target is None or reference is None or target["id"]!=reference["id"]:
            raise ValueError("Target/reference records do not align")
        yield target, family, seeds, labels(reference,seeds)

def examples(split, cfg, epoch=None, start=0):
    manifest = read(HERE/"split_manifest.json")
    selected = [f for f in manifest["families"] if f["split"]==split]
    if split not in ("train","test"): raise ValueError("Unknown split")
    if epoch is not None:
        if split!="train": raise ValueError("Only training order may be shuffled")
        random.Random(cfg["split_seed"]+epoch).shuffle(selected)
    passed=0
    for i,meta in enumerate(selected):
        seed = None if epoch is None else cfg["split_seed"]+epoch*1009+i
        shared=None
        for target,family,seeds,y in family_records(meta,cfg,seed):
            if passed<start:
                passed+=1
                continue
            if shared is None: shared=encode_shared(family,seeds,cfg)
            yield target,encode(target,family,seeds,cfg,shared=shared),y

def find_input(identifier):
    family_id = identifier.split(":")[0]
    metas = read(HERE/"split_manifest.json")["families"]
    meta = next((m for m in metas if m["family"]==family_id),None)
    if meta is None: raise KeyError(identifier)
    # Inference opens inputs and public definitions only, never reference labels.
    for target in rows(DATA/meta["inputs"]):
        if target["id"]==identifier:
            family = public_family(read(DATA/meta["definition"]),read(DATA/meta["masters"]))
            seeds = read(DATA/meta["seeds"])["indices"]
            return target,family,seeds
    raise KeyError(identifier)

def verify_sources(split=None):
    expected = read(HERE/"source_hashes.json")
    if split is not None:
        if split not in ("train","test"):raise ValueError("Unknown split")
        selected=[m for m in read(HERE/"split_manifest.json")["families"] if m["split"]==split]
        paths={m[k] for m in selected for k in ("definition","masters","inputs","references","seeds")}
        expected={path:digest for path,digest in expected.items() if path in paths}
        if len(expected)!=len(paths):raise ValueError("Missing source hashes for split")
    for path,digest in expected.items():
        h = hashlib.sha256()
        with (DATA/path).open("rb") as f:
            for b in iter(lambda:f.read(1048576),b""): h.update(b)
        if h.hexdigest()!=digest:
            raise ValueError("Source data changed; prepare the split again: "+path)
    return hashlib.sha256((HERE/"split_manifest.json").read_bytes()).hexdigest()

def storage_guard():
    total = 0
    for p in ROOT.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink(): total += p.stat().st_size
        except FileNotFoundError: pass
    # Reserve 100 MB for the original local workspace and leave 1 GB cap headroom.
    if total+100000000 > 9000000000:
        raise RuntimeError("Project storage headroom is below the required margin")
    return total
