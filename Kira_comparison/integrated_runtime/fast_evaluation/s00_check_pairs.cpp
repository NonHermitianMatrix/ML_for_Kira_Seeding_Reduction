// Compare all six modular features with the original ordered-pair calculation.
#include <string>
#include <vector>
#include <algorithm>
#include <iostream>
#include <random>
#include <stdexcept>
struct BaseIntegral {unsigned length=0;int id=0;std::string coefficientString;};
#include "s15_shared_modular.h"
int main(){
 std::mt19937 rng(20261010);unsigned valid=0,invalid=0;
 const std::vector<std::string> expressions={"1","-1","2","-3","d+1","(d-7)/(d+3)","(d^2-1)/(d-1)","(2*d+3)/(d+4)"};
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
  kira_mod::reset();bool a=kira_mod::prepare_reference(rows.data(),n);auto expected=kira_mod::estimates;
  kira_mod::reset();bool b=kira_mod::prepare_fast(rows.data(),n);
  if(a!=b || expected!=kira_mod::estimates)throw std::runtime_error("Unordered-pair feature disagreement");
  if(a)++valid;else ++invalid;
 }
 std::cout<<"{\"row_feature_checks\":1000,\"valid\":"<<valid<<",\"invalid\":"<<invalid<<",\"all_passed\":true}"<<std::endl;
}
