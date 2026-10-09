// Experimental individual-seed gate for Kira/pyRed; GPL-3.0-or-later.
#ifndef KIRA_ACCEL_SEED_FILTER
#define KIRA_ACCEL_SEED_FILTER
#include <atomic>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <mutex>
#include <set>
#include <stdexcept>
#include <unordered_set>
namespace kira_accel {
class SeedGate {
 bool enabled=false;
 std::unordered_set<pyred::Integral> allowed;
 std::atomic<unsigned long long> seen{0},kept{0};
 std::mutex mutex;
 std::set<std::string> used;
public:
 SeedGate(){
  const char* path=std::getenv("KIRA_ML_SEEDS");
  if(!path || !*path)return;
  enabled=true;std::ifstream in(path);
  if(!in)throw std::runtime_error("Cannot open explicit ML seed list");
  std::string line;while(std::getline(in,line))if(!line.empty())allowed.insert(pyred::Integral(line));
 }
 bool accept(uint32_t topo,const std::vector<pyred::pow_type>& powers){
  if(!enabled)return true;
  ++seen;pyred::Integral seed(topo,powers);
  if(!allowed.count(seed))return false;
  ++kept;
  const char* audit=std::getenv("KIRA_ML_SEED_AUDIT");
  if(audit && *audit){
   std::ostringstream s;s<<seed;std::lock_guard<std::mutex> lk(mutex);used.insert(s.str());
  }
  return true;
 }
 ~SeedGate(){
  const char* path=std::getenv("KIRA_ML_SEED_AUDIT");
  if(!enabled || !path || !*path)return;
  std::ofstream out(path);out<<"{\"seen\":"<<seen<<",\"accepted_calls\":"<<kept<<",\"allowed\":"<<allowed.size()<<",\"used\":[";
  bool first=true;for(const auto& s:used){if(!first)out<<",";first=false;out<<std::quoted(s);}out<<"]}\n";
 }
};
inline bool seed_allowed(uint32_t topo,const std::vector<pyred::pow_type>& seed){
 static SeedGate gate;return gate.accept(topo,seed);
}
}
#endif
