// Bounded modular estimates of exact row-update cancellations; GPL-3.0-or-later.
#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cctype>
#include <string>
#include <unordered_map>
#include <vector>
namespace kira_mod {
using I=long long;
constexpr I P=2147483647;
inline I power(I a,I n){I z=1;while(n){if(n&1)z=z*a%P;a=a*a%P;n>>=1;}return z;}
// Extended Euclidean inversion in the same prime field; zero is rejected by the parser.
inline I inverse(I a){
 I r=P,next=a,t=0,next_t=1;
 while(next){I q=r/next;I nr=r-q*next;I nt=t-q*next_t;r=next;next=nr;t=next_t;next_t=nt;}
 return t<0?t+P:t;
}
class Parser {
 const std::string& text;size_t pos=0;I dimension;bool ok=true;
 void space(){while(pos<text.size()&&std::isspace(static_cast<unsigned char>(text[pos])))++pos;}
 bool take(char c){space();if(pos<text.size()&&text[pos]==c){++pos;return true;}return false;}
 I atom(){
  space();if(take('(')){I z=expression();if(!take(')'))ok=false;return z;}
  if(pos<text.size()&&text[pos]=='d'){++pos;return dimension;}
  if(pos>=text.size()||!std::isdigit(static_cast<unsigned char>(text[pos]))){ok=false;return 0;}
  I z=0;while(pos<text.size()&&std::isdigit(static_cast<unsigned char>(text[pos]))){z=(10*z+text[pos]-'0')%P;++pos;}return z;
 }
 I raised(){
  I a=atom();if(!take('^'))return a;
  bool bracket=take('(');int sign=1;if(take('-'))sign=-1;else take('+');space();
  if(pos>=text.size()||!std::isdigit(static_cast<unsigned char>(text[pos]))){ok=false;return 0;}
  I n=0;while(pos<text.size()&&std::isdigit(static_cast<unsigned char>(text[pos]))){n=10*n+text[pos]-'0';++pos;if(n>10000){ok=false;return 0;}}
  if(bracket&&!take(')'))ok=false;
  if(sign<0){if(!a){ok=false;return 0;}a=inverse(a);}
  return power(a,n);
 }
 I unary(){if(take('+'))return unary();if(take('-'))return (P-unary())%P;return raised();}
 I term(){
  I a=unary();while(ok){if(take('*'))a=a*unary()%P;else if(take('/')){I b=unary();if(!b){ok=false;return 0;}a=a*inverse(b)%P;}else break;}return a;
 }
 I expression(){I a=term();while(ok){if(take('+'))a=(a+term())%P;else if(take('-'))a=(a-term()+P)%P;else break;}return a;}
public:
 Parser(const std::string& s,I d):text(s),dimension(d){}
 bool evaluate(I& value){if(text.size()>24000)return false;value=expression();space();return ok&&pos==text.size();}
};
struct Value{std::array<I,2> at{};bool valid=false;};
inline std::unordered_map<std::string,Value> cache;
inline size_t cache_bytes=0;
inline std::vector<std::array<double,6>> estimates;
inline void reset(){cache.clear();cache_bytes=0;estimates.clear();}
inline Value evaluate(const std::string& s){
 auto found=cache.find(s);if(found!=cache.end())return found->second;
 Value v;v.valid=Parser(s,17).evaluate(v.at[0])&&Parser(s,19).evaluate(v.at[1]);
 if(cache.size()>=8192||cache_bytes+s.size()>2*1024*1024){cache.clear();cache_bytes=0;}
 if(s.size()<=24000){cache.emplace(s,v);cache_bytes+=s.size();}
 return v;
}
inline bool prepare_reference(BaseIntegral** rows,unsigned n){
 estimates.assign(n,{0,0,0,0,0,0});
 size_t total=0;for(unsigned j=0;j<n;++j)total+=rows[j][0].length;
 if(total>8192)return false;
 std::vector<std::vector<Value>> values(n);
 for(unsigned j=0;j<n;++j){
  values[j].reserve(rows[j][0].length);
  for(unsigned k=0;k<rows[j][0].length;++k){
   Value v=evaluate(rows[j][k].coefficientString);if(!v.valid)return false;values[j].push_back(v);
  }
  if(!values[j][0].at[0]||!values[j][0].at[1])return false;
 }
 for(unsigned q=0;q<n;++q){
  double sum=0,unions=0,cancelled=0,maximum=0,zero_rows=0,squares=0;
  for(unsigned j=0;j<n;++j)if(j!=q){
   unsigned a=1,b=1,nonzero=0,cancels=0,un=0;
   const unsigned ns=rows[q][0].length,nd=rows[j][0].length;
   while(a<ns||b<nd){
    ++un;
    if(a==ns){++b;++nonzero;}
    else if(b==nd){++a;++nonzero;}
    else if(rows[q][a].id==rows[j][b].id){
     bool zero=true;for(unsigned k=0;k<2;++k)
      if((values[j][b].at[k]*values[q][0].at[k]-values[q][a].at[k]*values[j][0].at[k])%P!=0)zero=false;
     if(zero)++cancels;else ++nonzero;
     ++a;++b;
    }else if(rows[q][a].id>rows[j][b].id){++a;++nonzero;}
    else{++b;++nonzero;}
   }
   sum+=nonzero;unions+=un;cancelled+=cancels;maximum=std::max(maximum,double(nonzero));
   zero_rows+=nonzero==0;squares+=double(nonzero)*nonzero;
  }
  estimates[q]={std::log1p(sum),cancelled/std::max(1.,unions),std::log1p(maximum),
                std::log1p(zero_rows),std::log1p(squares),1.};
 }
 return true;
}

inline bool fast=false;
inline bool prepare_fast(BaseIntegral** rows,unsigned n){
 estimates.assign(n,{0,0,0,0,0,0});
 size_t total=0;for(unsigned j=0;j<n;++j)total+=rows[j][0].length;
 if(total>8192)return false;
 std::vector<std::vector<Value>> values(n);
 for(unsigned j=0;j<n;++j){
  values[j].reserve(rows[j][0].length);
  for(unsigned k=0;k<rows[j][0].length;++k){
   Value v=evaluate(rows[j][k].coefficientString);if(!v.valid)return false;values[j].push_back(v);
  }
  if(!values[j][0].at[0]||!values[j][0].at[1])return false;
 }
 std::vector<std::array<double,6>> aggregate(n);
 for(unsigned q=0;q<n;++q)for(unsigned j=q+1;j<n;++j){
  unsigned a=1,b=1,nonzero=0,cancels=0,un=0;
  const unsigned ns=rows[q][0].length,nd=rows[j][0].length;
  while(a<ns||b<nd){
   ++un;
   if(a==ns){++b;++nonzero;}
   else if(b==nd){++a;++nonzero;}
   else if(rows[q][a].id==rows[j][b].id){
    bool zero=true;for(unsigned k=0;k<2;++k)
     if((values[j][b].at[k]*values[q][0].at[k]-values[q][a].at[k]*values[j][0].at[k])%P!=0)zero=false;
    if(zero)++cancels;else ++nonzero;
    ++a;++b;
   }else if(rows[q][a].id>rows[j][b].id){++a;++nonzero;}
   else{++b;++nonzero;}
  }
  for(unsigned k:{q,j}){
   auto& v=aggregate[k];v[0]+=nonzero;v[1]+=un;v[2]+=cancels;
   v[3]=std::max(v[3],double(nonzero));v[4]+=nonzero==0;v[5]+=double(nonzero)*nonzero;
  }
 }
 for(unsigned q=0;q<n;++q){
  auto& v=aggregate[q];
  estimates[q]={std::log1p(v[0]),v[2]/std::max(1.,v[1]),std::log1p(v[3]),std::log1p(v[4]),std::log1p(v[5]),1.};
 }
 return true;
}
inline bool prepare(BaseIntegral** rows,unsigned n){return fast?prepare_fast(rows,n):prepare_reference(rows,n);}
} // namespace kira_mod

