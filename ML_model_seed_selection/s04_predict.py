"""Rank an input target's bounded candidate pool using an explicitly supplied trained checkpoint."""
import argparse, hashlib, json, pathlib
import torch
from s01_data import HERE, encode, find_input, read
from s02_model import SeedSelector

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
    with torch.no_grad(): probs=model.probabilities(encode(target,family,seeds,cfg)).tolist()
    ranked=sorted(zip(seeds,probs),key=lambda t:(-t[1],tuple(t[0])))
    print(json.dumps(dict(target=args.target,meaning="probability of membership in the recorded reference seed set",
                          candidates=[dict(indices=s,probability=v) for s,v in ranked]),indent=2))
if __name__=="__main__": main()
