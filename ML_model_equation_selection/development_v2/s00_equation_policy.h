// Learned equation filter. Exact IBP construction and algebra stay in Kira.
#pragma once
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <map>
#include <mutex>
#include <set>
#include <sstream>
#include <unordered_map>
#include <vector>
namespace kira_eq {
constexpr size_t NF=24;
using Features=std::array<double,NF>;
inline double now(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
struct Node{int f,left,right;double cut,p;};
struct Row{Features x;std::string support;double p;bool keep;};
struct State {
 std::string mode="off",records,metrics;
 std::vector<Node> nodes;
 std::vector<std::vector<int>> targets;
 std::unordered_map<pyred::Weight,bool> target_weights;
 std::map<unsigned,std::pair<int,int>> sector_limits;
 std::unordered_map<std::string,Row> cache;
 std::set<std::string> selected;
 std::mutex mutex;
 int loops=0,external=0,maxdots=0,maxsps=0;
 double threshold=0,seconds=0;size_t calls=0,kept=0,unique_kept=0,retrievals=0;
 State(){
  if(auto p=std::getenv("KIRA_EQ_MODE"))mode=p;
  if(mode=="off")return;
  if(auto p=std::getenv("KIRA_EQ_RECORDS"))records=p;
  if(auto p=std::getenv("KIRA_EQ_METRICS"))metrics=p;
  if(auto p=std::getenv("KIRA_EQ_THRESHOLD"))threshold=std::stod(p);
  if(auto p=std::getenv("KIRA_EQ_CONTEXT")){
   std::ifstream in(p);size_t nt,n;in>>loops>>external>>nt>>n;
   if(!in||nt>4096||n>128)throw std::runtime_error("Invalid equation context");
   for(size_t j=0;j<nt;++j){std::vector<int>a(n);unsigned sector=0;int d=0,s=0;
    for(size_t i=0;i<n;++i){in>>a[i];if(i<32&&a[i]>0)sector|=1u<<i;d+=std::max(0,a[i]-1);s+=std::max(0,-a[i]);}
    targets.push_back(a);auto &lim=sector_limits[sector];lim.first=std::max(lim.first,d);lim.second=std::max(lim.second,s);
    maxdots=std::max(maxdots,d);maxsps=std::max(maxsps,s);
   }
  }
  if(targets.empty())throw std::runtime_error("Missing equation target context");
  if(mode=="learned"){
   const char*p=std::getenv("KIRA_EQ_WEIGHTS");if(!p)throw std::runtime_error("Missing equation weights");
   std::ifstream in(p);size_t n;in>>n;if(!in||n>4095||!n)throw std::runtime_error("Bad equation tree");
   nodes.resize(n);for(auto &a:nodes)in>>a.f>>a.cut>>a.left>>a.right>>a.p;
   if(!in)throw std::runtime_error("Incomplete equation tree");
  }
 }
 ~State(){
  if(mode=="off")return;
  if(!records.empty()){
   std::ofstream out(records);
   out<<std::setprecision(17);
   // labels are membership of the final regenerated native equation system.
   for(const auto &kv:cache){out<<kv.first<<'\t'<<selected.count(kv.second.support);
    for(double x:kv.second.x)out<<'\t'<<x;
    out<<'\t'<<kv.second.p<<'\t'<<kv.second.keep<<'\n';
   }
  }
  if(!metrics.empty()){
   std::ofstream out(metrics);
   out<<std::setprecision(17)<<"{\"mode\":\""<<mode<<"\",\"candidate_calls\":"<<calls<<",\"retained_calls\":"<<kept
      <<",\"unique_candidates\":"<<cache.size()<<",\"unique_retained\":"<<unique_kept<<",\"filter_seconds\":"<<seconds
      <<",\"selected_supports\":"<<selected.size()<<",\"retrievals\":"<<retrievals<<"}\n";
  }
 }
};
inline State& state(){static State s;return s;}
struct StageTimer {
 const char* name;double start;StageTimer(const char*n):name(n),start(now()){}
 ~StageTimer(){if(const char*p=std::getenv("KIRA_STAGE_METRICS")){std::ofstream out(p,std::ios::app);out<<std::setprecision(17)<<"{\"stage\":\""<<name<<"\",\"seconds\":"<<now()-start<<"}\n";}}
};

inline std::string support(const pyred::eqdata& eq){
 std::map<pyred::Weight,pyred::Coeff_int> coeffs;
 for(const auto &ic:eq)coeffs[ic.first]+=pyred::parse_coeff<pyred::Coeff_int>(ic.second);
 std::set<std::string> indices;
 for(const auto&ic:coeffs)if(ic.second){auto a=pyred::Integral(ic.first);std::ostringstream out;out<<a.m_topoid<<":";for(auto v:a.m_powers)out<<int(v)<<",";indices.insert(out.str());}
 std::string out;for(const auto&a:indices)out+=a+";";return out;
}
inline void retrieve_begin(){
 auto&s=state();if(s.mode!="collect")return;
 std::lock_guard<std::mutex>l(s.mutex);s.selected.clear();++s.retrievals;
}
inline void selected(const pyred::eqdata&eq){
 auto&s=state();if(s.mode!="collect")return;
 std::lock_guard<std::mutex>l(s.mutex);s.selected.insert(support(eq));
}
inline bool allow(const std::vector<pyred::pow_type>&seed,size_t op,const pyred::eqdata&eq){
 auto&s=state();if(s.mode=="off")return true;
 const double start=now();std::lock_guard<std::mutex>l(s.mutex);
 std::string key;for(auto v:seed)key+=std::to_string(v)+",";key+=":"+std::to_string(op);
 ++s.calls;auto it=s.cache.find(key);
 if(it!=s.cache.end()){if(s.mode=="collect")it->second.support=support(eq);s.kept+=it->second.keep;s.seconds+=now()-start;return it->second.keep;}
 if(s.cache.size()>=100000)throw std::runtime_error("Equation candidate bound exceeded");
 Features x{};int dots=0,sps=0,lines=0;unsigned sector=0;
 for(size_t i=0;i<seed.size();++i){lines+=seed[i]>0;dots+=std::max(0,int(seed[i])-1);sps+=std::max(0,-int(seed[i]));if(i<32&&seed[i]>0)sector|=1u<<i;}
 int distance=100000,exact=0;
 for(const auto&a:s.targets){int d=0;for(size_t i=0;i<a.size();++i)d+=std::abs(a[i]-seed[i]);distance=std::min(distance,d);exact|=d==0;}
 auto lim=s.sector_limits.find(sector);bool present=lim!=s.sector_limits.end();
 x[0]=s.loops;x[1]=s.external;x[2]=seed.size();x[3]=std::log1p(s.targets.size());
 x[4]=lines;x[5]=dots;x[6]=sps;x[7]=dots-s.maxdots;x[8]=sps-s.maxsps;
 x[9]=present;x[10]=present?dots-lim->second.first:dots;x[11]=present?sps-lim->second.second:sps;
 x[12]=distance;x[13]=exact;x[14]=op;x[15]=eq.size();
 int chars=0,target_terms=0,maxl=0,maxd=0,maxs=0,mind=1000;
 for(const auto&ic:eq){
  chars+=ic.second.size();auto a=pyred::Integral(ic.first).m_powers;int nl=0,nd=0,ns=0;
  for(auto v:a){nl+=v>0;nd+=std::max(0,int(v)-1);ns+=std::max(0,-int(v));}
  maxl=std::max(maxl,nl);maxd=std::max(maxd,nd);maxs=std::max(maxs,ns);mind=std::min(mind,nd);
  for(const auto&t:s.targets)if(a.size()==t.size()&&std::equal(a.begin(),a.end(),t.begin())){++target_terms;break;}
 }
 x[16]=std::log1p(chars);x[17]=target_terms;x[18]=maxl;x[19]=maxd;x[20]=maxs;x[21]=mind==1000?0:mind;
 x[22]=s.maxdots;x[23]=s.maxsps;
 double p=1;
 if(s.mode=="learned"){size_t i=0;for(size_t depth=0;depth<=32;++depth){
  if(i>=s.nodes.size())throw std::runtime_error("Invalid equation tree index");
  const auto&a=s.nodes[i];if(a.f<0){p=a.p;break;}
  if(a.f>=int(NF)||depth==32)throw std::runtime_error("Invalid equation tree feature/depth");
  i=x[a.f]<=a.cut?a.left:a.right;
 }}
 bool keep=(s.mode!="learned"||p>=s.threshold);
 // Deterministic comparator uses the same available target distance.
 if(s.mode=="distance")keep=distance<=s.threshold;
 Row row{x,s.mode=="collect"?support(eq):"",p,keep};
 s.cache.emplace(std::move(key),std::move(row));s.kept+=keep;s.unique_kept+=keep;s.seconds+=now()-start;return keep;
}
}
