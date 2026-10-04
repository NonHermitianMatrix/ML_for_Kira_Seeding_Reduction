"""Measure CPU scaling using training records; never change production weights."""
import itertools,json,os,pathlib,resource,statistics,sys,time
sys.path.insert(0,str(pathlib.Path("ML_model_seed_selection").resolve()))
import torch
from s01_data import config,examples,storage_guard,HERE
from s02_model import SeedSelector,reference_loss
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
cfg=config()
start=time.monotonic()
records=list(itertools.islice(examples("train",cfg,epoch=2),128))
load_seconds=time.monotonic()-start
snapshot=torch.load(str(HERE/"runs/latest.pt"),map_location="cpu")
model=SeedSelector(cfg);model.load_state_dict(snapshot["model"]);model.train()
result=dict(training_examples=len(records),test_examples_read=0,optimizer_updates=0,
            checkpoint_targets=snapshot["trained_targets"],load_seconds=load_seconds,
            host=os.uname().nodename,cpu_threads=[],timing_repeats=3)
reference_gradients=None
for threads in (1,2,4,1):
    torch.set_num_threads(threads)
    for _,x,y in records[:8]:
        model.zero_grad(set_to_none=True);reference_loss(model(x),y).backward()
    timings=[]
    for _ in range(3):
        began=time.monotonic()
        for _,x,y in records:
            model.zero_grad(set_to_none=True);reference_loss(model(x),y).backward()
        timings.append(time.monotonic()-began)
    grads=torch.cat([p.grad.reshape(-1) for p in model.parameters() if p.grad is not None])
    if reference_gradients is None:reference_gradients=grads.clone()
    difference=float((grads-reference_gradients).abs().max())
    row=dict(threads=threads,seconds=timings,median_seconds=statistics.median(timings),
             max_gradient_difference=difference)
    result["cpu_threads"].append(row);print(json.dumps(row),flush=True)
start=time.monotonic()
result["project_bytes"]=storage_guard()
result["storage_check_seconds"]=time.monotonic()-start
result["max_rss_kib"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
out=HERE/"runs/resource_check"
out.mkdir(exist_ok=True)
(out/"cpu_scaling.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result),flush=True)
