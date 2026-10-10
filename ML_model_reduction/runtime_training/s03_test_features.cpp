// Standalone verification harness for modular coefficient features.
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
struct BaseIntegral{unsigned length=0;long long id=0;std::string coefficientString;};
#include "s01_modular_features.h"
int main(){
 std::cout<<std::setprecision(17);std::string line;
 while(std::getline(std::cin,line)){
  if(line=="@fixture"){
   BaseIntegral a[]={{3,5,"d"},{3,4,"2*d"},{3,3,"d+1"}};
   BaseIntegral b[]={{3,5,"1"},{3,4,"2"},{3,2,"1"}};
   BaseIntegral c[]={{3,5,"d+1"},{3,3,"2"},{3,2,"d"}};
   BaseIntegral* rows[]={a,b,c};if(!kira_mod::prepare(rows,3))return 2;
   std::cout<<"[";
   for(unsigned q=0;q<3;++q){if(q)std::cout<<",";std::cout<<"[";
    for(unsigned k=0;k<6;++k){if(k)std::cout<<",";std::cout<<kira_mod::estimates[q][k];}
    std::cout<<"]";
   }
   std::cout<<"]"<<std::endl;
  }else{
   const auto v=kira_mod::evaluate(line);
   std::cout<<v.valid<<" "<<v.at[0]<<" "<<v.at[1]<<std::endl;
  }
 }
}
