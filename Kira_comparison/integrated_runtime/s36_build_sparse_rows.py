"""Specialize feature construction for the fitted sparse linear row policies."""
import pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 folder=ROOT/"ML_model_reduction/runtime_training"
 s=(folder/"s07_fast_policy.h").read_text()
 s=s.replace("inline unsigned long long feature_parity_checked=0;","inline unsigned long long feature_parity_checked=0,sparse_groups=0;")
 s=s.replace("feature_parity_checked=0;active=true;","feature_parity_checked=0;sparse_groups=0;active=true;")
 s=s.replace('<<",\\\"decision_seconds\\\":"<<decision_seconds', '<<",\\\"sparse_groups\\\":"<<sparse_groups<<",\\\"decision_seconds\\\":"<<decision_seconds')
 anchor=" std::vector<Features> f=fast_features(rows,n);"
 assert s.count(anchor)==1
 replacement=r'''
 bool sparse=mode=="learned" && tree.empty() &&
   std::getenv("KIRA_SPARSE_FEATURES") && std::string(std::getenv("KIRA_SPARSE_FEATURES"))=="1";
 for(unsigned k=0;k<NF;++k)
  if(k!=1 && k!=2 && k!=16 && k!=18 && k!=22 && weights[k]!=0)sparse=false;
 std::vector<Features> f;
 if(sparse){
  ++sparse_groups;f.resize(n);
  for(unsigned q=0;q<n;++q){
   f[q].fill(0);
   f[q][1]=std::log1p(rows[q][0].length);
   if(weights[2]!=0)f[q][2]=std::log1p(double(bytes(rows[q])));
   f[q][16]=double(q==0);f[q][18]=kira_mod::estimates[q][0];f[q][22]=kira_mod::estimates[q][4];
  }
 }else f=fast_features(rows,n);
 if(sparse && std::getenv("KIRA_SPARSE_PARITY")){
  auto full=fast_features(rows,n);
  for(unsigned q=0;q<n;++q)for(unsigned k=0;k<NF;++k)
   if(weights[k]!=0 && std::abs(full[q][k]-f[q][k])>1e-12)
    throw std::runtime_error("Sparse row feature parity failed");
  ++feature_parity_checked;
 }
 // Training and debug records retain all feature values.
 if(sparse && records.is_open())f=fast_features(rows,n);
'''
 s=s.replace(anchor,replacement)
 (folder/"s10_sparse_policy.h").write_text(s)
if __name__=="__main__":main()
