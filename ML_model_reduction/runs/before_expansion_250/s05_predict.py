"""Return all next-step probabilities; optionally apply the selected exact row operation."""
import argparse,json,pathlib
import numpy as np
import torch
from s00_common import HERE,read
from s01_state import encode_state,normalize_state,eliminate,column
from s03_model import ReductionSelector

class Predictor:
    def __init__(self,checkpoint=None):
        saved=torch.load(checkpoint or HERE/"trained_model.pt",map_location="cpu",weights_only=False)
        self.cfg=saved["config"];torch.set_num_threads(self.cfg["cpu_threads"])
        self.model=ReductionSelector(saved["feature_dim"],self.cfg)
        self.model.load_state_dict(saved["model"]);self.model.eval()
    def predict(self,state,apply=False):
        matrix,masters,prime=normalize_state(state,self.cfg)
        actions=state["actions"]
        if not actions:
            targets=[k for k,v in state["row_roles"].items() if v=="target"]
            complete=bool(targets) and all(set(matrix[k])<=masters for k in targets)
            return dict(status="complete" if complete else "no_allowed_action",
                        selected_step=None,confidence=None,probabilities=[],has_choice=False)
        features=encode_state(state,self.cfg)
        with torch.inference_mode():
            logits=self.model(torch.from_numpy(features)[None,:,:],
                              torch.ones((1,len(actions)),dtype=torch.bool))[0]
            p=torch.softmax(logits,dim=0).cpu().numpy()
        # Stable identifiers resolve exact ties; their text does not enter model inputs.
        selected=min(range(len(actions)),key=lambda i:(-float(p[i]),actions[i]["id"]))
        result=dict(status="step_selected",selected_step=actions[selected],confidence=float(p[selected]),
                    probabilities=[dict(step=a,probability=float(v)) for a,v in zip(actions,p)],
                    has_choice=len(actions)>1,
                    confidence_meaning="uncalibrated reference-choice probability; a forced action has probability one")
        if apply:
            a=actions[selected];q=a["source_row"];r=a["destination_row"];k=column(a["pivot_indices"])
            after,factor=eliminate(matrix[r],matrix[q],k,prime)
            result["exact_update"]=dict(destination_row=r,coefficients=after,factor_mod_prime=factor,prime=prime)
        return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("state",type=pathlib.Path)
    ap.add_argument("--checkpoint",type=pathlib.Path);ap.add_argument("--apply",action="store_true")
    ap.add_argument("--output",type=pathlib.Path);args=ap.parse_args()
    if args.state.stat().st_size>33554432:raise ValueError("Input file exceeds 32 MiB")
    result=Predictor(args.checkpoint).predict(read(args.state),args.apply)
    text=json.dumps(result,indent=2,allow_nan=False)+"\n"
    if args.output:args.output.write_text(text,encoding="utf-8")
    else:print(text,end="")
if __name__=="__main__":main()
