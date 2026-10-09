"""NumPy inference using the original seed model, public inputs and float32 weights."""
import functools,hashlib,json,math,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent
@functools.lru_cache(maxsize=8192)
def text_features(text,bins):
 tokens=re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+|\*\*|[^\s]",text)
 result=[0.0]*bins;count=0
 for width in (1,2,3):
  for start in range(len(tokens)-width+1):
   digest=hashlib.blake2b("\x1f".join(tokens[start:start+width]).encode(),digest_size=8).digest()
   result[int.from_bytes(digest[:4],"little")%bins]+=1.0 if digest[4]&1 else -1.0;count+=1
 return tuple(x/math.sqrt(max(1,count)) for x in result)
def index_features(a,cfg):
 n=len(a);assert 0<n<=cfg["max_indices"]
 padded=list(a)+[0]*(cfg["max_indices"]-n)
 r=sum(max(0,x) for x in a);s=sum(max(0,-x) for x in a);t=sum(x>0 for x in a)
 return ([math.copysign(math.log1p(abs(x)),x) if x else 0.0 for x in padded]+
  [float(x>0) for x in padded]+[float(i<n) for i in range(len(padded))]+[math.log1p(x) for x in (r,s,t,r-t,n)])
class FastSeed:
 def __init__(self):
  global np
  import numpy as np
  self.cfg=json.loads((HERE/"seed_export.json").read_text())["config"]
  with np.load(HERE/"seed_weights.npz",allow_pickle=False) as f:self.w={k:f[k] for k in f.files}
 def linear(self,x,name):return x@self.w[name+".weight"].T+self.w[name+".bias"]
 def embed(self,x,name):return np.tanh(self.linear(x,name+".0"))
 def shared(self,definition,masters,seeds):
  c=self.cfg
  family={k:definition[k] for k in ("loop_momenta","external_momenta","propagators","invariants","scalarproduct_rules")}
  fv=list(text_features(json.dumps(family,sort_keys=True,separators=(",",":")),c["hash_bins"]))
  fv += [math.log1p(x) for x in (len(family["loop_momenta"]),len(family["propagators"]),len(family["external_momenta"]),len(family["invariants"]))]
  master=self.embed(np.array([index_features(a,c) for a in masters],np.float32),"master").mean(0)
  seed=self.embed(np.array([index_features(a,c) for a in seeds],np.float32),"seed")
  return self.embed(np.array(fv,np.float32),"family"),master,seed
 def predict(self,target,shared):
  c=self.cfg;terms=target["terms"];n=len(terms);assert 0<n<=c["max_terms"]
  rows=[index_features(t["indices"],c)+list(text_features(t["coefficient"],c["hash_bins"]))+[j/max(1,n-1),1/n] for j,t in enumerate(terms)]
  emb=self.embed(np.array(rows,np.float32),"term");total=np.zeros(c["hidden"],np.float32);count=0
  for start in range(0,n*n,c["pair_chunk"]):
   pos=np.arange(start,min(n*n,start+c["pair_chunk"]));left=pos//n;right=pos%n;valid=left!=right
   a,b=emb[left[valid]],emb[right[valid]]
   if len(a):total+=self.embed(np.concatenate((a,b,a-b,a*b),axis=-1),"pair").sum(0);count+=len(a)
  family,masters,seeds=shared
  context=np.concatenate((emb.mean(0),emb.max(0),total/max(1,count),family,masters)).astype(np.float32)
  scores=[]
  for start in range(0,len(seeds),c["candidate_chunk"]):
   s=seeds[start:start+c["candidate_chunk"]]
   att=s@emb.T/np.float32(math.sqrt(c["hidden"]));att=np.exp(att-att.max(1,keepdims=True));att/=att.sum(1,keepdims=True)
   inp=np.concatenate((np.broadcast_to(context,(len(s),len(context))),s,att@emb),axis=-1)
   scores.append(self.linear(np.tanh(self.linear(inp,"score.0")),"score.2").ravel())
  logits=np.concatenate(scores)
  return 1/(1+np.exp(-np.clip(logits,-80,80)))
