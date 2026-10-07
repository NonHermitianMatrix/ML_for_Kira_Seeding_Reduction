"""Independently check saved prediction counts, confusion counts, hashes and graph files."""
import gzip,hashlib,json,pathlib,sys
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def main():
    results=read(HERE/"test_results.json");manifest=read(HERE/"prediction_manifest.json")
    ids=set();counts=np.zeros(4,np.int64);families=set();positives=0
    for row in manifest["families"]:
        p=HERE/row["path"];assert sha(p)==row["sha256"]
        families.add(row["family"])
        with np.load(str(p),allow_pickle=False) as data:
            prob=data["probabilities"];y=data["labels"].astype(bool);chosen=prob>=.5
            assert np.isfinite(prob).all() and ((prob>=0)&(prob<=1)).all()
            assert prob.shape==y.shape and prob.shape[0]==row["targets"]
            assert str(data["model_sha256"])==results["checkpoint_sha256"]
            new={str(i) for i in data["target_ids"]}
            assert len(new)==row["targets"] and not ids&new;ids.update(new)
            counts+=np.array([np.count_nonzero(~chosen&~y),np.count_nonzero(chosen&~y),
                             np.count_nonzero(~chosen&y),np.count_nonzero(chosen&y)],np.int64)
            positives+=int(y.sum())
    split=read(HERE.parent/"split_manifest.json")
    test=[m for m in split["families"] if m["split"]=="test"]
    expected_targets=sum(m["counts"]["targets"] for m in test)
    expected_positive=sum(m["counts"]["positive_seed_labels"] for m in test)
    expected_labels=sum(m["counts"]["candidate_seed_labels"] for m in test)
    assert len(families)==len(test) and len(ids)==expected_targets and positives==expected_positive and int(counts.sum())==expected_labels
    expected=results["overall"]["confusion"]
    assert counts.tolist()==[expected[k] for k in ("tn","fp","fn","tp")]
    rows=0;seen=set();row_counts=np.zeros(4,np.int64)
    with gzip.open(str(HERE/"per_target_metrics.jsonl.gz"),"rt",encoding="utf-8") as f:
        for line in f:
            row=json.loads(line);rows+=1
            assert row["target"] not in seen;seen.add(row["target"])
            row_counts+=np.array([row[k] for k in ("tn","fp","fn","tp")])
    assert rows==expected_targets and seen==ids and np.array_equal(row_counts,counts)
    curves=read(HERE/"curves.json")
    assert sum(curves["positive_counts"])==expected_positive
    assert sum(curves["negative_counts"])==expected_labels-expected_positive
    assert sum(curves["positive_counts"][2048:])==expected["tp"]
    assert sum(curves["negative_counts"][2048:])==expected["fp"]
    assert sha(HERE.parent/"trained_model.pt")==results["checkpoint_sha256"]
    fm=read(HERE/"figure_manifest.json")
    for name in fm["figures"]:
        for ext in ("pdf","png"):assert (HERE/"figures"/(name+"."+ext)).stat().st_size>1000
        assert sha(HERE/"figures"/(name+".pdf"))==sha(HERE.parent.parent/"report/figures"/(name+".pdf"))
    result=dict(status="passed",targets=rows,families=len(test),candidate_labels=int(counts.sum()),
                positives=positives,confusion_verified=True,prediction_hashes_verified=True,
                model_unchanged=True,report_figure_copies_match=True,figures=len(fm["figures"]))
    (HERE/"validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result),flush=True)
if __name__=="__main__":main()
