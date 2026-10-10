"""Predict reference-membership probabilities from the documented 24 features."""
import argparse,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def predict(features,model):
 if len(features)!=len(model["features"]):raise ValueError("Feature dimension mismatch")
 i=0
 while True:
  n=model["nodes"][i]
  if n["feature"]<0:return n["probability"]
  i=n["left"] if features[n["feature"]]<=n["threshold"] else n["right"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("features",type=pathlib.Path);ap.add_argument("--threshold",type=float,default=.01);a=ap.parse_args()
 m=json.loads((HERE/"trained_model/model.json").read_text());rows=json.loads(a.features.read_text());out=[]
 for row in rows:
  p=predict(row["features"],m);label=int(p>=a.threshold)
  out.append(dict(id=row.get("id"),probability_0=1-p,probability_1=p,label=label,probability_of_label=p if label else 1-p))
 print(json.dumps(out))
if __name__=="__main__":main()
