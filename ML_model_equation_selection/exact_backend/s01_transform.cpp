// Bounded exact polynomial transformations with GMP.
#include <gmpxx.h>
#include <vector>
#include <map>
#include <string>
#include <stdexcept>
#include <cstdint>
#include <cstdlib>
#include <cstring>
typedef std::vector<unsigned char> Bytes;
struct Reader{
 const unsigned char*p;size_t n,k;
 Reader(const void*b,size_t s):p((const unsigned char*)b),n(s),k(0){}
 uint32_t u(){if(n-k<4)throw std::runtime_error("short");uint32_t x=0;for(int j=0;j<4;j++)x|=uint32_t(p[k++])<<(8*j);return x;}
 mpz_class z(){if(k==n)throw std::runtime_error("short");unsigned sign=p[k++];uint32_t m=u();if(sign>1||m>1048576||n-k<m)throw std::runtime_error("integer");mpz_class x;mpz_import(x.get_mpz_t(),m,-1,1,0,0,p+k);k+=m;if(sign)x=-x;return x;}
};
void u(Bytes&b,uint32_t x){for(int j=0;j<4;j++)b.push_back((x>>(8*j))&255);}
void z(Bytes&b,const mpz_class&x){b.push_back(x<0?1:0);size_t n=x==0?0:(mpz_sizeinbase(x.get_mpz_t(),2)+7)/8;if(n>1048576)throw std::runtime_error("integer");u(b,n);size_t start=b.size();b.resize(start+n);size_t written=0;if(n)mpz_export(&b[start],&written,-1,1,0,0,x.get_mpz_t());if(written!=n)throw std::runtime_error("export");}
struct Poly{std::vector<mpz_class>a;mpz_class d;};
typedef std::vector<std::vector<mpz_class> > Matrix;
static std::map<std::string,Matrix> cache;
Matrix& transform(const mpz_class&L){
 std::string key=L.get_str();
 auto found=cache.find(key);if(found!=cache.end())return found->second;
 if(cache.size()>=128)cache.erase(cache.begin());
 Matrix m(14,std::vector<mpz_class>(14));
 mpz_class power=1;
 for(int n=0;n<14;n++){unsigned long choose=1;for(int k=0;k<=n;k++){mpz_class shift;mpz_ui_pow_ui(shift.get_mpz_t(),2,n-k);if((n-k)%2)shift=-shift;m[k][n]=choose*power*shift;if(k<n)choose=choose*(n-k)/(k+1);}power*=L;}
 return cache.insert(std::make_pair(key,m)).first->second;
}
extern "C" int expand_exact(const void*data,size_t n,void**output,size_t*outn){
 *output=NULL;*outn=0;
 try{
  if(n>16777216)throw std::runtime_error("input");
  Reader r(data,n);uint32_t count=r.u();if(count>2048)throw std::runtime_error("polynomials");
  std::vector<Poly> polys(count);
  for(auto &p:polys){uint32_t length=r.u();if(length>14)throw std::runtime_error("degree");p.d=r.z();if(p.d<=0)throw std::runtime_error("denominator");for(uint32_t j=0;j<length;j++)p.a.push_back(r.z());}
  uint32_t nl=r.u();if(nl<1||nl>32)throw std::runtime_error("loops");
  Bytes out;u(out,nl);
  for(uint32_t l=0;l<nl;l++){
   mpz_class L=r.z();if(L<=0)throw std::runtime_error("loop");z(out,L);u(out,count);Matrix&m=transform(L);
   for(const auto&p:polys){
    u(out,p.a.size());
    for(size_t k=0;k<p.a.size();k++){
     mpz_class value=0,g;
     for(size_t j=k;j<p.a.size();j++)mpz_addmul(value.get_mpz_t(),p.a[j].get_mpz_t(),m[k][j].get_mpz_t());
     mpz_gcd(g.get_mpz_t(),value.get_mpz_t(),p.d.get_mpz_t());
     mpz_class num=value/g,den=p.d/g;z(out,num);z(out,den);
    }
   }
   if(out.size()>67108864)throw std::runtime_error("output");
  }
  if(r.k!=r.n)throw std::runtime_error("trailing");
  void*mem=std::malloc(out.size());if(!mem)throw std::bad_alloc();std::memcpy(mem,out.data(),out.size());*output=mem;*outn=out.size();return 0;
 }catch(...){return 1;}
}
extern "C" void release_exact(void*p){std::free(p);}
