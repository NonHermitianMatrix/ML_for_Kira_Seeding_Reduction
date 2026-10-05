"""Shared 32-component candidate encoder with pooled candidate context."""
import torch
from torch import nn
class ReductionSelector(nn.Module):
    def __init__(self,feature_dim,cfg):
        super().__init__()
        h=cfg["hidden"]
        self.encoder=nn.Sequential(nn.Linear(feature_dim,h),nn.Tanh())
        self.scorer=nn.Sequential(nn.Linear(3*h,cfg["score_hidden"]),nn.Tanh(),
                                  nn.Linear(cfg["score_hidden"],1))
    def forward(self,features,mask):
        # features [batch, candidates, features]; mask marks supplied actions.
        if features.ndim!=3 or mask.shape!=features.shape[:2]:raise ValueError("Bad batch shape")
        if not mask.any(dim=1).all():raise ValueError("Each state must contain an action")
        h=self.encoder(features)
        avg=(h*mask.unsqueeze(-1)).sum(1)/mask.sum(1,keepdim=True)
        maximum=h.masked_fill(~mask.unsqueeze(-1),-torch.inf).max(1).values
        joined=torch.cat((h,avg[:,None,:].expand_as(h),maximum[:,None,:].expand_as(h)),dim=-1)
        return self.scorer(joined).squeeze(-1).masked_fill(~mask,-torch.inf)
