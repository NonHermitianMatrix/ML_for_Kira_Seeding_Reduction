// Bounded inference for the existing float32 seed network.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
using V=std::vector<float>;
struct Layer {unsigned rows,cols;V w,b,wt;};
struct Model {
 unsigned ni,bins,h,pc,cc,mt;std::map<std::string,Layer> layers;
 template<class T> static void read(std::istream& in,T& v){in.read(reinterpret_cast<char*>(&v),sizeof(v));if(!in)throw std::runtime_error("truncated seed weights");}
 explicit Model(const char* path){
  std::ifstream in(path,std::ios::binary);char magic[8]={};in.read(magic,8);
  if(std::string(magic,8)!="MLSEED01")throw std::runtime_error("seed weight format");
  unsigned count;read(in,ni);read(in,bins);read(in,h);read(in,pc);read(in,cc);read(in,mt);read(in,count);
  if(ni>64 || bins>256 || h>128 || pc>4096 || mt>512 || count!=7)throw std::runtime_error("seed model bounds");
  for(unsigned i=0;i<count;++i){
   unsigned len;read(in,len);if(len>64)throw std::runtime_error("layer name");
   std::string name(len,' ');in.read(&name[0],len);Layer a;read(in,a.rows);read(in,a.cols);
   if(a.rows>128 || a.cols>2048)throw std::runtime_error("layer dimensions");
   a.w.resize(a.rows*a.cols);a.b.resize(a.rows);
   in.read(reinterpret_cast<char*>(a.w.data()),a.w.size()*4);in.read(reinterpret_cast<char*>(a.b.data()),a.b.size()*4);
   if(!in)throw std::runtime_error("layer data");a.wt.resize(a.w.size());
   for(unsigned j=0;j<a.rows;++j)for(unsigned k=0;k<a.cols;++k)a.wt[k*a.rows+j]=a.w[j*a.cols+k];
   layers.emplace(name,std::move(a));
  }
 }
 static void add(V& y,const V& x,const Layer& a,unsigned offset=0){
  if(y.size()!=a.rows || offset+x.size()>a.cols)throw std::runtime_error("affine dimensions");
  for(unsigned k=0;k<x.size();++k){
   const float v=x[k];const float* w=&a.wt[(offset+k)*a.rows];
   for(unsigned j=0;j<a.rows;++j)y[j]+=v*w[j];
  }
 }
 V linear(const V& x,const std::string& name,bool activation)const{
  const auto& a=layers.at(name);if(x.size()!=a.cols)throw std::runtime_error("input dimensions");
  V y(a.rows,0);add(y,x,a);
  for(unsigned j=0;j<a.rows;++j){y[j]+=a.b[j];if(activation)y[j]=std::tanh(y[j]);}
  return y;
 }
 V index(const int* a,unsigned n)const{
  V x(3*ni+5,0);int r=0,s=0,t=0;
  for(unsigned j=0;j<n;++j){
   int v=a[j];if(v< -10000 || v>10000)throw std::runtime_error("index magnitude");
   x[j]=v?float(std::copysign(std::log1p(double(std::abs(v))),double(v))):0;
   x[ni+j]=v>0;x[2*ni+j]=1;r+=std::max(0,v);s+=std::max(0,-v);t+=v>0;
  }
  int values[5]={r,s,t,r-t,int(n)};
  for(unsigned j=0;j<5;++j)x[3*ni+j]=float(std::log1p(double(values[j])));
  return x;
 }
 void predict(const float* family,const float* coefficient,const int* masters,unsigned nm,
              const int* targets,unsigned nt,const int* seeds,unsigned ns,unsigned n,float* out)const{
  if(!nm || nm>10000 || !nt || nt>mt || !ns || ns>300000 || !n || n>ni)throw std::runtime_error("prediction bounds");
  V f(family,family+bins+4);V ef=linear(f,"family.0",true),em(h,0);
  for(unsigned i=0;i<nm;++i){V z=linear(index(masters+i*n,n),"master.0",true);for(unsigned j=0;j<h;++j)em[j]+=z[j];}
  for(float& x:em)x/=float(nm);
  std::vector<V> et;et.reserve(nt);V mean(h,0),maximum(h,-INFINITY);
  for(unsigned i=0;i<nt;++i){
   V x=index(targets+i*n,n);x.insert(x.end(),coefficient,coefficient+bins);
   x.push_back(float(double(i)/std::max(1u,nt-1)));x.push_back(float(1./nt));
   V z=linear(x,"term.0",true);
   for(unsigned j=0;j<h;++j){mean[j]+=z[j];maximum[j]=std::max(maximum[j],z[j]);}et.push_back(std::move(z));
  }
  for(float& x:mean)x/=float(nt);

  const auto& pair_layer=layers.at("pair.0");
  std::vector<V> pair_prefix(nt,V(h,0));
  for(unsigned a=0;a<nt;++a)add(pair_prefix[a],et[a],pair_layer);
  V pair_delta(h),pair_product(h),pair_work(h);
  V pairs(h,0);unsigned pairs_count=0;
  for(unsigned start=0;start<nt*nt;start+=pc){
   V block(h,0);
   for(unsigned pos=start;pos<std::min(nt*nt,start+pc);++pos){
    unsigned a=pos/nt,b=pos%nt;if(a==b)continue;

    for(unsigned k=0;k<h;++k){pair_delta[k]=et[a][k]-et[b][k];pair_product[k]=et[a][k]*et[b][k];}
    pair_work=pair_prefix[a];add(pair_work,et[b],pair_layer,h);
    add(pair_work,pair_delta,pair_layer,2*h);add(pair_work,pair_product,pair_layer,3*h);
    for(unsigned j=0;j<h;++j){pair_work[j]+=pair_layer.b[j];block[j]+=std::tanh(pair_work[j]);}
    ++pairs_count;
   }
   for(unsigned j=0;j<h;++j)pairs[j]+=block[j];
  }
  for(float& x:pairs)x/=float(std::max(1u,pairs_count));
  V context;for(const V* p:{&mean,&maximum,&pairs,&ef,&em})context.insert(context.end(),p->begin(),p->end());

  const auto& score_layer=layers.at("score.0");const auto& output_layer=layers.at("score.2");
  V score_prefix(score_layer.rows,0),hidden(score_layer.rows);
  add(score_prefix,context,score_layer);
  const float root= float(std::sqrt(double(h)));
  for(unsigned i=0;i<ns;++i){
   V z=linear(index(seeds+i*n,n),"seed.0",true),attention(nt),attended(h,0);
   float mx=-INFINITY;
   for(unsigned a=0;a<nt;++a){float dot=0;for(unsigned j=0;j<h;++j)dot+=z[j]*et[a][j];attention[a]=dot/root;mx=std::max(mx,attention[a]);}
   float total=0;for(float& a:attention){a=std::exp(a-mx);total+=a;}
   for(unsigned a=0;a<nt;++a){attention[a]/=total;for(unsigned j=0;j<h;++j)attended[j]+=attention[a]*et[a][j];}

   hidden=score_prefix;add(hidden,z,score_layer,context.size());
   add(hidden,attended,score_layer,context.size()+h);
   for(unsigned j=0;j<score_layer.rows;++j){hidden[j]+=score_layer.b[j];hidden[j]=std::tanh(hidden[j]);}
   float score=0;for(unsigned k=0;k<hidden.size();++k)score+=hidden[k]*output_layer.w[k];score+=output_layer.b[0];
   score=std::max(-80.f,std::min(80.f,score));out[i]=1.f/(1.f+std::exp(-score));
  }
 }
};
static thread_local std::string last_error;
extern "C" {
const char* seed_error(){return last_error.c_str();}
void* seed_create(const char* path){try{return new Model(path);}catch(const std::exception& e){last_error=e.what();return nullptr;}}
void seed_destroy(void* p){delete static_cast<Model*>(p);}
int seed_predict(void* p,const float* f,const float* c,const int* m,unsigned nm,const int* t,unsigned nt,const int* s,unsigned ns,unsigned n,float* output){
 try{if(!p)throw std::runtime_error("null model");static_cast<Model*>(p)->predict(f,c,m,nm,t,nt,s,ns,n,output);return 0;}
 catch(const std::exception& e){last_error=e.what();return -1;}
}
}
