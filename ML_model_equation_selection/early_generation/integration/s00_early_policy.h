// Predict seed/operator relevance before constructing symbolic IBP equations.
#pragma once
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
namespace kira_eq {
using Features=std::array<double,24>;
inline double now(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
struct Node{int f,left,right;double cut,p;};
struct Seed{Features x{};std::vector<unsigned char> decisions;};
struct State{
 std::string mode="off",metrics;
 std::vector<Node> nodes;
 std::vector<std::vector<int>> targets;
 std::map<unsigned,std::pair<int,int>> sector_limits;
 std::unordered_map<std::string,Seed> seeds;
 std::mutex mutex;
 int loops=0,external=0,maxdots=0,maxrank=0;
 double logtargets=0,threshold=0,seconds=0;
 bool distance=false;
 size_t calls=0,kept=0,unique=0,unique_kept=0,skipped=0;
 State(){
  if(auto p=std::getenv("KIRA_EQ_MODE"))mode=p;
  if(mode=="off")return;
  if(mode!="learned"&&mode!="distance")throw std::runtime_error("Unsupported early equation policy");
  if(auto p=std::getenv("KIRA_EQ_METRICS"))metrics=p;
  if(auto p=std::getenv("KIRA_EQ_THRESHOLD"))threshold=std::stod(p);
  if(mode=="learned"){
   const char*p=std::getenv("KIRA_EQ_WEIGHTS");if(!p)throw std::runtime_error("Missing early equation weights");
   std::ifstream in(p);size_t n;in>>n;if(!in||n==0||n>8191)throw std::runtime_error("Invalid early equation tree");
   nodes.resize(n);
   for(auto &a:nodes){
    in>>a.f>>a.cut>>a.left>>a.right>>a.p;
    if(a.f>=15&&a.f<=21)throw std::runtime_error("Equation construction feature in early tree");
    if(a.f>=24)throw std::runtime_error("Unknown early tree feature");
    distance=distance||a.f==12||a.f==13;
   }
   if(!in)throw std::runtime_error("Incomplete early tree");
  }else distance=true;
  const char*p=std::getenv("KIRA_EQ_CONTEXT");if(!p)throw std::runtime_error("Missing target context");
  std::ifstream in(p);size_t nt,n;in>>loops>>external>>nt>>n;
  if(!in||nt==0||nt>4096||n==0||n>31)throw std::runtime_error("Unsupported early target dimensions");
  for(size_t j=0;j<nt;++j){
   std::vector<int>a(n);unsigned sector=0;int d=0,s=0;
   for(size_t i=0;i<n;++i){in>>a[i];if(a[i]>0)sector|=1u<<i;d+=std::max(0,a[i]-1);s+=std::max(0,-a[i]);}
   targets.push_back(a);auto &lim=sector_limits[sector];lim.first=std::max(lim.first,d);lim.second=std::max(lim.second,s);
   maxdots=std::max(maxdots,d);maxrank=std::max(maxrank,s);
  }
  if(!in)throw std::runtime_error("Incomplete early target context");
  logtargets=std::log1p(targets.size());
 }
 ~State(){
  if(metrics.empty())return;
  std::ofstream out(metrics);
  out<<std::setprecision(17)<<"{\"mode\":\""<<mode<<"\",\"candidate_calls\":"<<calls
   <<",\"retained_calls\":"<<kept<<",\"unique_candidates\":"<<unique<<",\"unique_retained\":"<<unique_kept
   <<",\"construction_skipped_calls\":"<<skipped<<",\"seed_count\":"<<seeds.size()
   <<",\"filter_seconds\":"<<seconds<<"}\n";
 }
};
inline State&state(){static State s;return s;}
struct StageTimer{
 const char*name;double start;StageTimer(const char*n):name(n),start(now()){}
 ~StageTimer(){if(auto p=std::getenv("KIRA_STAGE_METRICS")){std::ofstream out(p,std::ios::app);out<<std::setprecision(17)<<"{\"stage\":\""<<name<<"\",\"seconds\":"<<now()-start<<"}\n";}}
};
inline void retrieve_begin(){}
inline void selected(const pyred::eqdata&){}
inline int precheck(const std::vector<pyred::pow_type>&seed,size_t op){
 auto&s=state();if(s.mode=="off")return 1;
 const double start=now();std::lock_guard<std::mutex>lock(s.mutex);
 if(seed.size()!=s.targets.front().size()||op>4095)throw std::runtime_error("Unsupported seed/operator");
 std::string key(reinterpret_cast<const char*>(seed.data()),seed.size()*sizeof(pyred::pow_type));
 auto it=s.seeds.find(key);
 if(it==s.seeds.end()){
  if(s.seeds.size()>=100000)throw std::runtime_error("Early seed cache limit");
  Seed a;int dots=0,rank=0,lines=0;unsigned sector=0;
  for(size_t i=0;i<seed.size();++i){lines+=seed[i]>0;dots+=std::max(0,int(seed[i])-1);rank+=std::max(0,-int(seed[i]));if(seed[i]>0)sector|=1u<<i;}
  int distance=100000,exact=0;
  if(s.distance)for(const auto&t:s.targets){int d=0;for(size_t i=0;i<t.size();++i){d+=std::abs(t[i]-seed[i]);if(d>=distance)break;}distance=std::min(distance,d);if(d==0){exact=1;break;}}
  const auto lim=s.sector_limits.find(sector);const bool present=lim!=s.sector_limits.end();
  auto&x=a.x;x[0]=s.loops;x[1]=s.external;x[2]=seed.size();x[3]=s.logtargets;
  x[4]=lines;x[5]=dots;x[6]=rank;x[7]=dots-s.maxdots;x[8]=rank-s.maxrank;
  x[9]=present;x[10]=present?dots-lim->second.first:dots;x[11]=present?rank-lim->second.second:rank;
  x[12]=distance;x[13]=exact;x[22]=s.maxdots;x[23]=s.maxrank;
  it=s.seeds.emplace(std::move(key),std::move(a)).first;
 }
 auto&a=it->second;if(a.decisions.size()<=op)a.decisions.resize(op+1,2);
 ++s.calls;
 if(a.decisions[op]==2){
  a.x[14]=op;double p=1;bool leaf=false;
  if(s.mode=="learned"){
   size_t i=0;
   for(size_t depth=0;depth<=24;++depth){
    if(i>=s.nodes.size())throw std::runtime_error("Invalid early tree index");
    const auto&n=s.nodes[i];if(n.f<0){p=n.p;leaf=true;break;}
    i=a.x[n.f]<=n.cut?n.left:n.right;
   }
   if(!leaf)throw std::runtime_error("Early tree depth limit");
  }
  const bool keep=s.mode=="distance"?a.x[12]<=s.threshold:p>=s.threshold;
  a.decisions[op]=keep?1:0;++s.unique;s.unique_kept+=keep;
 }
 const bool keep=a.decisions[op]!=0;s.kept+=keep;s.skipped+=!keep;s.seconds+=now()-start;
 return keep?1:0;
}
inline bool allow(const std::vector<pyred::pow_type>&,size_t,const pyred::eqdata&){return true;}
}
