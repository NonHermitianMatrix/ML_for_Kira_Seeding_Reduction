// Native inference for the frozen source-row policy; GPL-3.0-or-later.
#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "s24_row_weights.h"
namespace kira_cpp {
using U=uint64_t;
using Row=std::map<std::string,U>;
inline U power(U a,U n,U p){U r=1;while(n){if(n&1)r=r*a%p;a=a*a%p;n>>=1;}return r;}
struct Parser {
 const std::string& s;const std::map<std::string,U>& point;size_t i=0;U p;
 Parser(const std::string& text,const std::map<std::string,U>& vars,U prime):s(text),point(vars),p(prime){}
 void space(){while(i<s.size() && std::isspace(static_cast<unsigned char>(s[i])))++i;}
 bool take(char c){space();if(i<s.size()&&s[i]==c){++i;return true;}return false;}
 U expression(){
  U x=term();
  while(true){if(take('+'))x=(x+term())%p;else if(take('-'))x=(x+p-term())%p;else break;}return x;
 }
 U term(){
  U x=unary();
  while(true){space();if(i<s.size()&&s[i]=='*'){++i;x=x*unary()%p;}
   else if(take('/')){U y=unary();if(!y)throw std::runtime_error("Singular row feature point");x=x*power(y,p-2,p)%p;}
   else break;}return x;
 }
 U unary(){if(take('+'))return unary();if(take('-'))return (p-unary())%p;return powered();}
 U powered(){
  U x=atom();
  if(take('^')){
   bool par=take('(');bool neg=take('-');if(!neg)take('+');space();long long n=0;size_t first=i;
   while(i<s.size()&&std::isdigit(static_cast<unsigned char>(s[i]))){n=10*n+s[i++]-'0';if(n>1000000)throw std::runtime_error("Exponent bound");}
   if(first==i || (par&&!take(')')))throw std::runtime_error("Noninteger exponent");
   if(neg){if(!x)throw std::runtime_error("Singular power");x=power(x,p-2,p);}
   x=power(x,static_cast<U>(n),p);
  }return x;
 }
 U atom(){
  if(take('(')){U x=expression();if(!take(')'))throw std::runtime_error("Unclosed coefficient");return x;}
  space();if(i>=s.size())throw std::runtime_error("Empty coefficient");
  if(std::isdigit(static_cast<unsigned char>(s[i]))){U x=0;while(i<s.size()&&std::isdigit(static_cast<unsigned char>(s[i])))x=(x*10+s[i++]-'0')%p;return x;}
  size_t first=i;
  while(i<s.size()&&(std::isalnum(static_cast<unsigned char>(s[i]))||s[i]=='_'))++i;
  if(first==i)throw std::runtime_error("Unsupported coefficient token");
  auto v=point.find(s.substr(first,i-first));if(v==point.end())throw std::runtime_error("Unknown coefficient variable");
  return v->second;
 }
 U value(){U x=expression();space();if(i!=s.size())throw std::runtime_error("Trailing coefficient text");return x;}
};
inline std::vector<int> indices(const std::string& key){
 std::vector<int> out;std::istringstream in(key);std::string item;
 while(std::getline(in,item,','))out.push_back(std::stoi(item));
 return out;
}
inline std::string label(pyred::Weight w){
 auto s=pyred::Integral(w).to_string();auto pos=s.find('[');
 if(pos==std::string::npos||s.back()!=']')throw std::runtime_error("Integral label");
 return s.substr(pos+1,s.size()-pos-2);
}
struct Context {
 U prime=0;size_t dimensions=0;std::map<std::string,U> point;std::set<std::string> masters;
 std::vector<double> family;
 Context(){
  auto path=std::getenv("KIRA_CPP_CONTEXT");if(!path)throw std::runtime_error("Missing native model context");
  std::ifstream in(path);if(!in)throw std::runtime_error("Cannot open native context");size_t n;in>>prime>>dimensions>>n;
  if(prime!=2147483647 || !dimensions || dimensions>16)throw std::runtime_error("Native model context bounds");
  for(size_t j=0;j<n;j++){std::string name;long long value;in>>name>>value;point[name]=((value%static_cast<long long>(prime))+prime)%prime;}
  in>>n;for(size_t j=0;j<n;j++){std::string key;in>>std::quoted(key);masters.insert(key);}
  in>>n;for(size_t j=0;j<n;j++){double x;in>>x;family.push_back(x);}
  if(!in||family.size()!=36)throw std::runtime_error("Native model context format");
 }
};
inline Context& context(){static Context c;return c;}
inline std::array<double,4> complexity(const std::string& key){
 auto a=indices(key);double r=0,s=0,t=0;
 for(int v:a){r+=std::max(v,0);s+=std::max(-v,0);t+=v>0;}return {r,s,t,r-t};
}
inline std::vector<float> pivot_features(const std::string& key,size_t n){
 auto a=indices(key);if(a.size()!=n)throw std::runtime_error("Index dimension");
 std::vector<float> out;
 for(size_t j=0;j<16;j++)out.push_back(j<n?(a[j]?std::copysign(std::log1p(std::abs(a[j])),a[j]):0.):0.);
 for(size_t j=0;j<16;j++)out.push_back(j<n && a[j]>0);
 for(size_t j=0;j<16;j++)out.push_back(j<n);
 auto c=complexity(key);for(double x:c)out.push_back(std::log1p(x));out.push_back(std::log1p(n));return out;
}
inline std::vector<float> row_features(const Row& row,const Context& c){
 size_t m=0;std::array<double,4> total{},maximum{};std::set<unsigned long> sectors;
 for(const auto& kv:row){
  m+=c.masters.count(kv.first);auto a=indices(kv.first);unsigned long sector=0;
  for(size_t j=0;j<a.size();j++)if(a[j]>0)sector|=1UL<<j;
  sectors.insert(sector);auto v=complexity(kv.first);
  for(size_t j=0;j<4;j++){total[j]+=v[j];maximum[j]=std::max(maximum[j],v[j]);}
 }
 std::vector<float> f;for(double x:{double(row.size()),double(m),double(row.size()-m)})f.push_back(std::log1p(x));
 for(double x:total)f.push_back(std::log1p(x/std::max<size_t>(1,row.size())));
 for(double x:maximum)f.push_back(std::log1p(x));
 f.push_back(std::log1p(sectors.size()));return f;
}
inline std::vector<std::vector<float>> features(const std::vector<size_t>& group,const std::map<size_t,Row>& rows,const std::string& pivot){
 const auto& c=context();std::map<std::string,size_t> incidence;size_t nnz=0,maximum=0,master_columns=0;
 for(const auto& kv:rows){nnz+=kv.second.size();maximum=std::max(maximum,kv.second.size());for(const auto& t:kv.second)incidence[t.first]++;}
 for(const auto& kv:incidence)master_columns+=c.masters.count(kv.first);
 std::vector<float> global;
 for(double x:{double(rows.size()),double(incidence.size()),double(nnz),double(master_columns),
    double(nnz)/rows.size(),double(maximum),double(group.size()-1),double(c.dimensions)})global.push_back(std::log1p(x));
 size_t dest=group.back();const auto& dst=rows.at(dest);std::vector<std::vector<float>> out;
 for(size_t q:group){
  if(q==dest)continue;const auto& src=rows.at(q);
  if(!src.count(pivot)||!dst.count(pivot))throw std::runtime_error("Singular model pivot");
  Row after=dst;U factor=dst.at(pivot)*power(src.at(pivot),c.prime-2,c.prime)%c.prime;
  for(const auto& t:src){U v=(after[t.first]+c.prime-factor*t.second%c.prime)%c.prime;if(v)after[t.first]=v;else after.erase(t.first);}
  size_t overlap=0,fill=0,cancelled=0,masters=0;
  for(const auto& t:src)overlap+=dst.count(t.first);
  for(const auto& t:after){fill+=!dst.count(t.first);masters+=c.masters.count(t.first);}
  for(const auto& t:dst)cancelled+=!after.count(t.first);
  auto f=pivot_features(pivot,c.dimensions);auto a=row_features(src,c);auto b=row_features(dst,c);
  f.insert(f.end(),a.begin(),a.end());f.insert(f.end(),b.begin(),b.end());f.insert(f.end(),global.begin(),global.end());
  for(double x:{double(overlap),double(fill),double(cancelled),double(after.size()),double(after.size()-masters),
      double(1+2*src.size()),double(incidence.at(pivot))})f.push_back(std::log1p(x));
  f.push_back(double(overlap)/std::max<size_t>(1,src.size()));f.push_back(double(cancelled)/std::max<size_t>(1,dst.size()));
  f.push_back(double(fill)/std::max<size_t>(1,src.size()));f.push_back(double(masters)/std::max<size_t>(1,after.size()));
  for(double x:c.family)f.push_back(x);
  if(f.size()!=132)throw std::runtime_error("Native feature width");out.push_back(f);
 }return out;
}
inline std::vector<float> linear(const std::vector<float>& x,const float* w,const float* b,size_t n,bool tanh){
 std::vector<float> y(n);
 for(size_t j=0;j<n;j++){float v=b[j];for(size_t k=0;k<x.size();k++)v+=w[j*x.size()+k]*x[k];y[j]=tanh?std::tanh(v):v;}
 return y;
}
inline std::vector<float> probabilities(const std::vector<std::vector<float>>& f){
 using namespace kira_row_weights;std::vector<std::vector<float>> h;std::vector<float> mean(32,0),maximum(32,-INFINITY);
 for(const auto& x:f){
  h.push_back(linear(x,encoder_0_weight,encoder_0_bias,32,true));
  for(size_t j=0;j<32;j++){mean[j]+=h.back()[j];maximum[j]=std::max(maximum[j],h.back()[j]);}
 }
 for(float& x:mean)x/=h.size();
 std::vector<float> scores;float largest=-INFINITY;
 for(auto x:h){x.insert(x.end(),mean.begin(),mean.end());x.insert(x.end(),maximum.begin(),maximum.end());
  auto y=linear(x,scorer_0_weight,scorer_0_bias,score_hidden,true);float z=linear(y,scorer_2_weight,scorer_2_bias,1,false)[0];scores.push_back(z);largest=std::max(largest,z);}
 float total=0;for(float& x:scores){x=std::exp(x-largest);total+=x;}for(float& x:scores)x/=total;return scores;
}
inline std::pair<size_t,size_t> choose(const std::vector<size_t>& group,const std::vector<BaseIntegral*>& native,pyred::Weight w){
 const auto& c=context();std::string pivot=label(w);if(c.masters.count(pivot))throw std::runtime_error("Protected master pivot");
 std::map<size_t,Row> rows;std::map<size_t,std::map<std::string,std::string>> symbolic;
 std::vector<std::vector<float>> f;std::vector<float> p(1,1);bool model=group.size()>2;
 if(model){
  for(size_t id:group){
   auto row=native[id];Row values;
   for(unsigned j=0;j<row[0].length;j++){
    auto k=label(row[j].id);const auto& expr=row[j].coefficientString;U v=Parser(expr,c.point,c.prime).value();
    symbolic[id][k]=expr;if(v)values[k]=v;
   }rows[id]=values;
  }f=features(group,rows,pivot);p=probabilities(f);
 }
 size_t selected=std::max_element(p.begin(),p.end())-p.begin();size_t q=group[selected],r=group.back();
 if(auto path=std::getenv("KIRA_CPP_TRACE")){
  std::ofstream out(path,std::ios::app);out<<std::setprecision(9)<<"{\"source\":"<<q<<",\"destination\":"<<r<<",\"pivot\":"<<std::quoted(pivot)<<",\"used_model\":"<<(model?"true":"false")<<",\"group\":[";
  for(size_t j=0;j<group.size();j++){if(j)out<<",";out<<group[j];}out<<"],\"probabilities\":[";
  for(size_t j=0;j<p.size();j++){if(j)out<<",";out<<p[j];}out<<"]";
  if(model&&std::getenv("KIRA_CPP_FEATURE_AUDIT")){
   out<<",\"features\":[";
   for(size_t i=0;i<f.size();i++){if(i)out<<",";out<<"[";for(size_t j=0;j<f[i].size();j++){if(j)out<<",";out<<f[i][j];}out<<"]";}out<<"],\"rows\":{";
   bool first=true;for(const auto& v:rows){if(!first)out<<",";first=false;out<<std::quoted(std::to_string(v.first))<<":{";bool ft=true;for(const auto& t:v.second){if(!ft)out<<",";ft=false;out<<std::quoted(t.first)<<":"<<t.second;}out<<"}";}out<<"},\"symbolic_rows\":{";
   first=true;for(const auto& v:symbolic){if(!first)out<<",";first=false;out<<std::quoted(std::to_string(v.first))<<":{";bool ft=true;for(const auto& t:v.second){if(!ft)out<<",";ft=false;out<<std::quoted(t.first)<<":"<<std::quoted(t.second);}out<<"}";}out<<"}";
  }out<<"}\n";
 }
 return {q,r};
}
} // namespace kira_cpp
