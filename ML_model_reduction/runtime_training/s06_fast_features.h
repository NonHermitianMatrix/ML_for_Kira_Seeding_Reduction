// Included inside namespace kira_cost, after Features and modular estimates exist.
inline std::vector<Features> fast_features(BaseIntegral** rows,unsigned n){
 struct Stats{double length=0,bytes=0,largest=0,pivot=0,division=0,multiplication=0,powers=0;};
 std::vector<Stats> a(n);double total_length=0,total_bytes=0,total_pivots=0;
 for(unsigned j=0;j<n;++j){
  auto& v=a[j];v.length=rows[j][0].length;v.pivot=rows[j][0].coefficientString.size();
  for(unsigned k=0;k<rows[j][0].length;++k){
   const auto& s=rows[j][k].coefficientString;
   v.bytes+=s.size();v.largest=std::max(v.largest,double(s.size()));
   for(char c:s){v.division+=c=='/';v.multiplication+=c=='*';v.powers+=c=='^';}
  }
  total_length+=v.length;total_bytes+=v.bytes;total_pivots+=v.pivot;
 }
 std::vector<double> overlap(n,0.);
 for(unsigned q=0;q<n;++q)for(unsigned j=q+1;j<n;++j){
  unsigned i=1,k=1,shared=0;
  while(i<rows[q][0].length&&k<rows[j][0].length){
   if(rows[q][i].id==rows[j][k].id){++shared;++i;++k;}
   else if(rows[q][i].id>rows[j][k].id)++i;
   else ++k;
  }
  overlap[q]+=shared;overlap[j]+=shared;
 }
 std::vector<Features> output;output.reserve(n);
 for(unsigned q=0;q<n;++q){
  const auto& v=a[q];const double nd=total_length-v.length,bd=total_bytes-v.bytes;
  const double unions=(n-1)*(v.length-2)+nd-overlap[q];
  const double form=(n-1)*v.bytes+bd+(v.length-1)*((n-1)*(v.pivot+8)+total_pivots-v.pivot);
  output.push_back(Features{std::log1p(n),std::log1p(v.length),std::log1p(v.bytes),std::log1p(v.largest),std::log1p(v.pivot),
   double(rows[q][0].coefficientString=="1"||rows[q][0].coefficientString=="-1"),
   std::log1p(v.division),std::log1p(v.multiplication),std::log1p(v.powers),
   std::log1p(nd),std::log1p(bd),std::log1p(overlap[q]),std::log1p(unions),std::log1p(form),
   std::log1p((n-1)*(1+2*v.length)),unions/std::max(1.,nd),double(q==0),
   std::log1p(v.bytes/std::max(1.,v.length)),kira_mod::estimates[q][0],kira_mod::estimates[q][1],
   kira_mod::estimates[q][2],kira_mod::estimates[q][3],kira_mod::estimates[q][4],kira_mod::estimates[q][5]});
 }
 return output;
}
