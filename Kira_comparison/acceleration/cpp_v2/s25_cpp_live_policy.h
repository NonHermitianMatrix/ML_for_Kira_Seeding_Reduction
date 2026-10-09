// Live symbolic forward-elimination experiment; GPL-3.0-or-later.
#pragma once
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <map>
#include <memory>
#include <algorithm>
#include <set>
#include <stdexcept>
#include <vector>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>
#include "/u/home/r/rushil/ML_for_Kira_Seeding_Reduction/Kira_comparison/acceleration/s23_cpp_model.h"
extern char **environ;
namespace kira_live {
using W=pyred::Weight;
using Forward=std::unordered_map<W,std::tuple<BaseIntegral***,int>>;
inline double now() {
 return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline bool active=false;
inline unsigned long long steps=0, operations=0, peak_row=0;
inline std::ofstream trace;
inline void write_row(std::ostream& out, BaseIntegral* p, unsigned n) {
 out << n << "\n";
 for(unsigned i=0;i<n;i++)
   out << pyred::Integral(p[i].id).to_string() << "\t" << p[i].coefficientString << "\n";
}
inline void before(BaseIntegral* dest,BaseIntegral* src) {
 if(!active)return;
 auto a=dest[0].length,b=src[0].length;
 steps++; operations+=1+2*b;peak_row=std::max<unsigned long long>(peak_row,std::max(a,b));
 if(trace.is_open()){trace<<"STEP\n";write_row(trace,src,b);write_row(trace,dest,a);}
}
inline void after(BaseIntegral* dest,unsigned n) {
 if(!active)return;
 peak_row=std::max<unsigned long long>(peak_row,n);
 if(trace.is_open()){write_row(trace,dest,n);trace.flush();}
}
inline void start() {
 if(!std::getenv("KIRA_LIVE_METRICS"))return;
 active=true;steps=operations=peak_row=0;
 auto path=std::getenv("KIRA_LIVE_TRACE");
 if(path){trace.open(path,std::ios::app);if(!trace)throw std::runtime_error("Cannot open row trace");}
}
inline void finish(double seconds) {
 if(!active)return;
 std::ofstream out(std::getenv("KIRA_LIVE_METRICS"),std::ios::app);
 const char* policy=std::getenv("KIRA_LIVE_POLICY");
 out<<"{\"policy\":\""<<(policy?policy:"native")<<"\",\"steps\":"<<steps
    <<",\"coefficient_operations\":"<<operations<<",\"peak_row_nonzeros\":"<<peak_row
    <<",\"forward_seconds\":"<<std::setprecision(17)<<seconds<<"}\n";
 active=false;if(trace.is_open())trace.close();
}
struct Broker {
 FILE *in=nullptr,*out=nullptr; pid_t pid=-1;
 Broker(){
  int parent[2],child[2];if(pipe(parent)||pipe(child))throw std::runtime_error("pipe");
  posix_spawn_file_actions_t fa;posix_spawn_file_actions_init(&fa);
  posix_spawn_file_actions_adddup2(&fa,parent[0],STDIN_FILENO);
  posix_spawn_file_actions_adddup2(&fa,child[1],STDOUT_FILENO);
  posix_spawn_file_actions_addclose(&fa,parent[1]);
  posix_spawn_file_actions_addclose(&fa,child[0]);
  const char* python=std::getenv("KIRA_LIVE_PYTHON");
  const char* server=std::getenv("KIRA_LIVE_SERVER");
  if(!python||!server)throw std::runtime_error("Missing policy server paths");
  char* argv[]={const_cast<char*>(python),const_cast<char*>("-u"),const_cast<char*>(server),nullptr};
  int status=posix_spawn(&pid,python,&fa,nullptr,argv,environ);
  posix_spawn_file_actions_destroy(&fa);close(parent[0]);close(child[1]);
  if(status)throw std::runtime_error("Policy spawn failed");
  in=fdopen(child[0],"r");out=fdopen(parent[1],"w");
  char buf[256];if(!fgets(buf,sizeof(buf),in)||std::string(buf)!="READY\n")
    throw std::runtime_error("Policy server failed during load");
 }
 void row(const char* event,size_t id,BaseIntegral* p){
  unsigned n=p?p[0].length:0;
  fprintf(out,"%s\t%zu\t%u\n",event,id,n);
  for(unsigned i=0;i<n;i++)
   fprintf(out,"%s\t%s\n",pyred::Integral(p[i].id).to_string().c_str(),p[i].coefficientString.c_str());
 }
 std::pair<size_t,size_t> choose(const std::vector<size_t>& group,W pivot){
  fprintf(out,"CHOOSE\t");
  for(size_t i=0;i<group.size();i++)fprintf(out,"%s%zu",i?",":"",group[i]);
  fprintf(out,"\t%s\n",pyred::Integral(pivot).to_string().c_str());fflush(out);
  char buf[256];size_t q,r;double probability;
  if(!fgets(buf,sizeof(buf),in)||sscanf(buf,"%zu %zu %lf",&q,&r,&probability)!=3)
    throw std::runtime_error("Policy server failed while choosing");
  if(q==r||!std::count(group.begin(),group.end(),q)||!std::count(group.begin(),group.end(),r))
    throw std::runtime_error("Policy selected an inadmissible action");
  return {q,r};
 }
 void finish(){
  fprintf(out,"DONE\n");fflush(out);char buf[256];
  if(!fgets(buf,sizeof(buf),in)||std::string(buf)!="DONE\n")throw std::runtime_error("Policy did not finish");
  fclose(out);fclose(in);in=out=nullptr;int status;waitpid(pid,&status,0);pid=-1;
  if(status)throw std::runtime_error("Policy returned failure");
 }
 ~Broker(){if(out)fclose(out);if(in)fclose(in);}
};
template<class Insert>
void forward(Forward& original,std::vector<W>& work,Insert insert,bool learned){
 std::vector<BaseIntegral*> rows;
 std::vector<W> weights;for(auto &kv:original)weights.push_back(kv.first);
 std::sort(weights.begin(),weights.end(),std::greater<W>());
 for(auto w:weights){
  auto &v=original.at(w);auto p=std::get<0>(v);int n=std::get<1>(v);
  for(int j=0;j<n;j++)rows.push_back(p[0][j]);
  delete[] p[0];delete[] p;
 }
 original.clear();work.clear();
 if(rows.size()>10000)throw std::runtime_error("Live model row capacity");
 std::map<W,std::set<size_t>> buckets;
 for(size_t i=0;i<rows.size();i++)buckets[rows[i][0].id].insert(i);
 learned = learned && std::any_of(buckets.begin(),buckets.end(),
     [](const auto& x){return x.second.size()>1;});
 const bool compiled=std::getenv("KIRA_ROW_SCOPE") && std::string(std::getenv("KIRA_ROW_SCOPE"))=="compiled_source";
 std::unique_ptr<Broker> broker;
 if(learned&&!compiled){broker.reset(new Broker());for(size_t i=0;i<rows.size();i++)broker->row("ROW",i,rows[i]);}
 auto cmp=[&](size_t a,size_t b){
  auto x=rows[a],y=rows[b];unsigned nx=x[0].length,ny=y[0].length;
  if(nx!=ny)return nx<ny;
  for(unsigned j=1;j<nx;j++)if(x[j].id!=y[j].id)return x[j].id<y[j].id;
  return a<b;
 };
 size_t step=0;
 while(true){
  auto it=buckets.rbegin();while(it!=buckets.rend()&&it->second.size()<2)++it;
  if(it==buckets.rend())break;
  auto weight=it->first;
  std::vector<size_t> group(it->second.begin(),it->second.end());
  if(++step>30000)throw std::runtime_error("Live step bound");
  if(group.size()*(group.size()-1)>10000)throw std::runtime_error("Live action capacity");
  size_t q,r;
  if(learned){auto action=compiled?kira_cpp::choose(group,rows,weight):broker->choose(group,weight);q=action.first;r=action.second;}
  else {q=*std::min_element(group.begin(),group.end(),cmp);r=group.front()==q?group[1]:group.front();}
  if(rows[q][0].id!=weight||rows[r][0].id!=weight)throw std::runtime_error("Wrong live pivot");
  int nonzero=insert(rows[r],rows[q]);
  buckets[weight].erase(r);
  if(nonzero){
   if(!(rows[r][0].id<weight))throw std::runtime_error("Elimination did not lower leading integral");
   buckets[rows[r][0].id].insert(r);
  }else{rows[r]=nullptr;}
  if(learned&&!compiled)broker->row("UPDATE",r,rows[r]);
 }
 if(learned&&!compiled)broker->finish();
 for(auto &kv:buckets){
  if(kv.second.empty())continue;
  if(kv.second.size()!=1)throw std::runtime_error("Nontriangular live result");
  auto p=new BaseIntegral**[1];p[0]=new BaseIntegral*[1];p[0][0]=rows[*kv.second.begin()];
  original.emplace(kv.first,std::make_tuple(p,1));work.push_back(kv.first);
 }
}
} // namespace

