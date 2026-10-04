"""Compare full training-input and gradient work with one and two CPU threads."""
import itertools,json,os,pathlib,statistics,sys,time,resource
sys.path.insert(0,str(pathlib.Path("ML_model_seed_selection").resolve()))
import torch
from s01_data import config,examples,HERE
from s02_model import SeedSelector,reference_loss
torch.set_num_interop_threads(1);torch.set_num_threads(1)
cfg=config();saved=torch.load(str(HERE/"runs/latest.pt"),map_location="cpu")
model=SeedSelector(cfg);model.load_state_dict(saved["model"]);model.train()
results=[]
for threads in (1,2,1,2):
    torch.set_num_threads(threads)
    start=time.monotonic(); families=set()
    for target,x,y in itertools.islice(examples("train",cfg,epoch=2),1024):
        families.add(target["id"].split(":")[0])
        model.zero_grad(set_to_none=True);reference_loss(model(x),y).backward()
    row=dict(threads=threads,seconds=time.monotonic()-start,targets=1024,families=len(families))
    results.append(row);print(json.dumps(row),flush=True)
result=dict(results=results,host=os.uname().nodename,optimizer_updates=0,test_examples_read=0,
    max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
result["two_thread_speed_ratio"]=statistics.mean(r["seconds"] for r in results if r["threads"]==1)/statistics.mean(r["seconds"] for r in results if r["threads"]==2)
(HERE/"runs/resource_check/end_to_end_scaling.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result),flush=True)
