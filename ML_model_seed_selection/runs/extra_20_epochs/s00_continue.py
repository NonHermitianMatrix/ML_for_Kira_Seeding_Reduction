"""Continue the published seed checkpoint for the requested twenty epochs."""
import fcntl,hashlib,json,math,os,pathlib,sys,time
WORK=pathlib.Path(__file__).resolve().parent
MODEL=WORK.parents[1]
sys.path.insert(0,str(MODEL))
import torch
from s01_data import read,config,verify_sources
from s03_train import train,atomic_json

def sha(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def write_status(stage,**more):
    atomic_json(WORK/"status.json",dict(stage=stage,utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),**more))
def main():
    lock=(WORK/"run.lock").open("w")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    torch.set_num_threads(1)
    plan=read(WORK/"request.json")
    goal=plan["target_epochs"]
    assert goal==plan["initial_epochs"]+plan["additional_epochs"]==30
    assert config()==plan["base_config"]
    assert sha(MODEL/"split_manifest.json")==plan["split_sha256"]
    snapshot=MODEL/"runs/epochs_10_snapshot"
    for relative,digest in plan["snapshots"].items():assert sha(snapshot/relative)==digest
    latest=MODEL/"runs/latest.pt"
    saved=torch.load(latest,map_location="cpu",weights_only=False)
    assert plan["initial_epochs"]<=saved["epoch"]<=goal
    files={p.name:sha(p) for p in MODEL.glob("*.py")}
    assert files==saved["source_files"],"Training implementation changed"
    assert all(saved["config"][k]==v for k,v in config().items() if k!="epochs")
    if saved["epoch"]==plan["initial_epochs"] and saved["processed_in_epoch"]==0:
        assert sha(latest)==plan["initial_checkpoint_sha256"]
        published=torch.load(snapshot/"trained_model.pt",map_location="cpu",weights_only=False)
        assert all(torch.equal(t,published["model"][k]) for k,t in saved["model"].items())
        assert saved["optimizer_steps"]==plan["base_metadata"]["optimizer_steps"]
    assert saved["optimizer"]["state"],"Optimizer state missing"
    assert saved["test_targets_processed"]==0
    if not (WORK/"preflight.json").exists():
        atomic_json(WORK/"preflight.json",dict(status="passed",resumed_epoch=saved["epoch"],
            resumed_targets_in_epoch=saved["processed_in_epoch"],optimizer_steps=saved["optimizer_steps"],
            initial_model_sha256=plan["initial_model_sha256"],initial_checkpoint_sha256=plan["initial_checkpoint_sha256"],
            source_files_unchanged=True,optimizer_state_preserved=True,training_split_unchanged=True,
            target_epochs=goal,runner_sha256=sha(__file__),github_publication=False))
    write_status("training",initial_epochs=plan["initial_epochs"],target_epochs=goal,
                 resumed_completed_epochs=saved["epoch"],progress_file="../training_status.json")
    if saved["epoch"]<goal:
        del saved
        train(epochs=goal,resume=True)
    saved=torch.load(latest,map_location="cpu",weights_only=False)
    if saved["epoch"]==goal and saved["processed_in_epoch"]==0:
        compact=dict(saved);compact.pop("optimizer")
        temp=MODEL/"trained_model.pt.part"
        torch.save(compact,temp)
        assert temp.stat().st_size<=config()["checkpoint_limit_bytes"]
        os.replace(str(temp),str(MODEL/"trained_model.pt"))
    final=torch.load(MODEL/"trained_model.pt",map_location="cpu",weights_only=False)
    steps=math.ceil(168330/config()["accumulate_targets"])*goal
    assert saved["epoch"]==final["epoch"]==final["config"]["epochs"]==goal
    assert saved["processed_in_epoch"]==0 and saved["trained_targets"]==168330*goal
    assert saved["optimizer_steps"]==steps and len(saved["history"])==goal
    assert all(r["targets"]==168330 for r in saved["history"])
    assert saved["history"][:plan["initial_epochs"]]==torch.load(snapshot/"runs/latest.pt",map_location="cpu",weights_only=False)["history"]
    assert all(torch.isfinite(t).all() and torch.equal(t,final["model"][k]) for k,t in saved["model"].items())
    assert saved["test_targets_processed"]==0
    result=dict(plan["base_metadata"])
    result.update(status="trained_testing_deferred",epochs=goal,optimizer_steps=steps,
        target_presentations=saved["trained_targets"],final_training_loss=saved["history"][-1]["mean_loss"],
        training_elapsed_seconds=saved["elapsed_seconds"],model_sha256=sha(MODEL/"trained_model.pt"),
        model_bytes=(MODEL/"trained_model.pt").stat().st_size,testing_performed=False,
        continuation=dict(initial_epochs=plan["initial_epochs"],additional_epochs=plan["additional_epochs"],
                          initial_model_sha256=plan["initial_model_sha256"],base_commit=plan["base_commit"],
                          runner_sha256=sha(__file__),request_sha256=sha(WORK/"request.json"),
                          optimizer_state_preserved=True,published=False,
                          previous_test_model="runs/epochs_10_snapshot/trained_model.pt"))
    atomic_json(MODEL/"trained_model.json",result)
    (MODEL/"runs/README.md").write_text(
        "# Seed-model training run\n\nTraining completed thirty epochs on the existing 693 training families. "
        "The additional twenty epochs continued the model and optimizer from epochs_10_snapshot/. "
        "latest.pt retains the current optimizer and weights, training.jsonl contains all thirty epochs, "
        "and training_status.json gives progress. extra_20_epochs/ records this cluster-only continuation. "
        "Existing test results and the report describe the archived ten-epoch model. "
        "The continued model has not been tested or published to GitHub.\n",encoding="utf-8")
    text=(MODEL/"README.md").read_text(encoding="utf-8")
    text=text.replace("Continuation requested: twenty additional epochs, from ten to thirty total.",
                      "Continuation completed: twenty additional epochs, from ten to thirty total.")
    (MODEL/"README.md").write_text(text,encoding="utf-8")
    write_status("complete",epochs_completed=goal,additional_epochs_completed=plan["additional_epochs"],
                 optimizer_steps=steps,model_sha256=result["model_sha256"],testing_performed=False,github_publication=False)
    print(json.dumps(dict(status="complete",epochs=goal,model_sha256=result["model_sha256"])),flush=True)
if __name__=="__main__":
    try:main()
    except BaseException as e:
        write_status("interrupted",type=type(e).__name__,message=str(e),
                     checkpoint="../latest.pt",github_publication=False)
        raise
