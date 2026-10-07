"""Implementation checks only: no optimizer, learned checkpoint or performance estimate."""
import copy, json, resource, unittest
import torch
from s00_prepare_data import group_for
from s01_data import HERE, DATA, config, read, encode, find_input, labels, family_records, storage_guard
from s02_model import SeedSelector, reference_loss, binary_decisions
from s05_evaluate import seed_metrics, confidence_bins

class ModelChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg=config()
        torch.set_num_threads(1)
        torch.manual_seed(20261004)
        cls.model=SeedSelector(cls.cfg).eval()
        cls.before={k:v.clone() for k,v in cls.model.state_dict().items()}
        cls.target,cls.family,cls.seeds=find_input("box_profile_0001:T00001")
        cls.x=encode(cls.target,cls.family,cls.seeds,cls.cfg)

    def test_grouped_split(self):
        manifest=read(HERE/"split_manifest.json")["families"]
        seen={}
        sums={"train":0,"test":0}
        for row in manifest:
            self.assertEqual(seen.setdefault(row["group"],row["split"]),row["split"])
            self.assertEqual(group_for(read(DATA/row["definition"])),row["group"])
            sums[row["split"]]+=row["counts"]["targets"]
        self.assertEqual(sum(sums.values()),240472)
        self.assertLessEqual(abs(sums["train"]-0.7*sum(sums.values())),1)
        self.assertEqual(len(manifest),1000)

    def test_shapes_all_initial_families(self):
        manifest=read(HERE/"split_manifest.json")["families"]
        selected=[m for m in manifest if not m["family"].startswith("box_profile_")]
        selected += [next(m for m in manifest if m["family"]==f) for f in ("box_profile_0001","box_profile_0322")]
        for meta in selected:
            t,f,seeds,y=next(family_records(meta,self.cfg))
            x=encode(t,f,seeds,self.cfg)
            with torch.no_grad(): z=self.model(x)
            self.assertEqual(tuple(z.shape),(len(seeds),))
            self.assertTrue(torch.isfinite(z).all())
            self.assertTrue(torch.isfinite(reference_loss(z,y)))
            self.assertTrue(((z.sigmoid()>0)&(z.sigmoid()<1)).all())

    def test_candidate_permutation(self):
        order=torch.arange(len(self.seeds)-1,-1,-1)
        x=dict(self.x,seeds=self.x["seeds"][order])
        with torch.no_grad(): a,b=self.model(self.x),self.model(x)
        torch.testing.assert_close(b,a[order],rtol=1e-5,atol=1e-6)

    def test_chunk_equivalence(self):
        other=SeedSelector(dict(self.cfg,pair_chunk=3,candidate_chunk=7)).eval()
        other.load_state_dict(self.model.state_dict())
        with torch.no_grad(): a,b=self.model(self.x),other(self.x)
        torch.testing.assert_close(a,b,rtol=1e-5,atol=1e-6)

    def test_coefficients_and_positions(self):
        target=copy.deepcopy(self.target)
        target["terms"][0]["coefficient"]="(d-3)/(d-7)"
        x=encode(target,self.family,self.seeds,self.cfg)
        self.assertFalse(torch.equal(self.x["terms"],x["terms"]))
        target=copy.deepcopy(self.target)
        target["terms"].reverse()
        x=encode(target,self.family,self.seeds,self.cfg)
        self.assertFalse(torch.equal(self.x["terms"],x["terms"]))
        self.assertEqual(x["terms"].shape[0],len(target["terms"]))

    def test_reference_information_is_excluded(self):
        poisoned=copy.deepcopy(self.target)
        poisoned.update(sufficient_seeds=[[999]],master_coefficients=[{"coefficient":"999"}],
                        construction={"steps":"private"},split="private",id="private",
                        family="private",reduction_steps=999,modular_terms={"fake":999})
        x=encode(poisoned,self.family,self.seeds,self.cfg)
        for key in x: self.assertTrue(torch.equal(x[key],self.x[key]))

    def test_gradients_without_updates(self):
        z=self.model(self.x)
        y=torch.zeros_like(z);y[0]=1
        gradients=torch.autograd.grad(reference_loss(z,y),tuple(self.model.parameters()))
        self.assertTrue(all(torch.isfinite(g).all() for g in gradients))
        self.assertTrue(all(float(g.abs().sum())>0 for g in gradients))
        for key,value in self.model.state_dict().items():
            self.assertTrue(torch.equal(value,self.before[key]))

    def test_binary_labels_and_confidence(self):
        p=torch.tensor([0.08,0.49,0.5,0.9,0.0,1.0])
        result=binary_decisions(p)
        self.assertEqual(result["predicted_label"].tolist(),[0,0,1,1,0,1])
        torch.testing.assert_close(result["probability_1"]+result["probability_0"],torch.ones_like(p))
        torch.testing.assert_close(result["confidence"],torch.tensor([0.92,0.51,0.5,0.9,1.0,1.0]))
        # A confident zero remains a low-ranked seed when sorting by membership probability.
        order=torch.argsort(result["probability_1"],descending=True)
        self.assertEqual(result["predicted_label"][order].tolist(),[1,1,1,0,0,0])
        for bad in (torch.tensor([-0.1]),torch.tensor([1.1]),torch.tensor([float("nan")])):
            with self.assertRaises(ValueError): binary_decisions(bad)

    def test_loss_follows_reference_labels(self):
        y=torch.tensor([1.,0.,1.])
        good=torch.tensor([3.,-3.,3.])
        self.assertLess(float(reference_loss(good,y)),float(reference_loss(-good,y)))

    def test_confidence_comparison(self):
        c,q,h=confidence_bins(torch.tensor([0.1,0.9,0.51]),torch.tensor([0.,0.,1.]))
        self.assertEqual(int(c.sum()),3)
        self.assertEqual(int(h.sum()),2)
        self.assertAlmostEqual(float(q.sum()),2.31,places=6)
        self.assertEqual(int(c[10:].sum()),2)

    def test_known_metric_values(self):
        result=seed_metrics(torch.tensor([0.9,0.1,0.8]),torch.tensor([1.,0.,1.]))
        self.assertEqual(result["average_precision"],1.0)
        self.assertEqual(result["recall_at_1"],0.5)
        self.assertEqual(result["recall_at_reference_size"],1.0)
        empty=seed_metrics(torch.tensor([0.1,0.2]),torch.zeros(2))
        self.assertNotIn("average_precision",empty)
        self.assertEqual(empty["jaccard_at_0_5"],1.0)

    def test_bounds_and_labels(self):
        with self.assertRaises(ValueError): encode(self.target,self.family,self.seeds*2,self.cfg)
        with self.assertRaises(ValueError): labels({"sufficient_seeds":[[999]*4]},self.seeds)
        with self.assertRaises(ValueError): encode(self.target,self.family,[],self.cfg)

def main():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ModelChecks))
    assert result.wasSuccessful(),"Implementation checks failed"
    model=SeedSelector(config())
    summary=dict(status="checks_passed_untrained",checks=result.testsRun,optimizer_steps=0,
                 parameter_count=sum(p.numel() for p in model.parameters()),
                 torch_version=torch.__version__,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 project_bytes=storage_guard(),checkpoint_created=False,
                 note="Forward, gradient and data-boundary checks only. No optimizer updates or trained evaluation.")
    (HERE/"implementation_checks.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary),flush=True)

if __name__=="__main__":main()
