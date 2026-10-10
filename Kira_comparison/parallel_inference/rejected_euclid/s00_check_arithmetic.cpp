// Exact checks for field inversion and all source-row features.
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>
#include <random>
#include <stdexcept>
#include <chrono>
#include <iomanip>
struct BaseIntegral {unsigned length=0;int id=0;std::string coefficientString;};
#define kira_mod baseline_mod
#include "s15_shared_modular.h"
#undef kira_mod
#include "s17_euclid_modular.h"
double now(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
int main(){
 std::mt19937 rng(20261010);unsigned valid=0,invalid=0;
 for(unsigned i=0;i<100000;++i){
  long long a=i<4096?i+1:i<8192?kira_mod::P-(i-4096+1):1+rng()%(kira_mod::P-1);
  auto b=kira_mod::inverse(a);
  if(b<1 || b>=kira_mod::P || b!=baseline_mod::power(a,kira_mod::P-2) || a*b%kira_mod::P!=1)
   throw std::runtime_error("Inverse mismatch");
 }
 const std::vector<std::string> expressions={"1","-1","2","-3","d+1","(d-7)/(d+3)","(d^2-1)/(d-1)","(2*d+3)/(d+4)","d^(-2)","((d^3-3*d+8)/(d^2+7))/(d-8)"};
 double old_time=0,new_time=0;
 for(unsigned trial=0;trial<1000;++trial){
  unsigned n=2+rng()%15;
  std::vector<std::vector<BaseIntegral>> data(n);std::vector<BaseIntegral*> rows(n);
  for(unsigned j=0;j<n;++j){
   data[j].push_back({0,1000,expressions[rng()%expressions.size()]});
   for(int k=60;k>0;--k)if(rng()%4==0)data[j].push_back({0,k,expressions[rng()%expressions.size()]});
   data[j][0].length=data[j].size();rows[j]=data[j].data();
  }
  if(trial%11==0)data[0][0].coefficientString="d-17";
  if(trial%13==0)data[n-1].back().coefficientString="1/(d-19)";
  if(trial%17==0)data[n-1].back().coefficientString="s+d";
  std::vector<double> times[2];bool ok[2]={};
  for(unsigned rep=0;rep<5;++rep){
   for(unsigned pos=0;pos<2;++pos){
    unsigned flag=(rep+trial+pos)%2;double t;
    if(flag){kira_mod::reset();t=now();ok[1]=kira_mod::prepare_fast(rows.data(),n);times[1].push_back(now()-t);}
    else{baseline_mod::reset();t=now();ok[0]=baseline_mod::prepare_fast(rows.data(),n);times[0].push_back(now()-t);}
   }
   if(ok[0]!=ok[1] || baseline_mod::estimates!=kira_mod::estimates)throw std::runtime_error("Feature mismatch");
  }
  for(auto& t:times)std::sort(t.begin(),t.end());
  old_time+=times[0][2];new_time+=times[1][2];
  if(ok[0])++valid;else ++invalid;
 }
 std::cout<<std::setprecision(17)<<"{\"all_passed\":true,\"inverse_checks\":100000,\"row_feature_checks\":1000,\"repetitions\":5,\"valid\":"<<valid<<",\"invalid\":"<<invalid<<",\"old_seconds\":"<<old_time<<",\"new_seconds\":"<<new_time<<",\"ratio\":"<<new_time/old_time<<"}"<<std::endl;
}
