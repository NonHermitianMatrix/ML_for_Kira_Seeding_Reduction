// Source-row cost policy for Kira; GPL-3.0-or-later.
#pragma once
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include "s12_cached_modular.h"
namespace kira_cost {
constexpr unsigned NF=24;
inline double decision_seconds=0;
inline unsigned long long feature_parity_checked=0,sparse_groups=0;
using Features=std::array<double,NF>;
inline double now(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
inline unsigned long long updates=0,operations=0,groups=0,changed=0,peak=0,training_groups=0;
inline bool probing=false,active=false;
inline std::ofstream records;
inline std::string mode;
inline std::array<double,NF> center{},scale{},weights{};
inline double bias=0,gain=0;
struct TreeNode {int feature,left,right;double cut,value;};
inline std::vector<TreeNode> tree;
inline unsigned long long bytes(BaseIntegral* r){
 unsigned long long n=0;for(unsigned j=0;j<r[0].length;j++)n+=r[j].coefficientString.size();return n;
}
inline void before(BaseIntegral* d,BaseIntegral* s){
 if(!active||probing)return;
 ++updates;operations+=1+2*s[0].length;peak=std::max<unsigned long long>(peak,std::max(d[0].length,s[0].length));
}
inline void after(BaseIntegral*,unsigned n){if(active&&!probing)peak=std::max<unsigned long long>(peak,n);}
inline void start(){
 mode=std::getenv("KIRA_COST_MODE")?std::getenv("KIRA_COST_MODE"):"native";
 tree.clear();kira_mod::reset();decision_seconds=0;feature_parity_checked=0;sparse_groups=0;active=true;updates=operations=groups=changed=peak=training_groups=0;
 const char* path=std::getenv("KIRA_COST_RECORDS");if(path){records.open(path,std::ios::app);if(!records)throw std::runtime_error("Cannot open cost records");}
 if(mode=="learned"){
  const char* path=std::getenv("KIRA_COST_WEIGHTS");if(!path)throw std::runtime_error("Missing cost weights");
  std::ifstream in(path);unsigned n;in>>n>>bias>>gain;if(n!=NF)throw std::runtime_error("Cost feature count");
  for(auto& x:center)in>>x;
  for(auto& x:scale)in>>x;
  for(auto& x:weights)in>>x;
  if(!in)throw std::runtime_error("Invalid cost weights");
  for(double x:scale)if(!(x>0))throw std::runtime_error("Invalid cost normalization");
  unsigned count=0;
  if(in>>count){
   if(count>127)throw std::runtime_error("Cost tree capacity");
   tree.resize(count);
   for(auto& node:tree){
    in>>node.feature>>node.cut>>node.left>>node.right>>node.value;
    if(node.feature>=int(NF)||node.feature< -1)throw std::runtime_error("Cost tree feature");
   }
   if(!in)throw std::runtime_error("Invalid cost tree");
   for(auto& node:tree)if(node.feature>=0 && (node.left<0||node.right<0||node.left>=int(count)||node.right>=int(count)))throw std::runtime_error("Cost tree child");
  }

 }
}
inline void finish(double seconds){
 if(const char* p=std::getenv("KIRA_COST_METRICS")){
  std::ofstream o(p,std::ios::app);
  o<<std::setprecision(17)<<"{\"mode\":\""<<mode<<"\",\"updates\":"<<updates<<",\"operations\":"<<operations
   <<",\"groups\":"<<groups<<",\"changed_sources\":"<<changed<<",\"peak_row\":"<<peak
   <<",\"training_groups\":"<<training_groups<<",\"feature_parity_checked\":"<<feature_parity_checked<<",\"sparse_groups\":"<<sparse_groups<<",\"decision_seconds\":"<<decision_seconds<<",\"forward_seconds\":"<<seconds<<"}\n";
 }
 if(records.is_open())records.close();
 active=false;
}
inline Features features(BaseIntegral** rows,unsigned n,unsigned q){
 auto s=rows[q];unsigned ns=s[0].length;double bs=0,mx=0,div=0,mul=0,pow=0,nd=0,bd=0,overlap=0,unions=0,form=0;
 for(unsigned k=0;k<ns;k++){
  auto& t=s[k].coefficientString;bs+=t.size();mx=std::max(mx,double(t.size()));
  div+=std::count(t.begin(),t.end(),'/');mul+=std::count(t.begin(),t.end(),'*');pow+=std::count(t.begin(),t.end(),'^');
 }
 for(unsigned j=0;j<n;j++)if(j!=q){
  auto d=rows[j];unsigned nr=d[0].length;nd+=nr;bd+=bytes(d);
  unsigned a=1,b=1,shared=0;
  while(a<ns&&b<nr){if(s[a].id==d[b].id){++shared;++a;++b;}else if(s[a].id>d[b].id)++a;else ++b;}
  overlap+=shared;unions+=ns+nr-2-shared;
  form+=bs+bytes(d)+(ns-1)*(s[0].coefficientString.size()+d[0].coefficientString.size()+8);
 }
 double p=s[0].coefficientString.size();
 Features f={std::log1p(n),std::log1p(ns),std::log1p(bs),std::log1p(mx),std::log1p(p),
  double(s[0].coefficientString=="1"||s[0].coefficientString=="-1"),
  std::log1p(div),std::log1p(mul),std::log1p(pow),std::log1p(nd),std::log1p(bd),
  std::log1p(overlap),std::log1p(unions),std::log1p(form),std::log1p((n-1)*(1+2*ns)),
  unions/std::max(1.0,nd),double(q==0),std::log1p(bs/std::max(1u,ns)),kira_mod::estimates[q][0],kira_mod::estimates[q][1],kira_mod::estimates[q][2],kira_mod::estimates[q][3],kira_mod::estimates[q][4],kira_mod::estimates[q][5]};
 return f;
}
#include "s06_fast_features.h"
inline void json_features(std::ostream& o,const Features& f){
 o<<"[";for(unsigned k=0;k<NF;k++){if(k)o<<",";o<<std::setprecision(17)<<f[k];}o<<"]";
}
inline BaseIntegral* clone(BaseIntegral* r){
 auto p=new BaseIntegral[r[0].length];std::copy(r,r+r[0].length,p);return p;
}
template<class Insert>
void choose(BaseIntegral** rows,unsigned n,Insert insert){
 if(n<2||!active)return;
 ++groups;
 // Native Kira already put its preferred source at zero. Keep its pivot and
 // group schedule and change only the source when the learned score warrants it.
 if(mode=="native")return;
 // The continuation samples favour native sources in two-row groups.
 // Avoid feature construction for this common case.

 if(n>32)return;
 const unsigned forced_group=std::getenv("KIRA_COST_FORCE_GROUP")?std::stoul(std::getenv("KIRA_COST_FORCE_GROUP")):0;
 if(mode=="forced"&&groups!=forced_group)return;
 const double decision_begin=now();
 const bool modular_valid=kira_mod::prepare(rows,n);
 if(!modular_valid && (mode=="learned"||mode=="fill"))return;

 bool sparse=((mode=="learned" && tree.empty()) || mode=="fill") &&
   std::getenv("KIRA_SPARSE_FEATURES") && std::string(std::getenv("KIRA_SPARSE_FEATURES"))=="1";
 for(unsigned k=0;k<NF;++k)
  if(mode!="fill" && k!=1 && k!=2 && k!=16 && k!=18 && k!=22 && weights[k]!=0)sparse=false;
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
   if(((mode=="fill" && k==18) || (mode!="fill" && weights[k]!=0)) && std::abs(full[q][k]-f[q][k])>1e-12)
    throw std::runtime_error("Sparse row feature parity failed");
  ++feature_parity_checked;
 }
 // Training and debug records retain all feature values.
 if(sparse && records.is_open())f=fast_features(rows,n);

 if(std::getenv("KIRA_COST_FEATURE_PARITY")){
  for(unsigned q=0;q<n;++q){
   Features original=features(rows,n,q);
   for(unsigned k=0;k<NF;++k)
    if(std::abs(original[k]-f[q][k])>1e-12)throw std::runtime_error("Row feature parity failed");
  }
  ++feature_parity_checked;
 }

 unsigned best=0;double confidence=1;std::vector<double> costs(n,0),elapsed(n,0),outnnz(n,0),outbytes(n,0);
 bool measured=false;
 unsigned limit=std::getenv("KIRA_COST_TRAIN_GROUPS")?std::stoul(std::getenv("KIRA_COST_TRAIN_GROUPS")):100;
 if(mode=="collect"&&n<=8&&training_groups<limit){
  bool small=true;for(unsigned q=0;q<n;q++)if(rows[q][0].length>96||bytes(rows[q])>24000)small=false;
  if(small){
   ++training_groups;measured=true;probing=true;
   for(unsigned rep=0;rep<2;rep++)for(unsigned pos=0;pos<n;pos++){
    const unsigned q=rep?(groups+n-1-pos)%n:(groups+pos)%n;
    unsigned long long ops=0;double measured_seconds=0;
    for(unsigned j=0;j<n;j++)if(j!=q){
     auto d=clone(rows[j]);auto source=rows[q];ops+=1+2*source[0].length;
     const double begin=now();const int nz=insert(d,source);
     measured_seconds+=now()-begin;
     if(nz){if(!rep){outnnz[q]+=d[0].length;outbytes[q]+=bytes(d);}delete[] d;}
    }
    elapsed[q]+=measured_seconds/2;costs[q]=ops;
   }
   probing=false;
  }
 }else if(mode=="forced"){
  best=std::stoul(std::getenv("KIRA_COST_FORCE_SOURCE"));
  if(best>=n)throw std::runtime_error("Forced source out of range");
 }else if(mode=="fill"){
  for(unsigned q=0;q<n;++q){costs[q]=f[q][18];if(costs[q]<costs[best])best=q;}
 }else if(mode=="learned"){
  for(unsigned q=0;q<n;q++){
   double score=0;
   if(!tree.empty()){
    if(q){
     unsigned node=0,steps=0;
     while(tree[node].feature>=0){
      if(++steps>tree.size())throw std::runtime_error("Cost tree cycle");
      auto& v=tree[node];node=(f[q][v.feature]-f[0][v.feature]<=v.cut)?v.left:v.right;
     }
     score=tree[node].value;
    }
   }else{
    score=bias;for(unsigned k=0;k<NF;k++)score+=weights[k]*(f[q][k]-center[k])/scale[k];
   }
   costs[q]=score;if(score<costs[best])best=q;
  }
  if(costs[best]>costs[0]-gain)best=0;
  double sum=0;for(double x:costs)sum+=std::exp(std::max(-80.0,std::min(80.0,costs[best]-x)));
  confidence=1/sum;
 }else if(mode!="collect")throw std::runtime_error("Invalid cost policy");
 if(records.is_open() && (measured || mode=="forced" || (mode=="learned"&&groups<=3000))){
  records<<"{\"group\":"<<groups<<",\"pivot\":"<<std::quoted(pyred::Integral(rows[0][0].id).to_string())
   <<",\"prefix_operations\":"<<operations<<",\"measured\":"<<(measured?"true":"false")<<",\"selected\":"<<best<<",\"confidence\":"<<confidence<<",\"candidates\":[";
  for(unsigned q=0;q<n;q++){
   if(q)records<<",";
   records<<"{\"features\":";json_features(records,f[q]);
   records<<",\"score\":"<<costs[q];
   if(measured)records<<",\"seconds\":"<<elapsed[q]<<",\"operations\":"<<costs[q]<<",\"after_nonzeros\":"<<outnnz[q]<<",\"after_bytes\":"<<outbytes[q];
   records<<"}";
  }
  records<<"]}\n";records.flush();
 }
 decision_seconds+=now()-decision_begin;
 if(best){std::swap(rows[0],rows[best]);++changed;}
}
} // namespace kira_cost
