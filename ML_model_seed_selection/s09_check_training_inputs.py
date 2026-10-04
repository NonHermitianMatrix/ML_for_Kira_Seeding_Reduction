"""Check training input reuse and resume ordering without evaluating the test split."""
import itertools,json
import torch
from s01_data import HERE,config,read,examples,find_input,encode,encode_shared
from s02_model import SeedSelector
torch.set_num_threads(1)
cfg=config()
manifest=read(HERE/"split_manifest.json")
train=[m for m in manifest["families"] if m["split"]=="train"]
test=[m for m in manifest["families"] if m["split"]=="test"]
assert len(train)==693 and len(test)==307
assert {m["family"] for m in train}.isdisjoint({m["family"] for m in test})
assert {m["group"] for m in train}.isdisjoint({m["group"] for m in test})
for m in train:
    assert all(m[k].startswith("training/") for k in ("definition","masters","inputs","references","seeds"))
for m in test:
    assert all(m[k].startswith("testing/") for k in ("definition","masters","inputs","references","seeds"))
first=list(itertools.islice(examples("train",cfg,epoch=0),12))
resume=list(itertools.islice(examples("train",cfg,epoch=0,start=8),4))
assert [a[0]["id"] for a in first[8:]]==[a[0]["id"] for a in resume]
model=SeedSelector(cfg).eval()
for target,x,y in first[:2]:
    t,f,seeds=find_input(target["id"])
    fresh=encode(t,f,seeds,cfg)
    shared=encode(t,f,seeds,cfg,shared=encode_shared(f,seeds,cfg))
    for k in x:
        assert torch.equal(fresh[k],x[k]) and torch.equal(fresh[k],shared[k])
    with torch.no_grad():
        torch.testing.assert_close(model(fresh),model(shared),rtol=0,atol=0)
result=dict(status="training_input_checks_passed",training_examples_checked=12,
            test_examples_read=0,model_testing_performed=False,optimizer_updates_in_check=0,
            input_reuse_preserves_values=True,resume_order_preserved=True)
out=HERE/"runs";out.mkdir(exist_ok=True)
(out/"input_checks.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(result),flush=True)
