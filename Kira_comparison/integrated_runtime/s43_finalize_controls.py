"""Apply model-free controls and the same needed-feature optimization to all row policies."""
import ast,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 assert len(list((HERE/"seed_threshold_training").glob("*.json.gz")))==96,"Finish the uniform threshold scan first"
 model=ROOT/"ML_model_reduction/runtime_training"
 s=(model/"s10_sparse_policy.h").read_text()
 s=s.replace('bool sparse=mode=="learned" && tree.empty() &&','bool sparse=((mode=="learned" && tree.empty()) || mode=="fill") &&')
 s=s.replace('if(k!=1 && k!=2 && k!=16 && k!=18 && k!=22 && weights[k]!=0)sparse=false;','if(mode!="fill" && k!=1 && k!=2 && k!=16 && k!=18 && k!=22 && weights[k]!=0)sparse=false;')
 s=s.replace('if(weights[k]!=0 && std::abs(full[q][k]-f[q][k])>1e-12)','if(((mode=="fill" && k==18) || (mode!="fill" && weights[k]!=0)) && std::abs(full[q][k]-f[q][k])>1e-12)')
 (model/"s11_final_policy.h").write_text(s)
 p=HERE/"s02_run.py";s=p.read_text()
 s=s.replace('if os.environ.get("KIRA_VECTOR_SEED")=="1" and os.environ.get("KIRA_CPP_SEED")!="1":','if os.environ.get("KIRA_VECTOR_SEED")=="1" and os.environ.get("KIRA_CPP_SEED")!="1" and policy!="closure":')
 s=s.replace('if os.environ.get("KIRA_CPP_SEED")=="1":','if os.environ.get("KIRA_CPP_SEED")=="1" and policy!="closure":')
 s=s.replace('".tools/kira-runtime-sparse/kira"]}', '".tools/kira-runtime-sparse/kira",".tools/kira-runtime-final/kira"]}')
 anchor='   threshold=float(os.environ.get("KIRA_SEED_THRESHOLD"'
 at=s.index(anchor)
 if 'if policy=="closure":result["seed_feature_backend"]="deterministic"' not in s:s=s[:at]+'   if policy=="closure":result["seed_feature_backend"]="deterministic"\n'+s[at:]
 ast.parse(s);p.write_text(s)
 p=HERE/"s24_workflow.py";s=p.read_text()
 anchor=' elif kind in ("small","seed","closure","combined"):'
 assert s.count(anchor)==1
 if 'elif kind in ("row_small","fill_small"):' not in s:s=s.replace(anchor,' elif kind in ("row_small","fill_small"):\n  mode="learned" if kind=="row_small" else "fill"\n  steps=[(mode,0),(mode,1)]\n'+anchor)
 ast.parse(s);p.write_text(s)
if __name__=="__main__":main()
