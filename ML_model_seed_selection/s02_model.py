"""Small shared neural scorer; every output is a reference-set membership probability."""
import math
import torch
from torch import nn
import torch.nn.functional as F

class SeedSelector(nn.Module):
    def __init__(self,cfg):
        super().__init__()
        self.cfg = cfg
        h = cfg["hidden"]
        index_dim = 3*cfg["max_indices"]+5
        def embed(n):
            return nn.Sequential(nn.Linear(n,h),nn.Tanh())
        self.term = embed(index_dim+cfg["hash_bins"]+2)
        self.pair = embed(4*h)
        self.family = embed(cfg["hash_bins"]+4)
        self.master = embed(index_dim)
        self.seed = embed(index_dim)
        self.score = nn.Sequential(nn.Linear(7*h,2*h),nn.Tanh(),nn.Linear(2*h,1))

    def context(self,x):
        terms = self.term(x["terms"])
        n,h = terms.shape
        pair_sum = terms.new_zeros(h)
        count = 0
        # Enumerate every ordered pair (i,j), i != j, with bounded temporary blocks.
        for start in range(0,n*n,self.cfg["pair_chunk"]):
            pos = torch.arange(start,min(n*n,start+self.cfg["pair_chunk"]),device=terms.device)
            left = torch.div(pos,n,rounding_mode="floor")
            right = pos % n
            valid = left != right
            a,b = terms[left[valid]],terms[right[valid]]
            if a.shape[0]:
                pair_sum = pair_sum + self.pair(torch.cat((a,b,a-b,a*b),dim=-1)).sum(dim=0)
                count += a.shape[0]
        pair_mean = pair_sum/max(1,count)
        masters = self.master(x["masters"]).mean(dim=0)
        global_context = torch.cat((terms.mean(dim=0),terms.max(dim=0).values,pair_mean,
                                    self.family(x["family"]),masters),dim=-1)
        return terms,global_context

    def forward(self,x):
        terms,context = self.context(x)
        scores = []
        h = self.cfg["hidden"]
        for block in x["seeds"].split(self.cfg["candidate_chunk"],dim=0):
            seeds = self.seed(block)
            weights = torch.softmax(seeds @ terms.T/math.sqrt(h),dim=-1)
            attended = weights @ terms
            inp = torch.cat((context.expand(len(seeds),-1),seeds,attended),dim=-1)
            scores.append(self.score(inp).squeeze(-1))
        return torch.cat(scores)

    def probabilities(self,x):
        return torch.sigmoid(self(x))

def reference_loss(logits,y):
    if logits.shape!=y.shape: raise ValueError("Prediction/label shape mismatch")
    # Unweighted BCE preserves the interpretation as reference-membership probability.
    # Both stored positives and absent memberships enter; the latter do not mean invalid seeds.
    return F.binary_cross_entropy_with_logits(logits,y,reduction="mean")
