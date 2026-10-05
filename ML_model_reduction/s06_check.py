"""Analytical and training-only checks; no held-out dataset is opened."""
import copy,json,math
import numpy as np
import torch
from s00_common import HERE,config,write_json
from s01_state import encode_state,normalize_state,eliminate,is_prime,feature_names
from s03_model import ReductionSelector

def toy():
    fam=dict(loop_momenta=["l1"],external_momenta=[],propagators=[dict(momentum="l1",mass_squared="m2")],
             invariants=["m2"],scalarproduct_rules=[])
    return dict(prime=101,family=fam,rows={"T":{"2":4,"1":1},"Q1":{"2":2,"1":6},"Q2":{"2":3,"3":5}},
                master_columns=["1"],row_roles={"T":"target","Q1":"identity","Q2":"identity"},
                actions=[dict(id="a",source_row="Q1",destination_row="T",pivot_indices=[2]),
                         dict(id="b",source_row="Q2",destination_row="T",pivot_indices=[2])])
def main():
    cfg=config();torch.set_num_threads(1);torch.manual_seed(cfg["seed"])
    s=toy();x=encode_state(s,cfg)
    assert x.shape==(2,len(feature_names(cfg)))
    after,factor=eliminate(s["rows"]["T"],s["rows"]["Q1"],"2",101)
    assert after=={"1":90} and factor==2
    m=ReductionSelector(x.shape[1],cfg);t=torch.from_numpy(x)[None,:,:];mask=torch.ones((1,2),dtype=torch.bool)
    z=m(t,mask);p=torch.softmax(z,dim=-1);assert abs(float(p.sum())-1)<1e-6
    reversed_state=copy.deepcopy(s);reversed_state["actions"].reverse()
    xr=encode_state(reversed_state,cfg)
    assert np.array_equal(xr,x[::-1])
    assert torch.allclose(m(torch.from_numpy(xr)[None,:,:],mask).flip(1),z,atol=2e-7)
    reordered=copy.deepcopy(s);reordered["rows"]=dict(reversed(list(s["rows"].items())))
    assert np.array_equal(encode_state(reordered,cfg),x)
    renamed=copy.deepcopy(s);renamed["actions"][0]["id"]="arbitrary";renamed["family"]["id"]="no_feature"
    assert np.array_equal(encode_state(renamed,cfg),x)
    scaled=copy.deepcopy(s)
    for i,row in enumerate(scaled["rows"].values()):
        for k in row:row[k]=row[k]*(i+7)%101
    assert np.array_equal(encode_state(scaled,cfg),x)
    leakage=copy.deepcopy(s);leakage["reference_choice"]="b";leakage["future_operations"]=100
    leakage["final_master_row"]={"1":0}
    assert np.array_equal(encode_state(leakage,cfg),x)
    # A supplied matrix may have several destination rows.
    multi=copy.deepcopy(s)
    multi["rows"]["T2"]={"2":9,"3":8}
    multi["row_roles"]["T2"]="target"
    multi["actions"].append(dict(id="c",source_row="Q1",destination_row="T2",pivot_indices=[2]))
    xm=encode_state(multi,cfg)
    assert xm.shape==(3,x.shape[1]) and np.isfinite(xm).all()
    out,factor=eliminate(multi["rows"]["T2"],multi["rows"]["Q1"],"2",101)
    for k in set(out)|set(multi["rows"]["T2"])|set(multi["rows"]["Q1"]):
        assert out.get(k,0)*2%101==(multi["rows"]["T2"].get(k,0)*2-9*multi["rows"]["Q1"].get(k,0))%101
    assert multi["rows"]["T"]==s["rows"]["T"]
    # Masked padding has no effect on valid scores or probabilities.
    padded=torch.cat((t,torch.ones((1,2,t.shape[-1]))*999),dim=1)
    pmask=torch.tensor([[True,True,False,False]])
    assert torch.allclose(m(padded,pmask)[:,:2],z,atol=2e-7)
    single=m(t[:,:1],mask[:,:1]);assert float(torch.softmax(single,-1)[0,0])==1
    rejected=[]
    for name,mutate in [
        ("zero_pivot",lambda a:a["rows"]["Q1"].update({"2":0})),
        ("protected_master",lambda a:a.update(master_columns=["1","2"])),
        ("target_source",lambda a:a["row_roles"].update(Q1="target")),
        ("duplicate_action",lambda a:a["actions"].append(dict(a["actions"][0]))),
        ("composite_modulus",lambda a:a.update(prime=100))]:
        bad=copy.deepcopy(s);mutate(bad)
        try:encode_state(bad,cfg)
        except ValueError:rejected.append(name)
        else:raise AssertionError("Failed to reject "+name)
    assert all(is_prime(v) for v in (101,2147483647,1000000007,1000000009))
    # Verify exact cancellation using an independent cross-multiplication identity.
    rng=np.random.default_rng(20261005)
    for _ in range(200):
        source={str(i):int(rng.integers(1,101)) for i in range(1,5)}
        dest={str(i):int(rng.integers(1,101)) for i in range(2,7)}
        out,_=eliminate(dest,source,"2",101)
        for k in set(source)|set(dest)|set(out):
            assert out.get(k,0)*source["2"]%101==(dest.get(k,0)*source["2"]-dest["2"]*source.get(k,0))%101
    optimizer=torch.optim.AdamW(m.parameters(),lr=0.01);label=torch.tensor([0])
    initial=float(torch.nn.functional.cross_entropy(m(t,mask),label))
    for _ in range(30):
        optimizer.zero_grad(set_to_none=True);loss=torch.nn.functional.cross_entropy(m(t,mask),label)
        loss.backward()
        assert all(v.grad is None or torch.isfinite(v.grad).all() for v in m.parameters())
        optimizer.step()
    final=float(torch.nn.functional.cross_entropy(m(t,mask),label))
    assert final<initial*0.1
    write_json(HERE/"implementation_checks.json",dict(status="passed",feature_dim=x.shape[1],
        parameter_count=sum(v.numel() for v in m.parameters()),exact_random_row_checks=200,
        multiple_destination_rows=True,candidate_permutation=True,row_permutation=True,row_scaling_invariance=True,
        identifiers_and_future_labels_excluded=True,padding_invariance=True,forced_probability=1,
        rejected_invalid_inputs=rejected,finite_gradients=True,toy_initial_loss=initial,toy_final_loss=final,
        held_out_data_used=False))
    print("Implementation checks passed",x.shape[1],sum(v.numel() for v in m.parameters()),flush=True)
if __name__=="__main__":main()
