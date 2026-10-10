"""Return probabilities and the chosen native source-row candidate."""
import argparse,json,pathlib
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
def predict(features,model=None):
 m=model or json.loads((HERE/"trained_model.json").read_text())
 x=np.array(features,dtype=float)
 if x.ndim!=2 or x.shape[1]!=m["features"] or not len(x):raise ValueError("Expected nonempty candidate feature rows")
 if "nodes" in m:
  if len(x)<m.get("minimum_group_size",3) or len(x)>m.get("maximum_group_size",32):
   return dict(selected=0,confidence=None,probabilities=None,decision_source="native size guard")
  from s08_train_tree import predict as tree
  score=np.array([0.]+[tree(m["nodes"],a-x[0]) for a in x[1:]])
  gain=m["minimum_predicted_gain"]
 else:
  score=(x-np.array(m["mean"]))/np.array(m["scale"])@np.array(m["weights"])+m["bias"]
  gain=m["minimum_predicted_log_gain"]
 q=int(score.argmin())
 if score[q]>score[0]-gain:q=0
 p=np.exp(-(score-score.min()));p/=p.sum()
 return dict(selected=q,confidence=float(p[q]),probabilities=p.tolist(),predicted_score=score.tolist(),decision_source="learned cost ranking")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("input",type=pathlib.Path);a=ap.parse_args()
 print(json.dumps(predict(json.loads(a.input.read_text())["features"])))
if __name__=="__main__":main()
