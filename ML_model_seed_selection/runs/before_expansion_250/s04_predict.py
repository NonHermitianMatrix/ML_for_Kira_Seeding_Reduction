"""Rank an input target's bounded candidate pool using an explicitly supplied trained checkpoint."""
import argparse, hashlib, json, pathlib
import torch
from s01_data import HERE, encode, find_input, read
from s02_model import SeedSelector, binary_decisions

def load_model(path):
    # Only load checkpoints produced by this project from a trusted location.
    data = torch.load(str(path),map_location="cpu")
    if data.get("status")!="trained" or data.get("optimizer_steps",0)<1:
        raise ValueError("Inference requires trained weights; no trained checkpoint exists at preparation time")
    digest = hashlib.sha256((HERE/"split_manifest.json").read_bytes()).hexdigest()
    if data.get("manifest_sha256")!=digest: raise ValueError("Checkpoint uses a different data split")
    cfg = data["config"]
    torch.set_num_threads(cfg["cpu_threads"])
    model = SeedSelector(cfg)
    model.load_state_dict(data["model"])
    model.eval()
    return model,cfg,data

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=pathlib.Path,required=True)
    p.add_argument("--target",required=True)
    p.add_argument("--seeds",type=pathlib.Path,help="Optional public candidate list in {'indices': [...]} form")
    args=p.parse_args()
    model,cfg,_=load_model(args.checkpoint)
    target,family,seeds=find_input(args.target)
    if args.seeds: seeds=read(args.seeds)["indices"]
    with torch.no_grad():
        probabilities=model.probabilities(encode(target,family,seeds,cfg))
        decisions=binary_decisions(probabilities)
    candidates=[dict(indices=s,predicted_label=int(decisions["predicted_label"][i]),
                     probability_1=float(decisions["probability_1"][i]),
                     probability_0=float(decisions["probability_0"][i]),
                     confidence=float(decisions["confidence"][i])) for i,s in enumerate(seeds)]
    candidates.sort(key=lambda row:(-row["probability_1"],tuple(row["indices"])))
    print(json.dumps(dict(target=args.target,
                          meaning="Binary membership in the recorded reference seed set",
                          decision_threshold=0.5,
                          confidence_meaning="Uncalibrated model-estimated probability of the returned label",
                          ranking="descending probability_1",
                          candidates=candidates),indent=2))
if __name__=="__main__": main()
